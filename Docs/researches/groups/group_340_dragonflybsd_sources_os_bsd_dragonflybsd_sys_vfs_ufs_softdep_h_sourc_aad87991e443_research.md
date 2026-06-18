# Group Research: group_340_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_ufs_softdep_h_sourc_aad87991e443

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/dragonflybsd`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/softdep.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/softdep.h

## Purpose

Defines the in-memory dependency records and state flags used by UFS/FFS soft updates. This header is structural rather than executable: it describes how metadata write ordering is represented for inode updates, block allocation, block freeing, directory additions/removals, mkdir/rmdir, and indirect-block updates.

## Key Definitions

- State flags: `ATTACHED`, `UNDONE`, `COMPLETE`, `DEPCOMPLETE`, `MKDIR_PARENT`, `MKDIR_BODY`, `RMDIR`, `DIRCHG`, `GOINGAWAY`, `IOSTARTED`, `ONWORKLIST`.
- `ALLCOMPLETE` means a dependency is attached, complete, and dependency-complete.
- `struct worklist` is the common first field for softdep work items. The file explicitly requires it to be first so cast macros such as `WK_INODEDEP()` and `WK_DIRADD()` are valid.
- Queue/list heads: `dirremhd`, `diraddhd`, `newblkhd`, `inodedephd`, `allocindirhd`, `allocdirecthd`, `allocdirectlst`.

## Main Structures

- `struct pagedep`: tracks dependencies for one directory page, including pending directory removals and directory additions hashed by offset.
- `struct inodedep`: tracks delayed inode work, inode-buffer wait lists, pending directory-name writes, and direct block allocation updates associated with an inode.
- `struct newblk`: represents an allocated block/fragment whose cylinder-group bitmap write may still be pending.
- `struct bmsafemap`: attaches allocation dependencies to a cylinder-group bitmap buffer.
- `struct allocdirect`: tracks a newly allocated direct block or fragment that cannot be claimed by the inode until data and bitmap dependencies complete.
- `struct indirdep` and `struct allocindir`: track safe copies and allocation dependencies for indirect block pointers.
- `struct freefrag`, `struct freeblks`, `struct freefile`: deferred block, fragment, and inode freeing records.
- `struct diradd`: tracks directory entries that cannot be written until referenced inode and mkdir dependencies are safe.
- `struct mkdir`: represents the two special mkdir dependencies: writing the new directory body and writing the parent inode link-count update.
- `struct dirrem`: represents a deferred link-count decrement after a directory entry removal reaches disk.

## Important Behavior Encoded By The Design

Soft updates uses rollback/roll-forward around buffer I/O. For example, unsafe pointers are temporarily undone before disk write, restored after I/O, and freed only when both local and upstream dependencies are complete. Directory operations are decomposed into separately ordered pieces so link counts, directory bodies, and names reach disk in crash-safe order.

## Dependencies And Integration Points

This header depends on queue/list primitives from `<sys/queue.h>` and on UFS/FFS types such as `struct fs`, `struct buf`, `struct vnode`, `ufs_daddr_t`, `ufs_lbn_t`, and inode/directory structures declared elsewhere. The functions that consume these structures are declared in `ufs_extern.h` and implemented in the softdep subsystem outside this file.

## Notes For Future Work

- The `worklist` first-field invariant is critical. Reordering fields in any softdep work item would break the cast macros.
- The header defines `mkdirlisthd` directly, which is a global list head declaration/definition in this old kernel style.
- Many fields intentionally overload state or union storage to keep structures small; changes must preserve those lifetime assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/softdep.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_bmap.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_bmap.c

## Purpose

Implements UFS logical-to-physical block mapping. It translates file logical offsets or logical block numbers into device offsets, computes contiguous run lengths, and constructs indirect-block traversal paths.

## Main Functions

- `ufs_bmap(struct vop_bmap_args *ap)`: vnode operation wrapper. Validates the logical offset alignment, calls `ufs_bmaparray()`, returns `NOOFFSET` for holes, and converts disk blocks to byte offsets.
- `ufs_bmaparray(struct vnode *vp, ufs_daddr_t bn, ufs_daddr_t *bnp, struct indir *ap, int *nump, int *runp, int *runb)`: core block mapper. Handles direct blocks, indirect blocks, holes, cached indirect blocks, synchronous reads of indirect blocks, and forward/backward sequential run detection.
- `ufs_getlbns(struct vnode *vp, ufs_daddr_t bn, struct indir *ap, int *nump)`: computes the path through single, double, or triple indirect blocks for a target logical block. Negative logical block numbers represent metadata blocks.

## Important Behavior

Direct blocks are read from `ip->i_db[]`; indirect roots come from `ip->i_ib[]`. Physical UFS block pointers are converted with `blkptrtodb()`. If a block pointer is zero, the mapper returns `-1` internally and `NOOFFSET` to callers.

Indirect blocks are addressed as negative logical block numbers on the file vnode. The code uses `findblk()` to avoid disk I/O for unallocated indirect blocks unless a cached buffer exists. When an indirect buffer is not cached, it is read synchronously via `vn_strategy()` using the cached physical offset in `bio2`.

## Dependencies And Integration Points

Relies on `struct inode`, `struct fs`, `struct ufsmount`, buffer cache operations, `ffs_blkatoff` conventions, and macros from `ufsmount.h`: `MNINDIR`, `blkptrtodb`, and `is_sequential`.

## Notes For Future Work

- `ufs_getlbns()` uses `int64_t` for `qblockcnt` to avoid overflow for triple-indirect calculations on 32-bit `long`.
- `runp` and `runb` are returned in blocks from `ufs_bmaparray()` and converted to bytes by `ufs_bmap()`.
- The code assumes callers pass block-aligned logical offsets to `ufs_bmap()`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_dirhash.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_dirhash.c

## Purpose

Implements optional hash-accelerated lookup and free-space tracking for large UFS directories when `UFS_DIRHASH` is enabled.

## Main Data And Tunables

- Allocator: `M_DIRHASH`.
- Sysctls:
  - `vfs.ufs.dirhash_minsize`: minimum directory size for hashed lookup.
  - `vfs.ufs.dirhash_maxmem`: global memory cap.
  - `vfs.ufs.dirhash_mem`: current memory use.
  - `vfs.ufs.dirhash_docheck`: optional consistency checks.
- Global LRU-like list: `ufsdirhash_list`.
- Object cache: `ufsdirhash_oc`, used for hash array blocks.

## Main Functions

- `ufsdirhash_build()`: builds a hash table and per-directory-block free-space summaries from existing directory contents.
- `ufsdirhash_free()`: releases hash arrays, free-space arrays, and the dirhash object.
- `ufsdirhash_lookup()`: looks up a name through linear probing, validates candidate directory entries, supports sequential-access optimization, and can return the previous entry offset for delete.
- `ufsdirhash_findfree()`: finds a directory block with enough free space for insertion.
- `ufsdirhash_enduseful()`: identifies trailing fully free directory blocks that could be truncated.
- `ufsdirhash_add()`, `ufsdirhash_remove()`, `ufsdirhash_move()`: maintain hash state as directory entries are inserted, removed, or compacted.
- `ufsdirhash_newblk()` and `ufsdirhash_dirtrunc()`: update state when a directory grows or shrinks.
- `ufsdirhash_checkblock()`: optional sanity checker that compares hash/free-space state to actual directory block contents.
- Static helpers implement hashing, free-space bucket updates, slot lookup/deletion, previous-entry discovery, recycling, and initialization.

## Important Behavior

Hash entries store directory offsets, not inode numbers. Collisions use linear probing with `DIRHASH_EMPTY` and `DIRHASH_DEL` sentinels. The filename hash mixes FNV-1 with the `dirhash` object address to reduce clustering for similar names.

Memory pressure is handled by recycling the lowest-scored dirhash entries from the head of `ufsdirhash_list`. Recycling detaches only the heavy hash/free arrays and leaves an inode-associated `dirhash` shell that later lookup code can detect and free/rebuild.

## Dependencies And Integration Points

Used by `ufs_lookup.c` during lookup, insertion, deletion, compaction, directory growth, and truncation. Depends on `dirhash.h`, `dir.h`, `inode.h`, `ufsmount.h`, `ffs_extern.h`, buffer cache reads through `ffs_blkatoff()`, and FNV hashing.

## Notes For Future Work

- All logic is inside `#ifdef UFS_DIRHASH`; callers must tolerate absence of these helpers.
- The code frequently falls back to linear search by returning `EJUSTRETURN` or `-1` when corruption, stale state, or allocation limits are encountered.
- Directory corruption checks are defensive; several paths free or abandon a hash instead of trusting inconsistent state.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_dirhash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_extern.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_extern.h

