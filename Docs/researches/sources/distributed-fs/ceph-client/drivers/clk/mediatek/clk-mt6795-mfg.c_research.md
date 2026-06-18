# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-mfg.c

## Purpose

This small MT6795 MFG clock driver registers GPU/manufacturing subsystem gates. It provides bus AXI, memory, 3D engine, and 26 MHz gates for the `"mediatek,mt6795-mfgcfg"` clock provider.

## Important APIs, types, and functions

The driver defines `mfg_cg_regs`, `GATE_MFG()`, `mfg_clks[]`, `mfg_desc`, and `of_match_clk_mt6795_mfg[]`. It uses the generic `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()` platform-driver callbacks with `struct mtk_clk_desc`.

## Control flow, state, and persistence

The generic probe maps the clock controller, allocates onecell data sized from `mfg_desc`, registers the four gates, and adds an OF clock provider. Gate operations use set/clear registers at `0x4` and `0x8` and status at `0x0` with normal set/clear semantics. The only state is common-clock registration and hardware gate bits until reset.

## Dependencies and integration points

Dependencies are `clk-gate.h`, `clk-mtk.h`, Linux platform device support, and MT6795 clock bindings. The MFG gates depend on topckgen parents `axi_mfg_in_sel`, `mem_mfg_in_sel`, `mfg_sel`, and `clk26m`. GPU and power-domain code consume these clocks during MFG power-up.

## Risks and test signals

Risks are limited but include wrong parent names, wrong gate shifts, and enabling GPU clocks before MFG power domains are ready. Test with GPU probe/runtime PM, `clk_summary`, and suspend/resume transitions that gate and ungate the MFG domain.
