# Group Research: group_860_linux_sources_os_linux_linux_fs_xfs_libxfs_xfs_iext_tree_c_sources_o_997e2eb77bfc

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_iext_tree.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_iext_tree.c

This file implements the in-core extent index used by XFS inode forks. It stores `xfs_bmbt_irec` mappings in compact `xfs_iext_rec` records and organizes them as a small 256-byte-node B-tree with linked leaves. The packed record layout preserves start offset, block count, start block, and unwritten state in two 64-bit words.

Major responsibilities:
- Encode/decode extent records via `xfs_iext_set` and `xfs_iext_get`.
- Traverse extent lists with cursor APIs: `xfs_iext_first`, `xfs_iext_last`, `xfs_iext_next`, and `xfs_iext_prev`.
- Locate mappings with `xfs_iext_lookup_extent`, `xfs_iext_lookup_extent_before`, and `xfs_iext_get_extent`.
- Mutate the tree with `xfs_iext_insert_raw`, `xfs_iext_insert`, `xfs_iext_remove`, and `xfs_iext_update_extent`.
- Grow, split, merge, and shrink internal/leaf nodes while keeping parent keys synchronized.
- Destroy the in-core tree through `xfs_iext_destroy`.

Important invariants:
- `if_bytes` counts extent-record bytes and drives `xfs_iext_count`.
- `if_height == 0` means no tree; `if_height == 1` is a single leaf/root; larger heights have inner nodes.
- Empty records are identified by `hi == 0`, relying on the fact that valid extents cannot have zero length.
- Leaf nodes are doubly linked to support efficient cursor movement.
- Mutations increment `if_seq` with `WRITE_ONCE`, notably for COW fork change detection in writeback paths.

Dependencies and integration:
- Operates on `struct xfs_ifork`, `struct xfs_iext_cursor`, and `struct xfs_bmbt_irec`.
- Exposes APIs declared in `xfs_inode_fork.h`.
- Uses tracing hooks around insert/remove/update operations.
- Used by inode fork formatting, bmap operations, delayed allocation, and COW fork management.

Risk notes:
- Correctness depends on careful key propagation when the first record of a leaf/node changes.
- Split and merge code assumes sorted records and valid cursor placement.
- Allocation uses no-fail kernel allocations, appropriate for core metadata paths but important for memory-pressure analysis.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_iext_tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_buf.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_buf.c

This file handles inode-buffer verification, conversion between on-disk dinodes and in-core inodes, dinode CRC calculation, and validation of inode metadata constraints.

Major responsibilities:
- Verify inode buffers for normal reads, readahead, and writes through `xfs_inode_buf_ops` and `xfs_inode_buf_ra_ops`.
- Map an inode location to a buffer with `xfs_imap_to_bp`.
- Convert timestamps between legacy/bigtime on-disk encodings and `timespec64`.
- Load in-core inode state from disk with `xfs_inode_from_disk`.
- Write in-core inode state to disk format with `xfs_inode_to_disk`.
- Validate dinode structure and feature constraints with `xfs_dinode_verify`.
- Validate metadata-directory inode rules with `xfs_dinode_verify_metadir`.
- Validate extent-size and COW extent-size hints.
- Compute v3 inode CRCs with `xfs_dinode_calc_crc`.

Important validation areas:
- Magic, version, inode number, UUID, CRC, and superblock feature compatibility.
- Mode/file-type validity and zero-length directory/symlink constraints.
- Fork offset and fork format consistency.
- Local, extent, btree, and metadata-btree fork limits.
- Large extent count feature and padding rules.
- Reflink/realtime compatibility.
- Bigtime feature gating.
- Metadata inode requirements: v3 only, zero permissions, root uid/gid, no DMAPI fields, required immutable/sync/noatime/nodump/nodefrag flags, and no DAX.

Integration:
- Calls fork loaders from `xfs_inode_fork.c`.
- Initializes COW fork for reflink inodes.
- Adjusts active vs metadata inode statistics for metadir inodes.
- Marks AG inode health sick when buffer reads reveal metadata corruption.

