<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-img.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-img.c

### Purpose
This driver registers MT6765 image subsystem gates.

### Important APIs, Types, And Functions
It defines `img_cg_regs`, `GATE_IMG`, `img_clks[]`, `img_desc`, and a simple driver for `mediatek,mt6765-imgsys`.

### Control Flow, State, And Persistence
Simple probe registers image gates and provider. Gate state persists in IMGSYS registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on image processing consumers and `mm_ck`/top-level parents. Risks include wrong bit shifts and missing image clocks. Test signals include image pipeline use and CCF gate state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765-img.c -->
