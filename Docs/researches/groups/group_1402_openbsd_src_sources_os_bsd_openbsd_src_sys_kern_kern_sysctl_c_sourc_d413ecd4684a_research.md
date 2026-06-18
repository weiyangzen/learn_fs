# Group Research: group_1402_openbsd_src_sources_os_bsd_openbsd_src_sys_kern_kern_sysctl_c_sourc_d413ecd4684a

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/openbsd-src`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_sysctl.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_sysctl.c

Read completely: 3010 lines.

Implements OpenBSD's legacy numeric `sysctl(2)` dispatch and many kernel/hardware sysctl handlers. The file is the central router from user MIBs into `CTL_KERN`, `CTL_HW`, `CTL_NET`, `CTL_VM`, `CTL_VFS`, `CTL_MACHDEP`, optional debug/DDB trees, and numerous kernel information export helpers.

Core dispatch and locking:
- `sys_sysctl()` validates privilege for writes, copies in the MIB, applies `pledge_sysctl()`, selects the top-level handler, copies in/out `oldlenp`, and uses `sysctl_vslock()` for handlers that need the old buffer wired while the kernel lock is held.
- `sysctl_vslock()` and `sysctl_vsunlock()` serialize large user-buffer locking with `sysctl_lock`, check against `uvmexp.wiredmax`, call `uvm_vslock()`/`uvm_vsunlock()`, and bracket the operation with `KERNEL_LOCK()`.
- `kern_sysctl_dirs()` dispatches non-terminal `KERN_*` nodes, with some handlers avoiding the generic buffer wiring path and others going through `kern_sysctl_dirs_locked()`.
- `kern_sysctl()` handles terminal kernel variables, message buffers, mbuf stats, CPU time, pool debug, bounded integer variables, and falls back to `kern_sysctl_locked()` for entries requiring the global sysctl locking path.

Kernel and hardware variables:
- Stores mutable kernel attributes such as `hostname`, `domainname`, `hostid`, cached `disknames`, `diskstats`, and `securelevel`.
- `kern_vars[]` and `hw_vars[]` define bounded/read-only integer sysctls used by `sysctl_bounded_arr()`.
- `kern_sysctl_locked()` handles securelevel, hostname/domainname updates, name-cache/fork stats, stack-gap tuning, buffer cache percentage, PF status, console device, and UTC offset.
- `hw_sysctl()` reports machine/model, online CPU count, physical/user memory, firmware strings, UUID, sensors, disk information, CPU speed/performance policy, powerdown control, ucom names, CPU topology controls, and battery charge controls.

Sysctl helper API:
- Integer helpers include `sysctl_int_lower()`, `sysctl_int()`, `sysctl_rdint()`, `sysctl_securelevel()`, `sysctl_securelevel_int()`, `sysctl_int_bounded()`, `sysctl_bounded_arr()`, and `sysctl_rdquad()`.
- String helpers include writable `sysctl_string()`, truncating `sysctl_tstring()`, internal `sysctl__string()`, and read-only `sysctl_rdstring()`.
- Structure helpers include writable `sysctl_struct()` and read-only `sysctl_rdstruct()`.
- Write helpers commonly copy in before changing state, but several preserve historical behavior where a new value may be committed before a later copyout error is reported.

Process and file introspection:
- `fill_file()` builds `struct kinfo_file` records for vnodes, sockets, pipes, kqueues, process-owned file descriptors, cwd/root/text/trace vnodes, and network PCB/socket state. Kernel pointers are exposed only to privileged callers.
- `sysctl_file()` implements `KERN_FILE_BYFILE`, `KERN_FILE_BYPID`, and `KERN_FILE_BYUID`, walking file tables, process lists, vnode references, and inet PCB tables; it estimates needed output size and returns `ENOMEM` if the provided buffer is too small.
- `sysctl_doproc()` enumerates live and zombie processes for `KERN_PROC_*` queries, optionally including threads, using `fill_kproc()` for each result.
- `fill_kproc()` fills `struct kinfo_proc` from process/thread state, credentials, sessions, tty state, VM RSS, usage aggregates, start time converted through boot time, CPU id, `%cpu`, and synthesized process state.
- `sysctl_proc_args()` reads argv/env vectors from another process's user VM via `uvm_io()`, with system/exiting/execing checks and owner/root checks for environment access.
- `sysctl_proc_cwd()` returns another process's current working directory through `vfs_getcwd_common()`.
- `sysctl_proc_nobroadcastkill()` exposes and optionally changes `PS_NOBROADCASTKILL` for a process.
- `sysctl_proc_vmmap()` exposes chunks of a process or kernel address map as `struct kinfo_vmentry`, requiring root for non-self and kernel-map queries.

Device, disk, IPC, and sensor exports:
- `sysctl_diskinit()` maintains cached disk name and diskstats arrays under `sysctl_disklock`, rebuilding on disk topology changes and refreshing statistics on request.
- `sysctl_sysvipc()` exports SysV IPC info for msg/sem/shm depending on kernel options, with partial-buffer handling.
- `sysctl_sensors()` copies out sanitized sensor device or individual sensor records.
- `sysctl_cpustats()` and `sysctl_cptime2()` export per-CPU times through `sysctl_ci_cp_time()`, which uses per-CPU generation-protected counters.
- `sysctl_audio()` and `sysctl_video()` expose optional recording/control toggles.
- `sysctl_utc_offset()` stores timezone offset in minutes through `KERN_UTC_OFFSET`, then adjusts the realtime clock and writes the RTC.

Security and concurrency notes:
- Writes require `suser()` at syscall entry; individual handlers add securelevel, owner/root, or subsystem-specific restrictions.
- `securelevel` prevents lowering by non-init processes under restrictive conditions and makes some sysctls read-only above securelevel 0.
- Kernel pointer exposure in process/file sysctls is gated by privilege.
- The file mixes global kernel locking, rwlocks, mutexes, vnode/process references, PCB locks, and per-CPU counter generation loops; callers must respect the old numeric sysctl ABI and its buffer-size semantics.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_task.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_task.c

Read completely: 464 lines.

Implements OpenBSD kernel task queues: deferred work items serviced by one or more kernel threads. It defines the global queues `systq` and `systqmp`, dynamic queue creation/destruction, enqueue/delete operations, barriers, worker loops, and optional WITNESS/kcov integration.

Core structures and queues:
- `struct taskq` tracks lifecycle state, running worker count, configured thread count, queue flags, name, mutex, queued `struct task` list, worker thread list, barrier accounting, and WITNESS metadata.
- `taskq_sys` is the default kernel-locked task queue; `taskq_sys_mp` is the MP-safe queue with `TASKQ_MPSAFE`.
- Worker membership is recorded in `struct taskq_thread` so barriers can detect when the caller is already one of the queue's workers.

Lifecycle:
- `taskq_init()` initializes WITNESS state and defers creation of the global queue threads.
- `taskq_create()` allocates and initializes a new queue, then schedules `taskq_create_thread()` so at least one worker exists.
- `taskq_create_thread()` transitions a queue from created to running, creates the configured number of kthreads, and handles the race where a queue is destroyed before its deferred creation runs.
- `taskq_destroy()` marks a queue destroyed, wakes workers, waits for `tq_running` to reach zero, and frees dynamic queues.

Work and barriers:
- `task_set()` initializes a task function, argument, and flags.
- `task_add()` enqueues a task once, sets `TASK_ONQUEUE`, optionally records kcov remote process context, and wakes one worker.
- `task_del()` removes a pending task if still queued.
- `taskq_next_work()` sleeps until work is available or the queue stops, removes the head task, clears `TASK_ONQUEUE`, copies it by value to avoid races with caller-owned task storage, and wakes another worker if more work is queued.
- `taskq_barrier()` and `taskq_del_barrier()` wait until all queue workers have passed through a barrier point; `taskq_do_barrier()` injects barrier tasks and coordinates barrier generations.

Execution model:
- `taskq_thread()` optionally drops the kernel lock for MP-safe queues, registers itself in the queue's thread list, repeatedly runs copied tasks under WITNESS/kcov hooks, calls `sched_pause(yield)` after each task, and exits when the queue is destroyed.
- Barriers are careful about callers already running inside the same taskq, counting that thread directly rather than deadlocking behind its own barrier task.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_task.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_tc.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_tc.c

Read completely: 986 lines.

Implements the kernel timecounter framework and `timehands` fast timekeeping data. It provides boot/realtime/uptime/runtime accessors, timecounter registration and selection, realtime and monotonic clock stepping, NTP/adjtime/frequency adjustments, userland timekeep export, and `KERN_TIMECOUNTER` sysctls.

Core state:
- A dummy timecounter provides early boot time service until real hardware registers.
- Two `struct timehands` instances form a generation-stamped ring. Readers copy from `timehands` and retry if `th_generation` changes or is zero.
- `tc_lock` protects timecounter adjustments and explicit realtime changes; `windup_mtx` protects `tc_windup()` updates.
- `timecounter` points to the selected hardware counter; `tc_list` contains registered counters.
- `time_second`, `time_uptime`, and `naptime` are volatile cached values updated from `tc_windup()`.

Time read APIs:
- Boot-time accessors: `binboottime()`, `microboottime()`, `nanoboottime()`.
- Uptime accessors: `binuptime()`, `getbinuptime()`, `nanouptime()`, `microuptime()`, `getuptime()`, `nsecuptime()`, `getnsecuptime()`.
- Runtime excluding suspend/nap time: `binruntime()`, `nanoruntime()`, `getbinruntime()`, `getnsecruntime()`.
- Realtime accessors: `bintime()`, `nanotime()`, `microtime()`, `gettime()`, `getnanotime()`, `getmicrotime()`.
- Cached uptime conversions: `getnanouptime()` and `getmicrouptime()`.

Counter selection and updates:
- `tc_init()` computes precision, rejects counters needing too-frequent polling for current `hz`, inserts the counter, and auto-selects non-negative high-quality counters.
- `tc_reset_quality()` changes a counter's quality and falls back to the best remaining counter if the active counter degrades.
- `tc_getfrequency()` and `tc_getprecision()` report active counter properties.
- `inittimecounter()` sets the periodic windup tick interval and warms up the selected counter.
- `tc_ticktock()` periodically calls `tc_windup()` to prevent counter wrap and refresh cached time.

Clock setting and windup:
- `tc_setrealtimeclock()` steps UTC by recomputing boot time from requested realtime minus uptime, clears adjtime state, updates timehands, optionally logs the step, and mixes time into randomness.
- `tc_setclock()` steps the monotonic/realtime notion used after boot, advances `naptime` when needed, and calls `timeout_adjust_ticks()` so tick-based timeouts are not skipped after a forward jump.
- `tc_windup()` is the central update routine: copies current timehands, applies counter deltas, handles monotonic offset changes, boot-time changes, adjtime changes, NTP second processing, cached realtime conversion, counter switches, scale recalculation including frequency adjustment, generation publishing, timekeep export, and global cached seconds.
- `tc_update_timekeep()` publishes selected timekeeping fields to the shared `timekeep` area with producer memory barriers.

Adjustment and sysctl:
- `ntp_update_second()` consumes `th_adjtimedelta` in bounded per-second chunks and converts it into the counter scale adjustment.
- `tc_adjfreq()` gets or sets hardware counter frequency adjustment under `tc_lock`, forcing a windup on writes.
- `tc_adjtime()` gets or sets remaining adjtime delta using generation-stamped reads and windup writes.
- `sysctl_tc_hardware()` reads or switches the active timecounter by name.
- `sysctl_tc_choice()` returns available counters with qualities.
- `sysctl_tc()` exposes hardware, choice, tick interval, and timestep warning controls under `KERN_TIMECOUNTER`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_tc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_time.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_time.c

Read completely: 1038 lines.

Implements public time syscalls, realtime clock setting policy, nanosleep, `gettimeofday`/`settimeofday`, `adjtime`/`adjfreq`, BSD interval timers, rate limiting helpers, RTC initialization/update, and periodic RTC resynchronization.

Time syscalls:
- `settime()` validates against near-wrap future times and securelevel clock rollback restrictions, calls `tc_setrealtimeclock()`, and writes the RTC through `resettodr()`.
- `clock_gettime()` supports realtime, uptime/runtime, monotonic/boottime, process CPU time, current thread CPU time, and encoded thread CPU clocks from `pthread_getcpuclockid()`.
- `sys_clock_gettime()` copies out a `timespec` and emits ktrace structure records.
- `sys_clock_settime()` allows root to set only `CLOCK_REALTIME` after validating the requested `timespec`.
- `sys_clock_getres()` derives hardware clock resolution from timecounter frequency/precision and CPU clock resolution from `stathz`.
- `sys_nanosleep()` sleeps in bounded chunks against uptime, recomputes elapsed time after wakeups, converts restart to interrupt, and optionally copies out the remainder.
- `sys_gettimeofday()` and `sys_settimeofday()` provide legacy timeval/timezone interfaces; timezone input is validated but not used to alter kernel timezone state here.

Clock adjustment:
- `sys_adjfreq()` optionally requires root, validates the fixed-point frequency adjustment range, uses `tc_lock` read/write mode, and delegates to `tc_adjfreq()`.
- `sys_adjtime()` applies `pledge_adjtime()`, requires root for new deltas, validates timeval arithmetic against `int64_t` overflow, reports old remaining delta, and delegates to `tc_adjtime()`.

Interval timers:
- `setitimer()` gets or sets `ITIMER_REAL`, `ITIMER_VIRTUAL`, and `ITIMER_PROF`. Real timers are stored as absolute uptime deadlines and use `ps_realit_to`; virtual/prof timers are stored as remaining intervals under `itimer_mtx`.
- `cancel_all_itimers()` clears all per-process interval timers.
- `sys_getitimer()` and `sys_setitimer()` implement the system calls with validation, ktrace, and optional old-value return.
- `realitexpire()` sends `SIGALRM`, clears one-shot timers, and advances periodic real timers to the next future absolute deadline to avoid drift.
- `itimerfix()` validates user `itimerval` input, bounds it below the historical maximum, clears intervals for disabled timers, and rounds small nonzero intervals up to at least one tick.
- `itimerdecr()` decrements virtual/profiling timers and reloads periodic timers while preserving overrun.
- `itimer_update()` runs from hardclock context, decrements virtual/prof timers based on elapsed hardclock periods, and marks `P_ALRMPEND`/`P_PROFPEND`.
- `process_reset_itimer_flag()` maintains `PS_ITIMER` based on whether virtual/prof timers are active.

Rate limiting:
- `ratecheck()` implements timeval-based minimum interval checks under `ratecheck_mtx`.
- `ppsratecheck()` implements per-second event limiting, including unlimited negative `maxpps`, disabled zero `maxpps`, and wrap-safe packet count increments.

RTC and periodic sync:
- `inittodr()` initializes system time from filesystem base time and the best attached TODR chip, warns on implausible filesystem or chip time, and calls `tc_setclock()`.
- `resettodr()` writes current realtime to the TODR chip only after `inittodr()` has run.
- `todr_attach()` selects the highest-quality TODR provider.
- `periodic_resettodr()`, `perform_resettodr()`, `start_periodic_resettodr()`, and `stop_periodic_resettodr()` use `systq` plus a timeout to periodically update the RTC every 1800 seconds.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_timeout.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_timeout.c

Read completely: 1053 lines.

Implements OpenBSD's timeout/callout subsystem using hierarchical timing wheels, a softclock interrupt, process-context timeout threads, MP-safe timeout handling, barriers, timeout statistics, and DDB inspection support.

Core state:
- `timeout_mutex` protects global timeout queues and statistics.
- Tick-based timeouts use `timeout_wheel[4 * 256]`; absolute uptime timeouts use `timeout_wheel_kc[4 * 256]`.
- `timeout_new` holds newly added or moved timeouts; `timeout_todo` holds softclock-due work; `timeout_proc` and optional `timeout_proc_mp` hold work requiring process context.
- `timeout_ctx_si`, `timeout_ctx_proc`, and optional `timeout_ctx_proc_mp` track each execution context's todo queue and currently running timeout for barrier synchronization.
- `timeout_kclock[]` caches per-kclock last scan, late threshold, and offset; this file currently handles `KCLOCK_UPTIME` absolute timeouts.

Initialization:
- `timeout_startup()` initializes all circular queues, computes wheel level widths, and stores tick duration as `tick_ts`.
- `timeout_proc_init()` establishes the softclock interrupt, initializes WITNESS lock objects, and defers softclock kthread creation.
- `softclock_create_thread()` creates the process-context softclock thread and, on multiprocessor kernels, an MP-safe softclock thread.

Timeout setup and scheduling:
- `timeout_set()`, `timeout_set_proc()`, and `timeout_set_flags()` initialize timeout callbacks, arguments, clock type, and flags; MP-safe is restricted to process-context timeouts.
- `timeout_add()` schedules tick-based timeouts at `ticks + to_ticks`, handles re-adds by rescheduling only when the new deadline is earlier, records kcov process context, and updates statistics.
- `timeout_add_sec()`, `timeout_add_msec()`, `timeout_add_usec()`, and `timeout_add_nsec()` convert wall durations to ticks with rounding-up semantics and overflow saturation.
- `timeout_abs_ts()` schedules `KCLOCK_UPTIME` absolute deadlines and reschedules earlier deadlines immediately.
- `timeout_del()` removes pending timeouts, clears triggered state, and updates cancellation/deletion stats.
- `timeout_del_barrier()` combines deletion with a completion barrier.

Barrier and execution:
- `timeout_barrier()` waits for an in-flight timeout to finish by injecting a same-context barrier timeout that signals a condition variable after the running callback completes.
- `timeout_run()` removes queue state, marks the timeout triggered, records the running timeout in its context, drops `timeout_mutex`, runs the callback under WITNESS/kcov hooks, then reacquires the mutex and clears `tctx_running`.

Wheel processing:
- `timeout_bucket()` chooses an absolute-time wheel bucket by comparing the deadline with the kclock's `kc_lastscan`.
- `timeout_maskwheel()` hashes seconds and nanoseconds into the requested 8-bit wheel level.
- `timeout_hardclock_update()` runs on the primary CPU each hardclock tick, moves expired tick and kclock buckets to `timeout_todo`, updates kclock cached scan/late values from `nanouptime()`, and schedules the softclock interrupt if work exists.
- `softclock()` drains `timeout_new` and `timeout_todo`, reschedules future entries into the appropriate wheel, runs softclock-context callbacks immediately, and wakes process-context workers when needed.
- `softclock_process_tick_timeout()` and `softclock_process_kclock_timeout()` decide whether a timeout is future, late, process-context, MP-safe process-context, or ready to run in softclock.
- `softclock_thread_run()` loops forever sleeping on its process-context queue and running queued timeout callbacks.
- `softclock_thread()` pins the conservative process-context thread to the primary CPU and runs at softclock IPL; `softclock_thread_mp()` drops the kernel lock and runs MP-safe callbacks.

Adjustment and diagnostics:
- `timeout_adjust_ticks()` moves pending tick-based timeouts forward after monotonic clock advances so elapsed time is not skipped.
- `timeout_sysctl()` snapshots `struct timeoutstat` for `KERN_TIMEOUT_STATS`.
- DDB helpers `db_show_callout()`, `db_show_callout_bucket()`, and `db_show_timeout()` print pending timeouts, remaining time, clock type, wheel location, callback argument, and symbol name.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_timeout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_unveil.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_unveil.c

Read completely: 829 lines.

Implements the kernel side of OpenBSD `unveil(2)`: per-process pathname access restrictions tied to directory vnodes plus optional terminal component names. It manages unveil state across add, lookup, fork copy, process destroy, vnode removal, and namei enforcement.

Data model:
- `struct unveil` binds a directory vnode to either directory-wide permission flags or a red-black tree of named terminal children, plus a cover index and rwlock.
- `struct unvname` stores a terminal component name, its length, permission flags, and RBT linkage.
- Limits are fixed at `UNVEIL_MAX_VNODES` and `UNVEIL_MAX_NAMES`, both 128 per process.
- `vnode.v_uvcount` counts unveil references across processes and allows fast skip when no process has unveiled a vnode.

Name tree and lifecycle:
- `unvname_compare()`, `unvname_new()`, and `unvname_delete()` manage RBT keys by NUL-terminated component name and length.
- `unveil_add_name_unlocked()`, `unveil_add_name()`, and `unveil_namelookup()` insert and find terminal names under an unveiled directory.
- `unveil_delete_names()` removes all terminal names for an unveil entry under its lock.
- `unveil_destroy()` releases all vnode references, decrements `v_uvcount`, deletes names, frees the per-process array, and clears process counters.
- `unveil_copy()` duplicates parent unveil state into a child process, taking vnode references and copying every terminal name and flag.

Adding unveils:
- `unveil_parsepermissions()` translates `r`, `w`, `x`, and `c` permission strings into `UNVEIL_*` flags plus `UNVEIL_USERSET`.
- `unveil_add()` receives a resolved `nameidata`, allocates the process unveil array on first use, enforces vnode/name limits, chooses the directory vnode for either directory or terminal-component entries, references it, and updates existing or new unveil entries.
- Directory adds make the directory unrestricted by terminal-name filtering and replace `uv_flags`.
- Terminal adds create or update an `unvname` under the containing directory and increment the process name count only for new names.
- `unveil_add_vnode()` allocates the next process slot, initializes its lock/name tree, stores the directory vnode, computes its covering unveil, and refreshes any entries covered by the same ancestor.

Cover and lookup:
- `unveil_find_cover()` walks upward from a vnode toward the process root or `rootvnode`, crossing mount roots through `mnt_vnodecovered`, and returns the nearest covering unveil slot.
- `unveil_lookup()` finds a process unveil entry for a vnode, using `v_uvcount == 0` as a fast negative check.
- `unveil_covered()` moves a match upward to its cover when path lookup traverses `..`.
- `unveil_start_relative()` initializes `ni_unveil_match` for relative lookups, either from the starting vnode or by walking up to a cover.
- `unveil_check_component()` updates the current unveil match while namei traverses intermediate directories, handling `..` specially.

Final enforcement:
- `unveil_check_final()` runs after successful final-component lookup. It bypasses checks for pledge's own unveil operation, absent unveil state, or `BYPASSUNVEIL`.
- Directory terminal matches require a vnode unveil with user-set flags and matching requested access.
- Non-directory terminal matches first check an exact named child under the parent directory, then directory-wide flags, then any covering matches found during traversal.
- Access mismatch sets `AUNVEIL` in accounting flags and returns `EACCES` when a visible unveil entry exists with some permission mask, or `ENOENT` when the path should appear hidden.

Vnode removal:
- `unveil_removevnode()` scans active processes for entries referencing a vnode being removed, nulls those entries, clears flags, releases references, decrements `v_uvcount`, and leaves holes for later lookup behavior.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_unveil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_uuid.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_uuid.c

Read completely: 119 lines.

Contains minimal kernel UUID formatting support and documentation for UUID octet layout. In this OpenBSD version the file defines only debug-only print helpers plus a private layout structure; the encode/decode section is represented by comments but no non-debug encode/decode functions are implemented in the file.

Key contents:
- `struct uuid_private` describes UUID fields as time-low, time-mid, time-hi, sequence, and node words for formatting.
- Under `DEBUG`, `uuid_snprintf()` formats a UUID into canonical hexadecimal groups, converting sequence and node words from big endian.
- Under `DEBUG`, `uuid_printf()` prints the formatted UUID via `printf()`.
- The final comment documents the RFC/DCE UUID octet layout with time, clock sequence, and node fields.

Dependencies and notes:
- Includes `sys/endian.h` for `betoh16()`, `sys/systm.h` for `snprintf()`/`printf()`, and `sys/uuid.h` for public UUID constants and types.
- There is no allocation, locking, parsing, generation, or syscall/sysctl surface in this file.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_uuid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_watchdog.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_watchdog.c

Read completely: 108 lines.

Implements the generic kernel watchdog control shim. Hardware drivers register a callback, and `KERN_WATCHDOG` sysctls control watchdog period and automatic tickling.

Core state:
- `wdog_ctl_cb` and `wdog_ctl_cb_arg` hold the registered hardware control callback and argument.
- `wdog_period` stores the active period in seconds.
- `wdog_auto` controls whether the kernel periodically refreshes the watchdog.
- `wdog_timeout` is the timeout used for automatic half-period tickles.

Behavior:
- `wdog_register()` accepts the first watchdog provider only and initializes `wdog_timeout`.
- `wdog_tickle()` calls the registered provider with the current period and reschedules itself for half the period in milliseconds.
- `wdog_shutdown()` cancels the timeout, disables the hardware watchdog by calling the provider with period 0, clears the callback, and restores defaults when the caller's argument matches.
- `sysctl_wdog()` exposes `KERN_WATCHDOG_PERIOD` and `KERN_WATCHDOG_AUTO`, using `sysctl_int_bounded()`. Period writes stop any current timeout, call the provider, and store the provider-returned period.

Concurrency and dependencies:
- Uses the timeout subsystem for recurring tickles.
- Returns `EOPNOTSUPP` if no watchdog provider is registered.
- No explicit mutex is used here; callers rely on the surrounding sysctl path and simple single-provider semantics.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_watchdog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_xcall.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_xcall.c

Read completely: 157 lines.

Implements cross-CPU function calls. It provides a common API for initializing an `xcall`, executing it locally at softclock IPL, queueing it to another CPU with an IPI on multiprocessor systems, synchronous cross-calls, and uniprocessor fallbacks.

Core behavior:
- `cpu_xcall_set()` stores the callback and argument in a caller-owned `struct xcall`.
- `cpu_xcall_self()` raises to `IPL_XCALL` (`IPL_SOFTCLOCK`), invokes the callback locally, and restores IPL.
- On multiprocessor kernels, `cpu_xcall()` executes immediately for the current CPU or atomically claims a slot in the target CPU's `ci_xcall.xci_xcalls[]`, sends an IPI, and busy-waits if all slots are full.
- `cpu_xcall_dispatch()` is called by machine-dependent IPI code, drains non-NULL xcall slots on the target CPU, clears each slot, and invokes callbacks.
- `cpu_xcall_establish()` initializes a CPU's xcall slots to NULL.

Synchronous calls:
- `struct xcall_sync` wraps an xcall plus a condition variable.
- `cpu_xcall_done()` runs the requested callback and signals the condition.
- `cpu_xcall_sync()` queues a wrapper xcall to the target CPU and waits on the condition variable with the provided wait message.

Uniprocessor fallback:
- `cpu_xcall()` and `cpu_xcall_sync()` simply execute the callback locally with `IPL_XCALL` raised.
- The file depends on machine-dependent `cpu_xcall_ipi()` only in the multiprocessor path.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_xcall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_xxx.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_xxx.c

Read completely: 181 lines.

Contains miscellaneous kernel entry points: reboot/powerdown helpers, stack-smash panic support when propolice/ret-protector are not used, and optional syscall debugging traces.

Reboot and power handling:
- `sys_reboot()` requires superuser privileges, stops secondary CPUs on multiprocessor kernels, and calls `reboot()` with the requested flags.
- `reboot()` stops periodic RTC syncing, sets the global `rebooting` flag, and calls machine-dependent `boot()`.
- `do_powerdown()` sends `SIGUSR2` to init once when `allowpowerdown` is enabled, then disables further automatic powerdown requests.
- `powerbutton_event()` ignores events during resume when suspend support says the system is resuming, otherwise queues `powerdown_task` on `systq`.

Safety/debug support:
- `__stack_smash_handler()` panics with the damaged function name for builds without propolice and return protector support.
- Under `SYSCALL_DEBUG`, `scdebug_call()` and `scdebug_ret()` print syscall entry/return diagnostics for unimplemented/out-of-range calls by default, or all calls when configured. Argument display is controlled by `SCDEBUG_SHOWARGS`; `lseek` return formatting handles `off_t`.

Global state:
- `rebooting` indicates reboot is in progress.
- `powerdown_task` is a taskqueue item wrapping `do_powerdown()`.
- Optional `scdebug` bit flags control syscall debug verbosity.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_xxx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/makesyscalls.sh -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/makesyscalls.sh

Read completely: 467 lines.

Shell/awk generator for OpenBSD syscall tables and headers. Given an input syscall master file, it generates syscall names, syscall numbers, syscall switch entries, and syscall argument structures.

Inputs and outputs:
- Requires exactly one input file and exits with usage otherwise.
- Emits `syscalls.c`, `../sys/syscall.h`, `init_sysent.c`, and `../sys/syscallargs.h`.
- Uses temporary files `sysent.dcl`, `sys.protos`, and `sysent.switch`, deleted via shell trap.
- Configurable variables include output paths, switch table name `sysent`, syscall name table `syscallnames`, constant prefix `SYS_`, and `compatopts`. This OpenBSD script explicitly does not support `LIBCOMPAT`.

Preprocessing:
- A `sed` stage removes dollar signs, joins backslash-continued lines, and inserts spaces around braces, parentheses, stars, and commas except preprocessor lines.
- The awk stage skips blank/comment lines, preserves includes and conditional preprocessor directives in generated outputs, and tracks nested `#if`/`#else`/`#endif` syscall number state.

