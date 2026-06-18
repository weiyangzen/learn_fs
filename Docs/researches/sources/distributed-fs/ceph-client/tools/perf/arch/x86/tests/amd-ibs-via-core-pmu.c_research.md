# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/amd-ibs-via-core-pmu.c

## Purpose
This file verifies that AMD IBS op sampling can be reached through selected core PMU event encodings and rejected for unsupported encodings. It is a small architecture test that opens precise perf events and checks whether kernel perf maps or rejects them as expected.

## Important APIs, Types, and Functions
`struct sub_tests` records `type`, `config`, and expected validity. The table contains five cases: CPU cycles valid, instructions invalid, raw `0x076` valid, raw `0x0C1` valid, and raw `0x012` invalid. `event_open()` builds a `struct perf_event_attr` with `disabled = 1`, `precise_ip = 1`, `sample_type = PERF_SAMPLE_IP | PERF_SAMPLE_TID`, and `sample_period = 100000`, then calls `sys_perf_event_open(&attr, -1, 0, -1, 0)` for CPU 0 across all processes.

The exported entry point is `test__amd_ibs_via_core_pmu(struct test_suite *, int)`. It uses `perf_pmus__find("ibs_op")` as a capability gate and returns `TEST_SKIP` if IBS op PMU is unavailable.

## Control Flow
The test locates `ibs_op`, iterates the static sub-test table, opens each event, logs the event type/config/fd, and marks failure when a valid case cannot open or an invalid case unexpectedly opens. Valid fds are closed immediately. The final status is the aggregate of all subtests: any mismatch makes the suite return `TEST_FAIL`.

## State and Persistence
There is no persistent state. Runtime state consists only of transient perf file descriptors. The event is opened disabled and not mmaped or enabled, so the test validates event admission rather than collecting samples.

## Dependencies and Integration Points
The file depends on perf UAPI constants, perf's `sys_perf_event_open()` wrapper, PMU discovery (`perf_pmus__find`), and test/debug infrastructure. `arch-tests.c` registers it with `DEFINE_SUITE("AMD IBS via core pmu", amd_ibs_via_core_pmu)`.

## Risks and Edge Cases
The test assumes the kernel and PMU expose the expected AMD IBS forwarding policy. Systems with restrictive perf permissions, virtualized PMUs, or changed raw-event mappings can produce failures unrelated to parser code. It checks `fd > 0` for invalid open success and close handling; file descriptor `0` is unlikely from perf in normal test processes but would not be closed or treated as success by that condition.

## Test Signals
Expected outcomes are a skip when `ibs_op` is absent, pass when valid events open and invalid events fail, and fail when admission policy differs. Debug lines provide per-case `Pass`/`Fail` evidence with event type and config.
