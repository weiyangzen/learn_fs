<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-cpumux.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-cpumux.c

### Purpose
`clk-cpumux.c` registers MediaTek CPU clock muxes backed by syscon/regmap registers. It gives SoC clock drivers a CCF mux primitive for CPU parent selection while preserving no-reparent rate determination semantics.

### Important APIs, Types, And Functions
`struct mtk_clk_cpumux` stores `clk_hw`, `regmap`, register offset, mask, and shift. Exported APIs are `mtk_clk_register_cpumuxes()` and `mtk_clk_unregister_cpumuxes()`. Internal helpers are `clk_cpumux_get_parent()`, `clk_cpumux_set_parent()`, `mtk_clk_register_cpumux()`, and `mtk_clk_unregister_cpumux()`.

### Control Flow, State, And Persistence
Registration resolves the device node to a regmap, iterates `struct mtk_composite` descriptions, skips duplicate populated IDs, registers each mux, and stores the resulting `clk_hw` in `clk_hw_onecell_data`. On any failure it unregisters already-created muxes in reverse order and marks slots `ERR_PTR(-ENOENT)`. Parent state is read and written through bitfields in persistent SoC registers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on syscon/regmap, CCF, `struct mtk_composite`, and DT nodes that expose a regmap. Risks include bad mux widths producing wrong masks, duplicate clock IDs hiding descriptor mistakes, missing syscon setup, and CPU parent switches without voltage/frequency coordination. Test signals are CPU clock parent selection, duplicate-ID warnings, failure unwind coverage, and boot on MT2701/MT2712 CPU mux users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-cpumux.c -->
