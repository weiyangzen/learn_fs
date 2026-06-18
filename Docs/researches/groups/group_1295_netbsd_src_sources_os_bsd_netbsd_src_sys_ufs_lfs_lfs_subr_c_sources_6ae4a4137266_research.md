# Group Research: group_1295_netbsd_src_sources_os_bsd_netbsd_src_sys_ufs_lfs_lfs_subr_c_sources_6ae4a4137266

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_subr.c

## Scope
Shared LFS kernel support for reserved segment memory, segment/pre locks, cleaner serialization, directory-operation draining, writer exclusion, cleaner wakeups, and segment-use flag maintenance.

## Key Behavior
- `lfs_setup_resblks()` / `lfs_free_resblks()` allocate and tear down per-mount emergency buffers plus small object pools used while segment-writing or under memory pressure.
- `lfs_malloc()` first tries nonblocking allocation, then falls back to typed reserved buffers tracked in `lfs_reshash`; `lfs_free()` detects reserved buffers and wakes waiters.
- `lfs_seglock()` / `lfs_segunlock()` implement nested segment writer exclusion, allocate `struct segment`, maintain `lfs_iocount`, write checkpoint superblocks, run automatic segment cleaning, and release completed dirop references.
- `lfs_prelock()` / `lfs_preunlock()` provide the recursive per-LWP prerequisite lock; `SEGM_PAGEDAEMON` callers fail with `EWOULDBLOCK` rather than sleep.
- `lfs_writer_enter()` / `tryenter()` / `leave()` prevent new directory operations while writers drain metadata.
- `lfs_cleanerlock()` / `cleanerunlock()` serialize cleaner activity and clear the per-cleaning vnode list.
- `lfs_segunlock_relock()` writes gathered data, signals must-clean state, drops nested segment locks, waits for cleaner-created space, and restores lock depth.
- `lfs_setclean()`, `lfs_clrclean()`, and `lfs_seguse_clrflag_all()` maintain cleaner vnode references and bulk segment-use flags.

## Dependencies And State
Uses `lfs_lock`, `lfs_resblk`, `lfs_prelock`, `lfs_seglock`, `lfs_iocount`, `lfs_cleanlock`, `lfs_dchainhd`, `lfs_cleanhd`, condition variables, segment writer routines, Ifile cleaner info, vnode refs, pools, and NetBSD malloc/buffer primitives.

## Invariants And Risks
Segment locking intentionally nests under one prelock owner. Reserved buffers must not be freed while marked in use. Checkpoint unlock ordering is delicate: I/O completion, superblock writes, active-superblock switching, auto-cleaning, and dirop unmarking are coupled. Dirop unmarking uses marker inodes so the list can be traversed while dropping `lfs_lock`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_syscalls.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_syscalls.c

## Scope
Legacy LFS cleaner syscall implementation and kernel helpers for markv, bmapv, segment clean, segment wait, cleaner-optimized vnode lookup, and fake cleaner buffers.

## Key Behavior
- `sys_lfs_markv()` copies cleaner-provided `BLOCK_INFO` arrays, including older compatibility conversion, then calls `lfs_markv()`.
- `lfs_markv()` authorizes cleaner access, validates inode bounds, references target vnodes, takes cleaner and segment locks, checks block liveness/address/size, copies cleaner data into buffers, writes with `SEGM_CLEAN|SEGM_CKP|SEGM_SYNC`, and returns `EAGAIN` when userland should retry.
- `sys_lfs_bmapv()` / `lfs_bmapv()` fill current disk addresses and sizes for cleaner inode/lbn tuples using Ifile entries and `VOP_BMAP`.
- `sys_lfs_segclean()` / `lfs_do_segclean()` mark empty, dirty, inactive segments clean.
- `lfs_markclean()` updates availability, free metadata accounting, cleaner info, segment flags, and reclaim stats.
- `lfs_segwait()` / `sys___lfs_segwait50()` sleep for per-filesystem or global segment activity.
- `lfs_fastvget()` injects cleaner hints for vnode loading; `lfs_fakebuf()` builds segment-writer buffers from user memory.

## Dependencies And State
Bridges userland `cleanerd` with mount lookup, kauth, VFS busying, Ifile entries, LFS segment writer/checkpoint paths, buffer cache, and compatibility block-info structures. Tracks cleaner thread identity and per-call vnode references.

