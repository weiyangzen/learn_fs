# Group Research: group_1407_openbsd_src_sources_os_bsd_openbsd_src_sys_kern_vfs_bio_c_sources_o_80edce3902fd

Scope checked against `Docs/research_subset_a.md`: subset A includes the complete `sources/os/bsd/openbsd-src` source tree. All ten listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_bio.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_bio.c

Read completely: 1529 lines.

Implements OpenBSD's buffer cache core: buffer allocation, cached block lookup, read/write helpers, delayed-write handling, I/O completion, memory pressure backoff, cleaner daemon coordination, and the clean/dirty cache queues.

Core buffer-cache sizing and lifecycle:
- `bufinit()` sizes the cache from physical/free pages and `bufcachepercent`, enforces minimums, reserves buffer KVA, initializes `bufpool`, initializes cache queues, and sets dirty-page watermarks.
- `bufadjust()` changes `bufpages`, recomputes `targetpages`, recovers pages if over target, rebalances cache queues, and wakes the cleaner under pressure.
- `bufbackoff()` lets UVM force the buffer cache down toward `buflowpages`.
- `buf_put()` removes a buffer from the global list, frees attached memory through `buf_dealloc_mem()`, and returns it to `bufpool` unless KVA cleanup is deferred.

Read/write paths:
- `bio_doread()` wraps `getblk()`, starts `VOP_STRATEGY()` reads for uncached data, charges resource counters, and updates per-mount sync/async read stats.
- `bread()` performs synchronous block reads; `breadn()` adds independent async read-ahead.
- `bread_cluster()` issues one large read-ahead I/O when `VOP_BMAP()` reports contiguous blocks, then splits pages back into per-block buffers in `bread_cluster_callback()`.
- `bwrite()` handles sync and async writes, converts eligible sync writes to delayed writes on `MNT_ASYNC`, updates mount stats and output counters, starts strategy I/O, and waits/releases for synchronous callers.
- `bdwrite()` marks delayed-write buffers dirty and complete without immediate I/O.
- `bawrite()` marks a buffer async and dispatches through `VOP_BWRITE()`.

Buffer lookup and allocation:
- Buffers are indexed per vnode in `v_bufs_tree` by logical block number.
- `incore()` checks for a valid cached block.
- `getblk()` waits for busy matching buffers, returns cached buffers with `B_CACHE`, or calls `buf_get()` to allocate a new busy buffer.
- `buf_get()` allocates a `struct buf`, optionally associates it with a vnode, allocates/map pages for nonzero sizes, enforces cache and KVA reserve limits, and waits on `needbuffer`/`nobuffers` when non-cleaner callers hit pressure.
- `geteblk()` obtains an anonymous invalid buffer.

Release, dirtying, and completion:
- `brelse()` invalidates noncacheable/error buffers, frees invalid buffers immediately, otherwise returns valid buffers to the clean or dirty cache, clears transient flags, wakes waiters, and triggers reclamation/rebalancing.
- `buf_dirty()` and `buf_undirty()` toggle `B_DELWRI` under `splbio()` and call `reassignbuf()`.
- `biowait()` sleeps for `B_DONE` and returns `EINTR`, buffer error, `EIO`, or success.
- `biodone()` marks completion, updates queue and pending-I/O stats, wakes vnode output waiters, invokes callbacks, releases async buffers, or wakes sync waiters.
- `buf_adjcnt()` adjusts `b_bcount` within allocated buffer size.

Cleaner and cache policy:
- `buf_daemon()` sleeps on `bd_req`, drains dirty buffers from `dirtyqueue`, and writes them asynchronously until dirty/KVA pressure drops.
- The clean cache is a 2Q-style design with hot, cold, and warm queues.
- `bufcache_release()` places clean buffers in hot/warm queues and dirty buffers in `dirtyqueue`.
- `bufcache_take()` removes a buffer from its current clean or dirty queue and updates page counters.
- `chillbufs()` moves over-limit hot/warm buffers to cold.
- `bufcache_recover_pages()` discards clean buffers until enough pages are recovered.
- Hibernation support drops all clean cache pages instead of preserving them in swap.

