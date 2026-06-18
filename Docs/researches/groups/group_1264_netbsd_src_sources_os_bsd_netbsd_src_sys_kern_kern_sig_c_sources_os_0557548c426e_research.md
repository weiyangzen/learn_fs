# Group Research: group_1264_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_kern_sig_c_sources_os_0557548c426e

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/os/bsd/netbsd-src`, which is included in subset A. All nine listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_sig.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_sig.c

Read completely: 2688 lines.

Implements NetBSD's kernel signal subsystem: signal action storage, pending signal queues, signal delivery, debugger/ptrace signal stops, process stop/continue state, signal-context save/restore, process-group signaling, core-dump termination, and kqueue signal filters.

Core state and initialization:
- `signal_init()` creates pool caches for `struct sigacts` and `ksiginfo_t`, initializes the process-stop callout, and registers a kauth listener for signal authorization.
- `siginit()` builds global masks for continue, stop, vfork-stop, and unmaskable signals, initializes process-0 signal state, ignored defaults, per-LWP pending queues, and default action flags.
- `sigactsinit()`, `sigactsunshare()`, and `sigactsfree()` manage shared or copied per-process signal actions with reference counts and a private mutex.

Pending signal queues:
- `ksiginfo_alloc()`/`ksiginfo_free()` manage `ksiginfo_t` lifetime, avoiding allocation for empty signal-info records where possible.
- `sigput()` adds pending signal information to either process or LWP queues, coalescing non-realtime signals and enforcing `SIGQUEUE_MAX`.
- `sigget()` and `siggetinfo()` select pending signals, remove one queued info record, manufacture `SI_NOINFO` when needed, and keep the signal bit set if multiple queued records remain.
- `sigclear()` and `sigclearall()` remove pending signals and move queued info records to a drain list for later freeing.

Signal posting and delivery:
- `kpsignal2()` is the central process-signal routine. It handles ignored signals, traced processes, process-vs-LWP delivery, stop/continue signal cancellation, signal waiters, pending queue insertion, and wakeup/notification of runnable or sleeping LWPs.
- `sigpost()` marks an LWP with `LW_PENDSIG`, wakes interruptible sleeps, restarts stopped LWPs for `SIGCONT`, promotes priority for default-kill signals, and decides whether an LWP can take the signal immediately.
- `issignal()` is the user/kernel-boundary selector for the current LWP. It processes ptrace stops, ignored/default actions, stop signals, pending per-LWP before per-process signals, and returns the signal to catch or terminate with.
- `postsig()` commits to a selected signal, updates masks for `sigsuspend`/normal delivery, extracts signal info, emits ktrace/DTrace probes, calls `sigexit()` for default-kill actions, or invokes the emulation signal sender.
- `sendsig()` dispatches between sigcode, legacy sigcontext, and siginfo trampoline versions; `sendsig_reset()` applies handler reset and mask changes after delivery.

Process stop, continue, and tracing:
- `proc_stop()`, `proc_stop_lwps()`, `proc_stop_done()`, and `proc_stop_callout()` coordinate stopping all LWPs, including races where an LWP enters interruptible sleep after `PS_STOPPING`.
- `sigswitch()` and `sigswitch_unlock_and_switch_away()` move the current LWP into stopped state and perform the scheduler switch.
- `proc_unstop()` resumes a stopped process, moving stopped LWPs back to sleep or run queues as appropriate.
- `trapsignal()`, `eventswitch()`, `eventswitchchild()`, and `proc_stoptrace()` integrate traps, ptrace events, syscall-entry/syscall-exit tracing, and synthetic `SIGTRAP` info with process stops.
- `sigchecktrace()` handles debugger-supplied signals while respecting pending `SIGKILL`.

Exit and core dump:
- `sigexit()` handles fatal-signal termination, coordinates multi-LWP core dumps, suspends peer LWPs while registers are dumpable, calls coredump module hooks, logs optional core status, applies PaX segvguard, clears `PS_WCORE`, and enters `exit1()`.
- `coredump_netbsd()`, `coredump_netbsd32()`, `coredump_elf32()`, and `coredump_elf64()` are module-hook wrappers.

Other interfaces:
- `killpg1()`, `pgsignal()`, `kpgsignal()`, `psignal()`, and `kpsignal()` implement process-group, broadcast, and process-specific sends with kauth checks and optional fd lookup by file data pointer.
- `getucontext()` and `setucontext()` copy signal mask, stack, link, and machine context while coordinating with `p_lock`.
- `sigismasked()` checks ignored or LWP-masked state.
- `filt_sigattach()`, `filt_sigdetach()`, and `filt_signal()` implement EVFILT_SIGNAL through the process klist.

Concurrency and notes:
- Most process signal mutation requires both `proc_lock` and `p_lock`; per-action mutation uses `sa_mutex`.
- Memory barriers protect pending-signal visibility before `LW_PENDSIG` is set.
- Several comments note allocations/freeing while locks are held and legacy SMP concerns.
- The stop path is deliberately conservative because parent notification must wait until all LWPs have stopped at least once.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_sig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_sleepq.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_sleepq.c

Read completely: 636 lines.

Implements NetBSD sleep queues used by condition variables, old sleep/wakeup APIs, and synchronization objects. It bridges wait-channel queues, LWP scheduler state, timeouts, interruptible sleeps, and signal-to-error conversion.

Core structures:
- `sleeptab` is the general-purpose hashed sleep table.
- `sleepq_locks[]` provides per-bucket spin mutexes.
- Individual `sleepq_t` queues are `LIST` heads containing sleeping LWPs.

Initialization and queue management:
- `sleeptab_init()` initializes each sleep-table queue and, once globally, the bucket locks.
- `sleepq_init()` initializes a single queue.
- `sleepq_insert()` inserts an LWP, optionally sorted by effective priority for priority-aware synchronization objects.
- `sleepq_reinsert()`, `sleepq_changepri()`, and `sleepq_lendpri()` reposition sleeping LWPs after priority or inherited-priority changes.

Sleep path:
- `sleepq_enter()` locks the current LWP, transfers to the sleep-queue lock if present, and drops kernel-lock recursion count as needed.
- `sleepq_enqueue()` records wait channel, wait message, sync object, sleep queue, interruptibility, sleep start ticks, and changes the current LWP to `LSSLEEP`.
- `sleepq_block()` performs the actual switch with optional timeout callout. It handles early interruption by cancellation, exit/core-dump flags, pending signals, timeout completion, and re-acquisition of dropped kernel locks.
- `sleepq_sigtoerror()` maps a delivered signal to `ERESTART` or `EINTR` depending on `SA_RESTART`.

Wake and removal:
- `sleepq_remove()` removes an LWP from its queue, clears sleep metadata, converts interruptible wakeups to non-interruptible state, and either leaves stopped/suspended LWPs stopped or makes sleeping LWPs runnable.
- `sleepq_wake()` wakes up to `expected` LWPs sleeping on a wait channel.
- `sleepq_unsleep()` removes one LWP from its queue due to out-of-band interruption.
- `sleepq_timeout()` is the timeout callout; it sets `LW_STIMO` and unsleeps the target if still waiting.

Special behavior:
- `sleepq_transfer()` moves an LWP from one sleep queue to another while updating wait channel, wait message, sync object, lock, and interruptibility.
- `sleepq_uncatch()` clears interruptible-sleep flags.
- `sleepq_abort()` supports autoconfiguration or panic-time sleeps by briefly lowering IPL and returning without real blocking.

Concurrency and notes:
- The sleep queue lock is also lent as the LWP lock while the LWP is queued.
- `LW_CATCHINTR` records the caller's intended interruptibility separately from transient `LW_SINTR`.
- Timeout callout halt is deliberately done in the sleeping LWP's context for cache locality and synchronization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_sleepq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_softint.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_softint.c

Read completely: 872 lines.

Implements NetBSD's generic software interrupt framework. It provides dynamically registered per-CPU callbacks at clock, bio, net, and serial software-interrupt levels, with both scheduler-based and architecture fast-softint dispatch paths.

Core structures:
- `softint_t` represents one interrupt level on one CPU, with a pending handler queue, backing LWP, CPU pointer, machine-dependent trigger token, event counters, active flag, IPL, and names.
- `softhand_t` stores one registered handler's function, argument, per-CPU interrupt object, flags, and optional remote-CPU IPI id.
- `softcpu_t` holds per-CPU softint state and the handler table.

Initialization and registration:
- `softint_init()` allocates per-CPU softint memory, initializes four softint LWPs per CPU, and copies established handlers from the boot CPU to later CPUs.
- `softint_init_isr()` creates the per-level interrupt LWP, attaches event counters, records IPL, and calls MD initialization.
- `softint_establish()` finds a free handler slot, optionally registers an IPI hook for `SOFTINT_RCPU`, and installs equivalent handler records on all CPUs.
- `softint_disestablish()` unregisters any IPI hook, runs an xcall barrier to ensure no handler is still executing, fires a DTrace probe, and clears the handler on all CPUs.

Scheduling and execution:
- `softint_schedule()` schedules a handler on the current CPU, requiring hardware-interrupt context or preemption disabled for stable `curcpu()`. It marks `SOFTINT_PENDING`, queues the handler, and triggers the softint if inactive.
- `softint_schedule_cpu()` schedules locally or sends an IPI to a remote CPU for handlers established with `SOFTINT_RCPU`.
- `softint_execute()` runs queued handlers FIFO at the requested softint level, drops/restores IPL around callbacks, takes the big kernel lock for non-MPSAFE handlers, emits SDT probes, and asserts no leaked spin locks, psrefs, biglocks, or preemption disables.
- `softint_block()` increments the per-level block counter when a softint LWP blocks.

Slow path without `__HAVE_FAST_SOFTINTS`:
- `softint_init_md()` makes each softint LWP runnable and records a CPU softint bit.
- `softint_trigger()` sets pending CPU bits and requests rescheduling or AST notification.
- `softint_thread()` loops running pending handlers then parks the softint LWP as idle.
- `softint_picklwp()` selects the highest-priority pending softint LWP for `mi_switch()`.

Fast path with `__HAVE_FAST_SOFTINTS`:
- `softint_thread()` must never be reached and panics.
- `softint_dispatch()` is entered by MD interrupt code, runs the softint on its dedicated LWP stack, optionally accounts interrupt time, and either returns to the pinned interrupted LWP or switches normally if the softint blocked.

Concurrency and notes:
- Handler queues are per-CPU and protected by raising IPL rather than inter-CPU locks.
- Registered handler identity is an offset within per-CPU `softcpu_t`, allowing the same handle to locate each CPU's copy.
- Softints may block briefly but must not perform long waits or resource sleeps.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_softint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ssp.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ssp.c

Read completely: 85 lines.

Implements kernel stack-smashing-protector support when built with `__SSP__` or `__SSP_ALL__`.

Behavior:
- Defines the stack canary storage as `stack_chk_guard`/`__stack_chk_guard`, with weak aliases for rump kernels.
- Defines `stack_chk_fail()`/`__stack_chk_fail()` to panic with `stack overflow detected; terminated`.
- `ssp_init()` obtains random guard bytes from `cprng_fast()`, raises IPL with `splhigh()`, copies the guard array into global canary storage without making extra function calls inside the critical update, restores IPL, and prints debug guard values.
- If SSP is not enabled, `ssp_init()` is an empty function.

Notes:
- The file is intentionally small and architecture-independent.
- Security depends on calling `ssp_init()` after entropy is available, as the comment states.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_ssp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_stub.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_stub.c

Read completely: 341 lines.

Provides fallback stubs, weak aliases, and generic error helpers for optional kernel facilities, unsupported syscalls, driver entry points, bus helpers, interrupt-distribution hooks, and architectures without kernel preemption.

Optional facility stubs:
- SYSV IPC entry points alias to `enosys` when non-modular kernels omit SYSV message queues, shared memory, or semaphores.
- Ktrace probes and syscalls alias to `nullop`, `sys_nosys`, or `enosys` when `KTRACE` is not configured.
- Device registration, SPL debug, machdep init, userconf, module MD init, kobj renamespace, interrupt query/distribution, bus-space reservation/tagging, bus-DMA tag creation, and kernel FPU hooks use weak aliases to no-op or error functions.
- Scheduler activation syscalls and selected compat stubs are hard-wired to `sys_nosys`.

Preemption stubs:
- When `__HAVE_PREEMPTION` is absent, `cpu_kpreempt_enter()` returns false, `cpu_kpreempt_exit()` is empty, and `cpu_kpreempt_disabled()` returns true.
- If preemption exists without `MULTIPROCESSOR`, the file triggers a build error.

Generic syscall/device helpers:
- `sys_nosys()` sends `SIGSYS` to the calling process under `proc_lock` and returns `ENOSYS`.
- `enodev()`, `enxio()`, `enoioctl()`, `enosys()`, and `eopnotsupp()` return their corresponding errno values.
- `voidop()`, `nullop()`, and `nullret()` provide common no-op callbacks.
- `default_bus_space_handle_is_equal()` and `default_bus_space_is_equal()` compare handles/tags with `memcmp()`.

Notes:
- This file is glue for build-time configurability; most symbols are intentionally replaceable by real implementations.
- The only active process side effect is `sys_nosys()` delivering `SIGSYS`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_stub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_subr.c

Read completely: 755 lines.

Implements root-device and dump-device selection during boot, including interactive root selection, NFS-root heuristics, memory-disk root handling, boot spec parsing, root hooks, wedge swap detection, and root/dump announcement.

Boot/root state:
- Defines `booted_device`, `booted_method`, `booted_partition`, `booted_startblk`, `booted_nblks`, and `bootspec`.
- Defines `dumpcdev` for savecore.
- `md_is_root` is initialized from `MEMORY_DISK_IS_ROOT`.
- `ROOT_WAITTIME` controls how long `setroot()` waits for a specified root device to appear before asking.

Root selection:
- `setroot()` normalizes `rootspec`, forces memory-disk root when requested, optionally handles TFTPROOT, applies NFS-root heuristics, enters ask mode when needed, and loops until `root_device` is set.
- `setroot_nfs()` chooses a non-loopback, non-point-to-point network interface as `rootspec` when the root filesystem is NFS and the boot device is missing or not a network interface.
- `setroot_md()` opens `md0` and rewrites the boot device to the memory disk if available.
- `setroot_root()` resolves non-interactive root selection from wildcard boot device, explicit `rootspec`, or existing `rootdev`.

Interactive selection:
- `setroot_ask()` prompts for root device, dump device, and filesystem type.
- It accepts defaults, wildcard `*`, `none` for dumps, `halt`, `reboot`, and optionally `ddb`.
- It updates `rootdev`, `dumpdev`, `rootfstype`, prints the chosen root, and calls `setroot_dump()`.

Dump device:
- `setroot_dump()` applies three rules: use the already selected interactive dump device, honor `dumpspec`, or default to root partition `b` for partitioned disks.
- For root devices without partitions, it searches configured devices for a `dk` wedge whose partition type is swap.
- It sets `dumpdev` and `dumpcdev`, or clears both to `NODEV`.

Parsing and device lookup:
- `finddevice()` first consults root-spec hooks, then falls back to `device_find_by_xname()`.
- `getdisk()` wraps `parsedisk()` and prints valid device alternatives on failure.
- `parsedisk()` parses optional partition suffixes, root-spec hooks, disk devices, network interfaces, and constructs `dev_t` values with or without partitions.
- `isswap()` opens a `dk` wedge, queries `DIOCGWEDGEINFO`, and checks for `DKW_PTYPE_SWAP`.

Notes:
- Despite living in `sys/kern`, this file is directly relevant to filesystem startup because it chooses the root filesystem device and dump device.
- The code supports network roots and disk roots uniformly through `device_class()` and `device_has_partitions()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_synch.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_synch.c