## Purpose

Declares exported UFS functions shared across the UFS/FFS implementation. It is the local interface header for vnode operations, directory helpers, inode hash helpers, VFS helpers, and softdep hooks.

## Main Declarations

- Vnode operation dispatchers: `ufs_vnoperate()`, `ufs_vnoperatefifo()`, `ufs_vnoperatespec()`.
- Block mapping: `ufs_bmap()`, `ufs_bmaparray()`, `ufs_getlbns()`.
- NFS/export helpers: `ufs_check_export()`, `ufs_fhtovp()`.
- Directory helpers: `ufs_lookup()`, `ufs_dirbad()`, `ufs_dirbadentry()`, `ufs_dirempty()`, `ufs_makedirentry()`, `ufs_direnter()`, `ufs_dirremove()`, `ufs_dirrewrite()`, `ufs_checkpath()`.
- Inode hash helpers: `ufs_ihashget()`, `ufs_ihashcheck()`, `ufs_ihashinit()`, `ufs_ihashuninit()`, `ufs_ihashins()`, `ufs_ihashlookup()`, `ufs_ihashrem()`.
- Inode lifecycle: `ufs_inactive()`, `ufs_reclaim()`.
- Generic init/root/vnode initialization: `ufs_init()`, `ufs_root()`, `ufs_start()`, `ufs_vinit()`.
- Timestamp helper: `ufs_itimes()`.
- Softdep integration hooks: directory add/change/remove setup, directory-entry offset changes, link-count changes, and slowdown check.

