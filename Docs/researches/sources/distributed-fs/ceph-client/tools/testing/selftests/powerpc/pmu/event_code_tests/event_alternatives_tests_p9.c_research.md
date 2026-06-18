# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event_code_tests/event_alternatives_tests_p9.c

## Purpose
`event_alternatives_tests_p9.c` checks POWER9 event alternative selection and group compatibility using alternate encodings for run cycles, dispatch, branch, load-miss, and completed-instruction events.

## Important APIs, Types, and Functions
The central routine is `event_alternatives_tests_p9, main`, executed through `test_harness()` from `main()`. It uses the shared PMU `struct event` wrapper from `../event.h`, platform helpers from `../sampling_tests/misc.h`, and event constants such as `PM_RUN_CYC_ALT, PM_INST_DISP, PM_BR_2PATH, PM_LD_MISS_L1, PM_RUN_INST_CMPL_ALT, EventCode_1`.

## Control Flow and State
The test initializes one or more `struct event` objects, applies platform gates, invokes `event_open` or grouped open helpers, and closes descriptors after each assertion path. State is transient: open perf file descriptors, event attributes, and any platform/PVR globals initialized by `platform_check_for_tests()` or related helpers. There is no persistent storage beyond kernel perf scheduling state during the test process.

## Dependencies and Integration Points
The file integrates with `perf_event_open`, the powerpc PMU raw-event parser, event group constraint logic in the kernel PMU driver, PVR/HWCAP platform detection, and the kselftest harness macros `SKIP_IF`/`FAIL_IF`.

## Risks and Test Signals
Risks include false skips on new POWER revisions, event-code drift when kernel encodings change, and tests that invert negative-open expectations. A pass means legal encodings open, illegal encodings fail with no crash, and group constraint decisions match the hardware-specific PMU scheduling rules.
