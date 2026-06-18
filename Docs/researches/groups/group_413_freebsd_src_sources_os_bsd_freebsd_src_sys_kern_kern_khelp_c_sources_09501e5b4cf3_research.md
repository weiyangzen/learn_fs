# Group Research: group_413_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_kern_khelp_c_sources_09501e5b4cf3

Complete source read for the nine files listed in `Docs/research_subset_a.md`; total source lines verified: 10,187.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_khelp.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_khelp.c

## Purpose
Implements the FreeBSD kernel helper framework (`khelp`), which lets loadable helper modules register hook callbacks and optional per-object OSD storage. It bridges helper modules with the `hhook` framework and `osd(9)` storage.

## Key Interfaces
- `khelp_register_helper()` / `khelp_deregister_helper()` add and remove helper modules.
- `khelp_init_osd()` / `khelp_destroy_osd()` allocate and release helper-specific OSD payloads.
- `khelp_get_osd()` and `khelp_get_id()` expose helper storage and helper lookup.
- `khelp_add_hhook()` / `khelp_remove_hhook()` wrap `hhook` hook management.
- `khelp_new_hhook_registered()` attaches registered helpers to hook points created later.
- `khelp_modevent()` is the module event entry point for load, quiesce, shutdown, and unload.

## State And Locking
Global helper state is a descending-`h_id` `TAILQ` guarded by `khelp_list_lock`. Each helper has an OSD id, refcount, hook list, class mask, flags, optional UMA zone, and optional module init/destroy callbacks.

## Control Flow
Module load optionally creates a UMA zone for helpers needing OSD, fills helper metadata, runs module init, then registers hooks and list membership. OSD initialization walks matching helpers, allocates per-helper storage with `M_NOWAIT`, and rolls back partial allocation on failure. Deregistration refuses helpers with nonzero OSD refcount and then removes hooks and OSD ids.

## Integration Notes
Depends on `hhook`, `osd`, `uma`, module events, rwlocks, and refcounts. The sorted helper list is intentionally used to make `osd_set()` allocation behavior more efficient.

## Risks
Unload safety depends on accurate OSD refcounting. OSD allocation is nonblocking and may fail, so callers must handle `ENOMEM`. `khelp_add_hhook()` and `khelp_remove_hhook()` do not update the helper's stored hook array, as noted by in-file comments.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_khelp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_kthread.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_kthread.c

## Purpose
Provides FreeBSD kernel process and kernel thread creation, exit, suspend, resume, and combined process/thread helper routines.

## Key Interfaces
- `kproc_start()` starts SYSINIT-described kernel processes.
- `kproc_create()` creates a kernel process via `fork1()` using `RFMEM | RFFDG | RFPROC | RFSTOPPED`.
- `kproc_exit()` reparents the process to init and exits through `exit1()`.
- `kproc_suspend()`, `kproc_resume()`, and `kproc_suspend_check()` implement voluntary process suspension.
- `kthread_start()` and `kthread_add()` create kernel threads, usually under `proc0` or a provided process.
- `kthread_exit()` tears down a kernel thread and exits the process if it is the last thread.
- `kthread_suspend()`, `kthread_resume()`, and `kthread_suspend_check()` implement voluntary thread suspension.
- `kproc_kthread_add()` creates a process on first call, then adds later threads to it.

## State And Locking
Uses process locks, thread locks, proctree lock, tid hash, cpuset kernel-thread affinity, scheduler primitives, and optional HWPMC/KTR hooks. Suspension uses `p_siglist` for kprocs and `TDF_KTH_SUSP` for kthreads.

## Control Flow
Kernel processes are forked stopped, named, assigned a kernel start handler, moved to kernel cpuset policy, priority-adjusted, then scheduled unless `RFSTOPPED` is requested. Kernel threads are allocated, initialized from an existing thread template, linked into the process, added to tidhash, and scheduled. Exit paths wake waiters before dropping into process/thread teardown.

## Integration Notes
Central utility for internal kernel daemons created by SYSINIT and for subsystems that need background kernel execution contexts.

## Risks
`kthread_add1()` returns `ESRCH` if the target process is exiting after allocating `newtd`; this code path relies on surrounding thread allocation semantics and should be checked carefully if modified. Suspension is cooperative; target main loops must call the corresponding check routines.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_kthread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_ktr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_ktr.c

## Purpose
Implements global state and the tracepoint write path for FreeBSD's low-level KTR kernel tracing facility.

