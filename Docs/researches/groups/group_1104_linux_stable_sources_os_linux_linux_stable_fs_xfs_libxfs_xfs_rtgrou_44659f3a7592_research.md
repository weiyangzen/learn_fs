# Group Research: group_1104_linux_stable_sources_os_linux_linux_stable_fs_xfs_libxfs_xfs_rtgrou_44659f3a7592

Scope verified against `Docs/research_subset_a.md`: `sources/os/linux/linux-stable` is included. All 22 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtgroup.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtgroup.c

## Purpose

Implements in-core XFS realtime group management: rtgroup geometry, allocation/freeing of `struct xfs_rtgroup`, metadata inode loading/creation, rtgroup metadata locking, realtime superblock verification, and realtime superblock logging.

## Main Responsibilities

- Computes realtime group extent/block geometry with `__xfs_rtgroup_extents`, `xfs_rtgroup_extents`, `xfs_rtgroup_calc_geometry`, and `xfs_update_last_rtgroup_size`.
- Allocates, inserts, removes, and unwinds in-core rtgroups through generic `xfs_group_*` infrastructure.
- Locks bitmap/summary, rmap, and refcount metadata inodes according to `XFS_RTGLOCK_*` flags.
- Joins locked rtgroup metadata inodes to transactions.
- Defines `xfs_rtginode_ops`, mapping each rtgroup metadata inode type to path name, metafile type, sickness flag, valid fork formats, feature predicate, and creation callback.
- Loads classic global realtime bitmap/summary inodes for non-rtgroup filesystems, or per-rtgroup metadata inodes from the metadir for rtgroup filesystems.
- Creates the `rtgroups` metadir parent and individual rtgroup metadata files.
- Verifies and updates realtime superblock buffers via `xfs_rtsb_buf_ops`, `xfs_update_rtsb`, and `xfs_log_rtsb`.

## Important Details

- Rtgroup 0 reserves its first realtime extent for the realtime superblock when `xfs_has_rtsb(mp)`.
- Zoned realtime filesystems skip bitmap/summary locking because free-space accounting does not use those inodes.
- `xfs_rtginode_load` validates metadata inode fork format and requires `i_projid == rtg_rgno(rtg)`.
- The rmap and refcount rtginode feature predicates use broader growfs-compatible checks, because growfs can create those inodes before the realtime volume exists.
- Lockdep setup orders rtgroup metadata inode locks by rtgroup number and inode type.
- The realtime superblock verifier checks magic, padding, zeroed trailing bytes, label, filesystem UUID, metadata UUID, and CRC on reads.

## Dependencies

Uses `xfs_group`, metadir/metafile helpers, realtime bitmap creation, rtrmap/refcount btree creation, health marking, transaction inode joins, and buffer verifier infrastructure.

## Research Notes

This is the coordinator for the new rtgroups model. Callers should use the rtgroup lock/join helpers instead of directly locking metadata inodes, because this file encodes zoned behavior, optional rmap/refcount metadata, and transaction ownership rules.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtgroup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtgroup.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtgroup.h

## Purpose

Defines the in-core realtime group structure and public rtgroup API: metadata inode slots, reference helpers, iteration helpers, address conversion helpers, locking flags, and optional stubs when realtime support is disabled.

## Main Contents

- `enum xfs_rtg_inodes` for bitmap, summary, rmap, and refcount metadata inodes.
- `struct xfs_rtgroup`, embedding `struct xfs_group`, per-rtgroup metadata inodes, `rtg_extents`, summary-cache/open-zone union, and zoned GC counter.
- `XFS_RTG_FREE` xarray mark for free zoned rtgroups.
- Inline accessors for mount, group number, block count, and metadata inodes.
- Passive references: `xfs_rtgroup_get`, `xfs_rtgroup_hold`, `xfs_rtgroup_put`.
- Active references: `xfs_rtgroup_grab`, `xfs_rtgroup_rele`.
- Iteration helpers over rtgroup ranges.
- Conversion helpers among realtime block numbers, rtgroup numbers, rtgroup block numbers, realtime extents, disk addresses, and raw device group sizes.
- Runtime declarations for rtgroup lifecycle, geometry, metadata inode management, locks, realtime superblock updates, and geometry reporting.

## Important Invariants