Read completely: 1277 lines.

Implements machine-independent synchronization and scheduling support: legacy sleep/wakeup wrappers, kernel pause, yield/preempt, kernel preemption, context switching, runnable-state transitions, reboot suspension, priority-change callbacks, runtime accounting, load average, and periodic process statistics.

Synchronization objects:
- `sleep_syncobj` backs normal sleep queues with sorted sleepq behavior and kernel boost priority.
- `sched_syncobj` represents scheduler-managed blocking/runnable state.
- `kpause_syncobj` is a null sleep-queue object for timed pauses where no wakeup is expected.
- `lbolt` is the once-per-second condition variable broadcast by `sched_pstats()`.

Sleep and wake wrappers:
- `tsleep()` and `mtsleep()` are legacy interfaces that resolve a sleep-table bucket, enter/enqueue on a sleepq, release optional interlocks, block with timeout and optional `PCATCH`, and restore locks as requested.
- `kpause()` blocks the current LWP with optional interruptibility and timeout, using the null sleep queue.
- `wakeup()` wakes all LWPs sleeping on a wait channel unless the system is still cold.

Yield, preemption, and preemption points:
- `yield()` and `preempt()` release kernel locks, move through `mi_switch()`, and reacquire locks; `preempt()` marks involuntary preemption.
- `preempt_needed()` checks the current CPU reschedule request with preemption temporarily disabled.
- `preempt_point()` voluntarily preempts long-running kernel code when needed.
- `kpreempt()` handles requested in-kernel preemption, deferring when preemption is disabled, running in softint context, holding/wanting the big kernel lock, or at an unsuitable IPL. It records event counters and lockstat failure timing.
- `kpreempt_disabled()`, `kpreempt_disable()`, and `kpreempt_enable()` expose explicit preemption state.

