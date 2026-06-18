# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/generic_events_valid_test.c

## Purpose
`generic_events_valid_test.c` validates that generic perf hardware/cache event types map to legal PMU encodings on supported POWER platforms and under generic compat PMU registration.

## Important APIs, Types, and Functions
The central routine is `generic_events_valid_test, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `raw event constants declared in the file`.

## Control Flow and State
The test alternates positive and negative opens: valid encodings must return a file descriptor, while invalid or unsupported encodings must fail cleanly without leaving stale event descriptors. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.
