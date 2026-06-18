# Group Research: group_862_linux_sources_os_linux_linux_fs_xfs_libxfs_xfs_rtgroup_c_sources_os__752e3bcf0532

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtgroup.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtgroup.c

## Purpose

`xfs_rtgroup.c` implements in-core realtime group management for XFS. It handles realtime group geometry, lifecycle, metadata inode locking/loading/creation, realtime group geometry reporting, and realtime superblock verification/logging.

## Main Content

- Computes per-realtime-group geometry:
  - Handles the first usable block, including reservation of the first realtime extent for an RT superblock when present.
  - Computes extents in each group, including shorter tail groups.
  - Precomputes group block count and minimum usable group block.
- Allocates, inserts, frees, and initializes `struct xfs_rtgroup` objects through the generic `xfs_group` infrastructure.
- Updates the previous last realtime group size after growfs recovery changes realtime geometry.
- Provides RT group metadata inode locking:
  - Bitmap and summary locks for non-zoned realtime devices.
  - Rmap and refcount metadata inode locks when present.
  - Transaction join helper for locked RT metadata inodes.
- Reports RT group geometry and health through `struct xfs_rtgroup_geometry`.
- Defines RT group metadata inode operations for bitmap, summary, rmap, and refcount inodes:
  - Feature predicates.
  - Metadata inode type.
  - Valid data fork formats.
  - Sickness bits.
  - Creation callbacks.
- Loads metadata inodes from legacy superblock inode fields or from the metadata directory `rtgroups/<rgno>.<name>` paths.
- Creates metadata directory entries and initializes metadata inodes.
- Provides lockdep ordering support for RT group metadata inode locks.
- Verifies, reads, writes, and logs realtime superblocks (`xfs_rtsb_buf_ops`, `xfs_update_rtsb`, `xfs_log_rtsb`).

## Key Interfaces and Invariants

- RT group zero can reserve the first realtime extent for the realtime superblock.
- `xfs_initialize_rtgroups` unwinds all newly inserted groups if any allocation fails.
- `xfs_update_last_rtgroup_size` requires an active reference to the old tail RT group.
- `XFS_RTGLOCK_BITMAP` and `XFS_RTGLOCK_BITMAP_SHARED` are mutually exclusive.
- Zoned realtime devices do not use bitmap/summary inode locking through this path.
- Metadata inode format is validated against the expected format mask for each inode type.
- Metadata inode project id must equal the RT group number.
- Missing or corrupt metadata directory state marks the filesystem metadir sick.
- RT superblocks must match the filesystem label, UUID, and metadata UUID and must have zero padding.

## Dependencies

Depends on generic group management, metadata directory APIs, transaction/inode APIs, realtime bitmap/summary creation, realtime rmap/refcount btree creation, health tracking, buffer verifiers, and superblock feature predicates.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtgroup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtgroup.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtgroup.h

## Purpose

`xfs_rtgroup.h` declares the realtime group abstraction, metadata inode slots, reference wrappers, address conversion helpers, validation helpers, locking flags, lifecycle APIs, and realtime superblock helper APIs.

## Main Content

- Defines `enum xfs_rtg_inodes` for per-RTG bitmap, summary, rmap, and refcount metadata inodes.
- Defines `struct xfs_rtgroup`:
  - Embedded generic `struct xfs_group`.
  - Metadata inode pointers.
  - Realtime extent count.
  - Union for bitmap summary cache or zoned open-zone tracking.
  - Zoned garbage-collection operation count.
- Defines `XFS_RTG_FREE` xarray mark for free zoned RT groups.
- Provides inline accessors for mount, group number, group size, and metadata inodes.
- Wraps generic group passive and active reference helpers for RT groups.
- Provides RT group iteration helpers.
- Defines RT group block validation and conversion helpers:
  - `xfs_verify_rgbno`, `xfs_verify_rgbext`.
  - `xfs_rgbno_to_rtb`, `xfs_rtb_to_rgno`, `xfs_rtb_to_rgbno`.
  - `xfs_rtx_to_rgbno`.
  - `xfs_rtb_to_daddr`, `xfs_daddr_to_rtb`.
- Declares RT group lifecycle, geometry, locking, metadata inode, and realtime superblock APIs when `CONFIG_XFS_RT` is enabled.
- Provides no-op stubs for many RT helpers when realtime support is disabled.
- Provides helpers for raw RT group sizing and RT group count to raw filesystem block conversion.

## Key Interfaces and Invariants

- `xfs_verify_rgbno` and `xfs_verify_rgbext` require rtgroups-enabled filesystems.
- Dense RT group device address conversion differs from filesystems with zone/daddr gaps.
- `xfs_rtgroup_raw_size` includes address gaps when `XFS_SB_FEAT_INCOMPAT_ZONE_GAPS` is active.
- RT group metadata inode paths are generated as `<rgno>.<shortname>`.
- Duplicate `xfs_rtginode_irele` declarations are present but harmless.

