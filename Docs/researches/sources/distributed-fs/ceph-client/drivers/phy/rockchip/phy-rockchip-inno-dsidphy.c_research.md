# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-dsidphy.c

## Purpose
This driver controls Rockchip Innosilicon video combo PHYs used for MIPI DSI D-PHY and LVDS modes. It programs analog, digital, lane, and LVDS register banks, calculates PLL dividers, applies timing tables for several maximum-rate families, and exposes the block through generic PHY mode/configure/power callbacks.

## Important APIs, Types, And Functions
`struct inno_dsidphy` stores clocks, MMIO bases, reset, selected mode, MIPI config, and cached PLL parameters. `struct inno_video_phy_plat_data` selects timing table, max rate, and max lanes. `inno_dsidphy_pll_calc_rate()` searches predivider/feedback divider values from the reference clock. `inno_dsidphy_mipi_mode_enable()` programs PLL, pre-emphasis/VOD, timing counters derived from `phy_configure_opts_mipi_dphy`, and lane enables. `inno_dsidphy_lvds_mode_enable()` programs fixed LVDS PLL and lane state. Generic PHY callbacks are `.set_mode`, `.configure`, `.power_on`, and `.power_off`.

## Control Flow
Probe maps the PHY registers, gets `ref` and `pclk`, obtains the APB reset, creates one PHY, registers a provider, and enables runtime PM. Consumers call `.set_mode` for MIPI D-PHY or LVDS. MIPI consumers must call `.configure`, which validates and stores D-PHY timings. Power-on enables pclk/ref clocks, gets runtime PM, powers bandgap/work logic, and dispatches to MIPI or LVDS setup. Power-off disables analog lanes, PLL/LDO, LVDS drivers, drops runtime PM, and disables clocks.

## State And Persistence
The current mode and MIPI timing config remain in memory between callbacks. PLL divider choices are recalculated and cached on MIPI power-on. Hardware state is register-only and cleared by power-off or reset.

## Dependencies And Integration Points
The driver uses generic PHY, MIPI D-PHY helper validation, clock framework, runtime PM, reset controls, platform MMIO, and compatible data for PX30, RK3128, RK3368, RK3506, RK3568, and RV1126 DSI DPHYs. It integrates with DRM bridge/DSI/LVDS consumers via generic PHY mode, configure, and power calls.

## Risks And Test Signals
MIPI power-on assumes a valid prior `.configure`; LVDS uses fixed dividers and does not validate display mode. The PLL calculation caps output above 1 GHz in its search, while max-rate data changes subsequent programming behavior, so high-rate modes need hardware validation. Error handling in power-on does not unwind clocks/PM if an unsupported mode is selected after enabling them. Test signals include mode rejection for unsupported modes, MIPI timing table boundaries, LVDS bring-up, runtime PM balance, lane count behavior for 2-lane and 4-lane variants, and display link stability across pixel rates.
