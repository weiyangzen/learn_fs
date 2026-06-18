<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sophgo.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sophgo.c

## Purpose
`dwmac-sophgo.c` is the Sophgo SG2042/SG2044 platform glue layer. It enables the TX clock, applies stmmac feature flags, configures TX clock rate handling, and accounts for SG2042 internal RX delay by adjusting the advertised PHY interface mode.

## Important APIs, Types, and Functions
- `struct sophgo_dwmac_data` records whether a compatible has internal RX delay.
- `sophgo_sg2044_dwmac_init()` gets the `tx` clock, disables SPH, installs generic `stmmac_set_clk_tx_rate`, and disables multicast hash bins.
- `sophgo_dwmac_probe()` parses resources/DT, runs common initialization, adjusts PHY mode with `phy_fix_phy_mode_for_mac_delays()` when needed, and calls `stmmac_dvr_probe()`.

## Control Flow
Probe obtains stmmac resources and DT data, initializes TX clock and platform flags, obtains match data, optionally rewrites the PHY interface to reflect MAC-provided RX delay, then registers stmmac. Remove uses the generic stmmac platform remove path.

## State and Persistence
The file holds no custom private state. Persistent hardware state is limited to enabled clock state and stmmac-programmed registers. PHY mode adjustment is stored in `plat_dat`.

## Dependencies and Integration Points
It depends on clk APIs, device properties, stmmac platform helpers, and PHY mode delay helpers. Compatible strings are `sophgo,sg2042-dwmac` and `sophgo,sg2044-dwmac`.

## Risks and Edge Cases
- `sophgo_sg2044_dwmac_init()` is used for both compatibles despite its name.
- `phy_fix_phy_mode_for_mac_delays()` can return `PHY_INTERFACE_MODE_NA`, causing probe failure for incompatible delay combinations.
- Multicast filter bins are forced to zero, affecting filtering behavior.

## Test Signals
Test SG2042 RGMII mode combinations with internal RX delay translation, SG2044 without translation, TX clock rate changes across link speeds, multicast filtering behavior, and probe failures for unsupported adjusted PHY modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sophgo.c -->
