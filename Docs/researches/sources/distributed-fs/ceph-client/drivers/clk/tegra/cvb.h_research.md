# sources/distributed-fs/ceph-client/drivers/clk/tegra/cvb.h

## Purpose

`cvb.h` declares the data model and exported helpers for Tegra CVB voltage-table handling. It is the shared contract between SoC-specific Tegra DVFS data and the implementation in `cvb.c`.

## Important APIs, Types, And Functions

`MAX_DVFS_FREQS` caps each table at 40 entries. `struct rail_alignment` describes regulator offset and step in microvolts. `struct cvb_coefficients` stores the quadratic coefficients used to calculate voltage from speedo. `struct cvb_table_freq_entry` pairs a frequency with coefficients. `struct cvb_cpu_dfll_data` carries CPU DFLL tuning values and the minimum millivoltage threshold for high tuning. `struct cvb_table` adds speedo/process matching, min/max voltage limits, scaling factors, the frequency entries, and optional CPU DFLL data.

The public helpers are `tegra_cvb_add_opp_table()` and `tegra_cvb_remove_opp_table()`.

## Control Flow

The header is included by Tegra clock/DVFS code that defines static CVB tables and then asks `cvb.c` to materialize them as OPP entries. Callers retain the returned `struct cvb_table` pointer so they can later remove only the entries that were added.

## State And Persistence Behavior

The structures are plain configuration data, usually static and read-only in SoC files. Runtime persistence is indirect: the add/remove functions create or delete OPP core state for the target device. `cvb_cpu_dfll_data` also carries values that CPU DFLL integration may program into hardware outside this file.

## Dependencies And Integration Points

The header depends on Linux integer types and forward-declares `struct device`. It integrates with Tegra fuse/process identification, regulator alignment data, OPP core registration, and CPU DFLL tuning code.

## Risks And Edge Cases

All units must be consistent: frequencies are `unsigned long`, voltages in the table are millivolts, rail alignment uses microvolts, and scaling factors are integer divisors/multipliers used by the CVB formula. A table without a terminating zero frequency relies on the fixed `MAX_DVFS_FREQS` bound. Wildcard `speedo_id` or `process_id` values are implemented in `cvb.c` as `-1`, so table authors need to reserve that convention.

## Test Signals

Compile tests should cover all files that define CVB tables. Runtime validation should inspect generated OPP entries, ensure the selected table matches fuse values, and verify DFLL tuning thresholds for CPU tables.
