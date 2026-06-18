# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622.c

## Purpose

This MT7622 top/peripheral clock driver registers topckgen clocks and pericfg gates/muxes/resets. It provides central fixed clocks, PLL factors, top gates, adjustable audio dividers, top muxes, peripheral gates, and a peribus mux.

## Important APIs, types, and functions

Important data includes parent arrays for AXI, memory, Ethernet, flash, audio, USB, and peripheral paths; `top_fixed_clks[]`, `top_divs[]`, `top_clks[]`, `top_adj_divs[]`, `peri_clks[]`, `top_muxes[]`, `peri_muxes[]`, `clk_rst_desc`, `topck_desc`, and `peri_desc`. The OF table maps `"mediatek,mt7622-topckgen"` and `"mediatek,mt7622-pericfg"` to descriptors for `mtk_clk_simple_probe()`.

## Control flow, state, and persistence

The generic probe registers either the full top descriptor or pericfg descriptor. Topckgen includes fixed clocks for USB/PCIe/SATA/SGMII references, many PLL factors, no-setclr top gates, adjustable dividers, and composite muxes under `mt7622_clk_lock`. Pericfg registers set/clear peripheral gates, one peribus mux, and a two-bank simple reset controller. State is hardware clock/reset state and CCF provider state.

## Dependencies and integration points

Dependencies are `clk-cpumux.h`, `clk-gate.h`, `clk-mtk.h`, MT7622 bindings, and Linux clock consumer helpers. It integrates with apmixed PLLs, infracfg, Ethernet, HIF, audio, serial, SPI, flash/NFI, MMC, USB, and reset consumers. Critical top muxes include AXI, memory, and DDRPHYCFG.

## Risks and test signals

Risks include top/peri descriptor mismatches, parent-order errors, critical flag loss, and reset-bank offset mistakes. Test boot, Ethernet/HIF/audio/peripheral devices, flash and MMC, peribus mux rate, and idle-clock disable.
