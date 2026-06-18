# Group Research: group_1881_xfsprogs_sources_local_fs_xfsprogs_libxfs_xfs_iext_tree_c_sources_l_2797853067a0

Scope: `Docs/research_subset_a.md` only. Files read completely: `sources/local-fs/xfsprogs/libxfs/xfs_iext_tree.c`, `sources/local-fs/xfsprogs/libxfs/xfs_inode_buf.c`, `sources/local-fs/xfsprogs/libxfs/xfs_inode_buf.h`, `sources/local-fs/xfsprogs/libxfs/xfs_inode_fork.c`, `sources/local-fs/xfsprogs/libxfs/xfs_inode_fork.h`, `sources/local-fs/xfsprogs/libxfs/xfs_inode_util.c`, `sources/local-fs/xfsprogs/libxfs/xfs_inode_util.h`, `sources/local-fs/xfsprogs/libxfs/xfs_log_format.h`, `sources/local-fs/xfsprogs/libxfs/xfs_log_recover.h`, `sources/local-fs/xfsprogs/libxfs/xfs_log_rlimit.c`, `sources/local-fs/xfsprogs/libxfs/xfs_metadir.c`, `sources/local-fs/xfsprogs/libxfs/xfs_metadir.h`, `sources/local-fs/xfsprogs/libxfs/xfs_metafile.c`, `sources/local-fs/xfsprogs/libxfs/xfs_metafile.h`, `sources/local-fs/xfsprogs/libxfs/xfs_ondisk.h`, `sources/local-fs/xfsprogs/libxfs/xfs_parent.c`, `sources/local-fs/xfsprogs/libxfs/xfs_parent.h`, `sources/local-fs/xfsprogs/libxfs/xfs_platform.h`, and `sources/local-fs/xfsprogs/libxfs/xfs_quota_defs.h`.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_iext_tree.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_iext_tree.c

## Role

This file implements XFS's in-core inode extent tree for `libxfs`. It stores `xfs_bmbt_irec` mappings in a compact 128-bit in-memory record format and provides cursor-based insertion, removal, lookup, update, iteration, and destruction for inode forks.

It is the data structure behind the incore extent lists used by data, attribute, and CoW forks. The on-disk mapping format is still the bmap extent or btree format; this file is only the in-memory search/update structure.

## Main Structures

- `struct xfs_iext_rec` packs start offset, block count, start block, and unwritten state into two 64-bit words.
- `struct xfs_iext_leaf` stores packed extent records and links neighboring leaves with `prev` / `next`.
- `struct xfs_iext_node` stores lookup keys and child pointers for internal levels.
- `struct xfs_iext_cursor` points to a leaf and record position.

The tree uses fixed 256-byte nodes. Height zero means empty. Height one means the root is a leaf-like record array. Larger heights use internal nodes above linked leaves.

## Core Operations

- `xfs_iext_count` returns extent count from fork byte count.
- `xfs_iext_first`, `xfs_iext_last`, `xfs_iext_next`, and `xfs_iext_prev` implement ordered cursor movement.
- `xfs_iext_lookup_extent` finds the extent covering an offset, or the first extent after it.
- `xfs_iext_lookup_extent_before` finds the last extent before an end offset.
- `xfs_iext_get_extent` expands the cursor record into `xfs_bmbt_irec`.
- `xfs_iext_insert_raw` inserts a record into a fork extent tree.
- `xfs_iext_insert` wraps raw insert with inode/fork-state selection and tracing.
- `xfs_iext_remove` deletes the cursor record and rebalances/free nodes as needed.
- `xfs_iext_update_extent` overwrites a cursor record and updates parent keys if the start offset changes.
- `xfs_iext_destroy` recursively frees the tree and resets the fork.

## Tree Mutation Details

Insertion grows an empty fork into a root, reallocates a height-one root as it grows, splits full leaves, and propagates new leaf keys into parent nodes. Sequential appends get a fast split path that spills into a new node without copying half the old contents.

Removal shifts records left, clears the last record, decrements `if_bytes`, updates parent keys when the first record changes, and merges underfull leaves or internal nodes when possible. A root with one child collapses down a level.

## Invariants

- An empty record is detected by `hi == 0`; valid extents cannot have zero length.
- Parent keys track the first start offset under each child.
- Cursor validity depends on both bounds and non-empty records.
- The fork sequence counter is incremented before extent tree mutations so CoW/writeback code can notice changes.
- The compact record layout assumes bmap field bit widths: 54-bit file offset, 21-bit block count, 52-bit startblock, and one unwritten bit.
- Memory allocation uses no-fail kernel-style allocation wrappers in userspace.

## Dependencies

This file depends on `xfs_ifork`, `xfs_bmbt_irec`, bmap fork state flags, tracing hooks, statistics, and basic XFS bit masks. Higher-level mapping code in `xfs_bmap.c` relies on this tree for all in-core extent cache mutations.

## Research Notes

The most important correctness risk is keeping parent keys, leaf links, cursor position, and `if_bytes` synchronized during splits, merges, and first-record updates. This file intentionally avoids on-disk accounting; callers must separately update fork extent counts, transaction logging, quota, rmap, and btree state.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_iext_tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_inode_buf.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_inode_buf.c

## Role

This file verifies inode buffers, maps inode locations to buffers, converts dinodes between on-disk and incore forms, calculates inode CRCs, and validates inode core metadata. It is the main libxfs bridge between raw `struct xfs_dinode` storage and `struct xfs_inode`.

## Inode Buffer Verification

`xfs_inode_buf_verify` checks every dinode in an inode buffer for:

- correct inode magic
- supported inode version
- valid `di_next_unlinked` AG inode pointer

Read verification reports corruption through the buffer verifier. Readahead verification treats invalid buffers as failed readahead by clearing `XBF_DONE` and setting `-EIO`, avoiding noisy recovery-time warnings.

Exports:

- `xfs_inode_buf_ops`
- `xfs_inode_buf_ra_ops`
- `xfs_imap_to_bp`

`xfs_imap_to_bp` reads the buffer containing a mapped inode and marks the AG inode metadata sick if metadata errors are detected.

## Disk To Incore Conversion

`xfs_inode_from_disk` validates the dinode with `xfs_dinode_verify`, loads permanent inode fields, and returns early for unused inodes. It handles:

- v1 inode link count compatibility
- uid/gid/project id
- legacy and bigtime timestamps
- size, blocks, extsize, fork offset, flags, unlinked pointer
- v3 fields including change count, creation time, flags2, CoW extent size, and large extent count union
- data fork and optional attr fork formatting
- CoW fork creation for reflink inodes
- metadata inode statistics adjustment

On attr fork formatting failure it destroys the already loaded data fork.

## Incore To Disk Conversion

`xfs_inode_to_disk` writes incore inode fields into a dinode, choosing v2 or v3 format from mount features. It writes the metatype only for metadata inodes, converts timestamps, stores fork formats, extent counters, flags, ids, link count, generation, device fields via fork flush, and v3 UUID/LSN/CRC-related fields.

`xfs_inode_to_disk_iext_counters` chooses normal or large extent counter fields and clears padding during upgrades.

`xfs_dinode_calc_crc` computes the v3 inode checksum over the full inode size.

## Dinode Validation

`xfs_dinode_verify` is the central inode verifier. It checks:

- magic, version, CRC, inode number, and metadata UUID
- metatype rules for v2/v3 and metadata inodes
- nonnegative file size
- mode-to-filetype validity
- zero-length symlink/directory rules for linked inodes
- large extent counter feature and padding
- extent counts versus block count
- directory max extents
- fork offset placement
- realtime flag availability
- data and attr fork formats
- extsize and cowextsize hints
- reflink feature and inode mode restrictions
- realtime/reflink compatibility
- bigtime feature compatibility
- metadata inode rules
- nonzero block counts with zero extents, except metadata btree forks

`xfs_dinode_verify_fork` validates local, extents, btree, and metadata-btree fork formats. Metadata btree forks are limited to supported metadir metafile types such as realtime rmap and realtime refcount metadata.

`xfs_dinode_verify_metadir` enforces metadata inode constraints: v3 only, valid metatype, directory or regular file only, zero permissions, zero uid/gid, no DMAPI state, mandatory immutable/sync/noatime/nodump/nodefrag flags, directory no-symlinks flag, and no DAX.

## Hint Validators

`xfs_inode_validate_extsize` validates data extent size hints for directories and regular files, including flag/mode compatibility, nonzero hints when flags are set, block or realtime extent alignment, max bmbt length, and AG half-size limits.

`xfs_inode_validate_cowextsize` validates CoW extent size hints similarly, requiring reflink support when the flag is set. Both validators preserve historic leniency around directory hints that may become realtime-alignment-invalid after adding a realtime device.

## Dependencies

This file coordinates with inode fork formatting, bmap extent validation, metadata health marking, transaction buffer reads, directory geometry, superblock feature predicates, metadir/metafile support, and timestamp conversion helpers.

## Research Notes

This file is the authoritative dinode policy gate. Changes to inode feature bits, fork formats, metadata inode types, timestamp encodings, or extent counters must be reflected here or filesystems may be incorrectly accepted, rejected, or written in a format older kernels cannot understand.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_inode_buf.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_inode_buf.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_inode_buf.h

## Role

This header declares inode buffer mapping, dinode verification, disk/incore conversion, CRC, timestamp, and extent-size validation interfaces.

## Main Contents

- `struct xfs_imap` records an inode chunk disk address, length, and byte offset.
- `xfs_imap_to_bp` reads the buffer containing a mapped inode.
- `xfs_dinode_calc_crc` updates a v3 dinode checksum.
- `xfs_inode_to_disk` and `xfs_inode_from_disk` convert between incore inode and on-disk dinode.
- `xfs_dinode_verify` and `xfs_dinode_verify_metadir` validate inode metadata.
- `xfs_inode_validate_extsize` and `xfs_inode_validate_cowextsize` validate allocation hint fields.
- `xfs_inode_encode_bigtime` encodes an incore timestamp into XFS bigtime units.
- `xfs_inode_from_disk_ts` decodes a dinode timestamp.
- `xfs_dinode_good_version` accepts v3 only for v3 inode filesystems, otherwise v1/v2.

## Dependencies

The header exposes types from mount, inode, dinode, timestamp, and buffer code. It is consumed by inode loading, inode flushing, repair, mkfs, and verifier code.

## Research Notes

This is a narrow public contract for inode core serialization and verification. The inline version rule is important because inode buffer verification uses it before deeper dinode validation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_inode_buf.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_inode_fork.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_inode_fork.c

## Role

This file manages incore inode fork contents. It formats data and attribute forks from dinodes, manages local fork data and btree roots, serializes fork contents back to dinodes during flush, initializes CoW forks, verifies shortform fork contents, handles large extent counter upgrades, and answers fork placement questions.

## Fork Formatting

`xfs_iformat_data_fork` initializes the data fork format and extent count, sets `if_needextents` for btree forks with release semantics, then dispatches by inode mode and fork format:

- device modes use `XFS_DINODE_FMT_DEV`
- local regular file data is invalid, but local directories and symlinks are loaded and verified
- extents format is loaded with `xfs_iformat_extents`
- btree format copies the on-disk bmap root with `xfs_iformat_btree`
- metadata-btree format loads special realtime metadata btrees

`xfs_iformat_attr_fork` initializes the attr fork and handles local shortform xattrs, extents, or btree roots. Invalid attr formats mark the inode sick and reset the attr fork.

## Local And Extent Loading

`xfs_init_local_fork` copies inline data into memory. Symlink data is overallocated by one byte and NUL-terminated so it can be returned directly to VFS-style callers.

