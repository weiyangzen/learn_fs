<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-img.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-img.c

### Purpose
This driver registers MT2712 image subsystem gates.

### Important APIs, Types, And Functions
It defines `img_cg_regs`, `GATE_IMG`, `img_clks[]`, `img_desc`, and a simple platform driver for `mediatek,mt2712-imgsys`.

### Control Flow, State, And Persistence
The simple probe registers image gates and publishes the provider. Runtime gate state persists in IMGSYS registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on image/camera consumers and the shared gate framework. Risks include missing or incorrect `mm_sel` parent relationships and wrong gate polarity. Test signals include image pipeline probe, camera use, and clock summary gate state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-img.c -->