Risk notes:
- This file is a central corruption boundary; verifier changes can affect mount compatibility.
- Some historical compatibility gaps are deliberately retained for old realtime extent-size hint behavior.
- Metadata-btree validation is feature-sensitive and depends on metadir, rmapbt, reflink, and realtime feature predicates.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_buf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_buf.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_buf.h

This header declares inode-buffer conversion and verification interfaces.

Key contents:
- Forward declarations for `struct xfs_inode` and `struct xfs_dinode`.
- `struct xfs_imap`, describing the disk buffer location of an inode:
  - `im_blkno`: starting basic block of the inode chunk.
  - `im_len`: chunk length in basic blocks.
  - `im_boffset`: byte offset of the inode inside the buffer.
- Prototypes for inode buffer mapping, CRC calculation, disk/in-core conversion, and dinode validation.
- Timestamp helpers:
  - `xfs_inode_encode_bigtime`
  - `xfs_inode_from_disk_ts`
- `xfs_dinode_good_version`, which enforces v3-only inode versions on v3 inode filesystems and v1/v2 otherwise.

Integration:
- Used by inode read/write paths, inode fork formatting, recovery, and verifiers.
- Provides shared declarations for code that must reason about dinode validity without owning the conversion implementation.

Risk notes:
- `xfs_dinode_good_version` encodes a core compatibility rule; misuse would allow unsupported dinode versions into higher layers.
- `xfs_imap` fields are low-level disk addressing data and must match allocation/inode geometry calculations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_buf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_fork.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_fork.c

This file converts inode fork data between on-disk representation and in-core fork state, manages fork memory, flushes fork contents back to dinodes, and provides helpers for COW forks and extent-count limits.

Major responsibilities:
- Initialize local-format forks with optional symlink NUL termination.
- Format data forks from disk via `xfs_iformat_data_fork`.
- Format attr forks from disk via `xfs_iformat_attr_fork`.
- Decode local, extent, regular btree, and metadata-btree fork formats.
- Allocate/reallocate btree roots with `xfs_broot_alloc` and `xfs_broot_realloc`.
- Resize inline data with `xfs_idata_realloc`.
- Destroy fork memory with `xfs_idestroy_fork`.
- Copy in-core extents to disk records with `xfs_iextents_copy`.
- Flush fork state into a dinode with `xfs_iflush_fork`.
- Initialize COW forks with `xfs_ifork_init_cow`.
- Verify local data and attr fork contents.
- Upgrade or reject extent counts through `xfs_iext_count_extend`.
- Decide realtime mapping behavior with `xfs_ifork_is_realtime`.

Important behavior:
- Extent-format forks are loaded into the in-core extent tree from `xfs_iext_tree.c`.
- Btree-format forks copy only the root initially; full extent loading can be deferred.
- `if_needextents` is stored with release semantics so readers can acquire it and safely observe fork format.
- Local data verifiers delegate to directory shortform, symlink shortform, and attr shortform validators.
- Metadata-btree forks dispatch to realtime rmap/refcount formatters and flushers based on inode metatype.

Risk notes:
- Fork format dispatch is mode-sensitive and corruption-sensitive.
- Delayed extent loading requires memory-ordering discipline.
- `xfs_iextents_copy` skips delayed/null-startblock extents and asserts physical extent validity before writing disk records.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_fork.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_fork.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_fork.h

This header defines the in-core inode fork structure and the public API for fork formatting, extent-tree manipulation, and fork helpers.

Key contents:
- `struct xfs_ifork`, containing:
  - inline data or extent-tree root in `if_data`
  - in-core btree root in `if_broot`
  - extent count, fork format, fork height, sequence counter, and delayed extent-read flag
- Worst-case extent-count growth constants for write, punch, xattr, reflink COW, and swap/rmap operations.
- Helpers for fork format, extent counts, max extent counts, and on-disk extent counter extraction.
- APIs for:
  - formatting data/attr forks
  - flushing forks
  - destroying/reallocating fork data
  - btree-root allocation
  - extent tree insert/remove/update/lookup/traversal
  - COW fork initialization
  - local fork verification
  - extent-count extension
  - realtime fork checks