Context switching:
- `updatertime()` updates per-LWP runtime from `l_stime`, warning once if the timecounter appears to go backwards.
- `nextlwp()` selects the next runnable LWP from scheduler queues or the idle LWP, updates per-CPU priority/idle flags, and clears reschedule state when no slow softints remain.
- `mi_switch()` is the main MI context-switch path. It handles softint handoff, run queue re-enqueue, migration hints, syscall sleep/wakeup time accounting, DTrace vtime hooks, pmap deactivate/activate, `cpu_switchto()`, `LP_RUNNING` release protocol, lwpctl status, PCU switchpoints, and voluntary/involuntary switch counters.

Runnable and suspend state:
- `setrunnable()` transitions `LSSTOP`, `LSSUSPENDED`, `LSSLEEP`, or `LSIDL` LWPs back toward runnable/onproc state, including unsleeping wait-channel LWPs and selecting a CPU.
- `suspendsched()` marks non-system processes stopped for reboot/suspend, sets `LW_WREBOOT`/`LW_WSUSPEND`, wakes interruptible sleepers, and kicks all CPUs to reach user/kernel boundaries.
- `sched_unsleep()` should not be called for scheduler sync objects and panics.

Priority operations:
- `sched_changepri()` changes base priority for runnable/onproc/other LWPs and may reschedule realtime onproc LWPs.
- `sched_lendpri()` changes inherited/protection-derived auxiliary priority with analogous run queue or reschedule handling.
- `syncobj_noowner()` returns no owner for sync objects without ownership.

