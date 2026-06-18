<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-img.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-img.c

### Purpose
This driver registers MT6779 image subsystem gates.

### Important APIs, Types, And Functions
It defines `img_cg_regs`, `GATE_IMG`, `img_clks[]`, `img_desc`, and a simple OF platform driver for `mediatek,mt6779-imgsys`.

### Control Flow, State, And Persistence
Probe registers IMGSYS gates via `mtk_clk_simple_probe()`. Gate state persists in the IMGSYS register block.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on image processing consumers and common MediaTek gate code. Risks are wrong parent names and gate shift errors. Test signals include image pipeline probe and debugfs clock activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-img.c -->
