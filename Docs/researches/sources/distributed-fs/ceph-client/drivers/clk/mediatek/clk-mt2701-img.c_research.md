<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-img.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-img.c

### Purpose
This file provides MT2701 IMGSYS gates for image-processing paths.

### Important APIs, Types, And Functions
It defines `img_cg_regs`, `GATE_IMG`, `img_clks[]`, `img_desc`, and an OF platform driver matching `mediatek,mt2701-imgsys`.

### Control Flow, State, And Persistence
`mtk_clk_simple_probe()` registers the gate descriptors as a onecell provider. Gate state is persisted by the IMGSYS set/clear/status registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on image pipeline consumers, DT clock IDs, and `clk-gate`. Risks include wrong parent `mm_sel`/multimedia source assumptions and missing gates for imaging blocks. Test signals include camera/image pipeline probe, CCF lookup by DT index, and runtime gate toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-img.c -->