## Invariants And Risks
Cleaner input is bounds checked, but correctness depends on revalidating live block addresses and sizes under the segment lock. VU_DIROP directories are not cleaned because directory truncation/order can invalidate cleaner assumptions. The final markv write must checkpoint synchronously so recovery never points at overwritten cleaner data. `lfs_fakebuf()` can return `NULL` on `copyin()` failure, so cleaner-data failure paths are particularly sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_vfsops.c

## Scope
Top-level LFS VFS module: syscall registration, sysctls, mount/unmount, root mount, vnode load/allocation, writer daemon, sync/statvfs, genfs page write integration, filesystem resize, and extattr dispatch.

## Key Behavior
- `lfs_vfsops` registers mount, unmount, sync, vget/load/new vnode, filehandle, init/done, root mount, and extattr hooks.
- `lfs_modcmd()` installs/removes the legacy cleaner syscalls and attaches/detaches the filesystem module.
- `lfs_sysctl_setup()` exposes LFS stats, debug controls, roll-forward controls, page flushing, and lazy-sync behavior.
- `lfs_writerd()` monitors dirty buffers/pages, per-mount pageout queues, dirop pressure, and cleaner starvation, then flushes or wakes the cleaner.
- `lfs_init()` / `lfs_done()` manage inode/dinode/lbn pools, global locks/CVs, workqueues, and ULFS initialization.
- `lfs_mount()` handles new mounts, remounts, read-only/read-write transitions, device checks, device authorization, and statvfs metadata.
- `lfs_mountfs()` reads primary/alternate superblocks, validates magic/version/inode format, mounts from the older checkpoint, initializes `struct lfs` and `ulfsmount`, reserve buffers, Ifile vnode, segment flags, freelist/orphans, roll-forward, cleaner info, active segment state, and the writer daemon.
- `lfs_unmount()` / `lfs_flushfiles()` checkpoint twice, stop sleepers/cleaner interaction, flush vnodes, write clean superblocks, drain I/O, close the device, and free per-mount state.
- `lfs_loadvnode()` and `lfs_newvnode()` load disk inodes or allocate fresh inodes, initialize LFS/ULFS vnode state, and support cleaner-provided inode hints.
- `lfs_gop_write()` is the LFS genfs page-write path: requires the segment lock, maps dirty pages, skips holes, splits by segment/summary capacity, gathers buffers into the active segment, and returns `EAGAIN` when cleaning or retry is required.
- `lfs_resize_fs()` grows/shrinks segment tables, rewrites/invalidate removed segments, shifts Ifile contents, adjusts superblock accounting, initializes new `SEGUSE` entries, and updates cleaner info.
- `lfs_extattrctl()` delegates ULFS1 extattrs when configured; otherwise uses standard VFS behavior.

## Dependencies And State
Owns VFS integration with NetBSD VFS, UVM/genfs, ULFS, specfs, sysctl, syscall packages, workqueues, Ifile state, active superblock selection, segment accounting trees, writer/cleaner queues, reserve memory, dirty-page counters, vnode pools, roll-forward flags, and mount flags.

## Invariants And Risks
Mount recovery deliberately starts from the older of the two superblocks, then roll-forward completes before normal `vget`. Writable mounts clear the clean flag in both superblocks immediately. `lfs_gop_write()` assumes callers hold the segment lock and have prepared segment finfo state. Resize has tightly coupled Ifile, segment table, and free-space accounting; several hard failures still panic or note incomplete cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_vnops.c

## Scope
LFS vnode operation tables and LFS-specific wrappers around ULFS for creation, removal, directory operations, fsync, reclaim, strategy reads, pageout queue flushing, cleaner/control fcntls, file stats, mmap, and extattr stubs.

