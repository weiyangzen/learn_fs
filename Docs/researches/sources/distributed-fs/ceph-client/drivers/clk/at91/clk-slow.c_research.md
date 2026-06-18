# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-slow.c

Purpose: legacy SAM9260 slow-clock mux provider exposing which slow-clock parent hardware selected.

Important APIs and data: `at91_clk_register_sam9260_slow()` registers a clock with two parents and `sam9260_slow_ops`. The private struct stores regmap and `clk_hw`.

Control flow: get_parent reads `AT91_PMC_SR` and returns parent 1 when `AT91_PMC_OSCSEL` is set, otherwise parent 0. Registration validates name and parent array, then registers the clock.

State and persistence: no mutable software state beyond the regmap pointer; parent selection is hardware-owned. No set_parent or save/restore hooks are provided.

Dependencies and integration: used by legacy DT compat `"atmel,at91sam9260-clk-slow"` rather than the newer SCKC slow-clock provider. It depends on syscon/regmap access to PMC status.

Risks: read-only parent reporting means Linux cannot switch the source through this provider; invalid parent count aborts setup. Test signals include correct slow clock parent in clk_summary and matching `OSCSEL` hardware status.
