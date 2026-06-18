<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-vdecsys.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-vdecsys.c

### Purpose
This driver registers MT6735 video decoder gates, including decoder and SMI/LARB related gates.

### Important APIs, Types, And Functions
It defines `vdec_cg_regs`, `smi_larb1_cg_regs`, `vdecsys_gates[]`, `vdecsys_clks`, and a simple driver for `mediatek,mt6735-vdecsys`.

### Control Flow, State, And Persistence
Simple probe registers VDECSYS gates and remove unregisters them. Gate state persists in decoder and SMI LARB register banks.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on video decoder and memory interconnect consumers. Risks include missing LARB gates causing DMA faults and wrong bank offsets. Test signals include decoder probe, media decode workloads, and SMI/larb clock dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-vdecsys.c -->