- `xfs_verify_rgbno` and `xfs_verify_rgbext` assert rtgroups are enabled.
- `xfs_rtx_to_rgbno` uses a shift when realtime extent size is a power of two.
- `xfs_rtb_to_daddr` and `xfs_daddr_to_rtb` account for rtgroup layouts with or without disk-address gaps.
- `xfs_rtgroup_raw_size` includes zone-gap padding when the on-disk rtgroup layout has address gaps.
- `XFS_RTGLOCK_BITMAP` and `XFS_RTGLOCK_BITMAP_SHARED` are mutually exclusive.

## Research Notes

This header is the main rtgroup API surface. It also exposes the point where bitmap-backed realtime and zoned realtime diverge: the same union stores either the summary cache or the open-zone state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtgroup.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrefcount_btree.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrefcount_btree.c

## Purpose

Implements the inode-rooted realtime refcount btree, which tracks shared reference counts for realtime extents in an rtgroup metadata inode.

## Main Responsibilities

- Defines `xfs_rtrefcountbt_ops` for an inode-rooted refcount btree.
- Implements cursor duplication, cursor creation, min/max record calculations, key/record/pointer initialization, key comparison, ordering, and contiguity tests.
- Verifies realtime refcount btree buffers with CRC long-format btree headers.
- Manages btree root resizing in inode forks, including moving pointer arrays when root sizes change.
- Computes maximum records, maximum levels, and reservation sizes.
- Converts between compact on-disk dinode-root format and normal in-memory btree block format.
- Creates empty realtime refcount btree metadata inodes.
- Commits staged btree roots by replacing the real inode fork and logging the inode.

## Important Invariants

- The btree requires reflink support; format loading rejects filesystems without reflink.
- The metadata inode data fork format is `XFS_DINODE_FMT_META_BTREE`.
- Root blocks stored in the inode are compact on disk but expanded in memory into normal btree block layout.
- Refcount keys are ordered by encoded startblock, including refcount domain.
- Maximum height is constrained by both data-device block availability and the number of realtime extents in a group.
- The verifier rejects blocks when reflink is absent, magic is wrong, v5 btree header is invalid, or level exceeds `m_rtrefc_maxlevels`.

## Dependencies

Uses generic btree cursor, inode-root btree staging, refcount record encoding, metafile block allocation/freeing, rtgroup ownership, and transaction inode logging.

## Research Notes

This is the realtime counterpart to the data-device refcount btree, adapted for rtgroup metadata inodes. The root conversion functions are especially sensitive because the on-disk dinode root does not match the in-core btree block layout.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrefcount_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrefcount_btree.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrefcount_btree.h

## Purpose

Declares the realtime refcount btree API and defines layout helpers for incore btree blocks and compact on-disk dinode-root blocks.

## Main API

- Cursor and staging:
  - `xfs_rtrefcountbt_init_cursor`
  - `xfs_rtrefcountbt_stage_cursor`
  - `xfs_rtrefcountbt_commit_staged_btree`
- Geometry:
  - `xfs_rtrefcountbt_maxrecs`
  - `xfs_rtrefcountbt_compute_maxlevels`
  - `xfs_rtrefcountbt_droot_maxrecs`
  - `xfs_rtrefcountbt_maxlevels_ondisk`
- Cursor cache lifecycle:
  - `xfs_rtrefcountbt_init_cur_cache`
  - `xfs_rtrefcountbt_destroy_cur_cache`
- Reservation sizing:
  - `xfs_rtrefcountbt_calc_reserves`
  - `xfs_rtrefcountbt_calc_size`
- Inode formatting:
  - `xfs_iformat_rtrefcount`
  - `xfs_rtrefcountbt_to_disk`
  - `xfs_iflush_rtrefcount`
  - `xfs_rtrefcountbt_create`

## Layout Helpers

Provides address helpers for:
- incore records, keys, and pointers
- on-disk dinode-root records, keys, and pointers
- incore root pointer placement based on actual root size
- incore and on-disk root space calculations

## Important Invariants

- `XFS_RTREFCOUNT_BLOCK_LEN` uses the CRC long btree block header length.
- Leaf roots store refcount records.
- Internal roots store key-pointer pairs.
- On-disk root space is based on `struct xfs_rtrefcount_root`; incore root space is based on `XFS_RTREFCOUNT_BLOCK_LEN`.

## Research Notes

This header is layout-sensitive and shared with userspace-oriented libxfs code. Consumers should use the helpers instead of open-coding offsets.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrefcount_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrmap_btree.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrmap_btree.c

## Purpose

Implements the inode-rooted realtime reverse mapping btree, mapping realtime physical extents back to owners for each rtgroup.

## Main Responsibilities

