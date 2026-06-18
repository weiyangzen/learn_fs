# Group Research: Linux XFS directory formats, quota dquot buffers, error tags, and exchange-mapping helpers

This group covers XFS libxfs code for directory data blocks, leaf and node directory formats, shortform directories, private directory cross-file interfaces, quota dquot buffer verification and metadata quota inode loading, error injection tag definitions, and the deferred file mapping exchange engine.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_data.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_data.c

## Purpose

Implements shared XFS directory data-block handling for block, leaf, and node directory formats: data entry field access, filetype storage, structural verification, CRC-aware buffer operations, data block initialization, transaction logging ranges, and bestfree/free-space mutation.

## Main Interfaces

- Entry accessors: `xfs_dir2_data_bestfree_p()`, `xfs_dir2_data_entry_tag_p()`, `xfs_dir2_data_get_ftype()`, `xfs_dir2_data_put_ftype()`.
- Verification and buffer ops: `__xfs_dir3_data_check()`, `xfs_dir3_data_buf_ops`, `xfs_dir3_data_header_check()`, `xfs_dir3_data_read()`, `xfs_dir3_data_readahead()`.
- Free-space accounting: `xfs_dir2_data_freefind()`, `xfs_dir2_data_freeinsert()`, `xfs_dir2_data_freescan()`, internal `xfs_dir2_data_freeremove()`.
- Block creation and logging: `xfs_dir3_data_init()`, `xfs_dir2_data_log_entry()`, `xfs_dir2_data_log_header()`, `xfs_dir2_data_log_unused()`.
- Free range mutation: `xfs_dir2_data_make_free()`, `xfs_dir2_data_use_free()`, `xfs_dir3_data_end_offset()`.

## Control Flow And Behavior

Verification walks each active and unused record from the directory data entry offset to the data area end, checking magic values, free-entry tags and back-tags, active entry inode numbers, active entry tags, filetype values, sorted bestfree entries, non-overlapping free ranges, and, for block-format directories, that every active data entry has a matching leaf record and that leaf records are hash sorted with an accurate stale count.

Read verification checks CRCs on v5 filesystems before structural checks; write verification refreshes the LSN, zeros v5 data-header padding, and updates the checksum. Readahead of directory block zero can land on either block-format or data-format storage, so `xfs_dir3_data_reada_verify()` switches buffer ops based on the on-disk magic before verifying.

`xfs_dir3_data_init()` allocates a directory data buffer, initializes v2 or v3 headers, sets the initial bestfree entry to the whole post-header data area, writes a single unused record, logs the header and unused entry, and returns the buffer. Logging helpers record exact byte ranges for data entries, headers, and unused entry head/tail fields.

`xfs_dir2_data_make_free()` merges a newly freed byte range with adjacent unused records when possible, updates or invalidates bestfree entries, and asks callers to rescan when local bestfree updates cannot prove correctness. `xfs_dir2_data_use_free()` carves a range out of an unused record, handling exact, front, back, and middle splits; it validates the source free range and reports corruption through directory sickness marking.

## State And Data Structures

Directory data blocks contain a header, three bestfree records, and a linear sequence of active `xfs_dir2_data_entry` and unused `xfs_dir2_data_unused` records. V5 directory data headers extend the v2 layout with CRC metadata, owner, UUID, block number, LSN, and padding. The bestfree table tracks only the three largest free regions, so some updates require a full data-block rescan.

## Dependencies

Uses directory geometry from `xfs_da_geometry`, transaction buffer logging, DA buffer read/readahead helpers, CRC buffer helpers, directory inode validation and hashing, health marking for directory/attribute forks, and block-directory tail/leaf helpers from the directory format layer.

## Risks And Invariants

- Bestfree entries must stay sorted, non-overlapping, exact when they reference an unused record, and zero-filled after the last valid entry.
- Free-space split/merge logic must keep unused back-tags accurate or later reverse scans can corrupt directory traversal.
- Block-format validation depends on matching data entries to embedded leaf entries by both hash and address.
- The `needscan` protocol is correctness-sensitive because bestfree tracks only three regions.
- CRC metadata checks cannot validate owner fields until `xfs_dir3_data_read()` supplies the expected directory inode.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_leaf.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_leaf.c

