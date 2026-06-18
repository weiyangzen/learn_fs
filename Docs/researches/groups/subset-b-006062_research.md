# subset-b-006062 Research

Grouped source research for Linux kernel time subsystem files under `sources/distributed-fs/ceph-client/kernel/time`. Each section is marker-delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/posix-cpu-timers.c -->
# sources/distributed-fs/ceph-client/kernel/time/posix-cpu-timers.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/posix-cpu-timers.c` implements POSIX CPU clocks and CPU-time-backed POSIX timers. It supports per-thread and per-process `CPUCLOCK_PROF`, `CPUCLOCK_VIRT`, and `CPUCLOCK_SCHED` clock IDs, process/thread CPU timer creation, CPU-clock nanosleep, `RLIMIT_CPU`, `RLIMIT_RTTIME`, and the handoff between scheduler tick accounting and POSIX timer signal delivery. The complete 1670-line source was read for this report.

## Important APIs, Types, and Functions

Primary exported or externally used functions include `posix_cputimers_group_init`, `update_rlimit_cpu`, `thread_group_sample_cputime`, `posix_cpu_timers_exit`, `posix_cpu_timers_exit_group`, `run_posix_cpu_timers`, `set_process_cpu_timer`, `clear_posix_cputimers_work`, and `posix_cputimers_init_work`. The file publishes `clock_posix_cpu`, `clock_process`, and `clock_thread` as `struct k_clock` implementations. Important internal helpers are `pid_for_clock`, `cpu_clock_sample`, `cpu_clock_sample_group`, `thread_group_start_cputime`, `posix_cpu_timer_create`, `arm_timer`, `disarm_timer`, `posix_cpu_timer_set`, `posix_cpu_timer_del`, `posix_cpu_timer_get`, `collect_posix_cputimers`, `check_thread_timers`, `check_process_timers`, `posix_cpu_timer_rearm`, and `do_cpu_nanosleep`. Key state is in `struct posix_cputimers`, `struct posix_cputimer_base`, `struct cpu_timer`, `struct k_itimer`, `struct thread_group_cputimer`, and per-task or per-signal tick dependency masks.

## Control Flow

Clock access starts by decoding and validating CPU clock IDs through `pid_for_clock`, which constrains nonzero thread clocks to the caller's thread group and process clocks to process TGIDs. `clock_gettime` through the `k_clock` vtable samples either the individual task (`task_cputime`, `task_sched_runtime`) or the thread-group atomic cputime store. Process timer setup may call `thread_group_start_cputime` to synchronize group totals and enable process-wide cputime accounting before arming timers.

Timer set/disarm paths lock the target task sighand, remove any existing timerqueue node, sample current CPU time, convert relative expirations to absolute CPU-time deadlines, then enqueue the timer in the appropriate per-task or per-signal timerqueue. Scheduler tick interrupts call `run_posix_cpu_timers`, which first uses `fastpath_timer_check` against cached `nextevt` values. On expiry it collects due timers into a private firing list under sighand lock, releases sighand, then locks each timer and calls `cpu_timer_fire`. Interval timers are rearmed later from signal delivery through `posix_cpu_timer_rearm`. CPU-clock nanosleep uses a stack `k_itimer` marked `nanosleep`, sleeps the task, and stores restart state if interrupted.

## State and Persistence Behavior

There is no file-backed persistence. Runtime state is per-task and per-signal: timerqueue heads, cached next expiration values, `timers_active`, `expiry_active`, cputime atomic snapshots, timer status, overrun counters, firing flags, and `pid` references. The code deliberately keeps process-wide cputime accounting disabled until a process timer, itimer, or rlimit needs it. Tick dependencies are set while CPU timers require scheduler ticks and cleared when all cached expirations become inactive. During exit, timerqueue nodes are detached but surviving POSIX timer objects may remain addressable until deletion and RCU/reference cleanup complete.

## Dependencies and Integration Points

The file depends on scheduler cputime accounting, signal locking and delivery, PID lookup, `timerqueue`, POSIX timer core helpers in `posix-timers.c`, restart blocks, hrtimer nanosleep copyout, rlimits, deadline scheduling overrun handling, and NO_HZ tick dependency APIs from the tick subsystem. It integrates with `kernel/time/posix-timers.c` via the `struct k_clock` callbacks, with `include/linux/posix-timers.h` for `struct k_itimer`, with signal delivery via `posix_timer_queue_signal`, and with `tick-sched.c` through `tick_dep_set_task`, `tick_dep_set_signal`, and matching clear calls.

## Risks and Edge Cases

Major risks are races between timer expiry, deletion, rearming, task exit, and signal delivery. The `firing` and `handling` fields, `TIMER_RETRY`, RCU protection, sighand locking, and optional task-work mutex are all there to avoid losing a timer signal or freeing a timer while expiry runs. CPU-clock IDs are subtle because PID 0 means current thread/process and process clocks may be looked up through the caller's thread PID for `clock_gettime`. `SIGEV_NONE` timers are never queued and require synthetic forwarding during gettime. RLIMIT soft-limit updates intentionally move the soft limit forward one second/usec interval to avoid continuous signal storms. NO_HZ full correctness depends on setting tick dependencies whenever CPU timers need time to elapse.

## Test Signals

Useful test signals include POSIX CPU timer syscall tests for per-thread and per-process clocks; interval overrun tests; timer set/delete races while signals are pending; CPU-clock `clock_nanosleep` interruption and restart coverage; `ITIMER_PROF` and `ITIMER_VIRTUAL` behavior; `RLIMIT_CPU` and `RLIMIT_RTTIME` soft/hard signal behavior; task-exit cleanup under active timers; and NO_HZ full tests that verify CPU timers keep the tick running only while necessary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/posix-cpu-timers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/posix-stubs.c -->
# sources/distributed-fs/ceph-client/kernel/time/posix-stubs.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/posix-stubs.c` provides minimal POSIX clock syscall support when `CONFIG_POSIX_TIMERS=n`. It preserves basic `CLOCK_REALTIME`, `CLOCK_MONOTONIC`, and `CLOCK_BOOTTIME` behavior for settime/gettime/getres/nanosleep without supporting full POSIX timer objects. The complete 209-line source was read.

## Important APIs, Types, and Functions

