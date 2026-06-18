<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timekeeping.h -->
# sources/distributed-fs/ceph-client/include/linux/timekeeping.h

## Purpose
declares the public kernel timekeeping API for initialization, setting wall time, reading coarse/fine/raw/boottime/TAI clocks, fast nanosecond readers, RTC/persistent clock hooks, cross timestamps, and snapshots.

## Important APIs, Types, and Functions
The file is 361 lines and exports these visible symbol families: types/enums `tk_offsets`, `system_time_snapshot`, `system_device_crosststamp`, `system_counterval_t`; macros/constants none; function-like macros none; inline helpers `ktime_get_real`, `ktime_get_coarse_real`, `ktime_get_boottime`, `ktime_get_coarse_boottime`, `ktime_get_clocktai`, `ktime_get_coarse_clocktai`, `ktime_get_coarse`, `ktime_get_coarse_ns`, `ktime_get_coarse_real_ns`, `ktime_get_coarse_boottime_ns`, `ktime_get_coarse_clocktai_ns`, `ktime_mono_to_real`, `ktime_get_ns`, `ktime_get_real_ns`, and 11 more; external prototypes `timekeeping_init`, `legacy_timer_tick`, `do_settimeofday64`, `do_sys_settimeofday64`, `ktime_get`, `ktime_get_ts64`, `ktime_get_real_ts64`, `ktime_get_coarse_ts64`, `ktime_get_coarse_real_ts64`, `ktime_get_clock_ts64`, `ktime_get_coarse_real_ts64_mg`, `ktime_get_real_ts64_mg`, `timekeeping_get_mg_floor_swaps`, `getboottime64`, and 28 more.

## Control Flow
Core boot initializes timekeeping; syscalls and RTC code set or adjust wall time; readers choose timespec, ktime, seconds, nanoseconds, coarse, or fast accessors. Cross-timestamp code correlates device counters with system time for PTP-style synchronization.

## State and Persistence Behavior
Most state lives in the internal timekeeper, while this header exposes `timekeeping_suspended`, persistent-clock locality, snapshot structures, cross-timestamp structures, and base-clock counter values.

## Dependencies and Integration Points
It depends on clocksource IDs, time64/ktime, time namespaces indirectly through readers, RTC/persistent clock code, and architecture VDSO/fast-time support. Direct includes are `linux/errno.h`, `linux/clocksource_ids.h`, `linux/ktime.h`.

## Risks and Edge Cases
Callers must choose the right clock domain: monotonic excludes suspend, boottime includes suspend, real is wall-clock, raw excludes NTP, and TAI includes TAI offset. Fast readers trade synchronization for speed and have context constraints.

## Test Signals
Run timekeeping and VDSO selftests, clock_settime/adjtimex tests, suspend/resume boottime checks, PTP cross-timestamp validation, persistent clock update tests, and namespace-offset tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timekeeping.h -->
