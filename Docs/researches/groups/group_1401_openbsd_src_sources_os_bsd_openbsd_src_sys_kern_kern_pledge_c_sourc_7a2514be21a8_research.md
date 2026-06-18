# Group Research: group_1401_openbsd_src_sources_os_bsd_openbsd_src_sys_kern_kern_pledge_c_sourc_7a2514be21a8

Scope: `Docs/research_subset_a.md`, OpenBSD kernel sources under `sources/os/bsd/openbsd-src/sys/kern`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_pledge.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_pledge.c

Purpose: Implements OpenBSD `pledge(2)` promise parsing and runtime enforcement across syscalls, path lookup, file descriptor passing, sysctl, ioctl, sockets, socket options, and selected helpers.

Key behavior:
- Defines `pledge_syscalls[]`, mapping each syscall to required promise bits or `PLEDGE_ALWAYS`.
- Parses promise strings through sorted `pledgereq[]` and `pledgereq_flags()`.
- `sys_pledge()` only permits promise reduction, supports exec promises, and destroys unveil state when path-related promises are dropped.
- `pledge_syscall()` snapshots per-process promises into the thread and rejects missing syscall promises.
- `pledge_fail()` either returns `ENOSYS` in `error` mode or logs, marks accounting, stops sibling threads, and forces `SIGABRT`.

Filesystem and path relevance:
- `pledge_namei()` is the central filesystem gate. It checks `ni_pledge` against current promises, handles `exec`, `rpath`, `wpath`, `cpath`, `dpath`, and delegates unveil checks to `namei()`.
- `__pledge_open()` paths receive special handling for fixed libc/service files such as `/dev/null`, `/etc/resolv.conf`, `/etc/hosts`, password databases, and zoneinfo.
- File descriptor passing rejects directory vnode descriptors while allowing sockets, pipes, dmabuf, sync objects, and non-directory vnodes.

Security and device filtering:
- `pledge_sysctl()` whitelists read-only MIBs by promise category.
- `pledge_ioctl()` contains narrow allowlists for tty, disklabel, audio, video, DRM, PF, BPF, VMM, PSP, tape, route, and write-route operations.
- `pledge_sockopt()` separates always-safe options, DNS resolver options, routing table changes, multicast options, and general inet/unix permissions.
- Helper checks cover `chown`, `adjtime`, `sendto`, `socket`, `flock`, `swapctl`, `fcntl(F_SETOWN)`, `kill`, and executable mappings after `kbind`.

Important dependencies:
- VFS/namei: `struct nameidata`, `BYPASSUNVEIL`, vnode/file types.
- Process state: `ps_pledge`, `ps_execpledge`, `PS_PLEDGE`, `PS_EXECPLEDGE`.
- Signal path: violations call `sigabort()` and may use `single_thread_set()`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_pledge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_proc.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_proc.c

Purpose: Maintains process, thread, uid, process-group, session, and debugger-visible process bookkeeping.

Key behavior:
- `procinit()` initializes global process lists, pid/tid/pgrp/uid hash tables, and pools for `proc`, `process`, `rusage`, `ucred`, `pgrp`, and `session`.
- `uid_find()`, `uid_release()`, and `chgproccnt()` track per-UID process counts behind `uidinfolk`.
- Lookup helpers include `tfind()`, `tfind_user()`, `prfind()`, `pgfind()`, and `zombiefind()`.
- `inferior()` checks parent ancestry for operations such as `setpgid`.

Process groups and sessions:
- `enternewpgrp()` creates a new process group and optionally a new session, including controlling-terminal/session metadata.
- `enterthispgrp()` moves a process between groups and updates job-control counts.
- `leavepgrp()` and `pgdelete()` remove group membership and release sessions.
- `fixjobc()`, `killjobc()`, and `orphanpg()` implement terminal job-control rules, including SIGHUP/SIGCONT delivery to orphaned stopped groups.

Filesystem relevance:
- Session cleanup can revoke a controlling terminal vnode through `VOP_REVOKE()` and release `s_ttyvp`.
- Process/session state here is used by tty, signal, and VFS permission-adjacent code elsewhere.

Diagnostics:
- DDB helpers print process state, kill/stop processes, and dump process lists in several views.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_prot.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_prot.c

Purpose: Implements process identity, credentials, process groups/sessions syscalls, group membership, login name, TCB syscalls, and thread names.

