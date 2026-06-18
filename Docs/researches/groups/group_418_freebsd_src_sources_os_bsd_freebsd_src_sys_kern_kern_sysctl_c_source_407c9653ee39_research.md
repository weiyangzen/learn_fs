# Group Research: group_418_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_kern_sysctl_c_source_407c9653ee39

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_sysctl.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_sysctl.c

Read status: complete file reviewed.

This file implements FreeBSD's kernel `sysctl(9)` MIB tree: OID registration, dynamic sysctl contexts, name/OID lookup, request dispatch, typed value handlers, kernel/user copy plumbing, tunable loading, VNET tunable refresh, and optional DDB inspection.

Core state is the root `sysctl__children` red-black tree plus per-OID child trees. `sysctllock` is a sleepable rmlock protecting the MIB and dynamic contexts, `sysctlmemlock` serializes large unprivileged user buffers, and `sysctlstringlock` protects writable string nodes. Dynamic OID memory comes from `M_SYSCTLOID`, request scratch from `M_SYSCTL`/`M_SYSCTLTMP`.

Registration paths include `sysctl_register_oid`, `sysctl_register_disabled_oid`, `sysctl_enable_oid`, `sysctl_unregister_oid`, `sysctl_add_oid`, `sysctl_remove_oid`, `sysctl_remove_name`, `sysctl_rename_oid`, `sysctl_move_oid`, and context helpers. Auto-numbered OIDs are assigned while preserving numeric order; duplicate named nodes increment refcounts, while leaf reuse is warned. Dynamic removal waits for running handlers via `oid_running` and `CTLFLAG_DYING`.

Tunable support builds dotted paths from OID parents and fetches loader/kernel environment values for numeric and string CTLTYPEs. VNET builds add `setenv`/`unsetenv` event handlers that refresh or restore per-vnet tunables when CTLFLAG_VNET tunables change.

The internal `CTL_SYSCTL` "staff" interface implements tree walking and metadata queries: debug dump, numeric-to-name, next/nextnoskip traversal, name-to-OID, format, description, and label. `name2oid` resolves dotted names under the lock and respects node handlers as terminal nodes.

`sysctl_root` is the central dispatcher. It resolves the OID, rejects writes to read-only nodes, enforces Capsicum `CTLFLAG_CAPRD/CAPWR`, securelevel, jail/VNET/write privileges, optional MAC checks, VNET arg rebasing, and handler Giant requirements before dropping the tree lock around the handler. Dynamic handler execution increments `oid_running` so unload/removal can wait safely.

The generic handlers cover bool, 8/16/32/int/long/64-bit integers, strings, opaque structs, and unit-conversion helpers for milliseconds-to-ticks, micro/milliseconds-to-sbintime, and seconds-to-timeval. String handling snapshots writable strings under `sysctlstringlock`; opaque handling retries copies if the thread generation changes during output.

Request plumbing includes `kernel_sysctl`, `kernel_sysctlbyname`, `userland_sysctl`, `sys___sysctl`, and `sys___sysctlbyname`. User requests use copyin/copyout functions, optional page wiring via `sysctl_wire_old_buffer`, KTRACE logging, CURVNET scoping, and EAGAIN retry/yield loops. Kernel requests use direct bcopy transfer functions.

With DDB enabled, the file adds a `show sysctl` debugger command that resolves named OIDs, walks subtrees, invokes safe handlers with debugger-specific output functions, supports name/value/opaque/hex modifiers, and skips unsafe handlers while recursing.

Risk areas are lock transitions around handler invocation, dynamic OID removal while modules unload, exact `oldidx/newidx` accounting across kernel/user copy paths, string updates under concurrent readers, VNET tunable restore ordering, and metadata leakage through capability-mode tree-walk interfaces.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_tc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_tc.c

Read status: complete file reviewed.

This file implements FreeBSD's timecounter/timehands core: lockless time reads, timecounter registration and selection, boot time tracking, clock stepping, NTP windup, optional feed-forward clocks, PPS timestamping, CPU tick calibration, and VDSO timehand export.

The main feedback-clock state is `struct timehands`, a ring of cached counter-derived times guarded by generation numbers. `timehands` points to the active entry, `timecounter` points to selected hardware, and `timecounters` is the registered list protected by `tc_lock`. Early boot uses a dummy timecounter so time APIs work before hardware counters register.

Read APIs such as `binuptime`, `nanouptime`, `microtime`, `getnanotime`, and `getboottimebin` snapshot a timehand, read a counter delta with `tc_delta`, and retry if the generation changed. The `get*` variants use cached tick values, while precise variants add current counter deltas. DTrace-specific clones avoid FBT probe recursion.

