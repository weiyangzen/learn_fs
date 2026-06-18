<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-vdec.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-vdec.c

### Purpose
This file registers MT2701 video decoder subsystem gates.

### Important APIs, Types, And Functions
It defines `vdec0_cg_regs`, `vdec1_cg_regs`, `GATE_VDEC0/1`, `vdec_clks[]`, `vdec_desc`, and a platform driver for `mediatek,mt2701-vdecsys`.

### Control Flow, State, And Persistence
Simple probe registers VDEC gates through `mtk_clk_simple_probe()`. Enable/disable state persists in the VDECSYS gate registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on video decoder consumers, DT IDs, and common gate helpers. Risks include wrong active-low polarity or parent `vdec_sel` mismatches causing decoder timeouts. Test signals include vcodec decoder probe, decode workload clocks, and debugfs clock state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-vdec.c -->
