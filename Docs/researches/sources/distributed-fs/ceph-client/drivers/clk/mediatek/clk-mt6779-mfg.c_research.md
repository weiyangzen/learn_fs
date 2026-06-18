<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-mfg.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-mfg.c

### Purpose
This driver registers the MT6779 MFG/GPU gate.

### Important APIs, Types, And Functions
It defines `mfg_cg_regs`, `GATE_MFG`, `mfg_clks[]`, `mfg_desc`, and a simple platform driver for `mediatek,mt6779-mfgcfg`.

### Control Flow, State, And Persistence
Simple probe publishes the GPU clock provider. Gate state persists in MFGCFG registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on GPU consumers and top-level MFG parent clocks. Risks are a wrong gate bit or parent name preventing GPU probe. Test signals include GPU initialization and runtime clock activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6779-mfg.c -->
