# Group Research: group_1885_xfsprogs_sources_local_fs_xfsprogs_repair_attr_repair_c_sources_loc_71976d516cba

Scope: `Docs/research_subset_a.md`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/attr_repair.c -->
# File Research: sources/local-fs/xfsprogs/repair/attr_repair.c

## Purpose

`attr_repair.c` validates and repairs XFS inode attribute forks during `xfs_repair`. It handles shortform attributes stored inside the inode, longform single-leaf attribute blocks, and node/tree-form attribute forks. It also validates legacy security attribute payloads such as ACLs, IRIX MAC labels, and IRIX capabilities.

The repair policy is conservative: shortform corruption can often be fixed by removing individual entries or truncating the shortform list, while most serious longform leaf/node corruption causes the whole attribute fork to be cleared and converted later to an empty shortform fork.

## Main Responsibilities

- Validate shortform attribute entry layout, sizes, flags, namespaces, names, incomplete flags, parent-pointer support, and selected root security values.
- Validate longform attribute root block 0 and distinguish leaf-form versus node-form attributes by magic number.
- Walk node-form attribute btrees from the leftmost leaf to the rightmost leaf with `da_util.c` path verification.
- Validate leaf entries, name/value heap ownership, hash ordering, sibling links, and header accounting.
- Read and validate remote attribute values where needed for root security attributes.
- Repair limited metadata fields such as shortform count/totsize, leaf `firstused`, leaf `usedbytes`, root sibling links, and stale interior hash values.
- Detect v5 metadata owner, block number, and UUID mismatches.

## Key Functions

- `process_attributes` is the public entry point. It dispatches by `di_aformat` to shortform, extents, or btree processing.
- `process_shortform_attr` validates and optionally mutates the in-inode shortform attribute list.
- `process_longform_attr` reads attribute block zero, checks the v5 header, and dispatches to leaf-root or node-root processing.
- `process_leaf_attr_block` validates one attribute leaf block and its heap/free-space usage.
- `process_leaf_attr_local` validates local leaf entries.
- `process_leaf_attr_remote` validates remote leaf entries and optionally reads remote value blocks.
- `process_node_attr` and `process_leaf_attr_level` traverse node-form attribute btrees.
- `valuecheck`, `xfs_acl_valid`, and `xfs_mac_valid` validate selected root security attribute values.

## Data and Control Flow

Shortform processing starts at `XFS_DFORK_APTR(dip)`, walks `xfs_attr_sf_entry` records, tracks the current byte size, and uses `memmove` to remove bad entries in modify mode. It recomputes `hdr->count` and `hdr->totsize`, then runs `libxfs_attr_shortform_verify` as a final verifier.

Longform processing maps file block zero through the repair `blkmap`, reads it with libxfs buffer verifiers, validates v5 fields, and uses the magic value to determine whether block zero is a leaf or an interior DA node. Leaf-root processing validates only block zero and clears root sibling pointers if needed. Node-root processing releases block zero and then uses `traverse_int_dablock`, `verify_da_path`, and `verify_final_da_path` to validate the full tree.

Leaf validation builds a byte-level free map for the filesystem block, marks the header and every leaf entry, then marks each local or remote name/value payload. Overlapping claims, invalid offsets, invalid flags, invalid namespaces, invalid names, bad hashes, unsupported parent pointers, and bad remote values all force failure.

## Dependencies

This file depends on:

- `bmap.c` for logical attribute block to filesystem block mapping.
- `da_util.c` for DA btree traversal and parent hash verification.
- libxfs attribute, DA node, buffer, and verifier helpers.
- global repair flags such as `no_modify`.
- repair warning/error reporting helpers.
- inode fork definitions from `dinode.h`.

## Important Invariants

- Shortform `totsize` must match the actual validated byte count.
- Shortform and longform entries may use exactly one valid namespace.
- Attribute names must pass `libxfs_attr_namecheck`.
- Parent-pointer attributes are invalid unless the filesystem supports parent pointers.
- Longform leaf hashes must match recomputed hashes and be nondecreasing across the walk.
- Leaf heap bytes and leaf entry bytes must not overlap.
- Node interior keys store the greatest hash value of the child block.
- v5 attribute blocks must have the expected owner inode, disk block number, and metadata UUID.