- Defines `xfs_rtrmapbt_ops`, an overlapping inode-rooted btree.
- Implements cursor duplication/creation, min/max record calculations, key/high-key creation, record packing, comparisons, ordering, and physical-key contiguity tests.
- Masks unwritten state out of key comparisons because written/unwritten is a record attribute, not a key component.
- Verifies realtime rmap btree buffers and defines `xfs_rtrmapbt_buf_ops`.
- Optionally defines in-memory realtime rmap btree support under `CONFIG_XFS_BTREE_IN_MEM`.
- Resizes inode-root btree forks and moves pointer arrays when root sizes change.
- Computes maximum records, maximum levels, btree size, and reservation sizes.
- Converts between compact on-disk dinode-root format and normal in-memory btree block format.
- Creates empty realtime rmap btree metadata inodes.
- Initializes the rmap record for the realtime superblock.
- Finds the highest rtgroup block covered by the rmap tree.

## Important Invariants

- The on-disk realtime rmap btree requires rmapbt support.
- It is an overlapping btree, so internal entries store low and high keys per pointer.
- Inode-root format is `XFS_DINODE_FMT_META_BTREE`.
- Reflink-capable realtime rmap trees can theoretically contain extreme numbers of owner records, so max-level computation falls back to data-device space constraints.
- In-memory rtrmap btrees can be generated even if the on-disk feature is not enabled.

## Dependencies

Uses generic btree, btree staging, memory btree support, rmap record/key packing, rtgroup ownership, metadata inode block allocation/freeing, and transaction logging.

## Research Notes

This file is the realtime version of the data-device rmap btree, but the inode-root and overlapping-key layout make it more specialized. The comparison logic deliberately excludes unwritten status from key identity.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrmap_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrmap_btree.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrmap_btree.h

## Purpose

Declares the realtime rmap btree API and provides address/space helpers for incore and on-disk rtrmap inode-root layouts.

## Main API

- Cursor and staging:
  - `xfs_rtrmapbt_init_cursor`
  - `xfs_rtrmapbt_stage_cursor`
  - `xfs_rtrmapbt_commit_staged_btree`
- Geometry:
  - `xfs_rtrmapbt_maxrecs`
  - `xfs_rtrmapbt_compute_maxlevels`
  - `xfs_rtrmapbt_droot_maxrecs`
  - `xfs_rtrmapbt_maxlevels_ondisk`
- Cursor cache lifecycle:
  - `xfs_rtrmapbt_init_cur_cache`
  - `xfs_rtrmapbt_destroy_cur_cache`
- Reservation and sizing:
  - `xfs_rtrmapbt_calc_reserves`
  - `xfs_rtrmapbt_calc_size`
- Format conversion:
  - `xfs_iformat_rtrmap`
  - `xfs_rtrmapbt_to_disk`
  - `xfs_iflush_rtrmap`
- Creation and special setup:
  - `xfs_rtrmapbt_create`
  - `xfs_rtrmapbt_init_rtsb`
  - `xfs_rtrmap_highest_rgbno`
- In-memory support:
  - `xfs_rtrmapbt_mem_cursor`
  - `xfs_rtrmapbt_mem_init`

## Layout Helpers

Provides helpers for:
- incore records, low keys, high keys, and pointers
- on-disk root records, keys, and pointers
- root pointer placement based on actual root size
- incore and on-disk root space calculations

## Important Invariants

- `XFS_RTRMAP_BLOCK_LEN` uses the CRC long btree block header length.
- Internal roots store two `struct xfs_rmap_key` values plus one pointer per record.
- Leaf roots store `struct xfs_rmap_rec`.
- On-disk and incore roots have different headers and must use the provided size helpers.

## Research Notes

Because this is an overlapping btree, internal-node layout is not interchangeable with simple key-pointer btrees. The header keeps those offset calculations centralized.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtrmap_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_sb.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_sb.c

## Purpose

Implements XFS superblock validation, disk/incore conversion, buffer verifiers, mount-derived geometry initialization, logging/syncing, secondary superblock handling, filesystem geometry reporting, and stripe/realtime geometry validation.

## Main Responsibilities

- Validates supported v4/v5 superblock versions and feature masks.
- Converts superblock version/feature bits into in-core feature flags.
- Validates realtime geometry, including metadir rtgroups and zoned realtime constraints.
- Validates stripe geometry and core allocation-group geometry.
- Converts between `struct xfs_dsb` and `struct xfs_sb`.
- Normalizes quota inode fields for old formats and metadir formats.
- Defines noisy and quiet superblock buffer ops.
- Initializes cached mount geometry for AGs, rtgroups, btrees, realtime bitmap block sizes, and allocation set-aside values.
- Logs and syncs the primary superblock, optionally updating the realtime superblock.
- Updates and reads secondary superblocks.
- Reports geometry through `xfs_fs_geometry`.
- Computes `rextslog` and `rgblklog`.

