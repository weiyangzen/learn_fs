# Group Research: FreeBSD UFS core vnode, lookup, quota, and mount support

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_inode.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_inode.c

## Purpose
Implements UFS inode lifecycle vnode operations: deciding whether inactive processing is required, handling the last vnode reference, and reclaiming inode memory/state.

## Key entry points
- `ufs_need_inactive()` decides whether `VOP_INACTIVE` must run. It skips read-only inodes, but requests inactive processing for pending page-queue flushes, deleted/unlinked inodes, softdep-effective unlink state, dirty inode flags, non-empty deleted files including UFS2 extended data, and attached quota references.
- `ufs_inactive()` performs last-reference cleanup. It handles quota sync, GEOM journal close, suspended-write coordination, truncation of unlinked files, quota inode accounting release, extended-attribute inactive cleanup, inode mode clearing, block/inode freeing through `UFS_VFREE`, timestamp updates, and vnode recycling.
- `ufs_reclaim()` tears down the in-core inode: releases dquots, frees directory hash state, promotes lazy modification to real modification, updates the inode, removes the vnode from the hash, clears `v_data` under the vnode interlock, and frees the inode through `UFS_IFREE`.

## Important behavior
- File deletion is split across truncation, link-count state, soft updates, and final inode free. `i_effnlink` is significant under soft updates, while `i_nlink` is the on-disk link count.
- `vn_start_secondary_write()` protects deletion/truncation against filesystem suspension. If the filesystem is suspended and the vnode is not doomed, `VI_OWEINACT` is set so inactive work can be retried later.
- UFS2 extended size contributes to the deletion truncation decision via `di_extsize`.
- Quotas are synchronized before inactive vnodes leave the active list, because inactive quota state is otherwise no longer checked.

## Dependencies
Uses UFS operation indirection from `ufsmount.h`: `UFS_RDONLY`, `UFS_TRUNCATE`, `UFS_UPDATE`, `UFS_VFREE`, `UFS_IFREE`. Optional paths depend on `QUOTA`, `UFS_DIRHASH`, `UFS_EXTATTR`, `UFS_GJOURNAL`, and soft updates.

## Research notes
This file is the cleanup boundary for UFS vnode lifetime. Most actual allocation, truncation, update, and free behavior is delegated to filesystem-specific callbacks, allowing common UFS code to serve UFS1/UFS2 and FFS-specific implementations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_lookup.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_lookup.c

## Purpose
Implements UFS directory lookup and directory-entry manipulation. This is the core bridge between namei/pathname resolution and on-disk UFS directory blocks.

## Key entry points
- `ufs_lookup()` is the `VOP_CACHEDLOOKUP` wrapper around `ufs_lookup_ino()`.
- `ufs_lookup_ino()` searches a directory for a component, optionally returning a vnode or just an inode number. It also records mutation state in directory inode fields for later create, delete, rename, and whiteout operations.
- `ufs_makedirentry()` builds a `struct direct` from an inode and component name, handling old UFS directory format quirks.
- `ufs_direnter()` inserts a new directory entry, either by allocating a new directory block or compacting/reusing free space in an existing block.
- `ufs_dirremove()` removes or whiteouts a directory entry and adjusts link counts, softdep state, dirhash state, and disclosure-sensitive name metadata.
- `ufs_dirrewrite()` changes an existing directory entry to point to a new inode, used heavily by rename.
- `ufs_dirempty()` verifies a directory contains only valid `.` and `..` entries, optionally ignoring whiteouts.
- `ufs_checkpath()` walks `..` links to prevent directory renames from creating cycles.
- Diagnostic tracker functions validate ownership of `i_offset`, `i_count`, and `i_endoff` when `DIAGNOSTIC` is enabled.