## Repair and Risk Notes

This file intentionally sacrifices longform attribute forks on many inconsistencies because partial deletion from longform leaves could require format conversion and remote value cleanup. The highest-risk logic is in `process_leaf_attr_block` and tree traversal, where byte-level heap accounting, hash propagation, remote value reads, sibling pointers, and no-modify behavior all interact. Remote attribute block ownership is not fully tracked here; the code validates content enough to decide whether the attribute fork should survive.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/attr_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/attr_repair.h -->
# File Research: sources/local-fs/xfsprogs/repair/attr_repair.h

## Purpose

`attr_repair.h` declares repair-local definitions used by `attr_repair.c`. It defines legacy ACL, MAC label, and capability structures/constants needed to validate root security attribute values, and it declares the `process_attributes` entry point.

## Main Contents

- POSIX ACL tag and permission constants.
- Repair-only in-core ACL structures:
  - `struct xfs_icacl_entry`
  - `struct xfs_icacl`
- IRIX MAC label structure `xfs_mac_label_t` and MSEN/MINT label type constants.
- Attribute names and sizes for `SGI_MAC_FILE` and `SGI_CAP_FILE`.
- IRIX capability structure `xfs_cap_set_t`.
- `process_attributes` prototype.

## Dependencies

The header assumes XFS/libxfs types such as `xfs_mount_t`, `xfs_ino_t`, and `struct xfs_dinode` are available from including code. It forward-declares `struct blkmap`.

## Important Invariants

- `XFS_MAC_MAX_SETS` caps combined MAC category/division lists at 250 entries.
- The ACL structures in this header are repair-local in-core representations, not kernel on-disk structures.
- `process_attributes` is the public bridge from inode processing to attribute fork validation.

## Research Notes

The header exists mainly to preserve validation knowledge for legacy root security attributes while keeping the repair entry point independent from the implementation details in `attr_repair.c`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/attr_repair.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/avl.c -->
# File Research: sources/local-fs/xfsprogs/repair/avl.c

## Purpose

`avl.c` implements a repair-local AVL interval tree. Nodes describe ordered half-open ranges via callbacks supplied in `avlops_t`, and the tree maintains both AVL parent/child links and a separate in-order `avl_nextino` chain for fast sequential scans.

This structure is used by repair code that needs range lookup, adjacency lookup, insertion, deletion, and ordered traversal of non-overlapping intervals.

## Main Operations

- `avl_init_tree` initializes a descriptor with root, first node, and range callbacks.
- `avl_insert` inserts a non-overlapping range and rebalances the tree.
- `avl_insert_immediate` inserts a node immediately after a known node.
- `avl_delete` removes a node and rebalances upward.
- `avl_find` finds a node by exact start value.
- `avl_findrange` is an inline header helper that finds the range containing a value.
- `avl_findanyrange` finds any range intersecting a requested range.
- `avl_findadjacent` finds a containing, predecessor, or successor range.
- `avl_findranges` returns the first and last nodes intersecting a range.
- `avl_firstino` and `avl_lastino` find leftmost and rightmost nodes.

## Data Structure Behavior

Each `avlnode_t` stores:

- `avl_back` for the left child.
- `avl_forw` for the right child.
- `avl_parent` for upward navigation.
- `avl_nextino` for in-order iteration.
- `avl_balance` as `AVL_BACK`, `AVL_BALANCE`, or `AVL_FORW`.

The tree descriptor stores root, first in-order node, callback operations, and flags. Range comparison is driven by `AVL_START(tree, node)` and `AVL_END(tree, node)`, allowing callers to embed AVL nodes inside larger structures.

## Balancing Logic

Insertion uses `avl_insert_find_growth` to locate a non-overlapping insertion point and `avl_insert_grow` to attach the node and fix the in-order chain. `avl_balance` then performs single or double rotations.

Deletion handles degenerate one-child cases and two-child replacement with the greatest lesser descendant. `retreat` propagates height shrinkage upward and performs single or double rotations as needed.

## Debug Support