The file defines native syscalls `clock_settime`, `clock_gettime`, `clock_getres`, and `clock_nanosleep`, plus compat 32-bit-time variants `clock_settime32`, `clock_gettime32`, `clock_getres_time32`, and `clock_nanosleep_time32` under `CONFIG_COMPAT_32BIT_TIME`. The main helper is `do_clock_gettime`, which switches among the supported clocks. It uses `struct timespec64`, `ktime_t`, restart-block nanosleep fields, and user-copy helpers.

## Control Flow

`clock_settime` accepts only `CLOCK_REALTIME`, copies a timespec from user space, and calls `do_sys_settimeofday64`. `clock_gettime` calls `do_clock_gettime`, which samples realtime, monotonic, or boottime and applies time namespace offsets for monotonic and boottime. `clock_getres` returns `hrtimer_resolution` for the same three clocks. `clock_nanosleep` validates the clock, copies and validates the requested time, disables remaining-time copyout for absolute sleeps, initializes the restart block, converts absolute time through `timens_ktime_to_host`, and delegates to `hrtimer_nanosleep`.

## State and Persistence Behavior

The file owns no persistent state. It mutates only the calling task's restart block for nanosleep restart/copyout behavior and relies on global timekeeping state for clock reads and realtime setting.

## Dependencies and Integration Points

Dependencies are the core timekeeping API, hrtimer nanosleep, time namespaces, syscall user-copy helpers, and compat timespec conversion helpers. This file substitutes for `posix-timers.c` when full POSIX timers are disabled, so unsupported clocks and all timer object operations fail elsewhere rather than being implemented here.

## Risks and Edge Cases

The deliberately small supported clock set is the main compatibility risk. `clock_getres` writes to `tp` unconditionally for valid clocks, unlike the full implementation which allows NULL for POSIX getres semantics. Absolute nanosleep must translate namespace-adjusted monotonic and boottime values to host time; missing that conversion would sleep until the wrong deadline in time namespaces.

## Test Signals

Build coverage with `CONFIG_POSIX_TIMERS=n`, syscall tests for the three supported clocks, negative tests for unsupported clocks, compat syscall coverage, namespace-aware absolute nanosleep tests, and realtime set permission/error tests are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/posix-stubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/posix-timers.c -->
# sources/distributed-fs/ceph-client/kernel/time/posix-timers.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/posix-timers.c` is the generic POSIX clocks and timers core. It implements POSIX timer object allocation, timer ID hashing, syscall entry points, signal queue/rearm semantics, common hrtimer-backed clock behavior, time namespace conversions, clock dispatch, and initialization of the POSIX timer cache/hash. The complete 1567-line source was read.

## Important APIs, Types, and Functions

Public syscall implementations include `timer_create`, `timer_gettime`, `timer_getoverrun`, `timer_settime`, `timer_delete`, `clock_settime`, `clock_gettime`, `clock_adjtime`, `clock_getres`, and `clock_nanosleep`, plus compat variants. Cross-file APIs include `posixtimer_deliver_signal`, `posix_timer_queue_signal`, `posixtimer_create_prctl`, `posixtimer_free_timer`, `common_timer_get`, `common_timer_set`, `posix_timer_set_common`, `common_timer_del`, and `do_clock_adjtime`. Important types and tables are `struct timer_hash_bucket`, `struct k_itimer`, `struct k_clock`, the `posix_clocks[]` dispatch table, and the static clock implementations for realtime, monotonic, raw, coarse, boottime, TAI, alarm, CPU, dynamic, and auxiliary clocks.

## Control Flow

Timer creation maps a clock ID to `struct k_clock`, allocates a `k_itimer`, reserves a unique per-process timer ID in a hash bucket, initializes signal notification metadata, copies the ID to user space, invokes the clock-specific `timer_create`, and only then marks the timer valid and links it into `signal->posix_timers`. Timer lookup is RCU-protected and then validated under `it_lock` so deletion cannot race with syscall operations.

Hrtimer-backed timers use `common_timer_set`: optionally read old state, try to cancel active hrtimer callback, reset overrun state, translate absolute times from time namespace to host time, arm via `timer_arm`, and mark non-`SIGEV_NONE` timers armed. Hrtimer expiry calls `posix_timer_fn`, which queues a signal and leaves interval rearming to signal delivery. `posixtimer_deliver_signal` drops `siglock`, locks the timer, verifies signal sequence numbers, rearms interval timers, updates overrun counts, and releases the queued reference. Deletion invalidates the timer under `siglock`, removes it from process and ignored lists, repeatedly cancels with `TIMER_RETRY` handling, then unhashes and drops references.

## State and Persistence Behavior

State is in memory only: a boot-time hash table, a slab cache, each process signal struct's timer list and next ID counter, per-timer signal metadata, overrun counters, sequence counters, hrtimer state, and reference counts. CRIU-oriented restore mode can request exact timer IDs and moves the allocator counter past restored IDs. Timer lifetime is RCU/refcounted because queued timer signals may outlive deletion from syscall-visible structures.

## Dependencies and Integration Points

The file depends on hrtimers, signal queues, PID references, ucounts for `RLIMIT_SIGPENDING`, RCU, `jhash`, timekeeping, time namespaces, dynamic POSIX clocks, alarm timers, CPU timers from `posix-cpu-timers.c`, and optional aux clocks. It integrates with signal delivery through `posixtimer_deliver_signal`, with `/proc/$PID/timers` through process timer lists, with CRIU through `PR_TIMER_CREATE_RESTORE_IDS_*`, and with architecture compat syscall layers.

## Risks and Edge Cases

Timer lifetime and signal sequencing are the central risks. A timer ID is visible to user space before the timer is valid, so invalid-marker handling on `it_signal` must remain correct. `SIGEV_NONE` timers are never enqueued and must be advanced lazily by gettime. Relative `CLOCK_REALTIME` timers intentionally switch to monotonic backing while preserving `it_clock`, which is easy to break when touching `common_hrtimer_arm`. `TIMER_RETRY` loops are required to avoid deleting or reprogramming while callbacks run, especially on PREEMPT_RT. `clockid_to_kclock` must handle negative dynamic and CPU clock IDs before array indexing, with nospec protection for positive IDs.

## Test Signals