Risks and notes:
- Correctness depends on strict `splbio()` discipline around buffer queues, vnode buffer lists, and cache counters.
- Buffer flags are stateful and overlapping; mistakes with `B_BUSY`, `B_DELWRI`, `B_INVAL`, `B_DONE`, `B_ASYNC`, or `B_WRITEINPROG` can corrupt lifetime or I/O accounting.
- `bread_cluster_callback()` moves pages between UVM objects after interrupt-time completion, making object/page offset invariants critical.
- Cleaner and syncer paths are exempt from some buffer pressure waits; changing reserve logic can deadlock memory reclaim.
- Write errors on regular-file buffers mark the vnode with `VBIOERROR`, so callers may observe damage after buffer release.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_bio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_biomem.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_biomem.c

Read completely: 315 lines.

Implements the memory-management side of OpenBSD buffers: reservation and reuse of kernel virtual address slots, mapping buffer pages into KVA, deferred freeing when KVA cannot be immediately reclaimed, and allocation/freeing of DMA-reachable buffer pages.

KVA reservation and mapping:
- `buf_mem_init()` reserves a contiguous `PROT_NONE` range in `kernel_map` for buffer mappings and initializes available KVA slot counters based on `MAXPHYS`.
- `buf_acquire()` marks a buffer busy and maps it.
- `buf_acquire_nomap()` marks a buffer busy while preserving any existing mapping and removing it from the available-KVA list.
- `buf_map()` assigns KVA to a buffer, first from unallocated reserved space, then by stealing an idle mapped buffer from `buf_valist`.
- Non-cleaner/non-syncer callers wait on `buf_needva` when KVA slots fall below `RESERVE_SLOTS`.
- Mapping inserts each buffer page with `pmap_kenter_pa()` and updates the kernel pmap.

Release and unmap behavior:
- `buf_release()` clears `B_BUSY`, places mapped buffers onto `buf_valist`, increments available KVA slots, and wakes KVA waiters.
- `buf_unmap()` removes an idle buffer mapping, returns its KVA address for reuse, and finally frees buffers marked `B_RELEASED`.
- `buf_dealloc_mem()` removes mappings, frees pages, and if KVA existed defers `pool_put()` by marking `B_RELEASED` and putting the buffer at the front of `buf_valist`.
- `buf_fix_mapping()` shrinks an existing mapping after clustered reads split one large mapping across multiple buffers.

Page allocation:
- `buf_alloc_pages()` initializes a buffer UVM object and allocates wired pages with DMA constraints.
- It first tries NOWAIT allocation, then asks `bufbackoff()` to recover clean cache pages, then falls back to WAITOK allocation.
- `buf_free_pages()` unwires and accounts each page, clears the buffer page object fields, and frees the UVM object.

Risks and notes:
- The KVA slot accounting in `bcstats.kvaslots_avail` and `bcstats.busymapped` must remain paired with `buf_valist` mutations.
- `buf_dealloc_mem()` temporarily clears `b_data` because many assertions expect unmapped buffers to have null data pointers.
- Deferred release via `B_RELEASED` means a buffer structure can survive page freeing until its KVA mapping is stolen.
- Buffer pages are allocated with DMA reachability assumptions; changing constraints can break block-device I/O.
- Most routines require `splbio()` and assume callers have already serialized buffer state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_biomem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_cache.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_cache.c

Read completely: 472 lines.

Implements OpenBSD's pathname namecache. It caches positive and negative directory lookups, keeps per-directory red-black trees for fast component lookup, tracks reverse directory-name mappings for `getcwd()`, and purges entries on vnode/filesystem invalidation.

Cache structures:
- Positive entries are counted in `numcache` and linked on `nclruhead`.
- Negative entries are counted in `numneg` and linked on `nclruneghead`.
- Each directory vnode owns a `v_nc_tree` keyed by component name length and bytes.
- Directory target vnodes keep reverse entries on `v_cache_dst`, excluding `.` and `..`.
- `doingcache` globally enables/disables namecache use.
- `nch_pool` allocates `struct namecache` entries.