## Dependencies

Depends on `xfs_group.h`, XFS mount geometry, group xarray state, realtime feature predicates, metadata inode types, and buffer/inode types declared elsewhere.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtgroup.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrefcount_btree.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrefcount_btree.c

## Purpose

`xfs_rtrefcount_btree.c` implements the realtime reference count btree. This inode-rooted btree tracks shared/COW reference counts for extents on the realtime device and mirrors regular refcount btree behavior with realtime-group-specific roots and cursors.

## Main Content

- Defines a kmem cache for realtime refcount btree cursors.
- Implements btree cursor operations:
  - Cursor duplication.
  - Min/max records.
  - On-disk root max records.
  - Key and high-key initialization.
  - Record initialization from cursor state.
  - Key comparisons and contiguity.
  - Pointer initialization.
- Implements block verification:
  - Magic number validation.
  - Reflink feature validation.
  - V5 fsblock btree header validation.
  - Level and max-record checks.
  - CRC read/write verification.
- Defines `xfs_rtrefcountbt_buf_ops`.
- Defines `xfs_rtrefcountbt_ops` for inode-rooted btree operations.
- Allocates live cursors with RT group references and metadata inode state.
- Commits staged btree roots by replacing the real inode fork and logging inode core/root.
- Computes block max records, on-disk max levels, mount max levels, btree size, and reserve size.
- Converts btree roots between on-disk dinode fork format and in-memory btree block format.
- Loads and flushes realtime refcount metadata btree roots from/to metadata inodes.
- Creates an empty realtime refcount metadata inode root.

## Key Interfaces and Invariants

- Realtime refcount btrees require realtime reflink support; loading with only generic reflink is tolerated for growfs preparation, but corruption is reported if reflink is absent.
- The btree is inode-rooted and uses long pointers, but root packing differs between in-core and on-disk forms.
- Root pointer arrays are not immediately adjacent to the block header, so root reallocations must move pointer arrays explicitly.
- `m_rtrefc_maxlevels`, `m_rtrefc_mxr`, and `m_rtrefc_mnr` must be initialized from mount geometry before verification and reservations are meaningful.
- Reserve sizing assumes one refcount record per realtime extent in a group.
- Staged root commit transfers the staging fork by shallow copy after destroying the real fork.

## Dependencies

Depends on generic btree, btree staging, refcount record encoding, realtime groups, metadata inode allocation, health tracking, buffer CRC helpers, transactions, and inode fork conversion helpers.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrefcount_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrefcount_btree.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrefcount_btree.h

## Purpose

`xfs_rtrefcount_btree.h` declares realtime refcount btree APIs and layout helpers for in-core and on-disk inode-rooted realtime refcount btree roots.

## Main Content

- Defines `XFS_RTREFCOUNT_BLOCK_LEN` as the CRC long btree block header length.
- Declares live/staged cursor, staged commit, max-record, max-level, reserve, and create helpers.
- Provides inline address helpers for in-core records, keys, and pointers.
- Provides inline address helpers for on-disk dinode-root records, keys, and pointers.
- Provides pointer lookup for in-core roots when only the block size is known.
- Provides size calculators for:
  - In-core btree roots.
  - On-disk root blocks.
  - In-core root size from on-disk root state.
  - On-disk root size from in-core root state.
- Declares inode format/load, disk conversion, and flush helpers.

## Key Interfaces and Invariants

- Some address helpers are kept for userspace even when not used in the kernel file.
- In-core root size includes `XFS_RTREFCOUNT_BLOCK_LEN`; on-disk root size includes `struct xfs_rtrefcount_root`.
- Non-leaf root entries contain key/pointer pairs; leaf roots contain records.
- Root size helpers must be used consistently to avoid overfilling the inode data fork.

## Dependencies

Depends on realtime refcount on-disk structures from `xfs_format.h`, btree cursor types, realtime group types, and inode/dinode definitions supplied by surrounding XFS headers.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrefcount_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrmap_btree.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrmap_btree.c

## Purpose

`xfs_rtrmap_btree.c` implements the realtime reverse mapping btree. This inode-rooted overlapping btree tracks ownership of realtime device extents, supports staged and optional in-memory forms, and provides conversion between metadata inode roots and generic btree blocks.

## Main Content

- Defines a kmem cache for realtime rmap btree cursors.
- Implements btree cursor operations:
  - Cursor duplication.
  - Min/max record calculations.
  - On-disk root max records.
  - Key/high-key initialization.
  - Record initialization from cursor state.
  - Pointer initialization.
  - Three-part key comparison: start block, owner, offset.
