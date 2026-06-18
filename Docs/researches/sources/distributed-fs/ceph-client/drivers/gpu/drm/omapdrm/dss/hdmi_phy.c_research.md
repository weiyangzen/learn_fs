# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_phy.c

Purpose: Implements shared OMAP HDMI PHY support: register dump, DT lane remap/polarity interpretation, PHY lane configuration, clock/frequency setup, feature selection for OMAP4 versus OMAP5, and resource mapping.

Important APIs/functions: `hdmi_phy_parse_lanes()` validates four differential pairs and fills `lane_function[]` and `lane_polarity[]`. `hdmi_phy_configure()` performs a dummy TX control read after reset, enables HFBITCLK divide-by-2 on OMAP5-class PHYs, chooses `freqout` from high/low bit clocks and hardware limit, enables TXVALID/TMDSCLKEN, optionally sets LDO voltage, and writes lane mux/polarity. `hdmi_phy_init()` selects feature flags and maps the `phy` resource. `hdmi_phy_dump()` prints key TX PHY registers.

Control flow: Top-level HDMI probe parses lanes and maps the PHY; full bridge enable computes PLL outputs, calls `hdmi_phy_configure()`, then wrapper power commands move the PHY through OFF/LDOON/TXON.

State and persistence: `struct hdmi_phy_data` holds mapped base, feature table pointer, lane functions, and lane polarities for device lifetime. Hardware register state is volatile and reprogrammed on enable.

Dependencies/integration: Uses `hdmi.h` register helpers, DSS logging, OF lane parsing through `hdmi_common.c`, and wrapper power state functions.

Risks and test signals: Lane table lookup supports only known permutations; invalid DT pairs reject probe. `freqout` selection depends on `hfbitclk / 10` versus SoC max PHY threshold. Validate default and swapped lane DTs, polarity inversion, OMAP4/OMAP5 feature differences, hotplug reconfiguration, and high pixel clock modes around the PHY max threshold.
