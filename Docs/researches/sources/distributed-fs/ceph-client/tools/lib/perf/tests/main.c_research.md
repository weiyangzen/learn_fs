<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/main.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/tests/main.c

## Purpose
This is the libperf test executable entry point. It defines the global harness state and invokes the individual test suites.

## Important APIs, Types, and Functions
- Defines `int tests_failed` and `int tests_verbose` declared by `internal/tests.h`.
- `main(int argc, char **argv)` runs `test_cpumap`, `test_threadmap`, `test_evlist`, and `test_evsel` with `__T` assertions.

## Control Flow and State
Each suite returns zero on success. `__T` records and prints failures, but `main` returns `0` unconditionally after the checks, so failure signaling is primarily via harness output and `tests_failed` increments inside the macro execution.

## Dependencies and Integration Points
It includes the internal test harness and local `tests.h`. It links with all test source files and libperf.

## Risks and Test Signals
The unconditional `return 0` can hide suite failures from process exit status if the outer `__T` does not return early in `main`; in practice a failing `__T` returns `-1` from `main` immediately. Test output indicates which suite failed. This file is the integration point for adding new libperf tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/main.c -->