## Rtgroup and Zoned Integration

Metadir superblocks are validated for:
- nonzero realtime extent size
- realtime group size lower and upper bounds
- group count covering all realtime extents
- exchange-range feature requirement
- stored `sb_rgblklog` matching computed value

Zoned superblocks are validated for:
- `sb_frextents == 0`
- `sb_rtstart` not overlapping data blocks
- `sb_rtreserved < sb_rblocks`
- realtime extents aligned to full rtgroup size

## Important Invariants

- V5 filesystems must carry required legacy v4 feature flags because other code tests those flags directly.
- Unknown read-only-compatible features block read-write mounts.
- Unknown incompatible features block mounting.
- Primary superblock summary counters are checked on write.
- Metadir filesystems store quota metadata differently and write classic quota inode fields as zero.
- Metadir filesystems zero classic realtime bitmap and summary inode fields on disk and set them to `NULLFSINO` in-core.
- Realtime bitmap block sizing changes for metadir and zoned filesystems.
- `xfs_sync_sb_buf` can log and synchronously write both the primary superblock and realtime superblock.

## Dependencies

Calls allocation, inode, rmap, refcount, realtime bitmap, realtime rmap, realtime refcount, dir geometry, health, log, and rtgroup helpers.

## Research Notes

This file is the main format gatekeeper. Any rtgroup, metadir, rtrmapbt, rtrefcountbt, zoned, or exchange-range behavior must match the validation and mount-geometry setup here or the filesystem can be rejected or mis-sized.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_sb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_sb.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_sb.h

## Purpose

Declares the superblock manipulation, validation, mount-geometry, sync, secondary-superblock, and filesystem geometry APIs.

## Main API

- Logging and syncing:
  - `xfs_log_sb`
  - `xfs_sync_sb`
  - `xfs_sync_sb_buf`
- Mount setup:
  - `xfs_sb_mount_common`
  - `xfs_sb_mount_rextsize`
  - `xfs_mount_sb_set_rextsize`
- Disk conversion:
  - `xfs_sb_from_disk`
  - `xfs_sb_to_disk`
  - `xfs_sb_quota_from_disk`
- Validation and feature interpretation:
  - `xfs_sb_good_version`
  - `xfs_sb_version_to_features`
  - `xfs_validate_stripe_geometry`
  - `xfs_validate_rt_geometry`
- Geometry reporting:
  - `xfs_fs_geometry`
- Secondary superblocks:
  - `xfs_update_secondary_sbs`
  - `xfs_sb_read_secondary`
  - `xfs_sb_get_secondary`
- Realtime calculations:
  - `xfs_compute_rextslog`
  - `xfs_compute_rgblklog`

## Important Invariants

- `XFS_FS_GEOM_MAX_STRUCT_VER` is 5, matching the newest geometry fields reported by `xfs_fs_geometry`.
- Realtime group block-log computation is part of the public libxfs superblock API.

## Research Notes

Small but central header exposing the validation and mount-geometry services used across libxfs and kernel XFS code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_shared.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_shared.h

## Purpose

Collects shared declarations and definitions used by kernel XFS and userspace libxfs when they do not belong in a narrower shared header.

## Main Contents

- Extern declarations for buffer verifier ops across AG headers, attr blocks, bmbt, dquot, inode buffers, refcount/rmap btrees, realtime bitmap/summary buffers, realtime superblock, realtime rmap/refcount btrees, superblock, and symlink buffers.
- Extern declarations for btree operation tables.
- Inline classifiers for btree op tables, including data-device and realtime rmap/refcount btrees and optional in-memory variants.
- Transaction flag definitions.
- Superblock modification field masks for `xfs_trans_mod_sb`.
- Metadata buffer cache reference priority constants.
- `struct xfs_ino_geometry`, holding computed inode allocation and formatting geometry.

## Important Invariants

- `XFS_TRANS_RTBITMAP_LOCKED` records that a transaction has locked realtime bitmap/summary inodes.
- `XFS_TRANS_SB_RGCOUNT` is the superblock modification mask for realtime group count changes.
- In-memory btree classifiers depend on `CONFIG_XFS_BTREE_IN_MEM`.
- Buffer reference constants are shared policy for metadata buffer cache retention.

## Research Notes