Periodic stats:
- Defines `ccpu` and `cexp[]` constants for CPU percentage decay and 1/5/15-minute load averages.
- `sched_pstats()` increments sleep/switch stats, calls scheduler LWP stats hooks, updates LWP and process CPU percentages, computes load averages, enforces `RLIMIT_CPU` by sending `SIGXCPU` or `SIGKILL`, broadcasts `lbolt`, and handles negative-runtime warnings.

Concurrency and notes:
- `mi_switch()` assumes the current LWP lock and per-CPU scheduler lock are held and preemption is disabled.
- Soft interrupt integration is explicit: slow softints can be selected before normal runnable LWPs, and fast softint return avoids normal VM-context accounting.
- Resource-limit enforcement uses `psignal()` after dropping `p_lock` while still under `proc_lock`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_synch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_syscall.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_syscall.c

Read completely: 310 lines.

Implements dynamic syscall module plumbing and syscall tracing hooks for NetBSD emulations.

Module-backed syscalls:
- `sys_nomodule()` is the placeholder for autoloadable syscall entries. With `MODULAR`, it takes `kernconfig_lock()`, checks whether the syscall entry was filled while waiting, looks up the emulation's autoload table, attempts `module_autoload()`, and returns `ERESTART` if the syscall should be retried. Without success, it falls through to `sys_nosys()`.
- `syscall_establish()` installs a package of syscall entry points after validating all requested slots are currently `sys_nomodule` or `sys_nosys`.
- `syscall_disestablish()` first gates removed entries back to `sys_nomodule` or `sys_nosys`, runs `xc_barrier()` for visibility across CPUs, scans all LWPs for active `l_sysent` references, and rolls back with `EBUSY` if any syscall is still in use.