- Cursor helper wrappers and `for_each_xfs_iext`.

Important invariants:
- Data/COW and attr forks have different small/large extent-count maxima.
- `xfs_need_iread_extents` uses acquire semantics matching release stores during fork formatting.
- `xfs_ifork_nextents(NULL)` returns zero and `xfs_ifork_format(NULL)` defaults to extents, simplifying absent attr/COW fork handling.

Integration:
- Central declaration point for extent tree code, inode fork conversion, bmap, writeback, and attr handling.

Risk notes:
- Constants here feed reservation and extent-count admission checks; incorrect counts can cause `-EFBIG` failures or overflows.
- The fork structure is heavily shared; layout or semantic changes have broad effects.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_fork.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_util.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_util.c

This file provides inode utility operations for flag conversion, inode initialization, inherited policy, unlinked-list management, link-count updates, and inode teardown.

Major responsibilities:
- Convert FS_XFLAG values to `di_flags` and `di_flags2`.
- Convert in-core XFS inode flags back to FS_XFLAG values.
- Determine initial project ID inheritance.
- Inherit inode flags and COW extent-size flags from parent directories.
- Initialize newly allocated inodes through `xfs_inode_init`.
- Decide whether a new inode needs an attr fork, especially for parent pointers.
- Maintain AGI-backed unlinked inode lists with in-core backrefs.
- Add/remove inodes from unlinked lists via `xfs_iunlink` and `xfs_iunlink_remove`.
- Drop and bump link counts with transaction logging.
- Free/reset inodes with `xfs_inode_uninit`.

Important behavior:
- Directory inheritance propagates realtime, extent-size, project, noatime, nodump, sync, nosymlinks, nodefrag, and filestream policy.
- Regular-file inheritance can turn directory RTINHERIT/EXTSZINHERIT into REALTIME/EXTSIZE.
- Invalid inherited extent-size or COW extent-size hints are cleared to prevent verifier or allocator problems.
- New inodes may get an empty attr fork immediately if xattrs will be set or parent pointers are enabled.
- The unlinked-list implementation uses on-disk AGI bucket heads plus in-memory doubly linked backrefs, avoiding per-AG list-head arrays.

Risk notes:
- AGI unlinked-list corruption is treated as filesystem metadata sickness.
- Link counts are pinned at `XFS_NLINK_PINNED` on underflow/overflow-like boundary cases.
- Inode freeing orders `xfs_difree` before unlinked-list removal to preserve AGI lock ordering.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_util.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_util.h

This header declares inode utility functions and the inode creation argument structure.

Key contents:
- Flag conversion APIs:
  - `xfs_flags2diflags`
  - `xfs_flags2diflags2`
  - `xfs_dic2xflags`
  - `xfs_ip2xflags`
- Project inheritance helper `xfs_get_initial_prid`.
- `struct xfs_icreate_args`, carrying idmap, parent inode, device number, mode, and creation flags.
- Creation flags:
  - `XFS_ICREATE_TMPFILE`
  - `XFS_ICREATE_INIT_XATTRS`
  - `XFS_ICREATE_UNLINKABLE`
- Timestamp-change flags for `xfs_trans_ichgtime`.
- Prototypes for inode initialization, uninitialization, unlinked-list operations, and link count updates.

Integration:
- Used by inode allocation/create paths, metadir creation, quota inode creation, unlink/inactivation, and transaction code.

Risk notes:
- The comments document idmap responsibilities because XFS only partially relies on VFS inheritance behavior.
- `XFS_ICREATE_UNLINKABLE` is important for parent-pointer behavior; callers creating detached metadata must choose flags carefully.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_inode_util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_log_format.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_log_format.h

This header defines the on-disk journal/log ABI for XFS, including physical log records, transaction headers, inode/buffer log items, deferred intent formats, quota log items, inode creation records, and attr operation records.