`xfs_iformat_local` bounds-checks inline fork size against available dinode fork space before copying.

`xfs_iformat_extents` validates extent count and byte size, decodes each disk bmbt record, validates it with `xfs_bmap_validate_extent`, inserts it into the incore extent tree, and traces the loaded extent.

`xfs_iformat_btree` validates btree root shape, level, record count, fork space, and extent count before allocating `if_broot` and converting the disk root to incore btree format. Actual extents are read lazily later.

## Memory Management

- `xfs_broot_alloc` allocates an incore btree root.
- `xfs_broot_realloc` resizes or frees the root, using allocate-copy-free when shrinking.
- `xfs_idata_realloc` resizes local fork data and updates `if_bytes`.
- `xfs_idestroy_fork` frees local data, btree roots, and extent trees according to fork format.
- `xfs_ifork_zap_attr` destroys and resets the attr fork.

## Flushing Forks

`xfs_iflush_fork` writes dirty fork contents into the dinode according to the current fork format, with format taking precedence over log flags:

- local data copies `if_data`
- extent format copies non-delalloc extents through `xfs_iextents_copy`
- btree format converts incore btree root to disk bmdr root
- device format writes the device id
- metadata-btree format calls realtime metadata-specific flush helpers

`xfs_iextents_copy` skips delayed allocation records because they are incore only and asserts each written extent validates.

## CoW And Verification

`xfs_ifork_init_cow` allocates and initializes the CoW fork for reflink inodes.

`xfs_ifork_verify_local_data` validates local directory and symlink contents using directory and symlink shortform verifiers.

`xfs_ifork_verify_local_attr` validates shortform attr contents and requires an attr fork.

## Extent Count Limits

`xfs_iext_count_extend` checks whether adding extents would overflow the fork's extent count. If the filesystem supports large extent counters and the inode is not already upgraded, it sets `XFS_DIFLAG2_NREXT64` and logs the inode core. CoW forks are exempt.

`xfs_ifork_is_realtime` reports whether a mapping belongs to the realtime device; attr forks are never realtime.

## Dependencies

This file integrates with bmap btree conversion, incore extent tree APIs, bmap extent validation, shortform dir/attr/symlink verifiers, realtime metadata btree handlers, transaction logging, and inode health reporting.

## Research Notes

The release/acquire pairing around `if_needextents` and fork format is a key concurrency contract shared with `xfs_need_iread_extents`. Another central risk is ensuring delayed allocation extents remain incore-only and are not serialized into the dinode.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_inode_fork.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_inode_fork.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_inode_fork.h

## Role

This header defines the incore inode fork structure and declares fork formatting, flushing, extent tree, local data, CoW fork, and extent count helper APIs.

## Main Data Structure

`struct xfs_ifork` stores:

- `if_bytes` for bytes used by local data or incore extent records
- `if_broot` and `if_broot_bytes` for incore bmap btree roots
- `if_seq` modification counter
- `if_height` and `if_data` for the incore extent tree or local data
- `if_nextents` on-disk extent count
- `if_format` dinode fork format
- `if_needextents` lazy-load flag for btree extent caches

## Extent Count Planning

The header defines worst-case extent count deltas for common operations:

- adding an extent without splitting
- punching a hole
- attr manipulation including remote xattr blocks
- writing into unwritten extents
- ending CoW
- reflink mapping swaps

`xfs_iext_max_nextents` returns fork-specific small or large extent counter limits.

## Fork Helpers

Inline helpers include:

- `XFS_IFORK_MAXEXT` for inline extent capacity
- `xfs_ifork_has_extents`
- `xfs_ifork_nextents`
- `xfs_ifork_format`
- `xfs_dfork_data_extents`
- `xfs_dfork_attr_extents`
- `xfs_dfork_nextents`
- `xfs_need_iread_extents`

The large extent counter helpers choose between old and new dinode counter fields.

## Extent Cursor APIs

The header declares all incore extent tree operations and provides convenience wrappers:

- `xfs_iext_next_extent`
- `xfs_iext_prev_extent`
- `xfs_iext_peek_next_extent`
- `xfs_iext_peek_prev_extent`
- `for_each_xfs_iext`

## Dependencies

This header binds together inode fork state, dinode fork formats, bmap records, btree roots, transaction logging, and extent cursor iteration. It is included by most inode mapping and fork manipulation code.

## Research Notes

`if_bytes` has different meanings depending on fork format, so callers must pair it with `if_format`. The `if_needextents` acquire-load contract is subtle: readers depend on seeing a valid format after observing that lazy extent loading is needed.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_inode_fork.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_inode_util.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_inode_util.c

## Role

This file provides inode utility operations: converting inode flags to/from user-visible xflags, inheriting creation attributes, initializing new inodes, maintaining the AGI unlinked inode list, updating link counts, and uninitializing freed inodes.

## Flag Conversion

- `xfs_flags2diflags` converts `FS_XFLAG_*` into `XFS_DIFLAG_*`, preserving prealloc and applying directory-only or regular-file-only flags appropriately.
- `xfs_flags2diflags2` converts DAX and CoW extent-size xflags while preserving reflink, bigtime, and large extent counter bits.
- `xfs_ip2xflags` converts incore flags back to user xflags and reports `FS_XFLAG_HASATTR` if the attr fork exists.
- `xfs_get_initial_prid` inherits project id when `PROJINHERIT` is set, otherwise uses root project id.

## Inode Creation

`xfs_inode_init` initializes a newly allocated inode from `xfs_icreate_args`. It sets link count, rdev, uid/gid/project ownership, mode, timestamps, version counter, data fork format, inherited flags, optional attr fork, and transaction logging.

Creation logic handles:

- tmpfiles with zero links
- directories with link count 2
- group inheritance with `XFS_MOUNT_GRPID`
- detached/tree-root creation with root ids
- parent-inherited realtime, extsize, project, noatime, nodump, sync, nosymlinks, nodefrag, filestream, DAX, metadata, and CoW extent size flags
- parent pointer filesystems forcing an attr fork unless the inode is explicitly unlinkable
- adding the attr feature bit to the superblock when initializing an attr fork on a filesystem without the attr bit

Inherited extsize and CoW extsize hints are validated after propagation, and invalid hints are cleared instead of propagating broken realtime-alignment state.

## Unlinked List Maintenance

XFS maintains on-disk per-AG unlinked inode hash chains in the AGI. This file adds an incore doubly linked helper model using `i_prev_unlinked` plus cached inode lookup so removal does not have to linearly scan the singly linked on-disk list.

Key functions:

- `xfs_iunlink` inserts a zero-link inode into the AGI unlinked list.
- `xfs_iunlink_insert_inode` validates the bucket head, updates backrefs, logs the inode next pointer, and updates the AGI bucket.
- `xfs_iunlink_remove` removes an inode from the AGI unlinked list.
- `xfs_iunlink_remove_inode` clears the inode's on-disk next pointer, updates the next inode's backref, updates the previous inode or bucket head, and resets incore pointers.
- `xfs_iunlink_update_bucket` logs a changed AGI bucket.
- `xfs_iunlink_update_backref` updates the next cached inode's prev pointer or reports `-ENOLINK` so reload logic can recover it.

The AGI buffer lock serializes list manipulation and enforces lock ordering.

## Link Count Helpers

`xfs_droplink` decrements link count, logs ctime/core changes, pins the count if it would underflow, and moves the inode to the unlinked list when the count reaches zero.

`xfs_bumplink` increments link count, logs changes, and pins the count if it would exceed the XFS maximum.

## Inode Uninitialization

`xfs_inode_uninit` frees an inode from the on-disk inode index, removes it from the unlinked list, frees local-format data still attached to the data fork, clears mode and flags, resets fork format and attr fork state, applies new default v3 flags2, increments generation, and logs the inode core.

The order frees the inode before removing it from the unlinked list to preserve AGI lock ordering consistent with tmpfile creation.

## Dependencies

This file depends on transaction logging, inode allocation/freeing, AGI reads, health marking, bmap/fork structures, mount feature bits, iunlink reload/log helpers, and VFS-style inode ownership helpers supplied by the userspace platform layer.

## Research Notes

The unlinked list code has tight invariants around AGI bucket validity and incore next/prev coherence. Parent pointer support changes creation behavior by requiring early attr fork creation for linkable files, which affects inode fork layout and transaction reservations.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_inode_util.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_inode_util.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_inode_util.h

## Role

This header declares inode utility interfaces for flag conversion, inode creation initialization, timestamp updates, unlinked-list management, link count updates, and inode uninitialization.

## Main Contents

- `xfs_flags2diflags`, `xfs_flags2diflags2`, `xfs_dic2xflags`, and `xfs_ip2xflags` expose flag conversion.
- `struct xfs_icreate_args` describes file creation context: idmap, parent inode, device id, mode, and creation flags.
- Creation flags cover tmpfile creation, immediate xattr initialization, and unlinkable metadata/detached files.
- `XFS_ICHGTIME_*` flags identify which inode timestamps to update.
- `xfs_inode_init` initializes a newly allocated inode.
- `xfs_inode_uninit` prepares an inode for freeing/reuse.
- `xfs_iunlink` and `xfs_iunlink_remove` maintain the AGI unlinked list.
- `xfs_droplink` and `xfs_bumplink` update link counts.

## Dependencies

The creation argument comments clarify that callers must provide idmap context for correct ownership inheritance and can use null parent/idmap for roots or detached metadata inodes.

## Research Notes

This header is the public contract for inode lifecycle helpers used by allocation, directory, unlink, and metadata file code. Parent pointer and unlinkable flags directly affect attr fork creation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_inode_util.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_log_format.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_log_format.h

## Role

This header defines XFS on-disk log record formats and all log item format structures interpreted by recovery. It covers physical log record headers, transaction headers, log item type codes, inode and buffer log formats, deferred intent/done formats, quota log formats, inode creation records, deferred attribute formats, and quota status flags.

## Physical Log Format

The file defines:

- log record size/version constants
- log cycle and LSN helpers
- log clients and unmount record type
- log operation header flags for start, commit, continuation, end, and unmount transactions
- log record host format codes
- `struct xlog_rec_header`
- `struct xlog_rec_ext_header`

The log record header includes magic, cycle, version, length, LSNs, CRC, previous block, operation count, cycle data, format, filesystem UUID, v2 size, compatibility padding, and extension headers. The comments preserve historic i386 checksum compatibility rules.

## Transaction And Item Types

`struct xfs_trans_header` identifies transaction type and item count. CIL-enabled logs use `XFS_TRANS_CHECKPOINT`.

The `XFS_LI_*` constants identify log items for extents, inode unlink, inode, buffers, dquots, quotaoff, inode create, reverse map intents, refcount intents, bmap intents, attr intents, mapping exchange intents, and realtime variants. `XFS_LI_TYPE_DESC` maps them to names.

## Inode Logging

`struct xfs_inode_log_format` describes an inode item in the log, including fields logged, fork data/root sizes, inode number, device id union, inode buffer block, length, and offset. A packed 32-bit compatibility variant is defined.

`XFS_ILOG_*` flags identify logged inode core, data fork local data, data fork extents, data btree root, device, attr local data, attr extents, attr root, replay owner changes, and in-memory-only timestamp/version triggers.

`struct xfs_log_dinode` mirrors `struct xfs_dinode` in host order for logging. It includes legacy and v3 inode fields, large extent counter unions, next-unlinked pointer, CRC/change count/LSN/flags2, CoW or used-blocks union, creation time, inode number, and UUID.

## Buffer Logging