Lookup and insertion:
- `cache_lookup()` rejects disabled caching and names longer than `NAMECACHE_MAXLEN`, then searches the directory vnode tree.
- Positive hits validate `nc_vpid` against the target vnode generation before returning a locked/referenced vnode.
- Negative hits return `ENOENT` except for final-component `CREATE`, where the stale negative entry is removed.
- `.` and `..` hits handle vnode locking carefully: `..` unlocks the parent before locking the child/parent combination required by lookup flags.
- Hits update LRU position and statistics; bad/false hits purge the entry.
- `cache_enter()` recycles old positive or negative entries once `numcache >= initialvnodes`, allocates a new entry, inserts into the directory tree, and records positive, negative, and reverse links.

Reverse lookup and purge:
- `cache_revlookup()` scans `v_cache_dst` to find a parent/name for a directory vnode and can prepend that name into a caller's buffer for `getcwd()`.
- `nchinit()` initializes LRU queues and the namecache pool.
- `cache_purge()` removes all reverse and child entries for a vnode, then bumps `v_id` to invalidate stale capabilities.
- `cache_purgevfs()` removes all cache entries whose directory vnode belongs to a mount being unmounted.

Risks and notes:
- A file comment explicitly notes namecache access should be locked; this implementation relies on existing kernel/VFS serialization assumptions.
- Generation checks via `v_id` are central to avoiding stale vnode hits after recycle or purge.
- Reverse lookup does not `vget()` the parent; callers must validate and lock the returned vnode if they need stable semantics.
- Negative cache growth is capped separately, but positive-entry pressure drives general recycling.
- Parent/leaf lock behavior in `cache_lookup()` must match `VOP_LOOKUP()` and namei contracts exactly.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_default.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_default.c

Read completely: 174 lines.

Provides generic vnode-operation defaults shared by filesystems and special vnode implementations.

Implemented defaults:
- `vop_generic_revoke()` handles `REVOKEALL`, first force-unmounting an associated mounted block device if needed, then eliminating aliased special-device vnodes and finally calling `vgonel()` on the target.
- It serializes alias teardown with `vnode_mtx`, `VXLOCK`, and `VXWANT`.
- `vop_generic_badop()` panics for impossible/unimplemented operations.
- `vop_generic_bmap()` maps logical block to itself, returns the same vnode, and reports zero run length.
- `vop_generic_bwrite()` delegates buffer writes to `bwrite()`.
- `vop_generic_abortop()` frees the namei pathname buffer when appropriate.
- `vop_generic_lookup()` always fails with `ENOTDIR`.

Risks and notes:
- Revoke behavior is special-device sensitive and may force unmounts through `dounmount()`.
- Alias cleanup assumes `VALIASED` and special-device hash-chain invariants are intact.
- `vop_generic_abortop()` depends on precise `HASBUF` and `SAVESTART` flag ownership of `cn_pnbuf`.
- `vop_generic_badop()` is intentionally fatal, so operation vectors must only use it for unreachable methods.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_default.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_getcwd.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_getcwd.c

Read completely: 433 lines.

Implements kernel pathname reconstruction for current-working-directory and related containment/path queries. It walks from a leaf vnode up toward a root vnode, using reverse namecache hits when possible and directory scans as fallback.

Parent/name discovery:
- `vfs_getcwd_getcache()` uses `cache_revlookup()` to find a parent vnode and component name, then unlocks the child, locks the parent with `vget()`, and validates the parent's `v_id`.
- On cache miss or invalidation it reacquires the child lock and tells the caller to use the slow path.
- `vfs_getcwd_scandir()` performs `VOP_LOOKUP("..")`, reads parent directory entries with `VOP_READDIR()`, and finds the entry whose file id matches the child vnode.
- It uses `VOP_GETATTR()` to obtain the child's file id and directory block size.
- It retries from offset zero up to three times on NFS-style `EINVAL` cookie failures.
- Directory entries are validated for record length and name bounds before copying names backward into the output buffer.

Common walk:
- `vfs_getcwd_common()` references the requested root and leaf, locks the leaf, then walks upward until it reaches the root, a mount boundary, an error, or a traversal limit.
- It handles mounted filesystem roots by stepping to `mnt_vnodecovered`.
- Optional `GETCWD_CHECK_ACCESS` enforces execute/read access while walking.
- Components are prepended into the caller buffer, with `/` separators inserted as the walk progresses.
- `sys___getcwd()` allocates a bounded temporary buffer, calls the common walker from `fd_cdir`, copies the result to userland, and emits ktrace namei data when enabled.

