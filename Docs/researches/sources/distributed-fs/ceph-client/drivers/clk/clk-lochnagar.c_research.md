# sources/distributed-fs/ceph-client/drivers/clk/clk-lochnagar.c

Purpose: Cirrus Logic Lochnagar board clock driver for Lochnagar 1 and 2 MFD variants. It exposes board clock outputs with selectable parents and enable bits via the parent regmap.

Important APIs, types, and functions: `lochnagar_clk` stores per-clock register/mask metadata and a `clk_hw`. `lochnagar_clk_priv` owns regmap and the fixed-size clock array. `lochnagar_config` selects parent lists and clock descriptions for Lochnagar 1 or 2. `lochnagar_clk_ops` implements prepare/unprepare and parent set/get. `lochnagar_of_clk_hw_get()` indexes clocks from DT phandles.

Control flow: probe allocates private data, obtains parent regmap, copies the variant clock table, initializes shared parent data, registers each named clock, then registers a custom OF provider. Prepare sets the enable mask in `cfg_reg`; unprepare clears it. Parent changes update `src_reg` with the raw parent index.

State and persistence: state is MFD register bits for enable and source selection. The copied clock array stores per-device metadata and backpointers. No persistent software state exists.

Dependencies and integration points: depends on Lochnagar MFD register definitions, DT clock bindings, regmap, platform driver matching, firmware parent names, and common clock APIs.

Risks and test signals: `get_parent()` returns `clk_hw_get_num_parents()` on regmap read failure, intentionally producing an invalid parent index. Source masks assume register values map directly to parent indexes. Probe assumes match data and parent regmap are valid. Test signals are variant-specific clock count/name registration, phandle index validation, enable bit writes, and parent switch register values.
