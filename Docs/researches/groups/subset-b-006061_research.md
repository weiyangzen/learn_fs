# Research Group: subset-b-006061

This grouped report covers Linux kernel time subsystem files under `sources/distributed-fs/ceph-client/kernel/time/`. Each file section preserves the source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/alarmtimer.c -->
# sources/distributed-fs/ceph-client/kernel/time/alarmtimer.c

Purpose: implements alarm timers, a hrtimer-like abstraction that can program an RTC alarm to wake the system from suspend. It backs `CLOCK_REALTIME_ALARM` and `CLOCK_BOOTTIME_ALARM` POSIX clocks and exposes exported kernel helpers such as `alarm_init()`, `alarm_start()`, `alarm_cancel()`, `alarm_forward()`, and `alarmtimer_get_rtcdev()`.

Important state and control flow: `alarm_bases[]` holds one timerqueue, spinlock, base clock id, and time reader per alarm type. `alarm_start()` records an absolute expiry, queues the alarm under the base lock, and arms the embedded hrtimer. `alarmtimer_fired()` dequeues the alarm and invokes the caller callback with current base time. Suspend scans all bases and freezer sleep state for the earliest expiry, bounds the delta via RTC limits, then starts `rtctimer`; resume cancels it. POSIX timer flow converts clock ids through `clock2alarm()`, requires `CAP_WAKE_ALARM`, and wires alarm callbacks into `common_timer_*`.

Dependencies and integration: depends on hrtimers, timerqueue, RTC class, platform driver PM callbacks, POSIX timer internals, freezer state, tracepoints, and time namespaces for absolute alarm nanosleep conversion. The device init path registers the RTC class interface and `alarmtimer` platform driver.

Risks and test signals: correctness depends on lock ordering between base locks, `freezer_delta_lock`, and hrtimer cancellation waits. RTC absence returns `-EOPNOTSUPP` or `-EINVAL`, so tests need both RTC and no-RTC configurations. Suspend wake tests should cover near-expiry `-EBUSY`, bounded RTC alarm ranges, namespace-adjusted absolute sleeps, restart-block behavior, and `CAP_WAKE_ALARM` permission failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/alarmtimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/clockevents.c -->
# sources/distributed-fs/ceph-client/kernel/time/clockevents.c

Purpose: manages registered `struct clock_event_device` instances, their state transitions, frequency configuration, event programming, release/replacement, suspend/resume, CPU hotplug cleanup, and optional sysfs control.

Important APIs and flow: `clockevents_register_device()` initializes a device as detached, fixes missing CPU masks, adds it to `clockevent_devices`, and asks tick code to select it. `clockevents_switch_state()` funnels state changes through device callbacks and enforces feature support for periodic, oneshot, and stopped states. `clockevents_program_event()` converts absolute monotonic expiry to device cycles, handles hrtimer-backed devices, coupled clocksource devices, minimum-delta fallback, forced events, and past expiries. `clockevents_config_and_register()` and `clockevents_update_freq()` compute mult/shift and min/max nanosecond bounds. Unbind paths coordinate `clockevents_mutex`, `clockevents_lock`, and CPU-local replacement via `smp_call_function_single()`.

State and persistence: global lists track active and released devices; per-device state, `next_event`, min/max delta, retries, owner module references, and forced-event state persist until exchange/unbind/hotplug removal. Sysfs exposes current and unbind controls for per-CPU and broadcast devices.

Dependencies and integration: tightly coupled to `tick-internal.h`, tick broadcast, CPU hotplug, clockchips, hrtimer broadcast devices, sysfs, module ownership, SMP callbacks, and optional generic min-delta adjustment/coupled-clockevent configs.

Risks and test signals: event programming is sensitive to overflow in latch-to-ns math, zero `mult`, devices with too-small min deltas, remote unbind races, and broadcast-device replacement. Test with periodic/oneshot devices, failing `set_next_event`, frequency changes while active, CPU offline paths, sysfs unbind failures, and coupled clocksource conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/clockevents.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/clocksource-wdtest.c -->
# sources/distributed-fs/ceph-client/kernel/time/clocksource-wdtest.c

Purpose: loadable or built-in unit test for the clocksource watchdog. It registers a synthetic `wdtest-ktime` clocksource and injects delay, positive skew, negative skew, and per-CPU skew to verify watchdog classification.