`struct xfs_buf_log_format` describes a logged buffer and a dirty bitmap of 128-byte chunks. Flags identify inode buffers, canceled freed buffers, and dquot buffers.

`enum xfs_blft` stores buffer type information in the upper bits of `blf_flags` so recovery can find magic fields and recompute CRCs after replay. Inline helpers encode and decode that type.

## Deferred Intent Formats

The header defines shared extent payload structures and log formats for:

- EFI/EFD extent free intents and done items, including 32-bit and 64-bit alignment variants
- RUI/RUD reverse mapping intents and done items
- CUI/CUD refcount update intents and done items
- BUI/BUD bmap update intents and done items
- XMI/XMD mapping exchange intents and done items

Flag masks encode operation type in low bits and fork/unwritten/realtime/shared metadata in high bits. Size helper functions compute variable-length intent item sizes.

## Quota And Inode Create Formats

`struct xfs_dq_logformat` logs a dquot location. `struct xfs_qoff_logformat` logs quotaoff operations. The header also defines quota accounting, enforcement, and checked bits stored in mount and superblock quota flags.

`struct xfs_icreate_log` records inode chunk initialization during inode allocation.

## Attribute Intent Format

The file defines deferred attr operation flags for set, remove, replace, and parent pointer set/remove/replace. `XFS_ATTRI_FILTER_MASK` limits persisted attr filter bits. `struct xfs_attri_log_format` records attr operation id, inode, generation for parent pointer ops, operation flags, name lengths, value length, and filter. `struct xfs_attrd_log_format` completes the intent.

## Invariants

- Many log item structures require the first fields to be type and size fitting in 32 bits because recovery relies on that.
- Structures are append-only from a format compatibility perspective.
- Several logged structures carry host-order fields for historical reasons.
- Variable-length intent records require exact size calculations for recovery parsing.
- Inode log dinode must remain layout-compatible with the dinode core definition except endianness annotations.

## Dependencies

This header is consumed by transaction logging, log recovery, inode flushing, buffer item logging, deferred operation recovery, quota code, and on-disk layout checks.

## Research Notes

This is a format contract, not just a local header. Any structure size, offset, flag, or type-code change affects recovery compatibility and must be mirrored in layout assertions and replay code.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_log_format.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_log_recover.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_log_recover.h

## Role

This header defines internal interfaces and structures for XFS log recovery. It binds recovered log item types to per-type recovery operations and declares helpers for recovery item ordering, readahead, inode lookup, intent handling, and buffer cancellation tables.

## Main Structures

`enum xlog_recover_reorder` classifies recovered items into replay queues:

- normal buffer list
- normal item list
- inode buffer list
- cancel list

`struct xlog_recover_item_ops` supplies per-log-item recovery behavior:

- item type code
- optional reorder callback
- optional pass2 readahead callback
- optional pass1 commit callback
- pass2 commit callback

The pass2 comments define intent/done recovery semantics: intent items reconstruct incore intent log items in the AIL with one reference; done items find and release corresponding intents.

`struct xlog_recover_item` stores recovered regions and the item ops. `struct xlog_recover` stores partial transaction reconstruction state.

## Declared Recovery Items

The header declares ops for icreate, buffer, inode, dquot, quotaoff, bmap, extent free, rmap, refcount, attr, mapping exchange, and realtime variants.

## Helpers And Constants

- `XLOG_RHASH_*` constants hash transaction ids.
- `XLOG_MAX_REGIONS_IN_ITEM` derives a maximum from block size and buffer log chunking.
- `ITEM_TYPE` extracts the item type from the first region.
- Recovery pass constants identify CRC, pass1, and pass2 stages.
- `xlog_recover_resv` transforms normal transaction reservations into single-step intent recovery reservations by forcing `tr_logcount = 1`.

## Dependencies

Recovery uses `struct xlog`, transactions, inode lookup, defer operation types, log items, LSNs, buffer ops, and AIL intent management.

## Research Notes

The separation of pass1, pass2, reordering, and intent recovery is the main contract. The reservation helper prevents livelock when recovered intents pin the log tail.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_log_recover.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_log_rlimit.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_log_rlimit.c

## Role

This file calculates minimum valid XFS log sizes from transaction reservation requirements. It preserves compatibility with older kernels by intentionally retaining historic overestimates for older feature sets, while allowing corrected calculations for newer parent-pointer filesystems.

## Compatibility Gate

`xfs_want_minlogsize_fixes` enables corrected minimum-log-size calculations only for v5 filesystems with the parent pointer incompat feature. This avoids formatting filesystems that older kernels would reject because the log became smaller than their historical minimum calculation expected.

## Attribute Reservation Calculation

`xfs_log_calc_max_attrsetm_res` estimates the largest local attr-set reservation. It computes the maximum local attr value size, directory/attr tree block needs, and extent-add reservation. For parent-pointer-era filesystems it corrects a previous unit conversion error by converting bytes to filesystem blocks before feeding the next-extent reservation macro.

## Alternate Reservation Table

`xfs_log_calc_trans_resv_for_minlogblocks` builds a transaction reservation table specifically for minimum log size calculations.

For old feature sets it preserves older behavior:

- temporarily forces old reflink+rmap maximum rmapbt level
- recomputes reservations
- copies dynamic atomic ioend reservation
- restores older write, truncate, and dquot-allocation log counts for rmap/reflink cases
- recomputes older write/truncate/dquot allocation log reservations that predate deferred refcount update log items

For new parent-pointer feature sets it uses current `xfs_trans_resv_calc` output plus dynamic atomic ioend reservation.

## Minimum Log Size

`xfs_log_get_max_trans_res` walks the alternate reservation table, finds the largest reservation considering log count, compares against maximum attr-set reservation, and returns the maximum transaction reservation.

`xfs_log_calc_minimum_size` converts that maximum transaction reservation to filesystem blocks. It accounts for log v2 stripe unit padding, requires enough room for two maximally sized transactions and padding, multiplies by `XFS_MIN_LOG_FACTOR`, and returns the rounded filesystem block count.