Major contents:
- Physical log constants: iclog counts, record sizes, header size, log versions, LSN helpers, and format tags.
- Log operation header and transaction header definitions.
- Log item type constants for inode, buffer, quota, inode-create, bmap intent/done, rmap intent/done, refcount intent/done, attr intent/done, mapping exchange intent/done, and realtime variants.
- Inode log format structures, including old 32-bit packed format.
- Inode log field flags such as `XFS_ILOG_CORE`, fork data/extent/root flags, owner-rewrite flags, and in-memory-only timestamp/iversion flags.
- `struct xfs_log_dinode`, the host-order logged mirror of `struct xfs_dinode`.
- Buffer log format, dirty bitmap definitions, buffer type encoding in `blf_flags`.
- EFI/EFD extent free intent/done formats with 32-bit and 64-bit compatibility extent layouts.
- RUI/RUD, CUI/CUD, BUI/BUD deferred intent/done formats.
- XMI/XMD mapping exchange formats and logged exchange flags.
- Quota log formats and quota mount/accounting/enforcement flags.
- Inode-create log record.
- Attr intent/done formats, including parent pointer operation opcodes.

Important ABI considerations:
- Many structures have fixed layout assumptions consumed by recovery and checked in `xfs_ondisk.h`.
- Some fields are host order by historical design, not pure disk endian format.
- Compatibility layouts exist for old 32-bit/i386 alignment differences.
- Variable-length intent structures use flexible arrays and helper `sizeof` functions.

Risk notes:
- This is recovery-visible persistent format; changes require extreme compatibility care.
- In-memory-only flags must never be written into recovered on-disk log item fields.
- Log item type values and struct layouts are effectively ABI.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_log_format.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_log_recover.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_log_recover.h

This header declares internal log recovery structures, item-operation callbacks, transaction reconstruction data, and helper APIs for replay.

Key contents:
- `enum xlog_recover_reorder`, controlling recovered item ordering into buffer, item, inode-buffer, and cancel lists.
- `struct xlog_recover_item_ops`, the per-log-item recovery vtable:
  - item type
  - reorder callback
  - pass2 readahead callback
  - pass1 commit callback
  - pass2 commit/replay callback
- Extern declarations for all supported recovery item ops, including realtime intent variants.
- Recovery hash constants for transaction IDs.
- `struct xlog_recover_item`, storing recovered log item regions and decoded ops.
- `struct xlog_recover`, representing a partially reconstructed transaction.
- Recovery pass constants: CRC pass, pass1, pass2.
- Buffer readahead/cancel-table helpers.
- Recovery inode-get helpers.
- Intent release and finishing helpers.
- `xlog_recover_resv`, which transforms normal transaction reservations into single-logcount reservations for intent replay.

Important behavior:
- Intent recovery pass2 reconstructs in-core intent items or releases them when done items are found.
- Reduced logcount for recovered intents avoids grant-space livelocks when recovered intents pin the log tail.

Integration:
- Used by log recovery implementation and deferred operation replay.
- Depends directly on log item type constants and formats from `xfs_log_format.h`.

Risk notes:
- Item ordering is central to safe replay, especially cancelled buffers and inode buffers.
- Reservation transformation is subtle and prevents recovery-time log-space deadlock.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_log_recover.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_log_rlimit.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_log_rlimit.c

This file computes maximum transaction reservations and minimum valid log size for a filesystem configuration, while preserving historical compatibility behavior.

Major responsibilities:
- Decide whether corrected minimum-log-size calculations are allowed through `xfs_want_minlogsize_fixes`.
- Calculate worst-case local attr set/remove reservation for minimum-log sizing.
- Build an alternate transaction reservation table for minimum-log calculations.
- Preserve older overestimates for filesystems lacking newer parent-pointer feature bits.
- Determine the largest reservation via `xfs_log_get_max_trans_res`.
- Compute minimum log size in filesystem blocks through `xfs_log_calc_minimum_size`.

Important compatibility behavior:
- Historical large-extent-count and reflink/rmap reservation bugs overestimated minimum log sizes.
- The code avoids reducing minimum log size for older feature sets so filesystems made by newer mkfs remain mountable by older kernels.
- Corrected calculations are only enabled for sufficiently new feature sets, currently gated by parent pointers on v5 filesystems.
- For old rmap+reflink behavior, `m_rmap_maxlevels` is temporarily forced to `XFS_OLD_REFLINK_RMAP_MAXLEVELS`.

