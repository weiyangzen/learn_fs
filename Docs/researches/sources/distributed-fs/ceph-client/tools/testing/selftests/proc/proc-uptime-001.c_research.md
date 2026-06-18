# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-uptime-001.c

Purpose: checks monotonicity between `/proc/uptime` boot time and `CLOCK_BOOTTIME` on a single running process.

Important APIs and functions: uses `proc_uptime()` and `clock_boottime()` from `proc-uptime.h`, `open`, and assertions on centisecond values.

Control flow: open `/proc/uptime`, capture initial proc and clock values, then loop until proc uptime advances by 100 centiseconds. Each iteration requires proc uptime monotonicity, clock monotonicity, and `CLOCK_BOOTTIME` not being behind `/proc/uptime`.

State and persistence: no persistent state, only local timestamp variables.

Dependencies and integration: depends on procfs uptime formatting and POSIX clock support.

Risks and test signals: scheduler delays are tolerated by monotonic comparisons. Failure indicates timekeeping regression or mismatch between proc uptime and boottime sources.
