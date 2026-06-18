# Group Research: group_298_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_kern_shutdown_c_so_9b254b4c8d7f

Scope confirmed against `Docs/research_subset_a.md`. All eight listed DragonFlyBSD kernel source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_shutdown.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_shutdown.c

## Purpose

`kern_shutdown.c` implements DragonFlyBSD's machine-independent reboot, shutdown, panic, kernel dump, and panic-notification path. It coordinates orderly sync/unmount behavior, panic-time CPU ownership, dump-device setup, registered shutdown event handlers, and final halt/reset behavior.

## Main Contents

- Shutdown registration:
  - `shutdown_conf()` registers final-stage handlers for poweroff delay, halt prompt, panic reboot delay, and reset.
  - `shutdown_nice()` records requested reboot flags and signals `init` with `SIGINT`, or directly boots with `RB_NOSYNC` if init is absent.
- Reboot path:
  - `sys_reboot()` checks reboot capability and calls `boot()`.
  - `boot()` raises priority, migrates shutdown to CPU 0 when possible, invokes shutdown eventhandler stages, cleans process filesystem references, syncs disks, optionally unmounts filesystems, performs dumps, and finally invokes reset/halt handlers.
- Panic path:
  - `panic()` serializes panic ownership through `panic_cpu_gd`, saves held token metadata, releases all tokens, resets spinlock accounting, formats and prints the panic, handles optional DDB/CPU stop behavior, and calls `boot()` with dump flags.
- Dump support:
  - `mkdumpheader()`, `setdumpdev()`, `dump_conf()`, `sysctl_kern_dumpdev()`, `set_dumper()`, and `dumpsys()` configure and execute kernel dumps.
- Shutdown support:
  - `shutdown_cleanup_proc()` drops process filesystem/vkernel/text/VM references.
  - `shutdown_kproc()` waits for system kthreads to suspend.
  - `dump_reactivate_cpus()` restarts stopped CPUs after requesting user reschedule.

## State And Interfaces

The file owns `panicstr`, `dumping`, dump-device setup, `bootverbose`, `cold`, `panic_cpu_gd`, and panic token snapshots. It exposes sysctls under `debug`, `kern`, `kern.shutdown`, and `machdep`, and uses eventhandler stages `shutdown_pre_sync`, `shutdown_post_sync`, and `shutdown_final`.

## Risks And Invariants

This code sits across VFS, buffer cache, process state, CPU control, console I/O, watchdog/panic notifiers, and dump devices. The panic path deliberately overrides normal lock/token rules; regressions here can deadlock secondary panics, lose dump state, or recurse while printing/dumping.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_shutdown.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_sig.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_sig.c

## Purpose

`kern_sig.c` implements DragonFlyBSD signal state, permission checks, process/LWP signal delivery, stop/continue handling, signal waits, signal posting to user mode, core dump policy, `kill` syscalls, `SIGIO` delivery, and kqueue signal filters.

## Main Contents

- Signal metadata and setup:
  - `sigproptbl`, `sigprop()`, `sig_ffs()`, and `sigsetfrompid()` classify signals and track sender info.
  - `kern_sigaction()`, `sys_sigaction()`, `siginit()`, `execsigs()`, `kern_sigprocmask()`, and related wrappers maintain handlers, masks, altstack state, and `SIGCHLD` flags.
- Delivery:
  - `kern_kill()`, `sys_kill()`, `sys_lwp_kill()`, `dokillpg()`, `gsignal()`, and `pgsignal()` implement direct, LWP, group, and broadcast signaling.
  - `trapsignal()` handles fault-originated LWP-specific signals.
  - `ksignal()` and `lwpsignal()` implement the core delivery logic, including ignored signals, traced processes, stop/continue side effects, generic vs LWP-specific pending sets, and kqueue notification.
  - `find_lwp_for_signal()`, `lwp_signotify()`, and `lwp_signotify_remote()` choose and wake target LWPs, including remote CPU IPI handling.
- Stop/continue:
  - `proc_stop()`, `proc_unstop()`, and `proc_stopwait()` manage process stop states and stopped LWP counts.
- Consumption:
  - `kern_sigtimedwait()`, `sys_sigtimedwait()`, and `sys_sigwaitinfo()` consume selected pending signals.
  - `iscaught()`, `issignal()`, and `postsig()` evaluate pending signals, handle tracing/default actions, and invoke the ABI send-signal hook.
- Termination/core:
  - `sigexit()` forces signal termination and coordinates core dumps.
  - `expand_name()` expands `kern.corefile`.
  - `coredump()` enforces core policy and delegates to `sv_coredump()`.