## Dependencies And Integration Points

Uses forward declarations rather than including the full definitions of vnode, mount, inode, directory, and credential types. Included by many files in this group to share cross-file functions.

## Notes For Future Work

- The header declares `ufs_start()` but this group does not include its implementation.
- Softdep functions are declared here even though their dependency structures are defined in `softdep.h`.
- The signatures reflect DragonFly’s older `vop_old_*` vnode operation interface.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_ihash.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_ihash.c

## Purpose

Maintains the per-mount in-core inode hash table keyed by inode number and device. This lets UFS find existing vnodes/inodes and prevents duplicate incore inodes for the same on-disk inode.

## Main Functions

- `ufs_ihashinit(struct ufsmount *ump)`: allocates the hash table sized by `vfs_inodehashsize()` and stores a mask in `um_ihash`.
- `ufs_ihashuninit(struct ufsmount *ump)`: frees the hash table.
- `ufs_ihashlookup(struct ufsmount *ump, cdev_t dev, ino_t inum)`: returns an incore vnode without locking or waiting.
- `ufs_ihashget(struct ufsmount *ump, cdev_t dev, ino_t inum)`: finds and locks the vnode, retrying if the vnode changes while blocked.
- `ufs_ihashcheck(struct ufsmount *ump, cdev_t dev, ino_t inum)`: returns whether an inode is present. Used to interlock inode free/reuse.
- `ufs_ihashins(struct ufsmount *ump, struct inode *ip)`: inserts an inode unless a duplicate exists, marking `IN_HASHED`.
- `ufs_ihashrem(struct ufsmount *ump, struct inode *ip)`: removes a hashed inode and clears `IN_HASHED`.

## Important Behavior

The hash bucket is `inum & ump->um_ihash`, where `um_ihash` is one less than the allocated hash size. Insert walks to the bucket tail and returns `EBUSY` if the same device/inode pair already exists.

`ufs_ihashget()` uses `vget()` and then rechecks the hash chain after potential blocking to ensure the vnode still represents the requested inode.

## Dependencies And Integration Points

Uses `struct ufsmount` fields `um_ihashtbl` and `um_ihash`. Called during inode allocation/loading and reclaim paths. `ufs_reclaim()` removes inodes from this hash.

## Notes For Future Work

- The implementation assumes external synchronization sufficient for bucket list mutation in this kernel context.
- `ufs_ihashlookup()` intentionally returns even if the vnode is locked; callers needing a locked vnode must use `ufs_ihashget()`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_ihash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_inode.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_inode.c

## Purpose

Implements UFS vnode inactive and reclaim operations. These handle final-reference cleanup, unlink completion, inode update flushing, quota release, dirhash release, and freeing incore inode memory.