Parsing and validation:
- Syscall numbers must be strictly synchronized with the first field; mismatches are fatal.
- `parseline()` handles optional `NOLOCK`, optional function alias, return type, function name, argument list, varargs marker, and a maximum of six syscall arguments.
- Argument metadata is used both for syscall switch argument size and for generated `struct <syscall>_args` definitions.
- Errors include unexpected tokens, unbalanced preprocessor conditionals, too many arguments, and unrecognized syscall keywords.

Generated content:
- Initializes standard generated-file comments and a `syscallarg(x)` macro with endian-aware padding.
- `putent()` writes prototypes, `struct sysent` entries, syscall names, syscall number defines, libc-lint prototype comments, and syscall argument structs.
- `STD`, `NODEF`, and `NOARGS` entries generate normal syscall switch entries with different header/argument-struct behavior.
- `OBSOL` and `UNIMPL` entries emit `sys_nosys` switch entries and human-readable names; obsolete entries still leave comments in the number header.
- Compatibility keywords would be mapped through generated wrapper macros if `compatopts` were populated.
- The END block closes generated arrays and defines `SYS_MAXSYSCALL`.

Build role:
- This is build-time source generation, not runtime kernel code.
- It is intentionally strict because the generated syscall ABI headers and dispatch table must remain numerically aligned with the master syscall list.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/makesyscalls.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sched_bsd.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/sched_bsd.c

