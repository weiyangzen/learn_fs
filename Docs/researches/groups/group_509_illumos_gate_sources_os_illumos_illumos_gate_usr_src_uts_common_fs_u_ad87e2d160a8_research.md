# Group Research: group_509_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_u_ad87e2d160a8

Scope: `Docs/research_subset_a.md`. This group covers illumos UFS quota enforcement/control, ACL shadow-inode storage, block/inode allocation, fallocate/free-space support, and logical-to-physical block mapping under `usr/src/uts/common/fs/ufs`.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/quota_ufs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/quota_ufs.c

This file implements runtime UFS quota enforcement for blocks and inodes. Its public entry points are `getinoquota`, `chkdq`, `chkiq`, and `dqrele`.

`getinoquota` chooses the `dquot` used by an inode. It requires `vfs_dqrwlock` and the inode contents write lock, ignores disabled quotas, the quota file itself, shadow inodes, and extended attribute directory inodes, and returns `NULL` when the user's quota record has no block or file limits. Otherwise it returns a held dquot whose UID matches the inode owner.

`chkdq` applies block usage deltas to `ip->i_dquot`. Negative changes always succeed, decrement current blocks with underflow protection, clear block warning state, and reset block grace time when usage drops below the soft limit. Positive changes reserve blocks unless the file is owned by uid 0, checking hard limits, soft limits, grace expiration, and the `force` override. It records quota modifications with `DQ_MOD`/`TRANS_QUOTA`, caps forced 32-bit block count overflow at `0xffffffff`, and can either return a user-facing warning string to the caller or log the quota warning directly.

The debug block in `chkdq` is an important consistency check: it recomputes the expected dquot through `getinoquota` or `getdiskquota`, permits only known transient quota errors, and asserts that the inode's cached dquot pointer matches the quota subsystem's view. This is specifically guarded for shadow inodes and extended attribute directories, which must not have quota records.

`chkiq` enforces per-user inode quotas. It requires the quota rwlock as reader, accepts only `+1` or `-1`, and handles two paths: freeing a specific inode through that inode's cached dquot, or allocating/freeing by UID via `getdiskquota`. Allocation checks hard limits, soft limits, file grace time, and `force`; deallocation clears warning state and grace time when usage falls below the soft limit. Shadow inodes and extended attribute directory inodes do not count as user inode allocation.

`dqrele` is the dquot release helper. It locks the dquot, pushes modified quota state with `dqupdate` when the last reference is being released, then drops the reference with `dqput`.

Integration notes: callers must hold the documented inode and quota locks before invoking these routines. Allocation callers rely on quota rollback with negative deltas when subsequent physical allocation fails. The warning-string path allocates kernel memory with `KM_NOSLEEP`, so callers that request messages must free the returned buffer after `uprintf`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/quota_ufs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/quotacalls.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/quotacalls.c

This file implements UFS quota control operations behind `quotactl`: turning quotas on and off, setting limits, reading limits, and syncing quota records. It also owns the global `quotas_initialized` flag.

`quotactl` copies in the native or ILP32 `quotctl` structure, defaults negative UIDs to the caller's real UID, resolves the target `ufsvfs` except for all-filesystem sync cases, then dispatches `Q_QUOTAON`, `Q_QUOTAOFF`, `Q_SETQUOTA`, `Q_SETQLIM`, `Q_GETQUOTA`, `Q_SYNC`, and `Q_ALLSYNC`. Quota initialization is protected by the global `dq_rwlock`.

`opendq` enables quotas for one mounted UFS filesystem. It requires quota privilege, holds the quota vnode, validates it is a regular file, then takes `vfs_dqrwlock` as writer to quiesce quota state. For a newly enabled filesystem it installs `vfs_qinod`, expands the quota file to at least `fs_bsize * NDADDR` to avoid partial fragment relocation, marks metadata, loads uid 0's quota record as the source of block and file grace defaults, sets `MQ_ENABLED`, updates mount options, and scans all cached inodes to attach dquots. If quotas were already enabled, it accepts only the same quota inode and otherwise warns that the previous quota file remains in use.

`closedq` disables quotas. Under `vfs_dqrwlock` writer it clears `MQ_ENABLED`, updates mount options, scans cached inodes to detach `i_dquot`, cancels pending logging quota transactions by clearing `DQ_TRANS` and dropping the extra reference, clears `vfs_qinod`, then syncs and releases the quota inode outside the quota rwlock.