`tc_init` validates new counters, creates per-counter sysctl nodes, inserts them into the global list, and automatically selects the best nonnegative-quality counter unless a user/tunable choice is active. Sysctls expose `kern.boottime`, available choices, selected hardware, tick/deviation precision, step warnings, timehand count, and fast VDSO gettime enablement.

`tc_setclock` steps wall time by recalculating boot time, winding up timehands under `tc_setclock_mtx`, bumping `rtc_generation`, notifying timerfd, waking sleeps tied to old realtime, and optionally logging the step. `tc_windup` advances the next timehand, processes NTP seconds/leap adjustments, recalculates scaling, switches counters when requested, updates `time_second/time_uptime`, and pushes VDSO state.

When `FFCLOCK` is enabled, the file maintains a separate feed-forward timehands ring (`fftimehands`) with daemon-supplied estimates, interpolation periods, boot time, and status. It implements reset, delta conversion, windup, counter-change handling, last-tick snapshots, absolute/difference conversion, raw counter reads, and `sysclock_getsnapshot`/`sysclock_snap2bintime` integration for comparing feedback and feed-forward clocks.

The PPS section implements RFC 2783 support: `pps_ioctl`, `pps_init`, `pps_init_abi`, `pps_capture`, and `pps_event`. It supports parameter/capability/fetch ioctls, optional feed-forward counter fetches, optional hardpps binding, sleeping fetches, ABI-aware driver locking, assert/clear timestamp capture, offsets, sequence counters, and wakeups.

Periodic maintenance is driven by `tc_ticktock`, which calls `tc_windup` every `tc_tick` hardclock ticks. Initialization sets tick thresholds and timehand ring length. CPU tick support provides a fallback `cpu_ticks` based on the active timecounter, calibrates variable CPU tick rates, and converts ticks to microseconds.

VDSO support fills native and 32-bit `vdso_timehands` with scale, offset count, counter mask, uptime, boot time, and counter-specific data when enabled. DDB support can print the active counter and timehand fields.

Risk areas are generation/fence correctness in lockless readers, overflow in counter-delta scaling, timecounter switch discontinuities, NTP/leap-second update ordering, realtime step wakeups via `rtc_generation`, feed-forward daemon estimate races, PPS capture when counters change, and unsynchronized VDSO publication.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_tc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_thr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_thr.c

Read status: complete file reviewed.

This file implements the FreeBSD user-visible thread/LWP syscall layer: creating user threads, exiting threads, per-thread signaling, suspend/wake primitives, thread naming, and per-process thread allocation limits.

Sysctls under `kern.threads` expose `max_threads_per_proc` and `max_threads_hits`. `kern_thr_alloc` enforces the per-process thread cap before calling the lower-level allocator from `kern_thread.c`.

Thread creation is exposed through `sys_thr_create`, `sys_thr_new`, `kern_thr_new`, and `thread_create`. `thr_create` copies in a full `ucontext_t`, writes the child TID if requested, and installs the machine context. `thr_new` copies `struct thr_param`, validates flags, optionally copies realtime priority parameters, KTRACE-logs the parameter, writes child/parent TIDs, sets the user upcall stack/start function/argument, and installs TLS.

`thread_create` performs the shared creation path. It validates realtime scheduling privilege and priority, charges RACCT `RACCT_NTHR`, allocates a new thread, copies selected thread state from the caller, shares COW credentials/limits, copies machine thread state, invokes the caller-provided initializer, links the thread into the process, marks `P_HADTHREADS`, names it from `p_comm`, calls scheduler fork hooks, handles process stop/ptrace birth flags, invokes PMC/HWT hooks, inserts the TID hash entry, applies realtime priority if requested, and schedules it runnable. Failure paths unwind COW state, thread memory, and RACCT charge.

Exit paths include `sys_thr_exit` and `kern_thr_exit`. The syscall notifies umtx state, optionally stores a user wake flag and wakes waiters, then enters kernel thread exit. `kern_thr_exit` clears kernel ASTs, detects the last live/pending-exit thread and returns so userland trampoline can terminate the whole process, calls ABI thread-exit hooks, reports ptrace LWP exit if needed, removes the thread from the TID hash, subtracts RACCT thread count, cleans pending signals, audits syscall exit, marks the process stopped, and calls `thread_exit`.

