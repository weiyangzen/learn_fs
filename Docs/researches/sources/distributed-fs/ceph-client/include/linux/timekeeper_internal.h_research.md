<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timekeeper_internal.h -->
# sources/distributed-fs/ceph-client/include/linux/timekeeper_internal.h

## Purpose
defines internal timekeeper state: clocksource read bases, sequence counters, NTP/error accumulation, offsets, leap-second state, shadow copies, and VDSO update hooks.

## Important APIs, Types, and Functions
The file is 215 lines and exports these visible symbol families: types/enums `timekeeper_ids`, `tk_read_base`, `timekeeper`; macros/constants none; function-like macros none; inline helpers `update_vsyscall`, `update_vsyscall_tz`, `vdso_time_update_aux`; external prototypes `update_vsyscall`, `update_vsyscall_tz`, `vdso_time_update_aux`.

## Control Flow
Timekeeping core updates `tk_read_base` instances from the active clocksource, advances `timekeeper` raw/monotonic/real/boot/TAI offsets, mirrors values for fast/VDSO readers, and calls architecture VDSO update hooks when clock state changes.

## State and Persistence Behavior
`timekeeper` is central persistent kernel state, containing seqcount-protected read bases, wall-to-monotonic offset, total sleep time, raw time, TAI offset, NTP error/multiplier fields, leap state, cycle interval, and shadow copy for update calculations.

## Dependencies and Integration Points
It depends on clocksource IDs, seqcount, time64, ktime, timecounter concepts, and optional GENERIC_GETTIMEOFDAY/VDSO hooks. Direct includes are `linux/clocksource.h`, `linux/jiffies.h`, `linux/time.h`.

## Risks and Edge Cases
This layout is concurrency-critical. Incorrect seqcount updates, clocksource masks, NTP error math, or VDSO shadow updates can produce non-monotonic time, broken fast reads, or wrong leap/TAI offsets.

## Test Signals
Run timekeeping selftests, clocksource switch tests, NTP adjustment/leap-second simulations, suspend/resume, VDSO correctness checks, and lockdep/seqcount validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timekeeper_internal.h -->