Important APIs and flow: `wdtest_ktime_read()` returns raw fast time, optionally delayed or offset. A watchdog interval counter advances only after a quarter second so retries observe consistent injection behavior. `wdtest_clocksource_reset()` unregisters, resets state, configures flags such as `CLOCK_SOURCE_MUST_VERIFY`, `CLOCK_SOURCE_WDTEST`, and optional `CLOCK_SOURCE_WDTEST_PERCPU`, then registers the test clocksource at 1 GHz. `wdtest_execute()` waits for expected `CLOCK_SOURCE_VALID_FOR_HRES` or `CLOCK_SOURCE_UNSTABLE` flags, and `wdtest_run()` sequences the clean, delay, positive, and negative cases for global and per-CPU modes.

State and persistence: state is module-global: injection mode, test count, last timestamp, offset, synthetic clocksource flags, and the kthread pointer. Built-in mode exits after test execution; module mode keeps a sleeping thread until unload so cleanup can stop it.

Dependencies and integration: depends on clocksource registration/unregistration, kthreads, `ktime_get_raw_fast_ns()`, delay loops, watchdog flags from core clocksource code, and `tick-internal.h`/timekeeping internals.

Risks and test signals: the file itself is a test signal. Fragility comes from timing thresholds, scheduler delays, and watchdog interval assumptions. Expected output is success after all injected cases pass; failure logs distinguish unexpected unstable/highres flags and timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/clocksource-wdtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/clocksource.c -->
# sources/distributed-fs/ceph-client/kernel/time/clocksource.c

Purpose: core clocksource registry, selection, watchdog verification, suspend-time measurement, sysfs override/unbind, and conversion math. It exports clocksource registration/update helpers and unstable marking used by architecture and driver code.

Important APIs and flow: `clocks_calc_mult_shift()` and `clocks_calc_max_nsecs()` compute scaled conversion limits. `__clocksource_register_scale()` initializes arch state, validates id/VDSO mode, updates frequency scaling, inserts the clocksource by rating, attaches watchdog state, selects current/watchdog/suspend clocks, and notifies timekeeping. `__clocksource_select()` chooses the best clocksource subject to boot/sysfs override and high-res validity. The watchdog timer compares candidate deltas against a continuous watchdog, checks remote CPU skew via async SMP calls, marks unstable clocks, drops their rating to zero in a kthread, and may trigger re-selection. Suspend helpers use a nonstop suspend clocksource to measure slept nanoseconds.

State and persistence: global state includes `curr_clocksource`, `suspend_clocksource`, `clocksource_list`, `override_name`, boot completion, watchdog list/timer/work, and per-CPU watchdog exchange data. Sysfs persists user override until changed or invalidated.

Dependencies and integration: integrated with timekeeping notification, tick high-res/nohz mode, VDSO clock modes, CPU topology/NUMA distances, kthreads/workqueues, sysfs, boot parameters `clocksource=` and deprecated `clock=`, and architecture clocksource hooks.

Risks and test signals: risks include watchdog false positives after long stalls, remote CPU timeout/skew detection, fallback failure when unbinding current/watchdog clocks, overflow in conversion math, and invalid VDSO mode. Test via watchdog unit module, sysfs selection/unbind, suspend/resume deltas, boot overrides, high-res enablement after validation, and unstable-clock re-selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/clocksource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/hrtimer.c -->
# sources/distributed-fs/ceph-client/kernel/time/hrtimer.c

Purpose: implements high-resolution timers, per-CPU timer bases, enqueue/cancel/restart semantics, hardirq and softirq expiry, nanosleep, clock-set reprogramming, high-res activation, and CPU hotplug migration.

Important APIs and flow: exported APIs include `hrtimer_setup()`, `hrtimer_start_range_ns()`, `hrtimer_try_to_cancel()`, `hrtimer_cancel()`, `hrtimer_forward()`, `__hrtimer_get_remaining()`, `hrtimer_cb_get_time()`, sleeper helpers, nanosleep syscalls, and CPU hotplug hooks. Timers live in per-CPU `hrtimer_bases` split by clock and hard/soft context. Start locks the current base, converts relative expiries, may migrate to a nohz housekeeping CPU, enqueues into a timerqueue, and reprograms only the local clockevent when needed. Expiry removes the timer, drops the base lock around callbacks, handles restart, and uses sequence barriers so `hrtimer_active()` avoids false negatives. High-res interrupt processes hard timers, raises softirq for soft timers, detects hangs, and rearms the clockevent.