- Masks unwritten state from rmap key comparisons because written/unwritten is a record attribute, not a key discriminator.
- Implements verifier and buffer ops for realtime rmap btree blocks.
- Defines `xfs_rtrmapbt_ops` as an overlapping inode-rooted btree.
- Provides optional `CONFIG_XFS_BTREE_IN_MEM` in-memory rtrmap btree verifier, buffer ops, btree ops, cursor creation, and initialization.
- Commits staged btree roots by replacing the metadata inode’s real data fork.
- Computes record capacity, maximum on-disk height, mount maximum height, btree size, and reserve size.
- Converts root blocks between on-disk dinode root format and in-memory generic btree block format.
- Loads and flushes realtime rmap metadata inode roots.
- Creates empty realtime rmap metadata inode roots.
- Initializes the rmap record for a realtime superblock reservation.
- Reads the highest tracked RT group block number from the root high key.

## Key Interfaces and Invariants

- Realtime rmap btrees require rmapbt support; growfs can create rmap inodes before an RT section is attached.
- The btree is overlapping, so internal nodes store low and high keys.
- Unwritten extent state is masked out of key comparisons.
- Reflink can create theoretically huge rmap record counts, so max-level calculation for rtreflink considers data-device space rather than record count alone.
- Reserve sizing keeps at least 1% of the RT group or enough for one block per record.
- Staged root commit sets the metadata inode project id to the RT group number.

## Dependencies

Depends on generic btree/staging APIs, optional in-memory btree APIs, realtime group state, rmap encoding, metadata inode allocation, health masks, buffer CRC helpers, and transaction/inode fork helpers.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrmap_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrmap_btree.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrmap_btree.h

## Purpose

`xfs_rtrmap_btree.h` declares realtime rmap btree APIs and root-layout helpers for in-core, on-disk, staged, and optional in-memory realtime rmap btrees.

## Main Content

- Defines `XFS_RTRMAP_BLOCK_LEN` as the CRC long btree block header length.
- Declares live/staged cursor, staged commit, max-record, max-level, reserve, size, create, and realtime-superblock initialization helpers.
- Provides in-core address helpers for records, low keys, high keys, and pointers.
- Provides on-disk dinode-root address helpers for records, keys, and pointers.
- Provides root size calculators for in-core and on-disk root formats.
- Declares inode format/load, disk conversion, and flush helpers.
- Declares optional in-memory realtime rmap btree cursor and initialization helpers.
- Declares `xfs_rtrmap_highest_rgbno`.

## Key Interfaces and Invariants

- Internal nodes store two rmap keys per pointer because the tree is overlapping.
- In-core and on-disk roots have different headers and must use the matching size/address helpers.
- In-memory helper declarations are present regardless of build guards in this header; definitions depend on `CONFIG_XFS_BTREE_IN_MEM`.
- Root space must fit inside the metadata inode data fork.

## Dependencies

Depends on realtime rmap on-disk structures, btree cursor types, realtime group state, optional xfbtree state, and inode/dinode definitions supplied by surrounding XFS headers.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_rtrmap_btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_sb.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_sb.c

## Purpose

`xfs_sb.c` implements XFS superblock validation, endian conversion, buffer verification, mount-time geometry setup, superblock logging/syncing, secondary superblock handling, filesystem geometry reporting, stripe validation, and realtime geometry helpers.

## Main Content

- Validates supported superblock versions:
  - V5 feature compatibility requirements.
  - V4 supported feature bits.
  - Required V4 directory and unwritten extent support.
- Converts superblock version fields into in-core feature flags.
- Validates feature masks during read and write verification.
- Validates realtime geometry:
  - Realtime extent size bounds.
  - Realtime block/extent/bitmap/summary consistency.
  - Zoned realtime constraints.
  - RT group count/size/log consistency.
  - RT groups requiring exchange-range support.
- Validates common superblock fields:
  - Magic, feature masks, block/sector/inode geometry.
  - Log device placement and size.
  - AG count/block math.
  - quota flag compatibility.
  - metadir padding and RT group feature fields.
  - stripe geometry.
- Converts quota fields between legacy on-disk and in-core layouts.
- Converts `struct xfs_dsb` to/from `struct xfs_sb`, including metadir, rtgroup, metauuid, and zoned fields.
- Provides read/write verifier operations and quiet probe verifier operations.
- Computes cached mount geometry:
  - AG and RT group block counts/logs/masks.
  - realtime bitmap block payload size.
  - btree min/max records for alloc, bmap, rmap, realtime rmap, refcount, and realtime refcount btrees.
  - allocation set-aside and AG usable limits.
- Logs and syncs the primary superblock, including lazy counter snapshots and realtime free extent counters.
- Updates secondary superblocks.
- Synchronously writes superblock buffers and optionally logs/writes the realtime superblock.
- Fills `xfs_fsop_geom` ABI structures through version 5.
- Reads and allocates secondary superblock buffers.
- Validates stripe geometry with optional mount-option repair.
- Computes realtime summary log (`rextslog`) and realtime group block log (`rgblklog`).

