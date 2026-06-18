# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_timeslice_test.sh

Purpose: `run_timeslice_test.sh` runs the rseq time-slice extension test when optimized rseq mode is available.

Important APIs, types, and functions: it exports `GLIBC_TUNABLES` with `glibc.pthread.rseq=0`, invokes `./check_optimized`, and then runs `./slice_test`.

Control flow: the script disables glibc rseq registration, checks optimized-mode support, prints a skip message and exits zero if unsupported, otherwise executes `slice_test`.

State and persistence: only environment state is changed. No persistent output is generated beyond stdout/stderr.

Dependencies and integration points: depends on `check_optimized`, `slice_test`, and kernel support for the optimized rseq mode and slice extension. It is the runner counterpart to `slice_test.c`.

Risks and test signals: unsupported optimized mode is treated as a skip rather than failure. Real failures are nonzero exits from `slice_test`. The output counters printed by `slice_test` are useful diagnostics.
