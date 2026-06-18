<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sun55i.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sun55i.c

## Purpose
`dwmac-sun55i.c` is the Allwinner sun55i A523 GMAC200 glue layer. It programs a syscon register for MII/RGMII/RMII mode and internal delay values, enables the MBUS clock and optional PHY regulator, sets GMAC200 platform flags, and delegates to stmmac.

## Important APIs, Types, and Functions
- `sun55i_gmac200_set_syscon()` reads delay properties, validates 100 ps granularity and field fit, sets interface bits, and writes `SYSCON_REG`.
- `sun55i_gmac200_probe()` parses stmmac data, disables SPH, constrains DMA width to 32 bits, programs syscon, enables `mbus`, enables optional `phy` supply, and calls `devm_stmmac_pltfr_probe()`.

## Control Flow
Probe obtains standard stmmac resources and DT config, mutates stmmac flags, runs syscon configuration before clocks/regulator are enabled, enables the bus clock and PHY supply through devm helpers, then registers the platform stmmac driver. Remove and failure cleanup are handled by devm and stmmac platform helpers.

## State and Persistence
The driver has no custom private structure. Hardware state is in the syscon mode/delay register, enabled MBUS clock, optional regulator state, and stmmac platform state.

## Dependencies and Integration Points
It depends on syscon/regmap, clk, regulator, stmmac platform helpers, OF delay properties, and phy mode helpers. Compatible string: `allwinner,sun55i-a523-gmac200`.

## Risks and Edge Cases
- Delay values must be multiples of 100 ps and fit the TX/RX field widths.
- RMII overrides the EPIT RGMII/MII bit, so mode bits must not conflict.
- Unsupported PHY modes fail probe.
- The syscon write replaces the full register value rather than using update-bits, so the register must be dedicated or fully described by this driver.

## Test Signals
Test MII, RGMII variants, and RMII mode programming; valid and invalid TX/RX delay properties; missing syscon, MBUS clock, and optional regulator paths; 32-bit DMA addressing; and traffic after repeated bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-sun55i.c -->
