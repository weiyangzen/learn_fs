<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-mm.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-mm.c

### Purpose
This driver registers MT6765 multimedia/display subsystem gates.

### Important APIs, Types, And Functions
It defines `mm_cg_regs`, `GATE_MM`, `mm_clks[]`, `mm_desc`, and a simple platform driver for `mediatek,mt6765-mmsys`.

### Control Flow, State, And Persistence
Simple probe registers MMSYS gates. Gate state persists in the multimedia set/clear/status registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on display/MDP consumers, `mm_ck`, and common gate code. Risks include disabling display pipeline clocks and wrong parent propagation. Test signals include display probe, frame updates, MDP workloads, and clock summary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-mm.c -->