## Key Interfaces and Invariants

- V5 filesystems must have all required historical V4 feature flags set because runtime code still checks them.
- Unknown read-only compatible features require read-only mount; unknown incompatible features reject mount.
- Write verification treats unknown feature bits as memory corruption because read verification should have rejected them.
- Metadir filesystems store quota metadata outside legacy superblock quota inode fields.
- Metadir filesystems force legacy realtime bitmap/summary inode fields to `NULLFSINO` in core and zero on disk.
- `sb_bad_features2` is kept in sync with `sb_features2` when writing.
- RT group filesystems require `sb_rgcount == ceil(sb_rextents / sb_rgextents)`.
- Zoned realtime filesystems require uniform zone capacity and no free-extent superblock counter.
- Secondary superblock update errors are logged but do not abort updates for later AGs.
- `xfs_sync_sb_buf` can hold and write both primary and realtime superblock buffers.

## Dependencies

Depends on XFS format definitions, mount state, btree geometry helpers, allocation/rmap/refcount/realtime helpers, log and transaction APIs, health tracking, buffer verifiers, and user ABI geometry structures.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_sb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_sb.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_sb.h

## Purpose

`xfs_sb.h` declares the public libxfs superblock helper APIs used by mount, logging, geometry reporting, validation, and secondary superblock code.

## Main Content

- Declares superblock logging and syncing:
  - `xfs_log_sb`.
  - `xfs_sync_sb`.
  - `xfs_sync_sb_buf`.
- Declares mount-time common geometry setup and realtime extent-size update helpers.
- Declares superblock disk/in-core conversion and quota conversion helpers.
- Declares version/feature validation helpers.
- Declares secondary superblock update/read/get helpers.
- Defines maximum filesystem geometry ABI structure version as 5.
- Declares filesystem geometry fill helper.
- Declares stripe and realtime geometry validators.
- Declares realtime extent log and realtime group block log calculators.

## Key Interfaces and Invariants

- `xfs_sync_sb_buf` can update realtime superblocks via its `update_rtsb` argument.
- `xfs_fs_geometry` is versioned; callers provide the requested ABI structure version.
- Stripe geometry validation accepts a `may_repair` mode for mount-option overrides.

## Dependencies

Forward-declares XFS mount, superblock, disk superblock, transaction, geometry, and per-AG types. It relies on scalar XFS block/extent types from shared type headers.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_shared.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_shared.h

## Purpose

`xfs_shared.h` collects declarations and constants shared between kernel and userspace libxfs that do not fit better elsewhere. It exposes verifier ops, btree ops, transaction flags, superblock modification masks, buffer reference priorities, and computed inode geometry.

## Main Content

- Forward-declares common XFS types.
- Declares global `xfs_buf_ops` for AG headers, btrees, quotas, inodes, realtime metadata, superblocks, symlinks, and newer RT rmap/refcount metadata.
- Declares global `xfs_btree_ops` for alloc, inode, bmap, refcount, rmap, realtime rmap, and realtime refcount btrees.
- Provides inline predicates to identify btree op tables.
- Provides optional in-memory rmap/rtrmap btree predicates.
- Declares log reservation sizing helpers.
- Defines transaction flags:
  - Dirty, superblock dirty, permanent reservation, sync, reserve pool, no writecount, freed-block reservation, intent-done, low-mode, RT bitmap locked.
- Defines `xfs_trans_mod_sb` field masks, including realtime group count.
- Defines metadata buffer cache reference values.
- Defines `struct xfs_ino_geometry` with inode-count, cluster, inobt, allocation, alignment, fork offset, flags, and folio-order fields.

## Key Interfaces and Invariants

- Buffer and btree op declarations are shared with userspace repair/check tooling.
- Btree identity helpers use pointer equality against global op tables.
- `XFS_TRANS_LOWMODE` documents allocator behavior for low free-space btree split handling.
- `XFS_TRANS_RTBITMAP_LOCKED` records transaction ownership of realtime bitmap/summary inode locks.
- Inode geometry includes both raw and rounded cluster sizes because validation and runtime allocation need different forms.

## Dependencies

Relies on definitions of buffer ops, btree ops, transaction reservations, and inode/mount types supplied elsewhere in libxfs/kernel builds.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_shared.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_symlink_remote.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_symlink_remote.c

## Purpose

`xfs_symlink_remote.c` implements XFS symlink target encoding, verification, reading, writing, local-to-remote conversion, and remote block truncation. It handles both legacy unheadered symlink blocks and CRC-protected symlink blocks with headers.

## Main Content

- Computes how many filesystem blocks are needed for a symlink target after accounting for per-block headers.
- Initializes CRC symlink headers with magic, target offset, byte count, metadata UUID, owner inode, and disk address.
- Validates symlink header owner, offset, and byte count.
- Verifies symlink buffers:
  - Magic.
  - Metadata UUID.
  - Disk address.
  - Bounds against `XFS_SYMLINK_MAXLEN`.
  - Owner.
  - LSN.
  - CRC.
