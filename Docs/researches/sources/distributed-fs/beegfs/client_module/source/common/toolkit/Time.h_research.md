# sources/distributed-fs/beegfs/client_module/source/common/toolkit/Time.h

## Purpose
Provides a kernel-version-compatible `Time` abstraction over monotonic or real timestamps and elapsed-time helpers.

## Important APIs and control flow
`Time` aliases `timespec64` or `timespec`. `Time_setToNow` uses monotonic kernel time; `Time_setToNowReal` uses real wall-clock time. `Time_init`, `Time_initZero`, and `Time_setZero` initialize values. `Time_elapsedSinceMS`, `Time_elapsedSinceNS`, `Time_toNS`, `Time_compare`, and `Time_elapsedMS` implement elapsed and comparison helpers over seconds/nanoseconds.

## State, dependencies, integration
State is caller-owned timestamp structs. `AckManager`, `InternodeSyncer`, and delayed queues use `Time` to track age and periodic intervals.

## Risks and test signals
`Time_getIsZero` checks `tv_sec` twice and never checks `tv_nsec`, so a timestamp with zero seconds and nonzero nanoseconds is considered zero. Millisecond elapsed calculations use unsigned seconds plus signed millisecond delta and assume non-decreasing times. Tests should cover nanosecond borrow, zero detection, compare overflow for far-apart times, and 32-bit/64-bit timestamp builds.
