# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-apmixed.c

## Purpose

This MT7981 apmixedsys driver registers eight PLLs for CPU, networking, multimedia, SGMII, WED MCU, memory, and audio. It is a built-in PLL root provider for router-class MT7981 systems.

## Important APIs, types, and functions

The file defines `PLL_xtal()`, `PLL()`, `plls[]`, `clk_mt7981_apmixed_probe()`, and `of_match_clk_mt7981_apmixed[]`. It uses `mtk_alloc_clk_data()`, `mtk_clk_register_plls()`, and `of_clk_add_hw_provider()`.

## Control flow, state, and persistence

Probe allocates onecell data sized to `ARRAY_SIZE(plls)`, registers PLLs, and publishes the provider. On provider failure it frees the clock data, but there is no PLL unregister path in that error branch. The driver is registered by `builtin_platform_driver()`. State is PLL hardware configuration and CCF provider registration.

## Dependencies and integration points

Dependencies are `clk-pll.h`, `clk-mux.h`, `clk-gate.h`, `clk-mtk.h`, MT7981 bindings, and `clkxtal` as parent. Topckgen uses PLL names such as `net1pll`, `net2pll`, `mmpll`, `mpll`, `sgmpll`, `wedmcupll`, and `apll2`.

## Risks and test signals

Risks include PCW field mistakes, array-size clock data depending on dense IDs, and missing unregister on provider failure. Test boot clock summary, topckgen parent rates, Ethernet/WED paths, and audio PLL users.
