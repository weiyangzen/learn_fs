<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-imgsys.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-imgsys.c

### Purpose
This file registers MT6735 image subsystem gates.

### Important APIs, Types, And Functions
It defines `IMG_CG_*` offsets, `imgsys_cg_regs`, `imgsys_gates[]`, `imgsys_clks`, and a simple driver for `mediatek,mt6735-imgsys`.

### Control Flow, State, And Persistence
Simple probe registers the image gate table and provider; remove uses `mtk_clk_simple_remove()`. Gate state persists in IMGSYS set/clear/status registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on MT6735 image consumers, binding IDs, and the common gate framework. Risks include parent name mismatches and bit-shift mistakes. Test signals include image/camera pipeline clock requests and gate toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-imgsys.c -->
