# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/snb_idle.c

## Purpose
Implements an Intel Sandy/Ivy/Haswell MSR residency monitor for core C7 and package PC2/PC7.

## Important APIs, Types, and Functions
Key functions are `snb_get_count`, `snb_get_count_percent`, `snb_start`, `snb_stop`, `snb_register`, and `snb_unregister`. The monitor descriptor is `intel_snb_monitor` with states `C7`, `PC2`, and `PC7`.

## Control Flow, State, and Persistence
Registration requires Intel family 6 and selected models for Sandy Bridge, Ivy Bridge, and Haswell. It allocates per-CPU arrays, snapshots state MSRs and TSC at start/stop, and computes percentages from residency deltas over TSC delta. State is per-process heap plus live MSR counters.

## Dependencies and Integration Points
Depends on model tables from CPU info, MSR access, root permission, and monitor framework integration.

## Risks and Test Signals
Model coverage is manually maintained. Validity OR behavior can hide one-sided read failures. Package counters may duplicate values for CPUs in the same package but are printed per selected topology row. Test supported/unsupported models, multi-package output, no MSR access, non-root filtering, and comparison with turbostat.
