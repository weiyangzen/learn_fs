# Group Research: group_296_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_kern_kmalloc_c_sou_666b92f0cdde

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/dragonflybsd`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_kmalloc.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_kmalloc.c

## Purpose

`kern_kmalloc.c` implements DragonFlyBSD's type-stable `kmalloc_obj` allocator for fixed-size object zones. It uses `struct malloc_type` plus `struct kmalloc_mgt` state to provide per-type slab allocation, with slab memory returned cleanly when a zone is destroyed.

## Main Responsibilities

- Initializes and tears down per-type object allocation management with `malloc_mgt_init()` and `malloc_mgt_uninit()`.
- Allocates and frees fixed-size objects through `_kmalloc_obj()` and `_kfree_obj()`.
- Maintains per-CPU active and alternate slabs for fast allocation.
- Maintains per-type global partial, full, and empty slab lists.
- Maintains a per-CPU global free-slab cache to reduce kernel map churn.
- Retires fully free slabs gradually through `malloc_mgt_poll()`.
- Optionally checks double frees with a per-slab bitmap under `KMALLOC_CHECK_DOUBLE_FREE`.

## Core Data Model

Each slab is `KMALLOC_SLAB_SIZE` aligned and contains metadata plus a free-object ring in `fobjs[]`. The allocator tracks `aindex` for allocation consumption, `findex` for free-slot reservation, and `xindex` as a synchronizer showing the free-side object pointer has been stored. A slab's `type`, original CPU, object size, object count, object offset, magic, spinlock, and EXIS state describe its lifetime and safety status.

Each malloc type has per-CPU `ks_use[]` state with local `active` and `alternate` slabs. The type-wide `ks_mgt` holds shared `partial`, `full`, and `empty` lists plus counters. Fully free slabs can move into `gd_kmslab` per-CPU free-slab caches, while overflow is returned to `kmem_slab_free()`.

## Allocation Flow

`_kmalloc_obj()` first enforces the type limit using loose per-CPU memory accounting. It then enters a critical section and tries the current CPU's active slab, then alternate slab. If both are unavailable, it rotates a partial or full slab from the type-wide manager into the per-CPU active slot, sending the displaced alternate slab to the type empty list. If no existing slab has objects, it polls empty slabs and finally obtains a new slab from the CPU slab cache or `kmem_slab_alloc()`.

New slabs are zeroed as metadata, populated with fixed-size object addresses, marked with `KMALLOC_SLAB_MAGIC`, and rotated into the active slot. On success, per-CPU allocation counters and loose memory counters are updated, and `M_ZERO` is honored if requested.

## Free and Retirement Behavior

`_kfree_obj()` derives the owning slab by masking the object pointer, verifies the slab magic and that it is not already fully free, updates current-CPU statistics, reserves a free slot by atomically incrementing `findex`, stores the freed object in the ring, then increments `xindex` to complete publication.

Freed objects do not immediately move their slab between manager lists. Empty-list polling later classifies slabs as partial or full. `malloc_mgt_poll()` periodically moves fully free slabs from the full list into a retirement list when `xindex == findex` and `exis_freeable()` says the type-stability delay has elapsed. It caches as many retired slabs as possible and frees the rest.

## Concurrency Notes

Per-CPU active/alternate slabs are manipulated under a critical section on the local CPU. Type-wide slab lists are protected by `kmalloc_mgt.spin`. Global free-slab cache transfer uses atomic pointer swaps and compare/exchange, with `remote_free_slabs` only manipulated atomically. Free-side publication intentionally separates `findex` reservation from the object store and `xindex` synchronization.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_kmalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_kthread.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_kthread.c

## Purpose

`kern_kthread.c` provides small wrappers for creating, starting, exiting, and voluntarily suspending DragonFlyBSD lightweight kernel threads.

## Main Responsibilities

- Allocates unscheduled or scheduled LWKT kernel threads with `_kthread_create()`.
- Exposes `kthread_alloc()`, `kthread_create()`, and `kthread_create_cpu()`.
- Installs the target function through `cpu_set_thread_handler()` with `kthread_exit()` as the return path.
- Sets `td_comm` formatting for diagnostics and `ps`-visible names.
- Holds `proc0` credentials for created kernel threads.
- Starts SYSINIT-described kernel daemons with `kproc_start()`.
- Implements cooperative kernel-thread suspend and resume helpers.

## Behavior

`_kthread_create()` allocates a thread with `lwkt_alloc_thread()`, optionally pins it to a CPU, sets its handler and argument, formats its command name, inherits a held reference to `proc0.p_ucred`, and optionally schedules it immediately. `kproc_start()` creates the thread named by `struct kproc_desc`, raises it to `TDPRI_KERN_DAEMON`, and panics if creation fails.

## Suspension Model

`suspend_kproc()` only accepts kernel threads with no `td_proc`. It sets `TDF_MP_STOPREQ`, wakes the target, and waits until the target cooperatively clears the request. `kproc_suspend_loop()` is called by participating kernel threads in their main loop; it clears `STOPREQ`, sleeps until `TDF_MP_WAKEREQ`, then wakes the controller. A global `kpsus_token` serializes the protocol.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_kthread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_ktr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_ktr.c

## Purpose

`kern_ktr.c` implements the in-kernel KTR tracepoint facility: per-CPU ring buffers of low-overhead trace events used during boot, runtime diagnostics, optional timing tests, and DDB inspection.

## Main Responsibilities

- Defines boot and runtime KTR ring buffer sizing.
- Provides early boot trace storage for CPU 0 and migrates it after normal allocation is available.
- Allocates per-CPU trace buffers in `ktr_sysinit()`.
- Provides `ktr_begin_write_entry()` and `ktr_finish_write_entry()` for tracepoint writes.
- Optionally resynchronizes TSC offsets across CPUs through a periodic callout.
- Provides optional test logging, IPI ping-pong, critical-section, and spinlock overhead probes.
- Provides `show ktr` DDB output sorted by timestamp across CPUs.

## Core Data Model

`ktr_cpu[MAXCPU]` holds each CPU's `ktr_cpu_core`, including a trace buffer and monotonically increasing index. Writers use `ktr_idx & ktr_entries_mask` to select the next slot. Each `struct ktr_entry` records timestamp, tracepoint metadata, source file, source line, and optional caller stack information.

During early boot CPU 0 writes to `ktr_buf0`; `ktr_sysinit()` allocates full-size buffers for all CPUs and copies early CPU 0 entries into the new buffer. The exposed `debug.ktr.entries`, `debug.ktr.version`, `debug.ktr.stacktrace`, and test sysctls describe runtime state.

## Timestamp and Resync Behavior

If the architecture supports TSC, entries use `rdtsc() - tsc_offsets[cpu]`; otherwise they use approximate wall time. When `debug.ktr.resynchronize` is enabled, CPU 0 periodically uses an LWKT CPU sync callback to update per-CPU TSC offsets. The code deliberately uses a callout rather than a preemptive systimer to reduce the risk of deadlock while CPUs hold spinlocks or serializers.

## DDB Integration

The `show ktr` command supports verbose output, all-output mode, and per-CPU filtering. It walks each CPU's ring backwards and prints entries in decreasing timestamp order. The output includes CPU, ring index, optional timestamp/source location, tracepoint name, and caller addresses.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_ktr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_ktrace.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_ktrace.c

## Purpose

`kern_ktrace.c` implements process-level ktrace support. Unlike KTR's in-memory diagnostic tracepoints, this code writes user-visible trace records for syscalls, returns, path lookups, sysctls, I/O, signals, context switches, and `utrace()` data to a vnode-backed trace file.

## Main Responsibilities

- Builds `struct ktr_header` records with process, LWP, CPU, command, and threaded-state metadata.
- Emits trace payloads for `KTR_SYSCALL`, `KTR_SYSRET`, `KTR_NAMEI`, `KTR_SYSCTL`, `KTR_GENIO`, `KTR_PSIG`, `KTR_CSW`, and `KTR_USER`.
- Implements the `ktrace` syscall for setting, clearing, clearing-by-file, process-group targeting, and descendant targeting.
- Implements `utrace` for user-supplied trace payloads.
- Manages reference-counted `ktrace_node` objects wrapping trace vnodes.
- Enforces trace-control permissions through `ktrcanset()`.

## Trace Record Flow

Trace emitters set `KTRFAC_ACTIVE` to avoid recursive tracing, build a header with `ktrgetheader()`, attach a stack or temporary payload, and call `ktrwrite()`. `ktrwrite()` temporarily references the process trace node, constructs a header-plus-payload `uio`, takes an exclusive vnode lock, stamps the time after locking to avoid trace-file timestamp reversal, and writes with `IO_UNIT | IO_APPEND`. For `KTR_GENIO`, it writes the header and data `uio` as separate append operations.

If a write error occurs, tracing is stopped for all processes using the same trace node, and the kernel logs the failure.

## Control Operations

`sys_ktrace()` opens a regular trace file for set operations, or handles clear operations without one. Positive PIDs target one process; negative PIDs target a process group; `KTRFLAG_DESCEND` walks child processes through `ktrsetchildren()`. `KTROP_CLEARFILE` scans all processes and clears those using the same vnode. Trace-node references are inherited with `ktrinherit()` and dropped with `ktrdestroy()`.

## Security Notes

`ktrcanset()` allows tracing only when the caller is in the same prison and either root or an unprivileged caller whose real IDs match the target's real/saved IDs, the target is not marked root-traced, and the target is not `P_SUGID`. If root sets tracing, `KTRFAC_ROOT` is recorded so only root can later alter it.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_ktrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_linker.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_linker.c

## Purpose

`kern_linker.c` implements DragonFlyBSD's machine-independent kernel linker and KLD loader framework. It tracks loaded linker files, linker classes, module version providers, dependencies, sysinit/sysuninit execution, sysctl registration, symbol lookup, preloaded modules, disk search paths, and KLD-related syscalls.

## Main Responsibilities

- Initializes linker class and loaded-file lists.
- Registers linker classes with file-format-specific operations.
- Creates, finds, references, and unloads `linker_file` objects.
- Registers module metadata and sysctl sets found in linker files.
- Runs per-file `sysinit_set` in sorted order and `sysuninit_set` in reverse order.
- Resolves symbols from a file, its dependencies, and global loaded files.
- Allocates storage for unresolved common symbols.
- Implements `kldload`, `kldunload`, `kldfind`, `kldnext`, `kldstat`, `kldfirstmod`, and `kldsym`.
- Processes loader-preloaded files and resolves their dependency order.
- Searches `kern.module_path` for modules and loads dependencies for userland-initiated loads.

## Core Data Model

`classes` is the list of registered linker backends. `linker_files` is the global list of loaded linker files, protected by `llf_lock`. `kld_lock` serializes high-level KLD load/unload syscalls and is recursive. Each `linker_file` tracks filename, pathname, ID, refs, userrefs, flags, dependencies, common symbols, private backend state, modules, and backend ops.

`found_modules` maps provided module/interface names plus versions to the containing linker file. Despite the name, these entries represent version-provider tags from module metadata.

## Load and Unload Flow

`linker_load_file()` refuses loads when `securelevel > 0` or `kernel_mem_readonly` is set. If a file is already loaded, it increments `refs`; otherwise it asks each linker class to load the path. On success it registers modules, sysctls, runs sysinit functions, marks the file linked, and returns it.

`linker_file_unload()` refuses unloads under the same securelevel/read-only policy. It drops extra references cheaply. On final unload it lets each contained module veto via `MOD_UNLOAD`, removes provided-module records, runs SYSUNINITs and unregisters sysctls for linked files, unloads dependencies, frees common symbols, invokes backend unload, and removes the file from the global list.

## Symbol and Metadata Handling

`linker_file_lookup_symbol()` first queries the file backend. If a symbol looks like a common symbol, it records its size and searches dependencies and globals before allocating zeroed common storage in the file. DDB helpers provide unlocked cross-file symbol lookup and nearest-symbol search.

Module metadata is discovered from `modmetadata_set`/`MDT_SETNAME`. `linker_file_register_modules()` registers `MDT_MODULE` entries with the module subsystem. `linker_addmodules()` records `MDT_VERSION` providers in `found_modules`, and dependency checks use `MDT_DEPEND` plus `struct mod_depend` version bounds.

## Preload and Dependency Handling

`linker_preload()` scans loader metadata, asks linker classes to create preloaded files, records providers from the static kernel, then repeatedly moves preloaded files whose dependencies are satisfied into a dependency-ordered list. Unresolved files are unloaded. Resolved files depend on the kernel and on provider containers, run backend `preload_finish()`, register modules, add SYSINITs through `sysinit_add()`, register sysctls, and become linked.

`linker_load_dependencies()` handles userland KLD loads. It adds an implicit kernel dependency, rejects provider/version duplicates, resolves dependencies from already loaded providers or by loading missing modules, and finally records the new file's provided interfaces.

## User Interface and Security

KLD syscalls use `caps_priv_check_self(SYSCAP_NOKLD)` for load/unload, validate user structure versions, and copy names/pathnames/results to userland. `kern.module_path` is a semicolon-separated search path with `.ko` fallback. Loads and unloads are blocked once securelevel is raised or kernel memory is read-only.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_linker.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_lock.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_lock.c

## Purpose

`kern_lock.c` implements DragonFlyBSD's `lockmgr` shared/exclusive lock primitive. The implementation is largely encoded in an atomic `lk_count` word, with explicit support for shared locks, exclusive locks, recursion, upgrade/downgrade, cancellation, sleep interruption, timed waits, and diagnostic status reporting.

## Main Responsibilities

- Acquires shared locks with `lockmgr_shared()`.
- Acquires exclusive locks with `lockmgr_exclusive()`.
- Downgrades exclusive locks to shared with `lockmgr_downgrade()`.
- Upgrades shared locks to exclusive with `lockmgr_upgrade()`.
- Releases locks and grants pending requests with `lockmgr_release()`.
- Starts and ends cancellation of cancelable blocked/future waiters.
- Initializes, reinitializes, uninitializes, queries, and prints lock state.
- Provides SYSINIT support through `lock_sysinit()`.

## Core State Machine

`lk_count` encodes shared-holder count, exclusive-holder count, request bits, upgrade request, cancellation, and shared-grant state. `lk_lockholder` identifies the exclusive holder only; shared ownership is intentionally not tracked per thread. `LKC_EXREQ2` aggregates exclusive waiters that could not set `LKC_EXREQ` immediately and need a wakeup opportunity.

The code keeps shared and exclusive request interactions explicit: exclusive requests block new shared grants while a shared lock exists, upgrade requests have priority over normal exclusive requests in several grant paths, and shared requests can proceed once the `LKC_SHARED` grant bit is set.

## Acquisition and Upgrade Behavior

Shared acquisition permits recursive acquisition by the exclusive owner only if `LK_CANRECURSE` is set. Otherwise it bumps `LKC_SCOUNT`, waits until `LKC_SHARED` is set, and undoes the count on cancellation, nowait failure, or sleep failure.

Exclusive acquisition handles recursive exclusive counts, then either immediately grants the lock or sets `LKC_EXREQ`/`LKC_EXREQ2` and sleeps. If a blocked exclusive request is canceled or interrupted, `undo_exreq()` either removes the request or reports that the lock was granted before the undo completed.

Upgrade attempts immediately succeed when the caller is the only shared holder. Otherwise the caller drops its shared count and sets `LKC_UPREQ`. If another upgrade exists, non-exclusive upgrade falls back to release-plus-exclusive-acquire, while `LK_EXCLUPGRADE` and `LK_NOWAIT` fail.

## Release and Cancellation

`lockmgr_release()` never blocks. On last exclusive or shared release it grants pending upgrade or exclusive requests by transferring the final count into an exclusive count and waking the requester. Otherwise it clears counts, preconditions the unlocked state for shared acquisition, or delegates shared-count race handling to `undo_shreq()`.

`lockmgr_cancel_beg()` sets `LKC_CANCEL` while the lock is held and wakes pending waiters; only callers using `LK_CANCELABLE` observe cancellation as `ENOLCK`. `lockmgr_cancel_end()` clears the cancel bit.

## Safety and Diagnostics

`_lockmgr_assert()` panics if a potentially blocking operation is attempted from interrupt/IPI/hard code context. `lockstatus()`, `lockowned()`, and `lockmgr_printinfo()` provide caller-visible status. `lockuninit()` asserts no request bits remain and the shared state is consistent.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_lockf.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_lockf.c

## Purpose

`kern_lockf.c` implements advisory byte-range file locking for `fcntl`/`lockf` style POSIX locks and flock-style locks. It manages sorted locked ranges, blocked waiters, deadlock checks, per-UID POSIX lock accounting, and range structure caching.

## Main Responsibilities

- Converts `struct flock` requests into absolute `[start, end]` byte ranges.
- Implements `F_SETLK`, `F_UNLCK`, and `F_GETLK` through `lf_advlock()`.
- Adds, removes, clips, splits, merges, and downgrades lock ranges in `lf_setlock()`.
- Finds conflicting lock holders for `F_GETLK` through `lf_getlock()`.
- Sleeps and wakes blocked lock requests.
- Enforces `RLIMIT_POSIXLOCKS` and `maxposixlocksperuid` for POSIX locks.
- Provides a small two-entry per-CPU cache for `struct lockf_range`.

## Core Data Model

Each `struct lockf` lazily initializes two TAILQs: `lf_range` for active ranges sorted by `lf_start`, and `lf_blocked` for blocked waiters. Each `lockf_range` records owner process, lock type, flags, start, and end. `F_NOEND` represents open-ended locks by using `LLONG_MAX` internally.

The lock object is serialized by an LWKT pool token selected from the `struct lockf *`. This allows the code to modify range lists without per-list locks while still blocking safely.

## Lock Mutation Behavior

`lf_setlock()` preallocates two range objects before editing so it does not have to block mid-mutation. It scans active ranges to find the insertion point, overlapping ranges owned by the caller, and conflicting ranges owned by others. Conflicts either return `EAGAIN`, detect a simple POSIX deadlock as `EDEADLK`, or enqueue a blocked range and sleep.

When no owned overlapping range exists, new locks are inserted directly. Otherwise the function may insert a new requested range, split an existing owned range into two pieces, clip left or right edges, delete enclosed ranges into a temporary dead list, and merge adjacent same-owner same-type ranges. POSIX lock accounting is adjusted before mutation for worst-case growth and corrected after merge/delete.

## Wakeup and Accounting

Unlocks and write-to-read downgrades mark wakeups needed. `lf_wakeup()` scans blocked ranges and wakes all overlapping waiters, marking their `lf_flags` so sleepers know they were removed from the blocked list.

Per-UID accounting uses per-CPU deltas on both `uidinfo` and process-local UID counters. `lf_count_adjust()` moves process lock accounting when credentials change, while `lf_count_change()` checks limits for non-root users and updates counters.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_lockf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_memio.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_memio.c

## Purpose

`kern_memio.c` implements DragonFlyBSD's memory special devices and related ioctls: `/dev/mem`, `/dev/kmem`, `/dev/null`, `/dev/random`, `/dev/urandom`, `/dev/upmap`, `/dev/kpmap`, `/dev/lpmap`, `/dev/zero`, and `/dev/io`.

## Main Responsibilities

- Defines memory-device `dev_ops` variants for normal, memory, and non-quick devices.
- Enforces open-time privilege and securelevel checks for memory and I/O devices.
- Implements read/write behavior for physical memory, kernel memory, null, random, urandom, and zero devices.
- Implements user-kernel mapping support through `d_uksmap`.
- Implements memory range attribute ioctls through `mem_range_softc`.
- Implements random interrupt registration ioctls.
- Implements kqueue readiness filters.
- Creates all memory special devices at driver init.

## Device Behavior

`/dev/mem` maps the requested physical page into `ptvmmap`, performs `uiomove()`, and unmaps it. `/dev/kmem` checks mapped kernel address access with `kvm_access_check()` before moving directly to or from the kernel virtual address. `/dev/null` returns EOF on read and discards writes. `/dev/zero` returns zero-filled data and discards writes. `/dev/random` reads from `read_random(..., 0)` and permits seeding only when `kern.seedenable` is set and securelevel allows it. `/dev/urandom` reads with nonblocking random semantics and disallows writes.

`/dev/io` raises and clears I/O privilege level on open/close, and is blocked when securelevel is raised or kernel memory is read-only.

## Mapping Support

`memuksmap()` handles `UKSMAPOP_ADD`, `UKSMAPOP_REM`, and `UKSMAPOP_FAULT`. It tracks `/dev/lpmap` mappings on the owning LWP's `lwp_lpmap_backing_list`. Faults for `/dev/mem` map physical pages directly; `/dev/kmem` resolves kernel virtual addresses with `vtophys()`; `/dev/upmap`, `/dev/kpmap`, and `/dev/lpmap` delegate to `user_kernel_mapping()`.

`user_kernel_mapping()` creates or locates shared process, global kernel, or LWP mapping pages and returns their physical address. `/dev/upmap` has special `vfork()` handling: a child sharing the parent's pmap maps the parent's `p_upmap` and marks `invfork`.

## Ioctl and Event Notes

`mmioctl()` serializes ioctls with `mem_lock`. `MEMRANGE_GET` and `MEMRANGE_SET` copy descriptors through `mem_range_attr_get()` and `mem_range_attr_set()`. Random ioctls can register, unregister, or find interrupt randomness sources after restricted-root capability checks. Kqueue filters report memory devices as readable/writable, while `/dev/random` uses the random subsystem's read filter.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_memio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_mib.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_mib.c

## Purpose

`kern_mib.c` defines top-level sysctl namespaces and machine-independent kernel, hardware, user, security, compatibility, and debug MIB entries for DragonFlyBSD.

## Main Responsibilities

- Creates root sysctl nodes such as `kern`, `vm`, `vfs`, `net`, `debug`, `hw`, `machdep`, `user`, `p1003_1b`, `lwkt`, `compat`, and `security`.
- Exposes kernel identity, release, version, OS revision/date, static TLS extra space, process limits, POSIX constants, bootfile, CPU count, byte order, page size, platform, and architecture.
- Exposes hostname, securelevel, NIS domain name, and host ID.
- Publishes placeholder POSIX user-level constants expected by libc/userland interfaces.
- Publishes `debug.sizeof` entries for `vnode`, `proc`, and `cdev`.
- Creates the `kern.features` node for feature flags registered elsewhere.

## Custom Handlers

`sysctl_hostname()` uses `CTLFLAG_NOLOCK` to avoid per-OID locking on read and upgrades the sysctl lock only for writes. In jailed processes it reads or writes the prison hostname and enforces `PRISON_CAP_SYS_SET_HOSTNAME` for writes.

`sysctl_kern_securelvl()` allows securelevel to increase but rejects attempts to lower it with `EPERM`.

## Integration Notes

The file exports globals used elsewhere in this group: `kernelname`, `securelevel`, `kernel_mem_readonly`, `hostname`, `domainname`, and `hostid`. `kern_lockf.c` uses `maxposixlocksperuid`, while `kern_memio.c` and `kern_linker.c` consult `securelevel` and `kernel_mem_readonly`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_mib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_module.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_module.c

## Purpose

`kern_module.c` implements the kernel module registry layered below the KLD linker. It tracks module names, IDs, containing linker files, reference counts, event handlers, module-private data, and module enumeration/stat syscalls.

## Main Responsibilities

- Initializes the global module list and registers a shutdown event handler.
- Registers modules from `moduledata_t` metadata.
- Calls module event handlers for load, unload, and shutdown.
- Maintains module references and frees modules on final release.
- Looks modules up by name or ID.
- Links modules into both the global module list and the containing linker file's module list.
- Implements `modnext`, `modfnext`, `modstat`, and `modfind` syscalls.

## Data Model

Each `struct module` stores global-list linkage, per-linker-file linkage, containing file pointer, reference count, unique ID, name, event handler, handler argument, and `modspecific_t` data. Module IDs are assigned from `nextid`. The global module list is serialized by `mod_token` for syscall traversal and lookup.

## Lifecycle Behavior

`module_register()` rejects duplicate names, allocates a module plus inline name storage, initializes refs to 1, and links it to the container or `linker_current_file`. `module_register_init()` supports statically initialized modules by registering them against `linker_kernel_file` if necessary, then issuing `MOD_LOAD`; on load failure it unloads and releases the module.

`module_unload()` calls the module's `MOD_UNLOAD` event and lets the handler veto. `module_release()` removes the module from all lists and frees it when its reference count reaches zero. `module_shutdown()` sends `MOD_SHUTDOWN` to every registered module after sync during shutdown.

## Syscall Behavior

`modnext` iterates global module IDs, `modfnext` iterates modules inside a linker file, `modstat` copies name/ref/id and optional module-specific data to userland after checking structure version, and `modfind` resolves a copied-in module name to its ID.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_module.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_mpipe.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_mpipe.c

## Purpose

`kern_mpipe.c` implements `malloc_pipe`, a bounded preallocation/cache layer over `kmalloc()` for subsystems that need a nominal reserve, optional maximum growth, optional zeroing, optional interrupt-reserve allocation, and optional deferred callback notification when buffers become available.

## Main Responsibilities

- Initializes a pipe with nominal and maximum buffer counts in `mpipe_init()`.
- Preallocates nominal buffers and optional construct callbacks.
- Starts a support kernel thread when `MPF_CALLBACK` is enabled.
- Destroys a pipe and all cached buffers with `mpipe_done()`.
- Provides nonblocking, callback, wait-hint, and blocking allocation APIs.
- Returns buffers to the cache or frees overflow buffers with `mpipe_free()`.

## Core Data Model

`struct malloc_pipe` stores the malloc type, object size, flags, derived malloc flags, construct/deconstruct callbacks, nominal array capacity, maximum total capacity, current free count, current total count, callback queue, pending flag, support thread pointer, and LWKT token. The free array is LIFO and sized to the nominal count.

Queued callbacks are `struct mpipe_callback` objects containing function and two arguments. They are processed by the support thread only when cached buffers are available.

## Allocation and Free Behavior

`_mpipe_alloc_locked()` first consumes a cached free buffer. If the cache is empty and the maximum count is reached, or a previous malloc attempt failed in the wait loop, it returns `NULL`. Otherwise it attempts a nonblocking `kmalloc()` and constructs the new buffer on success.

`mpipe_alloc_nowait()` simply tries allocation under the token. `mpipe_alloc_callback()` queues a callback if two allocation attempts fail. `mpipe_wait()` waits until a future allocation is likely to succeed but does not guarantee it. `mpipe_alloc_waitok()` sleeps on the pipe until allocation succeeds.

`mpipe_free()` returns buffers to the LIFO array while space remains, optionally zeroing them unless cached data or no-zero flags are set. It wakes callback and allocation waiters as needed. If the nominal cache is full, it deconstructs and frees the buffer and decrements total count.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_mpipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_mutex.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_mutex.c

## Purpose

`kern_mutex.c` implements DragonFlyBSD's compact shared/exclusive mutex primitive. It provides faster, smaller persistent locks than `lockmgr`, supports blocking and asynchronous lock acquisition, exclusive recursion, shared acquisition, spinlock variants, downgrade, try-upgrade, queued wait links, and abortable requests.

## Main Responsibilities

- Acquires exclusive locks synchronously or asynchronously with `_mtx_lock_ex*()`.
- Acquires shared locks synchronously or asynchronously with `_mtx_lock_sh*()`.
- Provides exclusive spinlock and try-spinlock variants.
- Provides nonblocking exclusive/shared try-locks.
- Downgrades exclusive locks to shared and tries shared-to-exclusive upgrade.
- Releases locks and chains queued waiters in priority order.
- Waits for queued link completion with `mtx_wait_link()`.
- Removes or aborts queued lock requests with `mtx_delete_link()` and `mtx_abort_link()`.

## Core Data Model

`mtx_lock` is an atomic integer containing active count, exclusive bit, wanted bits, and `MTX_LINKSPIN`. `mtx_owner` tracks the exclusive owner. Exclusive waiters and shared waiters are held in circular doubly linked lists `mtx_exlink` and `mtx_shlink`, using caller-supplied `mtx_link_t` nodes. Link state records idle, linked-exclusive, linked-shared, acquired, called-back, or aborted status.

Exclusive waiters have priority over shared waiters to avoid shared-side starvation of exclusive acquisitions.

## Acquisition and Wait Behavior

Exclusive lock acquisition first handles unlocked and recursive-exclusive fast paths. On conflict it obtains `MTX_LINKSPIN`, sets `MTX_EXWANTED`, links the request, and either returns `EINPROGRESS` for async links or blocks in `mtx_wait_link()`.

Shared lock acquisition succeeds immediately when the mutex is not exclusive and no exclusive waiter is pending. Otherwise it links on the shared queue under `MTX_LINKSPIN`, sets `MTX_SHWANTED`, and either returns asynchronously or waits.

`mtx_wait_link()` sleeps on the link until the state changes, integrates indefinite-wait diagnostics unless disabled, uses memory fences so post-acquire loads see the releasing CPU's stores, removes still-linked requests after sleep errors, maps aborts to `ENOLCK`, and resets link state to idle.

## Release, Chaining, and Abort

`_mtx_unlock()` handles final and non-final shared/exclusive releases. On final release it grants queued exclusive requests before shared requests. `mtx_chain_link_ex()` transfers the active count to one exclusive waiter, sets `mtx_owner`, and wakes or calls back that waiter. `mtx_chain_link_sh()` grants all queued shared waiters at once, pre-adjusting the active count for the number of shared links.

`mtx_abort_link()` can abort an idle future request or a linked active request. For linked async requests it calls the callback with `ENOLCK`; for synchronous requests it marks aborted and wakes the sleeper. If the lock was already acquired or callback already made, abort is too late and does not revoke the acquisition.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_mutex.c -->