## Purpose

Implements XFS leaf-format directory blocks and shared leaf helpers used by leaf and node directories: v2/v3 leaf header conversion, leaf verification, buffer operations, leaf block initialization, block-to-leaf conversion, add/lookup/remove/replace for single-leaf directories, stale-entry compaction, bests-table logging, data-block trimming, and node-to-leaf collapse.

## Main Interfaces

- Header conversion and verification: `xfs_dir2_leaf_hdr_from_disk()`, `xfs_dir2_leaf_hdr_to_disk()`, `xfs_dir3_leaf_check_int()`, `xfs_dir3_leaf_header_check()`.
- Buffer reads and allocation: `xfs_dir3_leaf_read()`, `xfs_dir3_leafn_read()`, `xfs_dir3_leaf_get_buf()`, `xfs_dir3_leaf1_buf_ops`, `xfs_dir3_leafn_buf_ops`.
- Format conversion: `xfs_dir2_block_to_leaf()`, `xfs_dir2_node_to_leaf()`.
- Leaf-format operations: `xfs_dir2_leaf_addname()`, `xfs_dir2_leaf_lookup()`, `xfs_dir2_leaf_removename()`, `xfs_dir2_leaf_replace()`.
- Shared leaf helpers: `xfs_dir3_leaf_find_entry()`, `xfs_dir3_leaf_compact()`, `xfs_dir3_leaf_compact_x1()`, `xfs_dir3_leaf_log_ents()`, `xfs_dir3_leaf_log_header()`, `xfs_dir2_leaf_search_hash()`, `xfs_dir2_leaf_trim_data()`.

## Control Flow And Behavior

Leaf verification decodes v2/v3 headers into an in-core header, validates DA block info, bounds the entry count, checks that leaf entries do not overlap a leaf1 bests table, and optionally checks hash ordering, stale count, and leaf1 bests-table address coverage. Reads also validate v5 owners after generic verification.

Block-to-leaf conversion allocates the first leaf-space block, initializes it as a leaf1 block, copies embedded block leaf entries into the new leaf, marks the old embedded leaf/tail area in the data block free, changes the old block directory to a data block, and seeds the leaf1 bests table from the data block bestfree value.

`xfs_dir2_leaf_addname()` reads the leaf1 block, finds the hash insertion point, prefers a data block already containing the same hash if it has room, otherwise scans the leaf bests table or allocates a new data block. It ensures leaf space exists for a new entry or bests entry, compacts stale entries if useful, converts to node form when the leaf no longer fits, writes the new data entry, updates data bestfree and leaf bests, inserts the sorted leaf record, and logs all changed ranges.

Lookup binary-searches to the first matching hash, scans equal-hash entries, reads data blocks as needed, supports exact and case-insensitive matches, and returns inode/filetype plus actual case-preserved name when needed. Removal marks the data entry free, marks the leaf entry stale, updates the leaf1 bests table, drops empty data blocks when possible, and then tries to convert the directory to block form. Replacement updates only the target data entry inode number and filetype.

Node-to-leaf conversion is attempted when a node directory has only one leafn block and one freespace block. It trims trailing empty freespace blocks, verifies the leafn plus freespace data fits in one leaf1 block, compacts stale leaf entries, changes the leafn to leaf1, copies the free block bests table into the leaf tail area, frees the separate free block, and then tries leaf-to-block conversion.

## State And Data Structures

Leaf1 directories have a sorted leaf-entry array plus a tail and bests table recording the largest free space in each data block. Leafn blocks are similar leaf arrays without the bests tail and are used below DA btree nodes. `xfs_dir3_icleaf_hdr` abstracts v2/v3 on-disk header differences and points to the on-disk leaf entries.

## Dependencies

Depends on directory data-block helpers, block-format conversion, node-format conversion, DA allocation and btree helpers, transaction logging, bmap last-offset queries, data/free block shrink helpers, and directory health marking through lower-level read functions.

