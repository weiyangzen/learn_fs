# File Research: sources/cow-pools/bcachefs-tools/include/linux/jiffies.h

This header emulates Linux jiffies using monotonic time. `HZ` is `1000`, so jiffies map directly to milliseconds. Conversion helpers convert jiffies to milliseconds/nanoseconds and vice versa.

It provides wrap-safe `time_after*`, `time_before*`, and range macros for `unsigned long` and `u64`. `sched_clock()`, `local_clock()`, and `ktime_get_ns()` use `clock_gettime(CLOCK_MONOTONIC_COARSE)`. `jiffies` is a macro evaluating `nsecs_to_jiffies(sched_clock())`.