## Main Functions

- `ufs_inactive(struct vop_inactive_args *ap)`: called when the last active reference is dropped. If the inode has no links and the mount is writable, it truncates the file, clears mode/rdev, marks metadata changed, and frees the inode with `ffs_vfree()`. It writes pending inode updates and recycles dead vnodes.
- `ufs_reclaim(struct vop_reclaim_args *ap)`: tears down the vnode-to-inode association. It flushes lazy modifications, removes the inode from the inode hash, releases the device vnode, releases quotas, frees any dirhash, and frees the inode allocation.

## Important Behavior

Unlinked files are not fully freed until inactive processing. The code ensures truncation happens before marking the inode free. Under `INVARIANTS`, reclaim warns and forces an update if a modified inode is being released.

Quota release is conditional on `QUOTA`; directory hash cleanup is conditional on `UFS_DIRHASH`.

## Dependencies And Integration Points

Depends on FFS helpers such as `ffs_truncate()`, `ffs_vfree()`, and `ffs_update()`. Calls `ufs_ihashrem()` and `ufsdirhash_free()`. Uses mount-specific inode allocator type from `ufsmount`.

## Notes For Future Work

- `vp->v_data` is cleared before inode memory is freed.
- The reclaim path explicitly tolerates stale file-handle inodes where `ip` is null or mode is zero.
- Lazy modified special-device inodes are pushed before release.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_lookup.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_lookup.c

## Purpose

Implements pathname component lookup within UFS directories and the directory-entry mutation helpers used by create, link, unlink, rename, mkdir, rmdir, whiteout, and symlink operations.

## Main Functions

- `ufs_lookup()`: central name lookup routine. Searches a directory for a component, optionally computes insertion/removal slot metadata, handles create/delete/rename semantics, lock-parent behavior, whiteouts, `.`/`..`, and vnode acquisition.
- `ufs_dirbad()` and `ufs_dirbadentry()`: report or validate malformed directory entries.
- `ufs_makedirentry()`: constructs a `struct direct` from an inode and `componentname`, including old-format byte-order handling.
- `ufs_direnter()`: inserts a new directory entry using slot information left by lookup. Handles new block allocation, compaction, dirhash updates, softdep ordering, async/sync writes, and directory truncation after compaction.
- `ufs_dirremove()`: removes or whiteouts a directory entry, updates dirhash, updates link counts, and schedules softdep remove work when enabled.
- `ufs_dirrewrite()`: rewrites an existing entry to point at a new inode, used by rename replacement.
- `ufs_dirempty()`: checks that a directory contains only `.` and `..`, ignoring empty and whiteout entries.
- `ufs_checkpath()`: prevents directory rename cycles by walking `..` from target toward root and checking whether source is encountered.

## Important Behavior

`ufs_lookup()` is both a lookup and planning routine. For create/rename/delete it records offsets in the directory inode:

- `i_offset`: target or insertion offset.
- `i_count`: previous-entry distance for deletion or available slot size for insertion.
- `i_reclen`: found entry record length.
- `i_endoff`: useful end of directory for possible truncation.

When `UFS_DIRHASH` is enabled, large directories can use dirhash for fast lookup and free-space discovery; otherwise the code performs a linear scan. Failed dirhash lookups can fall back to linear search.

Directory insertion may allocate a new directory block or compact an existing range. Soft updates receives explicit hooks so directory-entry writes are ordered after required inode/directory-body writes.

## Dependencies And Integration Points

Uses `ffs_blkatoff()`, `VOP_BALLOC()`, `ffs_update()`, `ffs_truncate()`, vnode locking, `VFS_VGET()`, dirhash helpers, and softdep hooks from `ufs_extern.h`.

## Notes For Future Work

- Old UFS directory format is handled with the `OFSFMT()` macro and little-endian field swapping.
- `dirchk` controls expensive directory-entry validation through a debug sysctl.
- Several code paths intentionally unlock a parent before fetching `..` to avoid directory-tree deadlocks.
- The directory mutation helpers depend on `ufs_lookup()` leaving valid slot metadata while the parent directory remains locked.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_quota.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_quota.c

## Purpose

Implements UFS quota accounting, enforcement, quotactl operations, and in-core dquot cache management.

## Main Accounting Functions

