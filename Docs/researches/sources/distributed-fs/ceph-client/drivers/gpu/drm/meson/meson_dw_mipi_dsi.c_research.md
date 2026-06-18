# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_mipi_dsi.c

Purpose: Provides the Meson platform glue for Synopsys DW MIPI-DSI on G12A-class SoCs. It maps the DSI TOP registers, owns the D-PHY, clocks, TOP reset, and supplies host/PHY callbacks to the generic `dw_mipi_dsi` bridge core.

Important APIs, types, and functions: `struct meson_dw_mipi_dsi` stores MMIO base, `phy`, D-PHY options, `dw_mipi_dsi` handle, attached `mipi_dsi_device`, current mode, bit/pixel clocks, and TOP reset. Key callbacks are `dw_mipi_dsi_phy_init()`, `dw_mipi_dsi_phy_power_on/off()`, `dw_mipi_dsi_get_lane_mbps()`, `dw_mipi_dsi_phy_get_timing()`, `meson_dw_mipi_dsi_host_attach()`, and `host_detach()`.

Control flow: platform probe allocates state, maps registers, gets the D-PHY and enabled bit/px clocks, toggles the TOP reset, fills `dw_mipi_dsi_plat_data`, and calls `dw_mipi_dsi_probe()`. Attach validates RGB888/RGB666, initializes the PHY, and resets/enables TOP clock/memory. The DW core asks for lane Mbps, timing, and escape clock; PHY init then sets bit clock to computed HS rate, takes an exclusive rate lock, resets the pixel clock to mode clock, configures DPI/VENC color mode, and calls `phy_configure()`.

State and persistence: `mipi_dsi->mode` is captured during lane-rate calculation and later reused by timing and clock setup, so ordering with the DW core matters. `dsi_device` persists between host attach/detach. `clk_rate_exclusive_get()` is released only on PHY power-off. TOP reset, clock enable, memory power, and color mux registers persist until reprogrammed or reset.

Dependencies and integration points: Integrates with `dw_mipi_dsi`, MIPI DSI host attach semantics, Linux PHY and CCF clock APIs, `meson_dw_mipi_dsi.h` register definitions, and `meson_encoder_dsi.c`, which configures ENCL/VENC for the panel mode.

Risks: Failure after `clk_rate_exclusive_get()` but before power-off can leave exclusivity held. Pixel format support is intentionally narrow. Timing values are keyed to a few `hdisplay` widths, so new panels may need tuning. Probe defers early `-EIO` bit-clock failures.

Test signals: G12A DT probe, panel attach/detach, RGB888 and RGB666 panels, lane-rate and D-PHY timing validation, clock-rate changes visible through CCF, and successful display enable via the DSI encoder bridge.
