# subset-b-006063 research

Grouped research for kernel timekeeping and timer files under `sources/distributed-fs/ceph-client/kernel/time`. Each section preserves the source path and is bounded for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/time.c -->
# sources/distributed-fs/ceph-client/kernel/time/time.c

## Purpose
This file provides the kernel-facing implementation of legacy time syscalls and common time conversion helpers. It bridges user ABI structures (`old_timeval32`, `__kernel_timespec`, `__kernel_itimerspec`, `__kernel_timex`) with the internal `timespec64`/`ktime_t` timekeeping model and exports many conversion routines used across drivers, filesystems, scheduler code, timers, and compatibility syscall paths.

## Important APIs, types, and functions
Key syscall entry points include `time`, `stime`, `time32`, `stime32`, `gettimeofday`, `settimeofday`, compat `gettimeofday`/`settimeofday`, `adjtimex`, and `adjtimex_time32`, all conditionally compiled by architecture and compatibility options. `do_sys_settimeofday64()` centralizes timezone and settimeofday permission/validation flow. Conversion helpers include `mktime64()`, `ns_to_kernel_old_timeval()`, `set_normalized_timespec64()`, `ns_to_timespec64()`, jiffies/milliseconds/microseconds conversions, clock tick conversions, `timespec64_add_safe()`, `get_timespec64()`, `put_timespec64()`, `get_old_timespec32()`, `put_old_timespec32()`, `get_itimerspec64()`, and `put_itimerspec64()`. The global `sys_tz` timezone is exported for legacy consumers.

## Control flow
Read-only syscalls fetch current realtime through `ktime_get_real_seconds()` or `ktime_get_real_ts64()` and copy results to user memory with `put_user()`/`copy_to_user()`. Setting time copies user structures, validates microsecond/nanosecond ranges, runs `security_settime64()`, then calls `do_settimeofday64()` from `timekeeping.c`. `do_sys_settimeofday64()` also handles first-time timezone setting: if only `tz` is supplied, it may call `timekeeping_warp_clock()` to convert a local persistent clock to UTC. `adjtimex` paths copy ABI structures, call `do_adjtimex()`, then copy the updated timex state back out.

## State and persistence behavior
Persistent state in this file is intentionally small: `sys_tz` holds the legacy timezone, and a static `firsttime` flag inside `do_sys_settimeofday64()` gates one-time clock warping. Actual wall-clock, NTP, TAI, boot, and monotonic state is owned by `timekeeping.c`. Conversion helpers are stateless except for compile-time constants such as `HZ`, `USER_HZ`, and generated `timeconst.h` multipliers. Saturation behavior is important: timeout conversion routines clamp impossible or negative values to `MAX_JIFFY_OFFSET`, and `timespec64_add_safe()` saturates overflow to `TIME64_MAX`.

## Dependencies and integration points
The file depends on security hooks (`security_settime64()`), user-copy helpers, compatibility ABI definitions, generated jiffies conversion constants, and core timekeeper exports such as `ktime_get_real_ts64()`, `do_settimeofday64()`, and `do_adjtimex()`. It is the ABI edge for legacy applications and for 32-bit compatibility on 64-bit kernels. Its exported conversion helpers are shared broadly by kernel subsystems, so arithmetic changes affect timeout scheduling and userspace ABI conversions far beyond this directory.

## Risks
The main risks are ABI compatibility regressions, off-by-one unit conversions, overflow/saturation mistakes, and invalid time normalization. `settimeofday` checks `tv_usec > USEC_PER_SEC` rather than `>=`, matching existing behavior but making boundary review important. The 32-bit timex and timespec paths must preserve padding and x32 behavior. Timezone warping is legacy and stateful, so changing `firsttime` or `sys_tz` semantics can alter boot-time wall-clock behavior.