Tracing:
- `trace_is_enabled()` reports whether syscall tracing is active through `SYSCALL_DEBUG`, ktrace syscall/sysret flags, or ptrace syscall tracing.
- `trace_enter()` emits DTrace syscall-entry hooks, optional syscall-debug output, ktrace syscall records, and ptrace syscall-entry stops through `proc_stoptrace(TRAP_SCE)`. It returns `EJUSTRETURN` when the tracer will emulate the syscall.
- `trace_exit()` emits DTrace syscall-return hooks, optional debug return output, ktrace sysret records, ptrace syscall-exit stops through `proc_stoptrace(TRAP_SCX)`, and clears `PSL_SYSCALLEMU`.

Concurrency and notes:
- Establish/disestablish require `kernconfig_lock()` to be held.
- Disestablish uses both a cross-call barrier and `alllwp` scan because a CPU may already have posted a `struct sysent *` in an LWP.
- This file ties directly into `kern_sig.c` through ptrace syscall-stop handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_sysctl.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_sysctl.c

Read completely: 2869 lines.

Implements the native NetBSD sysctl subsystem: the global sysctl tree, sysctl syscall dispatch, dynamic node create/destroy/query/describe operations, kernel convenience APIs, teardown logs, user/kernel copy wrappers, version conversion, generic helpers, and address hashing support.

