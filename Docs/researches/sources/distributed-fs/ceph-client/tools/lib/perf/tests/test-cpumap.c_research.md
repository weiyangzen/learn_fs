<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-cpumap.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-cpumap.c

## Purpose
This test suite validates basic public CPU-map behavior and libperf logging initialization.

## Important APIs, Types, and Functions
- Local `libperf_print` forwards libperf diagnostics to `stderr` with `vfprintf`.
- `test_cpumap(int argc, char **argv)` initializes the harness and libperf, creates maps, exercises refcounting, iterates online CPUs, and reports status.

## Control Flow and State
The test creates an any-CPU map, increments/decrements its refcount, then creates an online-CPU map and verifies each iterated CPU is not the dummy `-1`. It releases maps through `perf_cpu_map__put`.

## Dependencies and Integration Points
It depends on `perf/cpumap.h`, `perf/core.h` via the callback type, and `internal/tests.h`. It calls `perf_cpu_map__new_online_cpus`, which may read sysfs or fall back to processor counts.

## Risks and Test Signals
The test is small and does not cover parsing CPU-list strings, set operations, or empty-map edge cases. It does catch basic allocation, refcount, online-map iteration, and dummy-value regressions. Host CPU topology and sysfs availability affect the online map implementation path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/test-cpumap.c -->