## Risks And Invariants

- Leaf entries must stay sorted by hash, with duplicate hashes preserving scan semantics.
- Leaf stale counts must match entries whose address is `XFS_DIR2_NULL_DATAPTR`.
- Leaf1 bests entries must stay synchronized with data-block bestfree values and data block lifetime.
- Format conversions must not lose free-space records or leave buffers with the wrong verifier/type.
- Case-insensitive lookup must retain the first CI match while still preferring an exact match.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_leaf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_node.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_node.c

## Purpose

Implements XFS node-format directories: freespace block verification and management, leaf-to-node conversion, leafn add/lookup/split/rebalance/join helpers, data-entry add/remove for node directories, top-level node add/lookup/remove/replace operations, and cleanup of empty freespace blocks.

## Main Interfaces

- Free block mapping and verification: internal `xfs_dir2_db_to_fdb()`, `xfs_dir2_db_to_fdindex()`, `xfs_dir3_free_buf_ops`, `xfs_dir2_free_read()`.
- Free header conversion/allocation: `xfs_dir2_free_hdr_from_disk()`, internal `xfs_dir2_free_hdr_to_disk()`, `xfs_dir3_free_get_buf()`.
- Format conversion: `xfs_dir2_leaf_to_node()`, `xfs_dir2_node_trim_free()`.
- Leafn helpers: `xfs_dir2_leaf_lasthash()`, `xfs_dir2_leafn_lookup_int()`, `xfs_dir2_leafn_order()`, `xfs_dir2_leafn_split()`, `xfs_dir2_leafn_toosmall()`, `xfs_dir2_leafn_unbalance()`.
- Node-format operations: `xfs_dir2_node_addname()`, `xfs_dir2_node_lookup()`, `xfs_dir2_node_removename()`, `xfs_dir2_node_replace()`.

## Control Flow And Behavior

Freespace blocks cover arrays of data-block bestfree values. Header checks verify the free block's expected first data-block index, `nvalid <= free_max_bests`, `nused <= nvalid`, and v5 owner metadata. Free block allocation initializes an empty v2/v3 header and sets buffer type/ops.

Leaf-to-node conversion allocates the first free-space block, copies the leaf1 bests table into it, initializes `nvalid` and `nused`, and changes the single leaf block from leaf1 magic to leafn magic. This separates data-block free-space accounting from the leaf block so the directory can grow a DA btree.

For add lookup, `xfs_dir2_leafn_lookup_for_addname()` searches matching-hash leaf entries for a data block with enough free space, returning the corresponding free block as `state->extrablk` when useful. For normal lookup/removal/replace, `xfs_dir2_leafn_lookup_for_entry()` scans equal hashes, reads data blocks, supports CI matches, and returns the found data block in the DA state.

`xfs_dir2_node_addname()` builds a DA state cursor, uses node lookup to find the insertion point, adds the data entry first via `xfs_dir2_node_addname_int()`, then inserts the leafn entry. If the target leafn is full, it splits and rebalances leaf entries through the generic DA split path. Data-entry addition scans existing free blocks from high to low for space, allocates a new data block and maybe a new free block if needed, carves space with data helpers, writes the dirent, updates the free block bests entry, and returns the new data block/offset for the leaf entry.

Removal uses the DA state to find the leaf and data entry, marks the leaf entry stale, frees the data entry, updates data bestfree, updates or removes the corresponding free-block entry, can punch empty data blocks, fixes btree hash values, joins underfull leaf blocks, and finally tries to convert the node directory back to leaf form. Replacement preserves the new inode/filetype across lookup, then updates the matched data entry and logs it.

Leaf split/rebalance code moves sorted entries between sibling leafn blocks, preserving stale counts and choosing the insertion side. Join checks consider empty blocks, 50% fullness, sibling fit with 25% spare, and prefer retaining the lower-numbered block for gradual directory shrinkage.

## State And Data Structures