- `ufs_getinoquota()`: attaches user and group dquot structures to an inode when quotas are enabled.
- `ufs_chkdq()`: applies block usage changes, enforcing hard limits and soft-limit grace periods unless forced.
- `ufs_chkiq()`: applies inode usage changes with analogous hard/soft limit enforcement.
- `ufs_chkdqchg()` and `ufs_chkiqchg()`: validate prospective block/inode increases and emit user warnings.
- `ufs_quotawarn()`: rate-limited warning when quota operations target the quota file itself.
- Diagnostic `ufs_chkdquot()`: asserts modified inodes have dquots when quotas are active.

## Quotactl Functions

- `ufs_quotaon()`: opens a quota file, marks it system, initializes quota grace times from id 0, and scans active writable vnodes to attach dquots.
- `ufs_quotaoff()`: detaches dquots from vnodes, flushes cached dquots for the quota vnode, closes the quota file, and clears mount quota state.
- `ufs_getquota()`: copies a quota record out to user space.
- `ufs_setquota()`: replaces quota limits while preserving current usage and maintaining grace timers.
- `ufs_setuse()`: sets current block/inode usage and resets soft-limit timers where needed.
- `ufs_qsync()`: scans vnodes and syncs modified dquots.

## Dquot Cache Functions

- `ufs_dqinit()`: initializes hash table and free list.
- `ufs_dqget()`: finds or allocates a dquot, reads its record from the quota file, initializes timers/fake state, and returns a referenced structure.
- `ufs_dqrele()`: drops a reference, syncing modified dquots when the last reference is released.
- `ufs_dqsync()`: writes a modified quota record back to the quota file with dquot locking.
- `ufs_dqflush()`: removes all cached dquots associated with a quota vnode.

## Important Behavior

Block and inode usage decreases never fail and clear warning flags when usage falls. Increases are checked first for all active quotas, then applied. Soft limits are allowed until their grace time expires; hard limits fail immediately.

Quota files are protected from recursive quota accounting by warning and skipping normal charge changes when the quota vnode itself is involved.

## Dependencies And Integration Points

Called from vnode operations, inode lifecycle, allocation/free paths, and `ufs_quotactl()` in `ufs_vfsops.c`. Uses `vmntvnodescan()`, `VOP_READ()`, `VOP_WRITE()`, vnode locking, credentials saved in `ufsmount`, and quota fields embedded in `struct inode`.

## Notes For Future Work

- The dquot cache is global, keyed by quota vnode and id.
- `DQ_LOCK`/`DQ_WANT` provide sleep-based serialization around quota file I/O.
- `ufs_quotaon_scan()` only attaches dquots to vnodes with `v_writecount != 0`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_readwrite.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_readwrite.c

## Purpose

Implements FFS/UFS vnode read and write operations for regular files, directories, and long symlinks.

## Main Functions

- `ffs_read(struct vop_read_args *ap)`: reads file data through the buffer cache with read-ahead, EOF clipping, optional direct I/O buffer release, and atime marking.
- `ffs_write(struct vop_write_args *ap)`: writes file data through `VOP_BALLOC()`, handles append mode, immutable append enforcement, file size/resource limits, VM object size updates, buffer clearing, clustering, direct I/O, synchronous/asynchronous writes, setuid/setgid clearing, and timestamp updates.

## Important Read Behavior

Reads validate type under `DIAGNOSTIC`, reject offsets beyond `fs_maxfilesize`, stop at EOF, use `ffs_blkatoff_ra()` with sequence hints, and never copy past initialized buffer data. Buffers without dependencies may be marked `B_RELBUF` for VM/direct I/O.

## Important Write Behavior

Writes enforce `APPEND`, `fs_maxfilesize`, and `RLIMIT_FSIZE`. Before extending the file, the VM object size is updated via `nvnode_pager_setsize()`. Partial-block writes and no-copy writes use `B_CLRBUF` to avoid exposing stale data. Buffer writeback policy chooses among synchronous `bwrite()`, async `bawrite()`, clustered `cluster_write()`, direct-I/O async write, or delayed `bdwrite()`.

`IO_UNIT` error handling rolls the file back to its original size and restores the user I/O offset/residual.

## Dependencies And Integration Points

