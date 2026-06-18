<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/tests.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/tests/tests.h

## Purpose
This local test header declares the test-suite entry points used by `tests/main.c`.

## Important APIs, Types, and Functions
- `test_cpumap(int argc, char **argv)`
- `test_threadmap(int argc, char **argv)`
- `test_evlist(int argc, char **argv)`
- `test_evsel(int argc, char **argv)`

## Control Flow and State
The header has no logic. It standardizes all suite signatures so the main test runner can pass through command-line arguments, especially `-v` for the shared harness.

## Dependencies and Integration Points
It is included by each test implementation and by `main.c`. It works with `internal/tests.h`, where the common macros and globals are declared.

## Risks and Test Signals
Any signature mismatch between this header and implementation files would be caught at compile time. Adding new suites requires updating this header and `main.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/tests/tests.h -->
