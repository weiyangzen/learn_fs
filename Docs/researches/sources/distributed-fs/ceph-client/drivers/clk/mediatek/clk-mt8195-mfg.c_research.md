# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-mfg.c

## Purpose
`clk-mt8195-mfg.c` provides the MT8195 GPU MFG clock gate.

## Important APIs, Types, And Functions
It defines `mfg_cg_regs`, one `mfg_clks` entry using `CLK_SET_RATE_PARENT`, `mfg_desc`, and an OF match for `mediatek,mt8195-mfgcfg`.

## Control Flow, State, And Persistence
The simple MediaTek probe registers the MFG gate and publishes it to OF. Rate requests can propagate to the parent clock. No custom state is present.

## Dependencies, Integration Points, Risks, And Test Signals
Integration is with GPU drivers and MT8195 topckgen MFG mux notifier behavior. Risks include GPU hangs during clock-rate changes or wrong gate polarity. Test signals include GPU probe, devfreq transitions, idle gating, and suspend/resume.