Risks and notes:
- Correctness depends on careful lock transitions between child and parent vnodes.
- Reverse cache results are advisory and must be validated by vnode generation.
- The fallback directory scan depends on stable file ids and well-formed `struct dirent` records.
- Buffer construction works backward, so off-by-one checks around `bufp`, `bpp`, and separators are important.
- Crossing mount roots requires replacing the current vnode with `mnt_vnodecovered` without leaking references.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_getcwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_init.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_init.c

Read completely: 160 lines.

Initializes core VFS infrastructure and declares the statically configured filesystem type table for the kernel build.

Filesystem registration:
- `vfsconflist[]` contains compile-time `struct vfsconf` entries for enabled filesystems such as FFS, MFS, EXT2FS, CD9660, MSDOSFS, NFS client, NTFS, UDF, FUSE, and TMPFS.
- Each entry records VFS ops, mount type name, numeric type id, flags such as `MNT_LOCAL` and `MNT_SWAPPABLE`, and expected mount-argument size.
- `maxvfsconf` is initialized to the table length, then recomputed as the highest configured type number during initialization.

Initialization and lookup:
- `vfsinit()` initializes `namei_pool`, vnode tables, the namecache, and each filesystem's optional `vfs_init()` hook.
- It also sets `maxvfsconf` based on configured type numbers.
- `vfs_byname()` returns a `vfsconf` by mount type name.
- `vfs_bytypenum()` returns a `vfsconf` by numeric filesystem type.

Risks and notes:
- This is static registration; missing compile-time options omit filesystem support entirely.
- `namei_pool` uses fixed `MAXPATHLEN` buffers and is shared by pathname resolution.
- Type numbers are sparse and must remain ABI-compatible with userland and mount interfaces.
- Filesystem `vfs_init()` hooks run during global VFS initialization and must tolerate early boot context.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_lockf.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_lockf.c

Read completely: 904 lines.

Implements OpenBSD advisory byte-range locking for vnode-backed files and special devices. It supports POSIX `fcntl` locks and BSD `flock` semantics, storing sorted lock ranges in a per-vnode `lockf_state` protected by a global rwlock.

Core structures and limits:
- `struct lockf` records lock flags, type, inclusive start/end byte range, owner id, lock state, active/pending list links, blocking relationships, charged uid, and reporting pid.
- `struct lockf_state` owns active locks, pending locks, a backpointer to the vnode/special-device owner pointer, and a reference count.
- `lockf_lock` serializes all lock and state operations.
- `lf_init()` initializes pools for lock states and locks.
- `lf_alloc()` charges `uidinfo.ui_lockcnt` and enforces `maxlocksperuid`, with looser limits for unlock-time splitting.
- `ls_ref()` and `ls_rele()` manage state lifetime and clear the owner pointer when the last reference disappears.

External operation path:
- `lf_advlock()` normalizes `struct flock` `l_whence`, `l_start`, and `l_len` into inclusive ranges, including negative lengths and EOF locks represented by `lf_end == -1`.
- It creates a lock state on first use, allocates a candidate lock, fills POSIX pid reporting when needed, and dispatches `F_SETLK`, `F_UNLCK`, or `F_GETLK`.
- `F_SETLK` calls `lf_setlock()`, `F_UNLCK` calls `lf_clearlock()`, and `F_GETLK` calls `lf_getlock()`.

Range matching and mutation:
- `lf_findoverlap()` walks sorted locks and classifies overlap into six cases: none, exact, existing contains requested, requested contains existing, existing starts before, or existing ends after.
- `lf_getblock()` finds the first conflicting lock owned by another id, allowing read/read overlap.
- `lf_setlock()` waits for conflicts when `F_WAIT` is set, optionally detects POSIX deadlocks, removes shared flock locks before exclusive flock upgrades, and then inserts/merges/splits/replaces same-owner overlapping ranges.
- `lf_clearlock()` removes or shrinks same-owner locks and wakes waiters affected by the changed range.
- `lf_split()` splits an existing lock around a contained new or unlocked range, allocating a third range when needed.
- `lf_wakelock()` wakes every waiter blocked on a given lock and can mark interrupted purges.
- `lf_purgelocks()` interrupts pending locks, waits for them to exit, then removes all active locks for a state.