Read completely: 768 lines.

Implements the classic BSD scheduler policy pieces used by OpenBSD: round-robin prompting, load average calculation, CPU usage decay, priority recalculation, context switching glue, runnable-state transitions, scheduler clock charging, and CPU performance policy sysctls.

Scheduling timers and load:
- `roundrobin()` advances a clock request by `roundrobin_period`, marks the current CPU's scheduler flags with `SPCF_SEENRR`/`SPCF_SHOULDYIELD`, and calls `need_resched()` if there are runnable peers or a yield is due.
- `update_loadavg()` runs every five seconds, combines non-idle CPU count and per-CPU runqueue lengths, and updates 1/5/15 minute load averages with fixed-point decay constants.
- `scheduler_start()` starts `schedcpu()`, `update_loadavg()`, and the performance-policy timeout when dynamic policy is active.

CPU usage and priorities:
- `schedcpu()` runs every second over `allproc`, increments sleep time for sleeping/stopped threads, decays `p_pctcpu`, stops recalculating priorities for threads that slept the whole second, updates CPU tick deltas, computes new estimated CPU with load-sensitive decay, and requeues runnable threads if their priority bucket changes.
- `decay_aftersleep()` applies additional load-sensitive decay to a thread's estimated CPU usage after a long sleep.
- `setpriority()` computes user priority from base `PUSER`, estimated CPU, nice value weighted by `NICE_WEIGHT`, and `MAXPRI`.
- `schedclock()` charges the current non-idle, non-spinning thread one unit of estimated CPU and recalculates its priority.