When `AVL_DEBUG` is enabled, `avl_checknode` and `avl_checktree` assert ordering, parent pointers, balance state, and `nextino` consistency. There is also a disabled `STAND_ALONE_DEBUG` interactive test harness.

## Important Invariants

- Ranges are half-open `[start, end)`.
- Non-zero-length ranges must not overlap existing ranges.
- `avl_firstino` must point to the leftmost node.
- `avl_nextino` must preserve sorted order and terminate at `NULL`.
- Parent pointers must match child links after every rotation.
- Balance values must correspond to actual child presence.

## Repair and Risk Notes

The code is pointer-heavy and predates modern container abstractions. The highest-risk sections are delete replacement, `nextino` maintenance, and rotation parent rewiring. Because range start/end are callback-derived, caller bugs in those callbacks can break all ordering assumptions.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/avl.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/avl.h -->
# File Research: sources/local-fs/xfsprogs/repair/avl.h

## Purpose

`avl.h` declares the repair-local AVL interval tree API and core node/tree structures.

## Main Types

- `avlnode_t` is the embedded node containing left/right/parent pointers, the in-order `avl_nextino` pointer, and balance state.
- `avlops_t` supplies callbacks to compute a node range start and end.
- `avltree_desc_t` stores the tree root, first in-order node, callback table, and flags.

## Public API

The header declares insertion, deletion, initialization, range lookup, adjacency lookup, range enumeration, and first/last helpers. It also provides inline `avl_findrange` for containing-range lookup.

## Constants

- Balance values: `AVL_BACK`, `AVL_BALANCE`, `AVL_FORW`.
- Tree flag: `AVLF_DUPLICITY`.
- Adjacency directions: `AVL_PRECEED`, `AVL_SUCCEED`.
- Range matching modes: `AVL_INCLUDE_ZEROLEN`, `AVL_EXCLUDE_ZEROLEN`.

## Important Invariants

- Callback-provided ranges are the ordering key.
- `avl_findrange` treats ranges as `[start, end)`.
- The API assumes the caller embeds `avlnode_t` in a structure whose range callbacks are stable while the node is in the tree.

## Research Notes

This is a generic local range-tree interface, not an XFS on-disk btree. It is tuned for repair’s interval tracking and ordered inode/range scans.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/avl.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/bmap.c -->
# File Research: sources/local-fs/xfsprogs/repair/bmap.c

## Purpose

`bmap.c` implements a simple repair-local logical-to-physical block map for inode forks. It stores sorted extent records in a dynamically sized array and uses thread-local storage to reuse one data-fork and one attr-fork map per worker thread.

## Main Operations

- `blkmap_alloc` obtains or grows a thread-local map for a fork and resets `nexts`.
- `blkmap_free` releases unusually large maps to avoid pinning memory after pathological files.
- `blkmap_free_final` frees both thread-local maps at thread shutdown.
- `blkmap_set_ext` inserts an extent sorted by logical offset.
- `blkmap_get` maps one logical block to a filesystem block.
- `blkmap_getn` maps a multi-block logical range, optimized for single-extent directory/attr block reads.
- `blkmap_last_off` returns the logical offset just past the last extent.
- `blkmap_next_off` iterates mapped logical offsets while tracking an extent index.

## Data Model

`blkmap_t` contains:

- `naexts`: allocated extent capacity.
- `nexts`: number of active extents.
- `exts[]`: flexible extent array.

Each `bmap_ext_t` records logical start offset, physical filesystem block, and block count.

## Memory and Capacity Handling

The implementation caps allocation at `XFS_MAX_EXTCNT_DATA_FORK_LARGE` and has explicit 32-bit overflow checks around `BLKMAP_SIZE`. `blkmap_grow` grows in small increments for small files and larger increments for fragmented files.

## Important Invariants

- Extents are stored in increasing `startoff` order.
- `blkmap_get` returns `NULLFSBLOCK` if no mapping contains the requested offset.
- `blkmap_set_ext` leaves the caller’s map pointer unchanged on allocation failure.
- Thread-local keys distinguish data fork and attr fork maps.
- `blkmap_getn` may allocate a temporary extent list for non-contiguous logical ranges; callers free it when it is not the supplied single-record buffer.

## Repair and Risk Notes