Node directories use DA btree paths (`xfs_da_state`) over leafn blocks. Separate free blocks begin at `XFS_DIR2_FREE_OFFSET`; each entry maps to one data block and stores that block's largest free region or `NULLDATAOFF` for a missing/unused data block. The DA state's `extrablk` alternates between free blocks for add operations and data blocks for lookup/remove/replace operations.

## Dependencies

Depends on DA btree lookup/split/join/path-shift/hash-fix code, leaf helpers from `xfs_dir2_leaf.c`, data block helpers from `xfs_dir2_data.c`, directory block grow/shrink helpers, transaction logging, bmap last-offset queries, and corruption/health marking.

## Risks And Invariants

- Free block `firstdb`, `nvalid`, `nused`, and bests entries must match the data block range implied by the free block number.
- Add operations intentionally create the data entry before the leaf entry; error handling must keep transaction state coherent.
- Empty data and free blocks can fail to shrink without reservation; callers intentionally tolerate some `-ENOSPC` cleanup failures.
- Leafn stale entry accounting affects split/join decisions and later format collapse.
- `state->extrablk` meaning depends on operation type and must be set with correct buffer ops/type.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_priv.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_priv.h

## Purpose

Defines private cross-file interfaces for XFS directory version 2/3 implementations, including in-core abstractions for on-disk leaf/free headers, prototypes for shortform, block, data, leaf, node, and readdir helpers, and inline size calculations for directory data records.

## Main Interfaces

- In-core header shims: `struct xfs_dir3_icleaf_hdr` and `struct xfs_dir3_icfree_hdr`.
- Generic directory helpers declared from `xfs_dir2.c`: CI hash/compare, grow inode, CI lookup result, hash/compare wrappers.
- Block/data/leaf/node/shortform operation prototypes used by generic dispatch.
- Inline record sizing: `xfs_dir2_data_unusedsize()` and `xfs_dir2_data_entsize()`.
- Shortform entry helpers for parent inode, entry inode, filetype, next-entry walking, verification, and format conversion.

## Control Flow And Behavior

The header isolates directory implementation files from v2/v3 on-disk header differences by exposing host-endian in-core leaf/free headers whose `ents` or `bests` pointer references the variable-position on-disk arrays. It also centralizes format-operation prototypes so generic code can dispatch to shortform, block, leaf, or node code without exposing each implementation's local helpers.

The inline data record size helpers round unused and active directory data records to XFS directory alignment. Active entry size accounts for the fixed entry prefix, name bytes, optional filetype byte, and trailing offset tag.

## State And Data Structures

`xfs_dir3_icleaf_hdr` carries sibling block numbers, magic, entry count, stale count, and a pointer to leaf entries. `xfs_dir3_icfree_hdr` carries free-block magic, first covered data block, valid/used counts, and a pointer to bests entries. Both are transient views over v2/v3 disk blocks.

## Dependencies

Depends on public XFS directory, DA btree, mount, inode, buffer, and transaction types declared by included compilation units. It is consumed by all directory implementation files and by code that needs specific format conversions.

## Risks And Invariants

- Prototypes here define tight coupling among directory format files; signature drift breaks generic dispatch.
- Size helpers must exactly match on-disk layout, optional filetype support, and alignment rules.
- In-core header pointers are aliases into buffers, so callers must not use them after buffer lifetime ends or after format-changing reallocations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_priv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_sf.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_sf.c

## Purpose

Implements XFS shortform directories stored inside the inode data fork: variable-length entry encoding, parent and child inode number access, optional filetype storage, block-to-shortform conversion, create/add/lookup/remove/replace operations, shortform verification, and conversion between 4-byte and 8-byte inode-number encodings.

## Main Interfaces