## Dependencies

This file depends on mount geometry, superblock feature checks, transaction reservation calculators, attr geometry, bmap/da reservation macros, and tracepoints.

## Research Notes

The file is deliberately conservative because minimum log size is a format interoperability boundary. The parent-pointer feature is used as a forward-compatibility marker for when smaller corrected minimum logs are safe.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_log_rlimit.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_metadir.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_metadir.c

## Role

This file implements the metadata directory tree abstraction. It supports looking up, loading, creating, linking, committing, canceling, and making directories for metadata inodes stored under a special metadata directory tree.

It does not manage the legacy realtime bitmap/summary or quota inode locations; newer metadata inodes should go through the metadir/metafile APIs.

## Lookup And Load

`xfs_metadir_set_xname` builds an `xfs_name` from a path component and expected file type.

`xfs_metadir_lookup` looks up a component in a metadata directory using directory da args. It requires an exclusive ILOCK on the parent, verifies the parent is a directory, rejects shutdown, validates the returned inode number, checks file type when requested, marks the metadir sick on corruption, and returns the inode number.

`xfs_metadir_load` locks the parent, looks up the component, unlocks, and loads the inode with `xfs_trans_metafile_iget`, validating the expected metafile type.

## Update Lifecycle

`struct xfs_metadir_update` is initialized by callers and passed through start, mutate, and commit/cancel operations.

`xfs_metadir_teardown` releases parent pointer args and unlocks child/parent inode locks as needed.

`xfs_metadir_start_create` allocates parent-pointer context, allocates a create transaction, and locks the parent directory with parent lock ordering.

`xfs_metadir_commit` commits the transaction and tears down resources.

`xfs_metadir_cancel` cancels the transaction and tears down resources.

## Create And Link

`xfs_metadir_create` verifies the final component does not already exist, allocates and creates an inode, marks it with `xfs_metafile_set_iflag`, joins the parent directory after possible transaction rolling, and creates the directory entry. It returns the newly created inode locked in the update structure.

The non-kernel `xfs_metadir_start_link` and `xfs_metadir_link` paths link an existing metadata inode into the metadir tree. They reserve directory link space, lock parent and child, require reservation space, reject duplicate final components, and add the directory entry.

`xfs_metadir_mkdir` wraps create-start, directory create, commit, finish setup, and error cleanup for a metadata subdirectory.

## Invariants

- Metadata directory tree inodes require ILOCK synchronization; IOLOCK/MMAPLOCK are unnecessary because metadata files are not exposed to userspace.
- Created metadata files are marked with the metadata inode flag and mandatory metadata flags.
- Parent pointers are prepared and passed to directory updates when the feature is enabled.
- Files in the metadata directory tree currently cannot be unlinked here.
- Metadir feature must be enabled for create/link operations.

## Dependencies

This file integrates with directory lookup/add/create helpers, inode allocation and creation, transaction reservations, parent pointer update contexts, metafile flagging, health marking, and mount feature predicates.

## Research Notes

The transaction lifecycle is the main usage contract: callers must commit or cancel every started update. `xfs_metadir_create` can return an inode even on error, so callers must finish setup and release it during cleanup.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_metadir.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_metadir.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_metadir.h

## Role

This header declares the metadata directory update context and metadir operations for loading, creating, linking, committing, canceling, and creating metadata directories.

## Main Contents

`struct xfs_metadir_update` carries:

- parent directory inode
- path component
- parent pointer args
- child metadata inode
- transaction
- metadata file type
- lock state for parent and child

Declared functions cover:

- `xfs_metadir_load`
- `xfs_metadir_start_create`
- `xfs_metadir_create`
- `xfs_metadir_start_link`
- `xfs_metadir_link`
- `xfs_metadir_commit`
- `xfs_metadir_cancel`
- `xfs_metadir_mkdir`

## Dependencies

The API depends on metadata file types, transactions, inodes, mode values, and parent pointer contexts.

## Research Notes

This is a stateful API: callers own `xfs_metadir_update` and must pair start/create/link with commit or cancel to release locks and resources.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_metadir.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_metafile.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_metafile.c

## Role

This file implements metadata inode flag management and global reservation accounting for metadata btree files. It currently focuses on metadata files under the metadir feature, especially realtime rmap and realtime refcount btree metadata.

## Metadata Inode Flags

`xfs_metafile_type_str` maps `enum xfs_metafile_type` values to strings.

`xfs_metafile_set_iflag` turns an inode into a metadata inode by clearing permissions, setting root uid/gid, adding mandatory directory or file metadata flags, clearing DAX, setting `XFS_DIFLAG2_METADATA`, storing the metatype, logging the inode core, and moving inode stats from active to metadata.

`xfs_metafile_clear_iflag` clears the metadata flag for zero-link metadata inodes, logs the inode, and adjusts stats back.

## Reservation Criticality

`xfs_metafile_resv_can_cover` tests whether available metadata reservation plus free filesystem blocks can cover a requested block count.

`xfs_metafile_resv_critical` reports critical reservation state if available space cannot cover maximum realtime btree height or 10% of target reservation, or if an error tag forces it.

## Reservation Allocation

`xfs_metafile_resv_alloc_space` charges allocated blocks first against the hidden metadata reservation, updating delayed allocation and reserved fdblocks superblock counters. If allocation exceeds the reservation, it tries to decrement normal free blocks or consume transaction block reservation. It updates used count, inode block count, and logs the inode.

`xfs_metafile_resv_free_space` decrements inode block count and used reservation, returns blocks to hidden reservation up to the target, updates reserved fdblocks, and returns any excess to normal free blocks.

## Reservation Lifecycle

