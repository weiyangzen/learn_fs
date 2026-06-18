<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-vdec.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-vdec.c

### Purpose
This driver registers MT6779 video decoder gates across two decoder gate banks.

### Important APIs, Types, And Functions
It defines `vdec0_cg_regs`, `vdec1_cg_regs`, `GATE_VDEC0_I`, `GATE_VDEC1_I`, `vdec_clks[]`, `vdec_desc`, and a simple driver for `mediatek,mt6779-vdecsys`.

### Control Flow, State, And Persistence
Simple probe registers VDECSYS gates. Gate state persists in VDEC register banks.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on MT6779 video decoder consumers and top-level video parents. Risks include missing decoder/LARB gates and wrong inverted polarity assumptions. Test signals include decoder probe, decode workloads, and CCF gate activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-vdec.c -->
