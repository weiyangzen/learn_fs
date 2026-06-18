# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-apmixedsys.c

## Purpose
`clk-mt8192-apmixedsys.c` registers MT8192 analog mixed-signal PLL clocks and AP mixed gates. It is the PLL/root-frequency provider for the rest of the MT8192 clock tree.

## Important APIs, Types, And Functions
The file defines `apmixed_cg_regs`, `apmixed_clks`, `plls`, and frequency-hopping metadata `pllfhs`. `clk_mt8192_apmixed_probe()` allocates `CLK_APMIXED_NR_CLK` storage, registers PLLFH-backed PLLs with `mtk_clk_register_pllfhs()`, registers gates, and publishes an OF provider for `mediatek,mt8192-apmixedsys`.

## Control Flow, State, And Persistence
Probe creates clock data, registers PLLFH PLLs before gates, adds the OF provider, and stores driver data. Failures unwind gates, PLLFH registrations, and clock data. Remove deletes the provider and unregisters gates and PLLFH clocks.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `clk-pllfh`, `clk-mtk`, MT8192 PLL IDs, and topckgen consumers. Risks are significant because PLL table errors affect all derived rates; missing unwind can leave published root clocks inconsistent. Test signals include boot rate summaries, frequency-hopping behavior if enabled, parent rates for topckgen, and module remove/reprobe in test kernels.