## Lookup algorithm
The lookup path uses the name cache through `vfs_cache_lookup()` and falls back here for cache misses. It:
- Verifies the directory is still linked via `i_effnlink`.
- Creates a VM object for directory VMIO when needed.
- Uses `ufsdirhash` opportunistically for large directories.
- Otherwise scans directory blocks linearly, optionally starting from cached `i_diroff` for ordinary lookups.
- Tracks reusable slots for create/rename by recording `i_offset`, `i_count`, and `i_endoff`.
- Handles whiteouts by treating matching `DT_WHT` entries as create/delete not-found cases with `ISWHITEOUT`.
- Handles `DELETE`, `RENAME`, `CREATE`, ordinary lookup, `.`, and `..` as distinct cases.

## Directory mutation behavior
- `ufs_direnter()` can grow the directory by one `DIRBLKSIZ` block or compact an existing region. It updates dirhash, softdep dependencies, inode size, VM pager size, and write ordering.
- `ufs_dirremove()` decrements `i_effnlink` first so softdep can block, then updates on-disk link count immediately for non-softdep filesystems. Removed entry names are zeroed to reduce disk scavenging disclosure.
- `ufs_dirrewrite()` protects against stale `..` rewrites by checking that a `..` entry still references the expected old inode, returning `EIDRM` if it changed.

## Access and safety checks
- `ufs_delete_denied()` combines optional NFSv4 ACL delete semantics with traditional Unix write permission and sticky-directory ownership rules.
- `ufs_dirbadentry()` validates record length, block fit, minimum entry size, name length, and null termination when directory checking is enabled.
- `ufs_checkpath()` uses cached parent vnode information when available, falls back to reading `..`, and reports a wait inode if nonblocking `VFS_VGET` would block.

## Dependencies
Uses `UFS_BLKATOFF`, `UFS_BALLOC`, `UFS_UPDATE`, dirhash functions, softdep directory hooks, quota setup for directory growth, vnode/namecache APIs, and FFS-facing helpers.

## Research notes
This file is stateful by design: name lookup prepares precise directory insertion/removal offsets consumed later by vnode operations. Correct locking is central, especially for mutation lookups where the parent directory must remain exclusively locked so `i_offset/i_count/i_endoff` remain valid.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_quota.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_quota.c

## Purpose
Implements UFS disk quotas: quota attachment to inodes, block/inode limit enforcement, quotactl operations, quota vnode management, dquot cache management, soft updates integration, and 32-bit/64-bit quota record conversion.

## Key entry points
- `getinoquota()` attaches user and group dquots to an inode, skipping system vnodes and negative UID/GID cases.
- `chkdq()` adjusts block usage and enforces block hard/soft limits.
- `chkiq()` adjusts inode usage and enforces inode hard/soft limits.
- `quotaon()` opens and installs a quota file, marks it system, detects format, initializes grace periods, and attaches quota references to active writable vnodes.
- `quotaoff()` and `quotaoff_inchange()` disable quotas, suspend writes when needed, detach per-inode dquots, flush cached dquots, clear mount quota flags, and close the quota vnode.
- `getquota*`, `setquota*`, `setuse*`, and `getquotasize()` implement user-facing quota operations for both legacy 32-bit and native 64-bit forms.
- `qsync()` and `qsyncvp()` flush modified dquots globally or for one vnode.
- `dqinit()` and `dquninit()` initialize and tear down the global dquot hash/free-list system.
- `dqrele()` releases dquot references and writes dirty dquots before returning them to the free list.
- Soft updates helpers `quotaref()`, `quotarele()`, and `quotaadj()` provide deferred quota accounting support.

## Quota enforcement model
Each inode can hold up to `MAXQUOTAS` dquot pointers, currently user and group quotas. Positive allocation checks use privilege-aware enforcement unless `FORCE` is set or the caller can exceed quota. Negative changes never fail and clear prior warning flags.

Soft limits use time grace periods:
- Crossing a soft block limit initializes `dq_btime`.
- Crossing a soft inode limit initializes `dq_itime`.
- Remaining over the soft limit past the timer causes `EDQUOT`.
- Hard limits fail immediately.

If a later quota type fails during allocation, earlier successful quota adjustments are rolled back.

