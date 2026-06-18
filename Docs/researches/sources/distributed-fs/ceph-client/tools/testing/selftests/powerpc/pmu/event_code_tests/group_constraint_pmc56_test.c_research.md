# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/group_constraint_pmc56_test.c

## Purpose
`group_constraint_pmc56_test.c` verifies that events requiring PMC5/PMC6 placement are rejected when they violate the PMU group placement constraints.

## Important APIs, Types, and Functions
The central routine is `group_constraint_pmc56, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `raw event constants declared in the file`.

## Control Flow and State
The test initializes one or more `struct event` objects, applies platform gates, invokes `event_open` or grouped open helpers, and closes descriptors after each assertion path. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.
