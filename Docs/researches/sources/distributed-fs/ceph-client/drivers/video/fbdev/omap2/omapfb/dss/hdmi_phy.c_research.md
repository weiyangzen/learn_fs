# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_phy.c

## Purpose
`hdmi_phy.c` initializes, maps, configures, and dumps the HDMI TX PHY for OMAP4/OMAP5/DRA7 fbdev DSS HDMI paths. It handles feature differences, lane remapping/polarity, frequency-output selection, line enable, and optional LDO/BIST controls.

## Important APIs, types, and functions
Key public functions are `hdmi_phy_parse_lanes`, `hdmi_phy_configure`, `hdmi_phy_dump`, and `hdmi_phy_init`. The private `struct hdmi_phy_features` records whether BIST control and LDO voltage fields exist plus the maximum PHY threshold. Internal helpers include `hdmi_phy_configure_lanes` and `hdmi_phy_get_features`.

## Control Flow
Init selects feature data from `omapdss_get_version` and maps the `"phy"` resource. Lane parsing consumes four differential pairs, verifies each pair is adjacent and ordered as normal or inverted polarity, and fills `phy->lane_function`/`lane_polarity`. Configure performs a dummy read after reset, enables HFBITCLK divide-by-two for PHYs with BIST control, selects `freqout` based on high/low bit clocks and feature limits, enables TXVALID/TMDSCLKEN, optionally sets max LDO voltage, and writes lane/polarity fields.

## State and Persistence
The file has one global `phy_feat` pointer shared by the driver instance. Per-device state lives in `struct hdmi_phy_data` lane arrays and `base`. Hardware state remains in PHY TX, digital, power, pad config, and optional BIST registers while powered.

## Dependencies and Integration Points
It depends on platform resource mapping, `omapdss_get_version`, HDMI register access macros, and `hdmi_common.c`/DT lane parsing. HDMI display drivers call it before raising wrapper PHY power to LDO/TX modes.

## Risks
The global `phy_feat` assumes a single active feature set. Lane validation rejects non-adjacent or duplicate-looking pair layouts but does not explicitly detect duplicate lanes beyond invalid final mapping. Frequency threshold selection is coarse and depends on correct PLL clock values.

## Test Signals
Test default and DT-remapped lanes, polarity inversion, unsupported SoC version handling, OMAP4 versus OMAP5/DRA7 feature behavior, PHY bring-up at low/high TMDS clocks, hotplug power transitions, and PHY debug dumps.
