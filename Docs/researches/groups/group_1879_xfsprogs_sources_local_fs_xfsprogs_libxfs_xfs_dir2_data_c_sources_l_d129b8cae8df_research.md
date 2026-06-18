# Group Research: group_1879_xfsprogs_sources_local_fs_xfsprogs_libxfs_xfs_dir2_data_c_sources_l_d129b8cae8df

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2_data.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2_data.c

## Purpose
Implements shared XFS directory data-block handling for block, leaf, and node directory formats. It validates v2/v3 directory data buffers, initializes new data blocks, tracks the three-entry `bestfree` table, logs directory data changes, and converts byte ranges between active dirents and unused records.

## Main Entry Points
- `xfs_dir2_data_bestfree_p()` abstracts the v2/v3 header layout difference for the best-free table.
- `xfs_dir2_data_entry_tag_p()`, `xfs_dir2_data_get_ftype()`, and `xfs_dir2_data_put_ftype()` handle variable-size data entries.
- `__xfs_dir3_data_check()` performs structural verification of data and block-format directory buffers.
- `xfs_dir3_data_read()` and `xfs_dir3_data_readahead()` read/readahead data blocks with buffer verifiers and owner checks.
- `xfs_dir3_data_init()` allocates and initializes a new directory data block.
- `xfs_dir2_data_freefind()`, `xfs_dir2_data_freeinsert()`, `xfs_dir2_data_freescan()`, `xfs_dir2_data_make_free()`, and `xfs_dir2_data_use_free()` maintain free-space records.
- `xfs_dir2_data_log_entry()`, `xfs_dir2_data_log_header()`, and `xfs_dir2_data_log_unused()` log precise byte ranges into the transaction.
- `xfs_dir3_data_end_offset()` returns the end of the dirent area for data vs block-format buffers.

## Internal Mechanics
The verifier checks magic values, CRC-era UUID/block/LSN metadata, owner fields, sorted bestfree entries, unused-record tags, non-overlap, dirent inode validity, filetype validity, block-format leaf references, sorted block leaf hashes, and stale counts. The same low-level checker supports pure data blocks and block-format directories because both share dirent/free-record layout before the leaf/tail area.

Free-space mutation is local and careful: `make_free` merges with previous and/or following unused records and either updates the bestfree table directly or asks for a full rescan; `use_free` carves allocation from the front, back, middle, or whole unused record. Both paths report whether callers must log the header and whether the bestfree table needs reconstruction.

## Dependencies
Depends on XFS directory geometry, transaction logging, buffer verification/checksum helpers, inode health marking, endian helpers, and shared directory APIs from `xfs_dir2.h` / `xfs_dir2_priv.h`. It is used by block, leaf, node, and shortform conversion code.

## Risks and Notes
The code is metadata-critical: almost every caller relies on bestfree correctness to avoid directory corruption. Many functions assume the caller has already validated alignment and range choices; the defensive checks in `xfs_dir2_data_use_free()` are therefore important. Any format change affecting dirent size, ftype storage, CRC headers, or block-format tails must be reflected here and in all callers that calculate offsets.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2_data.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2_leaf.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2_leaf.c

## Purpose
Implements XFS leaf-format directory operations and shared leaf-block helpers. It covers v2/v3 leaf header conversion, leaf1/leafn verification, block-to-leaf and node-to-leaf format transitions, leaf-format add/lookup/remove/replace, stale-entry compaction, hash searching, and leaf bestfree table logging.

