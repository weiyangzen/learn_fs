# sources/distributed-fs/ceph-client/kernel/time/timekeeping.c

## Purpose
This is the core kernel timekeeper implementation. It owns wall-clock, monotonic, raw, boottime, TAI, leap-second, NTP-adjusted clocksource conversion, suspend/resume time injection, fast NMI-safe time reads, clocksource switching, cross timestamps, and optional auxiliary POSIX clocks.

## Important APIs, types, and functions
Central state is `struct tk_data`, which contains a seqcount, a published `struct timekeeper`, a staging `shadow_timekeeper`, and a raw spinlock. `tk_core` is the primary timekeeper and optional auxiliary entries live in `timekeeper_data`. Hot read APIs include `ktime_get()`, `ktime_get_real_ts64()`, `ktime_get_raw()`, `ktime_get_ts64()`, `ktime_get_with_offset()`, `ktime_get_coarse_with_offset()`, `ktime_get_snapshot()`, and fast `ktime_get_*_fast_ns()` variants. Write/update APIs include `do_settimeofday64()`, `timekeeping_inject_sleeptime64()`, `timekeeping_notify()`, `timekeeping_suspend()`, `timekeeping_resume()`, `update_wall_time()`, and `do_adjtimex()`.

## Control flow
Read paths use `read_seqcount_begin()`/retry around the published timekeeper, combine a base `ktime_t` with `timekeeping_get_ns()`, and return realtime, monotonic, raw, boot, TAI, or auxiliary variants. Write paths take the appropriate raw spinlock, operate on `shadow_timekeeper`, call `timekeeping_forward_now()` before discontinuous changes, then publish via `timekeeping_update_from_shadow()`, which updates ktime bases, VDSO data, pvclock notifiers, fast timekeepers, leap state, and finally memcpy-publishes the shadow under seqcount. Periodic advancement is handled by `update_wall_time()` -> `timekeeping_advance()` -> logarithmic cycle accumulation, second overflow/leap handling, and NTP frequency adjustment.

## State and persistence behavior
Persistent kernel state includes the active clocksource read bases, `xtime_sec`, shifted nanoseconds, raw seconds, wall-to-monotonic offset, realtime/boottime/TAI offsets, NTP error fields, leap scheduling, clocksource sequence numbers, suspend flags, persistent clock detection, and multigrain timestamp floor `mg_floor`. Suspend stores `timekeeping_suspend_time`, halts fast timekeeper reads through a dummy clock, and resume injects sleep time from a non-stop clocksource or persistent clock. State is not persisted to disk here, but it is initialized from architecture persistent clock hooks.

## Dependencies and integration points
This file integrates with clocksources, clockevents, tick/nohz, hrtimers, VDSO, pvclock, NTP, audit, random entropy, suspend/RTC, scheduler clock, timerfd, proc/syscore init, and optional auxiliary clocks. It exports foundational APIs consumed by syscall code in `time.c`, timer/hrtiner code, filesystems, drivers, tracing, PTP/cross-timestamp users, and architecture code.

## Risks
Timekeeping changes are high risk because they affect global ordering, wall-clock correctness, NTP convergence, suspend accounting, VDSO readers, and cross-CPU monotonicity. Specific risks include seqcount/write publication ordering, clocksource delta overflow, negative time jumps, leap-second offset handling, 32-bit torn reads, NMI fast-reader caveats, and auxiliary clock validity. Multigrain timestamp behavior intentionally allows realtime backward jumps to violate apparent ordering after clock set events.

## Test signals
Local direct tests are absent, so validation depends on timekeeping selftests, hrtimer/timer tests, suspend/resume tests, NTP/adjtimex tests, VDSO clock_gettime tests, and architecture clocksource coverage. Runtime signals include warnings in invalid suspend deltas, clocksource adjustment warnings, `clock_was_set()` effects, debugfs sleep-time accounting from `timekeeping_debug.c`, and trace/latency behavior under nohz and high-resolution timer configurations.
