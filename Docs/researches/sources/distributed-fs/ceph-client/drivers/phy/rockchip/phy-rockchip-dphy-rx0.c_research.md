# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-dphy-rx0.c

## Purpose
This driver controls the RK3399 Synopsys MIPI D-PHY RX0 block used by the ISP camera path. It configures GRF DPHY control/test registers, selects HS frequency range values from the requested MIPI D-PHY configuration, and manages the required clocks.

## Important APIs, Types, And Functions
`struct rk_dphy` holds the device, GRF regmap, bulk clocks, match data, current `phy_configure_opts_mipi_dphy`, and selected HS frequency code. `struct rk_dphy_drv_data` supplies clock names, HS frequency range table, and GRF register descriptions. `rk_dphy_configure()` validates MIPI D-PHY options and selects a range entry. `rk_dphy_enable()` writes the RX0 force/turn/enable bits, resets the test interface, programs lane HS RX control registers, and writes settle timing. Generic PHY callbacks prepare/unprepare clocks in `.init`/`.exit`, enable/disable clocks in power callbacks, and configure MIPI timing.

## Control Flow
Probe locates the parent GRF syscon, loads RK3399 match data, allocates and gets the clock bulk (`dphy-ref`, `dphy-cfg`, `grf`), creates a PHY, and registers a simple provider. A consumer first calls `.configure` with validated lane count and `hs_clk_rate`; the driver maps Mbps to a register code. `.init` prepares clocks, `.power_on` enables clocks and writes the DPHY sequence, and `.power_off` disables lanes and clocks.

## State And Persistence
Software retains the last valid MIPI D-PHY config and `hsfreq` code. Hardware state is GRF and internal test-interface programming. No runtime PM or persistent storage is used.

## Dependencies And Integration Points
The driver uses generic PHY, `GENERIC_PHY_MIPI_DPHY`, regmap/syscon from the parent node, bulk clocks, and compatible string `rockchip,rk3399-mipi-dphy-rx0`. It integrates with camera/ISP receivers through MIPI D-PHY configure and power callbacks.

## Risks And Test Signals
If `.configure` is skipped or chooses no range, power-on may program an invalid zero/default value; consumers should configure before enabling. The range lookup treats an unselected code of zero as invalid, which makes the first table entry with cfg `0x00` unreachable for rates under 89 Mbps. Test signals include config validation failures, lane enable mask for 1-4 lanes, correct clock prepare/enable pairing, CSI capture at representative lane rates, and power-off disabling RX0 lanes.
