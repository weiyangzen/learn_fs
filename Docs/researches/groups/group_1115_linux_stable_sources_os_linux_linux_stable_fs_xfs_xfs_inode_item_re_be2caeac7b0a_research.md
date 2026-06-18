# Group Research: group_1115_linux_stable_sources_os_linux_linux_stable_fs_xfs_xfs_inode_item_re_be2caeac7b0a

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_inode_item_recover.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_inode_item_recover.c

This file implements log-recovery handling for XFS inode log items. It registers `xlog_inode_item_ops`, providing readahead and pass-2 replay for `XFS_LI_INODE` records.

Key responsibilities:
- `xlog_recover_inode_ra_pass2` issues inode-buffer readahead from either native or 32-bit converted inode log formats.
- `xlog_recover_inode_commit_pass2` replays logged inode core and fork data into the inode buffer, with extensive validation before and after replay.
- `xfs_recover_inode_owner_change` handles post-replay btree owner rewrites needed after extent-swap recovery, instantiating a temporary `xfs_inode` directly from the recovered dinode to avoid `xfs_iget` and transaction-triggering inactive paths during log recovery.
- `xfs_log_dinode_to_disk` converts logged in-core dinode fields to ondisk big-endian fields, including bigtime timestamps, v3 inode fields, CRC LSN, UUID, and 64-bit extent counters.
- `xlog_dinode_verify_extent_counts` validates large extent count feature compatibility, padding, and `nextents + anextents <= nblocks`.
- `xlog_recover_inode_dbroot` converts logged data-fork btree roots into dinode-root format, including metadata btree roots for realtime rmap and realtime refcount files.

Important recovery flow:
1. Convert old log format if needed.
2. Skip replay if the target inode buffer was cancelled.
3. Read the inode buffer with inode-buffer verifiers.
4. Validate target inode magic and logged inode magic.
5. Compare ondisk inode LSN or legacy `di_flushiter` to avoid replaying stale records.
6. Validate file-type-specific fork formats, extent counts, fork offset, and log dinode size.
7. Replay core, device, data fork, and attr fork fields according to `ilf_fields`.
8. Apply owner-change replay for swapext metadata when required and inode is not deleted.
9. Recalculate CRC, verify the final dinode, mark the buffer as log-recovered, and queue it for delayed write.

Dependencies and integration:
- Uses log recovery interfaces from `xfs_log_recover.h`, buffer APIs, inode conversion helpers, bmap btree conversion, realtime metadata btree conversion, tracepoints, and corruption reporting.
- Interacts directly with delayed-write buffer recovery via `xfs_buf_delwri_queue`.
- The code is recovery-critical: it intentionally avoids normal inode cache lifecycle behavior where that could start transactions.

Risk notes:
- Correctness depends on carefully honoring log item field flags and iovec ordering.
- The owner-change replay path deliberately bypasses ordinary inode instantiation; verifier coverage after replay is therefore essential.
- LSN handling is subtle: logged dinode LSN is not trusted, so replay writes `current_lsn` into v3 dinodes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_inode_item_recover.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl.c

This file is the primary native ioctl implementation for XFS. It bridges userspace XFS-specific ioctl ABI requests to filesystem internals for bulk inode queries, geometry, file attributes, extent maps, handles, growfs, labels, reserved blocks, scrub, health, media verification, eof block reclamation, and range exchange/commit operations.

Major areas:
- Legacy bulkstat and inumbers:
  - `xfs_ioc_fsbulkstat` supports `XFS_IOC_FSBULKSTAT_SINGLE`, `XFS_IOC_FSBULKSTAT`, and `XFS_IOC_FSINUMBERS`.
  - `xfs_fsbulkstat_one_fmt` and `xfs_fsinumbers_fmt` convert current internal records to legacy ABI structures.
