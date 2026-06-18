<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-ipe.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-ipe.c

### Purpose
This file registers MT6779 Image Processing Engine subsystem gates.

### Important APIs, Types, And Functions
It defines `ipe_cg_regs`, `GATE_IPE`, `ipe_clks[]`, `ipe_desc`, and a simple driver for `mediatek,mt6779-ipesys`.

### Control Flow, State, And Persistence
Simple probe registers IPE gates and the onecell provider. Gate state persists in IPESYS registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on image/camera processing consumers and top-level image parents. Risks include disabled IPE/LARB clocks during camera processing. Test signals include camera/IPE workloads and CCF gate state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-ipe.c -->
