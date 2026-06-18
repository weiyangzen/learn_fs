# Group Research: group_453_freebsd_src_sources_os_bsd_freebsd_src_sys_ufs_ffs_ffs_snapshot_c_so_c89d4f8e99fe

Scope: `Docs/research_subset_a.md`  
Source tree: `sources/os/bsd/freebsd-src`  
Files read completely: `ffs_snapshot.c`, `ffs_subr.c`, `ffs_suspend.c`, `ffs_tables.c`, `ffs_vfsops.c`, `ffs_vnops.c`

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_snapshot.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_snapshot.c

## Role

Implements FreeBSD FFS snapshot support: snapshot file creation, copy-on-write protection, snapshot mount/unmount reattachment, snapshot deletion cleanup, and deferred inactive processing around suspended filesystems.

When `NO_FFS_SNAPSHOT` is defined, this file provides stub entry points returning `EINVAL` or doing nothing. Otherwise it provides the active snapshot subsystem.

## Main Responsibilities

- Creates snapshot files through `ffs_snapshot()`.
- Preallocates snapshot file direct/indirect blocks and metadata copies.
- Suspends filesystem writes while building a consistent snapshot image.
- Copies cylinder group maps, superblock, summary information, and snapshot block lists into the snapshot file.
- Expunges unlinked active files and soft-updates journal state from the snapshot view.
- Maintains per-device `struct snapdata` with a shared snapshot lock, active snapshot list, and preallocated block hint list.
- Handles copy-on-write when filesystem/device buffers are about to be written.
- Handles block-free notifications so snapshots can claim or copy blocks before they disappear.
- Reattaches persisted snapshots at mount time and detaches them at unmount time.
- Removes snapshot-specific block markers before a snapshot file is deleted.
- Processes deletes and lazy access-time updates deferred while writes were suspended.

## Important Data Structures

- `struct snapdata`: per-device snapshot state, stored at `devvp->v_rdev->si_snapdata`.
- `sn_head`: active snapshot inode tail queue, oldest to newest.
- `sn_lock`: shared lock used as the vnode lock for snapshot vnodes.
- `sn_blklist`: sorted list of logical blocks preallocated or otherwise safe from ordinary COW checks.
- `fs->fs_snapinum[]`: persistent superblock snapshot inode list.
- `ip->i_nextsnap`: inode linkage in the active snapshot queue.
- `ip->i_snapblklist`: temporary pointer while building the final snapshot block list.
- Magic block pointer values:
  - `BLK_NOCOPY`: snapshot does not need a copy of this logical block.
  - `BLK_SNAP`: block is owned/claimed by snapshot semantics rather than ordinary file mapping.
  - `0`: snapshot still needs the original block if it changes.

## Snapshot Creation Flow

`ffs_snapshot()` performs a multi-phase creation:

1. Rejects gjournal mounts because snapshots are unsupported with gjournal.
2. Finds a free `fs_snapinum[]` slot.
3. Creates the target regular file with `VOP_CREATE()` on the same mount.
4. Marks the vnode `VV_SYSTEM`, initializes a VM object, and makes it an `SF_SNAPSHOT` inode.
5. Sets snapshot size to filesystem size plus one block for the snapshot block list.
6. Preallocates indirect blocks, superblock copy space, summary info blocks, and cylinder group blocks.
7. Copies cylinder group maps before suspension and tracks changed cylinder groups through `fs->fs_active`.
8. Syncs the snapshot vnode, unlocks it, and suspends filesystem writes with `vfs_write_suspend()`.
9. Re-copies cylinder groups changed during the first pass.
10. Copies the in-memory superblock and summary data to temporary memory.
11. Temporarily clears `MNTK_SUSPENDED` to inspect active vnodes.
12. Expunges unlinked active files and the SUJ journal from the snapshot image.
13. Preallocates all direct snapshot blocks to avoid later inode writes for COW commits.
14. Acquires/creates `snapdata`, switches the snapshot vnode to the shared `snaplk`, and links the inode into `sn_head`.
15. Resumes writes with `vfs_write_resume()`.
16. Expunges older snapshots from the new snapshot’s view and computes the final block list.
17. Writes the snapshot block list, summary info, and snapshot superblock into the snapshot file.

This is a good example of a filesystem snapshot built using an ordinary file plus special block-pointer semantics rather than a separate volume object.

## Cylinder Group and Metadata Accounting

`cgaccount()` copies a cylinder group block into the snapshot and marks free blocks as `BLK_NOCOPY` in the snapshot inode mapping. On a second pass it undoes stale `BLK_NOCOPY` marks for blocks that became allocated between the first copy and write suspension. It also updates cylinder group check hashes when enabled.

