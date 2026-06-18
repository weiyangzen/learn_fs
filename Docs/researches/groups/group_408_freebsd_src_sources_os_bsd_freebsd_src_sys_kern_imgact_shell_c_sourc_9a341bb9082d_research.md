# Group Research: group_408_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_imgact_shell_c_sourc_9a341bb9082d

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/imgact_shell.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/imgact_shell.c

## Purpose
Implements FreeBSD's `#!` shell-script image activator for `execve(2)`. It recognizes scripts, parses the interpreter line, rewrites the exec argument vector, and registers the handler through the kernel exec switch.

## Key Elements
- Defines endian-aware `SHELLMAGIC` for `#!`.
- Enforces `MAXSHELLCMDLEN <= PAGE_SIZE` because the exec path maps only the first page.
- Enforces `MAXSHELLCMDLEN >= MAXINTERP + 3`.
- Main entry point: `exec_shell_imgact(struct image_params *imgp)`.
- Registration: `EXEC_SET(shell, shell_execsw)` with `.ex_name = "#!"`.

## Behavior
`exec_shell_imgact()`:
- Rejects non-`#!` files by returning `-1`, allowing other image activators to try.
- Rejects recursive shell interpretation using `IMGACT_SHELL`.
- Uses `VOP_GETATTR()` to limit parsing to actual file size rather than blindly trusting the mapped page.
- Parses interpreter path after leading spaces/tabs.
- Rejects empty interpreter paths with `ENOEXEC`.
- Rejects interpreter paths at or above `MAXINTERP` with `ENAMETOOLONG`.
- Parses the remainder of the first line as a single optional argument string, trimming trailing spaces/tabs.
- Requires a newline or NUL before `MAXSHELLCMDLEN`; otherwise returns `ENOEXEC`.
- Uses `imgp->args->fname` as script name, or synthesizes `/dev/fd/<fd>` through `sbuf` for fd-backed exec.
- Calls `exec_args_adjust_args()` to remove the original `argv[0]` and insert interpreter, optional argument string, and script filename.
- Sets `imgp->interpreter_name` to the rewritten argument buffer so the generic exec path can execute the interpreter.

## Research Notes
The historical comment is significant: FreeBSD intentionally passes all post-interpreter text as one argument instead of tokenizing it in-kernel. This keeps quoting/comment interpretation in the interpreter, not in the kernel.

## Interfaces And Dependencies
Depends on exec argument management from `kern_execve.c`-side helpers, vnode metadata via `VOP_GETATTR()`, and `sbuf` for `/dev/fd` fallback construction.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/imgact_shell.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/init_main.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/init_main.c

## Purpose
Contains the machine-independent kernel startup path, process 0 construction, init process creation, and the ordered `SYSINIT` execution machinery.

## Key Elements
- Permanent boot objects: `session0`, `pgrp0`, `proc0`, `thread0_st`, `vmspace0`, `initproc`.
- Startup entry point: `mi_startup()`.
- Sysinit structures: `sysinit_list`, `sysinit_done_list`, linker set `sysinit_set`.
- Init process path sysctl: `kern.init_path`.
- Init shutdown timeout sysctl: `kern.init_shutdown_timeout`.
- DDB support: `show sysinit`.

## Startup Ordering
`sysinit_mklist()` turns linker-set entries into a sorted STAILQ using `subsystem` then `order`. `sysinit_add()` merges new sorted sysinit entries into the live list, supporting later additions such as KLD-provided sysinits.

`mi_startup()`:
- Enables verbose boot if `RB_VERBOSE` is set.
- Builds and sorts the sysinit list.
- Iteratively removes the earliest sysinit from `sysinit_list`, appends it to `sysinit_done_list`, and calls it.
- Emits boottrace events at subsystem boundaries.
- Supports optional verbose sysinit printing and DDB symbol lookup.
- Unlocks `Giant` after startup and leaves the original startup thread sleeping forever.

