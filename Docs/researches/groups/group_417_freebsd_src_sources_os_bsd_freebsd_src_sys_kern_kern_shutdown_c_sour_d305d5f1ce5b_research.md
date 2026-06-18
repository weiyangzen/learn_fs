# Group Research: group_417_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_kern_shutdown_c_sour_d305d5f1ce5b

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/freebsd-src` is included in subset A. All six listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_shutdown.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_shutdown.c

## Purpose

Implements FreeBSD kernel shutdown, reboot, panic, reroot, and kernel crash dump support. This file is the central path from user/kernel initiated reboot requests through filesystem sync, shutdown event handlers, optional panic dump generation, final halt/power/reset behavior, and dumper configuration.

## Main Responsibilities

- Handles `reboot(2)` through `sys_reboot()`, privilege/MAC checks, and either `kern_reboot()` or `kern_reroot()`.
- Implements `shutdown_nice()` by signaling `init(8)` with shutdown intent-specific signals.
- Coordinates shutdown phases:
  - `shutdown_pre_sync`
  - filesystem sync via `bufshutdown()`
  - `shutdown_post_sync`
  - optional crash dump
  - `shutdown_final`
  - CPU reset fallback
- Implements panic handling via `panic()` and `vpanic()`, including recursive panic behavior, KDB/debugger hooks, panic tracing, optional sync suppression, and panic reboot/poweroff policy.
- Manages kernel dump devices through `dumper_create()`, `dumper_insert()`, `dumper_remove()`, `dumper_destroy()`, and `kern.shutdown.dumpdevname`.
- Supports encrypted kernel dumps under `EKCD`, with AES-256-CBC and ChaCha20 setup.
- Supports compressed dumps via the kernel compressor interface, including gzip/zstd format selection and residual block handling.
- Provides dump write lifecycle helpers: `dump_start()`, `dump_append()`, `dump_write()`, `dump_finish()`, and `dump_init_header()`.
- Implements `RB_REROOT` support for remounting a new root filesystem while preserving selected mounts.

## Important Control Flow

- `kern_reboot()` is the primary shutdown pipeline. It drops Giant if necessary, binds to CPU 0 on SMP, marks `rebooting`, invokes shutdown handlers, syncs buffers unless `RB_NOSYNC`, optionally dumps core, and finally invokes reset handlers.
- `vpanic()` stops other CPUs where possible, marks `scheduler_stopped`, sets `panicstr`, emits panic diagnostics, enters KDB depending on tunables, sets dump/sync/power policy bits, and calls `kern_reboot()`.
- `doadump()` serializes dump attempts with `dumping`, saves CPU context, and iterates registered dumpers until one succeeds.
- `dump_start()` computes dump layout near the end of the dump device, preserving leading metadata and reserving space for headers and optional encrypted dump key.
- `dump_finish()` flushes compression, patches dump length/parity when compressed, writes headers, and finalizes the device with a zero-length write.

## State, Tunables, and Locking

- Global shutdown/panic state includes `panicstr`, `scheduler_stopped`, `dumping`, `rebooting`, and `dumped_core`.
- Dumper list `dumper_configs` is protected by `dumpconf_list_lk`.
- Key tunables include `kern.panic_reboot_wait_time`, `kern.reboot_wait_time`, `kern.sync_on_panic`, `kern.poweroff_on_panic`, `kern.powercycle_on_panic`, `debug.debugger_on_panic`, and `kern.shutdown.poweroff_delay`.
- Shutdown ordering is eventhandler based; priority registration matters for final halt/panic/poweroff behavior.
- Dump writes enforce block alignment, device bounds, and media offset/size constraints in `dump_check_bounds()`.

## Filesystem Relevance

This file directly affects filesystem integrity at shutdown. The normal reboot path invokes `bufshutdown()` unless explicitly bypassed, while panic paths commonly set `RB_NOSYNC` unless `sync_on_panic` is enabled. The reroot path manipulates mount lists, preserves `/dev`, unmounts all other filesystems, remounts root, and updates directory references through `mountcheckdirs()`.

## Cautions

- Panic and shutdown paths run under degraded conditions; many operations are deliberately best-effort.
- Recursive panic paths suppress sync and may enter debugger conditionally.
- Compressed dumps may shrink effective dump extent dynamically but still rely on later bounds checks.
- AES-CBC encryption cannot be combined with compression because compressed output may not be block-aligned.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_shutdown.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_sig.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_sig.c

## Purpose

Implements FreeBSD signal semantics: signal actions, masks, queues, delivery, process/thread targeting, job-control stops, ptrace stops, `SIGCHLD` reporting, invalid syscall signaling, `kqueue` signal filters, and fast userspace signal blocking.

## Main Responsibilities

- Defines signal default properties in `sigproptbl`, including terminate, core dump, stop, tty-stop, ignore, and continue behavior.
- Initializes signal queues and AST handlers in `sigqueue_start()`.
- Allocates, queues, moves, deletes, and flushes `ksiginfo_t` entries through `sigqueue_*()` helpers.
- Implements signal action syscalls:
  - `sys_sigaction()`
  - compatibility `freebsd4_sigaction()`
  - compatibility `osigaction()` and `osigvec()`
- Implements mask and wait syscalls:
  - `sys_sigprocmask()`
  - `sys_sigwait()`
  - `sys_sigtimedwait()`
  - `sys_sigwaitinfo()`
  - `sys_sigsuspend()`
  - compatibility old-mask variants
- Implements alternate signal stack handling through `sys_sigaltstack()` and `kern_sigaltstack()`.
- Implements signal send APIs:
  - `sys_kill()` / `kern_kill()`
  - `sys_pdkill()`
  - `sys_sigqueue()` / `kern_sigqueue()`
  - `pgsignal()`, `kern_psignal()`, `pksignal()`, `tdsignal()`, `tdksignal()`
- Implements delivery selection and wakeup behavior in `tdsendsignal()`, `sigtd()`, `tdsigwakeup()`, `cursig()`, `issignal()`, and `postsig()`.
- Handles ptrace signal stops and remote requests through `ptracestop()`, `ptrace_remotereq()`, `ptrace_coredumpreq()`, and `ptrace_syscallreq()`.
- Handles job-control notifications and `SIGCHLD` generation through `childproc_stopped()`, `childproc_continued()`, `childproc_exited()`, and `sigparent()`.
- Implements `nosys()` / `kern_nosys()` behavior for invalid syscalls, optionally sending `SIGSYS`.
- Implements `EVFILT_SIGNAL` attachment and event accounting.
- Manages shared `sigacts` objects and copy-on-write style signal action state.
- Implements `sigfastblock`, allowing userland to defer signal delivery with a user memory word.

## Important Control Flow

- Signal posting usually enters through `tdsendsignal()`. It selects a process or thread queue, decides whether the signal is ignored, held, caught, or defaulted, updates pending queues, schedules AST delivery, wakes sleeping threads where needed, and handles immediate stop/continue effects.
- User return signal handling uses `ast_sig()`, which repeatedly calls `cursig()` and `postsig()` while pending deliverable signals exist.
- `cursig()` delegates policy to `issignal()`, which combines thread and process pending sets, subtracts masks, handles fast-block state, and processes ignored/stopped/traced signals.
- `postsig()` removes the selected signal from queues, accepts timer signals when appropriate, either exits on default fatal action or calls the ABI-specific `sv_sendsig()` to build a user signal frame.
- Trap-generated signals use `trapsignal()`, which can immediately call `sv_sendsig()` if the signal is caught and unmasked, otherwise falls back to normal posting. If `kern.forcesigexit` is set, blocked/ignored trap signals are forced back to default handling to avoid loops.
- `kern_sigtimedwait()` temporarily unmasks the wait set, sleeps on `p_sigacts`, consumes matching queued signals, handles timer acceptance, and kills immediately on waited `SIGKILL`.

## State, Tunables, and Locking

- Signal queues exist at both process and thread level: `p_sigqueue` and `td_sigqueue`.
- Signal actions live in `struct sigacts`, protected by `ps_mtx`; process-level signal state is protected by `PROC_LOCK`.
- Pending queue allocation uses UMA zone `ksiginfo_zone`.
- Tunables include:
  - `kern.sigqueue.max_pending_per_proc`
  - `kern.sigqueue.preallocate`
  - `kern.forcesigexit`
  - `kern.lognosys`
  - `kern.signosys`
  - `kern.sigfastblock_fetch_always`
  - `kern.sig_discard_ign`
  - `debug.ptrace_attach_transparent`
- The file carefully interleaves `PROC_LOCK`, `PROC_SLOCK`, thread locks, `ps_mtx`, process group locks, and `proctree_lock`.

## Filesystem Relevance

Signals are not filesystem code, but they influence filesystem-visible behavior through process interruption and termination. `PCATCH` sleeps in VFS, buffer, mount, and driver paths depend on this signal machinery for `EINTR`/`ERESTART` behavior. `SIGKILL`, job-control stops, and ptrace stops can determine when a thread leaves or remains in filesystem code. Core dump signaling also connects to filesystem output via ABI-specific coredump hooks and ptrace-triggered coredump requests.

## Cautions

- Queueing policy distinguishes traditional bit-only pending signals from queued `ksiginfo_t`; overflow degrades some signals to simpler pending bits.
- `SIGKILL` and `SIGSTOP` have special fast paths and cannot be caught or masked.
- Stop/continue behavior is process-wide but often delivered through one selected thread.
- Ptrace can replace, discard, or requeue signals, so signal state may be deliberately re-evaluated after stops.
- Fast signal blocking depends on user memory access and can trigger `SIGSEGV` on invalid state.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_sig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_switch.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_switch.c

## Purpose

Provides machine-independent scheduler switch helpers, critical-section preemption exit handling, and generic run queue manipulation used by scheduler implementations.

## Main Responsibilities

- Exposes `kern.sched.preemption` to report whether kernel preemption is compiled in.
- Optionally exposes scheduler switch statistics under `kern.sched.stats`.
- Implements `choosethread()` and panic-aware `choosethread_panic()`.
- Implements KBI wrappers for `critical_enter()` and `critical_exit()`.
- Implements `critical_exit_preempt()`, which performs pending preemption once the current thread exits its final critical section.
- Implements generic run queue primitives:
  - `runq_init()`
  - `runq_add()`
  - `runq_add_idx()`
  - `runq_remove()`
  - `runq_findq()`
  - `runq_first_thread_range()`
  - `runq_not_empty()`
  - `runq_choose()`
  - `runq_choose_fuzz()`
  - `runq_is_queue_empty()`

## Important Control Flow

- `choosethread()` asks scheduler-specific `sched_choose()` for a runnable thread and marks it running. During panic, `choosethread_panic()` rejects ordinary non-system threads unless they are the panic thread.
- `critical_exit_preempt()` checks `td_critnest`, ignores KDB-active state, temporarily disables interrupt preemption while acquiring the thread lock, then calls `mi_switch()` with preemption switch flags.
- Run queue state is represented by per-priority queues plus compact status words. Queue operations maintain both the `TAILQ` and the status bit for fast scanning.
- `runq_findq()` scans status words over an inclusive queue-index range and calls a predicate on non-empty queues.
- `runq_choose_fuzz()` optionally prefers a thread that last ran on the current CPU among the first few entries of the best queue.

## State, Tunables, and Locking

- Run queue callers are responsible for scheduler locking; these helpers manipulate supplied `struct runq`.
- `td_rqindex` records the queue index used for removal.
- `RQ_NQS <= 256` is asserted so queue index storage remains valid.
- Tracing uses `KTR_RUNQ`, `KTR_PROC`, and optional scheduler statistics counters.

## Filesystem Relevance

This file is infrastructure for all kernel execution, including filesystem threads, syncer activity, vnode reclaim workers, and interruptible filesystem sleeps. It does not implement filesystem policy, but its run queue and preemption behavior affects latency and fairness of filesystem work.

## Cautions

- Run queue status bits must remain consistent with queue emptiness; assertions check for impossible non-empty bits with empty queues.
- Panic scheduling deliberately restricts runnable threads to reduce further damage.
- `critical_exit_preempt()` depends on precise critical nesting and thread-lock semantics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_switch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_sx.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_sx.c

## Purpose

Implements FreeBSD `sx` shared/exclusive sleep locks. These locks support shared readers, exclusive writers, optional recursion, upgrade/downgrade, interruptible waits, sleep queues, adaptive spinning on SMP, WITNESS/lockstat integration, and DDB diagnostics.

## Main Responsibilities

- Defines `lock_class_sx` and lock class operations for generic lock APIs.
- Initializes and destroys locks with `sx_init_flags()`, `sx_sysinit()`, and `sx_destroy()`.
- Implements shared locking:
  - `sx_try_slock_int()`
  - `_sx_slock_int()`
  - `_sx_slock_hard()`
  - `_sx_sunlock_int()`
  - `_sx_sunlock_hard()`
- Implements exclusive locking:
  - `_sx_xlock()`
  - `_sx_xlock_hard()`
  - `sx_try_xlock_int()`
  - `_sx_xunlock()`
  - `_sx_xunlock_hard()`
- Implements lock conversion:
  - `sx_try_upgrade_int()`
  - `sx_downgrade_int()`
- Provides assertion and debug support through `_sx_assert()`, `db_show_sx()`, and `sx_chain()`.

## Important Control Flow

- Fast paths use atomic compare-and-set on `sx_lock` for uncontended acquisition/release.
- Exclusive hard lock path handles recursion, adaptive spinning on a running owner, writer-spinner coordination against readers, setting exclusive waiter bits, and sleeping on the exclusive sleep queue.
- Shared hard lock path tries to enter while shared ownership is allowed, spins adaptively on active exclusive owners or reader state, sets shared waiter bits, and sleeps on the shared sleep queue if needed.
- Exclusive unlock wakes either shared or exclusive waiters depending on waiter bits and sleep queue contents.
- Shared unlock wakes exclusive waiters when the final reader releases and exclusive waiters are present.
- Downgrade converts an unrecursed exclusive hold into one shared hold and may wake shared waiters.
- Upgrade succeeds only when the caller is the sole shared holder, preserving waiter state.

## State, Tunables, and Locking

- `sx_lock` encodes owner/readers plus waiter and spinner bits.
- `sx_recurse` tracks exclusive recursion depth.
- Sleep queues use two queues:
  - queue 0 for exclusive waiters
  - queue 1 for shared waiters
- Giant is dropped before sleeping or adaptive spinning and restored afterward.
- With adaptive sx enabled, backoff parameters come from the global lock delay configuration or `debug.sx.*` custom knobs.
- Integrated with WITNESS, LOCK_PROFILING, KDTRACE lockstat probes, KTR tracing, and optional HWPMC lock-failed hooks.

## Filesystem Relevance

`sx` locks are widely used in FreeBSD VFS and filesystem code for sleepable shared/exclusive protection: mount structures, namecache-related paths, global namespace operations, and long-running operations that cannot use spin mutexes. Correct sx behavior is foundational for filesystem concurrency and deadlock avoidance.

## Cautions

- Shared ownership is not per-thread tracked without WITNESS; non-WITNESS assertions can only prove some reader exists.
- Recursion applies to exclusive locks when the lock is initialized as recursable.
- Interruptible sx waits can return errors and must be handled by callers.
- Waiter bit transitions and sleep queue locking are subtle; correctness depends on preserving flags across atomic state changes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_sx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_synch.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_synch.c

## Purpose

Implements core sleep/wakeup synchronization, pause helpers, blockcount waiting, machine-independent context switch accounting, load average maintenance, scheduler AST handling, yielding, and CPU-query syscalls.

## Main Responsibilities

- Initializes sleep queues in `sleepinit()`.
- Implements general sleep primitive `_sleep()`.
- Implements spin-mutex sleep primitive `msleep_spin_sbt()`.
- Implements `pause_sbt()` for timed delay/sleep, using busy delay during cold boot, KDB, or stopped scheduler.
- Implements wakeup APIs:
  - `wakeup()`
  - `wakeup_one()`
  - `wakeup_any()`
- Implements blockcount wake/wait helpers:
  - `_blockcount_wakeup()`
  - `_blockcount_sleep()`
- Implements machine-independent context switching in `mi_switch()`.
- Implements `setrunnable()` for transitioning a thread to runnable state.
- Maintains load average in `loadav()` and initializes scheduler callouts in `synch_setup()`.
- Handles scheduler AST preemption/yield path in `ast_scheduler()`.
- Implements yield helpers and syscalls:
  - `should_yield()`
  - `maybe_yield()`
  - `kern_yield()`
  - `sys_yield()`
  - `sys_sched_getcpu()`

## Important Control Flow

- `_sleep()` validates locking and sleep state, locks the sleep queue, drops Giant and the interlock as appropriate, enqueues the thread, installs timeout if requested, waits interruptibly or uninterruptibly, then reacquires locks unless `PDROP` was requested.
- `msleep_spin_sbt()` is the spin-mutex variant: it drops a spin mutex before sleeping and reacquires it afterward.
- `pause_sbt()` converts zero timeout to one tick and avoids scheduler sleeps when scheduler operation is not available.
- `_blockcount_sleep()` atomically coordinates a counter with waiters, avoiding sleeps when the count is already zero and returning `EAGAIN` after ordinary wakeups.
- `mi_switch()` validates switch context, records voluntary/involuntary switch counts, updates runtime accounting, emits tracing/probes, calls scheduler-specific `sched_switch()`, and stashes a dead thread after switch.
- `ast_scheduler()` restores user priority and switches with `SWT_NEEDRESCHED`.

## State, Tunables, and Locking

- `hogticks` controls yield heuristics.
- `pause_wchan[MAXCPU]` provides per-CPU pause wait channels.
- `averunnable` stores 1, 5, and 15 minute load averages using fixed-point constants.
- Sleep paths interact with lock classes, WITNESS, sleep queues, Giant, KTRACE, and signal interruption (`PCATCH`).
- `mi_switch()` requires the current thread lock on entry and releases it through scheduler switch mechanics.

## Filesystem Relevance

This file is directly relevant to filesystem blocking behavior. VFS, buffer cache, storage, and filesystem code use `_sleep()`, `msleep`, pause, wakeup, and blockcount waiting to coordinate I/O completion, vnode state changes, mount activity, shutdown drains, and background workers. Signal interruption semantics here combine with `kern_sig.c` to produce `EINTR`/`ERESTART` behavior in filesystem syscalls.

## Cautions

- `_sleep()` requires a valid interlock unless explicitly using `PNOLOCK` or a timeout-only style path; incorrect locking can race wakeups.
- `PDROP` means the caller does not regain the interlock.
- Context switching from KDB is redirected to debugger reentry/panic handling.
- `mi_switch()` must not be called from arbitrary critical-section states.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_synch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_syscalls.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_syscalls.c

## Purpose

Implements dynamic syscall table registration and deregistration support for loadable kernel modules and syscall helper arrays, including concurrency protection for in-flight dynamic syscall execution.

## Main Responsibilities

- Provides placeholder syscall handlers:
  - `lkmnosys()`
  - `lkmressys()`
- Defines `nosys_sysent`, a capability-enabled `nosys` sysent used when dynamic syscall slots are absent or draining.
- Tracks active dynamic syscall users through `sy_thrcnt`.
- Implements dynamic syscall entry/exit accounting:
  - `syscall_thread_enter()`
  - `syscall_thread_exit()`
  - internal `syscall_thread_drain()`
- Registers and deregisters individual syscalls:
  - `kern_syscall_register()`
  - `kern_syscall_deregister()`
- Handles module lifecycle integration:
  - `syscall_module_handler()`
  - `kern_syscall_module_handler()`
- Registers and unregisters arrays of syscall helper records:
  - `syscall_helper_register()`
  - `kern_syscall_helper_register()`
  - `syscall_helper_unregister()`
  - `kern_syscall_helper_unregister()`

## Important Control Flow

- `kern_syscall_register()` either finds a free `lkmnosys` slot when `NO_SYSCALL` is requested or validates a specified slot. It rejects occupied non-placeholder slots, installs the new `sysent`, and publishes `sy_thrcnt` with release ordering.
- `syscall_thread_enter()` increments `sy_thrcnt` for non-static dynamic syscalls. If the syscall is draining or absent, it redirects the caller to `nosys_sysent`.
- `syscall_thread_exit()` decrements the active thread count.
- `syscall_thread_drain()` marks a dynamic syscall as draining and waits until the active count reaches absent before deregistration completes.
- `kern_syscall_module_handler()` registers on `MOD_LOAD`, stores the assigned syscall number in module-specific data, optionally chains module event handlers, and deregisters on `MOD_UNLOAD`.
- Helper registration rolls back already-registered helper syscalls if a later helper registration fails.

## State, Tunables, and Locking

- Uses atomic operations on `sy_thrcnt` with `SY_THR_STATIC`, `SY_THR_DRAINING`, `SY_THR_ABSENT`, and active-count increments.
- Uses `MOD_XLOCK` only to store module-specific syscall number after registration.
- Registration assumes placeholder slots have protected absent state before replacement.

## Filesystem Relevance

This file is not filesystem-specific, but it is relevant to filesystem-related kernel modules that expose syscalls or helper syscall arrays. It ensures module unload does not remove syscall code while threads are still executing it.

## Cautions

- Static syscalls cannot be drained or dynamically deregistered.
- Slot 0 deregistration is treated as a no-op to simplify unload paths.
- Failed module load marks `data->offset = NULL` so unload will not invoke chained unload or deregistration for a syscall that was never installed.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_syscalls.c -->