- Miscellaneous:
  - `sys_nosys()` sends `SIGSYS`.
  - `pgsigio()` sends stored-credential `SIGIO`/`SIGURG`.
  - `filt_sigattach()`, `filt_sigdetach()`, and `filt_signal()` implement kqueue signal filters.

## State And Dependencies

The file manipulates `proc`, `lwp`, `sigacts`, process groups, kqueue lists, process/LWP tokens, LWP spinlocks, and pending signal sets. It depends on scheduler wakeups, process lifecycle/exit code, VFS/namecache for core files, capability checks, tracing hooks, virtual-kernel trap redirection, and ABI-specific `sv_sendsig`/`sv_coredump`.

## Risks And Invariants

Correctness depends on token ordering and distinguishing process-pending from LWP-pending signals. Generic delivery uses `p_sigirefs` to avoid races with `sigsuspend`/`pselect`-style mask windows. Signal waits note a limitation where reposting after copyout failure can transform a thread-specific signal into a process signal.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_sig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_slaballoc.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_slaballoc.c

## Purpose

`kern_slaballoc.c` implements DragonFlyBSD's kernel malloc slab allocator. It provides per-CPU zone-backed small allocations, direct VM-backed oversized allocations, malloc type accounting, dynamic malloc pool management, remote-free handling, string duplication helpers, slab cleanup, and low-level wired kernel-memory allocation/free routines.

## Main Contents

- Initialization:
  - `kmeminit()` chooses zone sizing from memory/KVA limits and creates `ZeroPage`.
  - `kmemfinishinit()` adjusts free-zone release thresholds after CPU count is known.
  - `slab_gdinit()` initializes per-CPU slab queues.
- Malloc types:
  - `malloc_init()`, `malloc_uninit()`, and `malloc_reinit_ncpus()` manage `malloc_type` state and per-CPU accounting.
  - `kmalloc_raise_limit()`, `kmalloc_set_unlimited()`, `kmalloc_create()`, `_kmalloc_create_obj()`, and `kmalloc_destroy()` manage dynamic pools.
- Allocation/free:
  - `zoneindex()` maps sizes to chunk classes.
  - `_kmalloc()` handles limits, zero-size sentinel allocation, free-zone hysteresis cleanup, oversized VM allocation, and small slab allocation.
  - `krealloc()` reuses or reallocates based on usable size/chunk class.
  - `kmalloc_usable_size()` reports usable allocation size.
  - `_kfree()` handles local frees, oversized frees, deferred interrupt-context frees, and remote CPU frees.
  - `kfree_remote()` drains remote-freed chunks on the owning CPU.
  - `slab_cleanup()` periodically drains remote chunks and moves fully free zones to the free list.
- VM backend:
  - `kmem_slab_alloc()` reserves kernel map space, allocates/wires/maps VM pages, and handles blocking vs nonblocking allocation flags.
  - `kmem_slab_free()` removes the kernel map range.
- Debugging:
  - Defines common malloc types, KTR memory events, invariant allocation bitmaps, optional fill patterns, `SLAB_DEBUG` source tracking, and a `kmalloc_poller` kthread.

## State And Dependencies

The allocator uses per-CPU `SLGlobalData`, `SLZone` metadata, `btokup()` page-count metadata, `kmemstatistics`, kernel VM map/object state, pmap mappings, and malloc flags such as `M_WAITOK`, `M_RNOWAIT`, `M_ZERO`, `M_CACHEALIGN`, and reserve flags.

## Risks And Invariants

The hot path avoids locks through per-CPU ownership and critical sections. Remote free correctness depends on not dereferencing a zone after publishing a chunk to `z_RChunks` unless `z_RCount` protects it. Free paths avoid blocking because they may run from IPIs or interrupt-sensitive contexts.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_slaballoc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_spinlock.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_spinlock.c

## Purpose

`kern_spinlock.c` implements the contended slow paths for DragonFlyBSD exclusive/shared spinlocks, including exclusive-wait priority, shared-lock admission windows, indefinite-wait diagnostics, sysctl tuning, and invariant-only lock tests.

## Main Contents

- Defines `pmap_spin` and exposes `debug.spin_backoff_max`, `debug.spin_window_shift`, and `debug.indefinite_uses_rdtsc`.
- `spin_trylock_contested()` handles the degenerate shared-flag trylock case and unwinds failed optimistic attempts.
- `_spin_lock_contested()` converts an already-incremented inline attempt into a high-bit exclusive wait reservation, clears shared state, waits for low bits to drain, then transfers the reservation into an exclusive hold.
- `_spin_lock_shared_contested()` undoes the inline increment, waits for safe shared acquisition, and uses TSC windowing to balance shared progress against exclusive waiter priority.
- `spinlock_sysinit()` disables RDTSC-based indefinite behavior under VM guests.
- `sysctl_spin_lock_test()` provides invariant-only diagnostic/timing tests.