- v5 bulkstat and inumbers:
  - `xfs_bulk_ireq_setup` validates `xfs_bulk_ireq`, handles special root inode lookup, AG-scoped iteration, metadata-directory exposure, and 64-bit extent-count flags.
  - `xfs_ioc_bulkstat` and `xfs_ioc_inumbers` drive `xfs_bulkstat` / `xfs_inumbers` and write back updated cursors.
- Geometry:
  - `xfs_ioc_fsgeometry` emits v1/v4/v5 filesystem geometry.
  - `xfs_ioc_ag_geometry` reports per-AG geometry.
  - `xfs_ioc_rtgroup_geometry` reports realtime group geometry and, for zoned filesystems, current write pointer state through `xfs_rtgroup_report_write_pointer`.
- File attributes:
  - `xfs_fileattr_get` and `xfs_ioc_fsgetxattra` expose data-fork or attr-fork `file_kattr`.
  - `xfs_fileattr_set` validates and commits xflags, project IDs, extent-size hints, CoW extent-size hints, DAX state preparation, quota accounting, and project quota transfer.
- Extent maps and swapping:
  - `xfs_ioc_getbmap` handles `GETBMAP`, `GETBMAPA`, and `GETBMAPX`.
  - `xfs_ioc_swapext` validates file descriptors, modes, XFS file operations, mount identity, and swapfile status before calling `xfs_swap_extents`.
- Label and reserved blocks:
  - `xfs_ioc_getlabel` and `xfs_ioc_setlabel` read/write the superblock label, sync the primary superblock, update secondary superblocks, and invalidate block-device page cache.
  - `xfs_ioctl_getset_resblocks` gets or sets global reserved block pool state.
- Main dispatcher:
  - `xfs_file_ioctl` routes native ioctl commands, including `FITRIM`, labels, DIO alignment info, bulkstat, geometry, parent pointers, fsmap, scrub, handle operations, attr-by-handle operations, growfs, goingdown, error injection, eof block freeing, exchange/commit range, health monitor, and media verify.

Permission and safety patterns:
- Administrative ioctls generally require `CAP_SYS_ADMIN`.
- Mutating ioctls use `mnt_want_write_file` / `mnt_drop_write_file`.
- Shutdown and readonly checks are used where needed.
- Userspace structures are copied with `copy_from_user`, `copy_to_user`, `get_user`, and `put_user`, with reserved-field validation for newer ABIs.
- File attribute changes integrate with quota allocation and transaction logging before committing.

Integration points:
- Calls into `xfs_itable.c` for bulk inode enumeration.
- Calls into `xfs_iwalk.c` indirectly through bulkstat/inumbers.
- Uses growfs, trim, quota, health, scrub, handle, fsmap, reflink, realtime, zone, and media verification subsystems.

Risk notes:
- This is a broad ABI dispatcher, so compatibility and strict validation are central.
- File attribute updates are transaction-heavy and interact with DAX, realtime placement, quotas, and inode flags.
- Label setting intentionally performs extra synchronous writes and cache invalidation to satisfy userspace discovery tools.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl.h

This header declares the native XFS ioctl-facing entry points and formatter helpers shared by ioctl and compat ioctl code.

Exports:
- `xfs_ioc_swapext` for extent swapping.
- `xfs_fileattr_get` and `xfs_fileattr_set` for VFS file attribute operations.
- `xfs_file_ioctl` for native ioctl dispatch.
- `xfs_file_compat_ioctl` for compat ioctl dispatch.
- `xfs_fsbulkstat_one_fmt` and `xfs_fsinumbers_fmt` for legacy bulkstat/inumbers formatting.

Role:
- Provides the interface between VFS file operations, native ioctl implementation, compat ioctl implementation, and bulk inode query formatting.
- Forward-declares `xfs_bstat`, `xfs_ibulk`, and `xfs_inogrp` to avoid pulling heavier headers into users.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl32.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl32.c

