# Group Research: group_510_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_u_965eaaf81174

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is in subset A. All seven listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_dir.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_dir.c

## Purpose

`ufs_dir.c` implements UFS directory namespace manipulation: lookup, create, link, symlink insertion, rename, removal, directory emptiness checks, path-cycle prevention, and extended-attribute directory creation. It is the core directory-entry layer under the higher UFS vnode operations.

The file treats directory mutation as serialized by `i_rwlock`; its header notes that directories cannot be mmaped, so `i_contents` is redundant for some namespace serialization but is still used where inode fields and page/block operations require it.

## Main Interfaces

Public entry points include:

- `ufs_diraccess()` checks that an inode is a directory or attribute directory and delegates permission checks to `ufs_iaccess()`.
- `ufs_dirlook()` resolves a name to a held inode, using DNLC individual-name caching and optional whole-directory DNLC caching.
- `ufs_direnter_cm()` creates regular entries for create/mkdir/attribute-dir style operations, allocating a new inode when needed.
- `ufs_direnter_lr()` handles link, symlink, and rename insertion paths that already have a source inode.
- `ufs_dircheckforname()` scans a directory for an existing name and/or a free slot for a new entry.
- `ufs_dirmakeinode()` allocates and initializes an inode before it is linked into a directory.
- `ufs_dirremove()` removes names for unlink, rmdir, and rename cleanup.
- `blkatoff()` returns a mapped fbuf containing a directory block at a given offset.
- `ufs_dircheckpath()` walks `..` links to prevent moving a directory under itself.
- `ufs_xattrdirempty()` and `ufs_xattrmkdir()` implement extended-attribute directory support.

Important private helpers include `ufs_dirrename()`, `ufs_dirfixdotdot()`, `ufs_diraddentry()`, `dirprepareentry()`, `ufs_dirmakedirect()`, `ufs_dirempty()`, `ufs_dirpurgedotdot()`, `ufs_dirscan()`, `ufs_dirclrdotdot()`, `dirmangled()`, `dirbad()`, and `dirbadname()`.

## Directory Lookup And Caching

`ufs_dirlook()` first checks the ordinary DNLC. Negative entries use `DNLC_NO_VNODE` when `ufs_negative_cache` is enabled and the directory still has links. It then uses the directory-wide DNLC cache rooted at `i_danchor`; UFS packs a 32-bit inode number and a 32-bit directory offset into the DNLC directory handle with `INO_OFF_TO_H()`.

For large directories, controlled by `ufs_min_dir_cache`, the code attempts whole-directory caching through `dnlc_dir_start()`. Memory pressure disables caching briefly with `CD_DISABLED_NOMEM` and `ufs_dc_disable_duration`; directories that are too large are marked `CD_DISABLED_TOOBIG`.

Lookup has special handling for `"."` and `".."`. `"."` can hold the directory vnode directly. `".."` may require dropping the directory `i_rwlock` before `ufs_iget_alloced()` to avoid deadlock, then revalidating the entry with timestamps or a second directory cache lookup because the parent could have changed while the lock was dropped.

When scanning directory blocks, the code advances by `d_reclen`, validates alignment and record length, and optionally runs full checks with the `dirchk` tunable. Bad records are skipped to the next `DIRBLKSIZ` block; if whole-directory caching was active, the cache is purged because the scan no longer has reliable complete information.

## Entry Creation And Slot Management

`ufs_direnter_cm()` handles create/mkdir/attribute-dir operations. It rejects invalid entries in attribute directories, forbids slash in component names, handles `"."` and `".."` as existing entries, checks execute/write access, calls `ufs_dircheckforname()`, and creates a new inode with `ufs_dirmakeinode()` before installing the entry with `ufs_diraddentry()`.

`ufs_dircheckforname()` serves two roles: find an existing name and find usable free space. It can use the directory DNLC cache both for existing entries and free-space handles. Without cache coverage it scans the whole directory, tracks the last useful offset for possible truncation, and returns a `ufs_slot` describing either an existing entry, a reusable record, or a new block at the rounded-up end of the directory.

`dirprepareentry()` turns a returned slot into writable directory-entry space. If no slot exists, it allocates a new `DIRBLKSIZ` block with `BMAPALLOC()` and extends `i_size`. If a slot exists inside an occupied record, it splits the record by shrinking the old entry to `DIRSIZ(ep)` and placing the new entry in the remainder.

`ufs_diraddentry()` fills `d_namlen`, `d_name`, and `d_ino`, updates normal DNLC and directory DNLC state, records the directory block with `TRANS_DIR()`, writes it with `ufs_fbwrite()`, marks the parent inode changed, and may truncate trailing empty directory space when not logging.

## Inode Creation