## Main Entry Points
- `xfs_dir2_leaf_hdr_from_disk()` / `xfs_dir2_leaf_hdr_to_disk()` normalize v2/v3 leaf headers into `xfs_dir3_icleaf_hdr`.
- `xfs_dir3_leaf_read()` and `xfs_dir3_leafn_read()` read leaf1 and leafn blocks with CRC/owner checks.
- `xfs_dir3_leaf_get_buf()` initializes a new leaf block.
- `xfs_dir2_block_to_leaf()` converts a block-format directory into leaf form.
- `xfs_dir2_leaf_addname()`, `xfs_dir2_leaf_lookup()`, `xfs_dir2_leaf_removename()`, and `xfs_dir2_leaf_replace()` implement leaf-format directory mutation.
- `xfs_dir2_leaf_search_hash()` performs binary search over sorted leaf hash entries.
- `xfs_dir2_leaf_trim_data()` removes trailing empty data blocks from leaf-form directories.
- `xfs_dir2_node_to_leaf()` converts a simple node-form directory back to leaf/block form when possible.

## Internal Mechanics
Leaf entries are sorted by hash and can contain stale placeholders with `XFS_DIR2_NULL_DATAPTR`. Insertions either shift entries, reuse the nearest stale entry, compact all but one stale entry, or escalate to node form if the leaf block cannot hold the new entry or bests-table growth. Data-block allocation and dirent creation are delegated to `xfs_dir2_data_*` helpers, while the leaf tail stores per-data-block bestfree values for leaf1 directories.

Lookups binary-search to the first matching hash and then scan equal-hash entries, reading data blocks as needed and preserving case-insensitive matches until an exact match is found. Removal marks a leaf entry stale, frees the data entry, updates the bests table, may shrink empty trailing data blocks, and then attempts conversion back to block form.

## Dependencies
Uses directory data helpers from `xfs_dir2_data.c`, block-format conversion helpers, node-format helpers, DA buffer and bmap operations, transaction logging, buffer ops, tracepoints, and directory health marking.

## Risks and Notes
Leaf format depends on tight free-space accounting between leaf entries, leaf tail bests entries, and data block bestfree headers. Conversion paths assume specific block ordering: block-to-leaf creates the first leaf block at the leaf offset, and node-to-leaf only proceeds when the node root is already a single leafn block and free-space blocks can be removed. `xfs_dir2_leaf_search_hash()` assumes the leaf entry table is non-empty, so callers must maintain that precondition.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2_leaf.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2_node.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2_node.c

## Purpose
Implements XFS node-format directory support: free-space block verification/management, leaf1-to-leafn conversion, leafn lookup/add/remove/split/rebalance/join helpers, node-format add/lookup/remove/replace, and trimming empty free-space blocks.

## Main Entry Points
- `xfs_dir2_free_hdr_from_disk()` and the internal `xfs_dir2_free_hdr_to_disk()` abstract v2/v3 free-block headers.
- `xfs_dir2_free_read()` reads free-space blocks; `xfs_dir2_free_try_read()` tolerates holes.
- `xfs_dir2_leaf_to_node()` converts a leaf-format directory into node form by moving the leaf bests table to a free block.
- `xfs_dir2_leafn_lookup_int()` dispatches lookup behavior for addname vs entry lookup.
- `xfs_dir2_leafn_split()`, `xfs_dir2_leafn_toosmall()`, and `xfs_dir2_leafn_unbalance()` support DA btree split/join mechanics.
- `xfs_dir2_node_addname()`, `xfs_dir2_node_lookup()`, `xfs_dir2_node_removename()`, and `xfs_dir2_node_replace()` are top-level node-format operations.
- `xfs_dir2_node_trim_free()` removes trailing unused free-space blocks.

## Internal Mechanics
Node directories store hash-indexed leafn blocks separately from data blocks and maintain free-space summaries in blocks starting at `XFS_DIR2_FREE_OFFSET`. `xfs_dir2_db_to_fdb()` and `xfs_dir2_db_to_fdindex()` map data-block numbers to their free-space block and index. Addname first uses the DA btree lookup path to find the leaf insertion point and possibly a preferred free block, then finds or allocates a data block, creates the data entry, updates the free-space summary, and inserts a leafn entry. If the leaf is full, DA split calls `xfs_dir2_leafn_split()`.

Removal marks the leaf entry stale, frees the dirent in its data block, updates or removes the free-space entry, can shrink empty data/free blocks, fixes btree hashes, may join underfull leaf blocks, and finally tries node-to-leaf conversion.

