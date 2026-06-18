# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-apmixed.c

## Purpose

This MT7986 apmixedsys driver registers eight PLLs similar to MT7981: ARM, NET2, MM, SGM, WEDMCU, NET1, MPLL, and APLL2. It is a built-in PLL provider.

## Important APIs, types, and functions

Important elements are `PLL_xtal()`, `PLL()`, `plls[]`, `clk_mt7986_apmixed_probe()`, and the compatible `"mediatek,mt7986-apmixedsys"`. It uses `mtk_alloc_clk_data()`, `mtk_clk_register_plls()`, and `of_clk_add_hw_provider()`.

## Control flow, state, and persistence

Probe allocates clock data sized by the PLL array, registers all PLLs, and publishes the OF provider. On provider failure it frees the data but does not unregister PLLs. State is CCF registration and PLL hardware control until reset.

## Dependencies and integration points

Dependencies include MT7986 clock bindings, `clk-pll.h`, `clk-mtk.h`, and the `clkxtal` parent. Topckgen consumes these PLLs for networking, memory, multimedia, WED, SGMII, and audio-derived clocks.

## Risks and test signals

Risks are array-size/ID assumptions, PLL field mistakes, and missing cleanup on provider failure. Test boot, topckgen rates, Ethernet/WED throughput, SGMII, and audio users.