`ufs_dirmakeinode()` allocates a UFS inode near the parent or preferred directory cylinder group, sets type/mode, UID/GID, legacy 16-bit `i_suid`/`i_sgid` compatibility fields, device numbers, set-GID inheritance, quota attachment, ACL inheritance, xattr flags, and timestamps. It writes the inode synchronously before a name points to it.

For new directories and attribute directories, `ufs_dirmakedirect()` allocates the first directory block, writes the `.` and `..` template, updates the parent link count for normal directories, logs the directory block, and writes it.

Extended attribute directories are built with `ufs_xattrmkdir()`, which uses lockfs protocol, synchronous mkdir transactions, special IFATTRDIR modes, optional attachment to the owning inode via `i_oeftflag`, xattr vnode flags, and a retry path that drains delayed deletes if inode exhaustion occurs under logging.

## Rename And Removal

`ufs_direnter_lr()` prepares link, symlink, and rename operations by syncing source inode data and indirect blocks before incrementing link counts and exposing directory entries. If insertion later fails, it rolls back the source link count for non-symlink operations.

`ufs_dirrename()` replaces an existing target entry with the source inode. It avoids deadlocks by try-locking peer inode contents locks, checks same-filesystem constraints, sticky-directory permissions, type compatibility, mountpoint busy state, target-directory emptiness, and then rewrites the target `d_ino` before decrementing the overwritten inode. Directory rename across parents calls `ufs_dirfixdotdot()` to update the child `..` entry and adjust parent link counts.

`ufs_dirremove()` handles unlink/rmdir removal. It rejects empty names and removal of `"."` or `".."`, checks directory write/search access, obtains the target inode, handles mounted directories through `vn_vfsrlock()`, try-locks child directory `i_rwlock` to avoid rename cycles, applies sticky-directory checks, validates rmdir conditions, removes DNLC entries, clears `d_ino`, coalesces directory free space, logs/writes the directory block, decrements link counts, and purges `.`/`..` for removed directories.

`ufs_dircheckpath()` walks upward through `..` entries from a target directory to ensure a source directory is not in the target path. It uses try-lock/backoff behavior to avoid rename deadlocks and returns `EAGAIN` if a writer-wanted state could produce a cycle.

## Invariants And Dependencies

Key invariants:

- Callers generally hold target directory `i_rwlock` as writer for mutation.
- Directory block updates must be recorded through `TRANS_DIR()` before `ufs_fbwrite()`.
- New inodes are written before directory entries point to them.
- Directory rename must keep target entry replacement, target link-count decrements, and `..` repair ordered carefully.
- Whole-directory DNLC cache entries carry previous-entry offsets; cache updates must track record splitting/coalescing.
- Attribute directories use IFATTRDIR semantics and have different quota/link-count behavior.

This file depends on inode allocation and truncation (`ufs_ialloc`, `ufs_itrunc`, `ufs_iupdat`), block mapping (`BMAPALLOC`, `blkatoff`, `ufs_rdwri`), transaction logging (`TRANS_DIR`, `TRANS_INODE`), DNLC directory-cache APIs, quota locks (`vfs_dqrwlock`), xattr/ACL inheritance, vnode mount locking, and lockfs support.

## Research Notes

Audit hotspots are rename rollback after `..` repair, DNLC directory-cache offset correctness during split/coalesce, rmdir behavior with hard-linked directories or attribute directories, lock dropping around `".."` lookup, and any path that returns `EAGAIN` for deadlock avoidance. Directory corruption handling intentionally skips bad records rather than repairing them in place.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_directio.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_directio.c

## Purpose

`ufs_directio.c` implements UFS direct I/O for aligned file reads and writes that bypass the page cache and issue physical buffer I/O directly to the backing device or snapshot strategy layer. It also initializes direct-I/O kstats and a kmem cache for reusable `buf_t` wrappers.

The file is performance-oriented but correctness-sensitive because it must coordinate page cache invalidation, mmap exclusion, block allocation, partial failures, POSIX synchronous data-integrity constraints, snapshots, and user-page locking.

## Main Interfaces

Public entry points include:

- `directio_bufs_init()` creates `directio_buf_cache`.
- `ufs_directio_init()` installs the `ufs/directio` kstat and allocates the private zero buffer used for hole reads.
- `ufs_directio_write()` attempts direct writes, returning `DIRECTIO_SUCCESS` or `DIRECTIO_FAILURE` through `statusp`.
- `ufs_directio_read()` attempts direct reads, also reporting success/failure through `statusp`.

Private helpers include `directio_buf_constructor()`, `directio_buf_destructor()`, `directio_wait_one()`, `directio_wait()`, `directio_start()`, and `directio_hole()`.

## Direct I/O Buffers And Accounting

Each physical I/O request uses a `struct directio_buf` containing a `buf_t`, target address, byte count, and reverse-order list link. The buffer is initialized once by `bioinit()` in the slab constructor and finalized with `biofini()` in the destructor.

