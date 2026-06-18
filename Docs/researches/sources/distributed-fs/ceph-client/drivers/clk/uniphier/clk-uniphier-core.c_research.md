# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-core.c

Purpose: common UniPhier platform clock provider. It selects a SoC clock-data array by compatible string, gets the parent syscon regmap, registers each described clock, and publishes a onecell OF clock provider.

Important APIs/types/functions: `uniphier_clk_probe()`, `uniphier_clk_register()`, `uniphier_clk_match[]`, and builtin platform driver `uniphier_clk_driver`. It dispatches to `uniphier_clk_register_cpugear()`, fixed-factor, fixed-rate, gate, and mux helpers according to `uniphier_clk_data.type`.

Control flow: probe retrieves match data, obtains the parent node's syscon regmap, scans data to size `clk_hw_onecell_data` by maximum nonnegative index, initializes unused entries to `ERR_PTR(-EINVAL)`, registers every named clock, stores indexed clocks in `hws[idx]`, and calls `devm_of_clk_add_hw_provider()`.

State and persistence: all allocations are device-managed. The provider stores an array of `clk_hw` pointers for indexed outputs; unindexed internal clocks can serve as parents by name but are not exposed by cell index.

Dependencies/integration: requires DT clock nodes under a syscon parent, MFD syscon/regmap, CCF onecell provider support, and data arrays from `clk-uniphier-sys.c`, `mio.c`, and `peri.c`.

Risks: `idx` values must be dense enough for consumers but may intentionally leave holes. Helper registration failures warn and continue, possibly leaving an indexed output invalid. The parent must be a syscon node or probe fails.

Test signals: probe all compatible strings, inspect onecell indices, verify internal unindexed parents resolve by name, and test missing syscon parent or bad data entries.