Minimum log sizing rules:
- A single transaction must fit within a safe fraction of the log.
- The log must accommodate two maximally sized transactions.
- If a log stripe unit exists, padding for transaction data and commit record is included.
- Final result is converted from basic blocks to filesystem blocks.

Risk notes:
- This code affects mkfs and mount accept/reject decisions.
- Reducing historical minimums prematurely would create cross-version mount incompatibility.
- Reservation calculations depend on transaction reservation helpers and feature predicates.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_log_rlimit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_metadir.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_metadir.c

This file implements the metadata directory tree abstraction for metadata inodes stored inside special internal directories.

Major responsibilities:
- Look up metadata files/directories by path component with `xfs_metadir_lookup`.
- Load a metadata inode with `xfs_metadir_load`.
- Start, create, link, commit, and cancel metadata directory updates.
- Create metadata directories with `xfs_metadir_mkdir`.
- Coordinate transaction allocation, inode locks, directory updates, parent-pointer context, and cleanup.

Important behavior:
- Feature-gated by `xfs_has_metadir`.
- Metadata directory entries are validated for inode number and expected file type.
- Parent directory must be an actual directory; failure marks metadir health sick.
- Creation uses `xfs_dialloc`, `xfs_icreate`, `xfs_metafile_set_iflag`, and directory child creation.
- Parent pointer update context is allocated via `xfs_parent_start` when needed.
- Metadata files are not accounted to quota.
- Kernel builds exclude `xfs_metadir_start_link` and `xfs_metadir_link` via `#ifndef __KERNEL__`.

Lifecycle model:
- Callers populate `struct xfs_metadir_update`.
- Start function allocates transaction/resources and locks parent/child as appropriate.
- Create/link performs the actual directory operation.
- Caller must finish with commit or cancel, which tears down locks and parent-pointer context.
- If create returns an inode along with an error, caller must still finish inode setup before releasing it.

Risk notes:
- Files in the metadata directory tree currently cannot be unlinked.
- Cleanup paths are important because transactions and locks are staged across multiple functions.
- Metadata directory corruption maps to filesystem health state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_metadir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_metadir.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_metadir.h

This header defines the metadata directory update state and declares metadata directory operations.

Key contents:
- `struct xfs_metadir_update`, carrying:
  - parent directory inode
  - path component
  - parent-pointer args
  - child metadata inode
  - transaction
  - metadata file type
  - lock-state booleans
- Prototypes for:
  - `xfs_metadir_load`
  - `xfs_metadir_start_create`
  - `xfs_metadir_create`
  - `xfs_metadir_start_link`
  - `xfs_metadir_link`
  - `xfs_metadir_commit`
  - `xfs_metadir_cancel`
  - `xfs_metadir_mkdir`

Integration:
- Used by metadir-aware metadata inode creation/loading code, quota inode helpers, realtime metadata file setup, and repair/tools code.

Risk notes:
- The update struct encodes ownership of transaction and inode locks; callers must follow start/create-or-link/commit-or-cancel sequencing.
- `metafile_type` is used to stamp and later validate metadata inodes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_metadir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_metafile.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_metafile.c

This file implements metadata inode flag stamping and global space reservation accounting for metadata files, especially realtime metadata btrees.

Major responsibilities:
- Map metadata file type enum values to strings with `xfs_metafile_type_str`.
- Mark an inode as a metadata file/directory via `xfs_metafile_set_iflag`.
- Clear metadata inode marking via `xfs_metafile_clear_iflag`.
- Determine whether metadata file reservations are critically low.
- Account metadata file block allocation/freeing against the reservation and superblock counters.
- Initialize and free the global metadata file reservation.

Metadata inode stamping:
- Clears ordinary permission bits.
- Sets uid/gid to root.
- Applies required metadata file or metadata directory `di_flags`.
- Clears DAX.
- Sets `XFS_DIFLAG2_METADATA`.
- Stores the metadata type in `i_metatype`.
- Moves inode stats from active to metadata.