`directio_start()` fills device, logical block, byte count, user address, process, vnode, flags, and optional page shadow list. It issues the I/O through `fssnap_strategy()` when snapshots are present, otherwise `bdev_strategy()`. It updates logical/physical read/write kstats and per-LWP block counters.

`directio_wait_one()` waits with `biowait()`, computes an approximate completed-byte count for residual reporting, clears transient `buf_t` flags, and frees the wrapper. `directio_wait()` drains the reverse-order request list, preserving the first error.

## Write Path

`ufs_directio_write()` first declines direct I/O when the feature is disabled, the file is mmaped, the request exceeds `uio_llimit`, offset/resid are not sector aligned, the target is not a regular file, or the inode is the quota inode.

For synchronous allocating writes, it avoids direct I/O if the write would extend the file or if the file has holes, because synchronous allocation under direct mode is slow and historically risky. For misaligned iovec lengths or bases, it may allocate a temporary aligned kernel buffer and copy user data into it before continuing.

For non-rewrite writes, the function allocates blocks with `bmap_write()` before issuing physical I/O. It extends `i_size` as blocks are allocated, sets large-file superblock state when crossing `MAXOFF32_T`, and rolls back with `ufs_itrunc()` if allocation fails after partial growth.

Before direct writes it invalidates cached pages with `VOP_PUTPAGE(..., B_INVAL, ...)`, upgrading `i_contents` to writer when needed. Shared-lock rewrites are tracked by `ufs_shared_writes`, `ufs_cur_writes`, and `ufs_maxcur_writes`; if cached pages appear during shared direct writes, they are invalidated afterward to avoid stale cache data.

Actual I/O loops over iovecs and `vfs_ioclustsz` chunks, locks user pages with `as_pagelock(..., S_READ)`, maps file offsets to contiguous disk extents with `bmap_read()`, issues one or more `directio_start()` calls, waits for completion, unlocks pages, updates `uio` state, and adjusts residuals based on bytes completed.

If `FDSYNC` or `ufs_force_posix_sdi` applies to a rewrite, the code verifies that the write can be a single contiguous request; otherwise it upgrades to exclusive `i_contents` locking so concurrent readers cannot observe non-atomic data-integrity behavior.

## Read Path

`ufs_directio_read()` similarly declines direct I/O when disabled, mmaped, unaligned, or iovec bases/lengths are unsuitable. It treats reads starting at or beyond EOF as direct-I/O success with no residual change so the cached read path does not repeat EOF logic. Reads that would cross EOF are shortened, but only if the shortened length remains sector aligned.

The read path invalidates cached pages, locks destination pages with `as_pagelock(..., S_WRITE)`, maps extents with `bmap_read()`, and issues physical reads. Holes are handled by `directio_hole()`, which moves zeros from the private zero buffer into the caller's `uio` rather than issuing disk I/O.

On completion, `uio_resid` is reduced by completed bytes. The implementation reports partial failures by tracking bytes read or written independently from driver `b_resid`, because the comments do not assume all disk drivers maintain `b_resid` reliably.

## Invariants And Dependencies

Key invariants:

- Direct I/O is only attempted for sector-aligned offsets and lengths.
- Mapped files are excluded via `i_mapcnt`.
- Page cache data must be invalidated before bypass I/O proceeds.
- Allocating writes must allocate backing blocks before physical writes.
- Hole reads synthesize zeroes; direct writes must not target holes unless allocation has already handled them.
- Snapshot-aware filesystems route I/O through `fssnap_strategy()`.

This file depends on UFS block mapping (`bmap_read`, `bmap_write`, `bmap_has_holes`), truncation (`ufs_itrunc`), vnode page flushing (`VOP_PUTPAGE`), VM page locking (`as_pagelock`/`as_pageunlock`), buf strategy I/O, snapshots, UFS transaction macros for inode updates, and UFS mount fields such as `vfs_ioclustsz`.

## Research Notes

The main risks are stale page-cache interaction, residual accounting after partial physical I/O failure, direct write rollback after preallocation extends `i_size`, and the shared-lock rewrite path. The file is deliberately conservative: most unsuitable cases return success with `DIRECTIO_FAILURE` so callers can fall back to normal cached I/O.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_directio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_extvnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_extvnops.c

## Purpose

`ufs_extvnops.c` provides UFS support for external vnode-style data operations using `fdbuffer_t`. It is designed for reads/writes where data movement can be done through filesystem block mappings and device strategy I/O rather than ordinary user `uio` paths.

The file exposes two operations: one for read/write when file size and allocation must not change, and one for allocation plus optional I/O when file size or sparse regions may need to change.

## Main Interfaces

- `ufs_rdwr_data()` reads or writes existing allocated file data into an `fdbuffer_t`. It refuses to allocate blocks or grow the file.
- `ufs_alloc_data()` allocates backing store and optionally performs I/O through an `fdbuffer_t`; it can grow the file and fill holes.