This is libxfs glue. New metadata verifiers and btree op tables, including realtime rmap/refcount, must be declared here so generic code can identify and dispatch them.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_shared.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_symlink_remote.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_symlink_remote.c

## Purpose

Implements encoding, verification, reading, writing, conversion, and truncation of remote symlink target blocks.

## Main Responsibilities

- Calculates remote symlink block count with per-block header overhead.
- Creates CRC-format remote symlink headers with magic, offset, byte count, metadata UUID, owner inode, and block address.
- Verifies symlink buffers, including CRC, magic, metadata UUID, block address, bounds, owner, and LSN.
- Converts local inline symlink data to a remote block during fork conversion.
- Verifies in-memory shortform symlink targets.
- Reads remote symlink blocks into a null-terminated target string.
- Writes either inline symlink targets or remote symlink blocks depending on path length.
- Invalidates and unmaps remote symlink blocks during truncate.

## Important Invariants

- Non-CRC filesystems do not use remote symlink headers or buffer verification.
- CRC symlink reads validate that header owner, offset, and byte count match the expected inode and chunk position.
- Shortform symlinks cannot be zero length, negative length, too long, contain embedded NUL bytes before the terminator, or lack a final NUL terminator in memory.
- Remote symlink block buffers are logged as `XFS_BLFT_SYMLINK_BUF`.
- Remote truncate first invalidates mapped buffers, then unmaps the blocks and requires that unmap made progress.

## Dependencies

Uses bmap read/write/unmap helpers, transaction buffer logging, inode logging, symlink buffer ops, metadata health marking, and CRC verifier helpers.

## Research Notes

Remote symlink correctness depends on matching the logical chunk metadata in each block header to the inode and offset being read. Header checks are split between generic verifier checks and `xfs_symlink_hdr_ok`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_symlink_remote.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_symlink_remote.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_symlink_remote.h

## Purpose

Declares helper functions for symlink block encoding, verification, reading, writing, conversion from inline to remote form, and remote truncation.

## Main API

- `xfs_symlink_blocks`
- `xfs_symlink_hdr_set`
- `xfs_symlink_hdr_ok`
- `xfs_symlink_local_to_remote`
- `xfs_symlink_shortform_verify`
- `xfs_symlink_remote_read`
- `xfs_symlink_write_target`
- `xfs_symlink_remote_truncate`

## Important Invariants

- Callers use this API for both inline/shortform validation and remote block handling.
- Remote write requires owner inode, target path, path length, fsblock count, and reservation block count.

## Research Notes

