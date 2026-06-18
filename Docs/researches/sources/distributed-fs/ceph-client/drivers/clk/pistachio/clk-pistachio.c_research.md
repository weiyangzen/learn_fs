# sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk-pistachio.c

Purpose: Describes and registers the IMG Pistachio clock topology across the main clock controller, peripheral clock controller, CR peripheral gates, and CR top external gates.

Important APIs, types, and functions: Descriptor arrays define main gates, fixed factors, dividers, muxes, fixed PLLs, peripheral gates/dividers, system gates, and external gates. Init functions `pistachio_clk_init()`, `pistachio_clk_periph_init()`, `pistachio_cr_periph_init()`, and `pistachio_cr_top_init()` are bound with `CLK_OF_DECLARE()` compatibles. `pistachio_clk_force_enable()` keeps critical clocks on.

Control flow: Each init allocates a provider for its clock count, registers the relevant descriptor arrays through helper functions, registers the OF provider, and optionally force-enables critical clocks. The main controller also registers a debug mux with an explicit mux table.

State and persistence: Descriptor arrays are `__initdata`; registered CCF clocks and provider storage persist. Hardware state resides in MMIO registers. Critical clock enable counts persist after init.

Dependencies and integration points: Depends on `dt-bindings/clock/pistachio-clk.h`, helper functions from `clk.c` and `clk-pll.c`, and DT nodes with compatible strings `"img,pistachio-clk"`, `"img,pistachio-clk-periph"`, `"img,pistachio-cr-periph"`, and `"img,pistachio-cr-top"`.

Risks: The topology is table-driven; wrong IDs, offsets, shifts, or parent names create silent miswiring. Main PLLs are registered as fixed-parameter PLLs with no rate tables, so they expose current hardware rates but cannot be changed. Critical clocks must be force-enabled or the system can lose CPU/peripheral/DDR/ROM clocks.

Test signals: Boot should expose all four providers. `clk_summary` should show `mips`, core system clocks, peripheral gates, and external input gates. Critical clocks should be enabled even with no consumers. Debug mux parent selection should match the `mux_debug_idx` table.