Both functions obey lockfs through `ufs_lockfs_begin_getpage()`, use `i_contents` locking, coordinate with quota locking through `vfs_dqrwlock`, use `bmap_read()`/`bmap_write()`, and route physical I/O through snapshots when present.

## `ufs_rdwr_data()`

`ufs_rdwr_data()` begins the getpage-oriented lockfs protocol, caps I/O length to `i_size`, and takes `vfs_dqrwlock` plus `i_contents` as reader. It then loops over the requested range, translating file offsets to disk blocks with `bmap_read()`.

For allocated extents, it builds fdbuffer I/O buffers with `fdb_iosetup()`, fills device/block/vnode/offset fields, and submits them through `fssnap_strategy()` or `bdev_strategy()`. Synchronous requests wait with `biowait()` and finish each buffer with `fdb_iodone()`.

For holes, reads add a hole record to the fdbuffer with `fdb_add_hole()`. Writes are not expected to encounter holes; the code asserts that and returns `ENOSPC` if a write hole is seen.

Asynchronous operation calls `fdb_ioerrdone()` when no more I/O will be added. If at least one async I/O was started, the function returns zero and lets completion carry errors through the fdbuffer path.

## `ufs_alloc_data()`

`ufs_alloc_data()` is the heavier path because it can allocate space and grow the file inside a UFS log transaction. It begins lockfs, attempts `TRANS_TRY_BEGIN_CSYNC()` for `TOP_GETPAGE`, and returns `EDEADLK` for async fdbuffer callers if the transaction cannot begin without blocking.

With `i_contents` as writer, it walks filesystem blocks covering the requested range. If a block extends beyond EOF, it calls `bmap_write(..., BI_ALLOC_ONLY, ...)`, optionally records holes for bytes beyond old EOF, performs I/O for the pre-existing tail if needed, updates `i_size`, logs the inode, and sets `FSLARGEFILES` when the file crosses the legacy 2 GB threshold.

If the range is inside EOF, allocated blocks can be read/written through fdbuffer I/O. Holes are allocated with `bmap_write()` and reported as holes to the fdbuffer so callers know those bytes were logically absent before allocation.

On allocation failure after file growth, the function truncates back to `old_i_size`. Before returning it rounds `*len` to a fragment or block boundary, invalidates cached pages with `VOP_PUTPAGE(..., B_INVAL, ...)`, closes the transaction, and ends lockfs.

## Invariants And Dependencies

Key invariants:

- `ufs_rdwr_data()` must not allocate blocks or change file length.
- `ufs_alloc_data()` must be used when allocation or growth may occur.
- Writes through these paths bypass the page cache but still invalidate pages before completion.
- Async fdbuffer callers need `fdb_ioerrdone()` even on early lockfs/transaction failures.
- File-size growth is logged and rolled back on error.

Dependencies include `fdbuffer` APIs, lockfs getpage protocol, UFS block mapping/allocation, UFS transactions, snapshot strategy I/O, inode timestamps/sequence updates, large-file superblock state, and page invalidation.

## Research Notes

This file is a specialized bridge between UFS block allocation and fdbuffer consumers. It is smaller than the ordinary vnode I/O path but sensitive to transaction begin semantics, async error signaling, and cache invalidation after bypass I/O.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_extvnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_filio.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_filio.c

## Purpose

`ufs_filio.c` implements UFS filesystem-specific ioctl helpers. These operations expose private or semi-private controls for inode-open-by-number, access-time setting, delayed I/O, filesystem flushing, busy checks, direct-I/O toggling, tunables, hole/data seeking, and compressed-file marking.

Many routines are explicitly described as tailored to historical consumers such as Metamucil or contract-private backup products, so they are part of the compatibility/control surface rather than normal VFS behavior.

## Main Interfaces

- `ufs_fioio()` opens a file by inode number and generation.
- `ufs_fiosatime()` sets access time without changing change time.
- `ufs_fiogdio()` and `ufs_fiosdio()` get/set delayed-I/O state.
- `ufs_fioffs()` flushes a whole filesystem.
- `ufs_fioisbusy()` reports whether a vnode has external references or mappings.
- `ufs_fiodirectio()` toggles per-inode direct-I/O mode.
- `ufs_fiotune()` updates mounted filesystem tunables.
- `ufs_fio_holey()` implements seek-hole/seek-data support.
- `ufs_mark_compressed()` marks a regular file as compressed.

## Ioctl Behaviors

`ufs_fioio()` is privileged. It copies in a `fioio` structure, validates the inode number against filesystem bounds, obtains the inode with `ufs_iget()`, checks generation and allocation state, allocates a file descriptor with large-file semantics, checks read access, opens the vnode, and returns the descriptor to userland. On error it releases the allocated file structure and vnode hold.

`ufs_fiosatime()` is privileged and either sets atime to the current unique UFS time or to a copied-in timeval, with ILP32/LP64 conversion and overflow validation. It marks `IMODACC` so the access-time change is persisted without treating ctime as changed.