- Entry layout helpers: `xfs_dir2_sf_entsize()`, `xfs_dir2_sf_nextentry()`, `xfs_dir2_sf_get_ino()`, `xfs_dir2_sf_put_ino()`, `xfs_dir2_sf_get_parent_ino()`, `xfs_dir2_sf_put_parent_ino()`, `xfs_dir2_sf_get_ftype()`, `xfs_dir2_sf_put_ftype()`.
- Conversion sizing and conversion: `xfs_dir2_block_sfsize()`, `xfs_dir2_block_to_sf()`.
- Shortform operations: `xfs_dir2_sf_create()`, `xfs_dir2_sf_addname()`, `xfs_dir2_sf_lookup()`, `xfs_dir2_sf_removename()`, `xfs_dir2_sf_replace()`.
- Verification and internal mutation: `xfs_dir2_sf_verify()`, internal `xfs_dir2_sf_addname_easy()`, `xfs_dir2_sf_addname_hard()`, `xfs_dir2_sf_addname_pick()`, `xfs_dir2_sf_toino4()`, `xfs_dir2_sf_toino8()`.

## Control Flow And Behavior

Shortform entries store name length, block-format data offset, name bytes, optional filetype byte, and either 4-byte or 8-byte inode number depending on the header `i8count`. Parent inode storage follows the same width rule. Accessors handle unaligned big-endian loads and stores.

`xfs_dir2_block_sfsize()` computes whether a block-format directory can fit back inside the inode, walking block leaf entries to count non-dot entries, detect `..`, sum names/filetypes, and decide if any inode numbers require 8-byte encoding. `xfs_dir2_block_to_sf()` formats a temporary shortform buffer from the block entries, skips `.`, encodes `..` as the header parent, frees the data block, converts the data fork to local format, copies the shortform data into the inode, updates disk size, and logs core/data fork changes.

`xfs_dir2_sf_addname()` first checks if the new entry still fits in local format and can later be converted to block format. The easy path appends at the end when offset ordering permits. The hard path copies the old directory aside, finds a hole in the block-format offset sequence, rebuilds the inline directory with the new entry inserted, and handles an inode-width conversion first if required. If the shortform directory cannot fit, the code converts to block format and retries through block add.

Lookup special-cases `.` and `..`, then scans entries for exact or first case-insensitive match. Removal slides trailing bytes down, shrinks inline data, updates count and disk size, and may convert from 8-byte inode numbers back to 4-byte if the removed entry was the last large inode number. Replacement handles `..` or a named entry, converts to 8-byte storage when the new inode requires it, can convert to block form if the widened shortform would not fit, and shrinks back to 4-byte encoding if the last large inode number disappears.

`xfs_dir2_sf_verify()` validates minimum size, parent inode, entry bounds, nonzero names, monotonically increasing data offsets, inode numbers, filetype range, exact buffer end, accurate `i8count`, and that the directory still belongs in local format.

## State And Data Structures

The shortform directory is `xfs_dir2_sf_hdr` followed by packed `xfs_dir2_sf_entry` records inside `dp->i_df.if_data`, with `dp->i_df.if_format == XFS_DINODE_FMT_LOCAL` and `dp->i_disk_size == dp->i_df.if_bytes`. Entry offsets preserve the position the entry would occupy in block format, allowing conversion back to block form while maintaining free-space holes.

## Dependencies

Depends on inode local fork resizing, transaction inode logging, block-format conversion helpers, directory comparison/hash utilities, inode data fork size limits, and directory geometry offsets.

## Risks And Invariants

- `i8count` must exactly count parent plus entries requiring 8-byte inode storage.
- Entry offsets must remain monotonically increasing and compatible with later block-format conversion.
- Shortform add/replace must convert to block format before exceeding inline fork size.
- Rebuilding via temporary buffers must preserve filetype bytes and unaligned inode encodings.
- Lookup returns internal `-EEXIST` on success, matching generic directory dispatch expectations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_sf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dquot_buf.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dquot_buf.c

## Purpose

Implements XFS quota dquot buffer verification, repair initialization, buffer verifier operations, quota timer conversion, quota health mask mapping, and loading/creating metadata quota inodes either from legacy superblock inode fields or the metadata directory hierarchy.

## Main Interfaces