Switching:
- `yield()` and `preempt()` place the current thread back on its run queue, account voluntary or involuntary context switches, and call `mi_switch()`.
- `mi_switch()` releases the kernel lock on MP kernels before switching, charges runtime, cancels optional per-thread clock interrupts, clears switch-related scheduler flags, chooses the next process, calls `cpu_switchto()` when needed, restores IPL/scheduler lock state, runs SMR idle handling, restarts optional interval/profiling clock interrupts for the resumed thread, records runtime start time, and reacquires the kernel lock if it was held.
- Tracepoints record off-CPU, on-CPU, and remain-on-CPU events.

Runnable transitions:
- `setrunnable()` moves stopped or sleeping threads to run queues, handles races with `P_INSCHED`, emits tracepoints, uses sleep priority or user priority as appropriate, decays priority after long sleep, and clears `p_slptime`.

Performance policy:
- Global policy state includes `cpu_setperf`, `perflevel`, AC policy, and battery policy. Policies are manual, auto, or high.
- `setperf_auto()` samples per-CPU idle and total CPU state counters, detects load requiring full speed, applies downbeat hysteresis before slowing down, and reschedules itself every 100 ms when dynamic policy is active.
- `sysctl_hwsetperf()` exposes manual performance level setting only when AC policy is manual; otherwise it is read-only.
- `sysctl_hwperfpolicy()` reads or writes policy strings such as `manual`, `auto`, `high`, or an AC/battery pair, rejects unsupported manual battery combinations, immediately raises performance for high policy, and starts the dynamic timeout when needed.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sched_bsd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/spec_vnops.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/spec_vnops.c