The implementation is intentionally simpler than libxfs bmap code because repair mostly needs read-only mapping from already decoded inode forks. The main risks are capacity overflow, preserving sorted insertion order, and caller ownership of temporary arrays from `blkmap_getn`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/bmap.h -->
# File Research: sources/local-fs/xfsprogs/repair/bmap.h

## Purpose

`bmap.h` declares the repair-local block map used to map inode fork logical block offsets to filesystem blocks.

## Main Types

- `bmap_ext_t` describes one mapping extent with logical start, physical start, and length.
- `blkmap_t` is a dynamically sized array of extents with capacity and active-count fields.

## Public API

The header exposes allocation, freeing, insertion, single-block lookup, multi-block lookup, last-offset query, and next-offset iteration functions. It also declares the data and attribute fork thread-local keys.

## Important Invariants

- `BLKMAP_SIZE(n)` computes the allocation size for `n` extent records.
- `blkmap_alloc` requires a data or attr fork selector.
- The map is an in-memory repair helper and does not own on-disk metadata.

## Research Notes

This header is small but central to attribute and directory repair because DA blocks are read by first translating file block numbers through this map.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/bmap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/bmap_repair.c -->
# File Research: sources/local-fs/xfsprogs/repair/bmap_repair.c

## Purpose

`bmap_repair.c` rebuilds an inode data or attribute fork block mapping from reverse-mapping metadata. It is used when an inode fork’s extent or bmbt metadata is damaged but rmap data can still identify blocks owned by the inode.

The repair creates a fresh fork in a staged ifork, bulk-loads extents into extents or btree format, commits the staged fork to the inode, resets block counters, and leaves old bmbt blocks to be handled by later space metadata rebuild phases.

## Main Structure

`struct xrep_bmap` holds:

- A slab of new bmap records.
- A slab cursor for sorted bulk loading.
- A `bulkload` context for staging the new fork.
- An `xfs_btree_bload` descriptor.
- Repair context and target fork.
- Recomputed file block ownership counters.
- Count of old bmbt blocks found in rmap records.

## Main Flow

1. `rebuild_bmap` resets the on-disk dinode fork format/count to a zero-extent fork, starts a repair transaction, loads the inode, and calls `xrep_bmap`.
2. `xrep_bmap_check_inputs` rejects unsupported filesystems/forks/formats and skips local/dev/uuid forks.
3. `xrep_bmap_find_mappings` scans realtime rmap btrees and allocation-group rmap btrees.
4. Rmap callbacks filter records owned by the inode and fork, validate ranges/flags, and add bmap records to a slab.
5. `xrep_bmap_build_new_fork` sorts records, stages a fake fork, chooses extents or btree format, and loads the new mappings.
6. The staged bmbt is committed into the real inode fork.
7. Inode block counters are recomputed and unused reservation blocks are freed through `bulkload_commit`.

## Key Functions

- `xrep_bmap_from_rmap` converts one rmap extent into one or more bmbt records, splitting at `XFS_MAX_BMBT_EXTLEN`.
- `xrep_bmap_walk_rmap` handles data-device rmap records.
- `xrep_bmap_walk_rtrmap` handles realtime rmap records.
- `xrep_bmap_extents_load` populates an incore extent tree.
- `xrep_bmap_btree_load` computes btree geometry, reserves blocks, bulk-loads the btree, and populates incore extents.
- `xrep_bmap_reset_counters` updates `i_nblocks` from rmap-discovered blocks plus new bmbt block delta.
- `xrep_ino_ensure_extent_count` enables large extent counts if required and supported.

## Dependencies

This file depends on:

- rmapbt and realtime rmap scanning.
- slab storage and sorting.
- libxfs bmbt and generic btree bulk-loading APIs.
- `bulkload.c` for staging block reservations.
- transaction, inode, and buffer management.
- repair globals and error reporting.

## Important Invariants

- Rebuild requires rmapbt support.
- Data extents for realtime files must not appear on the data device.
- Attribute extents and bmbt blocks must not appear on realtime devices.
- Rmap flags must not combine attr/bmbt ownership with unwritten state.
- File offsets and physical extents must pass libxfs validators.
- The new fork must fit in normal or large extent-count limits.
- Transaction buffer ownership is carefully maintained across inode loading and transaction rolls.