`xfs_metafile_resv_init` resets existing state, walks realtime groups, sums used blocks and target reserves for realtime rmap and refcount btrees, caps reservation to one quarter of data blocks, hides unused target space from free blocks by moving it to delalloc accounting, and stores target/used/available counts.

`xfs_metafile_resv_free` releases unused hidden reservation back to free blocks.

## Dependencies

This file depends on metadir feature checks, realtime group iteration, realtime rmap/refcount btree reserve calculators, allocation args, transaction superblock accounting, inode logging, mount counters, and error tags.

## Research Notes

The reservation model intentionally hides unused metadata reserve space from free block accounting while keeping already-used metadata btree blocks accounted as used on disk. Any new metadata btree file requiring reserve space must be added to the reserve init loop.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_metafile.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_metafile.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_metafile.h

## Role

This header declares metadata inode type helpers, mandatory metadata inode flags, metadata reservation APIs, and external inode-get hooks for kernel/userspace-specific code.

## Main Contents

- `xfs_metafile_type_str` maps metadata type enum values to strings.
- `XFS_METAFILE_DIFLAGS` defines mandatory flags for metadata files: immutable, sync, noatime, nodump, and nodefrag.
- `XFS_METADIR_DIFLAGS` adds nosymlinks for metadata directories.
- `xfs_metafile_set_iflag` and `xfs_metafile_clear_iflag` manage metadata inode flags.
- Reservation functions test criticality, allocate/free reservation space, initialize reservations, and release unused reservations.
- `xfs_trans_metafile_iget` and `xfs_metafile_iget` are provided externally by kernel/userspace layers.

## Dependencies

The header depends on metadata file type enum definitions, transactions, inodes, mount state, and allocation args.

## Research Notes

Mandatory metadata flags are part of dinode verifier policy. Any change here must stay aligned with `xfs_dinode_verify_metadir`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_metafile.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ondisk.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ondisk.h

## Role

This header provides compile-time assertions for XFS on-disk and UAPI structure sizes, field offsets, and constant values. It is a guard against accidental ABI or disk-format layout drift.

## Main Mechanism

Macros wrap `static_assert` for:

- structure size checks
- member offset checks
- constant value checks
- paired superblock disk/incore offset checks

`xfs_check_ondisk_structs` runs these assertions at compile time.

## Checked Areas

The checks cover:

- file structures such as ACLs, bmap records, dinodes, dquots, symlink headers, and timestamps
- allocation, inode, rmap, and refcount btree structures
- dir and attr v4/v5 structures
- realtime superblock, bitmap/summary words, rt buffer headers, and realtime btree roots
- parent pointer records
- log structures including inode, buffer, extent intent, attr intent, bmap/rmap/refcount intent, mapping exchange, and log record headers
- v5 structures retaining v4 magic/header offsets
- bigtime and quota bigtime converted range constants
- superblock disk/incore size and all major field offsets
- ioctl UAPI structures such as bulkstat, inumbers, bmap, attrlist, geometry, scrub, and fs counts

## Compatibility Notes

Some checks are intentionally omitted or commented where architecture-specific padding or legacy definitions make size checks unreliable, such as old attr remote-name details and some ioctl structures.

## Dependencies

This header depends on nearly all core on-disk format structure definitions, log format definitions, ioctl UAPI structs, and compile-time assertion support.

## Research Notes

This file is a high-signal compatibility tripwire. When modifying any on-disk, log, or ioctl structure, this file must be updated deliberately and in sync with recovery, mkfs, repair, and kernel/userspace ABI expectations.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ondisk.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_parent.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_parent.c

## Role

This file implements parent pointer xattr handling. Parent pointers record directory parent identity in a child inode's attribute fork so metadata can reconstruct or validate directory relationships.

## Validation And Hashing

`xfs_parent_namecheck` validates parent pointer attr names. It rejects incomplete attrs and reuses directory name rules, so names cannot contain invalid dirent bytes.

`xfs_parent_valuecheck` requires the parent feature, a non-null local value exactly the size of `struct xfs_parent_rec`, and a valid parent directory inode number.

`xfs_parent_hashval` hashes the name using directory name hashing and mixes in the parent inode number to reduce hardlink collisions. `xfs_parent_hashattr` computes the hash from an xattr value after validating shape.

## DA Args Setup

`xfs_parent_da_args_init` initializes attr/da args for parent pointer operations:

- attr fork
- parent attr filter
- logged operations
- OKNOENT
- child inode as `dp`
- owner inode
- name/value from dirent name and parent record
- attr hash set by `xfs_attr_sethash`

`xfs_parent_iread_extents` ensures the child has an attr fork and loads attr extents before parent pointer updates, marking parent metadata sick on missing attr fork.

## Transactional Updates

- `xfs_parent_addname` adds a parent pointer after a dirent addition.
- `xfs_parent_removename` removes a parent pointer after a dirent removal.
- `xfs_parent_replacename` replaces an old parent/name record with a new one during rename.

Each builds `xfs_parent_rec` from the parent directory inode generation and inode number and delegates to logged attr set/remove/replace helpers.

## Parsing And Repair Helpers

`xfs_parent_from_attr` extracts parent inode and generation from a parent xattr, returning zero for valid parent pointers and `-EFSCORRUPTED` for malformed data.

`xfs_parent_lookup` looks up a specific parent pointer under an already locked inode.

`xfs_parent_set` and `xfs_parent_unset` are immediate non-transaction repair helpers that sanity-check the name/value, initialize scratch da args, and call `xfs_attr_set` with create or remove mode.

## Dependencies

This file depends on attr fork operations, directory name validation/hash, inode generation, transaction/defer infrastructure, health marking, bmap extent loading, and parent feature predicates.

## Research Notes

Parent pointer values are deliberately small enough to stay local, avoiding remote attr value handling. Missing attr forks are treated as corruption because parent-enabled filesystems create attr forks for linkable inodes at creation time.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_parent.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_parent.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_parent.h

## Role