This file implements 32-bit compat handling for XFS ioctls on 64-bit kernels. It translates compat userspace structures, pointer fields, alignment-sensitive layouts, and selected ioctl numbers into native XFS operations.

Major functionality:
- Alignment-specific helpers under `BROKEN_X86_ALIGNMENT`:
  - `xfs_compat_ioc_fsgeometry_v1` copies geometry into the packed 32-bit layout.
  - `xfs_compat_growfs_data_copyin` and `xfs_compat_growfs_rt_copyin` translate growfs requests.
  - `xfs_fsinumbers_fmt_compat` formats inode-group records into compat layout.
- Bulkstat compat:
  - `xfs_ioctl32_bstime_copyin`, `xfs_ioctl32_bstat_copyin`, and `xfs_bstime_store_compat` translate time/stat fields.
  - `xfs_fsbulkstat_one_fmt_compat` formats legacy `xfs_bstat` records for 32-bit userspace.
  - `xfs_compat_ioc_fsbulkstat` handles compat bulkstat, bulkstat single, and inumbers; x32 ABI is special-cased to use native output structure layout while keeping compat input pointers.
- Handle and attr-by-handle compat:
  - `xfs_compat_handlereq_copyin` translates embedded compat pointers.
  - `xfs_compat_attrlist_by_handle` and `xfs_compat_attrmulti_by_handle` enforce `CAP_SYS_ADMIN`, resolve handles, and invoke native attr list/multi operations with compat pointer conversion.
- Main dispatcher:
  - `xfs_file_compat_ioctl` maps compat commands to native helpers, directly handles commands whose structure layout differs, and falls back to `xfs_file_ioctl` for compatible commands.

Security and validation:
- Admin-only paths check `CAP_SYS_ADMIN`.
- Mutating operations acquire write access with `mnt_want_write_file`.
- Multi-attr operation count is overflow checked and capped to at most `16 * PAGE_SIZE`.
- All userspace pointers are converted through `compat_ptr`.

Notable implementation detail:
- `xfs_ioctl32_bstat_copyin` copies many individual `compat_xfs_bstat` fields. The source shows `bs_blocks` and `bs_xflags` being read from `bstat32->bs_size`, which is worth flagging for review because the surrounding field-by-field pattern suggests these should correspond to their own compat fields.

Integration:
- Calls native implementations from `xfs_ioctl.c`, handle helpers, attr helpers, growfs helpers, and itable formatting functions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl32.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl32.h

This header defines 32-bit compat XFS ioctl ABI structures and ioctl numbers.

Contents:
- Includes `<linux/compat.h>`.
- Defines `XFS_IOC_GETVERSION_32`.
- Defines `BROKEN_X86_ALIGNMENT` and `__compat_packed` for x86_64 alignment differences.
- Declares compat versions of:
  - `xfs_bstime`
  - `xfs_bstat`
  - `xfs_fsop_bulkreq`
  - handle request structures
  - `xfs_swapext`
  - attrlist-by-handle and attrmulti-by-handle request structures
  - attr multiop structures
  - x86 alignment-sensitive geometry, inogrp, growfs data, and growfs realtime structures.
- Defines compat ioctl numbers for bulkstat, inumbers, handle operations, swapext, attrlist, attrmulti, geometry v1, and growfs variants.

Role:
- Encodes the ABI contract needed by `xfs_ioctl32.c`.
- Isolates architecture layout differences so the compat dispatcher can translate to native internal structures.

Risk notes:
- These definitions are ABI-sensitive; field sizes, packing, and ioctl numbers must remain stable.
- Pointer fields use `compat_uptr_t` and must always be converted before use.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iomap.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iomap.c

This file implements XFS integration with the Linux iomap infrastructure for reads, buffered writes, direct writes, DAX writes, atomic writes, xattrs, seek/data-hole mapping, zeroing, truncation, delayed allocation, CoW, realtime, and zoned allocation.