`setquota` changes quota records. It requires privilege and enabled quotas, copies in a `dqblk`, preserves current usage for `Q_SETQLIM`, updates filesystem grace defaults when setting uid 0, and otherwise adjusts user grace timers and warning flags depending on whether usage crosses soft limits. It detects transitions from no limits to any limits, or from some limits to no limits, and scans cached inodes for that UID to attach or detach their dquot pointers accordingly. It writes the updated quota record to the quota file synchronously and computes `dq_mof` with `bmap_read` for logging metadata-offset tracking.

`getquota` allows users to read their own quota and requires quota privilege for other UIDs. It returns `ESRCH` if quotas are disabled or the record has no limits, otherwise copies the `dqblk` to user space.

`quotasync` flushes modified dquot records for one filesystem or all quota-enabled filesystems. It is a no-op for logging filesystems because quota state is treated as metadata in the log. For all-filesystem sync it uses `mutex_tryenter` and `rw_tryenter` to avoid deadlock with the normal `vfs_dqrwlock > dq_lock` order, skipping records it cannot safely lock.

Integration notes: the control path centers on `vfs_dqrwlock` as a filesystem-level quota quiescing mechanism. Cached inode dquot pointers are deliberately repaired after quota-on and limit/no-limit transitions. Sync paths may skip busy dquots rather than block in unsafe lock order.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/quotacalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_acl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_acl.c

This file implements UFS POSIX-draft ACL storage, access checks, inheritance, and ACL cache management. UFS stores nontrivial ACLs in special shadow inodes, while ordinary owner/group/other ACLs are collapsed back into mode bits with no shadow inode.

The central storage routine is `ufs_si_store`. Given an in-core `si_t`, it either removes ACL storage when only the three basic access entries remain, reuses an identical cached shadow inode, or allocates a new `IFSHAD` inode and writes serialized ACL data into it. When switching an object to the new ACL, it updates `i_ufs_acl`, `i_shadow`, mode bits, owner/group fields implied by ACL entries, and inode transaction state. It then decrements the old shadow inode link count and old ACL reference count, deleting the cache entry if no in-memory inode references remain.

`ufs_si_load` attaches an inode's existing shadow ACL. It validates `i_shadow`, looks up a cached `si_t` by device and shadow inode number, or reads the shadow inode from disk, parses `FSD_ACL` and `FSD_DFACL` records into `vsecattr_t`, sorts and validates them, converts them into an in-core `si_t`, and inserts the result into both ACL caches. Internal inconsistencies mark the shadow inode `ISTALE` so stray damaged shadow inodes are not kept alive.

`ufs_acl_access` implements the POSIX ACL access algorithm: owner entry first, then matching `ACL_USER`, then owning group and matching `ACL_GROUP` entries under the ACL mask, and finally `OTHER_OBJ`. Privilege fallback is delegated through `MODE_CHECK`.

`ufs_acl_get` returns either the stored ACL via `aclentry2vsecattr` or fabricates a four-entry ACL from mode bits (`USER_OBJ`, `GROUP_OBJ`, `OTHER_OBJ`, `CLASS_OBJ`) when no shadow ACL exists. `ufs_acl_set` requires owner or privilege, converts caller-provided `vsecattr_t` to `si_t`, normalizes owner and group object IDs to the inode UID/GID, and stores it through `ufs_si_store`.

The conversion and validation layer includes `acl_validate`, `vsecattr2aclentry`, `aclentry2vsecattr`, `formacl`, `formvsec`, `ufs_sectobuf`, and ACL list copy/free helpers. Validation rejects duplicate entries, unknown types, bad permissions, missing required regular ACL owner/group/other entries, group entries without masks, malformed default ACL triples, and lists exceeding `MAX_ACL_ENTRIES`.

`ufs_si_inherit` constructs inherited ACLs from a parent directory's default ACL. It requires a complete default owner/group/other triple, copies default entries into the child's access ACL, applies creation mode to owner/group/other entries, applies the mask when present, and propagates default ACLs to child directories. It stores the inherited ACL under the child inode's write lock and restores mode/UID/GID on failure.

`ufs_acl_setattr` keeps ACL state consistent with chmod/chown/chgrp. It copies the current ACL, updates owner permissions, mask-or-group permissions, other permissions, owner UID, and group GID as requested by the `vattr`, then stores the modified ACL.