## Repair and Risk Notes

This is a high-impact repair path: once `libxfs_bmbt_commit_staged_btree` succeeds, old fork mapping data are no longer accessible through the inode. The code relies on rmap metadata being more trustworthy than the damaged bmap. The most delicate parts are transaction/buffer handoff in `rebuild_bmap`, realtime/data-device distinction, large extent-count upgrade, and correct accounting for old versus new bmbt blocks.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/bmap_repair.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/bmap_repair.h -->
# File Research: sources/local-fs/xfsprogs/repair/bmap_repair.h

## Purpose

`bmap_repair.h` declares the public entry point for rebuilding an inode fork block map.

## Public API

`rebuild_bmap` takes a mount, inode number, fork selector, expected extent count, caller-held inode buffer/dinode pointers, and dirty flag. It repairs the selected fork and returns updated buffer/dinode pointers because the transaction and inode loading path can release and reacquire the inode cluster buffer.

## Important Invariants

- `whichfork` must select a supported inode fork.
- The caller must be prepared for `ino_bpp` and `dinop` to be refreshed.
- The function coordinates with caller dirty state to persist dinode changes before libxfs inode loading.

## Research Notes

The header is intentionally narrow: all rebuild machinery is private to `bmap_repair.c`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/bmap_repair.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/btree.c -->
# File Research: sources/local-fs/xfsprogs/repair/btree.c

## Purpose

`btree.c` implements a small generic in-memory B-tree mapping unsigned long keys to non-null pointer values. It is repair-local and separate from XFS on-disk btree code. It supports lookup, nearest-key find, ordered cursor movement, insertion, deletion, key/value updates, clearing, destruction, and optional statistics.

## Data Model

- Each node stores up to `BTREE_KEY_MAX` keys, currently 7.
- Each node stores up to 8 child/value pointers.
- Leaves store values in `ptrs`; internal nodes store child pointers.
- `struct btree_root` stores root node, tree height, a reusable path cursor, and lookup cache fields.

## Lookup Behavior

`btree_do_search` descends from root to leaf and records the search path in `root->cursor`. `btree_search` uses a small cache: if the requested key lies between the cached previous key and current key, it reuses the cursor.

Public lookup functions include:

- `btree_lookup` for exact key matches.
- `btree_find` for the first key greater than or equal to the requested key.
- `btree_peek_prev` and `btree_peek_next` around the current cursor.
- `btree_lookup_next` and `btree_lookup_prev` to move the active cursor.

## Mutation Behavior

Insertion rejects null values and duplicate keys. If a node is full, the code first tries to shift entries to previous or next siblings, then increases height if needed, then splits.

Deletion removes the leaf key/value, updates parent separator keys if needed, and handles underflow by merging with siblings or redistributing from siblings. Root height can shrink when the top root becomes empty.

## Key Functions

- `btree_insert_item`
- `btree_split`
- `btree_shift_to_prev`
- `btree_shift_to_next`
- `btree_delete_key`
- `btree_delete_node`
- `btree_balance_with_prev`
- `btree_balance_with_next`
- `btree_update_node_key`

## Important Invariants

- Values must be non-null.
- Keys must remain sorted.
- Nodes must stay within max/min occupancy except transiently during mutation.
- Cursor paths must be invalidated after insert/delete.
- Parent separator keys must track the relevant leaf/internal boundary key.
- Tree height is at least one after initialization.

## Repair and Risk Notes

The implementation uses compact fixed-size nodes and explicit sibling operations instead of a generic library. The most complex areas are cursor copying for neighboring nodes, separator key updates during shifts, and deletion underflow handling. There is a likely typo in a stats guard (`#ifdef btree_stats` lowercase) that means one optional statistic counter is not compiled under the normal `BTREE_STATS` symbol, but it does not affect behavior.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/btree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/btree.h -->
# File Research: sources/local-fs/xfsprogs/repair/btree.h

## Purpose

`btree.h` declares the repair-local generic in-memory B-tree API for unsigned long keys and pointer values.

## Public API

The header declares:

- lifecycle: `btree_init`, `btree_destroy`, `btree_clear`
- state: `btree_is_empty`
- lookup: `btree_lookup`, `btree_find`
- cursor-relative lookup: `btree_peek_prev`, `btree_peek_next`, `btree_lookup_next`, `btree_lookup_prev`
- mutation: `btree_insert`, `btree_delete`, `btree_update_key`, `btree_update_value`
- optional `btree_print_stats` under `BTREE_STATS`

## Important Invariants

- The root type is opaque to callers.
- Values passed to insert/update must be non-null.
- Cursor-relative functions depend on a valid prior lookup/find operation.

## Research Notes

This API is intentionally small and repair-oriented. It exposes enough ordered-map behavior for repair subsystems without exposing node layout or balancing internals.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/btree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/bulkload.c -->
# File Research: sources/local-fs/xfsprogs/repair/bulkload.c

## Purpose

`bulkload.c` provides common reservation and cleanup support for rebuilding XFS btrees in repair. It tracks extents reserved for a new btree, hands blocks to the generic libxfs bulk-loader, frees unused reservations, and estimates btree slack under low-space conditions.

## Main Concepts

A `struct bulkload` owns a list of `bulkload_resv` records. Each reservation records a per-AG reference, starting AG block, length, and number of blocks already consumed. The bulk-loader consumes blocks one at a time through `bulkload_claim_block`.

## Main Functions

- `bulkload_init_ag` initializes state for AG-rooted btree rebuilds.
- `bulkload_init_inode` initializes state for inode-fork btree rebuilds and creates a fake ifork.
- `bulkload_add_extent` adds caller-designated blocks to the reservation list.
- `bulkload_alloc_file_blocks` allocates new blocks for file/inode-rooted btrees.
- `bulkload_claim_block` returns the next reserved block as a btree pointer.
- `bulkload_commit` frees unused reservation space after successful commit.
- `bulkload_cancel` frees all reserved space after failed rebuild.
- `bulkload_estimate_ag_slack` and `bulkload_estimate_inode_slack` tune bulk-load slack.

## Allocation and Cleanup Flow

`bulkload_alloc_file_blocks` repeatedly allocates extents starting near `alloc_hint`, validates the hint against EOFS, adds reservations, advances the hint, and finishes deferred operations. Cleanup uses `libxfs_free_extent_later` to free unused blocks and rolls deferred frees after `XREP_MAX_ITRUNCATE_EFIS` extents.

For committed btrees, used blocks remain allocated and only unused tails are freed. For cancelled rebuilds, every reserved block is freed.

## Important Invariants

- Reservation list entries hold passive per-AG references that must be released.
- `bulkload_claim_block` assumes the first list item still has space unless all space is exhausted.
- Used-up reservations are moved to the tail.
- Long-pointer btrees receive filesystem block pointers; short-pointer btrees receive AG block pointers.
- Inode bulk-load contexts must free the temporary fake ifork.

## Repair and Risk Notes

This file is shared infrastructure for rebuild paths. The important failure mode is incomplete cleanup after ENOSPC or transaction errors. The code tries to free disk reservations even on failure and then always frees incore reservation records.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/bulkload.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/bulkload.h -->
# File Research: sources/local-fs/xfsprogs/repair/bulkload.h

## Purpose

`bulkload.h` declares shared repair infrastructure for staging and bulk-loading rebuilt btrees.

## Main Types

- `struct repair_ctx` groups mount, inode, and transaction pointers.
- `struct bulkload_resv` describes one reserved extent of btree blocks.
- `struct bulkload` tracks reservation state, fake btree roots, owner information, allocation hints, and reserved block counts.

## Public API

The header exposes initialization for AG and inode btrees, block claiming, reservation addition/allocation, cancel/commit cleanup, and slack estimation helpers.

## Constants and Globals

- `bload_leaf_slack` and `bload_node_slack` are global tuning knobs.
- `XREP_MAX_ITRUNCATE_EFIS` caps deferred free extents per transaction roll.

## Important Invariants

- Callers must commit or cancel every initialized bulkload context.
- `for_each_bulkload_reservation` safely iterates reservations while deleting.
- Owner information must match the btree being rebuilt so rmap records are correct.

