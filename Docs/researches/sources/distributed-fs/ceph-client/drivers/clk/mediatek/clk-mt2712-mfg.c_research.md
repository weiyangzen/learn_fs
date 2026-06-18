<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-mfg.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-mfg.c

### Purpose
This driver registers the MT2712 MFG/GPU gate clock.

### Important APIs, Types, And Functions
It defines `mfg_cg_regs`, `GATE_MFG`, `mfg_clks[]`, `mfg_desc`, and an OF platform driver for `mediatek,mt2712-mfgcfg`.

### Control Flow, State, And Persistence
Simple probe registers the single GPU gate. Gate state persists in the MFGCFG register block.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on GPU consumers and the top-level `mfg_sel` clock. Risks include a wrong gate bit preventing GPU initialization. Test signals include GPU driver probe, runtime GPU clocks, and debugfs gate state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-mfg.c -->