## Quota file lifecycle
`quotaon()` temporarily unbusies the mount while opening the quota file, then re-busies it and installs the vnode. It uses `QTF_OPENING` and `QTF_CLOSING` to serialize quota transitions and prevent `dqget()` from using half-open or closing quota files. Quota vnodes are marked `VV_SYSTEM`, allow recursive locking, and convert shared locks to exclusive to avoid deadlocks with directory inactive quota sync.

`quotaoff1()` clears per-vnode dquot references, flushes cached dquots for the quota file, clears `um_quotas[type]` before close, removes `VV_SYSTEM`, closes the file, and releases the saved credential.

## Dquot cache
The global cache uses:
- `dqhashtbl` keyed by quota vnode and id.
- `dqfreelist` for reusable unreferenced dquots.
- `dqhlock` protecting the hash table, free list, and dquot reference counters.
- Per-dquot `dq_lock` protecting fields and `DQ_LOCK/DQ_WANT` wait state.

`dqget()` checks the cache first, locks the quota vnode before adding a newly allocated dquot, reads the quota record from disk, initializes timers and `DQ_FAKE`, and wakes waiters. `dqsync()` writes modified records back using `VOP_WRITE` and secondary-write coordination.

## On-disk formats
- 32-bit quota files are arrays of native-endian `struct dqblk32`.
- 64-bit quota files have a `dqhdr64` header followed by network-byte-order `struct dqblk64` records.
- `dqopen()` detects the 64-bit header and sets `QTF_64BIT`.
- Conversion helpers clip 64-bit values to `UINT32_MAX` for 32-bit output.

## Dependencies
Uses mount state from `struct ufsmount`, vnode iteration, vnode I/O, credentials, privilege checks, soft updates hooks, mount suspension APIs, and quota definitions from `quota.h`.

## Research notes
The quota implementation is careful about mount busy state, quota vnode lock ordering, and dquot reference transitions. The most important invariants are that closing quota files are invisible to `dqget()`, dirty dquots are synced before becoming free, and inode quota pointers are detached before cached dquots for a quota file are flushed.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_vfsops.c

## Purpose
Provides common UFS VFS-level helpers: root lookup, quotactl dispatch, and module-level initialization/uninitialization.

## Key entry points
- `ufs_root()` returns the filesystem root vnode by calling `VFS_VGET()` on `UFS_ROOTINO`.
- `ufs_quotactl()` decodes quota subcommands, resolves default UID/GID for `id == -1`, validates quota type, and dispatches to quota implementation functions.
- `ufs_init()` initializes optional quota and directory-hash subsystems.
- `ufs_uninit()` tears down optional quota and directory-hash subsystems.

## Quotactl behavior
When `QUOTA` is not compiled, `ufs_quotactl()` returns `EOPNOTSUPP`. With quota support, it dispatches:
- `Q_QUOTAON` to `quotaon()`.
- `Q_QUOTAOFF` with mount reference and write-start handling, then `quotaoff()`.
- 32-bit and 64-bit set/get quota and set-use commands.
- `Q_GETQUOTASIZE`.
- `Q_SYNC` to `qsync()`.

For `Q_QUOTAOFF`, the function deliberately drops the mount busy state after taking a reference and starts a write operation before calling into quota shutdown, then restores completion with `vn_finished_write()` and `vfs_rel()`.

## Dependencies
Defines `M_UFSMNT` for UFS mount allocations. Uses optional `QUOTA` and `UFS_DIRHASH` initialization paths and quota command constants from UFS quota headers.

## Research notes
This file is small but important as the public VFS dispatch layer for common UFS behavior. Filesystem-specific mount code supplies the actual `struct mount` and `struct ufsmount`; this file handles generic UFS root and quota plumbing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_vnops.c

## Purpose
Implements the common UFS vnode operation vectors and most user-visible filesystem behavior: create, remove, link, rename, mkdir/rmdir, symlink, attributes, access checks, readdir, readlink, strategy I/O, pathconf, vnode initialization, and FIFO wrapping.