Strong tests include POSIX timer syscall suites across realtime, monotonic, boottime, TAI, CPU, alarm, and dynamic clocks; signal delivery and interval rearm tests; overrun clamp tests; CRIU restore-ID tests; timer delete while callback/signal pending stress; `SIGEV_THREAD_ID` permission tests; time namespace absolute timer and nanosleep tests; compat 32-bit syscall tests; and KASAN/KCSAN/lockdep stress around timer lookup, delete, and exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/posix-timers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/posix-timers.h -->
# sources/distributed-fs/ceph-client/kernel/time/posix-timers.h

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/posix-timers.h` is the internal contract between the generic POSIX timer core, CPU timers, alarm/dynamic/aux clocks, and common hrtimer-backed timer helpers. The complete 53-line header was read.

## Important APIs, Types, and Functions

The header defines `TIMER_RETRY`, `enum posix_timer_state` values `POSIX_TIMER_DISARMED`, `POSIX_TIMER_ARMED`, and `POSIX_TIMER_REQUEUE_PENDING`, and the `struct k_clock` vtable. The vtable covers clock resolution, set/get, namespace-root ktime get, clock adjustment, timer create/set/get/delete/rearm/forward/remaining/cancel/arm/wait, and nanosleep. It declares clock implementations `clock_posix_cpu`, `clock_posix_dynamic`, `clock_process`, `clock_thread`, `alarm_clock`, and `clock_aux`, plus helpers `posix_timer_queue_signal`, `common_timer_get`, `common_timer_set`, `posix_timer_set_common`, and `common_timer_del`.

## Control Flow

There is no runtime control flow in the header. Its function-pointer table defines the dispatch path used by POSIX clock syscalls and timer syscalls. `posix-timers.c` maps a clock ID to `struct k_clock`; callers then invoke the appropriate callback set, allowing hrtimer, CPU timer, alarm, dynamic, and aux clocks to share syscall code while specializing timer mechanics.

## State and Persistence Behavior

The header owns no storage. It defines state names and callback signatures used by `struct k_itimer` owners. The states model whether a timer is disarmed, armed in its backend queue, or waiting for signal delivery before interval requeue.

## Dependencies and Integration Points

The header depends on kernel time types such as `clockid_t`, `ktime_t`, `timespec64`, `itimerspec64`, and `struct k_itimer`. It is included by `posix-timers.c` and `posix-cpu-timers.c`, and its declarations are implemented by the generic hrtimer code, CPU timer code, alarm timer code, dynamic POSIX clock code, and optional auxiliary clock code.

## Risks and Edge Cases

Any signature change affects every POSIX clock backend. The semantic split between `clock_get_timespec` in the current time namespace and `clock_get_ktime` in the root namespace is easy to misuse in timer code. `TIMER_RETRY` is not a normal negative errno; callers must loop while preserving timer lifetime.

## Test Signals

Compile coverage across combinations of POSIX timers, CPU timers, alarm timers, dynamic clocks, aux clocks, high-res timers, PREEMPT_RT, and compat time is the primary signal. Runtime timer set/delete races validate that all backends honor the shared `TIMER_RETRY` contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/posix-timers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/sched_clock.c -->
# sources/distributed-fs/ceph-client/kernel/time/sched_clock.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/sched_clock.c` provides generic `sched_clock()` support by extending a low-level hardware counter into a monotonic 64-bit nanosecond value. It handles clock registration, epoch updates before counter wrap, NMI-safe latch reads, suspend/resume behavior, and optional IRQ time accounting enablement. The complete 333-line source was read.

## Important APIs, Types, and Functions

Important types are `struct clock_data` and `struct clock_read_data`. Externally visible functions include `sched_clock_read_begin`, `sched_clock_read_retry`, `sched_clock_noinstr`, `sched_clock`, `sched_clock_register`, `generic_sched_clock_init`, `sched_clock_suspend`, and `sched_clock_resume`. Internal helpers include `jiffy_sched_clock_read`, `cyc_to_ns`, `__sched_clock`, `update_clock_read_data`, `update_sched_clock`, `sched_clock_poll`, and `suspended_sched_clock_read`. The file registers syscore suspend/resume callbacks and exposes the `irqtime` core parameter.

## Control Flow

Before a hardware sched clock is registered, the implementation uses jiffies as a fallback source. `sched_clock_register` rejects slower sources than the current one, calculates mult/shift and wrap duration, samples the new and old clocks to preserve epoch continuity, updates both latch copies, restarts the wrap-protection hrtimer if active, and enables IRQ time accounting for fast enough clocks or explicit `irqtime`. `sched_clock()` disables preemption, marks its critical section atomic for KCSAN, and reads the active latch copy until the seqcount is stable. `generic_sched_clock_init` finalizes the fallback if needed, updates the epoch, and starts the polling hrtimer. Suspend freezes reads at the last epoch and cancels the poll timer; resume samples the actual clock as the new epoch and restarts polling.

## State and Persistence Behavior

State is global and in memory: `cd` stores the current read function, conversion parameters, epoch cycle/ns values, counter mask, rate, and wrap interval. Two `read_data` copies are maintained so NMI readers never observe partially updated conversion data. `sched_clock_timer` periodically advances the epoch before the underlying counter wraps.

## Dependencies and Integration Points

Dependencies include clocksource math helpers, hrtimers, seqcount latch APIs, scheduler clock headers, syscore operations, module/core parameters, KCSAN annotations, and timekeeping. Architecture or platform code integrates by calling `sched_clock_register` with a counter read function, bit width, and rate. Scheduler accounting, tracing, IRQ time accounting, and timestamp users consume `sched_clock()`.

## Risks and Edge Cases

The key risk is preserving monotonic-looking nanosecond output while changing clock sources or crossing hardware counter wraps. Registration must run with interrupts disabled and must not publish mixed epoch/conversion data. Suspend handling deliberately swaps the read function to return a stable cycle value; missing that would let stopped hardware counters appear to jump. Very slow or narrow counters require correct wrap polling or `sched_clock()` can regress.

## Test Signals