Deadlock and diagnostics:
- `lf_deadlock()` checks pending POSIX locks for a simple two-party cycle involving the current lock and a blocking owner.
- `LOCKF_DEBUG` includes lock/list printing helpers and debug categories.

Risks and notes:
- The global `lockf_lock` is simple but makes lock-list mutation, sleeping, waking, and state reference counts tightly coupled.
- Deadlock detection is limited and intentionally much simpler than full graph detection.
- EOF range representation with `-1` makes arithmetic and overlap ordering subtle.
- `lf_split()` may allocate while handling an unlock, so allocation-limit exceptions are part of correctness.
- `lf_purgelocks()` depends on pending waiters clearing `ls_pending` and waking the state before final free.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_lockf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_lookup.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_lookup.c

Read completely: 880 lines.

Implements OpenBSD pathname resolution: `namei()`, component walking, symlink expansion, mount crossing, `relookup()`, realpath component tracking, and integration with pledge/unveil checks.

Entry setup:
- `ndinitat()` initializes `struct nameidata` for path operations relative to a directory fd.
- `component_push()` and `component_pop()` maintain `REALPATH` reconstruction state in `cn_rpbuf`.
- `namei()` allocates/copies the path from user or kernel space, rejects empty paths, optionally strips trailing slashes, sets the effective root, and runs pledge/unveil prechecks unless `KERNELPATH` is set.
- Starting vnode selection handles absolute paths, `AT_FDCWD`, and explicit directory fd lookups.
- Absolute `REALPATH` lookups initialize the reconstructed path with `/`.

Main namei loop:
- `namei()` calls `vfs_lookup()` repeatedly until the path resolves or a symlink must be followed.
- On final non-symlink success it runs `unveil_check_final()`, releases or preserves the namei buffer according to `SAVENAME`/`SAVESTART`, and returns.
- Symlink handling enforces `SYMLOOP_MAX`, reads link contents with `VOP_READLINK()`, splices remaining path text, restarts from root for absolute links, and updates realpath state.
- `BPU_LOCALTIME` and `BPU_ZONEINFO` impose stricter symlink/path rules for `/etc/localtime` and `/usr/share/zoneinfo`.

Component lookup:
- `vfs_lookup()` locks the starting directory, strips leading slashes, parses each component, sets `REQUIREDIR`, `ISLASTCN`, `MAKEENTRY`, and `ISDOTDOT`, and updates `ni_next`/`ni_pathlen`.
- It prevents `..` from escaping `ni_rootdir` or `rootvnode`.
- For `..` at mounted filesystem roots, it climbs to `mnt_vnodecovered` unless `NOCROSSMOUNT` is set.
- It calls `unveil_check_component()` before filesystem lookup.
- `VOP_LOOKUP()` failures with `EJUSTRETURN` are used for create-like final components; read-only filesystems reject mutating operations unless the pledge unveil path permits the special case.
- Successful directory vnodes mounted over by another filesystem are crossed using `vfs_busy()` and `VFS_ROOT()`.
- Symlinks are returned to `namei()` for interpretation when `FOLLOW` or `REQUIREDIR` applies.
- Final checks enforce directory requirements, read-only restrictions for delete/rename, optional parent retention, and `LOCKLEAF`.

Relookup:
- `vfs_relookup()` reacquires a previously parsed final component under a supplied directory vnode.
- It rejects null and dot-dot names, calls `VOP_LOOKUP()`, handles create-style `EJUSTRETURN`, applies read-only checks, optionally preserves the start directory, and unlocks the leaf if `LOCKLEAF` is absent.

Risks and notes:
- Vnode reference and lock ownership across `ni_dvp`, `ni_vp`, symlinks, and mount crossings is delicate.
- Pledge/unveil integration can transform some access errors into `EJUSTRETURN` for unveil setup.
- `REALPATH` state is maintained incrementally and must be rolled back on relative symlinks and `..`.
- `cn_consume` lets filesystems consume additional path bytes, so path length and required-directory state must be adjusted carefully.
- Mount traversal depends on `vfs_busy()` protection while calling `VFS_ROOT()`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_subr.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_subr.c

Read completely: 2359 lines.