## Test signals
Direct test coverage in this subset targets `time64_to_tm()` in `time_test.c`; this file relies more on syscall ABI tests, compat syscall tests, and kernel selftests outside the subset. Useful signals are KUnit/time conversion tests, LTP syscall coverage for `gettimeofday`, `settimeofday`, `adjtimex`, 32-bit compat runs, and build coverage across `CONFIG_COMPAT`, `CONFIG_COMPAT_32BIT_TIME`, and `HZ` variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/time_test.c -->
# sources/distributed-fs/ceph-client/kernel/time/time_test.c

## Purpose
This KUnit file validates the Gregorian date conversion behavior of `time64_to_tm()`. It is narrowly focused on calendar correctness over a very large date range rather than on syscall or timekeeper behavior.

## Important APIs, types, and functions
The test defines local helpers `is_leap()`, `last_day_of_month()`, and `advance_date()` to compute expected calendar progression independently from the production conversion code. `time64_to_tm_test_date_range()` is registered as a slow KUnit case with `KUNIT_CASE_SLOW`. The test suite is named `time_test_cases` and is exported with `kunit_test_suite()`.

## Control flow
The test starts 80,000 years before 1970 and iterates by one-day steps through 80,000 years after 1970. For each day it calls `time64_to_tm(secs, 0, &result)`, computes the expected signed day count, and asserts year, month, month day, and year day with detailed failure context. The independent expected date is then advanced by one day through month and leap-year boundary logic.

## State and persistence behavior
The file has no persistent runtime state. It creates stack-local counters for year, month, day, yday, seconds, and `struct tm` result state. It does not mutate kernel timekeeping state or depend on current wall-clock values.

## Dependencies and integration points
It depends on KUnit and `linux/time.h`, especially the exported `time64_to_tm()` API. It indirectly validates the algorithm in `timeconv.c` and protects calendar users throughout the kernel, including filesystems, RTC/display paths, and timestamp formatting code.

## Risks
Because this is an exhaustive slow test over a wide range, runtime cost is intentional and it must remain marked slow. The expected implementation uses signed modulo and local leap-year logic to avoid accidentally sharing production helper assumptions. A risk is that future changes to `time64_to_tm()` offset handling are not covered here because the test always passes offset `0`.

## Test signals
The primary signal is KUnit success for `time_test_cases`. Failures include the exact expected date and day count in `FAIL_MSG`. Additional useful future coverage would include nonzero offsets, times within a day rather than midnight-only values, and boundary checks around negative seconds and leap-day transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/time_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timeconv.c -->
# sources/distributed-fs/ceph-client/kernel/time/timeconv.c

## Purpose
This file implements `time64_to_tm()`, converting signed seconds since the Unix epoch plus an offset into a broken-down Gregorian `struct tm`. It replaces older glibc-derived conversion code with a constant-time arithmetic calendar algorithm.

## Important APIs, types, and functions
The exported API is `time64_to_tm(time64_t totalsecs, int offset, struct tm *result)`. It fills `tm_sec`, `tm_min`, `tm_hour`, `tm_wday`, `tm_year`, `tm_mon`, `tm_mday`, and `tm_yday`. It uses kernel division helpers such as `div_s64_rem()`, `div64_u64_rem()`, and bit helpers like `upper_32_bits()`/`lower_32_bits()`.

## Control flow
The function first divides `totalsecs` into days and remainder seconds, applies `offset`, and normalizes the remainder into `[0, SECS_PER_DAY)`, adjusting days as necessary. It derives time-of-day fields from the normalized remainder and weekday from the known Thursday epoch. Date conversion then maps days into a March-based computational calendar using cycle arithmetic over Gregorian 400-year periods, calculates century, year-of-century, day-of-year, month, and day, then converts back to normal `struct tm` conventions.

## State and persistence behavior
The implementation is stateless and deterministic. It does not read the current clock, timezone state, or kernel timekeeper state. All intermediate state is local arithmetic state, with careful unsigned offsets used to make negative epochs tractable.

## Dependencies and integration points
The file depends on `linux/time.h`, `linux/module.h`, and `linux/kernel.h`. `time64_to_tm()` is exported for kernel users needing calendar decomposition. The KUnit test in `time_test.c` directly covers the date portion over a 160,000-year range.

