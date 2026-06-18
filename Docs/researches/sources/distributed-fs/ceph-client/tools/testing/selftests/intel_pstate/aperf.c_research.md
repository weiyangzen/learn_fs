# sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/aperf.c

Purpose: `aperf.c` is a helper load generator and measurement tool for the Intel P-state selftest. It pins itself to one CPU, reads TSC/APERF/MPERF MSRs before and after a CPU-heavy loop, and estimates effective frequency.

Important APIs and functions: `usage()` prints argument form. `main()` parses one CPU number, opens `/dev/cpu/<cpu>/msr`, sets process affinity using `CPU_ZERO`, `CPU_SET`, and `sched_setaffinity()`, timestamps with `clock_gettime(CLOCK_MONOTONIC)`, reads MSRs with `pread()` at offsets `0x10`, `0xe7`, and `0xe8`, runs a long `sqrt(i)` loop, computes deltas, and prints `runTime` plus `freq`. It includes `kselftest.h` for `KSFT_SKIP`.

Control flow: invalid args or parse errors return 1; missing MSR device returns kselftest skip; affinity/timing failures return 1; otherwise the before/read/load/after/read/compute path exits 0.

State and persistence: no persistent state. It reads MSR device files and consumes CPU. Local variables hold before/after counters and elapsed milliseconds.

Dependencies and integration points: requires x86 MSR device support, likely root or msr permissions, libm, scheduler affinity APIs, and `run.sh`, which launches one instance per CPU.

Risks: return values from `pread()` are unchecked, so short/failed reads can produce bogus output. The `pread()` size arguments for APERF/MPERF use the opposite variable names, though the sizes are the same. The heavy loop duration is fixed and may be excessive or insufficient depending on CPU speed. Division by zero is possible if APERF/MPERF deltas are invalid.

Test signals: stdout lines `runTime:` and `freq:` provide measurement evidence for manual or scripted interpretation; exit 4 means skip due to inaccessible MSR device.