Provides broad shared VFS support: vnode table management, mount allocation/busying, vnode recycling, special-device aliasing, buffer-vnode association, buffer invalidation/flushing, sync/shutdown helpers, export helpers, access checks, sysctls, and DDB diagnostics.

Initialization and mount support:
- `vntblinit()` initializes vnode pools, vnode free/hold lists, `mountlist`, syncer queues, and NFS radix infrastructure when enabled.
- `vfs_mount_alloc()` allocates a busy mount, initializes refs and locks, links the covered vnode, copies VFS ops/type data, and applies default flags.
- `vfs_mount_take()`, `vfs_mount_free()`, and `vfs_mount_rele()` manage mount references and VFS type refcounts.
- `vfs_busy()` acquires the mount rwlock in read or write mode, fails if unmounting, and supports wait/nowait behavior.
- `vfs_unbusy()` releases the mount lock; `vfs_isbusy()` reports lock state.
- `vfs_rootmountalloc()` creates the root mount from a filesystem type and device name.
- `vfs_getvfs()` finds a mount by fsid, and `vfs_getnewfsid()` generates unique fsids.

Vnode allocation and references:
- `getnewvnode()` allocates or recycles vnodes based on `maxvnodes`, buffer-cache size, free lists, and hold lists.
- New vnodes initialize buffer trees, namecache trees, reverse-cache lists, operation vectors, type/tag, mount queue membership, and usecount.
- `insmntque()` moves vnodes between mount vnode lists.
- `vget()` obtains a use reference and optional lock, handling `VXLOCK` cleanup races and free-list removal.
- `vref()`, `vput()`, `vrele()`, `vhold()`, and `vdrop()` manage active and buffer-held vnode references.
- `vputonfreelist()` places inactive vnodes on the hold or free list and clears bio error state.

Special devices and aliases:
- `bdevvp()` and `cdevvp()` create block/character device vnodes through `getdevvp()`.
- `checkalias()` detects existing special-device aliases, flushes unused aliases, shares clone bitmaps, sets `VALIASED`, or reuses `VT_NON` block-device vnodes for cases such as root devices.
- `vfinddev()`, `vdevgone()`, and `vcount()` find, revoke, or count references to special-device vnodes across aliases.
- `vfs_mountedon()` checks whether a block device or alias is already a mount backing device.

Vnode flushing and reclamation:
- `vfs_mount_foreach_vnode()` iterates a mount's vnode list robustly against list mutation.
- `vflush()` applies `vflush_vnode()` to detect or force-close busy vnodes, optionally skipping system vnodes, clean vnodes, or non-writable regular files.
- `vclean()` drains vnode activity with `VXLOCK`, locks the vnode, terminates UVM state, optionally invalidates buffers and closes active vnodes, calls inactive/reclaim, purges namecache, switches to `dead_vops`, and wakes waiters.
- `vrecycle()`, `vgone()`, and `vgonel()` recycle or eliminate vnodes, detach mount membership, remove special-device aliases, purge special-device locks, and move bad vnodes to the front of the free list.

Buffer and I/O helpers:
- `vwaitforio()` waits for `v_numoutput` to reach zero.
- `vwakeup()` decrements output count and wakes waiters.
- `vinvalbuf()` optionally fsyncs a vnode, waits for I/O, invalidates clean/dirty buffers, writes delayed buffers if saving, and panics if buffers remain unexpectedly.
- `vflushbuf()` writes dirty buffers asynchronously or synchronously and waits for completion when requested.
- `bgetvp()` attaches a buffer to a vnode, takes a hold, and inserts it on the clean list.
- `brelvp()` detaches a buffer, removes syncer list membership when no dirty buffers remain, and drops the vnode hold.
- `buf_replacevnode()` changes a buffer's vnode association while adjusting outstanding output accounting.
- `reassignbuf()` moves buffers between clean and dirty vnode lists and schedules dirty vnodes on the syncer with shorter delays for directories and mounted block devices.

System sync, stall, and shutdown:
- `vfs_stall()` can freeze all mounts by taking write busy locks, syncing UVM/vnodes, calling `VFS_SYNC(MNT_WAIT)`, and marking mounts stalled; unstalls release those locks.
- `vfs_stall_barrier()` lets operations wait while global stalling is active.
- `vfs_unmountall()` traverses mounts in reverse order and force-unmounts them, retrying once on failures.
- `vfs_shutdown()` syncs, unmounts, quiesces softraid if present, and waits for buffers.
- `vfs_syncwait()` repeatedly calls `sys_sync()`, flushes lingering delayed-write buffers, reports busy counts, and gives up after bounded retries.

