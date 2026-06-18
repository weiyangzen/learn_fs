<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-vdec.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-vdec.c

### Purpose
This driver registers MT2712 video decoder gates split across two register banks.

### Important APIs, Types, And Functions
It defines `vdec0_cg_regs`, `vdec1_cg_regs`, `GATE_VDEC0/1`, `vdec_clks[]`, `vdec_desc`, and an OF driver for `mediatek,mt2712-vdecsys`.

### Control Flow, State, And Persistence
Simple probe publishes VDEC gates. Enable/disable state persists in VDECSYS gate registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on video decoder consumers and `vdec_sel` parent clocks. Risks are incorrect bank selection and disabled LARB/decoder clocks during codec operation. Test signals include decoder probe, decode sessions, and clock debugfs state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-vdec.c -->
