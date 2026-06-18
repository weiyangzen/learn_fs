# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-mfg.c

## Purpose
`clk-mt8188-mfg.c` provides the MT8188 GPU manufacturing/MFG clock gate provider.

## Important APIs, Types, And Functions
It defines `mfgcfg_cg_regs`, one `mfgcfg_clks` gate using `CLK_SET_RATE_PARENT`, and `mfgcfg_desc`. The platform driver matches `mediatek,mt8188-mfgcfg` and uses `mtk_clk_simple_probe()`/`remove()`.

## Control Flow, State, And Persistence
The common probe registers the MFG gate and publishes it as an OF clock provider. `CLK_SET_RATE_PARENT` lets GPU clock changes propagate to the selected parent path. There is no custom state beyond the registered clock.

## Dependencies, Integration Points, Risks, And Test Signals
The file integrates with GPU/devfreq consumers and topckgen MFG mux handling. Risks include rate propagation bugs, wrong gate polarity, or topckgen notifier mismatch leading to GPU hangs during PLL changes. Test signals include GPU driver clock acquisition, rate changes, devfreq transitions, and clean disable on GPU idle.