Uses FFS macros and functions including `blksize`, `lblkno`, `blkoff`, `blkoffresize`, `VOP_BALLOC`, `ffs_blkatoff_ra`, `ffs_truncate`, `ffs_update`, and `ufs_itimes()`. Emits vnode write/extend knotes via `VN_KNOTE`.

## Notes For Future Work

- `UIO_NOCOPY` sets `IN_NOCOPYWRITE` and interacts with `VLASTWRITETS` timestamp handling in `ufs_itimes()`.
- The file aliases generic macro names (`FS`, `I_FS`, `BLKSIZE`) to FFS/UFS-specific fields before including VM/buffer headers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_readwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_types.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_types.h

## Purpose

Defines basic UFS on-disk scalar types for DragonFly BSD.

## Definitions

- `ufs1_ino_t`: 32-bit unsigned inode number type for UFS1.
- `ufs_daddr_t`: 32-bit signed disk address type.
- `ufs_time_t`: 32-bit signed timestamp type.

## Dependencies And Integration Points

Included by UFS headers that need stable on-disk type widths. These typedefs complement broader kernel types such as `ino_t`, `daddr_t`, and filesystem-specific block address fields.

## Notes For Future Work

- The file is intentionally small and guarded by `_VFS_UFS_UFS_TYPES_H_`.
- Width choices matter for disk-format compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_vfsops.c

## Purpose

Provides generic UFS VFS-level operations shared by UFS-based filesystems: root vnode lookup, quota command dispatch, one-time initialization, NFS file-handle conversion, and export checks.

## Main Functions

- `ufs_root(struct mount *mp, struct vnode **vpp)`: returns the root vnode by calling `VFS_VGET()` for `UFS_ROOTINO`.
- `ufs_quotactl()`: validates quota command permissions, resolves default uid/gid, busies the mount, and dispatches to quota operations when `QUOTA` is enabled. Returns `EOPNOTSUPP` without quota support.
- `ufs_init(struct vfsconf *vfsp)`: one-time UFS initialization; initializes quota dquot cache when quotas are compiled in.
- `ufs_fhtovp()`: converts a UFS file handle to a vnode and validates generation, mode, and link count to reject stale handles.
- `ufs_check_export()`: looks up export credentials/options for a client address using `vfs_export_lookup()`.

## Important Behavior

Quota permission checks use DragonFly capability checks. Mutating quota commands require `SYSCAP_NOQUOTA_WR`; `Q_GETQUOTA` allows self-query or restricted-root capability; `Q_SYNC` is allowed.

`ufs_fhtovp()` accounts for softdep effective link count if `um_i_effnlink_valid` is set, otherwise uses `i_nlink`.

## Dependencies And Integration Points

Uses `M_UFSMNT` allocation type, `struct ufsmount`, quota functions in `ufs_quota.c`, and export state in `ufsmount.h`.

## Notes For Future Work

- This file is generic UFS glue; actual mount/unmount and FFS-specific operations live elsewhere.
- `rootvp` is accepted by `ufs_fhtovp()` but not used in this implementation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_vnops.c

## Purpose

Implements the main UFS vnode operation layer: timestamps, attributes, permissions, file creation, directory operations, rename, links, symlinks, readdir/readlink, strategy I/O dispatch, FIFOs, kqueue filters, vnode initialization, inode creation, and vnode operation tables.

## Main Functional Areas

- Timestamp handling: `ufs_itimes()` updates access/change/modify times, handles 64-bit seconds split into base/ext fields, lazy special-device updates, and no-copy write timestamps.
- Creation and metadata ops: `ufs_create()`, `ufs_mknod()`, `ufs_makeinode()`, `ufs_setattr()`, `ufs_chmod()`, `ufs_chown()`.
- Link and removal ops: `ufs_link()`, `ufs_remove()`, `ufs_whiteout()`.
- Rename and directory ops: `ufs_rename()`, `ufs_mkdir()`, `ufs_rmdir()`.
- Symlink/directory reads: `ufs_symlink()`, `ufs_readdir()`, `ufs_readlink()`.
- I/O strategy and misc ops: `ufs_strategy()`, `ufs_print()`, `ufs_pathconf()`, `ufs_ioctl()`, `ufs_advlock()`.
- FIFO wrappers: `ufsfifo_read()`, `ufsfifo_write()`, `ufsfifo_close()`, `ufsfifo_kqfilter()`.
- Kqueue support: `ufs_kqfilter()`, `filt_ufsdetach()`, `filt_ufsread()`, `filt_ufswrite()`, `filt_ufsvnode()`.
- Vnode setup/dispatch: `ufs_vinit()`, `ufs_vnoperate()`, `ufs_vnoperatefifo()`, `ufs_vnoperatespec()`.