## Process 0 Initialization
`proc0_init()` builds the kernel process and initial thread:
- Initializes process, thread, scheduler, prison, session, process group, pid/tid hash state.
- Creates credentials rooted in uid/gid 0 and prison0.
- Initializes signal actions, fd tables, process descriptors, limits, racct, stats, and vmspace.
- Initializes `vmspace0` and its pmap/map.
- Invokes process/thread init and ctor event handlers.
- Charges root for the kernel process.

`proc0_post()` resets process and thread start/runtime accounting after filesystem time has been established, then updates per-CPU switch timing.

## Init Process
`create_init()` forks process 1 from `thread0` in stopped state, marks it system/in-memory/reaper, gives it separated credentials, and installs `start_init()` as its thread handler.

`kick_init()` later makes init runnable at `SI_SUB_KTHREAD_INIT`.

`start_init()`:
- Mounts root with `vfs_mountroot()`.
- Removes the GELI passphrase environment entry.
- Handles dual-console reporting.
- Reads `init_path` from the kernel environment if present.
- Tries each colon-separated init path.
- Builds exec args with `argv[0] = path` and optional `-s` for single-user mode.
- Calls `kern_execve()` and completes `exec_cleanup()` on `EJUSTRETURN`.
- Panics if no init path can be executed.

## Research Notes
This file is central boot glue rather than one subsystem. It wires together sysinit sequencing, proc0, pid 1, root mounting, and the final transition into userland.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/init_main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/init_sysent.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/init_sysent.c

## Purpose
Generated FreeBSD native syscall switch table. It maps syscall numbers to handlers, argument counts, audit events, Capsicum capability flags, and syscall-thread accounting mode.

## Key Elements
- Header explicitly says: generated, do not edit.
- Table: `struct sysent sysent[]`.
- Argument sizing macro: `AS(name)`.
- Compatibility dispatch macros: `compat`, `compat4`, `compat6`, `compat7`, `compat10`, `compat11`, `compat12`, `compat13`, `compat14`.
- Unsupported compatibility entries fall back to `nosys`.
- Loadable or reserved subsystem placeholders use `lkmressys` / `lkmnosys`.

## Table Semantics
Each entry contains:
- `.sy_narg`: argument count in `syscallarg_t` units.
- `.sy_call`: syscall handler cast to `sy_call_t *`.
- `.sy_auevent`: audit event identifier.
- `.sy_flags`: capability-mode and related flags, commonly `SYF_CAPENABLED`.
- `.sy_thrcnt`: syscall thread accounting/static/absent state.

## Coverage
The file includes syscall numbers 0 through 602. It covers legacy BSD syscalls, modern FreeBSD syscalls, compatibility shims, jail/rctl/capsicum calls, POSIX timers, aio, kqueue, cpuset, file-handle syscalls, and newer Linux-like interfaces such as `timerfd_*`, `renameat2`, and inotify-related calls.

## Filesystem-Relevant Entries
Important VFS/filesystem-related entries include:
- `open`, `openat`, `close`, `close_range`, `read`, `write`, `readv`, `writev`, `pread`, `pwrite`, `preadv`, `pwritev`.
- `link`, `linkat`, `unlink`, `unlinkat`, `rename`, `renameat`, `renameat2`, `symlink`, `symlinkat`, `readlink`, `readlinkat`.
- `mkdir`, `mkdirat`, `rmdir`, `mkfifo`, `mkfifoat`, `mknodat`.
- `stat`, `fstat`, `lstat`, `fstatat`, `statfs`, `fstatfs`, `getfsstat`, `fhstat`, `fhstatfs`, `getdirentries`.
- `mount`, `nmount`, `unmount`, `quotactl`, `sync`, `fsync`, `fdatasync`, `fspacectl`, `copy_file_range`.

## Research Notes
This is ABI-defining generated data. Behavioral research should trace handlers in their implementation files, while syscall number, audit, and capability-mode behavior should be read from this table.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/init_sysent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_acct.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_acct.c

## Purpose
Implements BSD process accounting: `acct(2)` enable/disable, process-exit record generation, accounting-file free-space monitoring, and accounting sysctls.

