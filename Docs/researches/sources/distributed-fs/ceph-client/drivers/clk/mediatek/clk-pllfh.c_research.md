# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pllfh.c

Purpose: `clk-pllfh.c` extends the MediaTek PLL framework with FHCTL frequency-hopping support. When a PLL has enabled FHCTL state from device tree, it registers the PLL with normal prepare/recalc/determine operations but routes rate changes through FHCTL hopping operations instead of direct PCW writes.

Important APIs and functions: `to_mtk_fh()` converts from PLL clock hardware to the enclosing `struct mtk_fh`. `fhctl_parse_dt()` parses a compatible FHCTL node and updates the caller-provided `mtk_pllfh_data` array. `mtk_clk_register_pllfhs()` bulk-registers a mixed set of FHCTL-backed PLLs and normal PLLs. `mtk_clk_unregister_pllfhs()` unregisters both variants and unmaps MMIO bases.

Control flow: `fhctl_parse_dt()` finds the FHCTL node, maps its registers, counts clock parents, reads paired `clocks` cells to find PLL IDs, reads `mediatek,hopping-ssc-percent`, and marks matching `mtk_pllfh_data` entries enabled with the FHCTL base and SSC rate. Registration maps the normal PLL provider base, walks each PLL descriptor, locates matching FH data, and either calls `mtk_clk_register_pllfh()` or falls back to `mtk_clk_register_pll()`. FH registration allocates `struct mtk_fh`, initializes register pointers from the FHCTL offset table, registers the embedded PLL with `mtk_pllfh_ops`, then calls `fhctl_hw_init()`.

State and persistence: state is held in the mutable `mtk_pllfh_data.state` entries, the FHCTL MMIO mapping, the normal PLL MMIO mapping, and allocated `struct mtk_fh` objects. No data survives reboot.

Dependencies and integration points: this file depends on `clk-pll.h`, `clk-pllfh.h`, and `clk-fhctl.h`. It integrates the common PLL CCF path with FHCTL operations returned by `fhctl_get_ops()` and offset tables returned by `fhctl_get_offset_table()`.

Risks: FHCTL enablement is parsed by matching PLL IDs from a DT `clocks` property; incorrect cell layout or missing SSC entries leaves PLLs using normal direct programming. `fhctl_parse_dt()` maps one FHCTL base and shares it across enabled PLL entries; unregister only unmaps a stored `fhctl_base` if at least one enabled FH PLL was registered. `mtk_clk_register_pllfhs()` does not check duplicate onecell IDs before assignment. Error unwind must choose the same FH-vs-normal path as registration, so descriptor/state drift can leak or unregister incorrectly.

Test signals: validate DT parsing with enabled and absent FHCTL nodes, check SSC rates appear in `pllfh_data.state`, confirm `clk_set_rate()` calls FH hopping through hardware behavior or tracepoints, verify fallback normal PLLs still change rate, and exercise probe-failure unwind with mixed FH and non-FH PLLs.