State and persistence: per-CPU base state tracks active bases, next hard/soft timers, offsets, high-res mode, deferred rearm, hang counters, online state, and running callbacks. Debug objects track timer lifetime when enabled.

Dependencies and integration: depends on clockevents/tick, timekeeping offsets, scheduler/nohz housekeeping, PREEMPT_RT policy, timerfd notification, syscalls, freezer, CPU hotplug, and tracepoints.

Risks and test signals: high-risk areas are base migration, callback/cancel races, PREEMPT_RT soft callback waits, clock-set IPIs, deferred rearm, hang avoidance, low-res rounding, and CPU dying migration. Test with hrtimer selftests, nanosleep restart/remain paths, nohz/highres toggles, RT kernels, CPU hotplug, timerfd after clock_settime, and stress cancellation from callback/remote CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/hrtimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/itimer.c -->
# sources/distributed-fs/ceph-client/kernel/time/itimer.c

Purpose: implements legacy interval timer syscalls `getitimer`, `setitimer`, optional `alarm`, and compat variants for `ITIMER_REAL`, `ITIMER_VIRTUAL`, and `ITIMER_PROF`.

Important APIs and flow: `do_getitimer()` returns remaining real hrtimer time or process CPU timer state. `do_setitimer()` cancels/rearms the real hrtimer under `sighand->siglock`, or delegates CPU timers to `set_process_cpu_timer()`. `it_real_fn()` sends `SIGALRM` to the thread-group leader and deliberately does not restart; `posixtimer_rearm_itimer()` rearms periodic real timers from signal delivery to avoid tiny-period high-res DoS patterns. User ABI helpers convert old `itimerval`/compat timeval layouts into `itimerspec64`.

State and persistence: uses `current->signal->real_timer`, `it_real_incr`, and `signal->it[]` CPU timer fields. Old timer values can be returned atomically during set. SELinux builds expose `clear_itimer()` to zero all three timers.

Dependencies and integration: hrtimer core, process CPU timers, signal delivery, syscall/compat layers, uaccess, timer tracepoints, and architecture opt-in for `sys_alarm`.