## Key Interfaces
- Global exported state: `ktr_idx`, `ktr_mask`, `ktr_compile`, `ktr_entries`, `ktr_version`, `ktr_buf`, and `ktr_cpumask`.
- Sysctls under `debug.ktr`: `version`, `compile`, `cpumask`, `clear`, `mask`, `entries`, and optional ALQ controls.
- `ktr_tracepoint()` records a KTR event.
- DDB `show ktr` support dumps the circular trace buffer.

## State And Locking
KTR uses a circular array of `struct ktr_entry`. Writers reserve slots with atomic compare-and-set on `ktr_idx`. Runtime resizing disables tracing, quiesces CPUs, swaps buffers, and frees the old buffer. CPU filtering is controlled by `ktr_cpumask`.

## Control Flow
A tracepoint returns early during panic/debugger activity, disabled masks, null buffer, or filtered CPU. It prevents recursion with `TDP_INKTR` when verbose or ALQ logging is enabled. Events are written either to the in-memory ring or optional ALQ output. Each record stores timestamp, CPU, thread pointer, source file/line, format string, and up to six parameters.

## Integration Notes
Uses sysctl, cpuset parsing, `get_cyclecount()`, optional ALQ, optional DDB, and optional SMP CPU labeling. Boot-time `KTR_ENTRIES > KTR_BOOT_ENTRIES` migration preserves early entries.

## Risks
Trace records keep pointers to format strings and file strings rather than copying them. Sysctl buffer clearing and resizing are intentionally coarse and can race with concurrent tracing except for the quiesce/disable sequence in resizing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_ktr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_ktrace.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_ktrace.c

## Purpose
Implements user-visible process tracing for `ktrace(2)` and `utrace(2)`, recording syscalls, returns, namei paths, genio data, signals, context switches, capability failures, faults, proc ctor/dtor events, structured records, sysctl names, arguments, environments, and extended errors.

## Key Interfaces
- Event emitters include `ktrsyscall()`, `ktrsysret()`, `ktrnamei()`, `ktrsysctl()`, `ktrgenio()`, `ktrpsig()`, `ktrcsw()`, `ktrstruct()`, `ktrstructarray()`, `ktrcapfail()`, `ktrfault()`, `ktrfaultend()`, and `ktrexterr()`.
- Process lifecycle hooks: `ktrprocexec()`, `ktrprocexit()`, `ktrprocctor()`, `ktrprocfork()`, and `ktruserret()`.
- Syscalls: `sys_ktrace()` and `sys_utrace()`.
- `ktr_get_tracevp()` exposes the trace vnode under process lock.

## State And Locking
`ktrace_mtx` protects the request free list, `p_traceflag`, `p_ktrioparms`, queued requests, and IO parameter refcounts. `ktrace_sx` serializes draining/writing. `TDP_INKTRACE` suppresses recursive tracing. Each traced process references `struct ktr_io_params`, containing vnode, credential, file-size limit, and refcount.

## Control Flow
Trace event generation allocates a `ktr_request` from a bounded pool, fills a versioned header, attaches fixed data and optional payload, then either writes immediately through VFS or queues to the process pending list for AST/user-return draining. `sys_ktrace()` opens and validates the trace file, then applies set/clear/clearfile operations to a pid, process group, or descendants. Writes append header, fixed type data, and dynamic payload with `VOP_WRITE`; on write failure tracing is disabled for that process.

## Integration Notes
Uses VFS, MAC checks, Capsicum capability failure reporting, process/proctree locks, AST callbacks, resource limits, credentials, and extended error conversion.

## Risks
Request pool exhaustion marks dropped records and emits only one warning until resized. Ordering across processes/threads writing the same vnode is explicitly weak. Permission and credential behavior is subtle: setuid exec disables tracing unless trace credentials have `PRIV_DEBUG_DIFFCRED`, and root-set traces carry `KTRFAC_ROOT`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_ktrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_linker.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_linker.c

## Purpose
Implements the FreeBSD kernel linker/KLD manager: class registration, module load/unload, preload finalization, dependency resolution, sysinit/sysuninit execution, sysctl registration, symbol lookup, CTF loading, and user syscalls such as `kldload`, `kldunload`, `kldfind`, `kldnext`, `kldstat`, `kldfirstmod`, and `kldsym`.

