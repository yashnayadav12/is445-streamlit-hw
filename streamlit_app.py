import streamlit as st
import pandas as pd
import altair as alt

# Page setup
st.set_page_config(
    page_title="Illinois Building Inventory",
    layout="wide"
)

st.title("Illinois Building Inventory Dashboard")

st.write(
    "Exploring Illinois state-owned buildings, "
    "their characteristics, and how they are used."
)

# Load the dataset
DATA_URL = (
    "https://raw.githubusercontent.com/UIUC-iSchool-DataViz/"
    "is445_data/main/building_inventory.csv"
)

@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL, low_memory=False)

df = load_data()


# Data preparation
buildings = df[
    ["Agency Name", "Year Constructed",
     "Square Footage", "Usage Description"]
].copy()

# Convert year and square footage to numbers
buildings["Year Constructed"] = pd.to_numeric(
    buildings["Year Constructed"], errors="coerce"
)

buildings["Square Footage"] = pd.to_numeric(
    buildings["Square Footage"], errors="coerce"
)

# Remove missing and invalid values
buildings = buildings.dropna(
    subset=["Agency Name", "Year Constructed", "Square Footage"]
)

buildings = buildings[
    (buildings["Year Constructed"] > 0) &
    (buildings["Year Constructed"] <= 2026) &
    (buildings["Square Footage"] > 0)
]

st.subheader("Data Preparation")

st.write("Usable building records:", len(buildings))
st.write("Number of agencies:", buildings["Agency Name"].nunique())
st.write(
    "Construction year range:",
    int(buildings["Year Constructed"].min()),
    "to",
    int(buildings["Year Constructed"].max())
)


### Visualization 1: Interactive scatter plot


st.header("1. Building Age vs. Size")

st.write(
    "Explore how building size varies by construction year. "
    "Select an agency to focus on its buildings."
)

# Dropdown to select an agency
agencies = ["All Agencies"] + sorted(
    buildings["Agency Name"].unique().tolist()
)

selected_agency = st.selectbox(
    "Select a government agency:",
    agencies
)

# Filter buildings based on selected agency
if selected_agency == "All Agencies":
    filtered = buildings.copy()
else:
    filtered = buildings[
        buildings["Agency Name"] == selected_agency
    ].copy()

st.write("Buildings matching selection:", len(filtered))

# Use a sample to keep the chart responsive
plot_data = filtered.sample(
    n=min(len(filtered), 3000),
    random_state=42
)

if len(plot_data) < len(filtered):
    st.caption(
        "Showing a sample of 3,000 buildings "
        "to keep the chart responsive."
    )

# Create scatter plot
scatter = alt.Chart(plot_data).mark_circle(
    size=60,
    opacity=0.5,
    color="steelblue"
).encode(
    x=alt.X(
        "Year Constructed:Q",
        title="Year Constructed",
        scale=alt.Scale(domain=[1750, 2025])
    ),
    y=alt.Y(
        "Square Footage:Q",
        title="Building Size (Square Feet)",
        scale=alt.Scale(type="log")
    ),
    tooltip=[
        "Agency Name:N",
        "Year Constructed:Q",
        "Square Footage:Q",
        "Usage Description:N"
    ]
).properties(
    height=450,
    title="Building Size by Construction Year"
)

st.altair_chart(scatter, use_container_width=True)

### Visualization 2: Building usage heatmap

st.header("2. Building Usage by Construction Decade")

st.write(
    "This heatmap shows when different types of "
    "Illinois government buildings were constructed."
)

# Keep buildings with usage information
usage_data = buildings.dropna(
    subset=["Usage Description"]
).copy()

# Focus on buildings constructed since 1900
usage_data = usage_data[
    usage_data["Year Constructed"] >= 1900
].copy()

# Find the eight most common building uses
top_uses = (
    usage_data["Usage Description"]
    .value_counts()
    .head(8)
    .index
)

usage_data = usage_data[
    usage_data["Usage Description"].isin(top_uses)
].copy()

# Group construction years into decades
usage_data["Decade"] = (
    usage_data["Year Constructed"] // 10 * 10
).astype(int)

# Count buildings in each decade and usage category
heatmap_data = (
    usage_data.groupby(["Decade", "Usage Description"])
    .size()
    .reset_index(name="Building Count")
)

# Create heatmap
heatmap = alt.Chart(heatmap_data).mark_rect().encode(
    x=alt.X(
        "Decade:O",
        title="Construction Decade"
    ),
    y=alt.Y(
        "Usage Description:N",
        title="Building Usage"
    ),
    color=alt.Color(
        "Building Count:Q",
        title="Number of Buildings",
        scale=alt.Scale(scheme="blues")
    ),
    tooltip=[
        "Decade:O",
        "Usage Description:N",
        "Building Count:Q"
    ]
).properties(
    height=400,
    title="Building Usage Across Construction Decades"
)

st.altair_chart(heatmap, use_container_width=True)

### Visualization write-up

st.header("Visualization Write-Up")

st.subheader("Visualization 1: Building Age vs. Size")

st.write(
    "For my first visualization, I created a scatter plot to explore "
    "how the size of Illinois government buildings varies depending "
    "on when they were constructed. Each point represents a building "
    "from the displayed data, with construction year on the x-axis "
    "and square footage on the y-axis. I used a logarithmic scale "
    "because building sizes vary a lot, and a regular scale made "
    "smaller buildings harder to see. I chose blue circles with some "
    "transparency so overlapping points would be easier to identify. "
    "I also added a dropdown that lets users filter the chart by "
    "government agency. If I had more time, I would add a filter "
    "for building usage to see whether certain types of buildings "
    "tend to be larger."
)

st.subheader("Visualization 2: Building Usage by Decade")

st.write(
    "For my second visualization, I used a heatmap to compare "
    "different types of buildings across construction decades. "
    "I focused on the eight most common usage categories and "
    "buildings constructed since 1900 to keep the chart readable. "
    "The darker blue cells represent higher numbers of buildings, "
    "which makes it easier to find patterns across decades. "
    "For example, storage buildings appear more frequently "
    "in several decades during the later twentieth century. "
    "I chose a heatmap because it makes comparisons across "
    "two categories easier than using a long bar chart. "
    "If I had more time, I would also compare percentages "
    "within each decade instead of only using building counts."
)

st.subheader("Comparison with Homework 5")

st.write(
    "This assignment uses a different dataset and different "
    "visualizations from my Homework 5 submission. "
    "Homework 5 focused on Illinois professional licenses "
    "using bar charts, while this project explores building "
    "inventory using a scatter plot and heatmap. "
    "No plots or written explanations were reused."
)

st.caption(
    "Data source: Illinois Building Inventory dataset, "
    "UIUC IS 445 course data repository."
)