## State And Dependencies

The lock word packs low-bit holders/shared flag and high-bit exclusive waiters. The code depends on machine atomics, CPU pause/fence/rdtsc helpers, critical-section accounting, per-CPU spinlock counts, KTR, and the indefinite-wait framework.

## Risks And Invariants

The slow paths assume inline fast paths have already adjusted critical-section and spinlock state. Exclusive acquisition must preserve earlier exclusive waiters and clear stale shared state. Shared acquisition must avoid both reader starvation and writer starvation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_spinlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_subr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_subr.c

## Purpose

`kern_subr.c` provides common kernel subroutines for fault-controlled user copies, `uio` data movement, hash table allocation helpers, iovec copyin/free support, and physical-page-backed `uiomove` using lightweight buffers.

## Main Contents

- `copyin_nofault()` and `copyout_nofault()` set `TDF_NOFAULT` around user copies.
- `uiomove()` copies between a kernel buffer and a `uio`, supporting userspace, sysspace, and no-copy modes while updating residual/offset/iovec state.
- `uiomovebp()` wraps `uiomove()` for locked buffers and zero-fills a partially valid final VM page for cached regular-file buffers.
- `uiomove_nofault()`, `uiomovez()`, `uiomove_frombuf()`, and `ureadc()` provide nofault, zero-fill, bounded-buffer, and single-character helpers.
- `hashinit()`, `hashdestroy()`, `hashinit_ext()`, `phashinit()`, and `phashinit_ext()` allocate and destroy hash tables.
- `iovec_copyin()` copies and validates user iovec arrays, using small caller storage when possible.
- `uiomove_fromphys()` maps physical pages through `lwbuf` and copies page-by-page to/from a `uio`.

## State And Dependencies

The file exposes `kern.iov_max`, uses thread flags for nofault/deadlock treatment, relies on VM page validity helpers, `lwbuf` mapping, malloc types, and buffer/vnode metadata.

## Risks And Invariants

For userspace `uio`s, `uio_td` must be the current thread. All `uiomove` variants mutate the `uio` in place and must preserve residual/offset consistency on partial errors. Hash destroy assumes callers have already removed entries.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_synch.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_synch.c

## Purpose

`kern_synch.c` implements DragonFlyBSD's sleep/wakeup machinery, interlocked sleeps with locks, direct LWKT sleeps, timeout handling, runnable-state transitions, process stop waits, per-CPU sleep queues, scheduler accounting callouts, load average collection, and debug wakeup sysctls.

## Main Contents

- Scheduler accounting:
  - `schedcpu()`, `schedcpu_stats()`, and `schedcpu_resource()` update sleep time, scheduler load, CPU percentage, and CPU resource-limit enforcement.
  - `updatepcpu()` computes one-second CPU percentage samples.
  - `loadav()` calculates per-CPU runnable counts and global load averages.
  - `sched_setup()` initializes per-CPU callouts and registers load collection.
- Sleep queues:
  - `sleep_early_gdinit()`, `sched_dyninit()`, and `sleep_gdinit()` initialize dummy and real per-CPU sleep queues.
  - `_tsleep_interlock()` queues the current thread on an ident/domain without descheduling.
  - `tsleep_interlock()` and `tsleep_remove()` expose queue interlock/removal.
  - `tsleep()` handles early boot/panic fallback, signal checks, user scheduler release, timeout setup/cancel, sleep queue cleanup, and return status.
  - `endtsleep()` handles timeout wakeups.
- Lock-integrated sleeps:
  - `ssleep()`, `lksleep()`, `mtxsleep()`, and `zsleep()` interlock, release a held lock/serializer, sleep, and reacquire.
  - `lwkt_sleep()` directly deschedules the current LWKT thread and optionally marks it signal-interruptible.
- Wakeups:
  - `_wakeup()` scans CPU-local queues and sends remote IPIs based on global sleep-queue CPU masks.
  - `wakeup()`, `wakeup_one()`, `wakeup_mycpu()`, `wakeup_oncpu()`, and domain variants expose wakeup modes.
  - `wakeup_start_delayed()` and `wakeup_end_delayed()` coalesce up to two wakeups per CPU.
- Runnable/stop:
  - `setrunnable()` schedules a sleeping/stopped LWP on its owning CPU.
  - `tstop()` records the current LWP as stopped and sleeps while the process remains stopped.

## State And Dependencies

The file owns `lbolt`, `ncpus`, `safepri`, `tsleep_now_works`, load averages, sleep-queue hash state, and tunables such as `kern.pctcpu_decay`. It depends on LWKT scheduling, callouts, process/LWP tokens, signal checks, spinlocks, locks, mutexes, serializers, and KTR.