## Key Elements
- Main syscall: `sys_acct()`.
- Exit hook entry point: `acct_process(struct thread *td)`.
- Accounting state: `acct_vp`, `acct_cred`, `acct_flags`, `acct_configured`, `acct_suspended`.
- Synchronization: `acct_sx`.
- Monitoring thread state: `acct_state` with `ACCT_RUNNING` and `ACCT_EXITREQ`.
- Sysctls: `kern.acct_suspend`, `kern.acct_resume`, `kern.acct_chkfreq`, `kern.acct_configured`, `kern.acct_suspended`.

## Enabling And Disabling
`sys_acct()`:
- Requires `PRIV_ACCT`.
- Opens the target path for append with `NOFOLLOW`.
- Requires a regular vnode.
- Applies MAC checks when enabled.
- Serializes replacement or disable through `acct_sx`.
- Closes the previous accounting file with `acct_disable()`.
- Saves vnode, credential, and flags for the active accounting file.
- Starts the low-priority accounting monitor kproc if needed.
- Treats file replacement as log rotation and avoids redundant enable/disable logs.

Passing `NULL` disables accounting and requests monitor-thread exit.

## Process Record Generation
`acct_process()`:
- Uses a lockless fast-path check before taking `acct_sx`.
- Fills `struct acctv3` on process exit.
- Records controlling tty, command name, user/system CPU time, start time, elapsed time, average memory, block I/O count, uid/gid, and accounting flags.
- Encodes time and long values into IEEE-754 single-precision bit patterns using `encode_timeval()` and `encode_long()`.
- Writes with `vn_rdwr(..., IO_APPEND | IO_UNIT, acct_cred, ...)`.
- Marks the thread with `TDP2_ACCT` while accounting is in progress.

## Space Monitoring
`acctwatch()`:
- Handles disabled or forcibly invalidated accounting vnodes.
- Uses `VFS_STATFS()` on the accounting file's mount.
- Suspends accounting below `kern.acct_suspend` percent available blocks.
- Resumes above `kern.acct_resume` percent available blocks.

`acct_thread()` runs at low priority, periodically calls `acctwatch()`, sleeps on `acct_state`, and exits when requested.

## Research Notes
The conversion block is explicitly marked for regression testing. The active vnode and credential lifetime is protected by `acct_sx`; callers should not touch `acct_vp` without observing that locking design.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_acct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_alq.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_alq.c

## Purpose
Implements the kernel asynchronous logging queue facility. Producers append fixed or variable sized records to in-memory circular buffers; a kernel daemon drains active queues to vnode-backed log files.

## Key Elements
- Queue type: `struct alq`.
- Entry type used by zero-copy API: `struct ale`.
- Global daemon/list state: `ald_queues`, `ald_active`, `ald_mtx`, `ald_proc`, `ald_thread`.
- Queue flags: `AQ_WANTED`, `AQ_ACTIVE`, `AQ_FLUSHING`, `AQ_SHUTDOWN`, `AQ_ORDERED`, `AQ_LEGACY`.
- Public APIs: `alq_open_flags()`, `alq_open()`, `alq_writen()`, `alq_write()`, `alq_getn()`, `alq_get()`, `alq_post_flags()`, `alq_flush()`, `alq_close()`.
- Module: `DECLARE_MODULE(alq, ...)`.

## Daemon And Shutdown
`ald_startup()` initializes global locks and lists. `ald_daemon()` waits for active queues, removes them from the active list, calls `alq_doio()`, and wakes blocked producers when space becomes available.

`ald_shutdown()` is registered on `shutdown_pre_sync`; it blocks new queues, drains every queue, wakes the daemon, and waits for daemon exit unless `RB_NOSYNC` or scheduler-stopped conditions apply.

## Queue Operation
`alq_open_flags()`:
- Opens/creates the target file for writing with `O_NOFOLLOW`.
- Holds a vnode reference and credential.
- Allocates the `alq` and ring buffer.
- Registers the queue globally unless shutdown is in progress.

`alq_open()` provides legacy fixed-size entry setup when `count > 0`.

`alq_writen()`:
- Checks message size, shutdown state, free space, and `ALQ_NOWAIT`.
- Supports ordered writers via `AQ_ORDERED`.
- Sleeps for resources when allowed.
- Copies data into the circular buffer with wrap handling.
- Activates the queue unless `ALQ_NOACTIVATE` is used.