`ufs_fiogdio()` returns mount delayed-I/O state. `ufs_fiosdio()` changes it only for non-logging filesystems, quiescing the filesystem, flushing data, updating `vfs_dio`, and setting `fs_clean` to `FSSUSPEND` or `FSACTIVE` for writable non-bad/non-log filesystems.

`ufs_fioffs()` flushes the filesystem from ioctl or VFS entry points. It suspends the delete thread, quiesces lockfs, may make a non-rollable log rollable and restart reclaim, flushes all dirty data/metadata with `ufs_flush()`, then resumes delete processing.

## Utility Controls

`ufs_fioisbusy()` purges DNLC references when `v_count > 1`, then reports busy if the vnode has more than the caller's reference or if `i_mapcnt` is nonzero.

`ufs_fiodirectio()` sets or clears `IDIRECTIO` under `i_contents` and `i_tlock` for `DIRECTIO_ON` or `DIRECTIO_OFF`.

`ufs_fiotune()` validates and applies mounted filesystem tunables (`maxcontig`, `rotdelay`, `maxbpg`, `minfree`, `optim`), recomputes `vfs_ioclustsz` and `vfs_minfrags`, and writes the superblock through UFS transaction macros if the filesystem is writable.

`ufs_fio_holey()` implements `_FIO_SEEK_HOLE` and `_FIO_SEEK_DATA`. It returns `ENXIO` when the starting offset is at or beyond EOF, fast-paths no-hole files by returning EOF as the virtual hole, and otherwise uses `bmap_find()` to locate the next hole or data extent.

`ufs_mark_compressed()` validates regular-file type, sets `ICOMPRESS`, logs the inode, marks ctime/sequence changes, and updates the inode asynchronously when logging is not active.

## Invariants And Dependencies

Key invariants:

- Configuration-changing ioctls require `secpolicy_fs_config()`.
- Delayed-I/O changes are blocked under logging and require quiesce plus flush.
- Filesystem flush must coordinate with lockfs, delete thread, log rolling, reclaim state, and superblock updates.
- Hole/data seeking relies on UFS block mapping rather than byte-by-byte scanning.

Dependencies include lockfs (`ufs_quiesce`, `ufs_flush`), inode cache lookup, DNLC purge, UFS transaction macros, logmap rolling, quota/reclaim/delete threads, block mapping (`bmap_has_holes`, `bmap_find`), and privilege/policy checks.

## Research Notes

This file is a control plane for operational and legacy features. The highest-risk paths are those that change mount-wide state (`ufs_fiosdio`, `ufs_fioffs`, `ufs_fiotune`) because they interact with lockfs, logging, clean flags, and background delete/reclaim threads.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_filio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_inode.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_inode.c

## Purpose

`ufs_inode.c` implements UFS in-core inode cache management, inode lookup/loading, inactive handling, inode writeback, truncation/block freeing, permission checks, inode scanning, and timestamp maintenance. It is the main bridge between on-disk `dinode` records and live UFS `inode`/`vnode` objects.

It also initializes several global UFS facilities: inode kstats, idle/delete queue thresholds, inode hash tables, quota support, fix-on-panic support, shadow inode cache, direct I/O, and logging.

## Main Interfaces

Public entry points include:

- `ufs_iinit()` initializes inode subsystem state, queues, kstats, and related UFS modules.
- `ufs_alloc_inode()` and `ufs_free_inode()` allocate/free in-core inode objects.
- `ufs_iget()` returns a held inode by inode number.
- `ufs_iget_alloced()` is the stricter lookup variant that rejects free/unlinked inodes.
- `ufs_reset_vnode()` derives vnode flags from inode mode/type.
- `ufs_iinactive()` handles last-reference inactive processing.
- `ufs_iupdat()` writes dirty inode fields to disk or the transaction log.
- `ufs_itrunc()` grows or truncates file storage and frees blocks.
- `ufs_iaccess()` performs read/write/execute permission checks.
- `ufs_rmidle()` removes an inode from idle queues.
- `ufs_scan_inodes()` walks the inode hash and calls a callback safely.
- `ufs_imark()` and `ufs_itimes_nolock()` maintain unique timestamps.

Private helpers include `ufs_inode_kstat_update()`, `ufs_inode_cache_constructor()`, `ufs_inode_cache_destructor()`, `ihinit()`, `ufs_iget_internal()`, and `indirtrunc()`.

## Inode Cache And Lookup

`ufs_iinit()` validates write-throttling tunables (`ufs_HW`, `ufs_LW`), bounds `ufs_ninode`, computes idle queue limits, starts idle and hlock threads, initializes hash tables, quotas, fix-on-panic, shadow inode cache, direct I/O, and logging. It installs the `ufs/inode_cache` kstat.

