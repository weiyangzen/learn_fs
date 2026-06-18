# sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/unit/unit_tests.c

## Purpose

`unit_tests.c` contains Check-based unit tests for selected rtla utility functions, currently strict integer parsing, CPU-set parsing, and scheduler-priority parsing.

## Important APIs, Types, and Functions

The test cases are `test_strtoi`, `test_parse_cpu_set`, and `test_parse_prio`. `utils_suite()` builds the Check suite and `main()` runs it. A local `int nr_cpus` satisfies `utils.c` parsing dependencies.

## Control Flow and Data Flow

Each Check test calls a utility function with valid and invalid inputs, then asserts return values and selected output fields. `test_parse_cpu_set` sets `nr_cpus = 8` and inspects `CPU_ISSET` results. `test_parse_prio` checks FIFO, RR, OTHER, DEADLINE, and invalid policy/bounds cases.

## State and Persistence Behavior

The test mutates only local variables and the test-global `nr_cpus`. It does not apply scheduler attributes; it only parses into `struct sched_attr`.

## Dependencies and Integration Points

It depends on the Check framework, libc scheduler macros, `utils.h`, and the rtla test build system. It guards behavior used by command-line parsing across rtla tools.

## Risks and Edge Cases

Coverage is intentionally narrow. It does not test duration suffix edge cases, trailing text accepted by `get_llong_from_str()`, cgroup helpers, procfs scanning, or actual `sched_setattr` syscalls. CPU-set tests do not cover trailing commas or reversed ranges beyond basic invalid cases.

## Test Signals

Passing the suite indicates the main parser contracts for CPU masks, priorities, and strict integer conversion are intact. Failures point directly to command-line behavior regressions.
