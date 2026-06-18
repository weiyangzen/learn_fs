# Group Research: group_629_jfsutils_sources_local_fs_jfsutils_fsck_fsckdtre_c_sources_local_fs__af53e8a316a2

Scope: `Docs/research_subset_a.md` includes `sources/local-fs/jfsutils`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckdtre.c -->
# File Research: sources/local-fs/jfsutils/fsck/fsckdtre.c

## Purpose
Implements JFS fsck directory dTree support: adding/removing directory entries, searching directory B+ trees, validating dTree structure, recording/unrecording directory node extents, checking leaf inode references, reconnecting orphaned filesystem inodes through `/lost+found`, and rebuilding damaged directory index cookies.

## Main Elements
- Directory entry mutation:
  - `direntry_add()` wraps `fsck_dtInsert()` and writes the parent inode back with `inode_put()`.
  - `direntry_remove()` finds the child name with `direntry_get_objnam()`, then calls `fsck_dtDelete()`.
- Directory lookup/name extraction:
  - `direntry_get_inonum()` searches the root directory dTree for a name and returns the stored inode number.
  - `direntry_get_objnam()` locates the leftmost leaf and scans leaf siblings for an entry with a target inode number.
  - `direntry_get_objnam_node()` reconstructs a possibly multi-slot Unicode name from `ldtentry` plus continuation slots.
- Search helpers:
  - `dTree_binsrch_internal_page()` selects the child slot whose key range may contain a target name.
  - `dTree_binsrch_leaf()` performs leaf-level binary search, using case folding for OS/2-compatible case-insensitive directories.
  - `dTree_search()` walks internal nodes using the binary-search helpers, then searches the final leaf.
- Key handling:
  - `dTree_key_compare()` implements lexicographic UniChar key comparison.
  - `dTree_key_compare_leaflvl()`, `dTree_key_compare_prntchld()`, and `dTree_key_compare_samelvl()` enforce different ordering rules for leaves, parent/child boundaries, and internal siblings.
  - `dTree_key_extract()`, `dTree_key_extract_cautiously()`, and `dTree_key_extract_record()` assemble segmented keys and detect malformed chains, repeated slots, overlong names, embedded nulls, and out-of-range slot indices.
  - `dTree_key_to_upper()` applies JFS OS/2 case-folding semantics through `UniToupper()`.
- Structural validation:
  - `dTree_processing()` is the main validator/recorder. It checks root and page header fields, sorted table placement, slot freelists, sibling chains, self PXD consistency, node sizes, level transitions, key ordering, and leaf/internal type consistency.
  - `dTree_process_internal_slots()` records child extents through `process_extent()`, updates aggregate/inode block counters, and queues child nodes.
  - `dTree_process_leaf_slots()` validates sorted leaf keys and, during `FSCK_RECORD_DUPCHECK`, validates child inode references, increments observed link counts, records parent extensions, schedules bad-entry removals, and calls `verify_dir_index()`.
  - `dTree_verify_slot_freelist()` verifies that every slot is either in a key chain/header/sorted table or on the freelist exactly once.
  - Node-position helpers validate forward/back sibling chains and first/last node rules.
- Valid-tree extent processing:
  - `process_valid_dir_data()` and `process_valid_dir_node()` reprocess already-validated internal dTree nodes to record, unrecord, or query extents without doing full structural validation.
- Directory initialization and repair:
  - `find_first_dir_leaf()` descends through the first child chain to locate the leftmost leaf.
  - `init_dir_tree()` initializes an empty inline root-leaf dTree.
  - `reconnect_fs_inodes()` adds entries for disconnected inodes into `/lost+found`, updates `/lost+found` link count for directories, and emits summary messages.
  - `rebuild_dir_index()` traverses all leaf entries and resets their `index` field while recalculating directory block accounting; non-root leaf pages are written back.

## Control Flow
`dTree_processing()` starts at the inline root in `di_btroot`, initializes per-node slot tracking, validates root sanity fields, extracts the first key cautiously, then processes either leaf or internal slots. Internal entries enqueue child nodes with their PXD, address, level, size, and boundary key. The function then breadth-first walks queued nodes, validating sibling links and level boundaries as it advances. Each non-root node is read with `dnode_get()`, checked against its queued self PXD, classified as leaf or internal, validated for header/sorted-table/free-list bounds, processed, and released back to the dTree queue pool.