Reservation behavior:
- Reservation is protected by `m_metafile_resv_lock`.
- Available reservation blocks are hidden via delalloc/free-block accounting.
- Allocation first consumes reservation, then falls back to free blocks or transaction reservation.
- Freeing returns blocks to reservation up to target, then to filesystem free blocks.
- Reservation initialization scans realtime groups for rtrmap and rtrefcount inode usage and target reserve sizes.
- Target reservation is capped to one quarter of data blocks.

Risk notes:
- Reservation overruns are expected only for rmap btrees and are handled specially.
- Incorrect reservation accounting can desynchronize in-core free counters and on-disk superblock counters.
- Metadata inode stats must be kept balanced when setting/clearing metadata flags.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_metafile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_metafile.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_metafile.h

This header declares metadata file helpers and defines required inode flags for metadata files and directories.

Key contents:
- `xfs_metafile_type_str`.
- `XFS_METAFILE_DIFLAGS`, requiring immutable, sync, noatime, nodump, and nodefrag.
- `XFS_METADIR_DIFLAGS`, adding nosymlinks for metadata directories.
- APIs to set/clear metadata inode flags.
- Metadata file reservation APIs:
  - `xfs_metafile_resv_critical`
  - `xfs_metafile_resv_alloc_space`
  - `xfs_metafile_resv_free_space`
  - `xfs_metafile_resv_free`
  - `xfs_metafile_resv_init`
- External kernel/userspace-specific inode lookup hooks:
  - `xfs_trans_metafile_iget`
  - `xfs_metafile_iget`

Integration:
- Used by metadir creation, inode verification, metadata file loading, and allocation paths.

Risk notes:
- Required flag definitions are part of metadata inode validation in `xfs_inode_buf.c`.
- External lookup hooks must enforce expected metadata type and inode validity.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_metafile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ondisk.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ondisk.h

This header provides compile-time assertions that XFS on-disk and UABI structures have expected sizes, offsets, and constant values.

Major responsibilities:
- Define assertion macros for structure size, member offset, constant value, and superblock field offsets.
- Implement `xfs_check_ondisk_structs`, called at init time to compile-check layout assumptions.
- Check file structures, space btrees, dir/attr structures, realtime structures, log structures, parent pointer ioctl structs, superblock fields, and selected ioctl UABI structures.

Important checked areas:
- Dinodes, dquots, bmbt records, symlink headers, timestamps.
- AGF/AGI/AGFL and btree block/key/record layouts.
- Attr and directory v2/v3 block/header layouts.
- Realtime superblock/buffer/root pointer structures.
- Log item formats from `xfs_log_format.h`.
- Physical log record headers.
- Parent pointer ioctl records.
- Superblock field offsets through `struct xfs_dsb` and `struct xfs_sb`.
- Bigtime and quota bigtime range conversions.
- Public ioctl struct sizes.

Purpose:
- Prevent compiler, architecture, or source changes from silently altering persistent disk format or userspace ABI.
- Preserve v4/v5 shared header offsets so older metadata fields remain findable at stable positions.

Risk notes:
- Some structures are intentionally omitted due to architecture-dependent padding.
- Any assertion change should be treated as disk-format or UABI review material.
- This file is a guardrail, not runtime validation; it catches layout drift at build time.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ondisk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_parent.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_parent.c

This file implements XFS parent pointer attributes. Parent pointers are stored as local extended attributes whose name is the directory entry name and whose value is a `struct xfs_parent_rec` containing parent inode number and generation.

Major responsibilities:
- Validate parent pointer attr names with `xfs_parent_namecheck`.
- Validate parent pointer values with `xfs_parent_valuecheck`.
- Compute parent pointer hash values with parent inode mixed into the directory name hash.
- Initialize `xfs_da_args` for parent pointer xattr operations.
- Ensure attr fork extents are loaded before parent pointer operations.
- Add, remove, and replace parent pointers for link/unlink/rename operations.
- Extract parent inode/generation from xattr data.
- Provide repair-oriented lookup/set/unset helpers.