## Key vnode operations
- Creation: `ufs_create()`, `ufs_mknod()`, `ufs_makeinode()`, `ufs_mkdir()`, `ufs_symlink()`.
- Removal and link changes: `ufs_remove()`, `ufs_link()`, `ufs_rmdir()`, `ufs_rename()`, `ufs_whiteout()`.
- Access and metadata: `ufs_accessx()`, `ufs_fplookup_vexec()`, `ufs_stat()`, `ufs_getattr()`, `ufs_setattr()`, `ufs_chmod()`, `ufs_chown()`, `ufs_itimes()`.
- Directory and symlink reads: `ufs_readdir()`, `ufs_readlink()`.
- I/O mapping and dispatch: `ufs_strategy()`, `ufs_ioctl()`, `ufs_read_pgcache()`.
- Vnode setup and diagnostics: `ufs_vinit()`, `ufs_print()`, `ufs_pathconf()`.
- Registered vectors: `ufs_vnodeops` and `ufs_fifoops`.

## Timestamp and metadata handling
`ufs_itimes_locked()` applies pending access/change/update flags to inode timestamps unless the filesystem is read-only. It marks inodes modified, lazy-modified, or lazy-accessed depending on vnode type, softdep state, and mount suspension. `ufs_stat()` and `ufs_getattr()` flush pending times under the vnode interlock before reporting attributes.

`ufs_setattr()` validates unsupported fields, enforces read-only and snapshot restrictions, handles file flags with securelevel and jail-aware privilege rules, truncates regular files/symlinks, updates timestamps and birthtime, and delegates mode and ownership changes.

## Access control
`ufs_accessx()` blocks writes to read-only mounts for normal file objects, initializes quotas on exclusive write opens, rejects modification of immutable or snapshot inodes, and then evaluates ACLs when enabled or falls back to Unix permission checks. `ufs_fplookup_vexec()` provides a lockless SMR fast path for execute permission during path lookup, returning `EAGAIN` if inode state cannot be safely read.

## Link and rename behavior
`ufs_link()` guards link-count limits with `ufs_sync_nlink()`, rejects unlinked/immutable/append-only sources, increments effective and on-disk link counts, sets up softdep link state, and inserts a directory entry.

`ufs_rename()` is the largest operation. It:
- Drops initial locks and reacquires `fdvp`, `tdvp`, `fvp`, and optional `tvp` in a restartable order.
- Revalidates source and target names with `ufs_lookup_ino()`.
- Supports `AT_RENAME_NOREPLACE` and rejects unsupported flags.
- Uses sequence counters around vnode namespace modification.
- Handles soft updates journaling preflight with `softdep_prerename()`.
- Prevents cross-device renames, mounted-on directory renames, rename cycles, sticky-directory violations, and incompatible file/directory replacement.
- Temporarily bumps the source link count to keep it alive.
- Creates or rewrites the target entry, removes the source entry, updates `..` when moving directories, and purges/updates namecache state.

`rename_restarts` records restarts caused by lock contention or revalidation races.

## Directory creation and removal
`ufs_mkdir()` manually allocates and initializes a directory inode, writes `.` and `..` from the static templates, updates parent link counts before exposing the new entry, applies MAC labels and ACL inheritance, then inserts the name in the parent directory.

`ufs_rmdir()` verifies the parent link count, checks emptiness, rejects append/immutable/nounlink and mounted-on directories, handles softdep journaling preflight, removes the parent entry, updates link counts, purges cache state, and frees any active dirhash.

## ACL, MAC, quota, and optional feature integration
The file conditionally supports:
- UFS quotas, including quota setup and accounting during create/chown/mkdir.
- POSIX.1e and NFSv4 ACL inheritance and mode synchronization.
- MAC multilabel extended attributes on create and mkdir.
- GEOM journaling orphan tracking on remove/rmdir.
- `SUIDDIR` ownership inheritance.
- Directory hash cleanup.
- Fast page-cache reads for suitable regular files.