## Dependencies
Depends on DA btree state/path operations, leaf helpers from `xfs_dir2_leaf.c`, data helpers from `xfs_dir2_data.c`, inode grow/shrink and bmap helpers, transaction logging, buffer verification, tracepoints, and XFS health marking.

## Risks and Notes
The free-space verifier has an explicit `XXX` noting that `xfs_dir3_free_verify()` should bounds-check the decoded in-core free header. Node add/remove has delicate ownership of `state->extrablk` buffers because that slot alternates between free blocks and data blocks depending on the operation. Error paths around no-space-reservation operations intentionally leave some empty blocks for later cleanup; callers must tolerate holes and stale summaries.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2_node.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2_priv.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2_priv.h

## Purpose
Defines private interfaces and in-core helper structures for XFS dir2/dir3 directory implementation files.

## Main Contents
- `struct xfs_dir3_icleaf_hdr` and `struct xfs_dir3_icfree_hdr` provide v2/v3-neutral in-core views of leaf and free-block headers.
- Declares private helpers across `xfs_dir2.c`, block, data, leaf, node, shortform, and readdir implementations.
- Provides inline size helpers: `xfs_dir2_data_unusedsize()` and `xfs_dir2_data_entsize()`.
- Declares name hashing/comparison helpers `xfs_dir2_hashname()` and `xfs_dir2_compname()`.

## Integration
This header is the private contract tying together directory format variants: shortform, block, leaf, and node. The inline entry-size calculation centralizes ftype-aware dirent sizing, which is used throughout data-block mutation and verification code.

## Risks and Notes
Because this header exposes many cross-file private functions, changes to directory geometry, ftype storage, CRC-era layout, or shortform inode encoding must be coordinated across all declared implementations. The in-core header structs intentionally carry pointers into on-disk buffers, so callers must not outlive or move the underlying buffer.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2_priv.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2_sf.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2_sf.c

## Purpose
Implements XFS shortform directory operations, where small directories are stored inline in the inode data fork. It handles shortform entry sizing, inode/filetype encoding, create/add/lookup/remove/replace, verification, conversion from block form, and conversion between 4-byte and 8-byte inode encodings.

## Main Entry Points
- `xfs_dir2_sf_entsize()` and `xfs_dir2_sf_nextentry()` handle variable-length entry layout.
- `xfs_dir2_sf_get_ino()`, `xfs_dir2_sf_put_ino()`, `xfs_dir2_sf_get_parent_ino()`, and `xfs_dir2_sf_put_parent_ino()` encode/decode parent and child inode numbers.
- `xfs_dir2_sf_get_ftype()` and `xfs_dir2_sf_put_ftype()` manage optional filetype bytes.
- `xfs_dir2_block_sfsize()` and `xfs_dir2_block_to_sf()` convert block directories back into shortform when they fit.
- `xfs_dir2_sf_addname()`, `xfs_dir2_sf_lookup()`, `xfs_dir2_sf_removename()`, and `xfs_dir2_sf_replace()` implement shortform operations.
- `xfs_dir2_sf_verify()` validates inline directory contents.
- `xfs_dir2_sf_toino4()` and `xfs_dir2_sf_toino8()` repack all entries when inode number width changes.

## Internal Mechanics
Shortform directories omit `"."`; they store `".."` as the parent inode in the header. Normal entries carry name length, block-format offset, name, optional filetype, and either a 32-bit or 64-bit inode number. Entries are ordered by their future block-format offsets so conversion to block form remains possible.

Adding a name chooses an easy append path if enough offset space remains at the end, a hard insert path if an interior hole must be used, or converts to block form if inline storage or block-format offset constraints fail. Replacement may force conversion to 8-byte inode storage, or convert to block form if the widened inline data no longer fits.

## Dependencies
Uses inode local-fork allocation helpers, directory data sizing helpers, block-format conversion routines, transaction inode logging, tracepoints, and name comparison helpers.

