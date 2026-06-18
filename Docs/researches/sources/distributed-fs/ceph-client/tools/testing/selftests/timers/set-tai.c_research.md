# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/set-tai.c

## Purpose
This test validates setting and reading the kernel TAI offset through `adjtimex(ADJ_TAI)`.

## Important APIs, Types, and Functions
`set_tai()` writes `struct timex.modes = ADJ_TAI` and `constant = offset`. `get_tai()` calls `adjtimex()` in query mode and returns `tx.tai`.

## Control Flow
`main()` prints the initial TAI offset, then sets offsets from 1 through 60 and verifies that each value is returned by the next query. It exits fail on the first mismatch and pass after the full range.

## State and Persistence
This modifies global kernel timekeeping TAI offset and does not restore the initial value. The ending TAI offset is 60 on success.

## Dependencies and Integration Points
The test requires privileges for `adjtimex(ADJ_TAI)` and depends on `sys/timex.h` plus kselftest exit helpers.

## Risks
Not restoring the starting TAI offset can affect later TAI-clock tests or system behavior. It does not inspect `adjtimex()` return codes before reading back state, so failures are detected only by mismatch.

## Test Signals
Pass means the kernel accepted every TAI offset in the tested range and reported it back accurately. Failure means `ADJ_TAI` did not take effect or was blocked.