Useful signals include boot logs showing registered source rate/resolution/wrap; architecture tests registering fallback and hardware clocks; suspend/resume timestamp monotonicity tests; long-running wrap tests for narrow counters; tracing/scheduler clock sanity checks; KCSAN/lockdep coverage around latch updates; and IRQ time accounting behavior with `irqtime=` overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/sched_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/sleep_timeout.c -->
# sources/distributed-fs/ceph-client/kernel/time/sleep_timeout.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/sleep_timeout.c` implements core kernel sleep helpers built on timer-wheel timers, hrtimer sleepers, and scheduler state transitions. It provides jiffy-based `schedule_timeout*`, high-resolution timeout helpers, and public millisecond/microsecond sleep APIs. The complete 377-line source was read.

## Important APIs, Types, and Functions

The file defines `struct process_timer`, `process_timeout`, exported `schedule_timeout`, `schedule_timeout_interruptible`, `schedule_timeout_killable`, `schedule_timeout_uninterruptible`, `schedule_timeout_idle`, `schedule_hrtimeout_range_clock`, `schedule_hrtimeout_range`, `schedule_hrtimeout`, `msleep`, `msleep_interruptible`, and `usleep_range_state`. It uses `struct timer_list`, `struct hrtimer_sleeper`, task states, jiffies conversion helpers, and hrtimer range APIs.

## Control Flow

`schedule_timeout` handles `MAX_SCHEDULE_TIMEOUT` by scheduling without a timer, rejects negative timeouts with diagnostics, creates an on-stack timer that wakes `current`, schedules, deletes/destroys the timer, and returns nonnegative remaining jiffies. The convenience wrappers set the current task state before calling it. `schedule_hrtimeout_range_clock` handles zero, infinite, and finite hrtimer sleeps: it creates an on-stack hrtimer sleeper, applies slack, starts it, schedules if the sleeper task remains set, cancels and destroys the timer, restores `TASK_RUNNING`, and returns 0 for expiry or `-EINTR` for early wake. `msleep` and `msleep_interruptible` loop over remaining jiffies. `usleep_range_state` repeatedly performs an absolute hrtimer range sleep until the minimum time has elapsed.

## State and Persistence Behavior

There is no persistent storage. All timers and sleepers are stack allocated and destroyed before return. The functions temporarily mutate the calling task state and rely on timer callbacks to wake that task. Return values communicate remaining time or interruption; no state survives except scheduler accounting and timer subsystem side effects.

## Dependencies and Integration Points

Dependencies include the timer wheel, hrtimers, scheduler state APIs, signal pending checks, jiffies conversion, delay APIs, and tick internals for timer/nohz integration. These helpers are widely consumed by kernel subsystems that need sleepable delays outside atomic context.

## Risks and Edge Cases

Callers must set a sleepable task state before many helpers or they will not actually sleep. On-stack timer and hrtimer objects require strict delete/destroy ordering. Negative jiffy timeout is treated as a caller bug but returns safely. `schedule_hrtimeout_range_clock(NULL, ...)` means infinite sleep and returns `-EINTR` after wake. `usleep_range_state` must handle `max < min` defensively and must not return before the minimum deadline.

## Test Signals

Signals include timer selftests for remaining jiffy values, interruptible sleep signal tests, hrtimer range/slack behavior, lockdep/KASAN checks for on-stack timer lifetime, `msleep_interruptible` early-return tests, and latency/power tests that verify `usleep_range_state` coalesces wakeups while respecting minimum sleep duration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/sleep_timeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/test_udelay.c -->
# sources/distributed-fs/ceph-client/kernel/time/test_udelay.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/test_udelay.c` is a debugfs kernel module for measuring whether `udelay()` delays at least as long as requested within a small allowed fast-error margin. Tests are configured by writing microseconds and optional iteration count to `/sys/kernel/debug/udelay_test`, then run by reading the same file. The complete 160-line source was read.

## Important APIs, Types, and Functions

Important functions are `udelay_test_single`, `udelay_test_show`, `udelay_test_open`, `udelay_test_write`, `udelay_test_init`, and `udelay_test_exit`. The file defines `DEFAULT_ITERATIONS`, `DEBUGFS_FILENAME`, module metadata, a mutex, and two configuration variables: `udelay_test_usecs` and `udelay_test_iterations`. It exposes `udelay_test_debugfs_ops` using `single_open`, `seq_read`, and a write handler.

## Control Flow

Module init creates the debugfs file. A write copies a short user buffer, parses `USECS [ITERS]`, defaults iterations when omitted, and updates configuration under `udelay_test_lock`. A read snapshots the configuration under the same mutex. Positive usec/iteration values run `udelay_test_single`, which loops, samples `ktime_get_ns` before and after `udelay`, tracks min/max/average, counts cases that are more than 0.5 percent fast, warns on negative deltas, and prints one summary line. A zero usec value prints usage and current `loops_per_jiffy`/ktime. Module exit removes the debugfs file.

## State and Persistence Behavior

State is limited to module globals protected by a mutex. Configuration persists only while the module is loaded. Test results are generated on demand and are not stored.

## Dependencies and Integration Points

The file depends on debugfs, seq_file, user copy, `udelay`, `ktime_get_ns`, `loops_per_jiffy`, mutexes, and kernel module infrastructure. It integrates with manual debug workflows rather than automated syscalls.

## Risks and Edge Cases

`sscanf` accepts negative usec/iteration values; negative or zero usec values avoid running a test and may show usage instead. Very large iteration counts can monopolize CPU because `udelay` busy-waits. The allowed error calculation uses integer arithmetic (`usecs * 5` ns) and only detects fast delays, not excessive slow delays except via printed max/avg. Debugfs creation failure is not checked.

## Test Signals

Signals include loading/unloading the module, writing valid and invalid debugfs input, checking output for expected min/avg/max and FAIL count, running with several `udelay` values across HZ/CPU-frequency configurations, and validating that debugfs removal leaves no stale file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/test_udelay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-broadcast-hrtimer.c -->
# sources/distributed-fs/ceph-client/kernel/time/tick-broadcast-hrtimer.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/tick-broadcast-hrtimer.c` implements an hrtimer-backed pseudo clock-event device used as a broadcast tick source. It lets the generic tick broadcast code emulate a broadcast clockevent when no suitable hardware broadcast device is available. The complete 104-line source was read.

## Important APIs, Types, and Functions

The main global state is `static struct hrtimer bctimer` and `static struct clock_event_device ce_broadcast_hrtimer`. Important functions are `bc_shutdown`, `bc_set_next`, `bc_handler`, and externally visible `tick_setup_hrtimer_broadcast`.

## Control Flow