Key behavior:
- Simple getters return pid, thread id, parent pid, pgrp, session, uid/gid variants, groups, and `issetugid`.
- `sys_setsid()` and `sys_setpgid()` enforce POSIX session and process-group rules using `prfind()`, `pgfind()`, `inferior()`, and pgrp creation helpers.
- UID/GID mutation syscalls copy credentials before modification, enforce root/current-id permissions, mark `PS_SUGID`, and adjust per-UID process counts when real UID changes.
- `sys_setgroups()` requires root and replaces supplementary groups.
- `groupmember()`, `suser()`, and `suser_ucred()` provide group/root checks.

Credential lifecycle:
- `crget()`, `crhold()`, `crfree()`, `crcopy()`, and `crdup()` manage pooled reference-counted credentials.
- `crset()` copies the mutable credential region.
- `crfromxucred()` converts exported user credentials into kernel credentials.

Filesystem/security relevance:
- Credentials maintained here are used throughout VFS permission checks, signal authorization, coredump ownership, and pledge helpers.
- `proc_cansugid()` blocks privilege elevation for traced processes or processes sharing file descriptor tables.
- `dorefreshcreds()` updates a thread's cached credential pointer from its process credential.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_prot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_resource.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_resource.c

Purpose: Implements priority syscalls, resource limits, CPU/runtime accounting, rusage aggregation, RLIMIT_CPU enforcement, and copy-on-write `plimit` structures.

Key behavior:
- `sys_getpriority()` and `sys_setpriority()` operate over process, process group, or user selection.
- `donice()` enforces ownership/root rules and updates all threads' scheduler priorities.
- `sys_setrlimit()` copies user limits and delegates to `dosetrlimit()`.
- `dosetrlimit()` serializes updates with `rlimit_lock`, clamps global maxima, adjusts stack VM protections for `RLIMIT_STACK`, and arms CPU-limit checking.
- `sys_getrlimit()` reads from the thread's cached `plimit`.

Accounting:
- `tuagg_sumup()`, `tuagg_get_proc()`, `tuagg_get_process()`, `tuagg_add_process()`, and `tuagg_add_runtime()` aggregate thread/process runtime and tick accounting using producer/consumer generation fields.
- `calctsru()` and `calcru()` convert statclock ticks into user/system/interrupt time.
- `dogetrusage()` builds `RUSAGE_SELF`, `RUSAGE_THREAD`, and `RUSAGE_CHILDREN`.
- `rucheck()` sends `SIGXCPU` at intervals and `SIGKILL` after hard CPU-limit breach.

Filesystem relevance:
- `RLIMIT_NOFILE` is clamped by `maxfiles`.
- `RLIMIT_CORE` is consumed by `kern_sig.c` coredump logic.
- Stack limit changes directly alter VM map protections through UVM.

Limit sharing model:
- `lim_startup()` initializes default limits and the `plimit` pool.
- `lim_fork()` shares limits after fork.
- `lim_write_begin()` and `lim_write_commit()` implement copy-on-write replacement.
- `lim_read_enter()` caches process limits per thread.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_resource.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_rwlock.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_rwlock.c

Purpose: Implements OpenBSD reader/writer locks, recursive rwlocks, WITNESS integration, diagnostics, and dynamically allocated rwlock objects.

Key behavior:
- Lock owner state encodes writer ownership or reader count in `rwl_owner`.
- Writers use CAS, optional MP spinning, waiters count, sleeps on `rwl_waiters`, and wake one writer before readers.
- Readers acquire directly when no writer and no waiters, otherwise sleep on `rwl_readers`.
- `rw_exit_read()` and `rw_exit_write()` validate ownership and call `rw_exited()` to wake waiters/readers.
- `rw_enter()` multiplexes read, write, downgrade, and no-sleep upgrade operations.
- `rw_status()` distinguishes unlocked, read-held, write-held by current thread, and write-held by another thread.

Concurrency details:
- Uses memory barriers around atomic owner transitions.
- Avoids spinning while holding the kernel lock.
- Supports interruptible sleeps via `RW_INTR`.
- WITNESS tracks lock ordering and assertions when enabled.

Recursive and object locks:
- `rrw_enter()` allows recursive write ownership and tracks `rrwl_wcnt`.
- `rrw_exit()` unwinds recursive holds before releasing the base rwlock.
- `rw_obj_init()`, `_rw_obj_alloc_flags()`, `rw_obj_hold()`, and `rw_obj_free()` manage pooled refcounted rwlock objects.

Filesystem relevance:
- This is a shared synchronization primitive used by VFS, process, resource-limit, and device paths. Correct wake ordering and ownership checks are foundational for filesystem concurrency.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_rwlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_sched.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_sched.c

Purpose: Implements per-CPU run queues, CPU selection, idle threads, process switching support, CPU sets, CPU hot/online controls, and scheduler barriers.

