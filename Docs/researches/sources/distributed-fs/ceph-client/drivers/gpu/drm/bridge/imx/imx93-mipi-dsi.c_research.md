# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx93-mipi-dsi.c

### Purpose
`imx93-mipi-dsi.c` provides the i.MX93 platform glue for the Synopsys DesignWare MIPI DSI host. It supplies mode validation, pixel-clock fixup, input bus-format selection, MIPI D-PHY PLL programming, D-PHY timing tables, and display-mux RGB mapping for the SoC media block.

### Important APIs, Types, And Functions
`struct imx93_dsi` owns clocks, media block regmap, DesignWare handle, platform data, cached D-PHY configuration, reference clock rate, and attached DSI pixel format. PLL support is organized around `struct dphy_pll_cfg`, `struct dphy_pll_vco_prop`, and `struct dphy_pll_hsfreqrange`. Key helpers are `dphy_pll_get_configure_from_opts()`, `dphy_pll_configure()`, `dphy_pll_init()`, `dphy_pll_power_off()`, `imx93_dsi_get_phy_configure_opts()`, `imx93_dsi_validate_mode()`, `imx93_dsi_validate_phy()`, `imx93_dsi_mode_valid()`, `imx93_dsi_mode_fixup()`, `imx93_dsi_phy_init()`, `imx93_dsi_get_lane_mbps()`, `imx93_dsi_phy_get_timing()`, and `imx93_dsi_host_attach()`.

### Control Flow
Probe obtains the media block regmap, `pix`, `phy_cfg`, and `phy_ref` clocks, validates that the D-PHY reference clock is between 2 MHz and 64 MHz, fills `dw_mipi_dsi_plat_data`, and calls `dw_mipi_dsi_probe()`. During mode validation, the driver first checks whether the pixel clock can be rounded within 0.5 percent when the last bridge offers detect and EDID, then computes default MIPI D-PHY options and verifies that a PLL M/N solution exists for the required lane rate. Mode fixup rounds the pixel clock and updates the adjusted mode. Lane-rate calculation stores `phy_cfg` for later PHY init. PHY init programs the `DISPLAY_MUX` RGB mapping based on the attached MIPI DSI format, initializes the PLL clock domain, writes PLL control registers from the calculated config and tables, enables the reference clock, and pulses `UPDATE_PLL`. Power-off clears PLL registers and disables ref/config clocks.

### State, Persistence, And Dependencies
State persists in the cached DSI format from host attach and the cached `union phy_configure_opts` from lane-rate calculation. Hardware state lives in media block mux and D-PHY PLL registers and the pixel/ref/config clocks. Dependencies include the DesignWare MIPI DSI bridge library, Linux MIPI D-PHY helpers, clk APIs, regmap syscon access, DRM mode helpers, and fixed databook-derived PLL and high-speed timing tables.

### Integration Points
The file is a platform adapter for `dw_mipi_dsi`: all bridge and host operation is mediated through DesignWare callbacks in `dw_mipi_dsi_plat_data`. It exposes max four data lanes, converts DRM media-bus formats to LCDIF input expectations, and validates modes against both display clock rounding and D-PHY PLL capability. It integrates with downstream panels through normal MIPI DSI device attach.

### Risks
`dsi->phy_cfg` is populated in `get_lane_mbps()`, so PHY init assumes the DesignWare core called that path for the active mode. PLL search uses integer rounding and picks the smallest frequency delta, making boundary rates important. Some `regmap_update_bits()` calls in mux setup ignore return values. `imx93_dsi_validate_mode()` assumes `drm_bridge_chain_get_last_bridge()` succeeds before checking ops. Clock enable failure in `dphy_pll_configure()` must be balanced carefully because ref clock is disabled only on later update failure or power-off. Unsupported DSI pixel formats leave mux `fmt` at zero.

### Test Signals
Useful tests are probe with invalid ref clock rates, mode validation at 80 Mbps and 2500 Mbps lane-rate edges, pixel-clock rounding outside +/-0.5 percent, RGB888/RGB666/RGB666_PACKED/RGB565 mux writes, D-PHY timing table boundaries, PLL M/N solution search with awkward reference clocks, DesignWare attach format propagation, and suspend/remove paths ensuring clocks are disabled.
