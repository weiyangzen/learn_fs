<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-spacemit.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-spacemit.c

## Purpose
`dwmac-spacemit.c` is the Spacemit K3 DWMAC glue layer. It uses an APMU syscon to configure MII/RMII/RGMII selection, RGMII TX/RX delay lines, and wake IRQ enablement, while exposing the supported PHY interfaces to stmmac.

## Important APIs, Types, and Functions
- `struct spacmit_dwmac` stores the APMU regmap and control/delay register offsets.
- `spacemit_dwmac_detected_delay_value()` converts requested picosecond delay into a K3 delay-line code.
- `spacemit_dwmac_set_delay()` writes TX/RX delay-line enable, step, and code fields.
- `spacemit_dwmac_update_irq_config()` enables wake IRQ routing when `stmmac_res.wol_irq` is valid.
- `spacemit_get_interfaces()` advertises MII, RMII, and all RGMII variants.
- `spacemit_set_phy_intf_sel()` writes APMU interface mode bits.
- `spacemit_dwmac_probe()` resolves clocks, syscon offsets, delays, callbacks, and registers stmmac.

## Control Flow
Probe gets stmmac resources, allocates private data, parses stmmac DT, enables the `tx` clock, looks up `spacemit,apmu` with two register offsets, programs wake IRQ enablement, reads optional internal delay properties, installs interface callbacks and private data, programs delay lines, and calls `stmmac_dvr_probe()`.

## State and Persistence
State is private regmap/offset data. Hardware state includes APMU control bits, wake IRQ enable, and RGMII delay-line codes. Clock enable is devm-managed through `devm_clk_get_enabled()`.

## Dependencies and Integration Points
The driver depends on syscon/regmap phandle arguments, clk APIs, stmmac platform helpers, OF delay properties, and generic interface selectors. Compatible string: `spacemit,k3-dwmac`.

## Risks and Edge Cases
- Delay values above 2800 ps are rejected; conversion uses a K3-specific 0.9 factor and rounding.
- There is no explicit check that computed codes fit the 8-bit delay fields, though the max delay is intended to keep them valid.
- Wake IRQ enablement depends on stmmac resource parsing setting `wol_irq >= 0`.
- The struct name is misspelled `spacmit_dwmac`, which is harmless but easy to propagate.

## Test Signals
Validate MII/RMII/RGMII selection writes, delay conversion for 0 and near-maximum values, invalid delay rejection, wake IRQ routing with and without WOL IRQ, TX clock enable probe deferral, and traffic across all advertised PHY modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-spacemit.c -->