Core state:
- `sysctl_root` is the root node of the native tree, initially read/write and numbered from `CREATE_BASE`.
- `sysctl_treelock` serializes tree access; comments note this lock is broad and held across allocation/copy operations.
- `sysctl_file_marker_lock` supports file-related sysctl marker users elsewhere.
- Kernel attributes stored here include `hostname`, `domainname`, `hostid`, and `defcorename`.
- `M_SYSCTLNODE` and `M_SYSCTLDATA` back node and sysctl-data allocations.

Initialization:
- `sysctl_init()` initializes the tree lock, root base node, all link-set sysctl setup functions, and the file marker lock.
- `sysctl_finalize()` marks the root permanent, preventing later permanent-node additions and enforcing read-only tree policy.
- `sysctl_copyin()`, `sysctl_copyout()`, and `sysctl_copyinstr()` abstract user vs kernel callers and emit ktrace MIB I/O records for user callers.

Syscall and dispatch:
- `sys___sysctl()` copies in the MIB and old length, locks the tree as writer if a new value is supplied, calls `sysctl_dispatch()`, unlocks, copies out the final length, and maps insufficient old buffer space to `ENOMEM`.
- `sysctl_lock()`, `sysctl_relock()`, and `sysctl_unlock()` manage read/write locking and mark the current LWP with `LP_SYSCTLWRITE`.
- `sysctl_dispatch()` locates the target node, enforces private-node read permission on final targets, invokes node-specific handlers, generic lookup, or meta-operations such as `CTL_QUERY`, `CTL_CREATE`, `CTL_DESTROY`, `CTL_MMAP`, and `CTL_DESCRIBE`.