Access, exports, sysctl, and diagnostics:
- `vattr_null()` initializes vnode attributes to `VNOVAL`.
- `vaccess()` implements Unix owner/group/other permission checks, with root read/write bypass but execute requiring at least one execute bit for non-directories.
- `vnoperm()` checks mount `MNT_NOPERM`.
- `vfs_export()` and `vfs_export_lookup()` manage NFS export address lists when `NFSSERVER` is enabled.
- `vfs_sysctl()` exposes generic VFS data, filesystem config data with kernel pointers cleared, and buffer-cache statistics.
- Debug/DDB helpers print vnodes, buffers, mounts, locked vnodes, and statfs data.
- `copy_statfs_info()` copies stable mount stat fields and mount info into a caller's `statfs`.

Risks and notes:
- This file is a central lifetime manager; refcount, usecount, holdcount, mount-lock, and vnode-lock mistakes can cascade across VFS.
- `vclean()` and `vgonel()` depend on `VXLOCK`/`VXWANT` exclusion to avoid recycling races.
- Special-device alias handling is subtle, especially cloned character devices and root block-device vnodes.
- `vinvalbuf()` and `vfs_syncwait()` contain comments about difficult delayed-write and softdep interactions.
- `vfs_getvfs()` returns a raw mount pointer without taking a reference, so users must protect lifetime separately.
- Several paths assume `splbio()` around buffer/vnode list mutation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_sync.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_sync.c

Read completely: 371 lines.

Implements the filesystem syncer daemon and synthetic syncer vnodes used to lazily flush dirty vnodes and periodically call filesystem sync operations.

Syncer queue model:
- `SYNCER_MAXDELAY` and `syncdelay` define a ring of delayed work queues.
- `vn_initialize_syncerd()` allocates the hash/ring of pending sync lists and records the mask.
- `vn_syncer_add_to_worklist()` inserts or moves a vnode into a future slot, clamping delay and marking `VBIOONSYNCLIST`.
- Dirty vnodes are scheduled by `reassignbuf()` in `vfs_subr.c`.

Daemon loop:
- `syncer_thread()` advances one slot per second.
- For each vnode in the current slot, it tries `vget(... LK_NOWAIT)`.
- If locking fails, the vnode is rescheduled one second later.
- If locking succeeds, the daemon calls `VOP_FSYNC(... MNT_LAZY ...)`, releases the vnode, and reschedules if it remains at the head of the same list.
- Diagnostic builds panic if a non-block vnode with no dirty buffers remains stuck on the worklist after fsync.
- The loop yields between items and sleeps only for the remainder of the one-second period.

Syncer vnode:
- `sync_vops` defines a minimal vnode operation vector for syncer vnodes, with `sync_fsync()`, `sync_inactive()`, and `sync_print()`.
- `vfs_allocate_syncvnode()` creates one syncer vnode per mount, marks it with a writecount, scatters initial sync delays across the ring, and records it in `mp->mnt_syncer`.
- `sync_fsync()` only acts on `MNT_LAZY`: it reschedules itself, temporarily clears `MNT_ASYNC`, and calls `VFS_SYNC(mp, MNT_LAZY, ...)` while the mount is busy.
- `sync_inactive()` removes a decommissioned syncer vnode from the worklist, clears mount linkage, resets writecount, and drops the vnode.
- `sync_print()` provides debug labeling.

Risks and notes:
- Worklist membership is protected at `splbio()` and represented by `VBIOONSYNCLIST`; duplicate insertion/removal must stay consistent.
- The syncer deliberately uses nonblocking vnode locks and reschedules failures, so heavily contended vnodes may be delayed.
- Syncer vnodes carry `v_writecount = 1`, making inactive handling nonstandard.
- `sync_fsync()` temporarily overrides `MNT_ASYNC` to make lazy filesystem sync behavior meaningful.
- The daemon is pacing-oriented, not a hard real-time writeback guarantee.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_sync.c -->