The UFS1 and UFS2 accounting code is duplicated by block pointer width:

- `expunge_ufs1()` / `expunge_ufs2()` clear an inode’s image in the snapshot and walk all direct/indirect blocks.
- `indiracct_ufs1()` / `indiracct_ufs2()` recursively traverse indirect block trees.
- `fullacct_*()` combines snapshot pointer marking with allocation bitmap updates.
- `snapacct_*()` marks blocks as `BLK_SNAP` or `BLK_NOCOPY` in the snapshot inode.
- `mapacct_*()` frees corresponding blocks from the copied allocation maps and optionally records logical block numbers in the snapshot block list.

## Copy-on-Write and Block-Free Handling

`ffs_copyonwrite()` is called from the FFS device strategy path before writes hit the underlying provider:

- Ignores writes to snapshot files themselves.
- Rejects recursive COW with `TDP_COWINPROGRESS`.
- Uses `sn_blklist` as a fast preallocated-block exclusion list.
- Locks the shared snapshot lock and checks each active snapshot inode.
- Allocates a snapshot block where needed, reads the old device block, and writes it into the snapshot.
- Writes synchronously for metadata, directories, or all data when `dopersistence` is enabled; otherwise it may use async writes.
- Temporarily backs the original buffer out of running-buffer accounting while waiting on snapshot locks.

`ffs_snapblkfree()` handles block deletion before free proceeds:

- If a full block is being freed and a snapshot needs it, the snapshot can claim the original block directly.
- If a fragment is being freed, snapshots copy the whole block because snapshots claim full blocks only.
- If a previous snapshot has already claimed the block, later snapshots can mark it `BLK_NOCOPY`.
- On allocation/copy failure, it returns non-zero to prevent freeing, preserving snapshot consistency at the cost of leaked space.

## Snapshot Lifecycle

- `ffs_snapshot_mount()` reads `fs_snapinum[]`, validates persisted snapshot files, switches their vnode locks to `sn_lock`, links them to `sn_head`, reads the newest snapshot block list, and enables `VV_COPYONWRITE` on the device vnode.
- `ffs_snapshot_unmount()` removes snapshot inodes from `sn_head`, restores vnode locks, drops references, and frees/recycles `snapdata` when possible.
- `ffs_snapgone()` handles last-name removal by dropping the extra snapshot vnode reference and deleting the inode number from `fs_snapinum[]`.
- `ffs_snapremove()` unlinks an active snapshot from the in-core list, clears `BLK_NOCOPY` / `BLK_SNAP` markers, pushes claimed blocks to other snapshots if needed, clears `SF_SNAPSHOT`, and re-enables quota charging.

## Locking and Concurrency

Snapshot locking is unusual and central to the file:

- All snapshots on a device share one `sn_lock`.
- Snapshot vnodes mutate `v_vnlock` from their private lock to `sn_lock`.
- `revert_snaplock()` safely restores a vnode’s private lock while preserving recursion counts.
- `ffs_snapdata_acquire()` publishes new `snapdata` with `sn_lock` already held to avoid races.
- `try_free_snapdata()` drains and recycles `snapdata`, but `snapdata` objects are kept on a free list rather than destroyed because threads may have slept on the lock.
- Device vnode interlock protects `si_snapdata`, `VV_COPYONWRITE`, and snapshot-list transitions.
- Several paths set `TDP_COWINPROGRESS` to prevent recursive snapshot allocation/COW loops.

## Buffer Flushing

`ffs_bdflush()` customizes dirty-buffer flushing when snapshots exist. It avoids flushing the triggering snapshot block in ways that would worsen snapshot lock contention, and it preferentially selects suitable dirty buffers. `ffs_bp_snapblk()` checks whether a buffer maps a block in the snapshot block list.

## Deferred Inactive Processing

`process_deferred_inactive()` is compiled regardless of snapshot support. It runs after suspended writes resume and:

- Converts `IN_LAZYACCESS` to `IN_MODIFIED`.
- Calls `vinactive()` for vnodes that owed inactive processing while the filesystem was suspended.
- Restarts vnode iteration when vnode locking races require it.

## Research Relevance

This file is highly relevant to filesystem research because it shows a mature in-kernel snapshot design layered onto FFS allocation metadata. It demonstrates write suspension, persistent snapshot discovery, block-level COW, interaction with soft updates, special vnode lock mutation, and correctness tradeoffs between metadata persistence and data persistence.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_snapshot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_subr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_subr.c

