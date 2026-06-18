<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-cam.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-cam.c

### Purpose
This file registers MT6765 camera subsystem gate clocks.

### Important APIs, Types, And Functions
It defines `cam_cg_regs`, `GATE_CAM`, `cam_clks[]`, `cam_desc`, and a simple driver for `mediatek,mt6765-camsys`.

### Control Flow, State, And Persistence
Simple probe publishes CAMSYS gates; runtime clock enable/disable manipulates the CAM register bank.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on camera sensor/image pipeline consumers and top-level camera muxes. Risks include gate bit mistakes and missing sensor interface clocks. Test signals include camera pipeline probe, streaming, and clock debugfs state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-cam.c -->
