# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7629.c

## Purpose

This is the combined MT7629 clock driver for apmixedsys, infracfg, topckgen, and pericfg. It registers PLLs, fixed clocks, factors, muxes, infra/peri gates, CPU muxes, and a peribus mux for a networking SoC.

## Important APIs, types, and functions

Important data includes `plls[]`, `apmixed_clks[]`, `infra_clks[]`, `top_fixed_clks[]`, `top_divs[]`, `peri_clks[]`, `infra_muxes[]`, `top_muxes[]`, and `peri_muxes[]`. Init functions are `mtk_topckgen_init()`, `mtk_infrasys_init()`, `mtk_pericfg_init()`, and `mtk_apmixedsys_init()`, selected by `clk_mt7629_probe()` from OF match data.

## Control flow, state, and persistence

The `arch_initcall` registers a platform driver for four compatible strings. Topckgen maps MMIO, registers fixed clocks/factors/composites, then explicitly prepares and enables AXI, memory, and DDRPHYCFG muxes before publishing the provider. Infracfg registers gates and CPU muxes. Pericfg registers gates and the peribus mux, publishes provider, and enables UART0. APMIXED registers PLLs/gates and enables ARMPLL plus `main_core_en`. State includes enabled critical clocks, CCF providers, and hardware registers.

## Dependencies and integration points

Dependencies include `clk-cpumux.h`, `clk-gate.h`, `clk-mtk.h`, `clk-pll.h`, and MT7629 clock bindings. It feeds Ethernet, SGMII, HIF/PCIe/USB, flash, MMC, crypto, serial, SPI, and peripheral consumers.

## Risks and test signals

Risks include explicit `clk_prepare_enable()` calls without cleanup, critical bus clocks not marked through flags, match-data dispatcher errors, and sparse error unwinding. Test boot, clock summary, Ethernet/SGMII, PCIe/USB, flash/MMC, UART console, and suspend/resume.