- Defines `xfs_symlink_buf_ops`.
- Converts inline/local symlink data to a remote block during fork format conversion.
- Verifies in-memory shortform symlink targets:
  - Nonzero length.
  - Nonnegative and within max length.
  - No interior NUL.
  - NUL terminator present.
- Reads remote symlink extents into a caller buffer, validating headers for CRC filesystems and marking symlink metadata sick on corruption.
- Writes symlink targets inline when they fit in the inode data fork or allocates/writes remote metadata blocks otherwise.
- Invalidates and unmaps remote symlink blocks during truncation.

## Key Interfaces and Invariants

- CRC symlink blocks include a header, reducing payload capacity per block.
- Legacy non-CRC symlink buffers have no verifier work.
- Header verification is split: buffer verifier checks block identity and bounds; read path checks caller-expected owner/offset/length.
- Remote read expects the bmap to cover the entire target and NUL-terminates the caller buffer.
- Remote truncate must both invalidate buffers and unmap extents; failure to unmap marks symlink metadata sick.
- Inline symlink write switches the data fork to `XFS_DINODE_FMT_LOCAL` and logs data/core.

## Dependencies

Depends on inode fork management, bmap read/write/unmap, transactions, buffer verifiers and CRC helpers, log item LSNs, mount feature predicates, and health marking.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_symlink_remote.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_symlink_remote.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_symlink_remote.h

## Purpose

`xfs_symlink_remote.h` declares the symlink encoding, verification, read, write, conversion, and truncation helpers implemented for XFS remote symlink targets.

## Main Content

- Declares symlink block count calculation.
- Declares CRC symlink header set/check helpers.
- Declares local-to-remote conversion helper.
- Declares shortform in-memory verifier.
- Declares remote symlink read/write helpers.
- Declares remote symlink truncation helper.

## Key Interfaces and Invariants

- `xfs_symlink_hdr_set` returns header size so callers can advance to payload.
- `xfs_symlink_write_target` accepts owner inode, target path, target length, allocated block count, and reservation block count.
- `xfs_symlink_shortform_verify` checks in-memory consistency, not full on-disk buffer format.

## Dependencies

Relies on XFS mount, inode, ifork, transaction, buffer, block, and fail-address types declared by surrounding headers.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_symlink_remote.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_inode.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_inode.c

## Purpose

`xfs_trans_inode.c` implements transaction helpers for joining inodes to transactions, changing timestamps, marking inode log items dirty, and rolling transactions while keeping an inode joined.

## Main Content

- `xfs_trans_ijoin`:
  - Requires the inode to be exclusively locked.
  - Initializes the inode log item if needed.
  - Records lock flags for commit-time unlock.
  - Clears per-transaction dirty state.
  - Adds the inode log item to the transaction.
- `xfs_trans_ichgtime`:
  - Updates ctime and optionally mtime, atime, and creation time.
  - Requires the inode to be locked and joined to the supplied transaction.
- `xfs_trans_log_inode`:
  - Marks the transaction dirty.
  - Sets inode log item dirty flags.
  - Bumps i_version once per transaction when configured and needed.
- `xfs_trans_roll_inode`:
  - Logs inode core.
  - Rolls the transaction.
  - Rejoins the inode to the new transaction.

## Key Interfaces and Invariants

- Joined inodes must not already have pending transaction lock flags.
- Stale inodes must not be joined or logged.
- Timestamp updates assert ctime change intent.
- Inode log item precommit later handles actual inode serialization; this file only records dirty state.
- i_version updates are avoided when possible unless core logging is already required.

## Dependencies

Depends on inode log items, transaction internals, VFS inode timestamp/version helpers, and XFS inode locking state.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_resv.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_resv.c

## Purpose

`xfs_trans_resv.c` calculates XFS transaction log reservations. It estimates worst-case log space and log operation counts for data writes, truncates, deferred operations, namespace changes, inode allocation/free, attributes, quotas, growfs, superblock updates, and atomic write completion.

## Main Content

- Defines buffer log overhead and generic buffer reservation calculations.
- Computes allocation/free btree block counts for allocbt/cntbt and optional rmapbt.
- Computes refcount and realtime refcount btree update reservation sizes.
- Computes inode logging reservation, accounting for in-memory btree root overhead that can exceed on-disk fork size.
- Computes inobt/finobt and inode chunk allocation/free reservations.
- Computes realtime allocation metadata reservation, including bitmap/summary and optional realtime rmap btree work.
- Calculates deferred intent completion reservations:
  - Data and realtime extent free.
  - Data and realtime rmap updates.
  - Data and realtime refcount updates.
  - Bmap updates.
