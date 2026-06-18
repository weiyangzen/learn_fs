# sources/distributed-fs/ceph-client/drivers/clk/tegra/cvb.c

## Purpose

`cvb.c` converts NVIDIA Tegra CVB voltage tables into Linux OPP entries. CVB tables describe the voltage needed for a clock frequency as a quadratic function of the chip's speedo value, with process/speedo table selection, rail alignment, and min/max voltage clamping. The resulting operating points are registered with the OPP core for consumers such as CPU or GPU DVFS drivers.

## Important APIs, Types, And Functions

`get_cvb_voltage()` evaluates `((c2 * speedo / s_scale + c1) * speedo / s_scale + c0)` using rounded integer arithmetic. `round_cvb_voltage()` applies the table voltage scale and aligns the result to the regulator's microvolt offset and step. `round_voltage()` rounds min/max limits up or down to the same regulator alignment. `build_opp_table()` walks up to `MAX_DVFS_FREQS`, stops at the first zero frequency or a frequency above `max_freq`, clamps each calculated voltage, and calls `dev_pm_opp_add()`.

The exported `tegra_cvb_add_opp_table()` selects the first CVB table whose `speedo_id` and `process_id` match, allowing `-1` wildcards, then builds the OPP table and returns the selected table or `ERR_PTR()`. `tegra_cvb_remove_opp_table()` removes the same frequency range with `dev_pm_opp_remove()`.

## Control Flow

A Tegra DVFS user supplies the device, CVB table array, rail alignment, process and speedo identifiers, raw speedo value, and maximum safe rate. The function scans tables in order and immediately attempts the first match. For each entry, it calculates millivolts from coefficients, rounds to rail requirements, clamps to table limits, converts to microvolts, and registers the OPP. Cleanup uses the returned table pointer and the same `max_freq` boundary to remove entries.

## State And Persistence Behavior

This file stores no private state. Its persistent side effect is the OPP table entries attached to `dev` in the OPP core. Partial failure during `build_opp_table()` returns immediately and does not roll back already added OPPs, so callers need to handle cleanup if they retry or abort after a mid-table failure.

## Dependencies And Integration Points

The code depends on `linux/pm_opp.h`, Tegra CVB structures from `cvb.h`, and regulator alignment values supplied by the platform. It integrates with whichever clock/voltage driver later consumes OPP entries for DVFS. The semantics of speedo/process IDs must match Tegra fuse-reading code outside this file.

## Risks And Edge Cases

Table ordering matters because selection stops at the first compatible table. Bad `voltage_scale`, `speedo_scale`, or rail alignment can silently over- or under-voltage every OPP. If `align->step_uv` is zero, `round_cvb_voltage()` uses a default scaled 1000 uV step but still multiplies `offset_uv` by `v_scale`, so table authors must understand the combined scale. Duplicate OPP frequencies or unsupported voltages surface as `dev_pm_opp_add()` errors. A failure after adding earlier OPPs leaves partial state unless the caller removes it.

## Test Signals

Unit-style validation can feed known speedo/coefficient/table values and compare generated microvolt OPPs. Platform tests should verify OPP entries in debugfs/sysfs, confirm max-frequency truncation, exercise wildcard and exact speedo/process matches, and test cleanup by unloading or reprobes. DVFS stress tests should confirm regulators accept the aligned voltages and frequency transitions remain stable.
