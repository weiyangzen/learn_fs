<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-mfgcfg.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-mfgcfg.c

### Purpose
This file registers MT6735 MFG/GPU configuration gates and reset metadata.

### Important APIs, Types, And Functions
It defines MFG gate offsets, `mfgcfg_cg_regs`, `mfgcfg_gates[]`, `mfgcfg_clks`, and an OF driver for `mediatek,mt6735-mfgcfg`.

### Control Flow, State, And Persistence
Simple probe registers the MFG clock provider and any descriptor reset support. Gate state persists in MFGCFG registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on GPU consumers and MT6735 binding IDs. Risks include wrong parent `mfg_sel` and gate polarity mistakes. Test signals include GPU probe, clock enable during rendering, and simple remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6735-mfgcfg.c -->
