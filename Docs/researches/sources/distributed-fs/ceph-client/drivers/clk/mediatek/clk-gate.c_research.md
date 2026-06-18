<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-gate.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-gate.c

### Purpose
`clk-gate.c` implements the shared MediaTek gate clock primitive. It supports set/clear/status register layouts, no-setclr read-modify-write layouts, inverted enable polarity, and hardware-voter gate operations.

### Important APIs, Types, And Functions
`struct mtk_clk_gate` stores `clk_hw`, normal and hardware-voter regmaps, and a `struct mtk_gate` descriptor. Exported ops include `mtk_clk_gate_ops_setclr`, `_setclr_inv`, `_no_setclr`, `_no_setclr_inv`, `mtk_clk_gate_hwv_ops_setclr`, and `_hwv_ops_setclr_inv`. Exported registration APIs are `mtk_clk_register_gates()` and `mtk_clk_unregister_gates()`.

### Control Flow, State, And Persistence
Registration resolves a DT node to a regmap and optional hardware-voter regmap, validates duplicate clock IDs, registers each gate with `CLK_SET_RATE_PARENT`, and stores the `clk_hw`. Enable/disable functions either write set/clear registers or update the status register directly, with polarity determined by selected ops. Hardware-voter enable/disable writes HWV set/clear registers and polls done status. Gate state persists in hardware registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on CCF, regmap/syscon, `mtk_clk_get_hwv_regmap()`, `clk-mtk.h`, and `clk-gate.h`. Risks include returning from `mtk_clk_register_gate()` without freeing `cg` if HWV ops lack a regmap, polarity descriptor mistakes, timeout from hardware voters, and partial registration unwinds. Test signals include gate toggles across all ops variants, duplicate-ID warnings, HWV regmap error handling, and `mtk_clk_simple_remove()` unregister paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-gate.c -->