- Dquot sizing and verification: `xfs_calc_dquots_per_chunk()`, `xfs_dquot_verify()`, `xfs_dqblk_verify()`, `xfs_dqblk_repair()`.
- Buffer ops: `xfs_dquot_buf_ops`, `xfs_dquot_buf_ra_ops`, internal CRC/struct read/write/readahead verifiers.
- Timer conversion: `xfs_dquot_from_disk_ts()`, `xfs_dquot_to_disk_ts()`.
- Health mapping: `xfs_dqinode_sick_mask()`.
- Quota inode access: `xfs_dqinode_load()`, `xfs_dqinode_metadir_create()`, userspace-only `xfs_dqinode_metadir_link()`, `xfs_dqinode_mkdir_parent()`, `xfs_dqinode_load_parent()`.

## Control Flow And Behavior

Dquot verification checks magic, version, type mask and record type, bigtime feature compatibility, bigtime id constraints, expected id when supplied, and quota soft-limit timer invariants. Disk quota block verification also checks the metadata UUID on CRC-enabled filesystems. Repair zeroes the whole dquot block, writes magic/version/type/id, and writes UUID/checksum when needed.

Buffer CRC verification walks all dquots in a buffer, using quota-info `qi_dqperchunk` when available and falling back to chunk-size calculation during log recovery. Structural verification expects monotonically increasing ids within the buffer, starting from the first dquot id. Normal read verification reports CRC or corruption through buffer verifier errors; readahead verification is silent and marks the buffer `!DONE` with `-EIO` so a later real read re-verifies it. Write verification checks structure but leaves CRC calculation to dquot flush.

Timer conversion supports legacy second-based timers and bigtime-encoded quota timers based on the dquot type flag. Quota inode loading uses legacy superblock quota inode numbers on non-metadir filesystems and named metadata directory lookups when metadir is enabled. Loaded quota inodes are checked for acceptable data fork formats and zero project id; metadata corruption marks the corresponding quota health bit.

Metadata directory helpers create or load the `/quota` directory and quota files, committing metadata directory update transactions and finishing inode setup after creation.

## State And Data Structures

On-disk quota buffers contain repeated `struct xfs_dqblk`, each embedding `struct xfs_disk_dquot` plus optional CRC metadata. Quota inode locations are either superblock fields (`sb_uquotino`, `sb_gquotino`, `sb_pquotino`) or metadata directory entries under `/quota`.

## Dependencies

Depends on quota manager state, CRC helpers, buffer verifier infrastructure, metadata inode loading, metadir/metafile helpers, transaction inode logging, and filesystem health reporting.

## Risks And Invariants

- Readahead verification must remain silent and leave final reporting to a normal read.
- During log recovery, verifier logic cannot assume quota subsystem initialization.
- Dquot ids within a verified buffer are assumed to increase from the first id; corruption of the first id can shift reported failure location.
- Bigtime dquot flags are invalid unless the filesystem supports bigtime.
- Quota inode loading must mark the correct quota health bit on metadata corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_dquot_buf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_errortag.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_errortag.h

## Purpose

Defines XFS error injection tag numbers and the X-macro table used to generate sysfs/debug error injection knobs and default randomization factors for fault testing.

## Main Interfaces

- Numeric constants: `XFS_ERRTAG_NOERROR` through `XFS_ERRTAG_ZONE_RESET`, with `XFS_ERRTAG_MAX` as the array/count bound.
- Default factor: `XFS_RANDOM_DEFAULT`.
- X-macro table: `XFS_ERRTAGS` when the including file defines `XFS_ERRTAG`.

## Control Flow And Behavior

The header supports two include modes. A normal include exposes all `XFS_ERRTAG_*` constants. An include with `XFS_ERRTAG` defined emits `XFS_ERRTAGS`, which expands one row per error injection knob with the symbolic suffix, sysfs knob name, and default randomization factor.

The tags are explicitly documented as consecutive because arrays are sized from the maximum. Removed drop-writes support keeps its numeric definition so attempts to configure that old tag can be rejected as invalid elsewhere.

## State And Data Structures

The file is a macro catalog, not runtime state. It maps error scenarios such as inode flush faults, DA read failures, btree checks, AG header reads, deferred bmap/rmap/refcount steps, quota/metafile reservation failures, writeback delays, exchange-mapping finish failures, and zone reset injection to stable numeric ids and knob names.