## Key Behavior
- Regular, special-device, and FIFO vnode operation tables install LFS handlers while reusing ULFS/genfs/specfs/fifofs behavior where possible.
- `lfs_makeinode()` allocates a new vnode/inode, writes the inode before entering the directory entry, handles SGID/whiteout bits, and rolls back link state on failure.
- `lfs_fsync()` writes pages with `VOP_PUTPAGES`, handles lazy sync by queueing pageout work, updates metadata unless data-only, optionally syncs device cache, and preserves modification state.
- `lfs_set_dirop()` / `lfs_unset_dirop()` reserve log space, exclude writers, enforce dirop count limits, and bracket all directory mutations.
- `lfs_mark_vnode()` / `lfs_unmark_vnode()` maintain VU_DIROP refs and active/completed dirop state.
- `lfs_create()`, `mknod()`, `symlink()`, `mkdir()`, `remove()`, `rmdir()`, and `link()` wrap ULFS mutations with read-only checks, dirop accounting, ordering, orphan handling, and explicit vnode reference cleanup.
- `lfs_getattr()` reports inode data without forcing time updates; `lfs_setattr()` checks LFS pressure before delegating to ULFS.
- `lfs_close()`, `lfsspec_close()`, and `lfsfifo_close()` update times and release log-wrap control when controlling root/Ifile descriptors close.
- `lfs_reclaim()` frees unlinked inodes, clears modification state, removes unexpected pageout state, rejects VU_DIROP reclamation, deregisters metadata, and returns pools.
- `lfs_strategy()` maps reads, avoids cleaner-write collision intervals, then dispatches device strategy I/O.
- `lfs_flush_dirops()` writes completed dirop vnodes into a segment; `lfs_flush_pchain()` writes vnodes queued for lazy/pageout flushing.
- `lfs_fcntl()` is the root/Ifile control interface for segwait, bmapv, markv, reclaim, Ifile file handles, rewind/invalidate/resize, wrap-stop/go/pass/status, file fragmentation stats, segment/file rewrite, cleaner info, seguse arrays, and autocleaner parameters.
- `lfs_filestats()` computes direct-block discontinuity metrics; `lfs_gop_size()` selects fragment/block-rounded write extents; extattr operations support ULFS1 only when compiled and otherwise return unsupported.

## Dependencies And State
Depends on ULFS lookup/readwrite/directory helpers, LFS reservation and segment writing, vnode cache, UVM page state, buffer cache, kauth, cleaner syscall helpers, and LFS control structures. Mutates inode link counts, dinode fields, `IN_*` flags, `VU_DIROP`, orphan state, pageout/dirop queues, cleaner sleep counts, and wrap-control state.

## Invariants And Risks
Directory updates must be bracketed by reservation and dirop marking so checkpoints do not persist inconsistent inode/directory ordering. VU_DIROP vnodes carry extra references until segment unlock safely clears them. `lfs_strategy()` assumes cleaner checkpoints are synchronous enough for interval checks to protect reads. `lfs_fcntl()` exposes privileged maintenance operations; mount-shutdown, inode bounds, segment bounds, and copyin/copyout checks are central.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_bmap.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_bmap.c

## Scope
ULFS logical-to-physical block mapping for LFS inodes, covering direct blocks, indirect traversal, run detection, snapshot sentinel handling, and construction of indirect block paths.

## Key Behavior
- `ulfs_bmap()` returns the underlying device vnode and maps a logical block via `ulfs_bmaparray()`.
- `ulfs_bmaparray()` handles ULFS1/ULFS2 direct and indirect block pointers, byte swapping, the special `UNWRITTEN == -2` value, holes, snapshot sentinel blocks, cached/read indirect blocks, and optional run-length calculation.
- `ulfs_getlbns()` computes the negative logical metadata block numbers and offsets needed for single, double, or triple indirect traversal.
- `ulfs_issequential()` supplies ordinary physical-adjacency run detection; callers may pass alternate callbacks such as LFS’s hole-oriented page-write predicate.

## Dependencies And State
Uses dinode direct/indirect arrays, `struct ulfsmount` geometry, LFS block-pointer conversion, buffer cache `incore/getblk`, `VOP_STRATEGY`, trace hooks, and `ulfs_bswap.h`.

## Invariants And Risks
The `UNWRITTEN` 32-bit value must be sign-preserved when promoted to 64-bit. Holes map to `-1` for ordinary reads, while snapshot files can map holes/sentinels specially. Negative logical numbering for indirect metadata is formula-sensitive; mistakes corrupt metadata lookup and allocation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_bswap.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_bswap.h

## Scope
Byte-order helper header for endian-independent ULFS/LFS on-disk field access.

## Key Behavior
- `ULFS_MPNEEDSWAP()`, `ULFS_FSNEEDSWAP()`, and `ULFS_IPNEEDSWAP()` report whether mount, filesystem, or inode fields require swapping when `LFS_EI` is enabled.
- `ulfs_rw16()`, `ulfs_rw32()`, and `ulfs_rw64()` return swapped or unchanged values.
- `ulfs_add16()`, `ulfs_add32()`, and `ulfs_add64()` read, add, and store values in on-disk byte order.

## Dependencies And State
Includes `sys/bswap.h` and optional kernel `opt_lfs.h`. Without `LFS_EI`, swap checks compile to constant false and accessors become simple casts.