## Key Interfaces
- Linker class and file lifecycle: `linker_add_class()`, `linker_make_file()`, `linker_file_unload()`, `linker_load_dependencies()`.
- Module ref APIs: `linker_reference_module()` and `linker_release_module()`.
- Symbol APIs: `linker_file_lookup_symbol()`, DDB helpers, and `linker_search_symbol_name[_flags]()`.
- KLD syscalls: `kern_kldload()`, `sys_kldload()`, `kern_kldunload()`, `sys_kldunload[f]()`, `sys_kldfind()`, `sys_kldnext()`, `sys_kldstat()`, `sys_kldfirstmod()`, `sys_kldsym()`.
- Function-name export sysctl: `kern.function_list`.

## State And Locking
Global linker state is guarded by `kld_sx`: classes, loaded files, ids, found module/version records, dependencies, load counter, and `kld_busy` serialization. File objects track refs, userrefs, flags, modules, dependencies, common symbols, load count, paths, address, size, and class-specific operations.

## Control Flow
Runtime load checks privilege and securelevel, serializes through `linker_kldload_busy()`, resolves a path or module name through `linker.hints` and `module_path`, invokes class-specific loading, registers module metadata and sysctls, propagates vnets, runs SYSINITs, loads CTF, and fires kld eventhandlers. Unload quiesces modules, runs module unload callbacks, unregisters sysctls, runs SYSUNINITs, releases dependencies, frees common symbols, and deletes the linker object.

## Integration Notes
Preload support scans loader metadata, topologically orders dependencies, finalizes relocation, registers sysinits and modules, and later assigns userrefs for unloadable preloaded files. Symbol lookup supports commons and the special `__this_linker_file` symbol used by LinuxKPI.

## Risks
Loading is disabled above securelevel 0. DDB lookup intentionally avoids normal locking. Hints parsing trusts bounded file size but still manually walks packed records. Dependency/version handling rejects duplicate or incompatible module versions and may force-unload partially linked files.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_linker.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_lock.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_lock.c

## Purpose
Implements FreeBSD `lockmgr` locks: sleepable shared/exclusive/upgradable locks used heavily by vnode and buffer code.

## Key Interfaces
- Initialization and teardown: `lockinit()`, `lockdestroy()`.
- Policy mutation: `lockallowshare()`, `lockdisableshare()`, `lockallowrecurse()`, `lockdisablerecurse()`.
- Fast entry points: `lockmgr_slock()`, `lockmgr_xlock()`, `lockmgr_unlock()`.
- General entry point: `lockmgr_lock_flags()` and `__lockmgr_args()`.
- State helpers: `_lockmgr_disown()`, `lockmgr_printinfo()`, `lockstatus()`, `_lockmgr_assert()`.
- DDB support: `lockmgr_chain()` and `db_show_lockmgr()`.

## State And Locking
The lock word encodes unlocked, shared count, exclusive owner, waiters, spinners, recursed writer, and disowned `LK_KERNPROC` state. Sleep queues have separate shared and exclusive queues. Thread counters track total locks and shared lockmgr locks. Optional DEBUG_LOCKS stores a stack.

## Control Flow
Shared and exclusive acquisition first try atomic fast paths. Hard paths perform WITNESS order checks, optional adaptive spinning on running exclusive owners, waiters-bit setup, sleepqueue sleeps with timeout/signal handling, Giant save/restore, lock profiling, lockstat probes, and PMC soft events. Release paths prefer exclusive waiters, handle `LK_SLEEPFAIL`, broadcast the selected queue, and preserve waiter bits when required. Upgrade, try-upgrade, downgrade, drain, recurse, and disown are handled as explicit state transitions.

## Integration Notes
Defines `lock_class_lockmgr` for the kernel lock class system, but generic sleep interlocking methods intentionally panic because lockmgr has specialized entry points.

## Risks
This is a delicate atomic state machine. Correctness depends on preserving waiter bits, synchronizing with sleepqueue locks, and maintaining priority rules between exclusive and shared waiters. Recursing non-recursive locks, draining while held, or downgrading recursed locks panics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_lockf.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_lockf.c

## Purpose
Implements advisory byte-range locking for vnode operations, covering POSIX `fcntl` locks, BSD `flock` locks, remote locks, async lock requests, deadlock detection, lock reporting, and remote-system cleanup.

## Key Interfaces
- `lf_advlockasync()` is the primary async lock operation handler.
- `lf_advlock()` adapts synchronous VOP advlock requests.
- `lf_purgelocks()` clears all locks for a doomed vnode.
- `lf_clearremotesys()` and `lf_countlocks()` manage remote lock owners by system id.
- `lf_iteratelocks_sysid()` and `lf_iteratelocks_vnode()` iterate locks for cleanup.
- `vfs_report_lockf()` and `sysctl kern.lockf` export lock state.