## Important Behavior

`ufs_rename()` is the most complex operation. It prevents cross-device renames, rejects unsafe directory moves, temporarily bumps source link count, checks for directory cycles with `ufs_checkpath()`, creates or rewrites the target entry, removes the old source entry with `relookup()`, and carefully unwinds locks/references on errors.

`ufs_mkdir()` manually allocates and initializes the child inode before entering it in the parent. It writes the `.` and `..` directory body first, then calls `ufs_direnter()`, with softdep-specific ordering when enabled.

`ufs_rmdir()` requires `i_effnlink == 2` and `ufs_dirempty()`, blocks removal during rename, removes the parent entry first, then truncates the directory when not using softdep.

`ufs_vinit()` selects special-device, FIFO, or regular vnode ops, creates VM objects for directories/regular files and long symlinks, sets `VROOT` for `UFS_ROOTINO`, and initializes file revision state.

## Dependencies And Integration Points

Integrates with nearly every file in this group: `ufs_lookup.c` for directory entry operations, `ufs_inode.c` for inactive/reclaim ops via vop tables, `ufs_bmap.c` through `.vop_bmap`, `ufs_quota.c` for quota checks in access/chown/makeinode/mkdir, and softdep hooks for link-count ordering.

Also calls FFS-specific helpers such as `ffs_valloc()`, `ffs_update()`, `ffs_truncate()`, and block allocation/read functions.

## Vnode Operation Tables

- `ufs_vnode_vops`: regular UFS vnode operations. Some FFS-provided operations such as read/write/fsync/reallocblks are marked with `ufs_missingop()` here.
- `ufs_spec_vops`: special-device vnode operations with UFS metadata handling.
- `ufs_fifo_vops`: FIFO vnode operations wrapping FIFO behavior while preserving UFS timestamps/attributes.

## Notes For Future Work

- Some permission checks are delegated to upper layers or helper functions; disabled historical checks remain in `#if 0`.
- Whiteout support depends on 4.4-style directory format.
- Kqueue read filters report remaining bytes from current file offset and handle revoke with EOF/NODATA flags.
- `ufs_missingop()` panics, so vnode op table wiring must ensure filesystem-specific operations override missing entries before use.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufsmount.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufsmount.h

## Purpose

Defines UFS mount arguments, MFS mount arguments, and the kernel-private `struct ufsmount` that stores per-mount UFS state.

## Main Structures

- `struct ufs_args`: mount arguments for UFS-based filesystems, including device path and export args.
- `struct mfs_args`: mount arguments for memory filesystems, including exported name, export args, base address, and size.
- `struct ufsmount`: per-mount state:
  - VFS mount pointer, device id, and device vnode.
  - FFS superblock pointer.
  - Quota vnodes, quota credentials, quota grace times, and quota flags.
  - Derived block mapping parameters: indirect pointers per block, block-pointer-to-disk-block shift, sequential increment.
  - Export state.
  - Saved max file size.
  - Inode allocation malloc type.
  - Effective-link-count validity flag.
  - Inode hash table and mask.

## Macros And Flags

- `QTF_OPENING`, `QTF_CLOSING`: quota transition flags.
- `VFSTOUFS(mp)`: casts `mnt_data` to `struct ufsmount`.
- `MNINDIR(ump)`: indirect pointers per block.
- `blkptrtodb(ump, b)`: converts UFS block pointer to disk blocks.
- `is_sequential(ump, a, b)`: tests physical sequentiality using `um_seqinc`.

## Dependencies And Integration Points

Included by UFS implementation files that need mount-private state. `ufs_bmap.c` relies on `MNINDIR`, `blkptrtodb`, and `is_sequential`; quota code relies on quota arrays and flags; inode hash code uses `um_ihashtbl` and `um_ihash`.

## Notes For Future Work

- Kernel-only contents are guarded by `_KERNEL`; user-visible mount argument structures are outside that guard.
- `um_i_effnlink_valid` lets code choose between softdep effective link counts and on-disk link counts.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufsmount.h -->