## Role

Provides shared FFS/UFS support routines used both in-kernel and by userland filesystem tools. It focuses on superblock loading, validation, recovery, writing, metadata check hashes, old-format compatibility, fragment accounting, block bitmap operations, and cluster accounting.

## Main Responsibilities

- Verifies and updates UFS2 inode check hashes.
- Reads a superblock from standard or alternate locations.
- Loads cylinder group summary information into `fs->fs_si`.
- Validates superblock field consistency and rejects unsafe values.
- Handles old UFS1/UFS2 compatibility field normalization on read and write.
- Searches alternate superblocks and boot-zone recovery data when the primary superblock is unusable.
- Writes superblock and summary information through caller-provided I/O callbacks.
- Calculates superblock check hashes.
- Updates fragment summary counters.
- Tests, sets, and clears free-block bitmap state.
- Updates cluster summary information for contiguous free block runs.

## Kernel/Userland Boundary

The file is written for dual use:

- In kernel builds, it includes vnode, buffer, mount, quota, inode, and sysctl headers and uses typed kernel malloc wrappers.
- Outside the kernel, it includes libc headers and exposes compatible allocation wrappers for tools such as libufs/fsck/newfs-style code.

The `ffs_sbget()` / `ffs_sbput()` APIs receive caller-provided read/write callbacks, so the same validation and serialization logic works across kernel buffers and userland device access.

## Superblock Read Path

`ffs_sbget()`:

- Reads either a requested alternate superblock or searches the `SBLOCKSEARCH` locations.
- Calls `readsuper()` for each candidate.
- Optionally stops after the superblock if `UFS_NOCSUM` is set.
- Allocates and fills `struct fs_summary_info`.
- Reads the cylinder group summary table from `fs_csaddr`.
- Initializes `fs_maxcluster` and `fs_contigdirs` in the summary area.

`readsuper()`:

- Calls the supplied block read function.
- Rejects `FS_BAD_MAGIC`.
- Handles the UFS1 64K block-size ambiguity around the UFS2 superblock location.
- Runs old-filesystem compatibility normalization.
- Runs full or recovery-only validation.
- Clears unsupported metadata check-hash and filesystem flags.
- Verifies the superblock check hash unless flags allow hash failure.
- Records `fs_sblockactualloc`.

## Validation and Recovery

`validate_sblock()` performs dense structural checks on:

- Magic number and endian mismatch.
- Superblock location.
- Block, fragment, sector, and cylinder group sizing.
- Inode geometry.
- Summary table location and size.
- Free inode/directory counts.
- Old UFS1 rotational layout fields.
- Maximum file size.
- Contiguous allocation parameters.

It distinguishes hard failures from warnings through `FCHK`, `WCHK`, and `FCHK2`. `UFS_NOWARNFAIL` can allow non-critical values to be normalized rather than fatal.

`ffs_sbsearch()` implements escalating recovery:

1. Try the standard superblock quietly.
2. Try the standard superblock while ignoring check-hash failures.
3. Try to use enough standard-superblock data to locate alternates.
4. If that fails, read UFS2 recovery data from the boot area.
5. Scan alternate cylinder group superblocks.
6. As a last resort, accept a standard superblock with only non-critical errors.

## Compatibility Handling

`ffs_oldfscompat_read()` updates older filesystems into the in-memory layout expected by current code:

- Copies old UFS1 fields into widened modern fields.
- Initializes `fs_flags` and `fs_sblockloc` where old filesystems lack them.
- Bounds UFS1 maximum file size.
- Supplies default average file size and files-per-directory values.

`ffs_oldfscompat_write()` copies fields back for on-disk compatibility and corrects unexpected superblock locations.

`ffs_oldfscompat_inode_read()` handles old UFS1 signed/unsigned timestamp issues by clamping future-looking times to the current mount time and marking the inode modified when needed.

## Metadata Check Hashes

- `ffs_verify_dinode_ckhash()` checks a UFS2 dinode CRC32C, excluding `di_ckhash` itself.
- `ffs_update_dinode_ckhash()` recomputes that field after inode changes.
- `ffs_calc_sbhash()` computes the superblock CRC32C, but returns the existing hash unchanged when superblock hashing is disabled.
- `readsuper()` disables metadata hashes if the filesystem was touched by a kernel that did not maintain them.

## Allocation Bitmap Helpers

`ffs_fragacct()` updates fragment availability summaries using the `fragtbl`, `around`, and `inside` tables from `ffs_tables.c`.

Block bitmap helpers are specialized by `fs_frag`:

- `ffs_isblock()` tests whether a full block is allocated/available in a fragment bitmap.
- `ffs_isfreeblock()` tests whether a full block is free.
- `ffs_clrblock()` clears a full block from the bitmap.
- `ffs_setblock()` sets a full block in the bitmap.

These helpers encode the historical FFS fragment layout for fragment counts 1, 2, 4, and 8.

## Cluster Accounting

`ffs_clusteracct()` maintains contiguous free-cluster summaries:

- Updates the cluster-free bitmap for an allocation or free.
- Scans forward and backward from the changed block.
- Adjusts the cluster length summary counts.
- Updates `fs->fs_maxcluster[cg]` to the largest available cluster in a cylinder group.

This supports FFS clustered allocation and read/write planning.

## Research Relevance

This file is central for understanding FFS on-disk trust boundaries. It captures how FreeBSD validates legacy metadata, recovers from damaged superblocks, maintains compatibility across decades of UFS format evolution, and represents fragment/cluster allocation summaries that higher-level allocation code depends on.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_suspend.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_suspend.c

## Role

Implements the `/dev/ufssuspend` character device used to suspend and resume writes to an FFS filesystem, and to permit controlled raw block reads/writes while the filesystem is suspended.

## Main Responsibilities

- Registers the `ffs_susp` character device.
- Implements `UFSSUSPEND` and `UFSRESUME` ioctls.
- Uses VFS write suspension to quiesce a mounted FFS filesystem.
- Associates a suspended mount with the caller’s file descriptor through `devfs_set_cdevpriv()`.
- Automatically resumes the filesystem when the descriptor is closed.
- Allows block-aligned reads and writes to the underlying device while suspended.
- Reloads filesystem metadata before unsuspending after forced descriptor cleanup.

## Character Device Interface

`ffs_susp_cdevsw` provides:

- `ffs_susp_open()`: trivial open.
- `ffs_susp_rdwr()`: read/write handler for raw device blocks.
- `ffs_susp_ioctl()`: suspend/resume control path.

`ffs_susp_initialize()` creates `/dev/ufssuspend` with mode `0600`; `ffs_susp_uninitialize()` destroys it.

## Suspend Flow

`ffs_susp_ioctl(UFSSUSPEND)`:

1. Rejects jailed callers.
2. Looks up the mount by `fsid_t`.
3. Takes a busy reference.
4. Requires the calling process to be single-threaded.
5. Checks that the process has no writable descriptors on the target mount.
6. Calls `ffs_susp_suspend()`.
7. Stores the mount in cdev private data with `ffs_susp_dtor()` as destructor.

`ffs_susp_suspend()`:

- Verifies the mount belongs to FFS via `ffs_own_mount()`.
- Rejects already suspended mounts.
- Checks read/write access to the original device vnode.
- Runs MAC mount stat policy when enabled.
- Calls `vfs_write_suspend(mp, VS_SKIP_UNMOUNT)`.
- Sets `UM_WRITESUSPENDED`.

## Resume Flow

`ffs_susp_ioctl(UFSRESUME)` clears the cdev private data. That invokes `ffs_susp_dtor()`, which:

- Checks whether the mount is still suspended.
- Calls `ffs_reload(mp, FFSR_FORCE | FFSR_UNSUSPEND)` to reload metadata and clear suspension flags.
- Panics if reload fails, since leaving the filesystem suspended would be fatal.
- Calls `ffs_susp_unsuspend()`.

`ffs_susp_unsuspend()` works around the fact that `vfs_write_resume()` expects the resuming thread to match the suspending thread by assigning `mp->mnt_susp_owner = curthread`, then resumes writes, clears `UM_WRITESUSPENDED`, and unbusies the mount.

## Raw I/O While Suspended

`ffs_susp_rdwr()`:

- Requires cdev private data to identify a suspended mount.
- Rejects I/O if the mount is not currently suspended.
- Operates on `ump->um_devvp`.
- Requires user-space `uio`.
- Requires offsets and lengths aligned to filesystem fragment boundaries.
- Limits each transfer to `fs->fs_bsize`.
- Uses `bread()` to read the device block.
- For writes, copies user data into the buffer and calls `bwrite()`.
- For reads, copies buffer contents back to userland and releases the buffer.

This interface supports tools that need a stable on-disk image while normal filesystem mutation is blocked.

## Locking and State

- `ffs_susp_lock` serializes suspend/resume and raw I/O state.
- Shared locking protects read/write access while suspended.
- Exclusive locking protects suspend/resume transitions.
- `UM_WRITESUSPENDED` records FFS-level suspended state.
- `MNTK_SUSPEND` is asserted during destructor cleanup.