## Research Notes

This header abstracts the repetitive mechanics of reserving replacement btree blocks, making rebuild code focus on collecting records and configuring libxfs bulk-load callbacks.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/bulkload.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/da_util.c -->
# File Research: sources/local-fs/xfsprogs/repair/da_util.c

## Purpose

`da_util.c` provides shared helpers for repairing XFS directory and attribute DA btrees. It reads possibly non-contiguous DA blocks, traverses interior nodes, maintains a cursor path, verifies parent-child hash propagation, checks sibling pointers, and releases dirty buffers.

## Main Functions

- `da_read_buf` reads one logical DA block from one or more mapped filesystem extents.
- `traverse_int_dablock` walks from the DA root down the left side of the tree and initializes a cursor.
- `release_da_cursor` releases held interior-node buffers in normal paths.
- `err_release_da_cursor` releases held buffers in error paths.
- `verify_da_path` validates and advances parent cursor state when a lower-level traversal crosses a block boundary.
- `verify_final_da_path` validates the final right edge of the tree after all leaves are processed.

## DA Tree Model

Directory and attribute DA interior nodes store `<hashval, before>` entries. Unlike many btrees, the propagated key is the greatest hash value in the child block. The cursor stores, for each level, the current block buffer, file block number, last verified hash value, current entry index, and dirty flag.

## Buffer Handling

`da_read_buf` builds an `xfs_buf_map` array from repair `bmap_ext_t` records. It uses a small stack array for up to four mappings and allocates only for rare multi-extent blocks. Reads use salvage mode and caller-supplied buffer ops.

## Validation Behavior

`traverse_int_dablock` verifies magic values, node levels, node entry counts, and root-to-leaf level consistency. For directories, it handles the special case where the root is a `LEAFN`.

`verify_da_path` checks that the parent entry points to the just-processed child block and that the parent hash matches the child’s greatest hash. If the parent block is exhausted, it validates that block upward, reads the next sibling, checks sibling back pointer/magic/count/level, and updates the cursor.

`verify_final_da_path` checks the rightmost path, including used/count consistency, final forward pointer, child block pointer, and final hash value.

## Repair Behavior

If a parent hash value is stale but the structure is otherwise consistent, the helper updates it in modify mode and marks the buffer dirty. If a buffer had a bad checksum but otherwise validates, it marks the block dirty to force checksum recomputation.

## Important Invariants

- Cursor `active` is the highest tree level.
- Interior node levels must descend by exactly one from root to leaves.
- Parent entries must point to the child file block just processed.
- Parent hash values must equal the child’s greatest hash.
- Rightmost interior blocks must have `forw == 0`.
- Dirty buffers are only written in modify mode.

## Repair and Risk Notes

This code is central to both directory and attribute repair. Its most subtle invariant is that cursor indices often point to the next unprocessed entry, while hash values refer to the last processed child. Mismanaging that off-by-one convention can invalidate the whole path check.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/da_util.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/da_util.h -->
# File Research: sources/local-fs/xfsprogs/repair/da_util.h

## Purpose

`da_util.h` declares shared cursor structures and helper functions for directory/attribute DA btree traversal and validation in repair.

## Main Types

- `struct da_level_state` stores one DA tree level’s buffer, file block number, hash value, entry index, and dirty state.
- `da_bt_cursor_t` stores active depth, inode number, greatest DA block number seen, dinode pointer, per-level states, and the fork block map.

## Public API

The header declares DA block reading, cursor release, interior traversal, regular path verification, and final right-edge verification functions.

## Important Invariants

- `level` has `XFS_DA_NODE_MAXDEPTH` entries.
- `blkmap` must map DA file blocks to filesystem blocks before traversal.
- The same helpers serve directory and attribute forks, selected by `whichfork`.

## Research Notes

This header captures repair’s local model of a DA btree cursor. It is intentionally independent of libxfs runtime cursors because repair needs salvage reads and custom validation/repair behavior.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/da_util.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/dino_chunks.c -->
# File Research: sources/local-fs/xfsprogs/repair/dino_chunks.c

## Purpose

