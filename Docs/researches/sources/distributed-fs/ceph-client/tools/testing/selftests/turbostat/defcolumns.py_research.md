# sources/distributed-fs/ceph-client/tools/testing/selftests/turbostat/defcolumns.py

## Purpose
This Python test checks that turbostat's default output header matches `turbostat --list`, with debug-only columns handled separately.

## Important APIs, Types, and Functions
The script uses `which()`, `subprocess.run()`, `turbostat --list`, `timeout --preserve-status -s SIGINT`, and byte-string header comparisons. It derives `expected_columns_debug` from `--list`, then removes `usec`, `Time_Of_Day_Seconds`, `X2APIC`, and `APIC` for normal expected columns.

## Control Flow
It locates `turbostat` and `timeout`, captures `turbostat --list`, runs turbostat briefly with `-i 0.250`, compares the first output line to expected normal columns, reruns with `--debug`, and compares to debug columns.

## State and Persistence
No persistent state is written. The script runs short external commands.

## Dependencies and Integration Points
It depends on turbostat and coreutils timeout. It integrates with turbostat selftests as an executable Python script.

## Risks
The test compares exact byte headers, so column ordering, separator, default list, or debug-only column changes must be reflected in the script. It exits 1 rather than kselftest skip when required binaries are absent.

## Test Signals
Pass means normal and debug turbostat headers match `--list`-derived expectations. Failure indicates default column reporting drift.