This is a compact public interface for the remote symlink implementation in `xfs_symlink_remote.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_symlink_remote.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_inode.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_inode.c

## Purpose

Provides inode transaction helpers for joining inodes to transactions, updating timestamps, logging inode dirty regions, and rolling transactions while keeping an inode joined.

## Main Responsibilities

- `xfs_trans_ijoin` initializes an inode log item if needed, records lock flags, resets per-transaction dirty flags, and adds the inode item to the transaction.
- `xfs_trans_ichgtime` updates ctime and optionally mtime, atime, and creation time for a transaction-joined inode.
- `xfs_trans_log_inode` marks the transaction dirty, marks the inode log item dirty, optionally bumps inode version, and ORs dirty flags into `ili_dirty_flags`.
- `xfs_trans_roll_inode` logs core inode changes, rolls the transaction, and rejoins the inode.

## Important Invariants

- Inodes must be exclusively ILOCKed for these operations.
- `xfs_trans_ijoin` expects the inode not to be stale and not already associated with dirty lock flags.
- `xfs_trans_ichgtime` requires ctime change when any timestamp change is requested.
- Inode log item precommit handles the actual log formatting after dirty flags are recorded.

## Research Notes

This file is the small transaction-facing inode state bridge. It records what changed and relies on the transaction/log item machinery for commit-time handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_resv.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_resv.c

## Purpose

Calculates transaction log reservations for XFS operations, including data and realtime extent allocation/freeing, refcount/rmap deferred updates, namespace operations, quota operations, growfs operations, attribute operations, and atomic write completion.

## Main Responsibilities

- Computes generic buffer and inode log reservation overhead.
- Computes allocation/free btree block counts, including rmapbt when enabled.
- Computes refcount and realtime refcount btree block counts.
- Computes realtime allocation metadata reservation needs, including bitmap/summary and realtime rmap deferred updates.
- Provides exported finish-reservation helpers for BUI, EFI, realtime EFI, RUI, realtime RUI, CUI, and realtime CUI completion.
- Calculates write, truncate, rename, link, remove, create, mkdir, symlink, tmpfile, inode free, inode change, growdata, growrt, addafork, attr, quota, superblock, and clear-AGI reservations.
- Adjusts namespace transaction reservations for parent pointer updates.
- Initializes `struct xfs_trans_resv` in `xfs_trans_resv_calc`.
- Computes default and custom atomic write ioend reservations and minimum log geometry.

## Realtime and Reflink Details

- `xfs_rtalloc_block_count` accounts for realtime bitmap/summary updates and separately considers realtime rmap btree splits.
- `xfs_calc_finish_rt_cui_reservation` covers realtime refcount inode logging plus rtrefcount btree updates.
- `xfs_calc_refcountbt_reservation` takes the max of data-device and realtime refcount update costs.
- Runtime write/truncate reservations account for deferred refcount work separately from the main allocation/free transaction.
- Minimum-log-size compatibility calculations preserve older reflink reservation assumptions.

## Important Invariants

- Reservations include log operation headers and historical 128-byte buffer overhead rounding.
- Runtime reservations differ from minimum-log-size estimates for older reflink behavior.
- Parent pointers add both attribute reservation costs and xattr intent overhead to namespace operations.
- Atomic write reservation sizing models chained BUI/RUI/CUI/EFI completion and relogging overhead.
- `xfs_trans_resv_calc` must calculate attribute reservations before namespace reservations because parent pointer namespace costs depend on attr reservations.

## Dependencies

Uses mount geometry, inode geometry, bmap/rmap/refcount levels, realtime bitmap helpers, transaction space macros, deferred item log-space helpers, quota constants, and tracepoints.

## Research Notes

This file is the reservation policy engine. It is tightly coupled to btree heights and feature flags, so changes to rtgroups, rtrmapbt, rtrefcountbt, reflink, rmapbt, parent pointers, or atomic writes must be reflected here.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_resv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_resv.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_resv.h

## Purpose

Defines transaction reservation structures, reservation slots, standard log count constants, directory-operation reservation macros, and exported reservation calculation helpers.

## Main Contents

- `struct xfs_trans_res` with log reservation bytes, log operation count, and log flags.
- `struct xfs_trans_resv`, containing precomputed reservations for writes, truncates, namespace operations, inode operations, growfs, attributes, quotas, superblock updates, fsync timestamp updates, and atomic write completion.
- `M_RES(mp)` shorthand.
- Directory operation log reservation and count macros.
- Standard log count constants.
- Historical reflink log count constants retained for minimum log size calculations.
- Exported APIs for reservation initialization, allocation/free block counts, deferred-item finish reservations, minimum-log-size reservations, and atomic write reservation sizing.

## Important Invariants

- Permanent log reservations are represented through `tr_logflags`.
- The reflink historical log count constants are not runtime reservations.
- Atomic write helpers expose both maximum supported block count and recalculation for requested block counts.

## Research Notes

This header defines the reservation ABI used throughout XFS transaction setup. The implementation in `xfs_trans_resv.c` fills these slots based on feature-specific geometry.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_resv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_space.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_space.c

## Purpose

Calculates filesystem block space reservations for namespace operations, especially with optional parent pointer attributes.

## Main Responsibilities

- `xfs_parent_calc_space_res` estimates blocks needed to add a parent pointer attribute.
- `xfs_create_space_res` adds inode allocation, directory entry insertion, and optional parent pointer space.
- `xfs_mkdir_space_res` aliases create reservation behavior.
- `xfs_link_space_res` covers directory entry insertion and optional parent pointer space.
- `xfs_symlink_space_res` covers inode allocation, directory entry insertion, remote symlink blocks, and optional parent pointer space.
- `xfs_remove_space_res` covers directory removal and optional parent pointer removal space.
- `xfs_rename_space_res` covers source removal, target insertion, optional whiteout parent pointer, source/destination parent pointer replacement, and target-exists cleanup.

## Important Invariants

- Parent pointers are assumed to be first attrs in an attr tree and no larger than a block.
- Rename parent-pointer reservation accounts for multiple parent pointer operations depending on whiteout and target existence.

## Dependencies

Uses transaction-space macros from `xfs_trans_space.h`, directory/attribute geometry, bmap geometry, and parent feature checks.

## Research Notes

This file provides block-space reservations, not log reservations. It complements `xfs_trans_resv.c`, which calculates log-space reservations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_space.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_space.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_space.h

## Purpose

Defines transaction block-space reservation macros and declares namespace space reservation helper functions.

## Main Contents

- Worst-case contiguous record capacities for bmap, rmap, realtime rmap, and allocation btrees.
- Space reservation macros for adding rmaps, realtime rmaps, extents, swapped mappings, directory/attribute tree changes, inode allocation, growfs, quota allocation, attribute operations, and inode free.
- Constants preserving old reflink rmap maxlevel reservation behavior.
- Function declarations for parent, create, mkdir, link, symlink, remove, and rename space reservation calculations.

## Important Invariants

- `XFS_RTRMAPADD_SPACE_RES` is based on realtime rmap maxlevels.
- `XFS_NRTRMAPADD_SPACE_RES` scales realtime rmap additions by leaf capacity and maxlevels.
- Directory entry reservation accounts for both directory blocks and bmap blocks.
- `XFS_IALLOC_SPACE_RES` includes finobt cost when the feature is enabled.

## Research Notes

This header is the static block-reservation side of transaction sizing. It is sensitive to btree fanout and feature-dependent btree heights.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_space.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_types.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_types.c

## Purpose

Implements type-specific verifier helpers for filesystem blocks, realtime blocks, inode numbers, inode counts, directory/attribute offsets, and file offsets.

## Main Responsibilities

- Verifies AG block numbers against AG size and static AG metadata.
- Verifies filesystem block numbers and extents against AG boundaries and static metadata.
- Verifies AG inode numbers and full filesystem inode numbers.
- Identifies internal superblock inode numbers.
- Rejects directory entry inode numbers that point to internal metadata or invalid inodes.
- Verifies realtime block numbers and extents.
- Computes valid inode count range from per-AG inode ranges.
- Verifies inode count summary values.
- Verifies directory/attribute block offsets and file offsets/extents.

## Rtgroup Details

- With rtgroups enabled, realtime block verification converts the block to rtgroup number and realtime extent number.
- It rejects rtgroup numbers beyond `sb_rgcount`.
- It rejects realtime extents beyond that rtgroup's extent count.
- If a realtime superblock exists, rtgroup 0 extent 0 is not allocatable.
- Realtime extents cannot cross rtgroup boundaries.

## Important Invariants

- Data-device extents cannot wrap and cannot cross AG boundaries.
- Realtime extents cannot wrap and cannot cross rtgroup boundaries when rtgroups are enabled.
- Directory inode verification excludes internal metadata inodes.
- Inode count verification uses live per-AG ranges instead of only superblock limits.

## Research Notes

These verifiers are low-level corruption guards used by metadata validation paths. Rtgroup-aware realtime validation is an important extension over classic `rtbno < sb_rblocks` checking.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_types.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_types.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_types.h

## Purpose

Defines core XFS scalar types, null constants, block/sector size limits, fork identifiers, name structures, bmap/rmap/refcount record types, reservation enums, group/free-counter enums, and verifier prototypes.

## Main Contents

- Typedefs for AG blocks, rtgroup blocks, AG inodes, extent lengths, AG numbers, rtgroup numbers, filesystem blocks, realtime blocks, file offsets, file block counts, realtime extents, and failure addresses.
- Null values for filesystem, realtime, AG, rtgroup, inode, and LSN types.
- Minimum and maximum filesystem block and sector sizes.
- Fork identifiers for data, attr, cow, and staging forks.
- `struct xfs_name`.
- `struct xfs_bmbt_irec`, `struct xfs_refcount_irec`, and `struct xfs_rmap_irec`.
- Refcount domains and rmap flags.
- Per-AG reservation type enum.
- Btree record-packing enum.
- `enum xfs_group_type` for AG and RTG groups.
- `enum xfs_free_counter`, including data blocks, free realtime extents, and zoned realtime available extents.
- Prototypes for verifier helpers implemented in `xfs_types.c`.

## Important Invariants

- `xfs_rgblock_t` and `xfs_rgnumber_t` are first-class realtime group address types.
- `XC_FREE_RTAVAILABLE` exists only for zoned realtime accounting semantics.
- Rmap key flags exclude unwritten status; unwritten is a record flag.
- `XG_TYPE_AG` and `XG_TYPE_RTG` share generic group infrastructure.

## Research Notes

This header is foundational. The rtgroup and zoned additions here provide the type vocabulary used throughout the realtime group implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_zones.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_zones.c

## Purpose

Validates block-device zone descriptors for zoned XFS realtime groups and extracts write-pointer positions for sequential zones.

## Main Responsibilities

- Validates sequential write-required zones by zone condition.
- Accepts empty, open, closed, active, and full sequential zones when write pointers are valid.
- Rejects unsupported sequential zone conditions: not-write-pointer, offline, readonly, and unknown conditions.
- Validates conventional zones only when condition is `BLK_ZONE_COND_NOT_WP`.
- Checks every zone's capacity and length against expected rtgroup geometry.
- Converts valid sequential write pointers from 512-byte block units to filesystem blocks.

## Important Invariants

- Zone capacity must match realtime group capacity.
- Zone length must match expected geometry.
- All zones, including the last one, must have uniform capacity.
- A sequential-zone write pointer must lie within `[zone->start, zone->start + zone->capacity)`, except full zones report write pointer as capacity.
- Conventional zones do not supply a sequential write pointer.

## Dependencies

Uses block-layer `struct blk_zone`, XFS mount geometry conversion macros, rtgroup block types, and warning reporting.

## Research Notes

This is the low-level validator behind zoned realtime mount/setup. It enforces the uniform-zone assumption required by XFS zoned garbage collection.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_zones.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_zones.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_zones.h

## Purpose

Defines zoned realtime reservation constants and declares the zone descriptor validation API.

## Main Contents

- Garbage collection reservation constants:
  - `XFS_GC_ZONES`
  - `XFS_RESERVED_ZONES`
  - `XFS_MIN_ZONES`
- Open-zone reservation constants:
  - `XFS_OPEN_GC_ZONES`
  - `XFS_MIN_OPEN_ZONES`
- Default open-zone limit:
  - `XFS_DEFAULT_MAX_OPEN_ZONES`
- Validator declaration:
  - `xfs_validate_blk_zone`

## Important Invariants

- GC reserves multiple zones to guarantee forward progress while relocating data.
- At least one zone is kept out of the general open-zone pool so GC can proceed while writers wait.
- The default max-open-zones value is 128 when hardware does not provide a limit or when regular devices use the zoned allocator.

## Research Notes

This header captures zoned allocator safety margins. The constants are policy inputs for zoned realtime free-space and GC behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_zones.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/agb_bitmap.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/agb_bitmap.c

## Purpose

Implements scrub helpers that record per-AG btree blocks into an AG-block bitmap.

## Main Responsibilities

- Visits btree blocks through a cursor and records their AG block numbers in `struct xagb_bitmap`.
- `xagb_bitmap_set_btblocks` walks all btree blocks with `xfs_btree_visit_blocks`.
- `xagb_bitmap_set_btcur_path` records the current cursor path from leaf toward root while a btree walk is already in progress.

## Important Algorithm

`xagb_bitmap_set_btcur_path` relies on left-to-right btree record iteration. While cursor level pointers are at `1`, the traversal has just entered a block not previously seen on that walk, so the helper records that block and continues upward. When a level pointer is not `1`, that level's block was already seen.

## Important Invariants

- Only blocks with live buffers from `xfs_btree_get_block` are recorded.
- Buffer disk addresses are converted to filesystem block numbers and then AG block numbers.
- The helper is intended for per-AG btrees.

## Dependencies

Uses generic btree block visitation, buffer disk addresses, filesystem-to-AG block conversion, and `xagb_bitmap` wrappers over `xbitmap32`.

## Research Notes

This scrub utility is optimized for btree scans: it can collect btree block ownership either by visiting all blocks directly or piggybacking on an existing cursor walk.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/agb_bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/agb_bitmap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/agb_bitmap.h

## Purpose

Defines a type-checked AG-block bitmap wrapper around `xbitmap32` for scrub code.

## Main Contents

- `struct xagb_bitmap`, wrapping `struct xbitmap32`.
- Inline lifecycle helpers:
  - `xagb_bitmap_init`
  - `xagb_bitmap_destroy`
- Inline mutation/query helpers:
  - `xagb_bitmap_clear`
  - `xagb_bitmap_set`
  - `xagb_bitmap_test`
  - `xagb_bitmap_disunion`
  - `xagb_bitmap_hweight`
  - `xagb_bitmap_empty`
  - `xagb_bitmap_walk`
  - `xagb_bitmap_count_set_regions`
- Btree collection declarations:
  - `xagb_bitmap_set_btblocks`
  - `xagb_bitmap_set_btcur_path`

## Important Invariants

- Public operations use `xfs_agblock_t` starts and `xfs_extlen_t` lengths while delegating storage to a 32-bit bitmap.
- Walk callbacks use the underlying `xbitmap32_walk_fn` convention.

## Research Notes

This header gives scrub code a clearer AG-block typed interface over generic bitmap range tracking.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/scrub/agb_bitmap.h -->