Key behavior:
- `sched_init()` and `sched_init_cpu()` initialize CPU sets, run queues, per-CPU clock interrupts, dead process lists, and SMR deferred queues.
- `sched_kthreads_create()` creates one idle thread per CPU.
- `sched_idle()` runs the idle loop, handles dead process cleanup, calls `smr_idle()`, enters/leaves idle CPU sets, and cooperates with CPU halt flags.
- `sched_exit()` moves dead threads to the local CPU dead list and switches to idle.
- `sched_toidle()` cancels per-thread timers, releases the kernel lock on MP, and switches directly to the CPU idle process.

Run queue logic:
- `setrunqueue()` chooses a CPU when needed, updates priority/run state, enqueues, marks queued CPU sets, wakes idle CPUs, and requests reschedule on priority preemption.
- `remrunqueue()` removes queued threads and updates per-CPU queue masks.
- `sched_chooseproc()` selects the highest-priority local runnable thread, steals from other CPUs, or runs idle.
- `sched_choosecpu()` and `sched_choosecpu_fork()` pick CPUs based on idle/queued sets, affinity, pegging, load, primary CPU cost, and pmap residency estimate.
- `sched_steal_proc()` migrates an eligible unpegged runnable thread.

Multiprocessor controls:
- `sched_peg_curproc()` and `sched_unpeg_curproc()` temporarily bind a thread to a CPU.
- `sched_start_secondary_cpus()` and `sched_stop_secondary_cpus()` maintain schedulable CPU sets.
- `sched_barrier()` queues a task that runs on a target CPU and signals completion.
- `cpuset_*()` helpers implement basic CPU set operations and sysctl-facing CPU online counts.

Filesystem relevance:
- Filesystem code depends on scheduler sleep/wakeup, SMR quiescence, process exit cleanup, and cross-CPU barriers for safe teardown.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_sensors.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_sensors.c

Purpose: Maintains kernel sensor device lists, sensor attachment numbering, lookup, periodic sensor task registration, and quiesce/restart behavior.

Key behavior:
- `sensordev_install()` inserts sensor devices into a sorted sparse-numbered global list and emits hotplug attach events.
- `sensor_attach()` inserts sensors per device, keeps sensors of the same type grouped, assigns per-type numbers, and updates `maxnumt`.
- `sensordev_deinstall()` and `sensor_detach()` remove devices/sensors and adjust counts.
- `sensordev_get()` and `sensor_find()` provide lookup by device number, type, and per-type sensor number.

Task model:
- `sensor_task_register()` creates or reuses the sensor task queue, allocates `sensor_task`, initializes timeout/task/rwlock, and starts the periodic cycle.
- `sensor_task_unregister()` marks tasks dead by setting period to zero under write lock.
- `sensor_task_tick()` queues work.
- `sensor_task_work()` runs the callback unless quiesced, frees dead tasks, or reschedules by period.

Concurrency:
- List mutations use `splhigh()`.
- Task lifetime is guarded by the task's rwlock plus deferred free from the worker.
- `sensor_quiesce()` waits for active sensor callbacks to drain; `sensor_restart()` clears the quiesced flag.

Filesystem relevance:
- No direct filesystem behavior. This is kernel device/sysctl support that may be observed through sensor sysctls allowed by pledge.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_sensors.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_sig.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_sig.c

Purpose: Implements signal dispositions, masks, delivery, process/thread stop and continue, traps, coredumps, signal wait/diversion, user return signal posting, and SIGIO ownership.

Signal state:
- `sigprop[]` defines default signal actions: kill, core, stop, continue, ignore, tty stop.
- `signal_init()`, `sigstkinit()`, `sigactsinit()`, and `sigactsfree()` initialize and manage signal action storage.
- `sys_sigaction()` and `setsigvec()` install dispositions, masks, restart behavior, `SA_RESETHAND`, `SA_SIGINFO`, `SA_ONSTACK`, `SA_NOCLDSTOP`, and `SA_NOCLDWAIT`.
- `execsigs()` resets caught signals and signal stack state across exec.
- `sys_sigprocmask()`, `sys_sigpending()`, `dosigsuspend()`, `sys_sigsuspend()`, `sys_sigaltstack()`, and `sigonstack()` handle masks and alternate stacks.

Signal authorization and sending:
- `cansignal()` enforces root, self, shared credentials, same-session SIGCONT, and restricted setugid child signaling rules.
- `sys_kill()`, `sys_thrkill()`, `killpg1()`, `pgsignal()`, and `pgsigio()` deliver to processes, threads, groups, broadcast targets, and SIGIO owners.
- `trapsignal()` records trap signal metadata and delivers immediately when possible.

