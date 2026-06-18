# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-mfg.c

## Purpose
`clk-mt8192-mfg.c` provides the MT8192 GPU MFG clock gate.

## Important APIs, Types, And Functions
The file defines `mfg_cg_regs`, one `mfg_clks` gate with `CLK_SET_RATE_PARENT`, `mfg_desc`, and the `mediatek,mt8192-mfgcfg` OF match.

## Control Flow, State, And Persistence
The simple helper registers the MFG gate and publishes it to OF. Rate changes may propagate to the parent because of the gate flag. State is limited to the registered clock and gate bit.

## Dependencies, Integration Points, Risks, And Test Signals
Integration is with GPU drivers and the MT8192 topckgen MFG mux notifier. Risks include GPU hangs during rate switch if parent bypass/notifier behavior is wrong. Test signals include GPU probe, devfreq rate changes, and idle clock gating.
