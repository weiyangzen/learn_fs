<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-meson8b.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-meson8b.c

## Purpose
`dwmac-meson8b.c` supports Amlogic Meson8b/Meson8m2/GXBB/AXG/G12A DWMAC variants. It creates a small clock tree for the RGMII TX clock, selects RGMII/RMII mode, programs TX/RX internal delays, and enables the PHY reference clock generator.

## Important APIs, Types, and Functions
- `struct meson8b_dwmac_data` selects mode programming and whether PRG_ETH1 has fine RGMII RX delay support.
- `struct meson8b_dwmac` stores MMIO registers, PHY mode, TX/RX delay values, RGMII TX clock, and optional timing-adjustment clock.
- `meson8b_init_rgmii_tx_clk()` registers mux, divider, fixed-factor, and gate clocks backed by PRG_ETH0 fields.
- `meson8b_set_phy_mode()` and `meson_axg_set_phy_mode()` program old and newer PHY mode fields.
- `meson8b_init_rgmii_delays()` validates and writes TX delay, optional RX retiming, and PRG_ETH1 RX clock delay.
- `meson8b_init_prg_eth()` enables RGMII clocking or RMII clock inversion and turns on the TX/PHY ref generator.

## Control Flow
Probe parses stmmac DT data, maps resource index 1, reads delay properties with legacy fallback, validates delay ranges based on variant, gets optional timing-adjustment clock, initializes delay registers, registers the synthetic RGMII TX clock, applies the PHY mode, initializes PRG_ETH clocking, stores `bsp_priv`, and calls `stmmac_dvr_probe()`.

## State and Persistence
State is per-device devm memory and registered clock hardware. Persistent hardware state is in PRG_ETH0/PRG_ETH1 mode, delay, clock mux/divider/gate, RMII inversion, and ref-clock enable bits. Devm actions disable prepared clocks on detach or probe failure.

## Dependencies and Integration Points
The driver depends on Linux common clock provider primitives, stmmac platform helpers, OF properties, and MMIO. Compatible strings include `amlogic,meson8b-dwmac`, `meson8m2`, `meson-gxbb`, `meson-axg`, and `meson-g12a`.

## Risks and Edge Cases
- G12A RX delay must be 0..3000 ps in 200 ps steps; older variants allow only 0 or 2000 ps.
- RX retiming on older variants requires the `timing-adjustment` clock.
- TX delay is encoded as `ns >> 1`, so odd nanosecond inputs are truncated.
- Clock registration uses device-name-derived names and depends on firmware clock parents.

## Test Signals
Test each compatible with RGMII, RGMII_ID/RXID/TXID, and RMII; validate delay property bounds; confirm generated clock rates and gate state; and run link-speed changes to ensure the RGMII TX clock remains functional. Probe-failure tests should cover missing timing-adjustment clock when RX retiming is requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-meson8b.c -->