`tick_setup_hrtimer_broadcast` initializes `bctimer` on `CLOCK_MONOTONIC` and registers `ce_broadcast_hrtimer` with the clockevents layer. The broadcast core programs the pseudo device through `bc_set_next`, which starts the hrtimer at an absolute pinned hard deadline and records the CPU base in `bc->bound_on`. When the hrtimer expires, `bc_handler` invokes the clockevent device's event handler, which is installed by the generic broadcast code. Shutdown uses `hrtimer_try_to_cancel` rather than a blocking cancel to avoid lock inversion with the broadcast handler.

## State and Persistence Behavior

State is global and in memory. The clockevent advertises oneshot and hrtimer features, broad CPU affinity, delta limits, and the current CPU it is bound on. `bctimer` persists for the lifetime of the kernel after registration.

## Dependencies and Integration Points

Dependencies include hrtimers, clockevents, CPU masks, and `tick-internal.h`. This file integrates directly with `tick-broadcast.c`: the generic broadcast logic treats `ce_broadcast_hrtimer` as a broadcast device but contains special handling to avoid recursion and to keep the CPU that owns the hrtimer out of deep idle.

## Risks and Edge Cases

The shutdown path is intentionally non-blocking because `tick_broadcast_lock` may be held while the callback is waiting for the same lock. `bc_set_next` cannot cancel or synchronously move a running hrtimer callback, so the timer may remain on its current CPU; `bound_on` must match the real hrtimer base after start. Broadcast recursion is a risk if the hrtimer broadcast device tries to run a local handler that expires the same hrtimer path.

## Test Signals

Relevant tests include booting systems that rely on hrtimer broadcast, NO_HZ idle entry/exit with hrtimer broadcast active, CPU hotplug when the broadcast hrtimer is bound to an outgoing CPU, suspend/resume, and lockdep tests around broadcast lock and hrtimer callback interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-broadcast-hrtimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-broadcast.c -->
# sources/distributed-fs/ceph-client/kernel/time/tick-broadcast.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/tick-broadcast.c` manages generic tick broadcast support. It selects a broadcast clockevent device, tracks CPUs whose local tick devices stop or are placeholders, broadcasts periodic and oneshot tick events, handles deep-idle enter/exit, supports oneshot wakeup devices, and coordinates CPU hotplug, suspend, and resume. The complete 1248-line source was read.

## Important APIs, Types, and Functions

External APIs include `tick_get_broadcast_device`, `tick_get_broadcast_mask`, `tick_get_wakeup_device`, `tick_install_broadcast_device`, `tick_is_broadcast_device`, `tick_broadcast_update_freq`, `tick_device_uses_broadcast`, `tick_receive_broadcast`, `tick_broadcast_control`, `tick_set_periodic_handler`, `tick_broadcast_offline`, `tick_suspend_broadcast`, `tick_resume_check_broadcast`, `tick_resume_broadcast`, `tick_get_broadcast_oneshot_mask`, `tick_check_broadcast_expired`, `tick_check_oneshot_broadcast_this_cpu`, `__tick_broadcast_oneshot_control`, `tick_broadcast_switch_to_oneshot`, `hotplug_cpu__broadcast_tick_pull`, `tick_broadcast_oneshot_active`, `tick_broadcast_oneshot_available`, and `tick_broadcast_init`. Key state includes `tick_broadcast_device`, `tick_broadcast_mask`, `tick_broadcast_on`, `tick_broadcast_oneshot_mask`, `tick_broadcast_pending_mask`, `tick_broadcast_force_mask`, per-CPU `tick_oneshot_wakeup_device`, and `tick_broadcast_lock`.

## Control Flow

Clockevent registration calls may install a device as either a per-CPU oneshot wakeup device or the global broadcast device if it is not dummy, per-CPU, or C3STOP-affected and has sufficient rating. Periodic broadcast uses `tick_handle_periodic_broadcast`: under the broadcast lock it computes online CPUs in `tick_broadcast_mask`, sends remote broadcast callbacks, optionally handles the local CPU after dropping the lock, and reprograms oneshot-style broadcast devices for the next period.

For oneshot broadcast, idle entry calls `__tick_broadcast_oneshot_control(TICK_BROADCAST_ENTER)`. The code may refuse deep idle if the current CPU owns an hrtimer broadcast event, otherwise it sets the CPU in the oneshot mask, shuts down the local timer if safe, and programs the broadcast device to the earliest sleeping CPU deadline. The broadcast interrupt scans sleeping CPUs for expired local `next_event` values, marks pending remote events, combines forced wakeups, sends broadcast IPIs/callbacks, and arms the next earliest event. Idle exit clears mask state, restores the local device, and either avoids reprogramming when a broadcast IPI is pending or forces the broadcast path to deliver an already expired local event.

## State and Persistence Behavior

All state is in memory and mostly global cpumasks protected by `tick_broadcast_lock`. `tick_broadcast_mask` covers CPUs needing periodic broadcast; `tick_broadcast_on` records explicit broadcast mode requests; oneshot, pending, and force masks track sleeping CPUs and in-flight events. Per-CPU wakeup device pointers persist until replaced or CPU offline. Suspend shuts down the broadcast device but preserves masks; resume reinitializes the device according to the saved mode and masks.

## Dependencies and Integration Points

The file depends on clockevents, cpumasks, SMP broadcast callbacks, IRQ affinity, hrtimers, CPU hotplug, suspend/resume, NO_HZ, and per-CPU `tick_cpu_device` from `tick-common.c`. It integrates with `tick-oneshot.c` for oneshot mode switching, `tick-sched.c` for idle/nohz behavior, and `tick-broadcast-hrtimer.c` for hrtimer pseudo broadcast devices.

## Risks and Edge Cases

Broadcast correctness is sensitive to cpumask races, offline CPUs, hrtimer broadcast ownership, and local handler recursion. Hrtimer broadcast devices cannot let their owning CPU enter deep idle or the broadcast event may never fire. Pending and force masks avoid repeated reprogramming and ping-pong when a CPU wakes just as its local deadline expires. Device replacement during oneshot mode must avoid setting oneshot bits for CPUs that are not actually idle. Missing broadcast function support degrades to a critical warning path where CPUs may become unresponsive.

## Test Signals