The inode kmem constructor allocates a vnode, assigns UFS vnodeops, initializes `i_rwlock`, `i_contents`, `i_tlock`, directory DNLC anchor, and write CV. `ufs_alloc_inode()` resets per-inode fields, associates the vnode with the mount, sets `VROOT` for the root inode, and calls `vn_exists()`.

`ufs_iget_internal()` first searches the inode hash by device and inode number, ignoring stale inodes. Cache hits take a vnode hold, remove the inode from idle queues if needed, reset vnode flags, and return. Cache misses allocate a placeholder inode, insert it into the hash under lock, read the on-disk dinode, copy `di_ic`, restore old 16-bit UID/GID compatibility fields, decode device numbers, set vnode type, load shadow ACL state when present, attach quotas when appropriate, and call `TRANS_MATA_IGET()`.

The `validate` mode used by `ufs_iget_alloced()` rejects type-zero or unlinked inodes, marks them stale, releases them, and logs a note recommending fsck.

## Inactive And Queue Handling

`ufs_iinactive()` runs when the vnode is no longer referenced. It purges directory DNLC state, takes `i_contents` writer, rechecks `v_count` under vnode lock, and handles three broad cases:

- Inodes from a forcibly unmounted filesystem (`i_ufsvfs == NULL`) are unhashed/clean and can be freed directly.
- Writable unlinked inodes are deleted immediately on non-logging filesystems or queued to the mount delete thread under logging, unless lockfs has `NOIDEL`.
- Other inodes go to idle queues. Inodes with pages or fast symlinks go to useful idle queues; others go to junk queues and get `IJUNKIQ`.

`ufs_rmidle()` removes an inode from idle queues, restores `IREF`, and updates useful/junk queue counters. `ufs_scan_inodes()` walks every hash chain while taking vnode holds only for inodes in the requested filesystem, drops hash locks around callback work, and optionally try-locks inode contents to avoid blocking.

## Inode Update And Timestamping

`ufs_iupdat()` writes dirty inode metadata. It skips forcibly unmounted or stale inodes, ignores writes on read-only filesystems after clearing dirty flags, calls `ufs_notclean()`, reads the containing inode block, applies `ITIMES_NOLOCK()`, logs access-time-only deltas when needed, updates legacy UID/GID and device-number encodings, copies `i_ic` into the dinode, clears unused fast-symlink block pointers, and either logs the dinode sector or writes the buffer synchronously/asynchronously.

If a prior asynchronous inode update left `IBDWRITE`, a later synchronous request flushes the inode block even if no new flags are set.

`ufs_imark()` maintains monotonically unique 32-bit UFS timestamps protected by `ufs_iuniqtime_lock`, clamps at `TIME32_MAX`, increments `i_seq` for deferred sequence updates, updates atime/mtime/ctime according to `IACC`, `IUPD`, and `ICHG`, and resets `i_diroff` on ctime changes. `ufs_itimes_nolock()` converts pending timestamp flags into `IMOD` or `IMODACC` unless noatime suppresses an access-only update.

## Truncation And Block Freeing

`ufs_itrunc()` supports regular files, directories, attribute directories, zero-length symlinks, and shadow inodes. It checks max file size, handles free-time generation updates, clears fast-symlink state, grows files through `BMAPALLOC()`, zeroes bytes beyond old EOF on growth, sets large-file superblock state, and returns after successful extension.

For shrinking, it invalidates or zeroes pages beyond the new EOF, ensures the partial final block is allocated and resident so `pvn_vpzero()` can clean it, writes the shortened inode before freeing blocks, and then frees indirect and direct blocks in reverse order. `indirtrunc()` recursively cleans indirect blocks, logging zeroed pointer ranges before freeing child blocks.

The truncation code keeps a temporary copy of the old inode block pointers, clears pointers in the real inode first, synchronously updates the inode when not logging, frees blocks from the copy, verifies real and copy pointers remain consistent, adjusts `i_blocks`, and updates quotas with negative block deltas.

## Permissions

`ufs_iaccess()` enforces read-only filesystem behavior for writes except character/block devices and FIFOs. If UFS ACL state is present, it delegates to `ufs_acl_access()`. Otherwise it selects owner/group/other bits based on credential UID and group membership and calls `secpolicy_vnode_access2()`.

## Invariants And Dependencies

Key invariants:

- Inode hash insertion uses a placeholder under `i_contents` writer so scanners and lookups see initialized state.
- `ISTALE` inodes are ignored by new lookups and eventually freed.
- Unlinked logged inodes are queued rather than deleted synchronously.
- Inode disk updates must preserve old UID/GID and device encoding compatibility.
- File shrinking writes the shortened inode before freeing blocks to remain crash-tolerant.
- Timestamps are unique within the filesystem's 32-bit on-disk time limits.