## Invariants And Risks
All on-disk dinode, directory, and block-pointer accessors must pass the correct swap flag. Builds without endian-independent support intentionally cannot interpret swapped LFS images.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_bswap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_dinode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_dinode.h

## Scope
Small ULFS/LFS compatibility header for traditional inode mode bit constants.

## Key Behavior
Defines `IEXEC`, `IWRITE`, `IREAD`, `ISVTX`, `ISGID`, and `ISUID` with standard Unix permission and special-mode octal values.

## Dependencies And State
Includes `ufs/lfs/lfs.h` and supplies names expected by ULFS/LFS inode creation and attribute code.

## Invariants And Risks
The numeric values must remain aligned with standard mode bits; changing them would break permission, sticky, setgid, and setuid interpretation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_dinode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_dirhash.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_dirhash.c

## Scope
ULFS directory hash cache for LFS: large-directory lookup acceleration, free-space discovery, mutation tracking, memory recycling, sanity checking, sysctls, and lifecycle management.

## Key Behavior
- `ulfsdirhash_build()` decides eligibility, reserves global dirhash memory, allocates two-level hash/free-space arrays, scans every directory entry, inserts live names, and records compactable free space.
- `ulfsdirhash_free()` detaches a hash from an inode/list, releases hash arrays and block-free metadata, destroys its lock, and updates memory accounting.
- `ulfsdirhash_lookup()` probes by filename, boosts score/LRU position, optionally uses sequential lookup optimization, validates directory entries from buffers, returns entry and previous offsets, or tells callers to fall back to linear search.
- `ulfsdirhash_findfree()` finds a directory block with enough compactable space; `ulfsdirhash_enduseful()` identifies trailing fully free directory space.
- `ulfsdirhash_add()`, `remove()`, `move()`, `newblk()`, and `dirtrunc()` keep hash slots and block-free summaries synchronized with directory changes.
- `ulfsdirhash_checkblock()` optionally verifies actual directory-block contents against hash entries and free-space summaries.
- Static helpers hash names, adjust free summaries, locate/delete probe slots, find previous entries, and recycle low-score hashes to stay within `ulfs_dirhashmaxmem`.
- `ulfsdirhash_init()` computes default memory caps, initializes locks/pool caches/sysctls; `ulfsdirhash_done()` tears them down.

## Dependencies And State
Global state includes `ulfsdirhash_list`, `ulfsdirhash_lock`, memory cap/usage/check sysctls, and pool caches. Per-directory `struct dirhash` stores two-level hash tables, block-free summaries, first-free indexes, sequential lookup state, score, list state, and `dh_lock`. Depends on LFS directory accessors, ULFS block reads, vnode/inode state, `hash32`, kmem, pools, atomics, and sysctl.

## Invariants And Risks
Open addressing uses `DIRHASH_DEL`; deletion must preserve probe chains while trimming trailing deleted slots. Memory recycling can detach storage by setting `dh_hash` to `NULL`, so users must detect this and rebuild/fallback. Free-space summaries must match actual directory records or create/truncate decisions become unsafe. Old-format directories and removed directories are excluded from hashing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_dirhash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_dirhash.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_dirhash.h

## Scope
Public declarations for the ULFS directory hash structure, constants, table layout macros, free-space accounting parameters, and API.

## Key Behavior
- Defines `DIRHASH_EMPTY`, `DIRHASH_DEL`, `DIRALIGN`, `DH_NFSTATS`, score constants, and two-level hash table geometry.
- `DH_ENTRY()` indexes the two-level hash slot array.
- `struct dirhash` stores hash arrays, free-space summaries, first-free indexes, sequential lookup optimization state, score, list membership, list link, and its mutex.
- Declares build, lookup, free-space, trailing-space, mutation update, truncation, free, check, init, and done entry points.

## Dependencies And State
Used through `struct inode->i_dirhash` and coordinated with the global dirhash list protected by `ulfsdirhash_lock`. Requires `doff_t`, `kmutex_t`, `TAILQ_ENTRY`, `LFS_DIRHEADER`, and LFS directory sizing constants.

## Invariants And Risks
The locking split matters: most `struct dirhash` fields are protected by `dh_lock`, while global list membership is protected by `ulfsdirhash_lock`. Hash utilization is kept low; if mutation makes it too full or memory is recycled, the implementation discards the hash and relies on fallback/rebuild.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_dirhash.h -->