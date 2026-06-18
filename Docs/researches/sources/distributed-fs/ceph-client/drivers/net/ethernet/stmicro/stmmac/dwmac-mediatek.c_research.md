<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-mediatek.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-mediatek.c

## Purpose
`dwmac-mediatek.c` is the MediaTek MT2712/MT8195 stmmac glue layer. It handles per-SoC clock lists, PERICFG interface selection, RMII clock-source configuration, MAC-side TX/RX delay programming, safety feature defaults, WOL policy, and clock gating around the generic stmmac core.

## Important APIs, Types, and Functions
- `struct mediatek_dwmac_plat_data` carries variant data, delay settings, clocks, PERICFG regmap, PHY mode, RMII clock flags, and WOL policy.
- `struct mediatek_dwmac_variant` supplies `dwmac_set_phy_interface`, `dwmac_set_delay`, clock list, delay limits, and DMA address width.
- MT2712 and MT8195 have separate `*_set_interface()`, `*_delay_ps2stage()`, `*_delay_stage2ps()`, and `*_set_delay()` implementations.
- `mediatek_dwmac_config_dt()` reads `mediatek,pericfg`, delay properties, clock inversion flags, RMII clock-source flags, and `mediatek,mac-wol`.
- `mediatek_dwmac_clks_config()` gates bulk clocks plus optional `rmii_internal`.
- `mediatek_dwmac_common_data()` fills stmmac flags, queue TBS defaults, safety features, DMA width, and callbacks.

## Control Flow
Probe allocates private data, selects variant from OF match, parses MediaTek-specific DT properties before stmmac DT parsing, initializes clocks, gets stmmac resources, fills common stmmac data, writes interface/delay registers once, enables clocks, and calls `stmmac_dvr_probe()`. Remove unregisters stmmac and disables the same clocks. Resume re-runs interface and delay programming through `plat->resume`.

## State and Persistence
Per-device state lives in `bsp_priv`. Persistent hardware state is in PERICFG interface and delay registers plus enabled clock tree state. The delay fields are temporarily converted from picoseconds to register stages and converted back after programming, so the private structure remains in picoseconds after init.

## Dependencies and Integration Points
The driver depends on syscon/regmap, clk bulk APIs, stmmac DT helpers, stmmac safety feature structures, and OF properties. Compatible strings are `mediatek,mt2712-gmac` and `mediatek,mt8195-gmac`.

## Risks and Edge Cases
- Delay values must be below variant-specific maxima; equality with the max is rejected.
- `clk_prepare_enable(NULL)` for absent `rmii_internal_clk` relies on common clk API tolerance.
- `mediatek_dwmac_common_data()` returns `-ENOMEM`, but probe does not check that return value in the current code path.
- Interface/delay programming errors from the initial `mediatek_dwmac_init()` call are not checked in probe.
- RMII delay semantics differ depending on whether the MAC or PHY provides the reference clock.

## Test Signals
Tests should validate MT2712 and MT8195 RGMII/MII/RMII combinations, delay rounding and inversion bits, invalid delay rejection, RMII internal-clock and external RXC/TXC cases, MAC-vs-PHY WOL behavior, clock disable on probe failure/remove, and TBS enablement on queues above TXQ0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-mediatek.c -->