Core mapping helpers:
- `xfs_iomap_inode_sequence` builds validity cookies from data, attr, and CoW fork sequence counters.
- `xfs_iomap_valid` lets iomap detect stale mappings after extent-tree changes.
- `xfs_bmbt_to_iomap` converts XFS bmbt records to `struct iomap`, handling holes, delalloc, mapped, unwritten, DAX device offsets, integrity flags, dirty datasync state, realtime group boundaries, and validity cookies.
- `xfs_hole_to_iomap` builds hole mappings.
- `xfs_iomap_end_fsb` bounds byte ranges by maximum file size.

Allocation sizing:
- `xfs_eof_alignment` and `xfs_iomap_eof_align_last_fsb` align EOF allocations to stripe, swalloc, and extent-size hint boundaries.
- `xfs_iomap_prealloc_size` computes dynamic speculative preallocation from file extent history, filesystem low-space thresholds, realtime free space, and quota preallocation watermarks.
- `xfs_aligned_fsb_count` is exported by the header as a helper to round allocation lengths to extent-size hints.

Direct writes:
- `xfs_direct_write_iomap_begin` maps or allocates blocks for direct writes and zeroing.
- It handles NOWAIT, overwrite-only, DAX conversion, shared/reflink CoW allocation, hardware atomic write constraints, EOF dirty signaling, and bounded allocation chunks.
- `xfs_iomap_write_direct` performs transactional block allocation or DAX unwritten conversion and returns an updated sequence cookie.

Unwritten extent conversion:
- `xfs_iomap_write_unwritten` loops over a written byte range, converting unwritten extents to written extents transactionally and optionally updating inode size and disk size.

Atomic writes:
- Hardware atomic writes are checked with `xfs_bmap_hw_atomic_write_possible`.
- `xfs_atomic_write_cow_iomap_begin` implements software atomic writes through the CoW fork by allocating/converting CoW mappings and returning shared iomaps.

Buffered writes and delayed allocation:
- `xfs_bmap_add_extent_hole_delay` merges or inserts delalloc extent records into the in-core extent tree and adjusts indirect block reservations.
- `xfs_bmapi_reserve_delalloc` reserves quota, free blocks or realtime extents, indirect blocks, updates delayed block accounting, inserts delalloc extents, and tags EOF or CoW preallocation.
- `xfs_buffered_write_iomap_begin` handles normal buffered writes, reflink CoW writes, unshare, zeroing, dirty-folio lookup, speculative EOF preallocation, data-fork and CoW-fork delalloc, and conversion of post-EOF delalloc during zeroing.
- `xfs_buffered_write_iomap_end` releases newly allocated delalloc blocks after short or failed writes, using invalidate locking when needed.
- `xfs_zoned_buffered_write_iomap_begin` is the zoned realtime variant, using caller-provided zone allocation context and CoW fork delalloc reservations.

Other iomap operations:
- `xfs_zoned_direct_write_iomap_begin` returns anonymous direct-write mappings for zoned realtime writes after ensuring data extents are loaded.
- `xfs_dax_write_iomap_end` finishes or cancels CoW for DAX writes.
- `xfs_read_iomap_begin` maps reads and optionally trims around shared extents for reporting or DAX.
- `xfs_seek_iomap_begin` supports SEEK_DATA/SEEK_HOLE style mapping, including CoW fork dirty data as unwritten.
- `xfs_xattr_iomap_begin` maps remote attribute fork extents.
- `xfs_zero_range` and `xfs_truncate_page` dispatch zero/truncate operations to DAX or buffered iomap paths.

Registered ops:
- `xfs_iomap_write_ops`
- `xfs_direct_write_iomap_ops`
- `xfs_zoned_direct_write_iomap_ops`
- `xfs_atomic_write_cow_iomap_ops`
- `xfs_dax_write_iomap_ops`
- `xfs_buffered_write_iomap_ops`
- `xfs_read_iomap_ops`
- `xfs_seek_iomap_ops`
- `xfs_xattr_iomap_ops`