## Dependencies

Consumed by XFS error injection code and by call sites using `XFS_TEST_ERROR`, including exchange-mapping code for `XFS_ERRTAG_EXCHMAPS_FINISH_ONE`.

## Risks And Invariants

- Tag numbers must remain consecutive and `XFS_ERRTAG_MAX` must remain one past the last tag.
- Existing tag values are part of debug/test interface expectations and should not be renumbered casually.
- X-macro users depend on each row having exactly suffix, knob name, and default factor.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_errortag.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_exchmaps.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_exchmaps.c

## Purpose

Implements XFS deferred file mapping exchange operations for the exchange-range feature: request validation, mapping discovery, quota and bmap updates, crash-resumable finish steps, post-operation shortform/reflink cleanup, reservation/extent-count estimation, intent allocation, reflink/large-extent-count preparation, and scheduling of exchange intent work.

## Main Interfaces

- Validation and lifecycle: `xfs_exchmaps_check_forks()`, `xfs_exchmaps_intent_init_cache()`, `xfs_exchmaps_intent_destroy_cache()`, `xfs_exchmaps_init_intent()`.
- Deferred execution: `xfs_exchmaps_finish_one()`, `xfs_exchange_mappings()`.
- Estimation: `xfs_exchmaps_estimate()`, `xfs_exchmaps_estimate_overhead()`.
- Inode preparation: `xfs_exchmaps_ensure_reflink()`, `xfs_exchmaps_upgrade_extent_counts()`.
- Internal execution helpers: mapping lookup/skip logic, `xfs_exchmaps_one_step()`, post-op conversion helpers for attributes, directories, and symlinks.

## Control Flow And Behavior

Fork validation rejects missing forks and local-format forks because mapping exchange works on extent/btree mappings. Intent initialization copies inode pointers, start offsets, blockcount, and allowed flags into an in-core deferred intent. Attribute-fork exchanges always request inode2 shortform cleanup; data-fork exchanges can request size swapping, reflink flag cleanup, and shortform cleanup for inode2 directories or symlinks.

`xfs_exchmaps_find_mappings()` walks the two file ranges while both inodes are ILOCKed and page cache has been flushed by callers. It reads one mapping from inode1, optionally skips unwritten or hole mappings when `XFS_EXCHMAPS_INO1_WRITTEN` allows it, reads the corresponding inode2 mapping, trims to the smaller mapping length, and ignores identical physical mappings unless their states differ, which is treated as corruption. Realtime files with large allocation units get special skip/trim rules to avoid exchanging partial unwritten allocation units incorrectly.

`xfs_exchmaps_one_step()` accounts quota deltas, removes both mappings, swaps logical offsets, maps each physical extent into the opposite inode, updates on-disk sizes upward if needed to avoid post-EOF mappings during recovery, and advances the intent cursor. `xfs_exchmaps_finish_one()` performs one exchange step per transaction, swaps final file sizes when requested, runs post-operation cleanup when range exchange is done, injects `EXCHMAPS_FINISH_ONE` failures for testing, and returns `-EAGAIN` when the deferred item needs relogging for more work.

Post-operation cleanup can convert inode2 attr leaf format back to shortform, convert a block-format directory back to shortform, convert a remote symlink target back to local format, and clear reflink flags that are being effectively exchanged. Final completion ensures CoW forks and cowblocks tags match reflink state and CoW fork contents.

Estimation simulates mapping exchanges to count affected data or realtime blocks, number of exchange steps, possible extent-count growth, bmbt reservation overhead, and rmapbt overhead. It models how deleting the current mapping and adding the swapped mapping can merge with left/right neighbors, checks extent-count overflow, applies the error tag that reduces max extent counts, and updates reservation fields in the request.

`xfs_exchange_mappings()` asserts both inodes are exclusively ILOCKed and joined, rejects incompatible flags, creates an intent for nonzero ranges, attaches it to deferred operations, ensures reflink flags are set on both inodes if either side has shared blocks, and upgrades extent-count fields when the filesystem supports large counters.