Dependencies include UFS buf I/O, page-cache invalidation and dirty walks, transaction logging, quotas, DNLC, ACL/shadow inode support, vnode lifecycle APIs, idle/delete thread queues, superblock clean-state helpers, and block allocator/free routines.

## Research Notes

This file is a major correctness center. The most important audit areas are stale inode races during lookup/inactive, queued delete behavior under lockfs/logging, `ufs_itrunc()` ordering, fast-symlink dinode sanitization, `IBDWRITE` synchronous flush semantics, and 2038-era timestamp clamping.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_lockfs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_lockfs.c

## Purpose

`ufs_lockfs.c` implements UFS filesystem locking, quiescing, flushing, thawing, and reconciliation. It backs the `lockfs` ioctl interface and the internal lockfs begin/end protocol used by UFS vnode operations to cooperate with filesystem suspension, backup locks, hard locks, error locks, and getpage faults.

The file is a state-machine layer over the mount's `ulockfs` structure. It tracks active vnode operations, fallocate-style operations, recursive VOP calls through thread-specific data, pending quiesce requests, and lock compatibility masks.

## Main Interfaces

Lock state and ioctl operations:

- `ufs_fiolfs()` and `ufs__fiolfs()` apply a new lockfs state.
- `ufs_fiolfss()` reports current lockfs state.
- `ufs_getlfd()` validates lock requests and lock keys.
- `ufs_freeze()` installs a new requested lock state in `ulockfs`.
- `ufs_quiesce()` sets softlock state and waits for active operations to drain.
- `ufs_thaw()` performs lock-type-specific cleanup and wakes blocked threads.

Flush and reconciliation:

- `ufs_flush_inode()` pushes and invalidates one inode.
- `ufs_flush()` flushes dnlc, delete/idle queues, quotas, inodes, superblock, block-device pages, buffers, and log transactions.
- `ufs_reconcile_fs()` reloads safe superblock fields from disk.
- `ufs_reconcile_inode()` reloads safe inode fields from disk.
- `ufs_reconcile()` coordinates flush, superblock reconciliation, inode reconciliation, and a second flush.

VOP protocol:

- `ufs_lockfs_begin()` starts normal lockfs protocol for a VOP.
- `ufs_lockfs_trybegin()` is the non-blocking variant.
- `ufs_lockfs_begin_getpage()` is the getpage/page-fault-specific variant.
- `ufs_lockfs_end()` terminates protocol and decrements active counters.
- `ufs_check_lockfs()` blocks or rejects operations based on the current lock mask.
- `ufs_lockfs_tsd_destructor()` frees per-thread recursion records.

## Quiesce And Flush

`ufs_quiesce()` obtains the current thread's lockfs TSD record, increments `lwp_nostop` to avoid `/proc` stop deadlocks while a softlock is pending, sets `SLOCK`, and waits until `ul_vnops_cnt` and `ul_falloc_cnt` drain. Fallocate threads have special handling so one fallocate flow can proceed once other VOPs drain and no fallocate write lock is already held.

`ufs_flush()` purges DNLC entries for the filesystem, drains delete and idle queues, syncs quota records, scans inodes with `ufs_flush_inode()`, writes superblock/summary state when dirty, invalidates block-device pages and buffers, drains queues again, checks clean state, and if logging is active commits and rolls the log unless `LDL_NOROLL` prevents it.

`ufs_thaw()` adjusts behavior for write, hard, and error locks. For write locks it flushes twice, blocks access-time/deletion side effects, invalidates buffers, and checks no mlocked pages remain. For hard/error locks it forcibly invalidates inode pages and buffers. When unlocking from `NOIDEL`, it flushes deleted files before restoring normal access/deletion/superblock behavior.

## Applying Lockfs State

`ufs__fiolfs()` validates the requested lock, guards against unmounted filesystems, prevents write/error locks when accounting or swap files are active, suspends reclaim and delete threads, increments `ufs_quiesce_pend`, rejects incompatible current states, validates lock keys, saves the prior state, freezes the new state, marks lockfs busy, and quiesces active VOPs.

It handles error-lock transitions specially. Setting an error lock marks the filesystem bad and disables delayed I/O; unlocking or relocking error locks passes state into reconciliation and fix-on-panic cleanup. A user-applied error lock can call `ufs_fault()` unless on-error panic handling is configured.

After quiescing, it reconciles if the filesystem had been write-locked or error-locked, flushes dirty state, thaws to the new state, clears modified/busy flags, frees old comments, wakes pollers, resumes delete/reclaim threads, and returns. On failure it restores the old lock state unless hard-locked and avoids `ufs_thaw()` after signal interruption during quiesce because that path can deadlock with getpage.

## Reconciliation

`ufs_reconcile_fs()` reads the on-disk superblock and verifies structural fields that must not change: block layout, sizes, shifts, geometry, postbl format, and magic. It refuses unsafe states for error-lock unlocks, reloads summary info, updates allowed mutable fields, restarts reclaim when needed, and lets on-disk bad/clean/error state override in-memory state under defined conditions.