## Research Relevance

This file is relevant for snapshotting, fsck, backup, and external metadata tooling research. It shows how FreeBSD exposes a privileged, descriptor-scoped write suspension mechanism and how that mechanism coordinates VFS suspension, FFS reload, raw device access, and process lifetime cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_suspend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_tables.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_tables.c

## Role

Defines static fragment allocation lookup tables used by FFS allocation accounting code.

## Main Responsibilities

- Provides bit masks for detecting contiguous fragment runs.
- Provides precomputed fragment availability tables for supported fragment layouts.
- Exposes `fragtbl[]` indexed by `fs->fs_frag`.

## Important Data

- `around[9]`: masks for identifying a run plus surrounding bits.
- `inside[9]`: expected bit patterns for an available fragment run within the `around` mask.
- `fragtbl124[256]`: fragment availability table for fragment counts 1, 2, and 4.
- `fragtbl8[256]`: fragment availability table for fragment count 8.
- `fragtbl[MAXFRAG + 1]`: dispatch table mapping fragment count to the correct lookup table.

## How It Is Used

`ffs_fragacct()` in `ffs_subr.c` uses these tables to update cylinder group fragment summary counts when fragments are allocated or freed.

For a given block bitmap byte pattern, the tables report whether a fragment of a particular size exists. This avoids recomputing contiguous-fragment availability from scratch for common bitmap patterns.

## Research Relevance

This file is small but important for understanding classic FFS fragment accounting. It captures the precomputed table-driven design used to make fragment allocation fast, especially in historical architectures where instructions such as VAX `scanc` could exploit compact lookup tables.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_tables.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_vfsops.c

## Role

Implements the FreeBSD VFS operations for the `ufs` filesystem when backed by FFS. It owns mount, remount, unmount, sync, statfs, vnode lookup by inode/file handle, superblock update, device strategy integration, initialization, and teardown.

## Main Responsibilities

- Registers `ufs_vfsops` with the VFS layer.
- Mounts FFS filesystems from GEOM-backed disk vnodes.
- Handles mount updates, including read-only/read-write transitions and snapshot requests.
- Loads and validates superblocks through `ffs_sbget()` / `ffs_sbsearch()`.
- Constructs and tears down `struct ufsmount`.
- Sets feature flags for ACLs, NFSv4 ACLs, MAC multilabel, TRIM, soft updates, gjournal, and untrusted mounts.
- Reloads in-core filesystem state after fsck or write suspension.
- Flushes vnodes, quotas, snapshots, softdep work, TRIM work, device buffers, and superblocks.
- Implements inode-to-vnode and file-handle-to-vnode lookup.
- Maintains UMA zones for inodes and UFS1/UFS2 dinodes.
- Provides custom FFS buffer operations and GEOM strategy glue.
- Initiates forced unmount cleanup when media disappears with `ENXIO`.

## VFS Registration

`ufs_vfsops` supplies:

- `vfs_mount`: `ffs_mount`
- `vfs_cmount`: `ffs_cmount`
- `vfs_unmount`: `ffs_unmount`
- `vfs_statfs`: `ffs_statfs`
- `vfs_sync`: `ffs_sync`
- `vfs_vget`: `ffs_vget`
- `vfs_fhtovp`: `ffs_fhtovp`
- `vfs_extattrctl`: `ffs_extattrctl`
- `vfs_susp_clean`: `process_deferred_inactive`
- root handling through `vfs_cache_root` / `ufs_root`

The module is registered as `ufs` and uses FFS-specific vnode and buffer operations.

## Mount Path

`ffs_mount()` parses options and handles three major cases:

- Snapshot requests: `MNT_SNAPSHOT` on an update mount calls `ffs_snapshot()`.
- New mounts: resolves the device vnode, checks access, then calls `ffs_mountfs()`.
- Update mounts: validates the same device, supports read-write to read-only, read-only to read-write, and reload operations.

`ffs_mountfs()`:

- Allocates a private mount device vnode with `mntfs_allocvp()`.
- Opens the provider through GEOM.
- Installs FFS buffer operations on the device vnode.
- Reads the superblock and summary info.
- Rejects unsafe dirty filesystems unless read-only, forced, or otherwise allowed.
- Allocates `struct ufsmount` and fills function pointers for allocation, truncate, update, valloc/vfree, read-only checks, and snapshots.
- Configures UFS1 versus UFS2 behavior.
- Enables untrusted block validation if requested.
- Sets mount fsid and local mount flags.
- Configures MAC, ACL, NFSv4 ACL, TRIM, and speedup capabilities.
- Starts soft updates when configured.
- Reattaches existing snapshots with `ffs_snapshot_mount()`.
- Marks the filesystem dirty on writable mounts and writes the superblock.