Read completely: 746 lines.

Implements vnode operations for special device files (`VCHR` and `VBLK`) in OpenBSD. It connects VFS operations to character/block device switch tables, enforces securelevel and mount restrictions, handles buffered block-device I/O, fsync/invalidation, advisory locks, pathconf, kqueue filters, and cloned character devices.

Vops table:
- `spec_vops` maps generic unsupported filesystem operations to badop/generic handlers and implements open, close, access, getattr, setattr, read, write, ioctl, kqfilter, fsync, inactive, strategy, print, pathconf, advlock, and bwrite behavior for special vnodes.
- `speclisth[SPECHSZ]` is the special vnode hash/list storage.

Open and close:
- `spec_open()` rejects opens from `MNT_NODEV` mounts, validates major numbers, enforces securelevel restrictions on writing disk devices and `/dev/mem`/`/dev/kmem`, prevents writing mounted corresponding block devices, marks tty vnodes, delegates clone devices to `spec_open_clone()`, and calls the relevant character or block `d_open`.
- `spec_close()` handles controlling-terminal vnode references, clone-device bookkeeping, last-reference behavior, block-device buffer invalidation via `vinvalbuf()`, forced close cases during vnode cleaning, and calls the relevant device `d_close`.
- Cloned character devices clear their bitmap slot and release their parent vnode after successful close.

