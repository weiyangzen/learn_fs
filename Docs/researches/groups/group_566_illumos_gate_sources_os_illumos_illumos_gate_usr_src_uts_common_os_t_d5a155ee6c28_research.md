# Group Research: group_566_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_t_d5a155ee6c28

Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`. All source files listed for this group were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/timers.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/timers.c

Implements kernel time-of-day helpers, legacy interval timer syscalls, high-resolution time conversions, `nanosleep()`, and UTC/TOD conversion utilities.

Key responsibilities:
- Provides monotonically increasing timestamp generation via `uniqtime()` and 32-bit ABI conversion through `uniqtime32()`.
- Implements `gettimeofday()`, `getitimer()`, `setitimer()`, `xgetitimer()`, and `xsetitimer()` for native and 32-bit data models.
- Manages `ITIMER_REAL` through timeout callbacks, `ITIMER_VIRTUAL` and `ITIMER_PROF` in per-LWP timer state, and `ITIMER_REALPROF` through cyclic timers.
- Provides `itimerfix()`, `itimerspecfix()`, `itimerdecr()`, timeval/timespec add/sub/fix helpers, tick conversion helpers, and hrtime/timeval/timespec conversion helpers.
- Implements `nanosleep()` with signal-interruptible `cv_waituntil_sig()` and optional remaining-time copyout.
- Converts between Unix UTC seconds and `todinfo_t` calendar fields, caching the last UTC/TOD conversion under `tod_lock`.

Important paths:
- `uniqtime()` uses `gethrestime()`, protects cached last timestamp with `tod_lock`, and increments microseconds when needed to preserve uniqueness after small backward or equal time observations.
- `xsetitimer(ITIMER_REAL)` serializes concurrent callers with `SITBUSY`, cancels existing timeout IDs outside `p_lock`, stores an absolute fire time, and schedules `realitexpire()`.
- `realitexpire()` posts `SIGALRM`, clears one-shot timers, or advances periodic timers past current time before rescheduling.
- `xsetitimer(ITIMER_REALPROF)` removes any prior cyclic under `cpu_lock`, creates a low-level cyclic, cancels per-LWP `ITIMER_PROF`, and allocates per-thread `struct rprof` buffers opportunistically.
- `realprofexpire()` samples every LWP's microstate, increments real profiling state counters, marks ASTs, and pokes remote CPUs running target threads.
- `delete_itimer_realprof()` removes real profiling timers and pending/current `SIGPROF` state during exec.
- `timespectohz()` and `timespectohz64()` convert absolute or relative times to ticks with nonpositive and overflow protection.
- `hrt2ts()`, `ts2hrt()`, and `hrt2tv()` use optimized arithmetic on non-x86 paths and straightforward division/multiplication on modern x86 paths.

Locking and lifetime:
- `tod_lock` protects time-of-day conversion cache state and `uniqtime()`'s last timestamp.
- Process interval timer state is protected by `p_lock`; `xsetitimer()` deliberately drops it around `untimeout()` and cyclic operations.
- `cpu_lock` protects cyclic add/remove for `ITIMER_REALPROF`.
- `t_delay_lock` protects `nanosleep()` condition-variable waits.

Filesystem relevance:
- This is kernel timing infrastructure rather than filesystem code, but VFS, filesystem, block, and VM paths depend on these conversions, sleeps, timeouts, and timestamp helpers for I/O deadlines, attribute times, delay scheduling, and interruptible waits.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/timers.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/tlabel.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/tlabel.c

Implements Trusted Extensions label allocation/refcounting and file-label resolution for local, loopback, ZFS, and NFS filesystems.

Key responsibilities:
- Initializes global label state in `label_init()`, including the `tslabel_cache`, `l_admin_low`, and `l_admin_high`.
- Allocates, duplicates, holds, releases, compares, and extracts DOI/basic-label data from `ts_label_t`.
- Resolves a file's effective label through vnode, VFS, zone, ZFS dataset, NFS server, CIPSO, and lofs export context.
- Exposes `getlabel()` and `fgetlabel()` syscall helpers that copy a file label to userland.

Important paths:
- `getflabel_cipso()` infers a remote CIPSO NFS resource label by matching exported NFS resource paths to local zones, relying on TX convention that zone names and paths match between server and client.
- `getflabel_zfs()` reads the ZFS `mlslabel` dataset property with `dsl_prop_get()`, ignores the default property value, converts a hex label, and returns a new `ts_label_t`.
- `getflabel_nfs()` looks up the NFS server transport endpoint in the trusted-network database, delegates CIPSO peers to `getflabel_cipso()`, and uses the peer default label for unlabeled hosts.
- `getflabel()` unwraps real vnodes with `VOP_REALVP()`, handles NFS first, fast-paths non-global-zone non-lofs files to the zone label, falls back to path-based zone lookup, checks ZFS explicit labels, and distinguishes global-zone admin-high files from admin-low files exported into non-global zones through lofs.
- `cgetlabel()`, `getlabel()`, and `fgetlabel()` are the user-visible copyout wrappers around `getflabel()`.

Locking and lifetime:
- `ts_label_t` lifetime is atomic reference-counted.
- VFS resources and mountpoint strings are held through `refstr_t`; VFS structures are held only when their mountpoint can safely be referenced.
- Zone references are acquired with `zone_hold()` / `zone_find_by_any_path()` and released with `zone_rele()`.
- The global VFS list is protected with `vfs_list_read_lock()` while scanning lofs exports.

Filesystem relevance:
- This file is directly VFS-facing. It determines security labels for file objects by combining vnode identity, filesystem type names in `vfssw`, mount resources, ZFS properties, NFS server trust metadata, loopback mounts, and zone path ownership.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/tlabel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/turnstile.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/turnstile.c

Implements turnstiles: the kernel blocking, wakeup, and priority-inheritance mechanism used by synchronization primitives such as mutexes, rwlocks, and user priority-inheritance locks.

Key responsibilities:
- Maintains a global hash table mapping synchronization-object addresses to active turnstiles.
- Lets the first waiter donate its per-thread turnstile and later waiters chain their turnstiles on the active turnstile freelist.
- Tracks reader and writer sleep queues per turnstile.
- Walks blocking chains to propagate priority inheritance and prevent unbounded priority inversion.
- Supports direct handoff wakeups where a woken thread inherits priority before it runs.
- Provides special interruptible behavior for `SOBJ_USER_PI` locks.

Important paths:
- `turnstile_lookup()` locks the hash bucket and returns the active turnstile for a synchronization object.
- `turnstile_block()` installs or joins an active turnstile, marks the thread sleeping, inserts it into the selected sleep queue, walks owners to apply priority inheritance, handles user-PI cycles as `EDEADLK`, and switches away.
- `turnstile_interlock()` handles difficult lock ordering when both waiter and owner locks are turnstile locks, using address order and a loser lock to avoid deadlock and livelock.
- `turnstile_wakeup()` waives inherited priority from the releasing owner, dequeues one or more waiters, performs scheduler-class wakeups, and applies inheritance to a direct-handoff owner when applicable.
- `turnstile_dequeue()` removes a waiter, returns or reassigns turnstile structures, removes inactive turnstiles from the hash chain, and clears thread wait-channel state.
- `turnstile_unsleep()` supports interrupting user-PI waiters without immediate disinherit; owners must later call `turnstile_pi_recalc()`.

Locking and invariants:
- Each turnstile hash bucket has a dispatcher lock that also protects the waiters bits of synchronization objects hashing to that bucket.
- Clients may manipulate waiters indicators and certain owner transitions only while under `turnstile_lookup()`.
- The implementation assumes clients never block on unheld locks.
- User-PI locks require special handling because an `upimutextab[]` lock is held until the thread has blocked and willed priority.

Filesystem relevance:
- Filesystems do not generally call this file directly, but mutexes and rwlocks used throughout VFS, vnode, VM, page-cache, and storage code depend on turnstiles for blocking correctness and priority inheritance under contention.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/turnstile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/unix_bb.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/unix_bb.c

Provides optional kernel basic-block coverage registration hooks when built with `KCOV`.

Key responsibilities:
- Maintains the global `unix_bb_list` of `bb_info` records and `unix_bb_lock`.
- Defines `__bb_init_func()`, the compiler-emitted basic-block initialization hook, under `KCOV`.
- Optionally tracks test counters and last caller metadata under `KCOV_TEST`.

Behavior:
- Raises PIL with `spl8()` and tries to acquire `unix_bb_lock`.
- If the lock is unavailable on an interrupt stack, returns to avoid possible NMI-level deadlock.
- Otherwise uses `lock_set_spl()` when needed and links an uninitialized `bb_info` into `unix_bb_list`.
- Avoids ordinary C helper calls in the hook because it can be invoked from arbitrary C routines and could recurse.

Filesystem relevance:
- No direct filesystem behavior. It is kernel instrumentation infrastructure that could include filesystem object files when coverage is enabled.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/unix_bb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/upanic.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/upanic.c

Implements `upanic()`, a user-process abort path intended to force a core dump with a small user-supplied panic message stored in procfs/core metadata.

Key responsibilities:
- Marks the current LWP as taking `SIGABRT`.
- Stops other LWPs with `proc_is_exiting()` and `exitlwps()`.
- Copies up to `PRUPANIC_BUFLEN` bytes of user message data into kernel memory.
- Sets `p_upanic` and `p_upanicflag` bits describing message presence, truncation, invalid copyin, and panic state.
- Coordinates audit events around the core dump when auditing is enabled.
- Calls `core(SIGABRT, B_FALSE)` and exits as `CLD_DUMPED` or `CLD_KILLED`.

Important details:
- The message buffer is zero-filled and truncated at the fixed procfs upanic buffer length.
- Copyin failure clears the have-message flag and records invalid-message state.
- `p_lock` protects current signal and process upanic fields.

Filesystem relevance:
- This is process/core-dump plumbing. It intersects filesystem behavior through `core()`, which writes a core file using the normal kernel core dump and vnode/filesystem path, and through procfs exposure of upanic state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/upanic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/urw.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/urw.c

Implements safe kernel reads and writes of another process's user address space through `uread()` and `uwrite()`.

Key responsibilities:
- Validates whether a target user page is meaningful and backed by real data.
- Temporarily adjusts protections when necessary.
- Soft-locks the target page, maps it into kernel virtual address space, copies data, and soft-unlocks it.
- Handles ordinary memory pages, device mappings, ISM shared segments, `MAP_NORESERVE` segvn pages, and `/dev/null` style segdev mappings.

Important paths:
- `page_valid()` rejects file mappings beyond EOF, addresses outside real ISM shared segment size, `/dev/null` segdev mappings, and unmaterialized `MAP_NORESERVE` anonymous pages.
- `mapin()` uses `hat_getpfnum()` and `ppmapin()` for normal memory pages with page structures; otherwise it allocates heap virtual space and maps device PFNs with `hat_devload()`.
- `urw()` locks the address space as writer, finds the segment, optionally expands protection with `SEGOP_SETPROT()`, soft-faults the page with `F_SOFTLOCK`, copies under `on_trap(OT_DATA_EC)`, syncs I-cache for executable writes, soft-unlocks, restores protection, and drops the address-space lock.
- `uread()` and `uwrite()` are thin wrappers selecting read or write mode.

Locking and fault behavior:
- Uses `AS_LOCK_ENTER(as, RW_WRITER)` to stabilize mappings and avoid copy-on-write races during read softlocks.
- Uses `S_READ_NOCOW` for segvn reads so soft-locking does not unnecessarily break sharing.
- Converts corrupt-memory traps to `EIO` and unmapped/invalid cases to `ENXIO`.

Filesystem relevance:
- It validates vnode-backed mappings against file size and VOP attributes, so it is relevant to `/proc`, debugging, and core/memory inspection paths that read or modify process memory mapped from files or devices.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/urw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vers.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vers.c

Defines the kernel `utsname` template.

Contents:
- Includes `sys/utsname.h`.
- Initializes global `struct utsname utsname` with `"SunOS"`, an empty nodename slot, and build-provided `UTS_RELEASE`, `UTS_VERSION`, and `UTS_PLATFORM`.

Filesystem relevance:
- No direct filesystem logic. The values can appear in system identity queries and diagnostics that accompany filesystem and kernel reports.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vers.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vfs_conf.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vfs_conf.c

Defines the static VFS switch table for built-in filesystem type names and initialization hooks.

Key responsibilities:
- Provides `vfssw[]`, the filesystem switch array indexed by filesystem type number.
- Reserves stable positions for built-in filesystems including `specfs`, `ufs`, `fifofs`, `namefs`, `proc`, `nfs`, `zfs`, `hsfs`, `lofs`, `tmpfs`, `pcfs`, `swapfs`, `devfs`, `ctfs`, `objfs`, `sharefs`, `dcfs`, and `smbfs`.
- Installs `swapinit` as the initialization hook for `swapfs`.
- Exports `nfstype` as the array length.

Important invariant:
- The file warns that entry positions must not be changed because many filesystems pass the filesystem type number into `vfs_make_fsid()`. Reordering can change NFS file handles after a server upgrade and cause clients to see stale file handles.

Filesystem relevance:
- Directly VFS-facing. This table ties filesystem names to type numbers and therefore affects mount behavior, filesystem IDs, exported file handles, and code such as label resolution that consults `vfssw[fstype].vsw_name`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vfs_conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vm_meter.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vm_meter.c

Implements once-per-second VM paging and free-memory metering used by the swapper and pageout policy.

Key responsibilities:
- Updates 5-second and 30-second exponentially smoothed free-memory averages (`avefree`, `avefree30`).
- Aggregates per-CPU page-in and page-out counters and updates 5-second `pginrate` and `pgoutrate`.
- Decays the global `deficit` estimate when pageout is active.

Important details:
- Uses the `ave()` macro for fixed-window smoothing.
- Computes global page activity from each CPU's `vm.pgin` and `vm.pgout` stats.
- Deficit decay assumes useful pages per paging I/O are roughly half of a `MAXBSIZE` transfer, with a minimum useful page count of one.
- Skips deficit decay when `lotsfree` is zero or pageout is disabled through `dopageout`.

Filesystem relevance:
- Indirect but important. Page-in/page-out rates and deficit behavior are driven by filesystem-backed and swap-backed paging I/O, and the comments note the assumptions are imperfect across filesystem types.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vm_meter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vm_pageout.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vm_pageout.c

Implements the kernel pageout daemon, page scanner scheduling, memory-pressure thresholds, async dirty-page push queue, and deadman detection for pageout stalls.

Key responsibilities:
- Defines and sizes free-memory thresholds: `lotsfree`, `desfree`, `minfree`, `throttlefree`, `pageout_reserve`, `needfree`, `deficit`, and scan rates.
- Calibrates page scanner spread and scan rate at boot through sampling.
- Runs one or more `pageout_scanner()` threads over disjoint regions of physical page memory.
- Uses a two-handed clock algorithm: the front hand clears reference state, and the back hand frees pages not referenced again.
- Queues dirty pages for asynchronous `VOP_PUTPAGE()` by the main `pageout()` thread.
- Signals memory waiters and integrates with kmem reaping, seg preaping, and kernel cage pressure.
- Panics through `pageout_deadman()` if pageout appears stuck too long in a single `VOP_PUTPAGE()` request.

Important paths:
- `setupclock()` computes memory thresholds, scan rates, scanner duty-cycle nanosecond budgets, hand spread, max page I/O, and desired page scanner count. It preserves boot-time tunable overrides in `clockinit`.
- `recalc_pagescanners()` chooses a scanner count from either `despagescanners` or memory size, bounded by `MAX_PSCAN_THREADS` and minimum per-scanner region size.
- `schedpaging()` runs four times per second, triggers kmem/seg reaping, computes `desscan` and `pageout_nsec` from memory pressure, adjusts scanner count, handles initial sampling, wakes scanners under low memory, and wakes waiters on `memavail_cv`.
- `pageout()` initializes the pageout process, async request pool, scanner thread, pageout scheduler, and kernel cage thread, then drains `push_list` by calling `VOP_PUTPAGE()` with `B_ASYNC | B_FREE`.
- `pageout_scanner()` waits on `proc_pageout->p_cv`, resets its memory-region clock hands when needed, scans up to `desscan` or its CPU budget, calls `checkpage()` for front and back hands, records samples, and exits excess scanner LWPs when scanner count shrinks.
- `checkpage()` skips kernel/free/locked/highly shared/locked-for-COW pages, uses `hat_pagesync()` to test/clear reference and modified state, demotes large pages when possible, queues dirty vnode pages for writeback, unloads clean pages, and disposes them with `VN_DISPOSE(B_FREE)`.
- `queue_io_request()` consumes a preallocated async request, holds the vnode from the caller, links it to `push_list`, and wakes the pusher when the request pool empties.

Locking and concurrency:
- `pageout_mutex` coordinates scanner wakeups, scanner count, and active scanner state.
- `push_lock` protects async request freelist, push queue, push counters, and condition variable.
- Page eligibility depends on page locks, HAT reference/modify bits, vnode holds, and page structure flags.
- Scanner threads can continue freeing clean pages while the pusher thread is blocked in filesystem writeback.

Filesystem relevance:
- Highly relevant to filesystem behavior. Dirty vnode-backed pages are reclaimed through `VOP_PUTPAGE()`, clean pages are returned with `VN_DISPOSE()`, filesystem writeback latency can stall memory reclaim, and pageout pressure interacts with swapfs, ZFS, and other filesystems that supply backing pages.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vm_pageout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vm_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vm_subr.c

Provides VM and raw-I/O support routines: physical I/O setup, user access checking, and temporary kernel mapping of user pages with optional copy-on-write protection.

Key responsibilities:
- Implements `minphys()` to clamp buffer I/O size to `maxphys`.
- Creates a `physio_buf_cache` for reusable `struct buf` objects used by physical I/O.
- Implements `default_physio()` for raw character/block driver I/O through page locking and strategy submission.
- Provides legacy `useracc()` address permission checking.
- Provides `cow_mapin()` for temporarily borrowing user pages into kernel mappings, optionally protecting MAP_PRIVATE segvn pages with COW.

Important paths:
- `physio_bufs_init()` creates a `kmem_cache` whose constructor/destructor run `bioinit()` and `biofini()`.
- `default_physio()` allocates or reuses a buf, fills DTrace-visible metadata, walks `uio` iovecs, checks offsets, clamps size with `mincnt`, locks user/kernel pages with `as_pagelock()`, submits the driver strategy routine, waits with `biowait()`, unlocks pages, and advances iov/resid/offset.
- `useracc()` maps `B_READ`/write-style access into `as_checkprot()` with `PROT_USER`.
- `cow_mapin()` validates the target segment for optional COW, softlocks pages with `hat_softlock()`, optionally increments anon refcounts and read-protects user mappings, maps pages into kernel space with `hat_devload()`, reuses cached mappings when possible, and faults pages in once on `FC_NOMAP`.

Locking and memory model:
- `default_physio()` requires the buf semaphore to be held and uses `as_pagelock()` / `as_pageunlock()` around I/O.
- `cow_mapin()` holds the address-space writer lock during COW setup to prevent racing COW faults or anon teardown.
- `cow_mapin()` uses `HAT_NOCONSIST`/`HAT_LOAD_NOCONSIST` device-style mappings and requires the caller to handle cache-consistency responsibilities.

Filesystem relevance:
- Directly relevant to device and filesystem raw I/O paths. It bridges `uio`, buf strategy calls, page locking, DTrace I/O probes, and user-page mapping, all of which are used by storage drivers and special-file I/O below filesystems.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vm_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vmem.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vmem.c

Implements the illumos virtual memory/resource arena allocator (`vmem`), a hierarchical allocator for kernel virtual addresses, identifiers, and other integer ranges.

Key responsibilities:
- Creates and destroys arenas with optional imported spans from source arenas.
- Represents arena contents as spans and allocated/free segments.
- Provides fast unconstrained allocation, constrained allocation, next-fit, first-fit, best-fit, end allocation, and quantum cache acceleration.
- Tracks allocated segments in per-arena hash tables and free segments in power-of-two freelists.
- Preallocates `vmem_seg_t` metadata to avoid recursive allocation deadlocks.
- Exports arena walking, sizing, containment checks, kstats, periodic hash resizing, and qcache reaping.

Important structures and concepts:
- `vmem_t` arenas form parent/child trees through source allocation/free functions.
- `vmem_seg_t` entries are linked in arena order and also in next-of-kin lists for allocation hash chains, freelists, or span marker lists.
- Span markers bound coalescing and allow whole imported spans to be returned to the source when fully free.
- Free lists use size-class markers and a bitmap-like `vm_freemap` for quick discovery of non-empty size classes.
- Small allocations can bypass vmem segment management through per-size kmem quantum caches.

Important paths:
- `vmem_span_create()` inserts a span marker and an initial free segment, updating import and total-memory kstats.
- `vmem_seg_alloc()` carves an allocation out of a free segment, splitting left/right/middle remainders as needed and hashing the allocated segment.
- `vmem_xalloc()` validates alignment/phase/nocross constraints, searches freelists for a suitable segment, imports from the source arena if needed, handles source over-import cleanup, and panics for mandatory `VM_PANIC` allocation failures.
- `vmem_alloc()` serves qcache-sized allocations through kmem caches, delegates constrained policies to `vmem_xalloc()`, and otherwise performs instant-fit freelist allocation.
- `vmem_xfree()` removes the allocated segment from the hash, coalesces neighbors, returns whole imported spans to the source, or reinserts the coalesced free segment.
- `vmem_nextfit_alloc()` advances a rotor through the arena to reduce address reuse and support cycling identifier allocation.
- `vmem_populate()` refills per-arena segment reserves from a global freelist or `vmem_seg_arena`, using separate locks for sleep, nosleep, pushpage, and panic contexts.
- `vmem_create_common()` initializes arena metadata, qcache caches, kstats, source links, populator state, and optional initial spans.
- `vmem_update()` periodically broadcasts arena condition variables and rescales allocation hash tables.
- `vmem_init()` bootstraps the heap arena and metadata arenas (`vmem_metadata`, `vmem_seg`, `vmem_hash`, `vmem_vmem`) from static early storage.

Locking and reliability:
- Each arena has a single `vm_lock`; hot arenas are expected to use quantum caching for scalability.
- Segment metadata reserves are carefully sized to handle worst-case import and allocation recursion.
- Allocation failure injection is supported through `vmem_mtbf` and per-arena `vm_mtbf`.
- Hash-delete failures or wrong-size frees panic, providing runtime sanity checking even without full kmem debug features.

Filesystem relevance:
- Indirect but foundational. VFS, filesystems, VM, device mappings, buffer mapping, and kernel heap consumers use vmem-backed arenas to allocate address ranges and identifiers. The legacy `rmap` wrapper elsewhere also builds on vmem.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/waitq.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/waitq.c

Implements priority-ordered wait queues used for CPU caps and scheduler throttling.

Key responsibilities:
- Initializes and finalizes `waitq_t` structures.
- Maintains a priority-ordered singly linked list of waiting threads with circular doubly linked sublists for equal priorities.
- Enqueues locked threads when a wait queue is unblocked.
- Reorders waiting threads when priority changes.
- Removes one or all waiters and makes them runnable.
- Blocks and unblocks queues as a whole.

Important paths:
- `waitq_link()` inserts a thread by dispatch priority while preserving FIFO order within a priority level.
- `waitq_unlink()` removes a known waiting thread efficiently by using `t_waitq`, priority sublist links, and limited head-list scanning only when needed.
- `waitq_enqueue()` refuses blocked queues, records wait timestamp, marks `TS_DONT_SWAP`, emits DTrace sleep probe state, links the thread, and transitions it to wait state.
- `waitq_change_pri()` unlinks, updates `t_pri`, and relinks the thread in the correct priority position.
- `waitq_setrun()` removes a specific waiter and calls scheduler class `CL_SETRUN()`.
- `waitq_runone()` and `waitq_block()` wake the first or all waiting threads.
- `waitq_unblock()` allows new waiters only after asserting the queue is empty and blocked.

Locking and invariants:
- Each wait queue uses a dispatcher lock.
- Callers must hold the target thread lock for enqueue, priority-change, and explicit setrun paths.
- `waitq_block()` sets `wq_blocked` under lock, then drains all current waiters and asserts the queue is empty.
- `waitq_isempty()` is intentionally lockless and only a hint unless externally synchronized.

Filesystem relevance:
- No direct VFS behavior, but it is kernel scheduling infrastructure. Filesystem and storage threads can be indirectly affected by CPU-cap wait queues and scheduler throttling when they block or are made runnable under system policy.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/waitq.c -->