## Risks and Notes
All mutation paths repack variable-length inline data, so size and pointer recalculation after `xfs_idata_realloc()` is central. The verifier checks entry bounds, increasing offsets, valid inode numbers, i8count consistency, filetype range, and that the directory could fit in block form. Any change to shortform field ordering must also update the get/put and repacking routines.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dir2_sf.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dquot_buf.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dquot_buf.c

## Purpose
Implements on-disk quota record verification, repair initialization, quota buffer verifiers, quota timer conversion, and quota metadata inode loading/creation helpers.

## Main Entry Points
- `xfs_calc_dquots_per_chunk()` derives quota records per buffer chunk.
- `xfs_dquot_verify()` validates a single `xfs_disk_dquot`.
- `xfs_dqblk_verify()` validates the containing `xfs_dqblk`, including UUID for CRC filesystems.
- `xfs_dqblk_repair()` zeroes and initializes a quota block for quotacheck repair.
- `xfs_dquot_buf_ops` and `xfs_dquot_buf_ra_ops` provide normal and readahead buffer verifier operations.
- `xfs_dquot_from_disk_ts()` and `xfs_dquot_to_disk_ts()` convert quota grace timers, including bigtime encoding.
- `xfs_dqinode_load()`, `xfs_dqinode_metadir_create()`, `xfs_dqinode_metadir_link()`, `xfs_dqinode_mkdir_parent()`, and `xfs_dqinode_load_parent()` manage quota inodes in legacy superblock fields or the metadata directory.

## Internal Mechanics
Quota verification checks magic, version, type mask, record type, bigtime feature compatibility, expected id, and consistency between soft limits, current usage, and timers. Buffer verification first checks per-record CRCs on CRC filesystems, then verifies monotonically increasing ids across all quota records in the buffer. Readahead failures are quiet: the buffer is marked not done so a real read can perform full reporting.

Quota inode loading supports old filesystems with superblock quota inode numbers and newer metadir filesystems where quota files live under `/quota`.

## Dependencies
Depends on quota definitions, transaction and inode helpers, filesystem health flags, metadir/metafile APIs, checksum helpers, and endian conversion utilities.

## Risks and Notes
The verifier intentionally tolerates some uninitialized quota-buffer scenarios by reporting structural failure without assuming quota loss. `xfs_dqinode_load()` marks the relevant quota metadata sick when loading detects metadata errors or invalid quota inode formats. Userspace-only `xfs_dqinode_metadir_link()` is excluded under `__KERNEL__`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_dquot_buf.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_errortag.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_errortag.h

## Purpose
Defines XFS error-injection tag identifiers and the macro table used to generate error-tag metadata.

## Main Contents
- Numeric `XFS_ERRTAG_*` constants from `XFS_ERRTAG_NOERROR` through `XFS_ERRTAG_ZONE_RESET`, with `XFS_ERRTAG_MAX` set to 48.
- `XFS_RANDOM_DEFAULT`, the default randomization divisor for error injection.
- Optional `XFS_ERRTAGS` macro expansion table, enabled when includers define `XFS_ERRTAG(name, knob, default)`.

## Integration
The header supports two include modes: direct inclusion for constants, or macro-driven inclusion to generate tables of sysfs/debug knobs and default injection frequencies. `XFS_ERRTAG_EXCHMAPS_FINISH_ONE` is used by `xfs_exchmaps_finish_one()` to inject failures into exchange-mapping deferred work.

## Risks and Notes
The numeric constants are expected to remain consecutive because arrays are sized from the maximum. The removed drop-writes tag remains reserved so invalid historical values can still be rejected. Adding a tag requires updating both the numeric list and the macro table consistently.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_errortag.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_exchmaps.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_exchmaps.c

## Purpose
Implements XFS file mapping exchange support: estimating exchange cost, preparing deferred exchange intents, swapping extents between two inodes/forks, maintaining quota/reflink/extent-count state, and performing post-operation conversions back to shortform metadata when possible.

