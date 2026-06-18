# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/time-utils.h

## Purpose
`time-utils.h` provides tiny kernel time helpers used by VDO/UDS code.

## Important APIs, Types, And Functions
`ktime_to_seconds(ktime_t reltime)` converts nanoseconds to seconds by dividing by `NSEC_PER_SEC`. `current_time_ns(clockid_t clock)` returns monotonic nanoseconds for `CLOCK_MONOTONIC`, otherwise realtime nanoseconds. `current_time_us()` returns realtime microseconds.

## Control Flow
All helpers are static inline and branch only on the requested clock id in `current_time_ns()`.

## State And Persistence
No state is stored. Values reflect the current kernel monotonic or real clock at call time.

## Dependencies And Integration Points
The header includes kernel `ktime`, `time`, and type headers. It can be included wherever low-overhead timestamp conversion is needed.

## Risks
`ktime_to_seconds()` assumes the input is a nanosecond value despite the `ktime_t` type. `current_time_ns()` treats any non-`CLOCK_MONOTONIC` clock as realtime, so callers needing other clock semantics must not use it as a general clock dispatcher.

## Test Signals
Tests should cover monotonic versus realtime branch selection, microsecond conversion, and expected truncation on division.