This header declares parent pointer validation, hashing, transactional update, parsing, lookup, and repair APIs. It also defines the parent pointer update context wrapper.

## Main Contents

- `xfs_parent_namecheck` and `xfs_parent_valuecheck` validate parent pointer xattr fields.
- `xfs_parent_hashval` and `xfs_parent_hashattr` compute parent pointer attr hashes.
- `xfs_parent_rec_init` and `xfs_inode_to_parent_rec` initialize parent records from inode number and generation.
- `struct xfs_parent_args` stores old/new parent records plus `xfs_da_args`.
- `xfs_parent_start` allocates parent args only when the parent feature is enabled.
- `xfs_parent_finish` frees parent args.
- `xfs_parent_addname`, `xfs_parent_removename`, and `xfs_parent_replacename` update parent pointers for directory operations.
- `xfs_parent_from_attr` parses parent pointer xattrs.
- `xfs_parent_lookup`, `xfs_parent_set`, and `xfs_parent_unset` support repair paths.

## Dependencies

This header depends on parent feature checks, kmem caches, inode generation access, da args, xfs names, and parent record format definitions.

## Research Notes

The inline allocation helpers make parent pointer support cheap to call from generic directory code: callers can request a context unconditionally and get `NULL` when the feature is off.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_parent.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_platform.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_platform.h

## Role

This header is the userspace compatibility layer that lets selected XFS kernel code compile inside xfsprogs `libxfs`. It maps kernel APIs, types, feature config, logging, allocation, locking, quota, buffer, stats, and helper functions onto userspace equivalents or stubs.

## Platform Setup

The header defines userspace build context and includes:

- API renaming definitions
- platform definitions
- XFS base headers
- list/hlist/cache/bitops/kmem/atomic/spinlock shims
- radix tree, bitmask, div64, utility helpers
- types and architecture headers
- CRC and buffer IO support

It enables XFS realtime and in-memory btree config macros for `IS_ENABLED`-style code.

## Kernel API Shims

Important shims include:

- `ASSERT` mapped to `assert`
- XFS logging macros mapped to `cmn_err`
- corruption/error reporting macros
- no-op shutdown, delayed allocation, readahead, locking, stats, and tag helpers
- userspace dev_t identity conversion
- inode version accessors
- owner initialization prototype
- min/max/swap/rounding helpers
- bitmap declarations and next-bit search helpers
- power-of-two helpers
- buffer state/type helpers
- transaction buffer type helpers
- extent busy stubs
- filestream and realtime allocation stubs where unsupported
- quota reservation and dquot attach stubs
- UUID mapping
- superblock counter update macros backed by `libxfs_mod_incore_sb`

## Exposed Prototypes

The file declares functions from local libxfs components that kernel code expects but may not have explicit shared headers for, including transaction setup, transaction item handling, buffer item handling, inode item init, mount common setup, bmap helpers, verifier reporting, zeroing extents, log helpers, inode allocation setup, and other compatibility entry points.

## Notable Behavior

- Locking macros are mostly no-ops in userspace, so callers rely on higher-level tool serialization.
- Statistics macros suppress unused variable warnings.
- Some kernel-only paths are intentionally stubbed with fixed return values, such as filestream selection and realtime allocator helper in this context.
- `xfs_buf_incore` always reports not found.
- Parent or log recovery behavior that depends on kernel background state must be provided elsewhere or remains a stub.

## Dependencies

This file sits at the bottom of almost every libxfs source file. It is included by kernel-derived XFS code before normal XFS headers to provide the userspace build environment.

## Research Notes

This compatibility layer is central to xfsprogs kernel-code sharing. Changes here can silently alter semantics across large parts of libxfs, especially because many synchronization, quota, stats, and kernel background mechanisms are reduced to no-ops or simplified userspace equivalents.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_platform.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_quota_defs.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_quota_defs.h

## Role

This header defines quota-related shared types, flags, reservation constants, option flags, helper mappings, and quota inode metadir helpers used by kernel and userspace XFS code.

## Main Types And Flags

- `xfs_qcnt_t` is a 64-bit quota counter/limit type.
- `xfs_dqtype_t` is the quota type id.
- `XFS_DQTYPE_STRINGS` maps user, project, group, and bigtime quota type names.
- `XFS_DQFLAG_DIRTY` identifies dirty dquots.

`XFS_DQUOT_LOGRES` reserves space for worst-case transactions that can modify up to six dquots plus their log format items.

## Mount Quota Tests

Macros test whether quota accounting or enforcement is active for user, group, project, or any quota type:

- `XFS_IS_QUOTA_ON`
- `XFS_IS_UQUOTA_ON`
- `XFS_IS_PQUOTA_ON`
- `XFS_IS_GQUOTA_ON`
- enforcement variants for each quota type

## Quota Operation Flags

`XFS_QMOPT_*` flags identify requested quota types, forced reservations, superblock version updates, reserved regular/realtime blocks, block and inode count modifications, delayed counters, and inherited dqalloc behavior.

Transaction-facing aliases map quota modification meanings to `XFS_TRANS_DQ_*` constants.

## Verification And Conversion Declarations

The header declares dquot and dquot-block verification/repair helpers, dquots-per-chunk calculation, and bigtime quota expiration conversion helpers.

## Quota Inode Helpers

`xfs_dqinode_path` maps quota type to metadir path names: `user`, `group`, or `project`.

`xfs_dqinode_metafile_type` maps quota type to metadata file type: user, group, or project quota.

The header declares helpers to derive health sick masks, load quota inodes from metadir, create/link metadir quota inodes, and create/load the quota parent directory.

## Dependencies

This header depends on quota status bits from log format, dquot disk structures, metadata file type definitions, transactions, inodes, and mount quota flags.

## Research Notes

The quota option flags are internal and explicitly not persistent. The path/metafile mapping functions connect traditional quota inode concepts to the newer metadata directory tree.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_quota_defs.h -->