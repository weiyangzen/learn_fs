# sources/distributed-fs/ceph-client/tools/testing/selftests/turbostat/added_perf_counters.py

## Purpose
This Python selftest validates turbostat's `--add perf/...` support by adding available perf counters and checking that turbostat output contains the requested columns in normal and debug modes.

## Important APIs, Types, and Functions
`PerfCounterInfo` formats perf event names and turbostat `--add` IDs. `PERF_COUNTERS_CANDIDATES` includes MSR counters and core/package C-state residency events. `check_perf_access()` probes counters with `perf stat`. `check_columns_or_fail()` compares expected and actual tab-separated output columns. The script uses `which()`, `subprocess.run()`, `turbostat --list`, and `timeout`.

## Control Flow
The script probes readable perf counters, skips if none are usable, locates `turbostat` and `timeout`, builds `--add` arguments for present counters with cpu/core/package scopes, runs turbostat with `--show CPU`, validates output columns, appends `--debug`, and validates the debug header including default debug columns.

## State and Persistence
It does not persist state. It launches short-lived `perf`, `timeout`, and `turbostat` processes.

## Dependencies and Integration Points
It depends on installed `perf`, `turbostat`, `timeout`, PMU counter availability, and permissions to read perf events.

## Risks
Hardware-dependent counters may be absent or permission-restricted. The script exits 0 when no counters are readable, using printed `SKIP` text rather than kselftest's numeric skip code. Header matching is exact and can fail on harmless column renames/order changes.

## Test Signals
Pass means all requested `--add` perf counters appear as columns in normal mode and debug mode includes `usec`, `Time_Of_Day_Seconds`, `APIC`, `X2APIC`, plus requested columns. Failure means turbostat execution or header generation regressed.