Important signals include platforms with C3STOP local timers, systems using hrtimer broadcast fallback, NO_HZ idle and full dynticks tests, CPU hotplug while CPUs are in broadcast masks, suspend/resume with broadcast active, dynamic clockevent replacement, IRQ affinity changes, and lockdep/KCSAN stress around `tick_broadcast_lock` and mask updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-broadcast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-common.c -->
# sources/distributed-fs/ceph-client/kernel/time/tick-common.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/tick-common.c` contains the generic periodic tick and clockevent device management core. It owns per-CPU tick device selection, periodic tick handling, `do_timer()` CPU assignment and handoff, replacement policy for clockevent devices, suspend/resume, CPU hotplug shutdown, and system freeze/unfreeze support. The complete 595-line source was read.

## Important APIs, Types, and Functions

Global state includes `DEFINE_PER_CPU(struct tick_device, tick_cpu_device)`, `ktime_t tick_next_period`, and `int tick_do_timer_cpu`. Important functions are `tick_get_device`, `tick_is_oneshot_available`, `tick_handle_periodic`, `tick_setup_periodic`, `tick_install_replacement`, `tick_check_replacement`, `tick_check_new_device`, `tick_broadcast_oneshot_control`, `tick_assert_timekeeping_handover`, `tick_cpu_dying`, `tick_shutdown`, `tick_suspend_local`, `tick_resume_local`, `tick_suspend`, `tick_resume`, `tick_freeze`, `tick_unfreeze`, and `tick_init`. Internal helpers include `tick_periodic`, `tick_setup_device`, `tick_check_percpu`, and `tick_check_preferred`.

## Control Flow

Periodic tick interrupts call `tick_handle_periodic`, which clears forced-next-event state, invokes `tick_periodic`, and, for devices operated in oneshot mode, repeatedly programs the next tick while catching up if timekeeping is valid for high-resolution operation. `tick_periodic` lets only `tick_do_timer_cpu` update jiffies/timekeeping via `do_timer` and `update_wall_time`; all CPUs still perform process accounting and profiling.

When a clockevent device is registered, `tick_check_new_device` compares it with the current per-CPU device using CPU affinity, oneshot support, rating, and current mode. If selected, `tick_setup_device` assigns first-time `do_timer` duty, preserves previous handler/next event on replacement, pins IRQ affinity if needed, asks broadcast logic whether this device should be controlled by broadcast, and configures periodic or oneshot mode. If not selected locally, the device may become the broadcast device. Hotplug and suspend paths shut down or resume per-CPU and broadcast devices while preserving tick mode.

## State and Persistence Behavior

State is kernel-resident. Each CPU has a `tick_device` pointer and mode. `tick_next_period` tracks the next periodic tick under `jiffies_lock`/`jiffies_seq`. `tick_do_timer_cpu` records which CPU updates global jiffies/timekeeping and can be transferred during NO_HZ idle or CPU hotplug. Suspend freeze state is protected by `tick_freeze_lock` and `tick_freeze_depth`.

## Dependencies and Integration Points

Dependencies include clockevents, jiffies/timekeeping, scheduler process accounting, profiling, hrtimers, CPU hotplug, suspend/resume, lockdep, tracepoints, broadcast support, NO_HZ, and high-resolution timer transition code. It integrates with `tick-broadcast.c` for broadcast device decisions, `tick-oneshot.c` for oneshot setup, and `tick-sched.c` for NO_HZ initialization and dying-CPU tick scheduler cleanup.

## Risks and Edge Cases

The `do_timer()` owner must never disappear without handoff or jiffies stall. Device replacement must avoid returning a broadcast device to the clockevents layer incorrectly. A non-per-CPU device may need IRQ affinity pinning, and existing CPU-local devices are preferred even with lower rating. Periodic devices that lack true periodic mode are emulated with oneshot reprogramming and can loop if timekeeping is invalid. Freeze/unfreeze runs in constrained suspend contexts, including PREEMPT_RT lockdep exceptions.

## Test Signals

Strong signals include clockevent registration/replacement tests, boot on systems with per-CPU and global timer devices, highres and lowres tick modes, CPU hotplug with the timekeeping CPU going down, suspend/resume and freeze/unfreeze, NO_HZ handoff tests, and tracing/profiling checks that process accounting still runs on non-timekeeping CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-internal.h -->
# sources/distributed-fs/ceph-client/kernel/time/tick-internal.h

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/tick-internal.h` is the private header tying together generic clockevents, tick broadcast, oneshot/high-resolution tick, NO_HZ, timer wheel, hrtimer, and timekeeping internals. The complete 213-line header was read.

## Important APIs, Types, and Functions

The header defines `struct timer_events`, `TICK_DO_TIMER_NONE`, `TICK_DO_TIMER_BOOT`, `JIFFIES_SHIFT`, and declares `tick_cpu_device`, `tick_next_period`, and `tick_do_timer_cpu`. It declares tick setup and lifecycle functions, clockevent helpers, broadcast functions, oneshot functions, NO_HZ functions, timer-wheel idle/remote helpers, hrtimer bases, clock-was-set helpers, `hrtimers_resume_local`, and `sysfs_get_uname`. It also provides no-op or BUG stubs when generic clockevents, broadcast, oneshot, or NO_HZ configs are disabled.

## Control Flow

The header has no runtime flow itself. It controls compile-time dispatch by exposing real functions only for enabled configurations and stubs otherwise. Source files such as `tick-common.c`, `tick-broadcast.c`, `tick-oneshot.c`, `tick-sched.c`, and timer code include this header to call each other without making these interfaces public.

## State and Persistence Behavior

No storage is owned here, but it declares global/per-CPU state owned elsewhere. The constants and prototypes define how jiffies, tick devices, broadcast masks, hrtimer bases, and timer idle state are coordinated.

## Dependencies and Integration Points

Dependencies include `linux/hrtimer.h`, `linux/tick.h`, `timekeeping.h`, and `tick-sched.h`. The header is an integration point between clockevents and the timer wheel/hrtimer subsystems, and between tick management and NO_HZ full/idle behavior.

## Risks and Edge Cases

Configuration stubs must preserve caller semantics. For example, `tick_broadcast_oneshot_available()` falls back to `tick_oneshot_possible()` when broadcast support is absent, and `tick_program_event()` is a harmless stub without oneshot support. `JIFFIES_SHIFT` selection is tuned to avoid NTP adjustment overflow at low HZ values; changing it can break jiffies clocksource math.

## Test Signals

Compile matrix coverage across `CONFIG_GENERIC_CLOCKEVENTS`, `CONFIG_GENERIC_CLOCKEVENTS_BROADCAST`, `CONFIG_TICK_ONESHOT`, `CONFIG_NO_HZ_COMMON`, `CONFIG_NO_HZ_FULL`, SMP, and hotplug is the key signal. Runtime tests should cover the real functions declared here in full-feature configs and ensure stub configs still boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-legacy.c -->
# sources/distributed-fs/ceph-client/kernel/time/tick-legacy.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/tick-legacy.c` provides the timer tick function for architectures that have not converted to generic clockevents. The complete 37-line source was read.