## Risks And Invariants

Sleep/wakeup correctness relies on CPU-local critical sections and no migration while queued. Wakeup uses memory fences before reading remote CPU masks to avoid lost wakeups. `tsleep()` must not block except by switching away after queue and timeout state are consistent.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_synch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_syscalls.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_syscalls.c

## Purpose

`kern_syscalls.c` provides dynamic syscall slot registration for loadable modules. It lets modules claim `sys_lkmnosys` placeholder entries in `sysent`, restore prior entries on unload, and chain module event handlers.

## Main Contents

- `sys_lkmnosys()` behaves like `sys_nosys()` but is identifiable as a reserved dynamic syscall placeholder.
- `syscall_register()` scans for a placeholder when `NO_SYSCALL` is requested, validates explicit offsets, rejects occupied slots, saves the old entry, and installs the new one.
- `syscall_deregister()` restores the old `sysent` entry for a nonzero offset.
- `syscall_module_handler()` registers on `MOD_LOAD`, stores the assigned offset in module-specific data, chains optional event handlers, and restores the syscall slot on successful unload.

## State And Dependencies

The file mutates the global `sysent` table and depends on syscall numbers, `struct syscall_module_data`, module-specific storage, and `sys_nosys()` behavior.

## Risks And Invariants

Registration assumes placeholder slots are preinstalled as `sys_lkmnosys`. There is no visible locking in this file, so module loading must provide serialization. The unload order lets chained handlers veto before the syscall entry is restored.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_sysctl.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_sysctl.c

## Purpose

`kern_sysctl.c` implements DragonFlyBSD's kernel sysctl MIB tree: static and dynamic OID registration, dynamic context cleanup, name/OID discovery nodes, default scalar/string/opaque handlers, kernel and user request transfer routines, syscall entry, sbuf draining, and global sysctl topology locking.

## Main Contents

- MIB tree:
  - `sysctl_register_oid()` / `sysctl_register_oid_int()` initialize OID locks, reuse existing nodes, assign `OID_AUTO` numbers, and insert OIDs sorted by number.
  - `sysctl_unregister_oid()` removes registered OIDs.
  - `sysctl_register_all()` registers static OIDs from `sysctl_set`.
  - `sysctl_rename_oid()` replaces an OID name.
- Dynamic contexts:
  - `sysctl_ctx_init()`, `sysctl_ctx_entry_add()`, `sysctl_ctx_entry_find()`, and `sysctl_ctx_entry_del()` manage context lists.
  - `sysctl_ctx_free()` dry-runs removals, restores on failure, then deletes for real.
  - `sysctl_remove_oid()` / `sysctl_remove_oid_locked()` remove dynamic OIDs, optionally recursively, wait for running handlers, and free dynamic storage.
  - `sysctl_add_oid()` creates or reuses dynamic OIDs.
- Discovery:
  - `sysctl_sysctl_name()`, `sysctl_sysctl_next()`, `sysctl_sysctl_name2oid()`, `sysctl_sysctl_oidfmt()`, and `sysctl_sysctl_oiddescr()` implement sysctl tree discovery.
- Default handlers:
  - Numeric handlers cover 8/16/32/64-bit values, `int`, `long`, `quad`, and bit fields.
  - `sysctl_handle_string()`, `sysctl_handle_opaque()`, and `sysctl_int_range()` handle strings, opaque data, and ranged ints.
- Execution:
  - `kernel_sysctl()` and `kernel_sysctlbyname()` run sysctls from kernel space.
  - `sys___sysctl()` and `userland_sysctl()` implement the user syscall path.
  - `sysctl_find_oid()` walks numeric OIDs.
  - `sysctl_root()` checks permissions, securelevel, capability requirements, handler presence, OID lock mode, and invokes handlers.
  - `sbuf_new_for_sysctl()` creates an sbuf draining through `SYSCTL_OUT()`.

## Locking Model

The topology lock is implemented as per-CPU `gd_sysctllock` locks. `_sysctl_xlock()` takes every CPU lock exclusively for topology mutation; normal traversal uses shared locking through macros. Individual OIDs also have per-OID locks, with default read-shared/write-exclusive behavior unless flags override it.

## Risks And Invariants

Dynamic removal is delicate because handlers can run while modules unload; `oid_running` draining and `CTLFLAG_DYING` protect unload correctness. `sysctl_handle_string()` assumes `arg1` is a valid writable buffer of size `arg2` for writes. Permission checks distinguish public discovery nodes from writes guarded by capability and securelevel rules.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_sysctl.c -->