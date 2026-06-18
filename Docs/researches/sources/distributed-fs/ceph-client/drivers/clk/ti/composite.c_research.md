# sources/distributed-fs/ceph-client/drivers/clk/ti/composite.c

Purpose: TI composite clock assembly. It collects separately declared mux/divider/gate component clocks and registers one CCF composite clock when all referenced components are available.

Important APIs/types/functions: `of_ti_composite_clk_setup()` for `ti,composite-clock`, `ti_clk_add_component()`, `_register_composite()`, and internal `component_clk`/`clk_hw_omap_comp`. Composite divider ops delegate recalc to `ti_clk_divider_ops` but reject rate changes in this wrapper; composite gate ops use default OMAP gate enable/disable.

Control flow: component setup files call `ti_clk_add_component()` to store component `clk_hw`, parent names, node pointer, and type. Composite setup records component phandle nodes and calls `_register_composite()`. If a component is missing, registration enters the TI retry list. Once all components are present, it chooses parent names from the highest-priority available component, calls `clk_register_composite()`, adds an alias/provider, and frees component list entries.

State and persistence: pending component list entries persist until consumed. The final composite clock persists in CCF; temporary assembly structs are freed after registration.

Dependencies/integration: integrates with `divider.c`, `mux.c`, and `gate.c` composite component declarations, OF phandles, TI retry init, and CCF composite registration.

Risks: duplicate component types or missing parents abort registration. Component entries are removed and freed when consumed, so a component node cannot safely be shared by multiple composites. Rate changes for composite dividers are intentionally disabled.

Test signals: DT composite-clock nodes with delayed component registration, duplicate/missing component negative tests, provider lookup by composite node, and parent/rate behavior through mux/divider/gate subcomponents.