## Important APIs, Types, and Functions

The file exposes one function, `legacy_timer_tick(unsigned long ticks)`. It uses `jiffies_lock`, `jiffies_seq`, `do_timer`, `update_wall_time`, `update_process_times`, `profile_tick`, and `get_irq_regs`.

## Control Flow

Architectural timer interrupt code calls `legacy_timer_tick` with the number of elapsed ticks. If `ticks` is nonzero, the function updates jiffies under the jiffies lock and sequence counter, then updates wall time. Regardless of whether this CPU advanced timekeeping, it performs process time accounting and profiling for the interrupted context.

## State and Persistence Behavior

The function updates global timekeeping state (`jiffies`, wall time) only when `ticks` is nonzero. It owns no persistent state of its own.

## Dependencies and Integration Points

This file integrates legacy architecture timer interrupt paths with the common scheduler accounting and timekeeping code. It depends on low-level IRQ register state, profiling, and `timekeeper_internal.h`.

## Risks and Edge Cases

Callers must invoke it with interrupts disabled. A zero `ticks` argument means the current CPU is not responsible for global timekeeping but still needs process accounting; losing that distinction could double-advance jiffies or skip accounting.

## Test Signals

Boot and timer interrupt tests on non-generic-clockevent architectures, jiffies progression checks, process CPU accounting, profiling tick behavior, and lockdep validation around interrupt-disabled calls are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-oneshot.c -->
# sources/distributed-fs/ceph-client/kernel/time/tick-oneshot.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/tick-oneshot.c` manages switching CPU-local tick devices from periodic mode to oneshot mode for high-resolution timers and NO_HZ. It also programs the next oneshot event and resumes stopped oneshot devices. The complete 146-line source was read.

## Important APIs, Types, and Functions

External functions are `tick_program_event`, `tick_resume_oneshot`, `tick_setup_oneshot`, `tick_switch_to_oneshot`, `tick_oneshot_mode_active`, and, under `CONFIG_HIGH_RES_TIMERS`, `tick_init_highres`. The code operates on per-CPU `tick_cpu_device`, `struct clock_event_device`, and event handlers such as `hrtimer_interrupt`.

## Control Flow

`tick_switch_to_oneshot` validates that the current CPU has a functional oneshot-capable clockevent device, sets the per-CPU tick mode to oneshot, installs the requested event handler, switches the device state, and asks broadcast code to switch to oneshot as well. `tick_setup_oneshot` configures a replacement device with a handler and initial event. `tick_program_event` handles `KTIME_MAX` by stopping the device, restarts a stopped oneshot device when a real deadline appears, and delegates programming to clockevents. `tick_resume_oneshot` restarts oneshot mode at `ktime_get()` after resume. `tick_init_highres` switches the handler to `hrtimer_interrupt`.

## State and Persistence Behavior

The file mutates per-CPU tick device mode, event handler, clockevent state, and `next_event`. It owns no independent storage.

## Dependencies and Integration Points

Dependencies include clockevents, per-CPU tick devices, hrtimer interrupt handling, broadcast oneshot transition, and high-resolution timer configuration. It is called by `tick-common.c` during device setup/replacement and by `tick-sched.c` during NO_HZ activation.

## Risks and Edge Cases

Switching fails if no device exists, the device is dummy/nonfunctional, or it lacks oneshot support. Programming `KTIME_MAX` must stop the device cleanly so deep NO_HZ idle can avoid unnecessary interrupts. Resume forces an immediate event to resynchronize timers. Broadcast must be switched along with local devices or CPUs with stopped local timers can miss ticks.

## Test Signals

Signals include high-resolution timer enablement, low-resolution NO_HZ switching, device replacement while in oneshot mode, `KTIME_MAX` stop/restart paths, suspend/resume in oneshot mode, and boot tests on systems lacking oneshot support to verify graceful failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-oneshot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-sched.c -->
# sources/distributed-fs/ceph-client/kernel/time/tick-sched.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/tick-sched.c` implements NO_HZ idle/full dynticks and scheduler tick emulation. It manages per-CPU tick hrtimers, jiffies catch-up, idle sleep accounting, tick dependency tracking, full-dynticks kicks, next-event calculation, tick stop/restart, IRQ idle transitions, and CPU hotplug cleanup. The complete 1716-line source was read.

## Important APIs, Types, and Functions

Important external functions include `tick_get_tick_sched`, `tick_nohz_dep_set`, `tick_nohz_dep_clear`, `tick_nohz_dep_set_cpu`, `tick_nohz_dep_clear_cpu`, `tick_nohz_dep_set_task`, `tick_nohz_dep_clear_task`, `tick_nohz_dep_set_signal`, `tick_nohz_dep_clear_signal`, `__tick_nohz_task_switch`, `tick_nohz_full_setup`, `tick_nohz_cpu_hotpluggable`, `tick_nohz_init`, `tick_nohz_is_active`, `tick_nohz_tick_stopped`, `tick_nohz_tick_stopped_cpu`, `get_cpu_idle_time_us`, `get_cpu_iowait_time_us`, `get_jiffies_update`, `tick_nohz_idle_stop_tick`, `tick_nohz_idle_retain_tick`, `tick_nohz_idle_enter`, `tick_nohz_irq_exit`, `tick_nohz_idle_got_tick`, `tick_nohz_get_next_hrtimer`, `tick_nohz_get_sleep_length`, `tick_nohz_get_idle_calls_cpu`, `tick_nohz_idle_restart_tick`, `tick_nohz_idle_exit`, `tick_irq_enter`, `tick_setup_sched_timer`, `tick_sched_timer_dying`, `tick_clock_notify`, `tick_oneshot_notify`, and `tick_check_oneshot_change`. Key state is per-CPU `struct tick_sched`, `last_jiffies_update`, `tick_nohz_full_mask`, `tick_nohz_full_running`, and global/per-CPU/task/signal tick dependency masks.