## Main Entry Points
- `xfs_exchmaps_check_forks()` rejects missing or local-format forks.
- `xfs_exchmaps_estimate()` walks mappings to estimate exchanged block counts, exchange count, extent-count deltas, and reservation overhead.
- `xfs_exchmaps_estimate_overhead()` adds bmbt/rmapbt reservation estimates.
- `xfs_exchmaps_intent_init_cache()` and `xfs_exchmaps_intent_destroy_cache()` manage the intent slab cache.
- `xfs_exchmaps_init_intent()` builds an in-core deferred intent from a request.
- `xfs_exchmaps_finish_one()` performs one deferred exchange step or post-operation cleanup and returns `-EAGAIN` when more transactions are needed.
- `xfs_exchmaps_ensure_reflink()` and `xfs_exchmaps_upgrade_extent_counts()` prepare inode flags before exchange work starts.
- `xfs_exchange_mappings()` schedules the deferred mapping exchange.

## Internal Mechanics
The exchange walker reads aligned mapping pairs from both inodes, skips file1 holes/unwritten extents when `XFS_EXCHMAPS_INO1_WRITTEN` allows it, handles realtime allocation-unit alignment, and rejects impossible delalloc or mismatched lookup results. A single exchange step unmaps both records, swaps logical offsets, maps each physical record into the other inode, updates quotas, and advances the intent cursor.

The estimator simulates the same walk, tracks adjacent mappings to estimate extent-count growth or shrinkage, records moved data/rt blocks, counts exchange steps, checks extent-counter overflow, and adds bmbt/rmapbt reservation overhead. Post-operation cleanup can convert inode2 attr/dir/symlink forks back to shortform and clear reflink flags when a full-file exchange allows the reflink state to be effectively swapped.

## Dependencies
Uses bmap read/map/unmap helpers, deferred operation plumbing, quota accounting, reflink/COW fork state, large extent count feature flags, dir/attr/symlink shortform conversion helpers, transaction logging, tracepoints, rmap/bmbt reservation constants, and `XFS_ERRTAG_EXCHMAPS_FINISH_ONE`.

## Risks and Notes
This code assumes callers have flushed delalloc/pagecache state and hold both inode ILOCKs. Reservation estimation is conservative but complex, especially around mapping merge simulation and realtime unwritten extents. In `xfs_exchmaps_estimate_overhead()`, the final `UINT_MAX` check compares `req->resblks` before assigning the accumulated `resblks`, which is worth reviewing because overflow checks update the local variable first. Post-operation shortform conversion helpers can return without releasing buffers when conversion is not possible; that may be transaction-buffer ownership by convention, but it is a path to audit carefully.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_exchmaps.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_exchmaps.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_exchmaps.h

## Purpose
Declares the public libxfs interface and data structures for XFS mapping exchange operations.

## Main Contents
- `struct xfs_exchmaps_intent` stores deferred in-core exchange state: inode pair, offsets, block count, optional final sizes, and operation flags.
- `struct xfs_exchmaps_req` is the caller-facing request plus estimator outputs such as moved block counts, reservation blocks, and number of exchange steps.
- `xfs_exchmaps_whichfork()` and `xfs_exchmaps_reqfork()` select data vs attr fork from flags.
- Defines internal flag `__XFS_EXCHMAPS_INO2_SHORTFORM` and accepted request parameter mask `XFS_EXCHMAPS_PARAMS`.
- Declares estimator, intent cache, intent creation, reflink preparation, extent-count upgrade, deferred step completion, fork validation, and scheduling functions.

## Integration
The header bridges higher-level exchange-range callers, deferred operation code, and the implementation in `xfs_exchmaps.c`. The request structure is intentionally split between caller-initialized inputs and fields filled by `xfs_exchmaps_estimate()`.

## Risks and Notes
`xfs_exchmaps_intent` is both deferred-work state and recovery-progress state, so flag semantics must remain compatible with logged exchange-map intent/done items. Internal flags are kept outside the logged flag namespace with a build-time assertion in the implementation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_exchmaps.h -->