Delivery engine:
- `ptsignal_locked()` decides target thread, ignored/held/caught/default action, process vs thread pending queues, sleep wakeups, stop handling, SIGCONT handling, and parent notifications.
- `setsigctx()` snapshots action context for `cursig()` and `postsig()`.
- `cursig()` selects pending signals, handles ptrace stops, default stop actions, ignored signals, and deep sleep unwind cases.
- `postsig()` builds `siginfo_t`, invokes MD `sendsig()`, updates masks, or terminates by `sigexit()`.
- `userret()` checks single-thread suspension, pending interval-timer signals, pending normal signals, and restores `sigsuspend` masks.

Thread/process suspension:
- `proc_trap()`, `process_stop()`, `process_continue()`, `proc_stop_setup()`, `proc_stop_finish()`, `process_suspend_signal()`, `proc_suspend_check()`, `single_thread_set()`, and `single_thread_clear()` coordinate ptrace, job-control stops, coredump/single-threading, and thread exit suspension.

Filesystem and coredump relevance:
- `sigexit()` performs coredumps for core-generating signals before `exit1()`.
- `coredump()` enforces `RLIMIT_CORE`, disables copyin checks if configured, handles setugid core policy, opens core files with `BYPASSUNVEIL`, validates regular file/link/mode/owner, truncates it, and calls ELF coredump writing.
- `coredump_write()` writes in `MAXPHYS` chunks, yields between writes, aborts on pending SIGKILL, and logs ENOSPC/write failures.
- `coredump_unmap()` unmaps VM ranges after dumping.

SIGIO:
- `sigio_setown()`, `sigio_getown()`, `sigio_copy()`, `sigio_free()`, and helpers manage async I/O signal ownership for processes or process groups, with session checks and stored credentials.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_sig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_smr.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_smr.c

Purpose: Implements safe memory reclamation deferred callbacks and grace-period waiting.

Key behavior:
- `smr_startup()` initializes the global deferred queue, WITNESS object, and wakeup timeout.
- `smr_startup_thread()` creates the `smr` kernel thread.
- `smr_thread()` waits for deferred callbacks, optionally pauses to batch work, waits for a grace period, then invokes each callback under WITNESS tracking.
- Long dispatch periods are rate-limited logged and tracepoints report latency/count.

Grace period model:
- `smr_grace_wait()` advances `smr_grace_period`, records it for the current CPU, then pegs the current process to each running CPU that has not crossed the period.
- `smr_idle()` dispatches local deferred callbacks and records quiescent-state grace-period progress with memory ordering.
- `smr_call_impl()` queues a callback on the current CPU deferred list and can expedite wakeup.
- `smr_barrier_impl()` waits until a queued callback has run using a `cond`.

Concurrency:
- Global queue protected by `smr_lock`.
- Per-CPU queues are dispatched at high IPL.
- MP builds use scheduler pegging and per-CPU grace-period counters; non-MP grace wait is effectively empty.

Filesystem relevance:
- Provides reclamation infrastructure suitable for lockless readers and deferred object teardown in kernel subsystems, including filesystem-adjacent caches and vnode-like structures.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_smr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_softintr.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_softintr.c

Purpose: Machine-independent soft interrupt implementation enabled under `__USE_MI_SOFTINTR`.

Key behavior:
- Defines `softintr_hand` with function, argument, runner CPU, level, flags, and state bits.
- `softintr_init()` initializes per-level queues.
- `softintr_establish()` maps IPL values to soft interrupt levels, allocates a handler, and records whether it is MPSAFE.
- `softintr_schedule()` queues a pending handler and calls machine `softintr()` while SPL is high, or marks restart if currently running.
- `softintr_dispatch()` drains a level queue, clears pending, records runner, runs with or without kernel lock depending on `SIF_MPSAFE`, handles restart, and increments `uvmexp.softs`.
- `softintr_disestablish()` marks dying, removes pending work, waits for a current runner through `sched_barrier()`, then frees.

Concurrency:
- All queues and handler state are protected by `softintr_lock`.
- Restart state prevents lost schedules while a handler is active.
- Disestablish uses scheduler barrier to avoid freeing a running handler.

Filesystem relevance:
- No direct filesystem logic. It is interrupt-bottom-half infrastructure used by drivers and networking/storage paths that can feed filesystem I/O.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_softintr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_srp.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_srp.c

Purpose: Implements shared reference pointers with garbage collection using hazard pointers on multiprocessor systems, with simpler behavior on uniprocessor builds.