## Remount and Reload

Read-only transition:

- Suspends writes.
- Flushes files via softdep or ordinary FFS flush.
- Marks the filesystem clean if appropriate.
- Writes the superblock.
- Tears down soft updates and GEOM write access.
- Sets `MNT_RDONLY`.

Read-write transition:

- Checks device permissions.
- Rejects unclean filesystems unless forced or allowed by softdep/SUJ rules.
- Reopens GEOM write access.
- Suspends writes during transition.
- Starts soft updates if needed.
- Marks the filesystem dirty.
- Writes the superblock.
- Reattaches snapshots.

`ffs_reload()`:

- Requires read-only mount unless forced.
- Invalidates device metadata buffers.
- Re-reads the superblock.
- Replaces `ump->um_fs`.
- Optionally clears suspension flags for unsuspend.
- Iterates active vnodes, invalidates file data, and reloads inode contents from disk.

## Inode Loading and Validation

`ffs_load_inode()` copies UFS1 or UFS2 dinodes into `struct inode`.

- UFS1: copies legacy fields and applies timestamp compatibility fixes.
- UFS2: verifies dinode check hash before accepting the inode.
- Both paths update mode, nlink, size, flags, generation, uid, and gid.

`ffs_check_blkno()` is enabled for `MNT_UNTRUSTED` mounts. It verifies data block pointers are inside legal filesystem data regions and do not point into inode/superblock areas, except for zero and snapshot marker values.

## Failure Cleanup

`ffs_fsfail_cleanup()` and `ffs_fsfail_cleanup_locked()` handle `ENXIO` media-loss failures:

- Mark `UM_FSFAIL_CLEANUP`.
- Panic if the affected mount is root.
- Queue a forced deferred recursive unmount.
- Return whether cleanup is in progress.

`ffs_breadz()` wraps buffered reads and can synthesize zeroed buffers during cleanup so soft updates can unwind dependencies even when the device can no longer be read.

## Unmount and Flush

`ffs_unmount()`:

- Stops extended attributes.
- Suspends writes on writable mounts.
- Flushes through softdep or `ffs_flushfiles()`.
- Unmounts soft updates.
- Marks the filesystem clean when possible.
- Writes the final superblock.
- Resumes suspended writes.
- Drains TRIM queues.
- Closes GEOM, releases vnodes/devices, destroys locks, and frees mount/superblock memory.

`ffs_flushfiles()`:

- Flushes user vnodes.
- Turns off quotas.
- Detaches active snapshots and forces system vnode closure when snapshots were active.
- Waits for TRIM work to drain.
- Fsyncs the device vnode.

## Sync and Statfs

`ffs_statfs()` reports block and inode totals using superblock summary counts plus pending softdep blocks/inodes.

`ffs_sync_lazy()` handles access-time-only lazy syncs and superblock updates.

`ffs_sync()`:

- Iterates dirty vnodes and calls `ffs_syncvnode()`.
- Flushes softdep work for wait syncs.
- Fsyncs the device vnode.
- Coordinates `MNT_SUSPEND` by checking softdep and secondary write counters, then setting `MNTK_SUSPEND2 | MNTK_SUSPENDED`.
- Writes the superblock if modified.

## Vnode Lookup and File Handles

`ffs_vgetf()`:

- Uses the VFS inode hash.
- Allocates `struct inode` from UMA.
- Creates a vnode with UFS1 or UFS2 vnode operations.
- Reads or initializes the dinode.
- Loads softdep inode dependencies when needed.
- Calls `ufs_vinit()` to set vnode type and aliases.
- Generates a missing inode generation number for old filesystems.
- Associates MAC labels for multilabel mounts.
- Marks the vnode constructed.

`ffs_inotovp()` validates inode range, checks UFS2 lazy inode initialization, gets the vnode, and verifies mode, generation, and link count for NFS/file-handle safety.

`ffs_fhtovp()` maps `struct ufid` file handles to vnodes through `ffs_inotovp()`.

## Superblock Update Path

`ffs_sbupdate()` serializes superblock updates through the superblock buffer, copies the in-memory superblock into it, clears `fs_fmod`, and calls `ffs_sbput()` with `ffs_use_bwrite()`.

`ffs_use_bwrite()` writes summary blocks and the superblock, marks suspended-write buffers with `B_VALIDSUSPWRT`, integrates softdep superblock dependencies, and returns negative error encoding when the caller must not restore pointer fields.