Read/write and strategy:
- `spec_read()` dispatches character reads directly to `cdevsw[].d_read()` with the vnode unlocked. For block devices it rejects negative offsets, chooses an I/O size from partition FFS fragment metadata when available, performs buffered reads with simple read-ahead using `v_lastr`, and copies data with `uiomove()`.
- `spec_write()` dispatches character writes to `cdevsw[].d_write()` with the vnode unlocked. For block devices it reads the containing block, copies user data into the buffer, and writes full blocks asynchronously or delayed-writes partial blocks.
- `spec_strategy()` forwards buffer I/O to the block device strategy routine.

Device operations and metadata:
- `spec_ioctl()` dispatches to character or block `d_ioctl`.
- `spec_kqfilter()` uses a device-provided character-device kqfilter when present, otherwise supports poll/select fallback through `seltrue_kqfilter()` for non-character cases.
- `spec_fsync()` flushes dirty buffers for block devices and waits for completion when requested.
- `spec_inactive()` simply unlocks the vnode.
- `spec_getattr()`, `spec_setattr()`, and `spec_access()` operate only on clone vnodes and forward metadata/access operations to the parent special vnode.
- `spec_print()` emits debug vnode information when debug/diagnostic flags are enabled.
- `spec_pathconf()` returns POSIX limits relevant to special devices.
- `spec_advlock()` delegates byte-range advisory locking to `lf_advlock()` over `v_speclockf`.

Clone devices:
- `spec_open_clone()` allocates a free clone minor slot from the parent bitmap, creates a new character device vnode with the encoded clone minor, opens the cloned device, marks the clone vnode with `VCLONE`, stores parent linkage in `v_specparent`, marks the parent `VCLONED`, and installs `struct cloneinfo` in the parent vnode data.
- Failure paths clear the allocated bitmap slot and release the clone vnode.

Filesystem relevance:
- This file is the VFS-to-device bridge for special files. Block device reads/writes use the buffer cache and partition geometry, while open/close rules protect mounted filesystems and securelevel-sensitive devices.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/spec_vnops.c -->