## Risks
The arithmetic is compact but non-obvious. Risks include signed/unsigned conversion mistakes, offset normalization bugs, weekday behavior for negative dates, and accidental changes to `struct tm` conventions where `tm_year` is years since 1900 and `tm_mon` is zero-based. Any change to constants such as the large day offset or Gregorian cycle factors can silently corrupt broad date ranges.

## Test signals
`time_test.c` is the strongest local signal for date correctness. Additional signals should include offset tests, sub-day time tests, comparisons with userspace date libraries for representative negative and far-future timestamps, and build coverage on 32-bit and 64-bit architectures because division helper behavior matters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timeconv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timecounter.c -->
# sources/distributed-fs/ceph-client/kernel/time/timecounter.c

## Purpose
This file implements a small generic accumulator that turns hardware or device cycle counters into monotonically accumulated nanoseconds. It is based on clocksource-style cycle conversion but packaged for `struct timecounter` users.

## Important APIs, types, and functions
`timecounter_init()` initializes a `struct timecounter` with a `struct cyclecounter`, the initial cycle reading, starting nanosecond timestamp, fractional mask, and zero fraction. `timecounter_read()` is the exported read/update API. `timecounter_read_delta()` is a private helper that reads cycles, calculates masked delta from the last cycle value, converts cycles to nanoseconds with `cyclecounter_cyc2ns()`, updates `cycle_last`, and returns the delta.

## Control flow
Initialization records the current hardware cycle value and the caller-supplied nanosecond base. Each read samples the cyclecounter, computes `(cycle_now - cycle_last) & cc->mask` to tolerate one wraparound, converts the delta while carrying fractional nanoseconds through `tc->frac`, advances `cycle_last`, adds the delta to `tc->nsec`, stores it back, and returns the accumulated nanoseconds.

## State and persistence behavior
The persistent mutable state is in the caller-owned `struct timecounter`: `cc`, `cycle_last`, `nsec`, `mask`, and `frac`. The file provides no locking. Callers must serialize access if concurrent readers or writers are possible. Correctness assumes the underlying counter does not wrap more than once between reads.

## Dependencies and integration points
The file depends on `linux/timecounter.h` and exports GPL symbols. It integrates with drivers and subsystems that correlate device cycles to nanoseconds without using the global kernel timekeeper directly, such as networking or PTP-style device timestamping code.

## Risks
The main risk is caller misuse: if reads are too infrequent and the cyclecounter wraps multiple times, elapsed time is undercounted. Concurrent unsynchronized reads can lose deltas by racing on `cycle_last`, `nsec`, and `frac`. Incorrect `cyclecounter` masks, shifts, or multipliers propagate directly into timestamp drift.

## Test signals
No local tests are present in this subset. Useful validation includes synthetic cyclecounter tests for wraparound, fractional carry, and concurrent access expectations, plus driver-level timestamp correlation tests. Static analysis should verify callers provide appropriate locking where shared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timecounter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timekeeping.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timekeeping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timekeeping.h -->
# sources/distributed-fs/ceph-client/kernel/time/timekeeping.h

## Purpose
This private header declares internal interfaces shared among files in `kernel/time/`. It is not the public time API; it exposes coordination hooks for timekeeping, timers, high-resolution timers, jiffies, suspend/resume, and sched clock integration.

## Important APIs, types, and functions
Declared functions include `ktime_get_update_offsets_now()`, `ktime_expiry_to_cycles()`, `timekeeping_valid_for_hres()`, `timekeeping_max_deferment()`, `timekeeping_warp_clock()`, `timekeeping_suspend()`, `timekeeping_resume()`, `update_process_times()`, `do_timer()`, and `update_wall_time()`. It also declares `jiffies_lock`, `jiffies_seq`, and `CS_NAME_LEN`. `sched_clock_suspend()`/`sched_clock_resume()` are either external declarations or no-op inline stubs based on `CONFIG_GENERIC_SCHED_CLOCK`.