Tree traversal and query:
- `sysctl_locate()` walks child arrays by numeric MIB component, handles private traversal checks, supports `CTLFLAG_ANYNUMBER`, follows aliases up to a bounded depth, and returns the last node plus consumed component count.
- `sysctl_query()` copies out `struct sysctlnode` descriptions under a node, merges emulation overlay trees, and supports version checks.
- `sysctl_cvt_in()` and `sysctl_cvt_out()` currently support `SYSCTL_VERSION`/`SYSCTL_VERS_1` node layout only.

Create, destroy, and lookup:
- `sysctl_create()` validates authorization, tree mutability, parent type, node name, number, type, flags, immediate/owned-data constraints, sizes, collisions, aliases, dynamic numbering, and optional symbol resolution. It allocates/grows child arrays, inserts the node in numeric order, reparents moved children, updates version numbers up to the root, and returns the created node description.
- `sysctl_destroy()` validates authorization and mutability, finds the requested child by number/name/version, refuses permanent or non-empty nodes, frees owned data/descriptions, compacts the child array, frees empty child arrays, updates versions, and returns the removed node description.
- `sysctl_lookup()` implements ordinary read/write of terminal values with private and modify authorization checks, exact-size writes for bool/int/quad/struct, bounded string writes with NUL handling, immediate-value support, and entropy mixing of new written data via `rnd_add_data()`.

Other tree operations:
- `sysctl_mmap()` forwards mmap-style requests only to nodes with `CTLFLAG_MMAP` and a handler.
- `sysctl_describe()` gets or sets node descriptions, with authorization and mutability checks, owned-description allocation, and packed `sysctldesc` copyout.
- `sysctl_free()` recursively frees a tree's owned data, descriptions, and child arrays.
- `old_sysctl()` bridges old in-kernel callers to the new dispatch path.

Kernel create/destroy convenience API:
- `sysctl_createv()` builds a node from varargs MIB components, calls `sysctl_create()`, treats compatible `EEXIST` as success, optionally returns the actual node pointer, logs dynamic nodes for later teardown, and attaches descriptions.
- `sysctl_destroyv()` locates and removes a node, treating missing nodes and non-empty parent nodes as successful cleanup cases.
- `sysctl_log_add()`, `sysctl_log_realloc()`, `sysctl_log_print()`, and `sysctl_teardown()` record dynamically created nodes in reverse-MIB form and remove them during module/device teardown.

Generic helpers and memory management:
- `sysctl_needfunc()` warns and returns static data for nodes that should have had a custom handler.
- `sysctl_notavail()` supports query but otherwise returns `EOPNOTSUPP`.
- `sysctl_null()` returns an empty result.
- `sysctl_map_flags()` translates flag words through a map table.
- `sysctl_alloc()` and `sysctl_realloc()` allocate and grow child-node arrays while maintaining parent pointers.

Address hashing:
- `hash_value_ensure_initialized()` initializes a secret 32-byte key once from `cprng_strong()`.
- `hash_value()` hashes arbitrary input with keyed BLAKE2s for address/value obfuscation users.

Concurrency and notes:
- The tree lock is global and intentionally simple; the file itself warns that holding it across allocations and copyout is problematic.
- Kernel-created dynamic nodes are not guaranteed stable by pointer for long after unlock unless the caller controls teardown.
- `sysctl_lookup()` may fault if a kernel-created node references later-invalid external data.
- Description privacy filtering contains a surprising negated kauth condition in the read loop; verify intended `kauth_authorize_system()` semantics before relying on it for private description visibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_sysctl.c -->