## Directory and symlink reads
`ufs_readdir()` walks raw UFS directory entries, validates record lengths, translates old-format fields if needed, emits generic `struct dirent` records, fills NFS cookies when requested, and reports EOF based on inode size.

`ufs_readlink()` serves short symlinks directly from inode storage when smaller than `um_maxsymlinklen`; longer symlinks are read through `VOP_READ`.

## I/O and vnode vectors
`ufs_strategy()` maps logical to physical blocks through `ufs_bmaparray()` before submitting buffers to the mount buffer object. Holes are zero-filled and completed without device I/O.

`ufs_vnodeops` registers common UFS vnode operations while leaving filesystem-specific read/write/fsync/reallocblks as panics here, because FFS supplies those implementations. `ufs_fifoops` wraps FIFO special operations while preserving UFS metadata, inactive, reclaim, access, and attribute behavior.

## Research notes
This file is the main user-facing UFS operation layer. It delegates block allocation, truncation, update, inode allocation/free, and read/write implementation through `ufsmount` callbacks or FFS-specific vectors, while centralizing namespace semantics, permission checks, metadata policy, and vnode operation registration.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufsmount.h -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufsmount.h

## Purpose
Defines the common UFS mount structure, mount arguments, mount flags, quota transition flags, filesystem type constants, and callback macros used by common UFS code to call UFS1/UFS2 or FFS-specific implementations.

## Key structures
- `struct ufs_args` contains the mount device path and export arguments.
- `struct ufsmount` is the UFS-specific mount-private state stored in `mount->mnt_data`.

## `struct ufsmount` contents
Major fields include:
- VFS and device bindings: `um_mountp`, `um_dev`, `um_cp`, `um_bo`, `um_odevvp`, `um_devvp`.
- Filesystem identity and geometry: `um_fstype`, `um_fs`, `um_nindir`, `um_bptrtodb`, `um_seqinc`, `um_bsize`, `um_maxsymlinklen`.
- Extended attributes and soft updates: `um_extattr`, `um_softdep`.
- Quota state: `um_quotas`, `um_cred`, `um_btime`, `um_itime`, `um_qflags`.
- Mount status and reporting: `um_flags`, full/integrity message timestamps and intervals.
- TRIM support state: inflight counts, totals, taskqueue, hash table, and hash mask.
- Operation callback table for allocation, block lookup, truncate, update, inode allocation/free, read-only test, snapshot gone hook, and block-number validation.

The lock legend documents fields as constant, protected by the UFS interlock, protected by quota-file locking, or requiring a VFS mount reference.

## Operation macros
The header defines common dispatch macros:
- `UFS_BALLOC`, `UFS_BLKATOFF`, `UFS_TRUNCATE`, `UFS_UPDATE`.
- `UFS_VALLOC`, `UFS_VFREE`, `UFS_IFREE`.
- `UFS_RDONLY`, `UFS_SNAPGONE`, `UFS_CHECK_BLKNO`.
- `VFSTOUFS` and `UFSTOVFS` for mount conversion.
- `UFS_LOCK`, `UFS_UNLOCK`, `UFS_MTX`.

These macros are used throughout the common UFS source files so shared code can call filesystem-specific implementations without directly knowing whether it is operating on UFS1, UFS2, or a specific FFS backend.

## Constants and flags
- Filesystem types: `UFS1`, `UFS2`.
- Mount flags: `UM_CANDELETE`, `UM_WRITESUSPENDED`, `UM_CANSPEEDUP`, `UM_FSFAIL_CLEANUP`.
- Quota state flags: `QTF_OPENING`, `QTF_CLOSING`, `QTF_64BIT`.
- Geometry helpers: `MNINDIR`, `blkptrtodb`, `is_sequential`.
- `OFSFMT(vp)` detects old filesystem directory format based on `um_maxsymlinklen`.

## Research notes
This header is the abstraction point that lets common UFS vnode, lookup, quota, inactive, and VFS code remain independent of lower-level allocation and update mechanics. Correct use of its lock annotations and callback macros is necessary to understand the rest of the UFS implementation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufsmount.h -->