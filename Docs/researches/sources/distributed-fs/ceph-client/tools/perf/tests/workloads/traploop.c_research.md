# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/traploop.c

## Purpose
This workload creates repeated privileged-register trap/return activity on AArch64 for perf tests that need exception/trap samples; on other architectures it degrades to an empty loop.

## Important APIs, Types, And Functions
The architecture-dependent helper is `trap_bench()`. On `__aarch64__` it executes inline assembly `mrs ID_AA64ISAR0_EL1`, which traps from EL0. The workload entry is `traploop()`, registered with `DEFINE_WORKLOAD(traploop)`.

## Control Flow
`traploop()` parses an optional iteration count, defaults to `BENCH_RUNS`, and calls `trap_bench()` in a counted loop. The AArch64 helper reads a system register into a local variable; the non-AArch64 helper is empty.

## State, Dependencies, And Integration
There is no persistent state. The key dependency is CPU/OS behavior for user-mode access to `ID_AA64ISAR0_EL1`. It integrates as a perf workload for exception-heavy traces.

## Risks And Test Signals
On non-AArch64 the workload has little profiling value beyond loop overhead. On AArch64, kernel configuration and CPU behavior determine trap characteristics. Downstream success is visible trap/exception behavior in perf data rather than workload output.