`ufs_reconcile_inode()` rejects in-core inodes that still have dirty flags after quiesce/flush. It reads the on-disk dinode, verifies immutable identity fields such as mode, generation, UID, and GID, then refreshes allowed mutable fields: size, flags, blocks, link count, and direct/indirect block pointers.

`ufs_reconcile()` first flushes as much in-memory state as possible, reconciles superblock and all relevant inodes, then flushes again to discard potentially stale allocation data.

## VOP Begin/End Protocol

`ufs_lockfs_begin()` detects recursive VOPs using a thread-specific list of `ulockfs_info_t` records and bypasses lock accounting for recursive calls or raw internal lockfs paths. For top-level VOPs it increments either `ul_vnops_cnt` or `ul_falloc_cnt`, checks current lock state and global `ufs_quiesce_pend`, may block in `ufs_check_lockfs()`, records the active filesystem in TSD, and sets `T_DONTBLOCK`.

`ufs_lockfs_end()` invalidates the TSD record, clears `T_DONTBLOCK` when returning from the top-level VOP, decrements the fallocate or normal VOP counter, clears fallocate state when needed, and broadcasts when counters reach zero.

`ufs_lockfs_trybegin()` mirrors begin logic but returns `EAGAIN` instead of blocking when the current lock conflicts with the requested operation. `ufs_lockfs_begin_getpage()` selects a read or write lock mask based on mapping type and access; it may strip `PROT_WRITE` from read faults so later write faults block correctly under write locks.

`ufs_check_lockfs()` waits while the current `ul_fs_lock` conflicts with the requested mask, respecting `T_DONTPEND`, `T_WOULDBLOCK`, hard/error-lock EIO behavior, interruptibility, and `vfs_dontblock`.

## Invariants And Dependencies

Key invariants:

- Lockfs quiesce must stop new conflicting VOPs and wait for active counters to drain.
- Recursive VOPs on the same filesystem must not self-deadlock through lockfs accounting.
- Hard/error locks can force page and buffer invalidation; write locks require clean, unmapped state.
- Reconciliation only accepts on-disk changes to an explicit set of mutable fields.
- Delete and reclaim threads are suspended outside the lockfs mutex/protocol.
- `ufs_quiesce_pend` is used as a global signal to prevent livelock while a quiesce request is trying to drain VOPs.

Dependencies include UFS vnode operation wrappers, transaction/logmap APIs, inode scanner, quota sync, DNLC purge, delete/idle/reclaim threads, fix-on-panic helpers, VM page invalidation, block-device buffer cache flushing, accounting/swap checks, poll notification, and thread-specific data.

## Research Notes

This is one of the highest-complexity UFS coordination files. Audit attention should focus on counter balance in begin/end error paths, recursive VOP TSD reuse, quiesce interruption handling, fallocate-specific state, reconciliation trust boundaries, and lock transitions involving error or hard locks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_lockfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_log.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_log.c

## Purpose

`ufs_log.c` is a small ioctl wrapper layer for enabling, disabling, and querying UFS logging. It delegates the real logging implementation to the logging subsystem while handling user/kernel copy semantics and status reporting.

## Main Interfaces

- `ufs_fiologenable()` copies in a `fiolog_t`, calls `lufs_enable()`, copies the possibly updated structure back out, and returns the logging operation status unless copyout fails.
- `ufs_fiologdisable()` copies in a `fiolog_t`, calls `lufs_disable()`, copies the result back out, and returns the operation status unless copyout fails.
- `ufs_fioislog()` reports whether the mount has an active `vfs_log`.

## Behavior

The enable and disable paths use `ddi_copyin()` and `ddi_copyout()` with ioctl flags, so they support kernel/user ioctl contexts consistently. They return `EFAULT` on copy failure and otherwise preserve the result from the lower logging function.

`ufs_fioislog()` reads `VTOI(vp)->i_ufsvfs` and checks `vfs_log`. For kernel ioctls (`FKIOCTL`) it writes directly to `*islog`; for user callers it uses `suword32()` and returns `EFAULT` if the user write fails.

## Invariants And Dependencies

Key invariants:

- Logging state is represented at the mount level by `ufsvfs_t.vfs_log`.
- Enable/disable request structures are round-tripped to the caller because lower layers may update fields.
- User-space status writes must use safe copyout helpers.

Dependencies include `lufs_enable()`, `lufs_disable()`, UFS inode-to-mount conversion, ioctl flag conventions, and low-level safe copy helpers.

## Research Notes

This file intentionally contains almost no policy. Permission checks, log allocation, lockfs interaction, and mount-state changes live below `lufs_enable()` and `lufs_disable()`. The main thing to verify around this wrapper is copyin/copyout ordering: a successful logging operation can still be reported as `EFAULT` if the updated structure cannot be copied back.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_log.c -->