## State And Locking
Each vnode can reference a `struct lockf` state with active and pending lists guarded by `ls_lock`. Global `lf_lock_states` is guarded by `lf_lock_states_lock`. Lock owners are hashed across 256 sx-protected chains. A global owner graph guarded by `lf_owner_graph_lock` tracks wait-for dependencies and uses dynamic topological sorting to reject cycles.

## Control Flow
Requests convert `flock` offsets into inclusive `[start,end]` ranges, create or find a lock owner, allocate a lock entry, create vnode state as needed, and dispatch set/unlock/get/cancel. Set-lock scans active locks for blockers. Blocking synchronous requests sleep on the lock entry; async requests return `EINPROGRESS` and a cookie. Unlock and same-owner lock changes use overlap classification to remove, shrink, split, or replace active locks, waking newly unblocked pending locks.

## Deadlock Handling
Per-vnode lock edges represent pending locks blocked by active or older pending locks. The global owner graph maps those edges to owner-to-owner waits. `graph_add_edge()` maintains topological order using forward/backward delta sets and returns `EDEADLK` if adding an edge would create a cycle.

## Risks
Correctness depends on keeping vnode active lists sorted, edge lists synchronized with the owner graph, and references balanced for remote vnode locks. `EDOOFUS` is used internally to retry after a sleeping lock object was consumed. Async cancel uses the lock pointer as a cookie and validates vnode/range before cancellation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_lockf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_lockstat.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_lockstat.c

## Purpose
Defines FreeBSD lockstat SDT probes and a timestamp helper used by lock instrumentation.

## Key Interfaces
- SDT provider: `lockstat`.
- Probe groups cover adaptive mutexes, spin mutexes, rwlocks, sx locks, lockmgr locks, and thread spinning.
- `lockstat_nsecs()` returns a nanosecond timestamp for profiling when lockstat is enabled.

## State And Locking
The only mutable state is `volatile bool __read_frequently lockstat_enabled`. No local locks are used.

## Control Flow
`lockstat_nsecs()` returns zero if lockstat is disabled or the lock object has `LO_NOPROFILE`. Otherwise it calls `binuptime()` and converts `bintime` to nanoseconds.

## Integration Notes
Probe names match kernel locking subsystems, for example `lockmgr__block`, `rw__upgrade`, and `sx__downgrade`. Other lock implementations record against these probes via lockstat macros.

## Risks
The timestamp conversion is intentionally lightweight but approximate to nanoseconds from `bintime`. Callers must treat zero as disabled/no-profile rather than an actual timestamp.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_lockstat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_loginclass.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_loginclass.c

## Purpose
Maintains login class objects and implements `setloginclass(2)` and `getloginclass(2)`. Login classes are attached to credentials and used by RACCT/RCTL for per-class resource accounting and limits.

## Key Interfaces
- `loginclass_hold()` and `loginclass_free()` manage refcounts.
- `loginclass_find()` returns an existing or newly created class by name.
- `sys_getloginclass()` copies the current credential login class name to userspace.
- `sys_setloginclass()` replaces the process credential login class after privilege checks.
- `loginclass_racct_foreach()` iterates login class RACCT objects under the list lock.

## State And Locking
Global `loginclasses` is protected by `loginclasses_lock`. Each `struct loginclass` has a name, refcount, RACCT pointer, and list linkage. Allocation is race-safe: lookup is retried under write lock after memory allocation to avoid duplicate class insertion.

## Control Flow
Lookup first checks the current credential's class, then scans the global list, then allocates a new class and inserts it if still absent. `setloginclass` checks `PRIV_PROC_SETLOGINCLASS`, copies the requested name, resolves the class, creates a new credential, swaps it into the process, updates RACCT/RCTL state when compiled in, and releases the old credential and old login class.

## Integration Notes
Depends on credentials, process locking, privilege checks, RACCT, RCTL, refcounts, and rwlocks. Empty names and names at least `MAXLOGNAME` are rejected.

## Risks
Credential replacement has distinct RACCT and RCTL hooks; changes here must preserve reference ownership around `proc_set_cred()`. `loginclass_free()` uses a fast refcount release path and then a locked last-reference path to safely remove classes from the global list.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_loginclass.c -->