## State And Data Structures

`struct xfs_exchmaps_intent` tracks the two inodes, current logical offsets, remaining block count, optional final file sizes, and flags. `struct xfs_exchmaps_adjacent` caches left/right bmbt records during estimation. Mapping changes operate on `struct xfs_bmbt_irec` records and are made persistent through deferred log intent/done items outside this file.

## Dependencies

Depends on bmap read/map/unmap helpers, deferred-operation infrastructure, quota accounting, rmap/bmbt transaction reservation formulas, reflink/CoW fork state, attr leaf-to-shortform conversion, directory block-to-shortform conversion, remote symlink read/truncate helpers, inode logging, tracepoints, health marking, and `xfs_errortag.h`.

## Risks And Invariants

- Callers must hold exclusive inode locks, flush delalloc/pagecache, and join inodes to the transaction before scheduling work.
- Mapping discovery assumes no delalloc mappings and exact start offsets; violations are treated as logic errors or invalid input.
- Exchange steps must not create post-EOF mappings visible to log recovery without first raising on-disk size.
- Reservation estimation must conservatively handle bmbt/rmapbt splits and extent counter growth.
- Reflink and CoW fork state must be repaired after data-fork exchanges so later shared-block and preallocation cleanup paths work.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_exchmaps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_exchmaps.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_exchmaps.h

## Purpose

Declares the public libxfs interface and data structures for XFS exchange-mapping operations, including in-core deferred intent state, caller request/estimation state, flag masks, fork selection helpers, cache lifecycle, estimation, inode preparation, deferred finishing, validation, and scheduling.

## Main Interfaces

- Deferred state: `struct xfs_exchmaps_intent`.
- Request and estimate state: `struct xfs_exchmaps_req`.
- Flag masks: internal `__XFS_EXCHMAPS_INO2_SHORTFORM`, `XFS_EXCHMAPS_INTERNAL_FLAGS`, and caller-visible `XFS_EXCHMAPS_PARAMS`.
- Fork helpers: `xfs_exchmaps_whichfork()` and `xfs_exchmaps_reqfork()`.
- API declarations: `xfs_exchmaps_estimate_overhead()`, `xfs_exchmaps_estimate()`, intent cache init/destroy, `xfs_exchmaps_init_intent()`, `xfs_exchmaps_ensure_reflink()`, `xfs_exchmaps_upgrade_extent_counts()`, `xfs_exchmaps_finish_one()`, `xfs_exchmaps_check_forks()`, `xfs_exchange_mappings()`.

## Control Flow And Behavior

Callers populate `xfs_exchmaps_req` with two inodes, source offsets, block count, and operation flags, then zero the estimate-output fields before calling the estimator. The estimator fills block movement counts, reservation blocks, and exchange count. Scheduling converts a request into an `xfs_exchmaps_intent`, which deferred operations repeatedly feed to `xfs_exchmaps_finish_one()` until all mapping and post-operation cleanup work completes.

Fork helper functions derive data versus attr fork selection from `XFS_EXCHMAPS_ATTR_FORK` in either intent or request flags.

## State And Data Structures

`xfs_exchmaps_intent` stores mutable progress: list linkage, two inodes, current offsets, remaining blockcount, optional final sizes, and flags. `xfs_exchmaps_req` stores immutable caller parameters plus estimator outputs for data-device blocks, realtime blocks, transaction reservation blocks, and number of exchange steps.

## Dependencies

Requires XFS inode, transaction, fork, and exchange-range flag definitions from surrounding XFS headers. The implementation uses the declared global `xfs_exchmaps_intent_cache` for intent allocation.

## Risks And Invariants

- Callers must not pass internal flags through the public request path.
- Estimate-output fields must be initialized by the caller before estimation because the estimator adds to them.
- `XFS_EXCHMAPS_SET_SIZES` is data-fork-only in the implementation.
- Intent state is mutable across deferred transaction relogs and must be treated as owned by deferred exchange machinery once scheduled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_exchmaps.h -->