`alq_getn()` / `alq_post_flags()` provide a direct-write API to avoid a copy. `alq_getn()` may wrap early to preserve contiguous space and records the skipped bytes in `aq_wrapearly`.

## Disk Flush
`alq_doio()`:
- Builds one or two iovecs depending on circular-buffer wrap.
- Performs `VOP_WRITE()` with `IO_UNIT | IO_APPEND`.
- Uses MAC write checks when enabled.
- Updates write tail, free byte count, wrap state, and queue indices.
- Wakes waiters when `AQ_WANTED` was set.

The source explicitly ignores `VOP_WRITE` errors in this path.

## Research Notes
The facility separates producer latency from disk I/O but does not provide per-record durable success reporting. The `ALQ_NOACTIVATE` path is intentionally constrained to avoid deadlocks when pending inactive data would prevent progress.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_alq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_boottrace.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_boottrace.c

## Purpose
Implements boot-time, runtime, and shutdown tracing tables for kernel and userland milestones. Trace data is exposed through `kern.boottrace` sysctls and optional console dumping.

## Key Elements
- Event record: `struct bt_event`.
- Table state: `struct bt_table`.
- Tables: `bt` for boot, `rt` for runtime, `st` for shutdown.
- Default sizes: boot 3000, runtime 2000, shutdown 1000, minimum 500.
- Global enable: `boottrace_enabled`, tunable/sysctl `kern.boottrace.enabled`.
- Public functions: `boottrace()`, `boottrace_dump_console()`, `boottrace_reset()`, `boottrace_resize()`.

## Event Data
Each event records:
- Cycle counter and kernel tick timestamp.
- CPU id.
- Current pid.
- Process/thread name.
- Event name.
- Process CPU time and block I/O counters when safe to fetch.

`dotrace()` is lockless and uses atomic compare-and-set on the table cursor so it can be called from interrupt-sensitive paths. Runtime traces wrap; boot and shutdown traces drop entries once full.

## Sysctl Interface
The file defines sysctls under `kern.boottrace`:
- `log`: read formatted boot/runtime trace log.
- `boottrace`: write a boot event.
- `runtrace`: write a runtime event and mark boot complete.
- `shuttrace`: write a shutdown event and mark shutdown tracing active.
- `reset`: reset runtime tracing by recording a reset event.
- `shutdown_trace`: console dumping control.
- `shutdown_trace_threshold`: minimum delta threshold for selective shutdown console output.
- `table_size`: boot table tunable.

User messages may be `thread:event`; otherwise the current process name is used.

## Display Behavior
`boottrace_display()` walks the circular table from the current cursor, prints event deltas in milliseconds, and can filter output by delta threshold. It also prints total measured time across the displayed trace.

`boottrace_dump_console()` dumps shutdown trace data during shutdown/reboot/panic, otherwise boot and runtime tables.

## Initialization
`boottrace_init()` runs at `SI_SUB_CPU`. If tracing is enabled, it allocates all three tables, creates an initial boot event, enables runtime wraparound, and leaves shutdown tracing non-wrapping.

## Research Notes
Because tracing is optional and disabled by default, users must enable it via tunables early enough for boot capture. Early events before table allocation are counted as `drops_early`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_boottrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_clock.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_clock.c

## Purpose
Implements core kernel clock handling: hardclock ticks, statclock accounting, profiling ticks, CPU time sysctls, interval timer AST delivery, optional deadlock detection, and software watchdog support.

## Key Elements
- Public clock handlers: `hardclock()`, `statclock()`, `profclock()`.
- Clock setup: `initclocks()`.
- Frequency globals: `stathz`, `profhz`, `profprocs`, `psratio`.
- Per-CPU tick tracking: `DPCPU_DEFINE_STATIC(long, pcputicks)`.
- Time conversion: `tvtohz()`.
- Profiling control: `startprofclock()`, `stopprofclock()`.
- Sysctls: `kern.cp_time`, `kern.cp_times`, `kern.clockrate`.

