<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-jpgdec.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-jpgdec.c

### Purpose
This file registers the MT2712 JPEG decoder subsystem gate.

### Important APIs, Types, And Functions
It defines `jpgdec_cg_regs`, `GATE_JPGDEC`, `jpgdec_clks[]`, `jpgdec_desc`, and a simple platform driver for `mediatek,mt2712-jpgdecsys`.

### Control Flow, State, And Persistence
Probe registers the JPEG decoder gate provider. The only meaningful runtime state is the gate bit in the JPGDEC register block.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on JPEG decoder consumers, DT bindings, and `clk-gate`. Risks are wrong parent `jpgdec_sel` or bit shift causing decoder access failures. Test signals are JPEG decoder probe/use and CCF enable/disable traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712-jpgdec.c -->
