<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time.h -->
# sources/distributed-fs/ceph-client/include/linux/time.h

## Purpose
declares common kernel time conversion and userspace copy helpers for `timespec64`, `itimerspec64`, `tm`, utimes, itimer clearing, and 32-bit wrap-safe comparisons.

## Important APIs, Types, and Functions
The file is 103 lines and exports these visible symbol families: types/enums `tm`; macros/constants none; function-like macros `time_after32`, `time_before32`, `time_between32`; inline helpers `clear_itimer`, `itimerspec64_valid`; external prototypes `get_timespec64`, `put_timespec64`, `get_itimerspec64`, `put_itimerspec64`, `mktime64`, `clear_itimer`, `do_utimes`, `time64_to_tm`.

## Control Flow
Syscall paths copy timespec/itimerspec values to and from userspace, validate interval timers, convert seconds to calendar `tm`, and compare 32-bit time values with wrap-aware macros.

## State and Persistence Behavior
`sys_tz` is the exposed global timezone record; other state lives in syscall/timekeeping implementations.

## Dependencies and Integration Points
It depends on time64 structures, user access annotations, timer configuration, and syscall implementations. Direct includes are `linux/cache.h`, `linux/math64.h`, `linux/time64.h`, `linux/time32.h`, `vdso/time.h`.

## Risks and Edge Cases
User copy validation, nanosecond range checks, and 32-bit wrap comparisons are easy to misuse. `itimerspec64_valid()` rejects invalid intervals and values before timers are armed.

## Test Signals
Run time syscall selftests, invalid timespec fuzzing, utimes coverage, itimer validation, and wrap-around tests for `time_after32`/`time_before32`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/time.h -->
