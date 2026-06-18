<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-rk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-rk.c

## Purpose
`dwmac-rk.c` is the Rockchip stmmac glue layer for a wide range of PX/RK/RV SoCs. It abstracts per-SoC GRF/PHP-GRF register layouts behind an ops table, handles RGMII/RMII interface selection, TX/RX delay programming, MAC clock routing and speed changes, PHY regulator/reset control, integrated PHY power sequencing, runtime PM, and stmmac lifecycle callbacks.

## Important APIs, Types, and Functions
- `struct rk_gmac_ops` contains SoC-specific init, RGMII/RMII programming, speed programming, integrated PHY power hooks, GRF register/mask metadata, supported interface flags, and optional MMIO base lists for instance id detection.
- `struct rk_priv_data` stores selected ops, interface, id, regulator, clocks, PHY reset, delays, GRF/PHP-GRF regmaps, and resolved register fields.
- `rk_encode_wm16()` builds Rockchip write-mask register values.
- `rk_gmac_setup()` parses `clock_in_out`, `tx_delay`, `rx_delay`, `rockchip,grf`, optional `rockchip,php-grf`, integrated PHY status, and runs ops init.
- `rk_gmac_powerup()` enables clocks, writes interface/mode bits, applies delay programming, enables PHY supply, runtime PM, and integrated PHY powerup.
- `rk_set_clk_tx_rate()` updates CRU clock rates and GRF speed selectors for RGMII/RMII.
- `rk_gmac_probe()` sets stmmac callbacks and calls `devm_stmmac_pltfr_probe()`.

## Control Flow
Probe selects `rk_gmac_ops` by compatible, parses stmmac DT data, normalizes core type/FIFO defaults, installs interface, clock, init/exit, suspend/resume callbacks, creates private Rockchip state, initializes clocks, and lets stmmac probe. The stmmac init path calls `rk_gmac_powerup()`. Suspend powers down unless wakeup is enabled; resume powers back up; exit powers down, releases optional PHY clock and reset handle. Link speed changes call the Rockchip clock-rate callback.

## State and Persistence
Private state is per-device. Hardware state spans GRF/PHP-GRF interface and clock registers, delay registers, RMII gates, CRU clocks, optional PHY clocks, regulators, reset controls, and runtime PM state. Delay defaults are stored in private memory and applied at each power-up.

## Dependencies and Integration Points
The driver depends on syscon/regmap, clk bulk APIs, regulators, reset controls, runtime PM, OF properties, stmmac platform helpers, and phylib interface helpers. It supports many compatible strings from `rockchip,px30-gmac` through `rockchip,rk3588-gmac` and `rockchip,rv1126-gmac`.

## Risks and Edge Cases
- SoC instance id detection relies on exact MMIO base addresses for variants with multiple MACs.
- Missing or misspelled `clock_in_out` defaults to input from PHY.
- Missing delay properties produce fallback hex delays and log errors, which can mask board-timing issues.
- `gmac_clk_enable()` does not unwind bulk clocks if enabling `clk_phy` fails.
- Some variants require PHP-GRF; missing phandle fails probe.
- Interface support is per-variant, and unsupported modes fail during init rather than early DT parse.

## Test Signals
Coverage should include each compatible's RGMII/RMII support matrix, multiple-instance id mapping, clock input/output routing, 10/100/1000 speed selector writes, integrated PHY reset/power sequencing, regulator failure handling, wake-on-LAN suspend behavior, and runtime PM balancing. Hardware tests should inspect GRF writes and run traffic after repeated suspend/resume and link-speed changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-rk.c -->
