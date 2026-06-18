<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-venc.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-venc.c

### Purpose
This file registers MT6779 video encoder gates.

### Important APIs, Types, And Functions
It defines `venc_cg_regs`, `GATE_VENC_I`, `venc_clks[]`, `venc_desc`, and a simple OF platform driver for `mediatek,mt6779-vencsys`.

### Control Flow, State, And Persistence
Probe registers VENC gates through the common simple probe. Gate state persists in VENC register bits.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on video encoder consumers and the top-level video clock tree. Risks include gate shift mistakes and disabled clocks during encode sessions. Test signals include encoder probe/workload and `clk_summary` transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-venc.c -->