## Control Flow

The per-CPU scheduler tick hrtimer runs `tick_nohz_handler`. It updates jiffies through `tick_sched_do_timer`, performs process accounting when IRQ regs are available, and either restarts for the next period or stops if NO_HZ has disabled the tick. Jiffies updates use a fast 64-bit acquire check or 32-bit seqcount check, then serialize under `jiffies_lock` and update `last_jiffies_update`, `tick_next_period`, load average, and wall time.

Idle entry sets `TS_FLAG_INIDLE` and starts idle accounting. The idle governor can call `tick_nohz_get_sleep_length`, which computes the next timer event, honors RCU/arch/irq_work/local timer softirq needs, limits the timekeeping CPU by `timekeeping_max_deferment`, and caches the result. `tick_nohz_idle_stop_tick` sets timer bases idle, hands off `tick_do_timer_cpu` if needed, records accounting stats, and programs either the per-CPU hrtimer or clockevent for the next real deadline. IRQ entry/exit and idle exit stop idle accounting, update stale jiffies, and restart or keep stopped the tick depending on NO_HZ full dependencies.

For NO_HZ full, dependency setters mark global, CPU, task, or signal dependencies and kick affected full-dynticks CPUs through IRQ work. On task switch, a stopped full-dynticks CPU rechecks current task/signal dependencies and restarts if needed.

## State and Persistence Behavior

All state is in memory and per-CPU/global. `struct tick_sched` stores flags, scheduler tick hrtimer, last/next tick deadlines, idle accounting times, cached timer expiration data, idle call counters, dependency masks, and clock-change notification bits. State persists across idle cycles and is partially preserved across CPU dying cleanup for cumulative idle/iowait counters. Boot parameters `nohz=` and `skew_tick=` affect runtime behavior.

## Dependencies and Integration Points

Dependencies include hrtimers, clockevents, jiffies/timekeeping, timer wheel idle APIs, RCU, irq_work, scheduler context tracking, load average, vmstat, softlockup watchdog, CPU hotplug, NO_HZ full masks, POSIX CPU timer dependencies, perf/scheduler tick dependencies, and tracepoints. It integrates with `tick-common.c` for tick device state and `tick_do_timer_cpu`, with `tick-oneshot.c` for event programming, with timer wheel code for next timer deadlines, and with POSIX CPU timers through `tick_nohz_dep_set_task/signal`.

## Risks and Edge Cases

Stopping the tick can stall jiffies if the timekeeping CPU sleeps without handoff, so `TS_FLAG_DO_TIMER_LAST` and `TICK_DO_TIMER_NONE` are critical. Local pending timer softirqs, RCU needs, irq_work, arch hooks, and reschedule requests must prevent tick stop. NO_HZ full must restart the tick when dependencies appear, including POSIX CPU timers and perf events. Stale cached `timer_expires_base` must be cleared after use. Hrtimer and lowres paths differ in whether `sched_timer` or the clockevent is programmed. Idle/iowait accounting is documented as potentially observing backward values because remote iowait counters are unsynchronized.

## Test Signals

Strong signals include NO_HZ idle/full boot tests, cpuidle sleep-length validation, jiffies progression under long idle and stop-machine/VMEXIT stalls, POSIX CPU timer and perf dependencies on nohz_full CPUs, CPU hotplug and dying cleanup, suspend/resume idle accounting, softirq-pending tick-stop warnings, highres and lowres configurations, and tracepoint checks for tick stop/restart reasons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-sched.h -->
# sources/distributed-fs/ceph-client/kernel/time/tick-sched.h

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/tick-sched.h` defines the private tick scheduling data structures and flags shared by NO_HZ, high-resolution tick, generic tick device, and broadcast code. The complete 124-line header was read.

## Important APIs, Types, and Functions

The header defines `enum tick_device_mode`, `struct tick_device`, `TS_FLAG_INIDLE`, `TS_FLAG_STOPPED`, `TS_FLAG_IDLE_ACTIVE`, `TS_FLAG_DO_TIMER_LAST`, `TS_FLAG_NOHZ`, `TS_FLAG_HIGHRES`, and `struct tick_sched`. It declares `tick_get_tick_sched`, `tick_setup_sched_timer`, `tick_sched_timer_dying` or its stub, and `__tick_broadcast_oneshot_control` or its stub.

## Control Flow

There is no executable control flow beyond config-dependent inline stubs. The data definitions shape runtime flow in `tick-common.c`, `tick-broadcast.c`, `tick-oneshot.c`, and `tick-sched.c`: each CPU has a tick device mode, and each CPU's `tick_sched` flags determine whether it is in idle, has stopped the tick, uses NO_HZ, or runs a high-resolution scheduler tick.

## State and Persistence Behavior

The header owns no storage but defines per-CPU persistent state fields. `struct tick_sched` retains scheduler tick hrtimer state, last/next tick times, idle and iowait sleep accounting, cached next timer deadlines, idle counters, dependency masks, and clock-change notification state across idle transitions.

## Dependencies and Integration Points

It depends on `linux/hrtimer.h` and, for broadcast declarations, on tick broadcast configuration. The header is included by `tick-internal.h` and is the structural contract between tick scheduler implementation and the rest of the tick subsystem.

## Risks and Edge Cases

Flag semantics are tightly coupled to interrupt-disabled sections. Misinterpreting `TS_FLAG_INIDLE` versus `TS_FLAG_IDLE_ACTIVE` can break idle accounting during IRQ entry. `TS_FLAG_STOPPED` controls whether the scheduler tick must be restarted. `TS_FLAG_DO_TIMER_LAST` is part of safe jiffies handoff after a timekeeping CPU enters NO_HZ idle.

## Test Signals

Compile coverage for oneshot and non-oneshot configs validates the stubs. Runtime NO_HZ idle/full tests, high-resolution tick tests, broadcast enter/exit tests, and CPU hotplug tests validate that the fields are updated consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/tick-sched.h -->