The same validator is used in multiple phases. During `FSCK_RECORD_DUPCHECK`, it reports inconsistencies and records extents/link observations. During later `FSCK_UNRECORD`, `FSCK_RECORD`, or `FSCK_QUERY` passes, it preserves the first-pass corruption stop point by temporarily clearing and then rechecking `inorecptr->ignore_alloc_blks`; mismatched outcomes become internal errors.

## Dependencies And Integration
This file depends on fsck globals from `xchkdsk.c` (`sb_ptr`, `agg_recptr`, shared key buffers), JFS Unicode/case-folding helpers, dTree queue helpers, inode record/extension allocation, `process_extent()`, `verify_dir_index()`, `dnode_get()`, `inode_get()`, `inode_put()`, and low-level disk write helpers.

Primary callers are in `fsckino.c`, `fsckmeta.c`, and `xchkdsk.c`. `fsckino.c` invokes `dTree_processing()` while validating directory inodes and uses `process_valid_dir_data()` once a tree is already considered structurally valid. `xchkdsk.c` calls `rebuild_dir_index()` for directories flagged for index-table rebuild and `direntry_remove()` for scheduled bad directory entries.

## Behavioral Notes
The code distinguishes structural dTree corruption from bad leaf inode references. Bad child inode references in leaf entries are only checked during `FSCK_RECORD_DUPCHECK`, because they do not necessarily imply that the B+ tree layout itself is unusable.

For indexed directories (`JFS_DIR_INDEX`), leaf entry header payload size and directory table handling differ from legacy directories. For OS/2-compatible directories (`JFS_OS2`), leaf comparisons and searches fold names to uppercase while preserving original mixed-case names.

`direntry_get_inonum()` accepts a `parent_inonum` parameter but reads `ROOT_I` directly, so the implementation is effectively root-directory lookup despite the broader parameter documentation.

## Risk Notes
This file sits on critical repair paths. Incorrect validation can either leak or double-count directory node extents, incorrectly mark a tree corrupt, or trust a corrupt tree long enough to mutate the wrong entries. The highest-risk areas are segmented key reconstruction, slot freelist accounting, sibling-chain validation, `ignore_alloc_blks` consistency across record/unrecord passes, and the manual directory-index rebuild writeback path.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckdtre.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckea.c -->
# File Research: sources/local-fs/jfsutils/fsck/fsckea.c

## Purpose
Validates the byte-level structure of a JFS extended attribute FEALIST used by fsck when checking inline and extent-backed extended attributes.

## Main Elements
- `FEA_SIZE(ea)`: computes one full FEA record length from little-endian value length, name length, null terminator, and fixed `struct FEA` header.
- `NEXT_FEA(ea)`: advances to the next FEA record by `FEA_SIZE()`.
- `GEA_SIZE()` / `NEXT_GEA()`: analogous get-EA-list helpers, defined here but unused in this file.
- `jfs_ValidateFEAList()`: validates the list byte count and each variable-length FEA record.

## Control Flow
`jfs_ValidateFEAList()` reads `pfeal->cbList` as little-endian, requires it to match the caller-supplied buffer size, subtracts the list length field, and accepts an otherwise empty list. It then walks records until no bytes remain. For each record it rejects reserved `fEA` flag bits, rejects headers that do not fit in the remaining bytes, computes the record size, advances to the next record, and reports inconsistency if the record extends beyond the remaining list bytes. On overrun, it stores the error offset in `*poError`.

## Dependencies And Integration
Declared through `xfsck.h` and called from `fsckino.c` during EA validation. Inline EAs are validated directly from the inode’s inline EA area after DXD bounds checks. Extent-backed EAs are first validated as extents, read into fsck’s EA buffer, and then passed here with the EA byte size from the inode DXD.

## Behavioral Notes
The validator checks list framing and reserved flag bits only. It does not validate EA name character sets, semantic name rules, duplicate names, value content, or alignment beyond what is implied by the packed record sizes.

## Risk Notes
The function relies on the caller to provide a buffer at least as large as `size` and on prior inode/DXD validation to ensure that `size` is meaningful. It is intentionally small, but because FEA records are variable-length on-disk data, integer sizing and remaining-byte checks are the key correctness boundary.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckea.c -->