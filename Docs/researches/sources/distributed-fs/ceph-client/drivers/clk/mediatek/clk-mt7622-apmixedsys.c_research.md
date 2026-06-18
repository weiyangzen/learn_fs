# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-apmixedsys.c

## Purpose

This MT7622 apmixedsys driver registers router SoC PLLs and a critical `main_core_en` gate. PLLs include ARM, main, universal, Ethernet, audio, TRG, and SGMII sources.

## Important APIs, types, and functions

The file defines `PLL_xtal()`, `PLL()`, `plls[]`, `apmixed_cg_regs`, `apmixed_clks[]`, `clk_mt7622_apmixed_probe()`, and `clk_mt7622_apmixed_remove()`. It uses `mtk_devm_alloc_clk_data()`, `mtk_clk_register_plls()`, `mtk_clk_register_gates()`, and `of_clk_add_hw_provider()`.

## Control flow, state, and persistence

Probe maps MMIO, allocates `CLK_APMIXED_NR_CLK`, registers PLLs, registers the critical inverted no-setclr `main_core_en` gate, and publishes the provider. Failure unwinds gates and PLLs. Remove deletes the provider and unregisters gates and PLLs. State is hardware PLL/gate programming and CCF registration.

## Dependencies and integration points

Dependencies include `clk-pll.h`, `clk-gate.h`, `clk-mtk.h`, and `dt-bindings/clock/mt7622-clk.h`. PLL parent names default to `clkxtal`. Topckgen and Ethernet/HIF/audio consumers depend on PLL names such as `mainpll`, `univ2pll`, `eth1pll`, `eth2pll`, `aud1pll`, `aud2pll`, and `sgmipll`.

## Risks and test signals

Risks include wrong reset-bar bit, critical gate polarity, and PLL parent-name mismatch. Test boot clock summary, Ethernet/SGMII rates, audio PLL users, CPU frequency path, and module removal if configured.
