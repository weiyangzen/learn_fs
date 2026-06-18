# sources/distributed-fs/ceph-client/include/linux/phy/phy-mipi-dphy.h

## Purpose
MIPI D-PHY timing configuration contract for generic PHY consumers and providers.

## Important APIs, Types, and Functions
`struct phy_configure_opts_mipi_dphy` enumerates D-PHY timing values for clock and data lanes: miss/post/pre/prepare/settle/term/trail/zero, turnaround timing, LPX, wakeup/init, HS and LP clock rates, and active lane count. It declares `phy_mipi_dphy_get_default_config()`, `phy_mipi_dphy_get_default_config_for_hsclk()`, and `phy_mipi_dphy_config_validate()`.

## Control Flow
Consumers can compute default timings from pixel clock, bits per pixel, and lane count, or from HS clock rate directly. Validation checks timing ranges before hardware configuration.

## State and Persistence
The timing structure is transient input. Applied values persist as PHY register programming and directly affect high-speed/low-power transitions.

## Dependencies and Integration Points
Included by generic PHY options and used by DRM/CSI/DSI camera/display PHY drivers. It bridges protocol timing requirements into PHY provider operations.

## Risks
Timing fields have strict unit expectations: picoseconds, microseconds, UI, and Hertz. Unit mistakes or invalid lane counts can cause intermittent DSI/CSI link failure. Providers must not silently accept invalid timing.

## Test Signals
Validation tests for min/max timing, DSI/CSI bring-up across lane counts and pixel clocks, and hardware link stability tests under power-cycle and mode-switch scenarios.
