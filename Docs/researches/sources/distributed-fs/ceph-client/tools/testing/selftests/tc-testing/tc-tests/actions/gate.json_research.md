# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/gate.json

## Purpose
Defines 12 tests for the time-aware `gate` tc action.

## Important APIs, Types, And Functions
Cases cover priority plus `sched-entry`, `base-time`, `cycle-time`, `cycle-time-ext`, replace of base-time action, delete valid/invalid index, list, flush, duplicate max index, invalid oversized index, and cookies. All require `nsPlugin`.

## Control Flow
Each test runs `tc action add/replace/delete/list/flush action gate ...`, verifies expected exit code, and matches `tc action get/list` output for timing fields normalized to seconds, index, ref count, priority, and cookies.

## State And Persistence
Per-namespace gate action state persists during each case. Schedule parameters are kernel action metadata, not active hardware offload state in these tests.

## Dependencies And Integration Points
Depends on `NET_ACT_GATE`, tc parser support for nanosecond time units and schedule entries, and namespace setup.

## Risks
Time formatting normalization (`200000000000ns` to `200s`) is output-sensitive. Delete test `d821` verifies through `action bpf` instead of `action gate`, which appears suspicious and could mask gate-specific behavior if not intentional. Gate availability may depend on kernel module loading.

## Test Signals
Signals include correct normalized base/cycle time display, sched-entry acceptance, replace updates, list/flush counts, invalid index rejection, duplicate max index behavior, and cookie display.
