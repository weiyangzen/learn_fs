<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124-dfll-fcpu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124-dfll-fcpu.c

Purpose: platform driver that supplies CPU DFLL operating-point data for Tegra114, Tegra124, and Tegra210. It turns fuse speedo/process information plus CVB voltage tables into CPU OPPs and registers the generic Tegra DFLL clock driver.

Important APIs, types, and functions: `struct dfll_fcpu_data` groups max-frequency and CVB table arrays per SoC. `tegra124_dfll_fcpu_probe()` is the core runtime path; `tegra124_dfll_fcpu_remove()` tears down DFLL and OPP state. Matching is through `"nvidia,tegra114-dfll"`, `"nvidia,tegra124-dfll"`, and `"nvidia,tegra210-dfll"`. Helpers `get_alignment_from_dt()` and `get_alignment_from_regulator()` define voltage rail alignment.

Control flow: probe gets SoC-specific data from the OF match, reads `tegra_sku_info` CPU process/speedo IDs and speedo value, bounds-checks the max-frequency table, allocates `tegra_dfll_soc_data`, binds it to CPU0's device, obtains rail alignment either from PWM DT properties or the `vdd-cpu` regulator, chooses `max_freq`, builds an OPP table with `tegra_cvb_add_opp_table()`, and calls `tegra_dfll_register()`. On DFLL registration failure it removes the OPP table. Remove unregisters DFLL first and then removes OPPs.

State and persistence: persistent runtime state is devm-allocated `tegra_dfll_soc_data`, the selected CVB table pointer, CPU OPP table entries, rail alignment, and DFLL driver state. Tables are static and encode fuse-dependent voltage/frequency policy. Runtime/system PM delegates to generic DFLL suspend/resume callbacks.

Dependencies and integration: depends on fuse data (`soc/tegra/fuse.h`), regulator APIs, CPU device discovery, CVB helpers, and `clk-dfll.c`. The SoC CAR drivers provide DFLL reset and reference clocks; DT properties decide PWM-to-PMIC alignment handling.

Risks and test signals: risks include unsupported speedo IDs causing probe failure, missing CPU0 device, regulator providers not ready, mismatched rail alignment creating unsafe voltages, and stale CVB table limits. Test probe on representative speedo/process bins, validate generated OPP voltages, exercise regulator and PWM paths, CPUfreq transitions through DFLL, runtime PM, system suspend/resume, and remove/error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124-dfll-fcpu.c -->