Important behavior:
- Parent pointers require the parent feature to be enabled.
- Names must satisfy directory filename constraints and cannot be incomplete attrs.
- Values must be local, non-null, exactly `sizeof(struct xfs_parent_rec)`, and contain a valid directory inode.
- Parent pointer attrs use `XFS_ATTR_PARENT`, logged operations, and OKNOENT behavior.
- Hashing mixes parent inode with name hash to reduce hardlink collision risk.
- Parent pointer updates call into attr set/remove/replace machinery.

Repair helpers:
- `xfs_parent_lookup` looks up a specific parent pointer under caller-held inode lock.
- `xfs_parent_set` and `xfs_parent_unset` are immediate, no-transaction repair functions and sanity-check inputs first.

Risk notes:
- Missing attr fork on a parent-enabled child is treated as corruption and marks inode parent health sick.
- Creating inodes without required parent pointers is considered corruption-prone; other code reserves blocks accordingly.
- Correct generation handling matters to distinguish reused inode numbers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_parent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_parent.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_parent.h

This header declares parent pointer validation, hashing, update, extraction, and repair interfaces.

Key contents:
- Validators:
  - `xfs_parent_namecheck`
  - `xfs_parent_valuecheck`
- Hash helpers:
  - `xfs_parent_hashval`
  - `xfs_parent_hashattr`
- Inline record initializers:
  - `xfs_parent_rec_init`
  - `xfs_inode_to_parent_rec`
- Parent args slab cache declaration.
- `struct xfs_parent_args`, carrying old/new parent records and `xfs_da_args`.
- `xfs_parent_start` and `xfs_parent_finish`, which allocate/free update context only when parent pointers are enabled.
- Update APIs for add, remove, and replace.
- `xfs_parent_from_attr` to parse parent pointer xattrs.
- Repair APIs for lookup, set, and unset.

Integration:
- Used by directory operations, metadir updates, attr item logging, scrub/repair paths, and inode creation policy.

Risk notes:
- `xfs_parent_start` returns success with `NULL` args when the feature is disabled, so callers must tolerate no-op parent pointer context.
- Parent pointer updates share attr machinery and must preserve correct owner/name/value state in `xfs_da_args`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_parent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_quota_defs.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_quota_defs.h

This header defines quota-related shared types, flags, reservations, helpers, and quota inode metadata-directory interfaces.

Key contents:
- `xfs_qcnt_t` as a 64-bit quota counter/limit type.
- `xfs_dqtype_t` as an 8-bit quota type.
- String tables for quota types and dquot flags.
- Dirty flag `XFS_DQFLAG_DIRTY`.
- `XFS_DQUOT_LOGRES`, sized for worst-case transactions modifying up to six dquots plus log format items.
- Quota enabled/enforced predicate macros for user, group, and project quotas.
- Non-persistent `XFS_QMOPT_*` operation flags for quota selection, reservation, accounting fields, and inheritance.
- Transaction dquot modification aliases.
- Quota option masks for all quota types and block reservation flags.
- Declarations for dquot verification, repair, timestamp conversion, and chunk sizing.
- Quota inode helpers for metadir path/type mapping and loading/creating/linking quota inodes.

Important behavior:
- User, group, and project quota inode paths map to `"user"`, `"group"`, and `"project"`.
- Quota inode metafile types map to `XFS_METAFILE_USRQUOTA`, `XFS_METAFILE_GRPQUOTA`, and `XFS_METAFILE_PRJQUOTA`.
- Header notes that `XFS_QMOPT_*` values are not persistent ABI and may change between versions.

Integration:
- Shares quota constants with kernel and userspace source trees.
- Depends on quota flags from `xfs_log_format.h`.
- Connects quota inode handling to metadir/metafile infrastructure.

Risk notes:
- `XFS_DQUOT_LOGRES` encodes worst-case transaction reservation assumptions.
- Operation flags must not be stored persistently.
- Invalid quota type reaches assertions in inline path/metafile-type helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_quota_defs.h -->