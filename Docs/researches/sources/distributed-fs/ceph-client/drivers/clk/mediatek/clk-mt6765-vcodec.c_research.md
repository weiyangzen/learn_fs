<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-vcodec.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-vcodec.c

### Purpose
This file registers MT6765 video codec subsystem gates.

### Important APIs, Types, And Functions
It defines `venc_cg_regs`, `GATE_VENC`, `venc_clks[]`, `venc_desc`, and a simple driver for `mediatek,mt6765-vcodecsys`.

### Control Flow, State, And Persistence
Simple probe publishes the video codec clock provider. Gate state persists in VCODECSYS registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on video codec consumers and top-level multimedia/video parents. Risks include bit-shift mismatches and codec DMA failures from disabled clocks. Test signals include encoder/decoder probe and media workload clock activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-vcodec.c -->