- Calculates write and truncate reservations, including separate refcount update transactions and historical minimum-log-size behavior.
- Computes parent pointer xattr intent overhead for namespace transactions.
- Calculates rename, link, remove, create, tmpfile, mkdir, symlink, inode free, inode change, growdata, growrt, synchronous write, writeid, addafork, attribute invalidation/set/remove, quota, and superblock reservations.
- Computes namespace transaction log counts adjusted for parent pointer transaction rolls.
- Fills `struct xfs_trans_resv` in `xfs_trans_resv_calc`.
- Adjusts write/truncate/quota log counts for deferred BUI, CUI, and RUI intent items on reflink/rmap filesystems.
- Calculates default and custom atomic write ioend reservations:
  - Per-intent overhead.
  - Per-step completion reservation.
  - Maximum supported atomic write size for current reservation.
  - Minimum log blocks and new reservation for a requested size.

## Key Interfaces and Invariants

- Reservations intentionally overestimate many worst cases to avoid transaction overruns.
- Runtime reflink refcount updates run in separate transactions; minimum log size calculations preserve older behavior by folding refcount splits into write/truncate reservations.
- Realtime rmap and realtime refcount deferred updates are included in separate completion paths.
- Namespace reservations must be calculated after static attribute reservations because parent pointers depend on attr set/remove reservation sizes.
- Parent pointer support increases both reservation size and permanent log count for namespace operations.
- Atomic write sizing temporarily overrides `tr_atomic_ioend.tr_logres` to compute minimum log size, then restores the old value.
- A requested atomic write reservation fails if required minimum log blocks exceed the mounted log size.

## Dependencies

Depends on mount geometry, btree max levels, realtime bitmap helpers, quota formats, log intent item sizing, transaction space macros, parent pointer formats, and log minimum-size calculation.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_resv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_resv.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_resv.h

## Purpose

`xfs_trans_resv.h` defines transaction reservation structures, standard log count constants, directory reservation macros, and exported reservation calculation APIs.

## Main Content

- Defines `struct xfs_trans_res` with log reservation bytes, log operation count, and log flags.
- Defines `struct xfs_trans_resv` containing reservation entries for:
  - Writes and truncates.
  - Namespace operations.
  - Inode free/change.
  - Growfs.
  - Attribute operations.
  - Quotas.
  - Superblock.
  - Fsync timestamp/writeid.
  - Atomic ioend.
- Defines `M_RES(mp)` mount shorthand.
- Defines directory operation log reservation/count macros.
- Defines default and operation-specific log count constants.
- Retains older reflink log count constants for minimum log size calculations only.
- Declares full reservation calculation and individual deferred completion reservation helpers.
- Declares minimum-log-size reservation helpers.
- Declares atomic write reservation geometry helpers.

## Key Interfaces and Invariants

- Permanent reservations are indicated via `tr_logflags`, not by a separate type.
- Old reflink log count constants must not be used for runtime reservations.
- Directory operation macros depend on mount directory geometry and bmap reservation macros.

## Dependencies

Depends on XFS mount state and transaction space macros/types provided by surrounding libxfs headers.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_resv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_space.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_space.c

## Purpose

`xfs_trans_space.c` computes filesystem block reservation counts for namespace operations. These are block-space reservations, distinct from log-space reservations in `xfs_trans_resv.c`.

## Main Content

- Computes parent pointer space reservation:
  - Parent pointer attr tree entry.
  - Additional attr fork extent mapping space.
- Computes create and mkdir space reservations:
  - Inode allocation.
  - Directory entry insertion.
  - Optional parent pointer space.
- Computes link space reservation:
  - Directory entry insertion.
  - Optional parent pointer space.
- Computes symlink space reservation:
  - Inode allocation.
  - Directory entry insertion.
  - Remote symlink blocks.
  - Optional parent pointer space.
- Computes remove space reservation:
  - Directory removal.
  - Optional parent pointer removal space.
- Computes rename space reservation:
  - Source removal.
  - Target insertion.
  - Parent pointer replacement/removal/addition cases.
  - Whiteout handling.
  - Existing target handling.

## Key Interfaces and Invariants

- Parent pointers are assumed to be first attrs in an attr tree and no larger than one block.
- Parent pointer support increases namespace block reservations.
- Rename reserves for both removal and insertion paths, then layers parent pointer cases depending on whiteout and target existence.
- `xfs_rename_space_res` always adds existing-target parent pointer space, even outside the parent-feature conditional in the current code.

## Dependencies

Depends on transaction space macros, directory/attribute geometry, bmap btree sizing, and parent pointer feature predicates.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_space.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_space.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_space.h

## Purpose

`xfs_trans_space.h` defines block-space reservation macros for XFS metadata operations and declares namespace block reservation helper functions.

## Main Content