Signal syscalls include `sys_thr_kill` for current-process TIDs and `sys_thr_kill2` for arbitrary process/TID pairs. They construct SI_LWP ksiginfo, validate signals, use `tdfind`/`pfind`, enforce `p_cansignal` for cross-process signaling, support signal 0 existence checks, and can broadcast to all other threads when id is -1.

Suspend/wake APIs implement libthr blocking. `kern_thr_suspend` handles optional relative timeout, pending wake flags, `msleep` on the thread under the proc lock, and maps timeout/restart results. `sys_thr_wake` either records a self-wakeup flag or locates another thread, sets `TDF_THRWAKEUP`, and wakes it.

`sys_thr_set_name` copies a bounded user string, locates the target thread, updates `td_name`, clears scheduler cached names for KTR, and invokes PMC/HWT hooks for logging.

Risk areas are races between quick child exit and parent TID storage, last-thread detection with `p_pendingexits`, ptrace stop/drop-lock windows during thread exit, RACCT charge unwinding, signal permission checks around changing process state, and suspend/wake lost wakeups across `TDP_WAKEUP` and `TDF_THRWAKEUP`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_thr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_thread.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_thread.c

Read status: complete file reviewed.

This file implements FreeBSD's core thread lifecycle machinery: thread object allocation, TID allocation and lookup, process-thread linkage, zombie reaping, COW credential/limit handling, thread exit, process single-threading/suspension, and TID hash maintenance.

Global resources include the UMA `thread_zone`, per-memory-domain zombie lists, reap task/callout, `tid_lock` and `tid_bitmap`, TID hash tables with per-bucket rwlocks, `maxthread`, and atomic `nthreads`. Eventhandler lists support thread constructor/destructor/init/fini hooks. Architecture KBI asserts pin selected `struct thread` and `struct proc` offsets on amd64/i386.

Allocation starts with `thread_count_inc`, which opportunistically reaps zombie threads, enforces `kern.maxthread`, allows privileged reserve use near the limit, and rate-limits warnings. `tid_alloc` assigns IDs from a bitmap above `NO_PID`; batch helpers amortize freeing TIDs and decrementing thread counts during reaping.

UMA callbacks initialize and tear down type-stable thread fields: scheduler state, critical nesting, audit/DTrace/umtx state, sleepqueues, turnstiles, allocation domain, and eventhandler callbacks. `threadinit` initializes global locks/tables, reserves thread0/TID0, creates the zone and hash locks, starts the reap callout, and registers the suspend AST.

Exited threads are placed on per-domain lock-free zombie stacks by `thread_zombie`/`thread_stash`. `thread_reap_domain`, `thread_reap`, `thread_reap_all`, callout/task callbacks, and `thread_reap_barrier` drain dead threads, invoke destructors, batch-release TIDs/creds/limits/counts, free kernel stacks, drain sleep callouts, and return objects to UMA.

`thread_alloc`, `thread_recycle`, `thread_free`, and `thread_free_batched` allocate kernel stacks, sanitizer state, MD state, cpusets, lock profiling state, and callouts. COW helpers (`thread_cow_get_proc`, `thread_cow_get`, `thread_cow_free`, `thread_cow_update`, `thread_cow_synced`) manage per-thread credential and limit references against process generation counters.

Process linkage functions `proc_linkup0`, `proc_linkup`, `thread_link`, and `thread_unlink` initialize thread queues, signal queues, process ksi state, per-thread contested/profiling/epoch lists, sleep callouts, and `p_numthreads`.

`thread_exit` is the low-level irreversible exit path. It requires proc and scheduler locks, drops MD resources, unlinks non-last threads, updates exit-thread counts, calls scheduler exit hooks, wakes single-thread waiters when appropriate, notifies PMC/HWT, records runtime/rusage, marks the thread inactive, handles witness exit, and enters `sched_throw`. `thread_wait` cleans the last remaining thread during process reap.

Single-threading and suspension are handled by `thread_single`, `thread_suspend_check`, `thread_check_susp`, `thread_suspend_switch`, `thread_suspend_one`, `thread_unsuspend_one`, `thread_unsuspend`, `thread_run_flash`, and `thread_single_end`. They support exec/exit single-threading, boundary-only suspension, all-process stops, ptrace suspend requests, interruptible sleep aborts, AST scheduling, boundary counters, and wakeups when all other threads have stopped.

TID lookup uses `tdfind_hash` and `tdfind`: lookup first snapshots thread/proc under the TID hash lock, then locks and verifies the proc because thread exit establishes the opposite lock order. `tidhash_add` and `tidhash_remove` maintain hash membership.

