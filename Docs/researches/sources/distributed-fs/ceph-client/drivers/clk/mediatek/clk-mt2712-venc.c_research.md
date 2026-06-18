<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-venc.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-venc.c

### Purpose
This file registers MT2712 video encoder gates.

### Important APIs, Types, And Functions
It defines `venc_cg_regs`, `GATE_VENC`, `venc_clks[]`, `venc_desc`, and a platform driver matching `mediatek,mt2712-vencsys`.

### Control Flow, State, And Persistence
Probe delegates to `mtk_clk_simple_probe()` to register VENC gates. Gate state persists in the VENC register block.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on video encoder consumers and the top-level `venc_sel` parent. Risks include wrong active-low gate behavior or missing encoder/LARB gating. Test signals include encoder probe, encode workloads, and CCF gate transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-venc.c -->
