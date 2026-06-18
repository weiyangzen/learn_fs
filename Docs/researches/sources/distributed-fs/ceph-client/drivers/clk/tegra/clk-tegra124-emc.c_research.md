<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124-emc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124-emc.c

Purpose: Common Clock Framework clock for Tegra124 external memory controller frequency switching. It loads EMC timing tables from DT, coordinates timing transitions with the external EMC driver, and programs the CAR EMC source/divider register safely.

Important APIs, types, and functions: exported `tegra124_clk_register_emc()`, `tegra124_clk_set_emc_callbacks()`, and `tegra124_clk_emc_driver_available()` are the integration surface. Internal types are `struct emc_timing` and `struct tegra_clk_emc`. CCF callbacks are `emc_recalc_rate()`, `emc_determine_rate()`, `emc_get_parent()`, and `emc_set_rate()`.

Control flow: registration scans CAR DT child nodes with `nvidia,ram-code`, loads timing children via `load_timings_from_dt()`, sorts each RAM-code group by rate, stores a phandle to `nvidia,external-memory-controller`, registers critical clock `"emc"`, records the current parent, and registers a debug clkdev alias. Rate determination selects the lowest timing for the current RAM code that satisfies the request, preferring upward rounding unless constrained by max rate. `emc_set_rate()` finds an exact timing; if the new timing uses the same underlying clock source but requires a different parent rate, it first switches to a backup timing with a different source. `emc_set_timing()` gets the external EMC driver and callbacks, sets/enables the parent, calls prepare, writes mux/divider under lock, calls complete, reparents CCF state, disables the old parent, and updates `prev_parent`.

State and persistence: state includes DT-loaded timing table, `prev_parent`, `changing_timing` recursion guard, callback pointers, retained EMC device node until first use, and cached external `tegra_emc`. Hardware state is `CLK_SOURCE_EMC`. The clock is critical because disabling memory clocking would break the system.

Dependencies and integration: called by Tegra124/132 CAR init; the custom OF clock provider defers consumers until `tegra124_clk_emc_driver_available()` is true. Depends on `tegra_read_ram_code()`, DT timing schema, external EMC driver callbacks, CCF parent/rate APIs, and CAR lock.

Risks and test signals: risks are missing or malformed DT timings, no backup timing for same-source parent-rate changes, callbacks not registered, parent rate mismatch, leaked parent clk refs on partial failures, and integer divider truncation. Test every RAM-code timing, exact and rounded rate requests, callback defer behavior, backup timing path, suspend/resume memory stability, and clock summary parent/rate after transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124-emc.c -->