Risk notes:
- The file is concurrency-sensitive: it coordinates inode locks, extent sequence validation, NOWAIT behavior, page cache dirty state, direct I/O races, and CoW fork state.
- Delalloc accounting spans quota reservations, free block counters, realtime extents, inode delayed block counts, and global delalloc accounting.
- Zeroing over CoW and dirty page cache has explicit race handling; this is an area to inspect carefully for behavioral changes.
- Atomic write support has strict mapping, alignment, and single-extent requirements.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iomap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iomap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iomap.h

This header declares XFS iomap integration entry points and exported iomap operation tables.

Exports:
- Direct allocation and unwritten conversion:
  - `xfs_iomap_write_direct`
  - `xfs_iomap_write_unwritten`
- EOF allocation alignment:
  - `xfs_iomap_eof_align_last_fsb`
- Sequence and conversion:
  - `xfs_iomap_inode_sequence`
  - `xfs_bmbt_to_iomap`
- Zero/truncate helpers:
  - `xfs_zero_range`
  - `xfs_truncate_page`
- `xfs_aligned_fsb_count`, an inline helper that expands a block count to satisfy extent-size alignment.
- Iomap operation tables for buffered write, direct write, zoned direct write, read, seek, xattr, DAX write, atomic CoW write, and iomap write validation.

