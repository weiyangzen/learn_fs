# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clkc.c

Purpose: probes the ZynqMP/Versal firmware clock database and registers a one-cell CCF provider containing all valid output clocks.

Important APIs/types/functions: `struct zynqmp_clock`, `struct clock_parent`, firmware response structs, `zynqmp_pm_clock_get_num_clocks()`, `_get_name()`, `_get_topology()`, `_get_parents()`, `_get_attributes()`, `zynqmp_clk_map_common_ccf_flags()`, `zynqmp_get_clock_info()`, `zynqmp_register_clocks()`, and the platform driver matching `xlnx,zynqmp-clk`/`xlnx,versal-clk`.

Control flow: probe calls `zynqmp_clk_setup()`, which queries the clock count, allocates `zynqmp_data` and the `clock` array, gathers attributes/names/topology/parents for each valid clock, registers output clocks by walking each topology node, and finally calls `of_clk_add_hw_provider()`.

State and persistence: global `clock`, `zynqmp_data`, and `clock_max_idx` persist for the driver lifetime. Runtime clock state remains in PM firmware; Linux stores discovered names, parent lists, topology nodes, and registered `clk_hw` pointers.

Dependencies and integration points: depends on ZynqMP PM query ABI, OF clock provider APIs, CCF, and the local PLL/divider/mux/gate/fixed-factor registration helpers.

Risks: firmware response parsing is tightly bound to bitfield layouts. Parent-name mutation uses `strcat()` into fixed buffers and assumes firmware names plus postfixes fit. `__zynqmp_clock_get_parents()` indexes the passed response slice, so caller offset handling must stay correct. Intermediate names allocated with `kasprintf()` are freed after registration, relying on CCF copying names as expected.

Test signals: boot-time clock registration count, `clk_summary`, firmware topology fuzz/compatibility, external parent resolution through `clock-names`, and probe failure tests for allocation or PM query errors.