## Initialization
`initclocks()`:
- Initializes `time_lock`.
- Calls machine/eventtimer clock initialization through `cpu_initclocks()`.
- Computes `profhz`, `stathz`, and profiling ratio.
- Registers AST handlers for deferred profiling updates and interval timer signals.
- Attaches watchdog handling.

## Hardclock
`hardclock(int cnt, int usermode)`:
- Updates per-CPU and global ticks using atomic compare-and-set.
- Handles virtual and profiling interval timers via `hardclock_itimer()`.
- Invokes PMC hooks when configured.
- Calls `tc_ticktock()` for global timecounter advancement.
- Optionally runs device polling.
- Decrements and fires the software watchdog.
- Dispatches `clk_intr_event`.
- Performs CPU tick calibration on the first CPU.
- Enqueues epoch callback group tasks when pending.

## Statclock And Profiling
`statclock()`:
- Charges user, nice, system, interrupt, or idle CPU states.
- Updates per-thread tick counters.
- Updates resource usage integrals and max RSS.
- Records scheduler trace probes.
- Updates thread runtime and calls `sched_clock()`.

`profclock()` records user-mode profiling samples for processes with `P_PROFIL`.

`startprofclock()` and `stopprofclock()` maintain `profprocs` and start/stop the CPU profiling clock when transitioning between zero and nonzero profiled processes.

## Time Conversion
`tvtohz()` normalizes user-provided `timeval` values, handles microsecond underflow/overflow, clamps negative times to one tick, clamps huge values to `INT_MAX`, and returns one extra tick to avoid early expiry.

## Optional Deadlock Resolver
Under `DEADLKRES`, a kernel thread scans all processes and threads for excessive blocking on turnstiles or sleepqueues. It uses tunable thresholds and panics when possible deadlock conditions persist.

## Watchdog
`watchdog_config()` converts watchdog interval commands to tick counts. `watchdog_fire()` enters KDB when available and interactive, otherwise panics.

## Research Notes
This file accounts CPU time at interrupt frequency and links low-level timer interrupts to scheduler, timecounter, resource accounting, profiling, watchdog, and eventhandler subsystems.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_clocksource.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_clocksource.c

## Purpose
Provides common eventtimer management for kernel clocks. It selects and programs hardware event timers, supports periodic and one-shot modes, handles per-CPU timer state, broadcasts timer events on SMP, and integrates callout scheduling.

## Key Elements
- Active eventtimer: `timer`.
- Per-CPU state: `struct pcpu_state`, stored in `DPCPU_DEFINE_STATIC(timerstate)`.
- Public clocksource hooks: `hardclockintr()`, `cpu_initclocks_bsp()`, `cpu_initclocks_ap()`, `suspendclock()`, `resumeclock()`, `cpu_startprofclock()`, `cpu_stopprofclock()`, `cpu_idleclock()`, `cpu_activeclock()`, `cpu_et_frequency()`, `cpu_new_callout()`.
- Sysctls: `kern.eventtimer.timer`, `kern.eventtimer.periodic`, `kern.eventtimer.singlemul`, `kern.eventtimer.idletick`.

## Event Handling
`timercb()` is the hardware eventtimer callback:
- Ignores callbacks during reconfiguration.
- Records current `sbinuptime()`.
- Updates next periodic or one-shot tick time.
- For non-per-CPU timers on SMP, marks other CPUs needing hardclock IPIs when their events are due.
- Calls `handleevents()` on the current CPU.
- Sends `IPI_HARDCLOCK` to other CPUs as needed.

`handleevents()`:
- Runs overdue hardclock events.
- Runs overdue statclock events.
- Runs overdue profclock events when profiling is active.
- Processes callouts when `nextcall` or `nextcallopt` is reached.
- Computes the next CPU event and reprograms the timer if needed.

## Timer Programming
`loadtimer()`:
- Starts periodic timers aligned to their period.
- For one-shot timers, computes the earliest next event across CPUs when required and calls `et_start()` only when the programmed time changes.