`dino_chunks.c` validates, discovers, and processes inode allocation chunks during `xfs_repair`. It checks inode blocks, reconstructs missing inode chunk records when possible, processes known and uncertain inode records, updates incore block-state maps, handles sparse inode clusters, and records inode state needed by later repair phases.

## Main Responsibilities

- Validate candidate inode blocks with basic dinode checks.
- Verify whether an uncertain inode belongs to a valid inode chunk.
- Add verified missing inode chunks to the good inode tree.
- Mark inode blocks in the incore block map.
- Process every inode in a known chunk through `process_dinode`.
- Correct inode allocation map state when disk inode state disagrees.
- Handle sparse inode clusters and optionally punch all-bad sparse clusters.
- Track directory status, parent inode numbers, file type, and on-disk nlink count.
- Mark special filesystem inodes as needing reconstruction if they are cleared.

## Key Functions

- `check_aginode_block` reads one filesystem block and counts dinodes that pass uncertain verification.
- `verify_inode_chunk` tries to establish a valid chunk around a candidate inode and inserts a good inode record if successful.
- `verify_aginode_chunk` and `verify_aginode_chunk_irec` are AG-relative wrappers.
- `process_inode_agbno_state` updates the incore block map for an inode block.
- `process_inode_chunk` reads cluster buffers and processes all inodes covered by one allocation unit.
- `process_aginodes` walks the known good inode tree for an AG.
- `check_uncertain_aginodes` validates uncertain records before normal processing.
- `process_uncertain_aginodes` validates and immediately processes uncertain records discovered after the main AG pass.

## Inode Chunk Discovery

`verify_inode_chunk` has three major cases:

- Filesystems with multiple chunks per block (`ialloc_blks == 1`) validate the block directly and create records for all chunks in the block.
- Aligned inode filesystems round down to the inode alignment and validate the full aligned allocation.
- Older unaligned filesystems search around the candidate block, use nearby known inode records to tighten the range, scan outward until non-inode blocks are found, and accept a chunk-sized valid range if it does not conflict with allocated data.

When accepted, the code creates an inode record, marks all inodes free by default, marks the discovered inode used, and marks backing blocks as `XR_E_INO`.

## Inode Processing Flow

`process_inode_chunk` reads all cluster buffers for the chunk unless a cluster is sparse. In discovery mode, it first verifies whether enough dinodes are valid to keep the chunk; if no valid inodes are found, the caller can delete the records.

For each present inode, it calls `process_dinode`, updates dirty buffers and CRCs, reconciles free/in-use state in the incore inode record, stores file type and nlink count, tracks directory parent information, and handles cleared special inodes.

Sparse cluster inconsistencies are handled by marking affected inodes sparse and free if the imap claims present inodes inside a skipped sparse cluster.

## Special Inode Handling

If a cleared inode is one of the root, metadata directory, realtime bitmap, realtime summary, rtgroup bitmap, rtgroup summary, rtgroup rmap, or rtgroup refcount inodes, the code sets global flags so later phases can rebuild or avoid dependent checks.

## Dependencies

This file depends on:

- AVL-backed inode record trees from repair incore state.
- AG block-state bitmap helpers.
- dinode verification and processing from `dinode.h`/related repair code.
- prefetch/progress coordination.
- sparse inode geometry and libxfs inode buffer verifiers.
- realtime and rmap/refcount repair state helpers.

## Important Invariants

- Inode chunks must align to `XFS_INODES_PER_CHUNK`.
- Multi-chunk-per-block filesystems may require synthesizing missing chunk records to cover a full inode allocation.
- Blocks already claimed by file data or metadata conflicts are marked multiply claimed unless metadata-directory reconstruction makes overlap tolerable.
- Sparse inodes occur at cluster granularity for the handled punching path.
- Dirty dinodes have CRCs recalculated before buffers are released.
- Uncertain inode trees are destroyed as they are checked/processed.

## Repair and Risk Notes

This file is a core phase-3/phase-4 repair bridge: it turns uncertain references into inode records, processes actual dinodes, and feeds later directory/link-count phases. The hardest logic is unaligned legacy chunk discovery and the interaction between sparse clusters, missing inobt records, and avoiding data loss from falsely claiming user data as inode chunks.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/dino_chunks.c -->