## Control flow
The header itself has no runtime control flow beyond the sched-clock conditional stubs. Its purpose is compile-time wiring so timer interrupts can call process accounting and wall-time advancement, hrtimers can fetch offset updates, and architecture/syscore suspend code can enter timekeeping suspend and resume flows.

## State and persistence behavior
No state is defined here. It declares global synchronization objects for jiffies and exposes functions that operate on state owned by `timekeeping.c`, `timer.c`, and related kernel/time components.

## Dependencies and integration points
The header is included by source files inside `kernel/time`, including `time.c` and `timekeeping.c`. It connects internal timekeeping code to hrtimer and tick subsystems without exposing all implementation details to the rest of the kernel.

## Risks
Because this header defines internal coupling, signature changes can break several time subsystem files at once. Adding public-looking declarations here risks widening internal APIs. Conditional sched-clock stubs must remain consistent with the configured scheduler clock implementation.

## Test signals
Build coverage across configurations is the main signal, especially with and without `CONFIG_GENERIC_SCHED_CLOCK`, high-resolution timers, and generic clockevents. Functional tests are attached to the implementing `.c` files rather than this declaration-only header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timekeeping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timekeeping_debug.c -->
# sources/distributed-fs/ceph-client/kernel/time/timekeeping_debug.c

## Purpose
This file provides debugfs and accounting support for timekeeping suspend diagnostics. It tracks suspend sleep-time duration bins and counts multigrain timestamp floor swaps for debug visibility.

## Important APIs, types, and functions
It defines per-CPU `timekeeping_mg_floor_swaps` and a `sleep_time_bin[NUM_BINS]` histogram. `tk_debug_sleep_time_show()` renders the sleep-time histogram through seq_file. `tk_debug_sleep_time_init()` creates the `sleep_time` debugfs file at late init. `tk_debug_account_sleep_time()` accounts one suspend duration and emits a deferred PM debug message. `timekeeping_get_mg_floor_swaps()` sums per-CPU floor swap counters using `data_race()`.

## Control flow
At late init, debugfs registration creates a read-only `sleep_time` file. When suspend sleep time is injected, `timekeeping.c` calls `tk_debug_account_sleep_time()`, which bins `tv_sec` with `fls()` capped at `NUM_BINS - 1`, increments the bin, and logs the duration. Reads of debugfs iterate nonzero bins and print ranges and counts.

## State and persistence behavior
State is in memory only: a global histogram and per-CPU counters. It is not persistent across reboot. The histogram increment is not explicitly locked, reflecting debug-only use. Per-CPU multigrain counters are incremented through inline helpers in `timekeeping_internal.h` and summed locklessly for diagnostics.

## Dependencies and integration points
The file depends on debugfs, seq_file, PM suspend debug logging, and `timekeeping_internal.h`. It is compiled under debugfs support and complements the main suspend accounting in `timekeeping.c` and multigrain timestamp logic.

## Risks
The debug histogram is intentionally lightweight and may race under unusual concurrent accounting, so it should not be used as a strict accounting source. Bin boundaries are powers of two seconds; extremely long durations are capped into the final bin. Debugfs creation failures are ignored, matching typical diagnostics behavior but limiting observability.

## Test signals
Signals include debugfs presence of `sleep_time`, readable histogram formatting, PM debug logs after suspend/resume, and nonzero multigrain floor swap counts when filesystem timestamp paths use fine-grained updates. Build coverage should include `CONFIG_DEBUG_FS` enabled and disabled, where stubs in the internal header replace this functionality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timekeeping_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timekeeping_internal.h -->
# sources/distributed-fs/ceph-client/kernel/time/timekeeping_internal.h

## Purpose
This internal header defines private helpers for timekeeping debug support, safe clocksource delta calculation, timekeeper lock serialization, and NTP seconds access. It is shared by timekeeping implementation files rather than exposed as a general kernel API.