## Buffer and GEOM Integration

`ffs_ops` installs:

- `ffs_bufwrite()` for custom buffer write behavior.
- `ffs_geom_strategy()` for direct GEOM I/O.
- `ffs_bdflush()` when snapshots are enabled.

`ffs_bufwrite()`:

- Supports background writes for buffers marked `BX_BKGRDWRITE`.
- Copies buffers for async background write so the original remains usable.
- Moves softdep dependencies to the copy.
- Updates cylinder group check hashes before release/write.
- Handles background write completion through `ffs_backgroundwritedone()`.

`ffs_geom_strategy()`:

- Bypasses `VOP_STRATEGY()` for private FFS device vnodes.
- Rejects unauthorized writes during suspension unless `B_VALIDSUSPWRT` is set.
- Runs `ffs_copyonwrite()` before writes when snapshots are active.
- Starts softdep dependencies before write I/O.
- Updates cylinder group CRCs for metadata buffers.
- Marks non-read I/O for ENXIO conversion when enabled.
- Submits the buffer to GEOM via `g_vfs_strategy()`.

## Research Relevance

This file is a broad map of how FFS plugs into FreeBSD VFS and GEOM. It is especially useful for studying mount lifecycle, filesystem trust validation, soft updates integration, snapshot write interception, buffer-cache policy, forced unmount on media loss, and vnode/inode instantiation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_vnops.c

## Role

Implements FFS-specific vnode operations for file I/O, sync, locking, paging, extended attributes, file handles, and paired vnode release. It layers FFS block sizing, allocation, soft updates, snapshots, and UFS2 extended-attribute storage onto the generic UFS vnode operation set.

## Main Responsibilities

- Defines UFS1/UFS2 vnode and FIFO operation vectors.
- Implements `fsync`, `fdatasync`, and vnode-buffer flushing.
- Implements regular file and directory reads.
- Implements regular file and symlink writes.
- Handles direct I/O fallback and clustered I/O.
- Supports UFS2 extended attribute blocks.
- Provides extended attribute VOPs for open/close/get/list/set/delete.
- Integrates with VM page-in through `getpages` and async `getpages`.
- Implements FFS vnode locking with snapshot lock mutation awareness.
- Exports inode/generation file handles.
- Provides `vput_pair` handling for directory compaction and vnode-reclamation races.

## Vnode Operation Vectors

The file registers four operation vectors:

- `ffs_vnodeops1`: UFS1 ordinary vnode ops.
- `ffs_fifoops1`: UFS1 FIFO ops.
- `ffs_vnodeops2`: UFS2 ordinary vnode ops, including extended attributes.
- `ffs_fifoops2`: UFS2 FIFO ops, including extended attributes and `ffsext_strategy()`.

All ordinary vnode vectors inherit from `ufs_vnodeops` and override FFS-specific sync, read, write, reallocblks, locking, page-in, file-handle, and paired release behavior.

## Sync Path

`ffs_fsync()` calls `ffs_syncvnode()` and then, for synchronous soft updates, calls `softdep_fsync()` and retries if dirty buffers reappear.

`ffs_syncvnode()`:

- Flushes softdep inode metadata before full wait syncs.
- Walks dirty vnode buffers.
- Skips or orders indirect blocks based on wait mode, indirect level, and `DATA_ONLY`.
- Calls `softdep_sync_buf()` when dependencies exist.
- Alternates async and sync passes to flush dependency chains.
- Handles truncated-data assertions.
- Waits for outstanding buffer I/O on `MNT_WAIT`.
- Updates inode metadata unless `NO_INO_UPDT` is requested.
- Handles SUJ journal fsync and clears `IN_NEEDSYNC`.

`ffs_fdatasync()` is a data-only `ffs_syncvnode()` call.

## Locking

`ffs_lock()` wraps vnode locking to handle snapshot vnode lock mutation:

- Snapshot vnodes may have `v_vnlock` changed between their private lock and shared `snaplk`.
- If a thread acquires a lock that is no longer the vnode’s current lock, it releases and retries.
- It enables adaptive locking for path lookup cases marked `LK_NODDLKTREAT`.
- Diagnostic builds track exclusive lock generations.

`ffs_unlock_debug()` asserts that modified lazy-list inodes remain on the lazy list and that directory `IN_ENDOFF` state is not leaked at unlock.

## Read Path

`ffs_read()`:

- Supports regular files, directories, and long symlinks.
- Uses `ffs_rawread()` first for `IO_DIRECT` when direct I/O is compiled in.
- Enforces offset and maximum file-size overflow checks.
- Uses unmapped buffer reads and sparse-hole handling.
- Chooses plain `bread`, clustered reads, or readahead depending on mount flags and sequentiality.
- Uses `ffs_read_hole()` to return zeroes for sparse holes reported by `EJUSTRETURN`.
- Moves data with `vn_io_fault_uiomove()` or `vn_io_fault_pgmove()`.
- Sets `IN_ACCESS` unless `noatime` or read-only.

## Write Path

`ffs_write()`:

- Preallocates soft updates journal resources when SUJ is active.
- Supports `IO_APPEND` and enforces append-only files.
- Rejects directory writes.
- Checks file size limits with `vn_rlimit_fsizex()`.
- Uses `UFS_BALLOC()` to allocate or fetch target blocks.
- Uses `BA_CLRBUF` for partial-block writes to prevent stale data exposure.
- Updates vnode pager size before extending writes.
- Updates inode size, `i_size`, and dinode size on extension.
- Uses unmapped buffer uiomove/page move paths.
- Clears invalid full-size buffers after uiomove failures to avoid exposing uninitialized pages through mmap.
- Chooses sync, async, clustered, direct, or delayed writes based on flags and memory pressure.
- Clears setuid/setgid bits after successful non-privileged writes.
- Rolls back writes with `ffs_truncate()` on `IO_UNIT` errors.
- Performs synchronous inode update for `IO_SYNC`.

## Extended Attribute Storage

UFS2 stores extended attributes in inode extension blocks addressed by negative logical block numbers.

Low-level helpers:

- `ffs_extread()` reads from `di_extsize` using negative logical blocks.
- `ffs_extwrite()` writes to extension blocks, grows `di_extsize`, clears buffers as needed, and supports rollback on `IO_UNIT`.
- `ffsext_strategy()` routes negative extension-block I/O correctly for UFS2 and falls back for FIFOs.

In-memory transaction helpers:

- `ffs_findextattr()` searches an aligned packed `struct extattr` area.
- `ffs_rdextattr()` reads and validates the on-disk EA area, truncating at zeroed tails and rejecting overlong entries.
- `ffs_lock_ea()` / `ffs_unlock_ea()` serialize EA transactions through inode flags.
- `ffs_open_ea()` loads the EA area and increments `i_ea_refs`.
- `ffs_close_ea()` commits or aborts, writes the full EA area plus zero padding, frees the cached area on last close, and truncates empty EA storage.

VOPs:

- `ffs_openextattr()` opens an EA transaction.
- `ffs_closeextattr()` optionally commits, rejecting commits on read-only mounts.
- `ffs_deleteextattr()` removes one named attribute and compacts the EA area.
- `ffs_getextattr()` returns one attribute’s size or content.
- `ffs_listextattr()` lists attribute names in a namespace.
- `ffs_setextattr()` appends or rewrites a named attribute, enforces size limits, pads entries to 8-byte alignment, and commits through `ffs_close_ea()`.

## VM Paging

`ffs_getpages()` and `ffs_getpages_async()` choose between the generic vnode pager and buffer-cache pager:

- `ffs_gbp_getblkno()` maps file offsets to FFS logical block numbers.
- `ffs_gbp_getblksz()` reports FFS block size for a logical block.
- `use_buf_pager` sysctl can force buffer pager usage.
- Async getpages invokes the caller’s completion callback when the chosen path does not do so itself.

## File Handles

`ffs_vptofh()` exports inode number and generation in `struct ufid`. This pairs with `ffs_fhtovp()` / `ffs_inotovp()` in `ffs_vfsops.c` for NFS and other file-handle users.

## Paired Vnode Release

`ffs_vput_pair()` is a specialized parent/child release hook used after lookup/create-style operations.

It handles parent directory cleanup before releasing locks:

- If `IN_ENDOFF` is set, truncates the directory to compact unused tail space.
- If `IN_NEEDSYNC` is set, synchronously flushes the directory vnode.
- Releases the directory and optionally the child vnode.

When the child vnode was intentionally left locked by the caller, it handles the possibility that releasing the directory allowed the child to be reclaimed. It may try to reinstantiate the same inode/generation with `ffs_inotovp(..., FFSV_REPLACE_DOOMED)`.

## Research Relevance

This file is the main FFS vnode behavior layer. It is valuable for studying how a production Unix filesystem connects block allocation, buffer cache, VM paging, soft updates, snapshots, extended attributes, and VFS locking into ordinary file read/write and sync semantics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_vnops.c -->