- Defines worst-case contiguous record capacity for bmap, realtime rmap, rmap, and allocation btrees.
- Defines space needed to add rmap, realtime rmap, and bmap extents.
- Preserves old reflink rmap maxlevels constant for compatibility in reservation calculations.
- Defines directory/attribute entry insertion and removal reservation components.
- Defines inode allocation and inode free reservation components.
- Defines transaction-level space macros for:
  - Add attr fork.
  - Attribute remove/set.
  - Direct I/O strategy.
  - Growfs data and realtime.
  - Quota allocation and quota inode creation.
- Declares block reservation functions for parent pointers and namespace operations.

## Key Interfaces and Invariants

- Reservation macros depend heavily on mount precomputed btree min/max record counts.
- DA reservation macros account for directory blocks fragmenting below directory block size.
- `XFS_IALLOC_SPACE_RES` accounts for finobt when enabled.
- Realtime rmap reservation macros use realtime rmap btree height and record density.

## Dependencies

Depends on mount btree geometry, inode geometry, directory geometry, fork identifiers, and feature predicates such as finobt.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_space.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_types.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_types.c

## Purpose

`xfs_types.c` implements runtime validators for XFS scalar address and count types, including filesystem blocks, extents, inodes, realtime blocks, inode counts, directory/attribute block offsets, and file offsets.

## Main Content

- Validates AG block numbers:
  - Must be within the AG.
  - Must not point at static AG metadata through the AGFL block.
- Validates filesystem block numbers and extents:
  - Must map to an existing AG.
  - Must not overflow.
  - Must not cross AG boundaries.
  - Must not point at static AG metadata.
- Validates inode numbers:
  - AG number must exist.
  - AG inode encoding must round-trip.
  - AG inode must be within per-AG inode range.
- Identifies superblock/internal inode numbers: realtime bitmap, realtime summary, and quota inodes.
- Validates directory inode targets by rejecting internal inodes.
- Validates realtime block numbers and extents:
  - For rtgroups, checks RT group number, group extent count, first RT superblock extent exclusion, and group boundary crossing.
  - For non-rtgroups, checks against `sb_rblocks`.
- Computes valid inode count range by walking per-AG state.
- Validates inode count, directory/attribute block offsets, file offsets, and file offset ranges.

## Key Interfaces and Invariants

- Extent validators reject arithmetic overflow by checking `start + len <= start`.
- Data device extents cannot cross allocation group boundaries.
- RT group extents cannot cross realtime group boundaries.
- RT superblock reservation in group zero is not allocatable.
- Directory entries cannot point to internal superblock/quota/realtime metadata inodes.
- Minimum inode count assumes root, rtbitmap, and rtsum occupy the first inode chunk.

## Dependencies

Depends on mount geometry, per-AG iteration, AG inode range helpers, realtime group helpers, realtime block conversions, quota inode predicates, and format macros.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_types.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_types.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_types.h

## Purpose

`xfs_types.h` defines fundamental XFS scalar types, null sentinels, size limits, fork identifiers, record structures, reservation enums, group/free-counter enums, and type verifier declarations.

## Main Content

- Defines scalar types for:
  - AG/RT group block numbers.
  - AG/RT group numbers.
  - extent lengths and counts.
  - file sizes and offsets.
  - realtime bitmap words/summary offsets.
  - log sequence numbers.
  - filesystem and realtime block addresses.
- Defines `xfs_failaddr_t` for verifier failure sites.
- Defines null sentinel constants for blocks, AGs, RT groups, file offsets, inodes, and LSNs.
- Defines minimum/maximum filesystem block and sector sizes.
- Defines inode fork identifiers, including staging, data, attr, and CoW forks.
- Defines lookup modes and trace string mappings.
- Defines name structure and dquot id type.
- Defines realtime bitmap bit-manipulation constants.
- Defines extent cursor, bmap extent record, extent state, refcount domain, refcount record, and rmap record.
- Defines rmap flags and key/record flag masks.
- Defines AG reservation types.
- Defines btree record packing scan results.
- Defines generic group types: AG and realtime group.
- Defines free counter types:
  - data blocks.
  - realtime extents.
  - zoned realtime available extents.
- Declares type verifier functions.

## Key Interfaces and Invariants

- `xfs_rfsblock_t` represents raw filesystem block numbers distinct from encoded filesystem block numbers.
- `xfs_rtblock_t` is a block address in realtime space, not necessarily a realtime extent number.
- `XFS_STAGING_FORK` is a fake fork id used for staging btrees.
- Rmap key flags exclude unwritten state; unwritten is a record flag.
- `XC_FREE_RTAVAILABLE` is meaningful for zoned realtime devices and differs from total free realtime extents.

## Dependencies

This foundational header is consumed broadly by libxfs and kernel XFS code; verifier declarations depend only on a forward-declared `struct xfs_mount`.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_zones.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_zones.c

## Purpose