Key behavior:
- `srp_init()`, `srp_gc_init()`, and `srpl_rc_init()` initialize SRP references and destructor/refcount state.
- Locked variants `srp_swap_locked()`, `srp_update_locked()`, and `srp_get_locked()` assume external update serialization.
- MP `srp_swap()` uses atomic pointer swap; `srp_update()` increments GC refcount for new values and starts GC for replaced values.
- `srp_enter()` reserves a per-CPU hazard record and reads a stable pointer.
- `srp_follow()` switches from one hazard-protected pointer to another.
- `srp_leave()` clears the hazard pointer.

GC model:
- `srp_v_referenced()` scans all CPUs' hazard records for a specific `srp` and value.
- If unreferenced, `srp_v_dtor()` calls the destructor and releases the GC refcount.
- If still referenced, `srp_v_gc_start()` allocates a context and retries via timeout until safe.
- `srp_finalize()` waits until a raw value is absent from all hazard records.

Filesystem relevance:
- SRP is a kernel pattern for read-mostly pointer publication and deferred free, useful for networking/VFS-style tables where readers avoid heavy locks.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_srp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_subr.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_subr.c

Purpose: Provides miscellaneous kernel support routines: safe user copy wrappers, `uio` movement, one-byte uio read helper, generic hash table allocation, and hook lists.

Key behavior:
- Under `PMAP_CHECK_COPYIN`, `copyinstr()` and `copyin()` call `check_copyin()` to reject ranges overlapping protected VM map regions.
- `uiomove()` copies between kernel buffers and user/kernel iovecs, respecting `uio_rw`, `uio_segflg`, residual count, offset, and iovec advancement.
- `ureadc()` emits one byte into a `uio`, advancing iovec/resid/offset.
- `hashinit()` rounds element count to a power of two, allocates an array of LIST heads, initializes them, and returns a hash mask.
- `hashfree()` frees the corresponding rounded hash table allocation.

Hooks:
- `startuphook_list` is globally initialized.
- `hook_establish()` allocates and inserts a hook at head or tail.
- `hook_disestablish()` removes and frees a hook.
- `dohooks()` runs hooks, optionally removing and freeing them.

Filesystem relevance:
- `uiomove()` is central to read/write paths across filesystems and devices.
- `copyin()` and `copyinstr()` gate user pointers used by syscall and path-handling code.
- `hashinit()` is a common primitive for vnode/inode/cache tables.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_synch.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_synch.c

Purpose: Implements kernel sleep/wakeup queues, sleeps with mutex/rwlock release, thread sleep/wakeup syscalls, reference counts, and simple condition waits.

Sleep/wakeup:
- `sleep_queue_init()` initializes hashed sleep queues by wait-channel address.
- `tsleep_nsec()` and `tsleep()` sleep on a channel, with signal and timeout semantics.
- `msleep_nsec()` and `msleep()` sleep while atomically releasing and optionally reacquiring a mutex.
- `rwsleep_nsec()` and `rwsleep()` do the same for rwlocks, restoring prior read/write status.
- `sleep_setup()` places the current thread on the hashed sleep queue and marks state.
- `sleep_finish()` arms/cancels timeouts, handles signal checks, suspension, scheduler switching, and timeout races.
- `wakeup_proc()`, `endtsleep()`, `unsleep()`, `wakeup_n()`, and `wakeup()` remove sleepers and make them runnable.

Signal and scheduler integration:
- `sleep_signal_check()` integrates interruptible sleeps with process suspension, stop signals, `cursig()`, `EINTR`, and `ERESTART`.
- `sys_sched_yield()` requeues the current thread and switches, using sibling run priorities for multithreaded processes.

User thread sleeps:
- `tslp_init()` initializes bucketed userspace thread-sleep queues.
- `sys___thrsleep()` copies and validates absolute timeout input, unlocks a userspace atomic lock, optionally checks abort, and sleeps on a stack entry.
- `sys___thrwakeup()` wakes matching waiters in the same process, or all shared `ident == -1` waiters.
- Bucket locks interlock userspace wakeups against sleep insertion/removal.

Reference and condition helpers:
- `refcnt_init()`, `refcnt_take()`, `refcnt_rele()`, `refcnt_rele_wake()`, `refcnt_finalize()`, and `refcnt_read()` provide traced atomic reference counting with memory barriers.
- `cond_init()`, `cond_signal_handler()`, and `cond_wait()` implement a small wait/signal primitive used by SMR and scheduler barriers.

Filesystem relevance:
- This file supplies the blocking, wakeup, timeout, and refcount mechanics used by VFS, buffer cache, locks, vnode teardown, and file/device wait paths.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/kern_synch.c -->