Risk areas are TID reuse and lookup verification, zombie reaping synchronization with CPU deadthread handoff, lock ordering across proc locks, scheduler locks, TID hash locks, and sleepqueues, exact `p_suspcount/p_boundary_count` accounting, single-thread exit races, and ensuring COW credentials/limits are released exactly once.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_thread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_time.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_time.c

Read status: complete file reviewed.

This file implements FreeBSD's time-related syscall layer and timer services: clock get/set/resolution, nanosleep, gettimeofday/settimeofday, BSD interval timers, POSIX timers, CPU clocks, timer signal delivery, and timer cleanup for exec/exit.

Clock IDs are backed by `posix_clocks[MAX_CLOCKS]`; POSIX realtime timer support is registered at boot by `itimer_start`, which creates the `itimer` UMA zone, registers realtime-style handlers for CLOCK_REALTIME/MONOTONIC/UPTIME/TAI, and fills POSIX.1B sysctl capability values.

Clock read paths include `sys_clock_gettime`, `kern_clock_gettime`, `kern_clock_getcpuclockid2`, CPU-clock helpers, and `kern_clock_getres`. Realtime, monotonic, uptime, fast, precise, second, TAI, virtual/profiling, process CPU, thread CPU, and encoded per-process/per-thread CPU clock IDs are supported. CPU clocks derive from thread/process runtime and `cpu_tickrate`.

Clock set paths include `sys_clock_settime`, `kern_clock_settime`, `sys_settimeofday`, `kern_settimeofday`, and internal `settime`. They enforce `PRIV_CLOCK_SETTIME`/`PRIV_SETTIMEOFDAY`, validate ranges, optionally reject extreme dates, clamp steps under securelevel, call `tc_setclock`, and reset the time-of-day hardware via `resettodr`.

Sleep paths include `kern_nanosleep`, `kern_clock_nanosleep`, `sys_nanosleep`, and `sys_clock_nanosleep`. They validate clock/flags, support absolute and relative sleeps, choose precise or coarse sbintime deadlines, handle realtime jumps with `td_rtcgen`, chunk very large sleeps, return remaining time for interrupted relative sleeps, and map POSIX errors through `kern_posix_error`.

Legacy interval timers are handled by `kern_getitimer`, `kern_setitimer`, `realitexpire`, `itimerfix`, `itimerdecr`, and timeval helpers. `ITIMER_REAL` is stored as an absolute uptime deadline and scheduled with a callout; virtual/profiling timers live in `p_stats` and are decremented elsewhere. Periodic realtime expiry advances by intervals until future time to avoid drift and compresses missed signals into one SIGALRM.

Rate helpers `ratecheck` and `eventratecheck` provide timeval/tick based rate limiting. Basic `timevaladd`, `timevalsub`, and `timevalfix` normalize timeval arithmetic.

POSIX timer creation/deletion/set/get paths include `sys_ktimer_create`, `kern_ktimer_create`, `kern_ktimer_delete`, `kern_ktimer_settime`, `kern_ktimer_gettime`, `kern_ktimer_getoverrun`, and `itimer_find`. Timers validate sigevent modes/signals, allocate per-process timer arrays lazily, reserve IDs 0-2 for setitimer compatibility, store ksiginfo, protect timers with `it_mtx`, use `ITF_DELETING/ITF_WANTED` and usecounts to serialize deletion, and remove pending queued signals on delete.

Realtime POSIX timer backend functions (`realtimer_create`, `realtimer_delete`, `realtimer_gettime`, `realtimer_settime`, `realtimer_expire_l`) manage callouts, absolute deadlines, relative/absolute settime conversion, interval overrun accounting, stopped/killed process deferral with `ITF_PSTOPPED`, and rescheduling based on clock time.

`itimer_fire` delivers SIGEV_SIGNAL or SIGEV_THREAD_ID notifications through `tdsendsignal`, updates overrun counters if a previous signal is still queued, disables timers whose target thread cannot be found, and records ERANGE on overrun saturation. `itimer_accept` transfers overrun state when a queued timer signal is accepted.

Process lifecycle hooks `itimers_exec` and `itimers_exit` delete POSIX timers on exec/exit, preserving XSI interval timers across exec as required. `itimer_proc_continue` restarts deferred legacy and POSIX realtime timers when a stopped process resumes.

Risk areas are realtime clock jumps versus absolute sleeps/timers, deletion races with active callouts and signal delivery, timer overrun saturation, proc lock versus timer lock ordering, preserving setitimer timer IDs while sharing POSIX cleanup code, CPU-clock lookup lifetime, and stopped/killed process timer deferral/restart semantics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_time.c -->