## Important APIs, types, and functions
Under `CONFIG_DEBUG_FS`, it declares per-CPU `timekeeping_mg_floor_swaps`, `timekeeping_inc_mg_floor_swaps()`, and `tk_debug_account_sleep_time()`. Without debugfs, those become no-op stubs. `clocksource_delta()` computes `(now - last) & mask` but returns zero if the delta exceeds `max_delta`, preventing backward or implausible jumps from advancing time. It also declares `timekeeper_lock_irqsave()`, `timekeeper_unlock_irqrestore()`, and `ktime_get_ntp_seconds()`.

## Control flow
The header provides inline control flow for debug and delta helpers. `clocksource_delta()` is used by timekeeping advancement paths to reject deltas beyond a clocksource-defined safe bound. Debug helpers either increment per-CPU counters or compile away depending on configuration.

## State and persistence behavior
The header itself owns no state, but it declares debug per-CPU counters and functions that manipulate core timekeeper state. `clocksource_delta()` enforces state safety by refusing large deltas rather than attempting recovery in place.

## Dependencies and integration points
It depends on clocksource, spinlock, and time definitions. It is included by `timekeeping.c` and `timekeeping_debug.c`; the delta helper is part of the core update path, and the debug hooks connect multigrain timestamp and suspend accounting to debugfs.

## Risks
Changing `clocksource_delta()` can directly affect time progression after clocksource anomalies, suspend, or cross-CPU inconsistencies. Returning zero on excessive deltas is conservative but can hide clocksource failures as stalled time. Debug conditional declarations must match the compiled implementation to avoid link or silent instrumentation issues.

## Test signals
Build coverage with and without `CONFIG_DEBUG_FS` is essential. Runtime signals include stable timekeeping under clocksource wrap conditions and debugfs counter visibility when enabled. Fault-injection or simulated clocksource tests can validate the max-delta guard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timekeeping_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timer.c -->
# sources/distributed-fs/ceph-client/kernel/time/timer.c

## Purpose
This file implements the kernel's classic timer wheel, jiffies state, timer initialization/modification/deletion APIs, timer softirq execution, nohz timer event prediction, timer migration support, process tick accounting entry points, and CPU hotplug timer migration.

## Important APIs, types, and functions
Global `jiffies_64` is exported. Core state is per-CPU `struct timer_base`, with lock, running timer pointer, base clock, next expiry, idle/pending flags, pending bitmap, and wheel buckets. Public APIs include `timer_init_key()`, stack timer init/destroy helpers, `mod_timer_pending()`, `mod_timer()`, `timer_reduce()`, `add_timer()`, `add_timer_local()`, `add_timer_global()`, `add_timer_on()`, `timer_delete()`, `timer_shutdown()`, `timer_delete_sync_try()`, `timer_delete_sync()`, `timer_shutdown_sync()`, jiffies rounding helpers, `get_next_timer_interrupt()`, `timer_base_try_to_set_idle()`, `timer_clear_idle()`, `update_process_times()`, and `timers_init()`.

## Control flow
Timers are placed into a multi-level wheel by `calc_wheel_index()`, which selects a bucket based on expiration delta and level granularity. `__mod_timer()` serializes on the timer's current base, optimizes unchanged/same-bucket updates, detaches pending timers, migrates base ownership when necessary, and enqueues into the selected bucket. Timer interrupt processing calls `update_process_times()`, which runs hrtimer queues, checks timer bases, and raises `TIMER_SOFTIRQ` when needed. The softirq runs `__run_timer_base()`, collects expired buckets, recalculates next expiry, detaches timers, drops locks around callbacks, and tracks `running_timer` for synchronous deletion.

## State and persistence behavior
Persistent runtime state is per-CPU and in-memory: timer bases, pending bitmaps, bucket lists, next-expiry calculations, nohz static keys, migration settings, and timer object flags encoding base CPU, pinned/deferrable/irqsafe/shutdown state, and wheel index. There is no disk persistence. CPU hotplug moves pending timers from dead CPU bases to the current CPU while preserving expiry behavior.

