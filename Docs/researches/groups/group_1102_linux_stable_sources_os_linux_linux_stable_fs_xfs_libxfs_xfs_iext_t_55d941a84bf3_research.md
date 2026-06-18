# Group Research: group_1102_linux_stable_sources_os_linux_linux_stable_fs_xfs_libxfs_xfs_iext_t_55d941a84bf3

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux-stable`.

This group covers XFS libxfs inode fork storage, in-core extent indexing, dinode import/export and verification, inode lifecycle helpers, journal format ABI, log-size limits, metadata directory/file support, parent pointer attributes, quota constants, and on-disk layout assertions.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_iext_tree.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_iext_tree.c

## Role
`xfs_iext_tree.c` implements the in-core extent index used by XFS inode forks. It stores `struct xfs_bmbt_irec` mappings in a compact 256-byte node/leaf tree, supports cursor-based traversal and lookup, and provides insert, remove, update, and destroy operations for data, attr, and CoW forks.

## Main Responsibilities
- Pack and unpack in-core extent records into `struct xfs_iext_rec`, preserving start offset, start block, block count, and unwritten-state bit.
- Maintain a small btree-like structure with internal nodes keyed by the first extent offset of each child and leaves containing packed extent records plus prev/next leaf links.
- Provide cursor movement helpers: `xfs_iext_first`, `xfs_iext_last`, `xfs_iext_next`, and `xfs_iext_prev`.
- Support lookups by file offset through `xfs_iext_lookup_extent` and reverse/range-end lookup through `xfs_iext_lookup_extent_before`.
- Insert, split, merge, remove, and rebalance leaves and internal nodes while keeping parent keys current.
- Increment `if_seq` before extent-tree mutations so writeback and CoW fork users can notice changes.

## Important Functions
- `xfs_iext_set` and `xfs_iext_get` are the only packing/unpacking boundary for in-core extent records.
- `xfs_iext_find_level` descends to the requested tree level using separator keys.
- `xfs_iext_insert_raw` allocates the first root, grows the inline root, splits full leaves, inserts a record, and propagates new child nodes upward.
- `xfs_iext_insert_node` and `xfs_iext_split_node` maintain internal levels after leaf splits.
- `xfs_iext_remove` deletes the current cursor record, fixes cursor position, updates parent keys, and triggers leaf/node rebalance or root removal.
- `xfs_iext_rebalance_leaf`, `xfs_iext_remove_node`, and `xfs_iext_rebalance_node` merge underfull nodes when combined entries fit.
- `xfs_iext_update_extent` overwrites an existing extent and repairs separator keys if the first record offset changes.
- `xfs_iext_destroy` recursively frees the tree and resets the fork’s extent-tree fields.

## Data and Invariants
- `if_bytes` counts packed in-core extent records, not allocated tree-node bytes.
- `if_height == 0` means no tree; `if_height == 1` means `if_data` points directly at a leaf/root record area; higher values use internal nodes.
- Empty extent records are detected by `hi == 0`; zero-length extents are impossible, so this is a safe sentinel.
- Internal node keys are first offsets of child subtrees; `XFS_IEXT_KEY_INVALID` marks unused slots.
- Leaves are linked in sorted order to make adjacent cursor movement cheap after lookup.
- The tree is optimized for append patterns: splitting at the end spills into a new empty node rather than moving half the entries.

## Error Handling and Risks
- Allocation uses `__GFP_NOFAIL`, so tree operations do not return allocation errors.
- Corruption-style conditions are enforced with assertions because this is in-memory metadata derived from already-verified fork mappings.
- The recursive destroy path is explicitly noted as stack-sensitive.

## Dependencies
This file depends on inode fork state from `xfs_inode_fork.h`, bmap extent records, XFS tracepoints, and bmap fork-state flags via `xfs_iext_state_to_fork`.

## Research Notes
This is not an on-disk btree. It is a compact in-memory acceleration structure for inode fork extents, with parent keys keyed by first child extent offset and leaf links for efficient sequential scans.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_iext_tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_buf.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_buf.c

## Role
`xfs_inode_buf.c` handles disk inode buffer verification, conversion between on-disk dinodes and in-core `xfs_inode` state, dinode CRC calculation, and validation of inode core fields, fork formats, extent-count encodings, metadata inode rules, and extent size hints.

## Main Responsibilities
- Verify inode cluster buffers for magic, inode version, and valid unlinked-list pointers.
- Map an inode location to its containing buffer with `xfs_imap_to_bp`.
- Decode and encode legacy and bigtime timestamps.
- Convert dinodes into in-core inode fields via `xfs_inode_from_disk`.
- Convert in-core inode fields back to dinode fields via `xfs_inode_to_disk`.
- Verify full dinode consistency with `xfs_dinode_verify`.
- Validate fork formats, fork offsets, large extent counter encoding, metadata inode constraints, extent size hints, and CoW extent size hints.
- Calculate v3 inode CRCs.

## Important Functions
- `xfs_inode_buf_verify` checks every inode in a buffer. Readahead verification suppresses normal corruption reporting and marks the buffer for reread with `-EIO`.
- `xfs_inode_from_disk` validates the dinode first, imports ownership, mode, timestamps, sizes, extents, flags, project id, v3 fields, forks, and initializes CoW/metadir accounting as needed.
- `xfs_inode_to_disk` writes in-core inode state into a dinode, including v2/v3 selection, metadata type, timestamps, fork formats, extent counters, UUID, inode number, and LSN.
- `xfs_dinode_verify_fork` validates local/extents/btree/meta-btree fork format rules and feature dependencies.
- `xfs_dinode_verify_forkoff` checks attr fork split points and special device fork offsets.
- `xfs_dinode_verify_metadir` enforces metadata inode constraints: v3 inode, metadata feature, valid metatype, zero permissions, root uid/gid, no DMAPI fields, mandatory flags, no DAX.
- `xfs_dinode_verify` performs the central dinode verifier, including CRC/UUID/ino checks, mode/type checks, extent count versus block count, realtime/reflink/bigtime feature checks, fork checks, and metadata inode checks.
- `xfs_inode_validate_extsize` and `xfs_inode_validate_cowextsize` validate hint flags, mode applicability, nonzero rules, alignment, max extent length, and AG-size bounds.

## Data and Invariants
- v3 dinodes must match filesystem UUID and inode number and pass CRC verification.
- v1 inodes are converted to v2-style in-core state; v1 `di_metatype` historically held old link count data.
- Large extent counters require the filesystem feature and zero padding in the alternate union field.
- Local directories must be local format when size fits in the inode; oversized data cannot claim local format.
- Metadata inodes using `XFS_DIFLAG2_METADATA` are deliberately hidden from userspace through mode and flag constraints.
- Metadata btree inodes have zero normal extent counts because their data fork is an embedded metadata btree root, not normal bmap extents.

## Error Handling and Corruption Response
- Verification failures return fail addresses to callers; import paths convert them to `-EFSCORRUPTED`, emit verifier errors, and mark inode/AG health sick.
- Buffer read failures that indicate sick metadata mark AG inode health sick in `xfs_imap_to_bp`.
- Hint validators intentionally retain historical compatibility around directory realtime hint alignment and expect callers to sanitize inheritance into regular files.

## Dependencies
This file integrates inode fork import from `xfs_inode_fork.c`, directory/attr validation, health reporting, metadata file flags, quota-independent metadata inode handling, and mount feature predicates.

## Research Notes
This is the main trust boundary for disk inode cores. Most later inode and fork code assumes the invariants enforced here: valid fork formats, valid v3 integrity fields, sane extent counters, and feature-compatible inode flags.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_buf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_buf.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_buf.h

## Role
`xfs_inode_buf.h` declares inode-buffer mapping, dinode conversion, dinode verification, timestamp conversion, and inode hint validation interfaces.

## Main Definitions
- `struct xfs_imap` records the disk block, length, and byte offset needed to find an inode inside an inode chunk buffer.
- `xfs_inode_encode_bigtime` converts in-core timestamps into the XFS bigtime nanosecond encoding.
- `xfs_dinode_good_version` defines acceptable dinode versions based on whether the mount supports v3 inodes.

## Exported API
- Buffer/dinode access: `xfs_imap_to_bp`.
- Disk/in-core conversion: `xfs_inode_from_disk`, `xfs_inode_to_disk`, and `xfs_inode_from_disk_ts`.
- Integrity: `xfs_dinode_calc_crc`, `xfs_dinode_verify`, and `xfs_dinode_verify_metadir`.
- Hint validation: `xfs_inode_validate_extsize` and `xfs_inode_validate_cowextsize`.

## Dependencies
The header depends on XFS mount, inode, dinode, transaction, timestamp, and fail-address types supplied by surrounding libxfs headers.

## Research Notes
This header is the compact contract for inode core verification and conversion. It separates inode-buffer location (`xfs_imap`) from dinode semantic validation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_buf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_fork.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_fork.c

## Role
`xfs_inode_fork.c` imports, manages, verifies, flushes, and destroys XFS inode forks. It handles local-format data, extent-format forks, btree-format roots, metadata btree forks, attr forks, CoW forks, and conversion of in-core extents back to disk records.

## Main Responsibilities
- Initialize inline/local forks, including NUL termination for in-core symlink bodies.
- Import local, extents, btree, and metadata-btree fork formats from a dinode.
- Initialize, reset, and destroy attr forks and CoW forks.
- Allocate and resize in-core bmap btree roots.
- Resize local fork data buffers.
- Copy in-core extent records to on-disk bmbt records during inode flush.
- Flush each fork according to its current format and inode log flags.
- Verify shortform directory, symlink, and attr fork contents.
- Check whether a fork can accept additional extents and upgrade to large extent counters if possible.

## Important Functions
- `xfs_iformat_local` copies local fork bytes after checking the size fits in the selected fork region.
- `xfs_iformat_extents` imports inline bmbt records into the in-core extent tree, validating every extent through bmap validation.
- `xfs_iformat_btree` validates and imports an inode-rooted bmap btree root into `if_broot`.
- `xfs_iformat_data_fork` chooses fork import logic based on inode mode and data fork format, including special device handling and metadata-btree dispatch.
- `xfs_iformat_attr_fork` imports the attr fork and zaps it back to empty extents format on failure.
- `xfs_broot_alloc` and `xfs_broot_realloc` manage in-core btree root buffers; shrink uses allocate-copy-free to avoid relying on `krealloc` shrinking behavior.
- `xfs_idata_realloc` resizes local fork data and updates `if_bytes`.
- `xfs_idestroy_fork` frees local data, btree roots, and in-core extent trees.
- `xfs_iextents_copy` skips delayed allocation/null-startblock mappings and writes only real extents to disk format.
- `xfs_iflush_fork` serializes the selected fork based on current format, not merely stale log flags.
- `xfs_iext_count_extend` checks extent-count limits, optionally sets `XFS_DIFLAG2_NREXT64`, and logs the inode core.

## Data and Invariants
- `if_format` controls how `if_data`, `if_broot`, and `if_bytes` are interpreted.
- `if_needextents` uses release/acquire semantics so readers that notice deferred btree extent loading also see the fork format.
- Local regular files are not supported; local data fork verification applies to shortform directories and symlinks.
- Btree-format forks must have enough extents to justify btree format and a nonzero root level within max bmap levels.
- Disk flushing prioritizes current fork format because fork format may have changed after log flags were set.
- CoW fork extent counts are not constrained by on-disk extent counters.

## Error Handling and Corruption Response
- Bad fork sizes, invalid extents, impossible btree roots, or invalid fork formats produce verifier errors, mark inode core sick, and return `-EFSCORRUPTED`.
- Attr fork import failure destroys any partially imported attr fork and resets it to empty extents format.
- Large extent counter upgrade returns `-EFBIG` if limits would be exceeded and the filesystem cannot upgrade.

## Dependencies
This file depends on bmap/bmbt conversion, DA directory and attr shortform verifiers, symlink verifier, realtime metadata btree import/flush helpers, inode log item flags, and the in-core extent tree from `xfs_iext_tree.c`.

## Research Notes
This is the bridge between the dinode fork bytes and XFS’s in-core fork representations. The key behavior is format-driven import/flush with strict validation before any fork contents become trusted.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_fork.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_fork.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_fork.h

## Role
`xfs_inode_fork.h` defines the in-core inode fork structure and declares APIs for fork import, flush, destruction, extent tree manipulation, local data management, and extent count limit handling.

## Main Definitions
- `struct xfs_ifork` stores fork data bytes, in-core btree root, modification sequence, extent-tree height, data/root pointer, extent count, btree root byte size, fork format, and deferred extent-read flag.
- `XFS_IEXT_*_CNT` macros estimate worst-case extent count growth for operations such as adds, hole punches, attr manipulation, unwritten conversion, reflink CoW completion, and rmap swaps.
- `XFS_IFORK_MAXEXT` computes how many bmbt records fit in a fork region.
- `xfs_iext_max_nextents` returns small or large extent-count limits for data/CoW versus attr forks.
- `xfs_dfork_*_extents` helpers read small or large dinode extent counters.

## Exported API
- Fork initialization/import/flush: `xfs_iformat_data_fork`, `xfs_iformat_attr_fork`, `xfs_ifork_init_attr`, `xfs_ifork_zap_attr`, `xfs_iflush_fork`, and `xfs_ifork_init_cow`.
- Memory lifecycle: `xfs_idestroy_fork`, `xfs_idata_realloc`, `xfs_broot_alloc`, `xfs_broot_realloc`, and `xfs_init_local_fork`.
- Extent tree operations: insert, remove, lookup, lookup-before, get, update, cursor movement, peek helpers, and `for_each_xfs_iext`.
- Extent loading/copying: `xfs_iread_extents`, `xfs_iextents_copy`, and `xfs_need_iread_extents`.
- Validation and policy: `xfs_ifork_verify_local_data`, `xfs_ifork_verify_local_attr`, `xfs_iext_count_extend`, and `xfs_ifork_is_realtime`.

## Data and Invariants
- A null fork pointer is treated as empty extents format by `xfs_ifork_nextents` and `xfs_ifork_format`.
- Forks have extents only when format is `EXTENTS` or `BTREE`.
- `xfs_need_iread_extents` uses acquire semantics paired with import-time release stores.
- Cursor helpers expose a stable iteration idiom without exposing the extent tree layout.

## Dependencies
The header connects inode fork users to bmap state, dinode formats, transaction logging, and in-core extent tree operations.

## Research Notes
This header is the public map for inode fork storage. It encodes both representation details (`struct xfs_ifork`) and operation-risk estimates used before metadata updates grow extent counts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_fork.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_util.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_util.c

## Role
`xfs_inode_util.c` provides inode flag conversion, inode creation initialization, parent-to-child flag inheritance, project id inheritance, unlinked-list maintenance, link count updates, and inode uninitialization/freeing.

## Main Responsibilities
- Convert between userspace `FS_XFLAG_*` flags and on-disk `di_flags`/`di_flags2`.
- Initialize new inodes with correct ownership, mode, link count, timestamps, fork format, inherited flags, project id, and optional attr fork.
- Maintain per-AG on-disk unlinked inode hash chains plus in-core backreferences.
- Increment/decrement link counts and move zero-link inodes to or from AGI unlinked lists.
- Free an inode from allocation metadata and reset the in-core inode to an unallocated state.

## Important Functions
- `xfs_flags2diflags`, `xfs_flags2diflags2`, and `xfs_ip2xflags` translate between ioctl-visible flags and inode disk flags.
- `xfs_get_initial_prid` inherits project id only when the parent has `PROJINHERIT`.
- `xfs_inode_inherit_flags` and `xfs_inode_inherit_flags2` propagate realtime, extent-size, project, DAX, CoW extent-size, and metadata flags while clearing invalid inherited hints.
- `xfs_icreate_want_attrfork` pre-creates an attr fork when requested or when parent pointers require one.
- `xfs_inode_init` performs initial inode setup and logs the core/dev fields.
- `xfs_iunlink_update_bucket`, `xfs_iunlink_insert_inode`, and `xfs_iunlink` insert zero-link inodes into the AGI unlinked bucket chain.
- `xfs_iunlink_remove_inode` and `xfs_iunlink_remove` remove inodes from the unlinked chain, updating either the AGI bucket or the previous cached inode.
- `xfs_droplink` decrements link count, handles underflow by pinning the count, logs the inode, and inserts into unlinked lists at zero.
- `xfs_bumplink` increments link count, pins at overflow, and logs the inode.
- `xfs_inode_uninit` frees allocation metadata first, removes from unlinked list, clears local data, resets mode/flags/fork state, bumps generation, and logs the core.

## Data and Invariants
- Unlinked-list updates are serialized by the AGI buffer lock.
- In-core backreferences avoid scanning singly linked AGI chains when removing an inode.
- Inodes on unlinked lists must have VFS references, allowing lockless inode cache lookups for backreference updates.
- `O_TMPFILE` and zero-link files are kept reachable through AGI unlinked buckets until inactive/free time.
- Metadata children inherit the metadata flag from metadata directories.

## Error Handling and Corruption Response
- Invalid AGI bucket pointers or self-referential list entries mark the AGI sick and return `-EFSCORRUPTED`.
- Missing cached next inodes during unlinked updates trigger reload helpers; missing previous inodes during removal marks the current inode core sick.
- Link count underflow/overflow is rate-limited and pinned to avoid wrapping.

## Dependencies
This file depends on inode allocation/freeing, AGI reads, iunlink item logging, transaction timestamp logging, quota/project id policy, bmap hint validators, and health reporting.

## Research Notes
The most important design point is the two-layer unlinked-list model: persistent AGI singly linked buckets for crash consistency, plus in-core backreferences for scalable removal while the AGI lock serializes updates.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_util.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_util.h

## Role
`xfs_inode_util.h` declares utility interfaces for inode flags, inode creation, inode timestamp logging, unlinked-list operations, link count updates, and inode uninitialization.

## Main Definitions
- `struct xfs_icreate_args` carries inode creation context: idmap, parent inode, device number, mode, and creation flags.
- Creation flags distinguish tmpfile creation, immediate xattr initialization, and inodes that can never be linked into the directory tree.
- `XFS_ICHGTIME_*` flags select which inode timestamps `xfs_trans_ichgtime` should update.

## Exported API
- Flag conversion: `xfs_flags2diflags`, `xfs_flags2diflags2`, `xfs_dic2xflags`, and `xfs_ip2xflags`.
- Creation/lifecycle: `xfs_inode_init` and `xfs_inode_uninit`.
- Project id inheritance: `xfs_get_initial_prid`.
- Unlinked/link operations: `xfs_iunlink`, `xfs_iunlink_remove`, `xfs_droplink`, and `xfs_bumplink`.
- Timestamp logging: `xfs_trans_ichgtime`.

## Dependencies
The header is consumed by inode allocation, create/link/unlink paths, metadata directory creation, and transaction code.

## Research Notes
This header is the call contract for creating and retiring inodes. Its creation arguments are intentionally explicit about idmapped ownership and detached/tree-root cases.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_log_format.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_log_format.h

## Role
`xfs_log_format.h` defines the on-disk journal format for XFS: physical log record headers, transaction headers, log item type codes, and per-item format structures used by log writing and recovery.

## Main Format Areas
- Physical log constants define iclog counts, record sizes, log versions, header sizes, cycle fields, and LSN helpers.
- `struct xlog_rec_header` and `struct xlog_rec_ext_header` define physical log record headers, CRC fields, cycle data, format identifiers, filesystem UUID, and log v2 size fields.
- `struct xlog_op_header` defines per-region operation headers and continuation/commit/unmount flags.
- `struct xfs_trans_header` identifies checkpoint transactions and item counts.
- `XFS_LI_*` constants enumerate all log item types, including inode, buffer, dquot, quotaoff, icreate, extent free, rmap, refcount, bmap, attr, exchange-map, and realtime intent/done pairs.

## Log Item Structures
- `struct xfs_inode_log_format` and `_32` describe logged inode items, fork data sizes, inode location, and special device data.
- `struct xfs_log_dinode` mirrors `struct xfs_dinode` in host CPU format for journaled inode cores.
- `struct xfs_buf_log_format` records buffer identity, flags, length, and dirty 128-byte chunk bitmap.
- EFI/EFD structures log extent free intents and completions, with 32-bit and 64-bit compatibility extent layouts.
- RUI/RUD structures log reverse mapping operations using `struct xfs_map_extent`.
- CUI/CUD structures log refcount updates using `struct xfs_phys_extent`.
- BUI/BUD structures log bmap updates.
- XMI/XMD structures log file mapping exchange operations and completion.
- Dquot and quotaoff structures log quota metadata updates and quota-off sequencing.
- `struct xfs_icreate_log` logs inode chunk initialization.
- ATTRI/ATTRD structures log deferred attr and parent-pointer attr operations.

## Flags and Helpers
- `XFS_ILOG_*` flags identify which inode core/fork/device fields are logged; timestamp and iversion flags are in-memory-only.
- Buffer log flags identify inode buffers, canceled buffers, dquot buffers, and buffer type magic-offset classes.
- Intent flag masks define allowed rmap, bmap, refcount, exchange-map, and attr operation bits.
- `xfs_*_log_format_sizeof` helpers compute variable-length log item sizes.

## Data and Invariants
- Many structures are part of the persistent log ABI and cannot be reordered without recovery changes.
- Some log items carry host-order data for historical reasons; recovery code must decode compatibility variants.
- Physical log record checksum sizing has i386 compatibility handling through `XLOG_REC_SIZE` and `XLOG_REC_SIZE_OTHER`.
- Buffer dirty maps use explicit padding rules so 32-bit and 64-bit structure sizes remain consistent.
- Parent pointer attr operations reuse attr intent records with dedicated PPTR operation codes and old/new name length handling.

## Dependencies
This header is included by most XFS log, transaction, recovery, inode, quota, bmap, attr, and deferred-operation code. It is also checked by `xfs_ondisk.h`.

## Research Notes
This is an ABI file, not merely an internal header. Its central constraint is compatibility with existing logs across architectures and kernel versions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_log_format.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_log_recover.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_log_recover.h

## Role
`xfs_log_recover.h` declares internal log recovery structures, item recovery operation hooks, recovered transaction state, buffer cancellation helpers, and intent recovery interfaces.

## Main Definitions
- `enum xlog_recover_reorder` classifies recovered items into buffer, generic item, inode buffer, or cancel lists for correct replay ordering.
- `struct xlog_recover_item_ops` is the per-log-item recovery vtable: item type, reorder hook, pass2 readahead, pass1 commit, and pass2 commit.
- `struct xlog_recover_item` stores recovered log item regions, operation hooks, and list linkage.
- `struct xlog_recover` tracks one recovered transaction, including transaction id, header, LSN, and recovered item queue.
- `XLOG_RHASH_*` defines the recovered transaction hash table layout.
- `XLOG_MAX_REGIONS_IN_ITEM` bounds region counts from the buffer dirty bitmap format.

## Exported Recovery Hooks
- Declares recovery ops for icreate, buffer, inode, dquot, quotaoff, bmap, extent free, rmap, refcount, attr, exchange-map, and realtime intent/done item types.
- Provides buffer readahead and cancellation table helpers.
- Provides inode lookup helpers for recovery by inode number and optional generation.
- Provides intent release, intent item reconstruction, and intent finish functions.

## Important Helper
- `xlog_recover_resv` converts a normal transaction reservation into a recovery reservation by keeping logres/logflags but forcing `tr_logcount = 1`, avoiding grant-space livelock while recovered intents pin the log tail.

## Dependencies
This header ties log recovery to deferred operation types, transaction reservations, in-core log items, buffer replay, inode cache lookup, and AIL intent item lifecycle.

## Research Notes
The key concept is two-pass recovery with per-item hooks. Intent items are reconstructed into in-core log items, paired done items release them, and unfinished intents are replayed through deferred operation recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_log_recover.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_log_rlimit.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_log_rlimit.c

## Role
`xfs_log_rlimit.c` calculates the maximum transaction reservation relevant to minimum log sizing and derives the minimum legal XFS log size for a filesystem configuration.

## Main Responsibilities
- Preserve historical minimum log size behavior for older feature sets, even when old reservation formulas overestimated requirements.
- Enable corrected minimum-log calculations only for sufficiently new feature combinations, specifically v5 filesystems with parent pointers.
- Compute the worst-case local attr set transaction space.
- Build alternate transaction reservation tables for minimum log size calculations.
- Choose the largest transaction reservation and convert it into minimum log blocks.

## Important Functions
- `xfs_want_minlogsize_fixes` checks the superblock directly for v5 plus parent-pointer incompat feature because this code can run before mount feature flags are fully established.
- `xfs_log_calc_max_attrsetm_res` estimates maximum logged local attr value space and conditionally fixes an older unit conversion overestimate.
- `xfs_log_calc_trans_resv_for_minlogblocks` either uses current reservation calculations or deliberately recreates historical rmap/reflink reservation behavior for compatibility.
- `xfs_log_get_max_trans_res` scans a temporary reservation table and returns the largest effective reservation, comparing attrset worst case separately.
- `xfs_log_calc_minimum_size` turns the largest reservation into filesystem blocks, accounting for log v2 stripe unit padding and the `XFS_MIN_LOG_FACTOR`.

## Data and Invariants
- Minimum log size cannot be reduced for older feature sets because newer mkfs output must remain mountable on older kernels.
- For striped logs, two log stripe units are considered per transaction reservation because both transaction data and commit records can need padding.
- The minimum size uses a factor of three so at least two maximally sized transactions can fit with headroom.

## Dependencies
This file depends on transaction reservation calculation, DA attr geometry, bmap btree reservation helpers, mount/superblock feature checks, and tracepoints.

## Research Notes
This file intentionally contains compatibility math. Some calculations are known historical overestimates, but preserving mount compatibility takes precedence unless the filesystem has a new enough feature gate.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_log_rlimit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metadir.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metadir.c

## Role
`xfs_metadir.c` implements the metadata directory abstraction for looking up, creating, linking, committing, and canceling metadata inode updates inside the special XFS metadata directory tree.

## Main Responsibilities
- Convert metadata path components into `struct xfs_name`.
- Look up metadata directory entries with directory btree/shortform machinery and verify inode/filetype results.
- Load metadata inodes by path and metatype.
- Allocate transaction and parent-pointer context for metadata directory creation/link operations.
- Create metadata files/directories and insert directory entries.
- Commit or cancel metadata directory updates while releasing locks and parent pointer resources.
- Provide a convenience mkdir wrapper for one metadata directory path component.

## Important Functions
- `xfs_metadir_lookup` performs a locked directory lookup, verifies the parent is a directory, validates returned inode number and requested file type, and marks metadata directory health sick on corruption.
- `xfs_metadir_load` looks up a path component under a metadata directory and reads it through `xfs_trans_metafile_iget`.
- `xfs_metadir_start_create` allocates parent pointer context and a create transaction, then locks the parent directory.
- `xfs_metadir_create` checks nonexistence, allocates and creates the inode, sets metadata inode flags, joins the parent directory after possible transaction roll, and creates the directory entry.
- `xfs_metadir_start_link` and `xfs_metadir_link` support userspace-only linking of an existing metadata inode into the tree.
- `xfs_metadir_commit` commits the transaction and tears down locks/resources.
- `xfs_metadir_cancel` cancels the transaction and tears down locks/resources.
- `xfs_metadir_mkdir` creates a metadata subdirectory and handles inode setup/release on commit or failure.

## Data and Invariants
- All metadata directory tree operations require the metadir feature.
- Callers synchronize metadata directory inodes with ILOCK; IOLOCK/MMAPLOCK are unnecessary because metadata inodes are not user visible.
- New metadata inodes get `XFS_DIFLAG2_METADATA` and mandatory metadata flags immediately after creation.
- The path parameter is a single metadata directory component in these helpers; ancestor directories must already exist.
- Metadata directory files are not quota-accounted.

## Error Handling and Corruption Response
- Non-directory metadata parents, invalid lookup inode numbers, and filetype mismatches mark filesystem metadata directory health sick and return `-EFSCORRUPTED`.
- Creation can return an inode even on later error; callers must finish inode setup before releasing it so cleanup can proceed correctly.
- Cancel/commit teardown frees parent pointer args and unlocks any locked parent/child inode.

## Dependencies
This file depends on directory lookup/create helpers, parent pointer update setup, inode allocation/create, metadata file flagging, transaction reservations, health reporting, and metadir feature checks.

## Research Notes
This is an abstraction layer for new metadata inodes, excluding legacy realtime bitmap/summary and quota inodes. The update object centralizes parent inode, child inode, transaction, parent-pointer args, metatype, and lock state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metadir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metadir.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metadir.h

## Role
`xfs_metadir.h` declares the metadata directory update object and APIs for loading, creating, linking, committing, canceling, and making metadata directory entries.

## Main Definition
- `struct xfs_metadir_update` stores the metadata parent directory, path component, parent pointer args, child inode, transaction, metadata file type, and lock-state bits.

## Exported API
- Lookup/load: `xfs_metadir_load`.
- Create workflow: `xfs_metadir_start_create` and `xfs_metadir_create`.
- Link workflow: `xfs_metadir_start_link` and `xfs_metadir_link`.
- Transaction completion: `xfs_metadir_commit` and `xfs_metadir_cancel`.
- Convenience directory creation: `xfs_metadir_mkdir`.

## Dependencies
The header depends on inode, transaction, parent pointer, and metadata file type definitions from surrounding XFS headers.

## Research Notes
This header models metadata directory mutations as explicit begin/change/commit-or-cancel workflows so callers can finish inode-specific initialization before releasing resources.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metadir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metafile.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metafile.c

## Role
`xfs_metafile.c` manages metadata inode identity flags and block reservations for metadata files, particularly realtime rmap and realtime refcount btree metadata files stored in the metadata directory tree.

## Main Responsibilities
- Map metadata file type enum values to string names.
- Set and clear metadata inode flags and update active/metafile inode statistics.
- Determine whether metadata file block reservations are critically low.
- Charge allocations against metadata file reservation pools and update superblock/free block counters.
- Return freed metadata file space to the reservation or filesystem free space.
- Initialize and release mount-wide metadata file reservations.

## Important Functions
- `xfs_metafile_type_str` returns the string name for a metadata file type.
- `xfs_metafile_set_iflag` clears permissions, sets root uid/gid, applies mandatory metadata file or directory flags, clears DAX, sets `XFS_DIFLAG2_METADATA`, records metatype, logs the inode, and moves stats from active to metadata.
- `xfs_metafile_clear_iflag` clears the metadata flag on zero-link metadata inodes and reverses stats.
- `xfs_metafile_resv_critical` reports low reservation when available reserved/free space cannot cover max btree height or 10% of target reservation.
- `xfs_metafile_resv_alloc_space` consumes reservation first, then free blocks or transaction reservation, updates reservation accounting, increments `i_nblocks`, and logs the inode.
- `xfs_metafile_resv_free_space` decrements `i_nblocks`, returns blocks to reservation up to target, and sends remaining blocks to filesystem free space.
- `xfs_metafile_resv_init` computes used and target reservation for realtime rmap/refcount btrees across realtime groups, hides unused reserved space from fdblocks, and records reservation state.
- `xfs_metafile_resv_free` releases unused reservation back to filesystem free blocks.

## Data and Invariants
- Metadata files must be marked with `XFS_DIFLAG2_METADATA` and mandatory immutable/sync/noatime/nodump/nodefrag flags; metadata directories also require nosymlinks.
- Reservation accounting uses `m_metafile_resv_lock` to protect target/used/available counters.
- Reserved but unused metadata file space is hidden from normal free block accounting.
- Reservation target is bounded by current used blocks and at most one quarter of data blocks.

## Error Handling and Risks
- Reservation initialization can fail if free block reservation cannot hide the target space.
- Allocations beyond metadata reservation are expected only for rmap btree overruns and are charged carefully to either in-core or transaction counters.
- Critical-reservation checks include an error tag injection path.

## Dependencies
This file depends on realtime group iteration, realtime rmap/refcount btree reserve calculators, allocation args, transaction superblock accounting, inode logging, mount free counters, and metadata feature predicates.

## Research Notes
This file is the reservation/accounting side of metadata files. It keeps metadata btree growth from consuming all normal free space while still allowing controlled overruns for realtime metadata needs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metafile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metafile.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metafile.h

## Role
`xfs_metafile.h` declares metadata file flag policy, metadata inode flag setters, metadata reservation APIs, and external metadata inode lookup hooks.

## Main Definitions
- `XFS_METAFILE_DIFLAGS` lists mandatory flags for metadata files: immutable, sync, noatime, nodump, and nodefrag.
- `XFS_METADIR_DIFLAGS` extends metadata file flags with nosymlinks for metadata directories.

## Exported API
- Metadata type names: `xfs_metafile_type_str`.
- Flag manipulation: `xfs_metafile_set_iflag` and `xfs_metafile_clear_iflag`.
- Reservation management: `xfs_metafile_resv_critical`, `xfs_metafile_resv_alloc_space`, `xfs_metafile_resv_free_space`, `xfs_metafile_resv_free`, and `xfs_metafile_resv_init`.
- Environment-provided inode lookup: `xfs_trans_metafile_iget` and `xfs_metafile_iget`.

## Dependencies
The header is shared by kernel and userspace libxfs builds; lookup functions are intentionally supplied externally for environment-specific inode handling.

## Research Notes
This header codifies the rule that metadata files are real inodes but must be hidden and protected by mandatory inode flags and separate reservation accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_metafile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ondisk.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ondisk.h

## Role
`xfs_ondisk.h` performs compile-time assertions for XFS on-disk and UAPI structure sizes, member offsets, and constant values. It protects persistent metadata, journal formats, ioctl ABI, and compatibility layout assumptions from accidental C structure drift.

## Main Responsibilities
- Define assertion helpers for structure size, member offset, constant value, and matching superblock offsets in disk and in-core superblock structures.
- Check file metadata structures such as dinodes, bmbt records, dquots, symlink headers, and timestamps.
- Check AG and btree structures for allocation, inode, refcount, rmap, and realtime btrees.
- Check directory and attribute v2/v3 layout structures and shared prefix offsets.
- Check log item structures and physical log record headers.
- Check parent pointer ioctl and general XFS ioctl UABI structures.
- Check superblock field offsets, including newer metadir and realtime group fields.
- Check bigtime and quota bigtime conversion boundary constants.

## Data and Invariants
- v5 structures must preserve v4-compatible magic/header offsets at the start of metadata blocks.
- Some historically architecture-sensitive structures are checked through explicit 32-bit and 64-bit variants.
- Some structures are intentionally omitted where architecture-dependent padding or legacy layout makes exact checks unsuitable.
- Parent pointer record size is fixed at 12 bytes.
- Log structures such as inode log format, attr intent, exchange mapping intent, and physical record headers have fixed sizes.

## Dependencies
This header depends on all relevant XFS on-disk format headers being included before `xfs_check_ondisk_structs` is compiled. It is normally used during initialization/build validation.

## Research Notes
This file is a layout tripwire. It contains no operational filesystem logic, but it is essential for preventing silent ABI or disk-format breakage from structure edits.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ondisk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_parent.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_parent.c

## Role
`xfs_parent.c` implements XFS parent pointer attribute handling. Parent pointers are stored as special local xattrs whose name is the directory entry name and whose value is `struct xfs_parent_rec` containing parent inode number and generation.

## Main Responsibilities
- Validate parent pointer attribute names and values.
- Compute parent pointer attr hashes using directory name hash mixed with parent inode number.
- Initialize `xfs_da_args` for parent pointer xattr operations.
- Add, remove, and replace parent pointers during directory entry create/unlink/rename.
- Decode parent pointer information from raw xattr name/value pairs.
- Provide lookup, set, and unset helpers for repair code.

## Important Functions
- `xfs_parent_namecheck` rejects incomplete attrs and validates the name as a directory component.
- `xfs_parent_valuecheck` requires the parent feature, exact `xfs_parent_rec` value length, local value presence, and valid parent directory inode number.
- `xfs_parent_hashval` uses normal directory hash plus upper/lower parent inode bits to reduce hardlink collisions.
- `xfs_parent_hashattr` derives the same hash from xattr name/value components.
- `xfs_parent_da_args_init` sets up attr fork, parent attr filter, logged operation flags, owner, name, value, and hash.
- `xfs_parent_iread_extents` verifies that the attr fork exists and reads attr fork extents before parent operations.
- `xfs_parent_addname`, `xfs_parent_removename`, and `xfs_parent_replacename` wrap logged attr set/remove/replace operations for directory changes.
- `xfs_parent_from_attr` validates and extracts parent inode/generation from a raw parent xattr.
- `xfs_parent_lookup` looks up a specific parent pointer while caller holds ILOCK.
- `xfs_parent_set` and `xfs_parent_unset` perform immediate non-transaction repair-oriented create/remove operations after sanity checking.

## Data and Invariants
- Parent pointer values are always local xattr values because `xfs_parent_rec` is only 12 bytes.
- Parent pointer updates always use logged operations; incomplete parent attrs are invalid.
- Parent-pointer-enabled files must have an attr fork, which inode creation pre-creates for linkable files.
- Parent pointer attr owner is generally the child inode.
- The parent generation is included in the value so stale parent inode reuse can be detected.

## Error Handling and Corruption Response
- Missing attr fork on a parent-pointer filesystem marks the inode parent metadata sick and returns `-EFSCORRUPTED`.
- Invalid raw parent attrs return `-EFSCORRUPTED`.
- Repair set/unset helpers assert and reject invalid name/value pairs before changing xattrs.

## Dependencies
This file depends on attr set/remove/replace/get machinery, DA attr geometry, directory name validation and hashing, transaction/deferred attr logging, inode fork extent loading, and parent pointer feature checks.

## Research Notes
Parent pointers deliberately reuse the xattr/DA infrastructure but impose stricter invariants: logged-only operations, local fixed-size values, directory-name-compatible names, and hashes mixed with parent inode numbers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_parent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_parent.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_parent.h

## Role
`xfs_parent.h` declares parent pointer validation, hashing, update, decode, lookup, and repair interfaces, plus the parent pointer operation context object.

## Main Definitions
- `xfs_parent_rec_init` initializes an on-disk parent record from inode number and generation.
- `xfs_inode_to_parent_rec` builds a parent record from a directory inode.
- `struct xfs_parent_args` carries old parent record, new parent record, and embedded `xfs_da_args` for deferred/logged attr update machinery.
- `xfs_parent_start` allocates a parent args object only when the parent pointer feature is enabled.
- `xfs_parent_finish` frees that object when present.

## Exported API
- Validators and hashing: `xfs_parent_namecheck`, `xfs_parent_valuecheck`, `xfs_parent_hashval`, and `xfs_parent_hashattr`.
- Directory operation hooks: `xfs_parent_addname`, `xfs_parent_removename`, and `xfs_parent_replacename`.
- Raw attr decode: `xfs_parent_from_attr`.
- Repair helpers: `xfs_parent_lookup`, `xfs_parent_set`, and `xfs_parent_unset`.

## Dependencies
The header depends on `struct xfs_parent_rec` from on-disk DA format definitions, attr/DA args, mount feature checks, inode generation access, and the parent args slab cache.

## Research Notes
This header makes parent pointer updates optional at runtime: callers can always call `xfs_parent_start`, and non-parent filesystems simply receive a null context.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_parent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_quota_defs.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_quota_defs.h

## Role
`xfs_quota_defs.h` provides quota constants, flags, reservation sizing, option masks, quota state predicates, dquot verification declarations, quota timestamp conversion declarations, and metadata-directory quota inode helpers shared by kernel and userspace XFS code.

## Main Definitions
- `xfs_qcnt_t` is a 64-bit quota counter/limit type.
- `xfs_dqtype_t` identifies user, project, group, and bigtime quota-related types.
- `XFS_DQUOT_LOGRES` estimates log reservation for worst-case dquot updates, including up to six dquots plus log format items.
- `XFS_IS_*QUOTA_*` macros test accounting and enforcement bits in mount quota flags.
- `XFS_QMOPT_*` flags select quota types, forced reservations, superblock version changes, reserved/actual block and inode counter fields, delayed counters, realtime counters, and inherited dquot behavior.
- `XFS_TRANS_DQ_*` aliases map transaction dquot modification operations to quota option bits.
- `xfs_dqinode_path` maps dquot type to metadata directory path names.
- `xfs_dqinode_metafile_type` maps dquot type to metadata file type enum values.

## Exported API
- Dquot integrity and repair: `xfs_dquot_verify`, `xfs_dqblk_verify`, `xfs_calc_dquots_per_chunk`, and `xfs_dqblk_repair`.
- Bigtime quota expiry conversion: `xfs_dquot_from_disk_ts` and `xfs_dquot_to_disk_ts`.
- Quota inode health and metadir support: `xfs_dqinode_sick_mask`, `xfs_dqinode_load`, `xfs_dqinode_metadir_create`, `xfs_dqinode_metadir_link`, `xfs_dqinode_mkdir_parent`, and `xfs_dqinode_load_parent`.

## Data and Invariants
- User, group, and project quotas can all be active simultaneously, so reservations must account for multi-dquot updates.
- Group and project quota flags retain historical “other quota” conversion constraints handled by superblock qflags conversion code, not here.
- `XFS_QMOPT_*` values are not persistent ABI values and may change between versions.
- Metadata directory quota inode helpers map quota files into named metadata files: `user`, `group`, and `project`.

## Dependencies
This header depends on dquot disk structures, log dquot format, mount quota flags from log format definitions, metadata file type definitions, and quota inode implementation elsewhere.

## Research Notes
Despite the filename, this header includes more than constants: it is the shared quota operation vocabulary for transaction accounting, metadata quota inode discovery, and dquot verification.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_quota_defs.h -->