`setuptimer()`:
- Adapts desired periodic/one-shot mode to active timer capabilities.
- Clamps `singlemul`.
- Computes a feasible timer period with `round_freq()`.

`configtimer()`:
- Stops or starts the active timer.
- Initializes all per-CPU next-event fields.
- Uses IPIs and per-CPU `action` flags to start/stop per-CPU timers on other CPUs.
- Uses `busy` to block callbacks during reconfiguration.

## Initialization
`cpu_initclocks_bsp()`:
- Initializes global and per-CPU timer locks/state.
- Selects requested timer or best available periodic/one-shot timer.
- Applies C3-stop handling.
- Chooses `hz`, `stathz`, `profhz`, `tick`, `tick_sbt`, and related periods based on timer capabilities.
- Starts the configured timer.

`cpu_initclocks_ap()` initializes AP-local timer state and performs a fake event handling pass to program per-CPU timers.

## Idle, Profiling, And Callouts
`cpu_idleclock()` may suppress unnecessary ticks while idle, unless disabled or unsafe for the active mode. `cpu_activeclock()` catches up skipped events when the CPU becomes active.

`cpu_startprofclock()` and `cpu_stopprofclock()` switch timer configuration or profiling state as needed.

`cpu_new_callout()` updates per-CPU next callout deadlines, reprograms one-shot timers locally, or sends an IPI to make the target CPU reprogram its timer.

## Research Notes
This file is the bridge between abstract eventtimer hardware and higher-level clock consumers in `kern_clock.c`. Race control depends on `busy`, per-CPU spin locks, and IPI-synchronized reconfiguration.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_clocksource.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_condvar.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_condvar.c

## Purpose
Implements FreeBSD kernel condition variables on top of sleep queues, including interruptible waits, timed waits, unlock-on-wait variants, signal, and broadcast.

## Key Elements
- Public initialization/destruction: `cv_init()`, `cv_destroy()`.
- Wait variants: `_cv_wait()`, `_cv_wait_unlock()`, `_cv_wait_sig()`, `_cv_timedwait_sbt()`, `_cv_timedwait_sig_sbt()`.
- Wake variants: `cv_signal()`, `cv_broadcastpri()`.
- Waiter accounting: `cv_waiters`, bounded by `CV_WAITERS_BOUND`.
- KTRACE support for context switch tracing when `KTRACE` is enabled.

## Wait Behavior
Common wait paths:
- Assert valid current thread, condition variable, and lock.
- Emit WITNESS sleep warnings.
- Return immediately when `SCHEDULER_STOPPED()` requires it.
- Lock the sleepqueue for the condition variable.
- Increment approximate waiter count.
- Drop `Giant` around the sleep.
- Add the thread to the sleepqueue as `SLEEPQ_CONDVAR`, optionally `SLEEPQ_INTERRUPTIBLE`.
- Release the caller's lock through its lock class before sleeping.
- Sleep through `sleepq_wait()`, `sleepq_wait_sig()`, `sleepq_timedwait()`, or `sleepq_timedwait_sig()`.
- Reacquire the caller lock unless using `_cv_wait_unlock()`.

Timed waits set an sbintime timeout with `sleepq_set_timeout_sbt()`.

## Signal And Broadcast
`cv_signal()`:
- Fast-returns if `cv_waiters` is zero.
- Locks the sleepqueue and rechecks waiters.
- Handles saturated waiter count by checking `sleepq_lookup()`.
- Decrements waiter count when precise.
- Wakes one thread with `sleepq_signal(..., SLEEPQ_DROP, ...)`.

`cv_broadcastpri()`:
- Fast-returns when no waiters are known.
- Converts legacy priority `-1` to `0`.
- Resets waiter count to zero.
- Wakes all waiters with optional priority.

## Invariants
`cv_destroy()` verifies under `INVARIANTS` that no sleepqueue remains associated with the condition variable. `CV_ASSERT` requires the current thread to be running and the lock/cv pointers to be valid.

## Research Notes
`cv_waiters` is an optimization, not an exact unbounded count. Once it reaches `INT_MAX`, signal falls back to checking the sleepqueue so missed wakeups are avoided despite counter saturation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_condvar.c -->