Risks and test signals: races around concurrent real-timer expiry and cancellation are handled with retry and `hrtimer_cancel_wait_running()`. Tests should cover invalid `which`, timeval validation, NULL new-value legacy warning, compat ABI, real timer signal delivery/rearm, CPU virtual/prof accounting, old-value return, and second rounding in `alarm()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/itimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/jiffies.c -->
# sources/distributed-fs/ceph-client/kernel/time/jiffies.c

Purpose: provides the baseline jiffies clocksource, 64-bit jiffies accessor on 32-bit systems, optional refined-jiffies registration, and sysctl conversion handlers between user units and kernel jiffies.

Important APIs and flow: `clocksource_jiffies` reads global `jiffies`, has minimal rating, coarse `TICK_NSEC` conversion, and registers at `core_initcall`. `clocksource_default_clock()` weakly returns it as the fallback default. `register_refined_jiffies()` clones and slightly increases the rating after computing a more accurate multiplier from cycles-per-second. Sysctl helpers route `proc_dointvec_*_jiffies` and `proc_doulongvec_ms_jiffies_minmax()` through generic proc conversion callbacks.

State and persistence: exports `jiffies`, `jiffies_lock`, and `jiffies_seq`. On 32-bit, `get_jiffies_64()` reads `jiffies_64` with seqcount retry. Registered clocksources persist globally for timekeeping selection.

Dependencies and integration: clocksource core, timekeeping/tick internals, proc sysctl, jiffies conversion helpers, and initcall ordering. It is intentionally the lowest common denominator for platforms without better counters.

Risks and test signals: risks are coarse resolution, lost tick inaccuracy, poor tickless suitability, and unit conversion overflow/minmax behavior. Test by forcing fallback clocksource, validating 32-bit seqcount read consistency, refined-jiffies multiplier calculation, sysctl read/write conversions in seconds/USER_HZ/milliseconds, and no-proc-sysctl `-ENOSYS` stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/jiffies.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/namespace.c -->
# sources/distributed-fs/ceph-client/kernel/time/namespace.c

Purpose: implements time namespace creation, installation, fork commit, lifetime management, `/proc` namespace operations, and monotonic/boottime offset read/write support.

Important APIs and flow: `do_timens_ktime_to_host()` subtracts namespace offsets from absolute monotonic/boottime deadlines while clamping already-expired or overflowed values. `copy_time_ns()` either references the old namespace or clones a new `time_namespace`, charging user counts and allocating VDSO state. `timens_install()` requires a single-threaded caller plus `CAP_SYS_ADMIN` in both relevant user namespaces. `timens_on_fork()` switches a child from `time_ns_for_children` to active `time_ns` and commits VDSO layout. Proc offset setting validates clock ids, `CAP_SYS_TIME`, range against current host time, and refuses changes after offsets are frozen.

State and persistence: each namespace stores offsets, owner user namespace, ucounts, frozen flag, ns_common refcounting, and optional VVAR page. `timens_offset_lock` serializes offset writers and VDSO freezing. `init_time_ns` is frozen and registered at boot.

Dependencies and integration: user namespaces, nsproxy, proc ns operations, namespace tree, credentials/capabilities, timekeeping accessors, VDSO helpers, RCU freeing, and proc task files.

Risks and test signals: key risks are offset range validation, post-freeze mutation denial, namespace install permission rules, user-count exhaustion, and fork-time VDSO commitment. Test unshare/setns paths, `/proc/$pid/timens_offsets` writes, nested user namespaces, absolute sleeps under offsets, and remote task exit races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/namespace_internal.h -->
# sources/distributed-fs/ceph-client/kernel/time/namespace_internal.h

Purpose: private bridge between time namespace core and VDSO implementation. It declares `timens_offset_lock` and the VVAR page allocation/free hooks used by namespace cloning and teardown.

Important APIs and types: forward-declares `struct time_namespace`; exports `timens_offset_lock` for offset/VDSO freeze serialization; declares `timens_vdso_alloc_vvar_page()` and `timens_vdso_free_vvar_page()` when `CONFIG_TIME_NS_VDSO` is enabled. When VDSO support is disabled, inline stubs make allocation a no-op success and freeing a no-op.

State and persistence: this header owns no storage beyond the external mutex declaration. Its conditional stubs define whether a time namespace has per-namespace VVAR page lifecycle behavior.

Dependencies and integration: included by `namespace.c` and `namespace_vdso.c`; depends only on mutex definitions and time namespace type visibility. It separates generic namespace lifetime logic from architecture/config-dependent VDSO mapping support.

Risks and test signals: risks are mostly configuration skew: namespace clone/free must behave identically when VDSO support is compiled out. Build-test both `CONFIG_TIME_NS_VDSO=y` and `n`, verify no duplicate definitions, and exercise clone failure unwinding when VVAR allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/namespace_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/namespace_vdso.c -->
# sources/distributed-fs/ceph-client/kernel/time/namespace_vdso.c

Purpose: supports time namespace VDSO data by allocating a per-namespace VVAR page, freezing namespace offsets into VDSO clock data, and zapping VVAR mappings when a task joins a namespace.

Important APIs and flow: `timens_setup_vdso_clock_data()` writes `VDSO_CLOCKMODE_TIMENS` and namespace offsets for monotonic, raw/coarse monotonic, boottime, and boottime alarm clocks. `find_timens_vvar_page()` returns the current task namespace page and warns on remote VVAR access. `timens_set_vvar_page()` freezes offsets once per non-init namespace under `timens_offset_lock`, including auxiliary clock data when configured. `timens_commit()` sets the page then calls `vdso_join_timens()`, which scans VMAs and zaps the VVAR special mapping so faults rebuild with the namespace-specific layout.

State and persistence: `ns->vvar_page` is allocated zeroed at clone time and freed at namespace teardown. `ns->frozen_offsets` permanently prevents later proc offset writes once a task enters the namespace and VDSO data is materialized.

Dependencies and integration: VDSO datastore/page layout, special VVAR mapping, mm VMA iteration, mmap read lock, time namespace offsets, and optional POSIX auxiliary clock data.

Risks and test signals: risks include stale VVAR mappings after setns/fork, remote access warnings, offset freeze races, and missing auxiliary clock offsets. Test namespace entry after offset writes, rejected writes after first task commit, VDSO clock_gettime results versus syscall paths, and VMA zapping across processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/namespace_vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/ntp.c -->
# sources/distributed-fs/ceph-client/kernel/time/ntp.c

Purpose: implements kernel NTP state discipline: tick length adjustment, PLL/FLL phase/frequency control, leap-second state, `adjtimex` state import/export, optional PPS discipline, and optional synchronized RTC/CMOS updates.

Important APIs and flow: `ntp_data` stores per-timekeeper discipline fields. `ntp_update_frequency()` folds tick, frequency, and boot adjustment into scaled tick length. `ntp_update_offset()` clamps phase offset, computes PLL/FLL frequency adjustment, and sets residual offset. `second_overflow()` advances leap-second state, maxerror, phase chunking, PPS validity, and `adjtime()` tick adjustments once per second. `ntp_adjtimex()` processes modes such as status, nano/micro, frequency, errors, time constant, TAI, offset, and tick, emits audit changes, and fills return timex fields. PPS paths normalize timestamps, update frequency intervals/stability, reject jitter/wander, and optionally drive clock phase/frequency. CMOS sync uses an hrtimer plus workqueue to write persistent clock or RTC near the desired second edge.

State and persistence: `tk_ntp_data[]` persists per timekeeper. Hardware sync has static offset state plus `sync_hrtimer` and work item. Boot parameter `ntp_tick_adj=` modifies core tick adjustment.

Dependencies and integration: timekeeping internals, audit, hrtimer/workqueue, RTC class or legacy persistent clock, jiffies tick constants, PPS config, timex ABI, and leap-second consumers.

Risks and test signals: risks include scaled math overflow/clamping, leap second boundaries, PPS false rejection, unsynchronized status propagation, RTC phase-window retries, and multi-timekeeper indexing. Test with `adjtimex`, leap insert/delete simulations, PPS hardpps input, `STA_UNSYNC` transitions, RTC sync retry/offset changes, and boot tick adjustment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/ntp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/ntp_internal.h -->
# sources/distributed-fs/ceph-client/kernel/time/ntp_internal.h

Purpose: private internal interface between timekeeping code and the NTP discipline implementation.

Important APIs: declares initialization and reset (`ntp_init()`, `ntp_clear()`), scaled tick query (`ntp_tick_length()`), leap query (`ntp_get_next_leap()`), per-second update (`second_overflow()`), `adjtimex` processing (`ntp_adjtimex()`), PPS discipline (`__hardpps()`), and conditional CMOS/RTC notification (`ntp_notify_cmos_timer()`).

State and persistence: no direct storage. It defines compile-time behavior for callers when hardware clock synchronization is unavailable by providing an inline no-op `ntp_notify_cmos_timer()`.

Dependencies and integration: included by NTP/timekeeping internals; relies on `ktime_t`, `time64_t`, `__kernel_timex`, `timespec64`, and audit NTP data types supplied by including context. It keeps these APIs out of public kernel headers.

Risks and test signals: risks are ABI drift between declarations and `ntp.c`, and configuration drift around CMOS/RTC sync. Build-test with and without `CONFIG_GENERIC_CMOS_UPDATE`/`CONFIG_RTC_SYSTOHC`, and verify timekeeping callers can link all declared functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/ntp_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/posix-clock.c -->
# sources/distributed-fs/ceph-client/kernel/time/posix-clock.c

Purpose: implements dynamic POSIX clock devices, allowing character devices such as PTP hardware clocks to provide file operations and `clock_gettime/settime/adjtime/getres` through encoded file-descriptor clock ids.

Important APIs and flow: `posix_clock_register()` initializes the rwsem and cdev, registers the device, and binds ownership/dev pointers. `posix_clock_unregister()` removes the cdev/device, marks the clock zombie under write lock, and drops the device reference. File operations open a per-file `posix_clock_context`, call optional driver ops for read/poll/ioctl/release, and guard operations with `get_posix_clock()` so stale zombie clocks return `-ENODEV`. Dynamic clock callbacks decode fd clock ids with `clockid_to_fd()`, validate the file is a posix clock, hold the file and rwsem, enforce write mode for set/adjust, and call driver clock ops.

State and persistence: each `posix_clock` owns a cdev, rwsem, zombie flag, device pointer, and driver ops. Each open file owns `posix_clock_context` and a device reference until release.

Dependencies and integration: cdev/device core, file descriptor references, POSIX timer `k_clock` dispatch, uaccess, driver-provided posix clock ops, and module ownership.

Risks and test signals: risks include use-after-unregister, missing private data, stale fd clock ids, write permission bypass, and driver op absence. Test register/open/read/poll/ioctl/release, unregister while fds remain open, clock id operations on invalid fds, read-only set/adj denial, strict timespec validation, and missing-op `-EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/time/posix-clock.c -->