## Dependencies and integration points
The file integrates with jiffies, hrtimers, tick/nohz, timer migration hierarchy, softirqs, scheduler tick accounting, POSIX CPU timers, RCU scheduler clock ticks, irq_work, debug objects, lockdep, tracepoints, sysctl, and CPU hotplug. It is a foundational service for most kernel timeout users, including networking, block I/O, workqueues, and drivers.

## Risks
Risks are dominated by concurrency and timing semantics: timer-base locking, migration races, shutdown-vs-rearm ordering, lockdep expectations for `timer_delete_sync()`, PREEMPT_RT callback wait behavior, idle/nohz wakeups, and one-jiffy delays from lockless next-expiry reads. Wheel granularity intentionally batches far-future timers; users requiring precise expiry must use hrtimers. Incorrect pending bitmap or bucket index maintenance can lose timers or fire them late.

## Test signals
Runtime signals include timer tracepoints, debug object warnings, lockdep reports, nohz idle behavior, sysctl `kernel.timer_migration`, CPU hotplug stress, and softirq timer execution. Useful tests include timer selftests, workqueue delayed-work teardown tests using `timer_shutdown_sync()`, PREEMPT_RT coverage, nohz full/timer migration scenarios, and boot tests across different `HZ` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timer_list.c -->
# sources/distributed-fs/ceph-client/kernel/time/timer_list.c

## Purpose
This diagnostic file prints active high-resolution timers, tick scheduler state, and clock event devices through `/proc/timer_list` and SysRq-Q. It is for observability, not for timer scheduling.

## Important APIs, types, and functions
`struct timer_list_iter` tracks proc iteration state: CPU, second pass, and snapshot `now`. `SEQ_printf()` abstracts output to either seq_file or console. `print_timer()`, `print_active_timers()`, `print_base()`, `print_cpu()`, and `print_tickdevice()` emit timer and clockevent details. `sysrq_timer_list_show()` prints to console. The proc path is implemented by `timer_list_show()`, `move_iter()`, `timer_list_start()`, `timer_list_next()`, `timer_list_stop()`, `timer_list_sops`, and `init_timer_list_procfs()`.

## Control flow
SysRq output snapshots `ktime_get()` once, prints a header, iterates online CPUs, prints hrtimer bases, then prints broadcast and per-CPU tick devices when generic clockevents are enabled. The proc implementation uses seq_file iteration: the first pass prints per-CPU hrtimer/tick scheduler data, and the optional second pass prints clockevent device data. `print_active_timers()` deliberately locks, copies one timer, unlocks for printing, and repeats by index to avoid holding base locks during potentially slow formatting.

## State and persistence behavior
The file does not own scheduler state. It reads live per-CPU hrtimer bases, tick scheduler state, clockevent devices, and jiffies. Proc iterator state is per-open file private data. Output is a snapshot with possible races; it favors diagnostic usefulness and watchdog friendliness over a fully atomic global view.

## Dependencies and integration points
It depends on procfs, seq_file, kallsyms symbol formatting, hrtimer internals, tick internals, clockevents, broadcast tick support, CPU online masks, and NMI watchdog touching. It complements `timer.c` and hrtimer/tick code by exposing their current state to operators and developers.

## Risks
The main risk is diagnostic traversal racing with timer changes. The O(N*N) active timer walk is intentional to avoid printing under locks but can be expensive on systems with many timers. Pointer and symbol output must respect kernel pointer formatting/security policy. Procfs creation failure simply disables the interface.

## Test signals
Signals include successful creation and readable output of `/proc/timer_list` when `CONFIG_PROC_FS` is enabled, SysRq-Q output, stable behavior under timer churn, and watchdog non-triggering during large dumps. Build coverage should include combinations of `CONFIG_GENERIC_CLOCKEVENTS`, broadcast support, high-resolution timers, tick oneshot, and procfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/timer_list.c -->
