# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/reserved_bits_mmcra_sample_elig_mode_test.c

## Purpose
`reserved_bits_mmcra_sample_elig_mode_test.c` verifies that reserved MMCRA sample eligibility/mode bits are rejected, with architecture-specific handling for POWER9 versus POWER10/11.

## Important APIs, Types, and Functions
The central routine is `reserved_bits_mmcra_sample_elig_mode, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `raw event constants declared in the file`.

## Control Flow and State
The test opens a leader event, attempts one or more sibling opens expected to fail, then tries a compatible event where applicable. It treats the negative `perf_event_open` result as success for invalid combinations. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.
