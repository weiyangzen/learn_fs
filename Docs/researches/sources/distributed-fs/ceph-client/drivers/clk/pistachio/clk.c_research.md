# sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk.c

Purpose: Provides shared Pistachio clock-provider allocation and descriptor registration helpers for gates, muxes, dividers, fixed factors, PLLs, and critical clock enabling.

Important APIs, types, and functions: `pistachio_clk_alloc_provider()` allocates provider state, one-cell array, and maps the DT node. `pistachio_clk_register_provider()` warns about failed entries and adds an OF one-cell provider. `pistachio_clk_register_gate()`, `_mux()`, `_div()`, `_fixed_factor()`, and `_force_enable()` perform CCF registrations from descriptor arrays.

Control flow: SoC init files allocate a provider, register descriptor arrays, publish the provider, and optionally force-enable critical clocks. Mux width is computed from number of parents using `get_count_order()`.

State and persistence: Provider memory and clock array are allocated with `kzalloc()` and intentionally persist for early clock providers. The MMIO mapping persists in `p->base`. Clock state is hardware-backed.

Dependencies and integration points: Consumed by `clk-pistachio.c` and `clk-pll.c`. Depends on OF address mapping and CCF registration functions.

Risks: No cleanup path exists after partial registration failures, which is common for early clock providers but means failed entries remain in the provider array. Gate/mux/div registrations use no lock. `pistachio_clk_register_provider()` warns on `IS_ERR()` entries but still publishes the provider.

Test signals: Provider allocation failure should prevent registration cleanly. Boot logs should warn for failed individual clocks. Consumers should resolve clock IDs through `of_clk_src_onecell_get`. Critical force-enable errors should be logged with clock names.
