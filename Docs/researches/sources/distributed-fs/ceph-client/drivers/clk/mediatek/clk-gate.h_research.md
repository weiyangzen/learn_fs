<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-gate.h -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-gate.h

### Purpose
`clk-gate.h` defines the descriptor format and registration API for MediaTek gate clocks.

### Important APIs, Types, And Functions
It declares the exported gate ops, `struct mtk_gate_regs`, `struct mtk_gate`, `GATE_MTK_FLAGS()`, `GATE_MTK()`, `mtk_clk_register_gates()`, and `mtk_clk_unregister_gates()`.

### Control Flow, State, And Persistence
The header has no direct runtime behavior. Its macros produce constant gate descriptors consumed by `clk-gate.c` and by SoC-specific clock tables.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on kernel integer types and CCF declarations. Integration is broad: almost every subsystem clock file in this subset creates `struct mtk_gate` arrays through these macros. Risks are descriptor field omissions, wrong polarity ops, and stale declarations. Test signals are successful compilation and runtime gate registration for each SoC subsystem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-gate.h -->
