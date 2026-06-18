# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk.c

Purpose: shared table-driven registration utilities for MMP clock providers.

Important APIs/functions: `mmp_clk_init` creates an OF onecell clock table. `mmp_register_fixed_rate_clks`, `mmp_register_fixed_factor_clks`, `mmp_register_general_gate_clks`, `mmp_register_gate_clks`, `mmp_register_mux_clks`, and `mmp_register_div_clks` register arrays of parameter structs. `mmp_clk_add` inserts an arbitrary registered clock into a provider table.

Control flow: SoC files call `mmp_clk_init`, then invoke table helpers with base MMIO pointers. Each helper loops over its descriptor array, registers a CCF clock, logs failures, and stores successful nonzero IDs in `unit->clk_table`.

State and persistence: `mmp_clk_unit` owns the clock pointer table and onecell metadata; the clocks and providers persist after init. No unregister path is implemented here.

Dependencies and integration: CCF fixed-rate/fixed-factor/gate/mux/divider registration, OF onecell providers, `clk.h` descriptor types, and MMP custom gate APIs.

Risks: ID zero is never stored, so descriptor authors must reserve zero for non-exported internal clocks. Failed registrations only log and continue, which can produce partially populated providers. `mmp_clk_init` returns void, so callers may continue after allocation/provider failure.

Test signals: static table ID audits, `of_clk_get_by_name` and by index, boot log failure scans, and checking that provider `clk_num` matches binding maximums.