Role:
- Provides the shared interface between XFS file operations, inode operations, writeback/direct I/O paths, and the implementation in `xfs_iomap.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iomap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iops.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iops.c

This file implements VFS inode operations for XFS: create, lookup, link, unlink, symlink, rename, getattr, setattr, update_time, fiemap, tmpfile, DAX inode setup, and Linux inode initialization.

Creation and namespace operations:
- `xfs_generic_create` is the common path for regular file, directory, special file, and tmpfile creation.
  - Validates device numbers for special files.
  - Creates POSIX ACLs.
  - Predicts whether xattrs are needed for ACL/security setup.
  - Calls `xfs_create` or `xfs_create_tmpfile`.
  - Initializes security xattrs and ACLs after inode creation.
  - Sets inode operations and instantiates the dentry or tmpfile.
  - Cleans up the inode if post-create xattr/ACL setup fails.
- Wrappers implement `mknod`, `create`, `mkdir`, and `tmpfile`.
- `xfs_vn_lookup` performs normal lookup; `xfs_vn_ci_lookup` performs ASCII case-insensitive lookup and uses `d_add_ci` for casefolded names.
- `xfs_vn_link`, `xfs_vn_unlink`, `xfs_vn_symlink`, and `xfs_vn_rename` translate VFS dentries to `xfs_name` and call core XFS namespace operations.

Security/xattr setup:
- `xfs_initxattrs` writes initial security xattrs via `xfs_attr_change`.
- `xfs_inode_init_security` invokes LSM security initialization.
- `xfs_create_need_xattr` predicts whether inode allocation should initialize an attr fork.

Stat and attribute reporting:
- `xfs_vn_getattr` fills `kstat`, including size, ownership through idmapped mounts, birth time, block count, immutable/append/nodump flags, block size, DIO alignment, and atomic write limits.
- `xfs_report_dioalign` reports separate read/write DIO alignment for CoW files.
- `xfs_get_atomic_write_min`, `xfs_get_atomic_write_max`, and `xfs_get_atomic_write_max_opt` report hardware/software atomic write capabilities.

Setattr and truncation:
- `xfs_vn_change_ok` checks readonly, shutdown, and VFS permission constraints.
- `xfs_setattr_nonsize` handles mode, uid/gid, timestamps, quota transfer, inode logging, and ACL chmod updates.
- `xfs_vn_setattr_size` handles truncation and extension:
  - Requires IOLOCK/MMAPLOCK exclusivity.
  - Attaches dquots.
  - Waits for direct I/O.
  - Reserves zoned space when needed.
  - Zeroes exposed EOF ranges or partial truncate blocks.
  - Updates page cache size before transaction.
  - Writes dirty beyond-disk-size data to avoid stale/null file exposure.
  - Allocates truncate transaction, logs new disk size, truncates extents on shrink, clears EOF block tags, copies attrs, and commits.
- `xfs_vn_setattr` routes size vs non-size updates and breaks layouts for size changes.

Time and fiemap:
- `xfs_vn_update_time` handles lazytime and transactional timestamp logging.
- `xfs_vn_sync_lazytime` forces timestamp log update for lazytime inodes.
- `xfs_vn_fiemap` dispatches to xattr or read iomap ops.

Inode operation tables:
- `xfs_inode_operations` for regular/special inodes.
- `xfs_dir_inode_operations` for normal directories.
- `xfs_dir_ci_inode_operations` for ASCII case-insensitive directories.
- `xfs_symlink_inode_operations` for symlinks.

Inode setup:
- `xfs_inode_supports_dax` and `xfs_inode_should_enable_dax` decide DAX capability and policy.
- `xfs_diflags_to_iflags` maps XFS flags to VFS `i_flags`, setting `S_DAX` only during initialization.
- `xfs_setup_inode` initializes Linux inode state, fake hash, size, flags, metadata-private state, lockdep classes, GFP_NOFS mapping mask, realtime stable writes, and no-xattr/no-ACL hints.
- `xfs_setup_iops` installs inode/file/address-space operations based on inode mode and DAX state.

Risk notes:
- Truncate ordering is critical to avoid stale data exposure after crash.
- Creation cleanup must undo namespace entries if security/ACL initialization fails.
- DAX flag transitions are intentionally conservative because active access paths cannot safely change `S_DAX`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iops.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iops.h

This header declares XFS inode-operation helpers used outside `xfs_iops.c`.

Exports:
- `xfs_vn_listxattr`
- `xfs_vn_setattr_size`
- `xfs_inode_init_security`
- `xfs_setup_inode`
- `xfs_setup_iops`
- `xfs_diflags_to_iflags`
- Atomic write capability helpers:
  - `xfs_get_atomic_write_min`
  - `xfs_get_atomic_write_max`
  - `xfs_get_atomic_write_max_opt`

Role:
- Connects inode setup, VFS attribute handling, xattr listing, security initialization, and atomic write reporting to the rest of the XFS implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_itable.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_itable.c

This file implements XFS bulk inode reporting for userspace, using inode btree walking to produce bulkstat and inumbers records.

Bulkstat:
- `xfs_bulkstat_one_int` loads an inode with `xfs_iget`, fills `struct xfs_bulkstat`, and invokes a caller-provided formatter.
- It skips missing, invalid, private, and superblock-reserved inodes unless metadata-directory reporting is explicitly requested.
- It reloads incomplete unlinked-list state before allowing inodegc-sensitive paths to proceed.
- It maps uid/gid through the request idmap and superblock user namespace.
- It reports size, times, generation, mode, xflags, extent size, extent counts, health, attr extent counts, fork offset, v5 version, birth time, CoW extent size, rdev, block size, and block count.
- `xfs_bulkstat_one` reports one inode.
- `xfs_bulkstat` walks allocated inodes using `xfs_iwalk`.

Legacy conversion:
- `xfs_bulkstat_to_bstat` converts v5 `xfs_bulkstat` to legacy `xfs_bstat`, including byte conversion for extent size and CoW extent size.

Inumbers:
- `xfs_inumbers_walk` converts inode btree records into `struct xfs_inumbers`, including start inode, allocated count, allocation mask, and version.
- `xfs_inumbers` walks inode btree records using `xfs_inobt_walk`.
- `xfs_inumbers_to_inogrp` converts v5 inumbers to legacy `xfs_inogrp`.

Cursor behavior:
- `breq->startino` is used as the userspace cursor and advanced whenever the current inode or inode chunk can be skipped or reported.
- `-ECANCELED` is used internally to stop iteration when the userspace output buffer is full; callers translate it as success if records were produced.

Validation and limits:
- Bulkstat rejects idmapped mounts except `nop_mnt_idmap`.
- `xfs_bulkstat_already_done` returns early if the starting inode is beyond the filesystem or cannot map cleanly to AG/agino coordinates.
- Empty transactions are used for recursive buffer locking and cycle detection while walking inode btrees.

Integration:
- Called by native and compat ioctl paths.
- Depends on `xfs_iwalk.c` for iteration and `xfs_health` for inode health flags.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_itable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_itable.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_itable.h

This header defines the in-memory bulk inode request structure and declares bulkstat/inumbers APIs.

Contents:
- `struct xfs_ibulk`:
  - Mount pointer.
  - Mount idmap.
  - Userspace output buffer.
  - Start inode cursor.
  - Input count and output count.
  - Bulk flags.
  - Iwalk flags.
- Flags:
  - `XFS_IBULK_NREXT64` requests 64-bit extent count output.
  - `XFS_IBULK_METADIR` allows metadata directory records.
- `xfs_ibulk_advance` advances the userspace buffer pointer, increments output count, and returns `-ECANCELED` when the requested count is filled.
- Formatter callback typedefs for bulkstat and inumbers.
- Function declarations for:
  - `xfs_bulkstat_one`
  - `xfs_bulkstat`
  - `xfs_bulkstat_to_bstat`
  - `xfs_inumbers`
  - `xfs_inumbers_to_inogrp`

Role:
- Provides the shared request/formatter abstraction used by native ioctl, compat ioctl, and itable implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_itable.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iunlink_item.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iunlink_item.c

This file implements the transaction log item used to update an inode’s ondisk `di_next_unlinked` pointer for XFS unlinked inode lists.

Core structures and operations:
- Global `xfs_iunlink_cache` stores `struct xfs_iunlink_item` objects.
- `IUL_ITEM` converts a generic log item to `xfs_iunlink_item`.
- `xfs_iunlink_item_release` drops the per-AG reference and frees the item.
- `xfs_iunlink_item_sort` sorts log items by inode number.
- `xfs_iunlink_log_dinode` maps the inode cluster buffer, validates that the ondisk old pointer matches `old_agino`, updates `di_next_unlinked`, recalculates the dinode CRC, marks the inode buffer in the transaction, and logs exactly the changed field range.
- `xfs_iunlink_item_precommit` performs the buffer update just before commit, removes the log item from the transaction, and releases it.
- `xfs_iunlink_item_ops` wires release, sort, and precommit hooks.

Public entry:
- `xfs_iunlink_log_inode` allocates and initializes an iunlink log item, captures the inode, per-AG reference, new agino, and old agino, adds it to the transaction, marks the transaction dirty, and marks the item dirty.
- It validates `next_agino` and current `i_next_unlinked`, rejects non-null no-op pointer updates as corruption, and treats null-to-null as a no-op.

Design reason:
- The precommit hook ensures inode cluster buffers are logged in correct order relative to other inode cluster buffers while updating unlinked-list pointers.

Risk notes:
- The old pointer check protects against stale or corrupted unlinked list state.
- The code avoids logging stale inode buffers because doing so could incorrectly clear stale state during inode cluster freeing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iunlink_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iunlink_item.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iunlink_item.h

This header declares the in-memory log item for unlinked inode pointer updates.

Contents:
- Forward declarations for `xfs_trans`, `xfs_inode`, and `xfs_perag`.
- `struct xfs_iunlink_item`, containing:
  - Embedded `xfs_log_item`.
  - Target inode.
  - Held per-AG pointer.
  - New next unlinked agino.
  - Old agino expected on disk.
- Global cache declaration `xfs_iunlink_cache`.
- Public function `xfs_iunlink_log_inode`.

Role:
- Provides the transaction-facing API for scheduling ondisk unlinked-list pointer updates at transaction precommit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iunlink_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iwalk.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iwalk.c

This file implements generic inode and inode-btree walking for XFS. It supports single-threaded inode iteration, threaded per-AG inode iteration, and raw inobt record iteration.

Core model:
- `struct xfs_iwalk_ag` tracks one AG walk: mount, transaction, perag, start inode, last inode, cached inobt records, callbacks, caller data, and behavior flags.
- The walker reads inode btree records into an in-memory cache, drops btree cursor/AGI state before invoking callbacks, then reconstructs cursor state afterward. This allows callbacks to perform arbitrary work without holding inobt cursor or AGI locks.

Key helpers:
- `xfs_iwalk_ichunk_ra` performs inode-cluster readahead for allocated inodes in an inobt record.
- `xfs_iwalk_adjust_start` marks inodes before the requested start agino as free to support restarting inside a chunk.
- `xfs_iwalk_alloc` / `xfs_iwalk_free` manage cached record arrays.
- `xfs_iwalk_ag_recs` invokes inobt-record callbacks and inode callbacks for allocated inodes.
- `xfs_iwalk_del_inobt` tears down btree cursor and releases AGI buffer.
- `xfs_iwalk_ag_start` positions the cursor at the start point and handles mid-record start trimming.
- `xfs_iwalk_run_callbacks` drops cursor/AGI, optionally drops the empty transaction, runs callbacks, clears cache, recreates cursor, and resumes from the next agino.
- `xfs_iwalk_ag` walks all relevant records in one AG, ensures monotonic progress, skips empty records when configured, triggers readahead, and runs cached callbacks.

Public inode walk:
- `xfs_iwalk` walks allocated inodes from `startino` with optional `XFS_IWALK_SAME_AG`.
- It uses an empty transaction supplied by the caller, trims the start record, skips empty records, and prefetches based on requested inode count.

Threaded inode walk:
- `xfs_iwalk_threaded` queues one work item per AG using `xfs_pwork`.
- `xfs_iwalk_ag_work` allocates per-work state, creates an empty transaction, walks its AG, cancels the transaction, frees resources, and drops the perag reference.
- Optional polling is supported.

Inobt record walk:
- `xfs_inobt_walk` walks inode btree records instead of individual inodes.
- It uses `xfs_inobt_walk_prefetch`, capped to a page of records and with a minimum of two records.

Flags:
- `XFS_IWALK_SAME_AG` limits walking to the AG containing `startino`.

Risk notes:
- Correctness depends on preserving cursor progress across callback execution while avoiding stale lock state.
- The monotonic `lastino` check marks the btree sick and returns corruption if records go backwards.
- Callback return `-ECANCELED` is intentionally supported as a non-error stop signal for users such as bulkstat.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iwalk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iwalk.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_iwalk.h

This header declares XFS inode and inode-btree walk APIs.

Exports:
- `xfs_iwalk_fn`, callback for allocated inode numbers.
- `xfs_iwalk`, single-threaded allocated-inode walk.
- `xfs_iwalk_threaded`, per-AG threaded allocated-inode walk.
- `XFS_IWALK_SAME_AG` and `XFS_IWALK_FLAGS_ALL`.
- `xfs_inobt_walk_fn`, callback for raw inode btree records.
- `xfs_inobt_walk`, single-threaded inode btree record walk.

Semantics:
- Walk callbacks return `0` to continue or nonzero to stop.
- `-ECANCELED` is a special stop value used by callers that need to end iteration without treating it as a native walker error.
- `XFS_IWALK_SAME_AG` constrains iteration to the allocation group containing the starting inode.

Role:
- Provides the common iterator interface used by bulkstat/inumbers and other inode-scanning code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_iwalk.h -->