The ACL cache uses two hash tables protected by `si_cache_lock`: `si_cachea` by ACL signature/content for deduplication, and `si_cachei` by shadow inode for loading. Individual `si_t` objects use `s_lock`, `s_ref` tracks in-memory references, and `s_use` tracks shadow inode link count. `si_cache_del` carefully removes only zero-reference entries while avoiding a known race where another thread may already have deleted or reattached the ACL. `ufs_si_cache_flush` removes all ACLs for a device, and `ufs_si_del` detaches an ACL from an in-core inode.

Integration notes: ACL correctness depends on shadow inode link counts matching `s_use`, in-memory references matching `s_ref`, and releasing `s_lock` before `VN_RELE` paths that can reacquire inode locks. Shadow inodes intentionally have no quota records. Cache lookup by signature is only a candidate filter; exact ACL comparison is still required.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_alloc.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_alloc.c

This file implements UFS block, fragment, inode, preallocation, and free-space allocation policy. It bridges quota accounting, cylinder-group bitmaps, rotational layout, UFS logging metadata tracking, and filesystem lock coordination.

`alloc` allocates a block or fragment for an inode. It validates size, checks filesystem free space and minfree privilege, reserves block quota through `chkdq`, chooses a preferred cylinder group, and calls `hashalloc` with `alloccg`. If physical allocation loses a race after quota reservation, it rolls quota back. Full-filesystem warnings are rate-limited through `vfs_lastwhinetime`.

`realloccg` grows an existing fragment. It reserves quota for the size delta, first tries `fragextend` to extend in place, then falls back to allocating either a full block under `FS_OPTTIME` or exactly the requested fragment run under space optimization. Unused fragments from a full-block allocation are immediately freed. Failed allocation rolls back the quota delta.

`ufs_ialloc` allocates an inode. It charges inode quota except for shadow inodes and extended attribute directory inodes, finds a free inode through `hashalloc`/`ialloccg`, then obtains and initializes the inode. If the supposedly free inode is unexpectedly allocated, it marks it `ISTALE`, warns to run fsck, and retries. If stale size or block pointers remain on a free inode, it clears them defensively to avoid exposing old data, accepting that fsck may later report unaccounted blocks.

`dirpref` chooses a cylinder group for new directories. With `ufs_close_dirs` enabled, it prefers the current or first cylinder group with more than 25% free inodes and blocks; otherwise it falls back to the traditional policy of choosing a group with at least average free inodes and few directories.

`blkpref` chooses the preferred physical location for the next logical block. It keeps early direct blocks near the inode's cylinder group, starts later block groups in cylinder groups with above-average free blocks, and otherwise prefers contiguous blocks up to `fs_maxcontig`, adding rotational delay spacing when configured. It also understands negative fallocate block markers by converting them back into positive physical preferences.

`free` returns blocks or fragments to a cylinder group bitmap. It handles negative fallocate block numbers, validates size and block range, cancels logging reservations unless told not to, marks metadata frees, updates free block/fragment summaries, fragment summary buckets, rotational summaries, delete-queue accounting for logged filesystems, superblock summary state, and cylinder group buffers. It detects attempts to free already-free blocks or fragments and reports filesystem faults.

`ufs_ifree` returns an inode to the cylinder group inode bitmap, validates range and current mode, updates the inode rotor, free inode counts, directory counts, clean state, and logging metadata. It reports double-free and range corruption through `ufs_fault`.

The lower-level allocation helpers are `hashalloc`, `fragextend`, `alloccg`, `alloccgblk`, `ialloccg`, and `mapsearch`. `hashalloc` tries the preferred cylinder group, quadratic rehash, then brute-force search. `alloccg` allocates either full blocks or fragments, splitting a full block when needed. `alloccgblk` honors an exact preferred block, then same-cylinder rotational layout, then the cylinder-group block rotor. `mapsearch` scans the fragment bitmap for a matching run while avoiding blocks on the logging cancel list.

`ufs_allocsp` implements UFS preallocation/fallocate. It write-locks the filesystem, holds `i_rwlock` across the operation, allocates direct blocks normally, then allocates indirect-referenced blocks as negative block numbers to mark preallocated-but-unwritten storage. It breaks the work into `vfs_iotransz` transactions, yields the filesystem write lock to waiters between chunks, sets `IFALLOCATE` on success or partial interruption, updates large-file superblock state, and rolls back direct and indirect allocations on error using saved direct block state and an undo list.