`xfs_zones.c` validates block-layer zone descriptors against XFS zoned realtime geometry and extracts write pointer positions for sequential zones.

## Main Content

- Validates sequential write-required zones:
  - Empty zones set write pointer to zero.
  - Open, closed, and active zones require write pointer within zone capacity.
  - Full zones set write pointer to capacity.
  - Not-write-pointer, offline, and readonly conditions are rejected.
  - Unknown conditions are rejected.
- Validates conventional zones:
  - Only `BLK_ZONE_COND_NOT_WP` is accepted.
- Validates generic zone geometry:
  - Zone capacity must match expected RT group capacity.
  - Zone length must match expected raw zone size/geometry.
  - Dispatches by zone type to conventional or sequential validation.
  - Rejects unsupported zone types.

## Key Interfaces and Invariants

- All zones, including the last zone, must have uniform capacity matching the RT group size in the superblock.
- Sequential zone write pointers are converted from 512-byte sectors to filesystem blocks relative to zone start.
- A sequential zone write pointer must be at least zone start and strictly below start plus capacity unless the zone is full.
- Validation emits warnings with zone number and failed field values.

## Dependencies

Depends on Linux block zone definitions, XFS mount block conversion helpers, realtime group block types, and warning infrastructure.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_zones.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_zones.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_zones.h

## Purpose

`xfs_zones.h` defines zoned realtime allocator reservation constants and declares zone descriptor validation.

## Main Content

- Defines garbage collection zone reserve:
  - Three zones are reserved to guarantee GC forward progress with simpler accounting.
- Defines total reserved and minimum zone counts:
  - GC zones plus one write-reserve zone.
  - Minimum zones require one additional usable zone.
- Defines open-zone reserve:
  - One zone kept out of the general open pool for GC.
  - Minimum open zones count.
- Defines default max open zones as 128 for devices without an explicit limit or regular devices using the zoned allocator.
- Declares `xfs_validate_blk_zone`.

## Key Interfaces and Invariants

- Zoned allocation assumes enough reserved zones to relocate nearly full zones and continue user writes.
- `XFS_MIN_ZONES` and `XFS_MIN_OPEN_ZONES` encode allocator progress requirements, not merely hardware limits.

## Dependencies

Forward-declares realtime group and Linux block zone types; validation requires XFS mount and RT group block scalar types from surrounding headers.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_zones.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/agb_bitmap.c -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/agb_bitmap.c

## Purpose

`scrub/agb_bitmap.c` implements helpers for recording allocation-group block numbers of btree blocks into a type-safe scrub bitmap.

## Main Content

- Provides a btree block visitor that:
  - Retrieves the btree block buffer at a cursor level.
  - Converts buffer disk address to filesystem block.
  - Converts filesystem block to AG block.
  - Sets that AG block in an `xagb_bitmap`.
- Provides `xagb_bitmap_set_btblocks` to mark every block in a per-AG btree by using `xfs_btree_visit_blocks`.
- Provides `xagb_bitmap_set_btcur_path` to mark the current cursor path from leaf toward root while walking records.

## Key Interfaces and Invariants

- `xagb_bitmap_set_btcur_path` relies on btree query order from left edge to right edge.
- While walking records, a level’s block is newly seen when the cursor pointer at that level is `1`; once a non-first pointer is observed, higher levels have already been recorded for that path.
- The helpers record block numbers in AG block units, not fsblock units.
- Missing buffers during visitation are ignored.

## Dependencies

Depends on scrub bitmap wrappers, `xbitmap32`, generic btree cursor/block visitation, buffer disk addresses, and XFS block address conversion macros.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/agb_bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/agb_bitmap.h -->
# File Research: sources/os/linux/linux/fs/xfs/scrub/agb_bitmap.h

## Purpose

`scrub/agb_bitmap.h` defines a type-safe bitmap wrapper for XFS allocation group block numbers and declares btree block marking helpers used by scrub code.

## Main Content

- Defines `struct xagb_bitmap` as a wrapper around `struct xbitmap32`.
- Provides inline wrappers for:
  - Initialize and destroy.
  - Clear and set ranges.
  - Test a range.
  - Subtract/disunion another bitmap.
  - Count set blocks.
  - Check emptiness.
  - Walk set regions.
  - Count set regions.
- Declares helpers to mark all btree blocks or the current btree cursor path.

## Key Interfaces and Invariants

- The wrapper provides type clarity for `xfs_agblock_t` ranges while reusing 32-bit sparse bitmap storage.
- Range lengths use `xfs_extlen_t`.
- Walk callbacks use the generic `xbitmap32_walk_fn` signature.
- Region counting delegates directly to `xbitmap32`.

## Dependencies

Depends on `xbitmap32`, XFS AG block and extent length scalar types, and generic btree cursor declarations from the scrub build context.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/scrub/agb_bitmap.h -->