`ufs_freesp` implements the supported free-space operation: `l_len == 0`, meaning truncate/free from `l_start` to EOF. It checks mandatory locks, takes `i_rwlock` to exclude block allocation, and delegates to `TRANS_ITRUNC`.

`contigpref` and `findlogstartcg` search for contiguous block ranges for UFS log placement. `findlogstartcg` uses a sliding window over cylinder-group free-block summaries to find the smallest group span that can satisfy the requested size while respecting the log extent table capacity.

Integration notes: allocation routines must pair quota reservations with physical allocation success, must not reuse blocks currently on the logging cancel list, and must update cylinder group, superblock summary, and transaction metadata together. The fallocate negative-block convention is understood by this file and by `ufs_bmap.c`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_bmap.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_bmap.c

This file maps UFS logical file offsets to physical disk blocks and allocates blocks during writes. It handles direct blocks, single/double/triple indirect blocks, fragments, holes, preallocated negative block markers, synchronous metadata safety, and partial-allocation rollback.

`bmap_read` maps an offset to a disk block and transfer length without allocation. It handles direct blocks through the `DOEXTENT` macro, walks indirect blocks for larger logical block numbers, returns `UFS_HOLE` for missing pointers, limits extents by EOF and `vfs_iotransz`, and returns disk block numbers rather than filesystem block numbers.

`bmap_write` ensures that a block range exists for a write or preallocation request. For direct blocks it grows the previous last fragment to a full block when crossing a block boundary, allocates or reallocates the target fragment/block, zeroes or reads pages as needed, updates `i_db`, `i_blocks`, inode transaction state, and frees old fragments when a reallocation moved them. Directories, quota files, shadow inodes, and synchronous inodes force normal allocation and more conservative zero/write ordering.

For indirect blocks, `bmap_write` determines the required indirection depth, allocates missing indirect blocks synchronously zeroed before linking them, then allocates missing data blocks. It keeps an `ufs_allocated_block` undo table recording newly allocated blocks, their owner pointer location, and free flags. If any later read, write, or allocation fails, `ufs_undo_allocation` removes any installed pointers before freeing blocks to avoid creating double-owned blocks. For `BI_FALLOCATE`, lowest-level data block pointers are stored as negative block numbers.

The very-large-file guard protects the signed 32-bit `i_blocks` field. When `ip->i_blocks` approaches the `VERYLARGEFILESIZE` threshold, allocation checks whether adding metadata or data sectors would exceed `INT_MAX` and returns `EFBIG` before corrupting the count.

`bmap_has_holes` uses file length and allocated block count, including expected indirect metadata blocks, to conservatively detect sparse files. If another thread is in the writer critical region, it reports holes because `i_size` and `i_blocks` cannot be trusted.

`findextent` scans contiguous direct or indirect block-pointer arrays and returns an extent length capped by `fs_maxcontig` or the device transfer size. This is the helper behind read-side clustering in `DOEXTENT`.

`ufs_undo_allocation` is the rollback engine for indirect allocation failure. It first clears inode or indirect-block pointers and logs those pointer updates; only if pointer updates succeed does it free the newly allocated blocks. It adjusts `i_blocks`, marks the inode changed, and writes the inode synchronously on non-logging filesystems so the filesystem does not transiently point at blocks it has returned to free space.

`bmap_find` searches from an offset for the next hole or data block. It checks direct blocks first, then walks indirect levels using cached buffers per level, skips whole missing indirect subtrees when looking for data, and returns `ENXIO` at or beyond EOF. This is suitable for SEEK_HOLE/SEEK_DATA-style behavior.

`bmap_set_bn` overwrites the block pointer for a logical offset, directly in `i_db` or inside the appropriate indirect block. It requires the caller to hold inode locking and to perform transaction logging. It is used by allocation rollback paths such as `ufs_allocsp` undo.

Integration notes: `bmap_write` is called with `i_contents` held for write and assumes truncation is excluded by higher-level locking. Metadata blocks are synchronously zeroed before being linked so crashes do not leave indirect blocks pointing through garbage. Fallocate's negative block numbers must be preserved until later write/read paths convert or zero them appropriately.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_bmap.c -->