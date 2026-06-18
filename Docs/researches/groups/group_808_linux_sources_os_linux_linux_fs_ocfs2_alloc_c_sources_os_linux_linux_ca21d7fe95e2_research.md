# Group Research: group_808_linux_sources_os_linux_linux_fs_ocfs2_alloc_c_sources_os_linux_linux_ca21d7fe95e2

Scope: `Docs/research_subset_a.md`

Files researched:
- `sources/os/linux/linux/fs/ocfs2/alloc.c`
- `sources/os/linux/linux/fs/ocfs2/alloc.h`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/alloc.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/alloc.c

## Purpose

`alloc.c` is OCFS2's core extent allocation, extent b-tree editing, truncation, delayed deallocation, inline-data conversion, truncate-log, and fstrim implementation. It supplies a generic extent-tree engine used by multiple OCFS2 metadata owners, not only file dinodes:

- regular inode data extent trees;
- xattr value extent trees;
- xattr tree block extent trees;
- indexed directory dx root extent trees;
- refcount tree extent trees.

The file is large because it owns the complete lifecycle of extent records: inserting newly allocated clusters, growing and rotating b-trees, splitting and merging leaf records, changing unwritten/refcount-related extent flags, removing ranges, caching metadata frees until allocator locks can be taken safely, replaying cluster frees through truncate logs, zeroing partial truncate ranges, converting inline data to extents, committing file truncation, and issuing discard/trim over the main bitmap.

## Extent Tree Abstraction

The file defines `struct ocfs2_extent_tree_operations`, a private vtable used by the public `struct ocfs2_extent_tree` declared in `alloc.h`. The vtable abstracts root-object details:

- how to read and write the root's `last_eb_blk`;
- how to update the owning object's cluster count;
- whether to update an extent map;
- optional insert and sanity checks;
- how to locate the root `ocfs2_extent_list`;
- optional maximum leaf extent size;
- optional custom contiguity rules.

Concrete operation sets are implemented for:

- `ocfs2_dinode_et_ops`: updates `ocfs2_dinode.i_last_eb_blk`, `i_clusters`, inode in-memory `ip_clusters`, and the inode extent map. Its insert check rejects sparse allocation when the filesystem lacks sparse allocation support and disallows inline-data owners.
- `ocfs2_xattr_value_et_ops`: roots at `ocfs2_xattr_value_root.xr_list`, tracks `xr_last_eb_blk` and `xr_clusters`.
- `ocfs2_xattr_tree_et_ops`: roots at `ocfs2_xattr_tree_root.xt_list`, tracks `xt_last_eb_blk` and `xt_clusters`, and caps leaf extents to `OCFS2_MAX_XATTR_TREE_LEAF_SIZE`.
- `ocfs2_dx_root_et_ops`: roots at `ocfs2_dx_root_block.dr_list`, tracks `dr_last_eb_blk` and `dr_clusters`, and checks `OCFS2_IS_VALID_DX_ROOT`.
- `ocfs2_refcount_tree_et_ops`: roots at `ocfs2_refcount_block.rf_list`, tracks `rf_last_eb_blk` and `rf_clusters`, and disables normal extent coalescing by always returning `CONTIG_NONE`.

The exported initializers (`ocfs2_init_dinode_extent_tree`, `ocfs2_init_xattr_tree_extent_tree`, `ocfs2_init_xattr_value_extent_tree`, `ocfs2_init_dx_root_extent_tree`, and `ocfs2_init_refcount_extent_tree`) all call `__ocfs2_init_extent_tree`, which installs the vtable, root buffer, caching info, root journaling function, root object pointer, optional deallocation context, root extent list, and maximum leaf cluster limit.

## Path Model

The file manipulates allocation trees through `struct ocfs2_path`, which stores a root and up to `OCFS2_MAX_PATH_DEPTH` path nodes. A path node contains a buffer head and an `ocfs2_extent_list`. The helpers:

- reset and free paths (`ocfs2_reinit_path`, `ocfs2_free_path`);
- copy and move path contents internally (`ocfs2_cp_path`, `ocfs2_mv_path`);
- create paths from an extent tree or another path (`ocfs2_new_path_from_et`, `ocfs2_new_path_from_path`);
- insert extent blocks into a path (`ocfs2_path_insert_eb`);
- journal individual path nodes or whole paths (`ocfs2_path_bh_journal_access`, `ocfs2_journal_access_path`);
- find the leaf/path for a logical cluster (`ocfs2_find_path`, `ocfs2_find_leaf`);
- find neighboring leaf search keys (`ocfs2_find_cpos_for_left_leaf`, `ocfs2_find_cpos_for_right_leaf`);
- find the common subtree root for adjacent leaves (`ocfs2_find_subtree_root`).

Path traversal is handled by `__ocfs2_find_path`. It walks interior extent records by logical cluster range, reads child extent blocks through `ocfs2_read_extent_block`, validates tree depth, record counts, nonzero child block numbers, and can deliberately accept a `cpos` past the current tree to return the rightmost path.

## Extent Block Validation

`ocfs2_validate_extent_block` validates cached extent block reads. It checks metadata ECC, signature, self block number, filesystem generation, expected extent record count, and `l_next_free_rec <= l_count`. ECC failure is reported as local to the block; structural failures call `ocfs2_error`, making them filesystem errors. `ocfs2_read_extent_block` wraps `ocfs2_read_block` with this validator and returns a referenced buffer head.

## Extent Record Semantics

The file distinguishes interior and leaf records:

- interior records use `e_int_clusters`;
- leaf records use `e_leaf_clusters` and may carry extent flags such as `OCFS2_EXT_UNWRITTEN` and `OCFS2_EXT_REFCOUNTED`;
- only leaf records can be "empty" records, represented by zero `e_leaf_clusters`.

Contiguity is tested with:

- `ocfs2_extents_adjacent`: logical adjacency;
- `ocfs2_block_extent_contig`: physical block adjacency;
- `ocfs2_extent_rec_contig`: logical + physical adjacency with matching flags;
- `ocfs2_et_extent_contig`: vtable-aware wrapper, with refcount trees overriding normal coalescing.

Insertion planning uses:

- `enum ocfs2_contig_type`: none, left, right, or both-side contiguity;
- `enum ocfs2_append_type`: non-append or tail append;
- `enum ocfs2_split_type`: no split, left split, or right split;
- `struct ocfs2_insert_type`: computed insert plan;
- `struct ocfs2_merge_ctxt`: merge decision state for split/flag-change paths.

## Tree Growth

When a leaf has no free record for a non-contiguous insert, the file grows the b-tree:

- `ocfs2_create_new_meta_bhs` claims extent metadata blocks, initializes extent block signatures, block numbers, suballocator origin fields, generation, and list capacity, and journals them as created.
- `ocfs2_sum_rightmost_rec` computes the logical end of a list's rightmost record.
- `ocfs2_adjust_rightmost_branch` repairs stale rightmost parent ranges before branch addition when the root's theoretical range exceeds the rightmost leaf's actual end.
- `ocfs2_add_branch` allocates a whole empty branch of extent blocks, links it to the previous rightmost leaf through `h_next_leaf_blk`, inserts the top block into the target list, and updates `last_eb_blk`.
- `ocfs2_shift_tree_depth` creates a new extent block from the current root list, promotes the root one level, and converts the root into a single-record interior list.
- `ocfs2_find_branch_target` searches the rightmost side for the lowest interior list with room, falling back to root room or signaling that the tree must shift depth.
- `ocfs2_grow_tree` orchestrates depth shift and branch addition.

The growth path can reuse recently deleted extent blocks from `et->et_dealloc` via `ocfs2_reuse_blk_from_dealloc`, which reinitializes the reused buffer as a fresh extent block in the current transaction.

## Leaf Rotation And Parent Repair

OCFS2 uses explicit b-tree rotations to make room in leaves or remove empty slots:

- `ocfs2_shift_records_right`, `ocfs2_rotate_leaf`, `ocfs2_remove_empty_extent`, and `ocfs2_create_empty_extent` handle leaf-array reshuffling.
- `ocfs2_adjust_adjacent_records`, `ocfs2_adjust_root_records`, and `ocfs2_complete_edge_insert` repair parent record `e_cpos` and `e_int_clusters` after records move between adjacent leaves.
- `ocfs2_rotate_subtree_right` moves the rightmost record from a full left leaf into an empty slot at the start of the right leaf, then repairs interior records.
- `ocfs2_rotate_tree_right` repeatedly rotates adjacent subtrees right from the rightmost leaf toward the target insertion point. It may return a left path requiring post-insert edge repair.
- `ocfs2_rotate_subtree_left` moves records left after deletion creates an empty record, with special handling for rightmost leaf deletion and empty right leaves.
- `ocfs2_rotate_tree_left` drives left rotations and removes the rightmost path when a leaf becomes empty.
- `ocfs2_remove_rightmost_path` unlinks a rightmost branch, frees extent blocks through the cached deallocation context, updates `last_eb_blk`, and can collapse the root back to inline extent records when the last branch is removed.

Transaction credit extension is centralized in `ocfs2_extend_rotate_transaction`, which ensures rotations can journal both sides of an affected subtree plus caller-required credits.

## Insertion Flow

`ocfs2_insert_extent` is the main exported logical insert primitive. It constructs an `ocfs2_extent_rec`, runs vtable insert checks, computes an insert plan with `ocfs2_figure_insert_type`, grows the tree if needed, and calls `ocfs2_do_insert_extent`. On success it updates the extent map when the tree type supports one.

Planning includes:

- free record count in the rightmost leaf;
- current tree depth;
- whether the new record can coalesce with an existing leaf record;
- whether it is a tail append;
- whether left-contiguous cases at a leaf edge must be treated as non-contiguous to force tree repair.

Actual insertion uses:

- `ocfs2_insert_at_leaf` for depth-zero or already prepared leaves;
- `ocfs2_append_rec_to_path` for appends that need rightmost parent range updates;
- `ocfs2_rotate_tree_right` for non-contiguous insertion requiring an empty slot;
- `ocfs2_split_record` and `ocfs2_insert_path` for split-aware insertions.

`ocfs2_add_clusters_in_btree` combines physical cluster allocation with extent insertion. It checks for enough metadata reservation, claims clusters from the data allocation context, journals the root early, inserts the extent at `*logical_offset`, advances the caller's logical offset, and returns `-EAGAIN` with `RESTART_META` or `RESTART_TRANS` when the caller must restart with more metadata or transaction space. If insertion fails after cluster claim, it frees claimed bits back to local allocation or the global cluster allocator.

## Split, Merge, Flag Change, And Unwritten Extents

`ocfs2_split_extent` is the central partial-record mutation primitive. It verifies that the requested split range lies inside the original record, determines whether the replacement range can merge with left/right neighbors, reads the rightmost leaf if needed, and either:

- replaces a fully covered record;
- grows/splits/inserts using `ocfs2_split_and_insert`;
- merges into neighbors using `ocfs2_try_to_merge_extent`.

Merge helpers include:

- `ocfs2_figure_merge_contig_type`, which checks neighboring records in the same leaf and adjacent leaf blocks;
- `ocfs2_merge_rec_left` and `ocfs2_merge_rec_right`, which can merge across extent blocks and repair parent records;
- `ocfs2_cleanup_merge`, which turns consumed records into a single legal empty extent slot.

`ocfs2_change_extent_flag` changes flags over an existing logical range by building a replacement split record with modified flags and calling `ocfs2_split_extent`. It validates that new flags are not already set and clear flags are present before changing them.

`ocfs2_mark_extent_written` is the exported unwritten-extent conversion path. It verifies that the superblock supports unwritten extents, truncates the inode extent map conservatively, and clears `OCFS2_EXT_UNWRITTEN` over the requested range with `ocfs2_change_extent_flag`.

## Range Removal And Truncate

`ocfs2_remove_extent` removes a logical range from an extent tree. It truncates the extent map, finds the containing leaf record, and handles three cases:

- removal covers a full record;
- removal touches the left or right edge of a record;
- removal is in the middle, so `ocfs2_split_tree` first splits the record at the right boundary, then a normal edge removal handles the target range.

`ocfs2_truncate_rec` edits or removes one leaf record and then rotates away any empty extent. It updates left-edge parent records when a leaf's first real record changes and adjusts rightmost parent lengths when the right edge shrinks.

`ocfs2_remove_btree_range` is the higher-level exported range removal entry point. It handles refcounted extent preparation and locking, reserves metadata for record truncation, locks the truncate-log inode, flushes the truncate log if full, starts a transaction, frees quota space, removes the extent from the tree, updates cluster counts and fsync transaction state, and either decreases refcounts or appends physical clusters to the truncate log. Metadata frees are stored in the caller-provided cached deallocation context.

`ocfs2_commit_truncate` loops over the rightmost extent path of a dinode after `i_size` has already been changed. It repeatedly removes tail records or tail portions until the inode allocation matches the new highest cluster. It handles empty rightmost extent blocks, refcounted tail extents, extent map truncation, truncate-log scheduling, and cached deallocation execution.

`ocfs2_zero_range_for_truncate` zeroes partial clusters before truncate or hole punch so stale data is not exposed on later extension. It only operates on sparse-capable filesystems, clamps work to current `i_size`, maps the physical extent, skips holes and unwritten extents, grabs folios covering the range, zeroes and maps buffers, records ordered-data writes when needed, and starts writeback for the zeroed range.

## Truncate Log

OCFS2 defers cluster bitmap frees through per-slot truncate-log inodes. This file implements:

- `ocfs2_truncate_log_needs_flush`: true when `tl_used == tl_count`;
- `ocfs2_truncate_log_append`: append or coalesce a freed physical cluster range into the local truncate log under `tl_inode` lock;
- `ocfs2_replay_truncate_records`: free truncate-log records back to the global bitmap one transaction at a time, clearing each record before freeing clusters;
- `__ocfs2_flush_truncate_log` and `ocfs2_flush_truncate_log`: flush the local truncate log, including a journal flush before replay to avoid double-free after crash replay of append and flush transactions;
- `ocfs2_schedule_truncate_log_flush`: delayed work scheduling with cancellation support;
- `ocfs2_try_to_free_truncate_log`: opportunistic flush when allocation may succeed if truncated clusters are released;
- `ocfs2_begin_truncate_log_recovery`: copy and clear another slot's truncate log during node recovery;
- `ocfs2_complete_truncate_log_recovery`: append recovered records into the local truncate log, flushing as needed;
- `ocfs2_truncate_log_init` and `ocfs2_truncate_log_shutdown`: acquire/release the local truncate-log inode and buffer and drain pending work.

The truncate log is tightly serialized with `osb->osb_tl_inode` locking. Several paths assert the inode lock is already held by using `BUG_ON(inode_trylock(tl_inode))`.

## Cached Deallocation

The file implements a delayed deallocation system for metadata blocks and clusters:

- `struct ocfs2_cached_block_free` stores one block/suballocator free or one cluster-range free.
- `struct ocfs2_per_slot_free_list` groups block frees by suballocator inode type and slot.
- `ocfs2_cache_block_dealloc` records extent-block/suballocator frees.
- `ocfs2_cache_cluster_dealloc` records cluster frees for truncate-log append.
- `ocfs2_cache_extent_block_free` extracts suballocator information from an extent block.
- `ocfs2_run_deallocs` drains all cached frees after the caller has dropped locks that would make allocator locking unsafe.

Block frees are executed by `ocfs2_free_cached_blocks`, which opens and locks the relevant system inode, starts one transaction per cached block, and calls `ocfs2_free_suballoc_bits`. Cluster frees are executed by `ocfs2_free_cached_clusters`, which appends ranges to the truncate log and flushes it when full.

This deferred design is important because extent block deletions can involve suballocator inodes from multiple slots and would otherwise create difficult lock-ordering problems deep inside unrelated extent mutations.

## Inline Data And Dinode Layout

The file includes helpers for switching a dinode between inline-data and extent-list layouts:

- `ocfs2_zero_dinode_id2_with_xattr` clears the `id2` union while preserving inline xattr space when present.
- `ocfs2_dinode_new_extent_list` initializes an empty root extent list sized for the inode/xattr layout.
- `ocfs2_set_inode_data_inline` sets the in-memory and on-disk inline-data feature flags and initializes `id_count`.
- `ocfs2_convert_inline_data_to_extents` reserves one cluster when inline data exists, starts a transaction, claims a data cluster, copies inline bytes into a folio, maps and dirties it, clears the inline-data feature, initializes an extent list, inserts a single cluster extent, updates quota/failures correctly, and frees claimed clusters if conversion fails after allocation.
- `ocfs2_truncate_inline` zeroes a byte range inside inline data and optionally updates `i_size`, timestamps, block count, fsync transaction state, and the dinode.

## Folio And Buffer Handling

`ocfs2_map_and_dirty_folio` maps folio buffers to physical blocks, optionally zeroes a segment, marks buffers uptodate/dirty through `walk_page_buffers`, registers ordered-data writes with JBD2 when required, marks the folio uptodate if no partial buffers remain, and flushes dcache. Supporting helpers grab folios over a truncate range and release them through OCFS2's folio unlock/free helper.

## Fstrim

The trim implementation scans the global bitmap and issues discard for sufficiently large free ranges:

- `ocfs2_trim_extent` translates cluster offsets to block discard ranges and handles the first cluster group specially because its descriptor is offset from group start.
- `ocfs2_trim_group` scans a group descriptor bitmap for zero-bit runs at least `minlen` clusters long, issues discard, tracks trimmed clusters, and aborts on fatal signals.
- `ocfs2_trim_mainbm` locks the global bitmap inode, walks affected cluster groups, releases locks between groups to avoid starving I/O, and stores the resulting trimmed byte length in `range->len`.
- `ocfs2_trim_fs` serializes cluster-wide trim with the OCFS2 trim lock. If another node just completed the same trim successfully, it reuses that result and avoids duplicate discard on shared storage.

## Locking, Journaling, And Error Model

Nearly all metadata mutations are journaled before modification. Root objects use tree-specific journal access functions, while extent blocks use `ocfs2_journal_access_eb`. The code frequently extends active JBD2 transactions before rotations or branch edits because one logical operation can touch both adjacent leaf paths and their shared ancestors.

Important locks and serialization points:

- inode and system-file mutexes around truncate logs and allocator inodes;
- OCFS2 inode cluster locks in external callers, with this file taking allocator/refcount/truncate-log locks as needed;
- refcount tree locks around deletion of refcounted extents unless the caller already holds the lock;
- trim lock resource to coordinate fstrim between cluster nodes.

Corruption paths usually call `ocfs2_error` and return `-EROFS` or a specific negative errno. Internal logic invariants often use `BUG_ON`/`mlog_bug_on_msg`, especially for impossible path/record states after prior validation.

## Key Invariants

- `last_eb_blk` points at the rightmost leaf extent block when tree depth is nonzero.
- Interior records describe child logical ranges and should not contain holes.
- Empty leaf extents are legal only as the first record in a leaf.
- Leaf record coalescing requires matching extent flags and physical/logical adjacency, unless a tree type overrides contiguity.
- Rightmost parent record lengths must be updated whenever the rightmost leaf end changes.
- Deleting the only branch collapses the root back to depth zero and clears `last_eb_blk`.
- Truncate-log records are cleared before the corresponding clusters are freed to make crash replay safe.
- Cached deallocation must be drained after the main extent mutation transaction and after conflicting locks have been dropped.

## External Dependencies

This file is coupled to most of OCFS2's core subsystems:

- journaling: `journal.h`, JBD2 handles, metadata access and dirtying helpers;
- block validation/ECC: `blockcheck.h`;
- extent map cache: `extent_map.h`;
- allocator/suballocator: `suballoc.h`, `localalloc.h`, `sysfile.h`;
- inode state and inline data: `inode.h`, `file.h`, `aops.h`;
- refcount trees: `refcounttree.h`;
- xattrs: `xattr.h`;
- cluster locks and trim locks: `dlmglue.h`;
- folio/page-cache helpers and buffer-head I/O.

## Research Notes

This file is not a simple allocator. It is the consistency core for OCFS2 extent metadata. The most fragile areas are the cross-leaf rotations, split/merge operations that cross extent blocks, and range deletion on refcounted extents because they couple tree shape, transaction credits, deallocation deferral, and parent range repair. Any change here should be tested with extent-heavy workloads: sparse writes, unwritten extent conversion, hole punching, full and partial truncation, inline-to-extent conversion, xattr tree growth, reflink/refcounted range deletion, forced ENOSPC/restart paths, crash recovery around truncate logs, and clustered fstrim.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/alloc.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/alloc.h

## Purpose

`alloc.h` is the public interface for OCFS2 allocation and extent-tree manipulation implemented mostly by `alloc.c`. It declares the generic extent-tree abstraction, path abstraction, truncate-log API, cached deallocation API, inline-data conversion/truncation helpers, b-tree search helpers, and fstrim entry point used by other OCFS2 files.

## Extent Tree Interface

The header declares `struct ocfs2_extent_tree`, the caller-visible object that represents any OCFS2 extent b-tree root. It contains:

- private operation table pointer `et_ops`;
- root buffer head `et_root_bh`;
- root extent list `et_root_el`;
- caching info `et_ci`;
- root journal access callback `et_root_journal_access`;
- root object pointer `et_object`;
- optional `et_max_leaf_clusters` limit;
- optional cached deallocation context `et_dealloc`.

The header documents that callers must initialize this structure with one of the provided initializers before using the allocation code:

- `ocfs2_init_dinode_extent_tree`;
- `ocfs2_init_xattr_tree_extent_tree`;
- `ocfs2_init_xattr_value_extent_tree`;
- `ocfs2_init_dx_root_extent_tree`;
- `ocfs2_init_refcount_extent_tree`.

This allows `alloc.c` to operate generically on dinode data, xattr data, xattr tree blocks, indexed directory roots, and refcount trees while preserving owner-specific cluster counters, journaling, and last-leaf fields.

`OCFS2_MAX_XATTR_TREE_LEAF_SIZE` is defined as 65536 bytes and is used by xattr tree extent handling to cap leaf extent size.

## Core Extent Operations

The header exports the primary b-tree operations:

- `ocfs2_read_extent_block`: cached and validated read of an extent block.
- `ocfs2_insert_extent`: insert a logical-to-physical extent record into an initialized extent tree.
- `ocfs2_add_clusters_in_btree`: claim clusters and insert them into an extent tree, with restart reporting.
- `ocfs2_split_extent`: split or replace a leaf extent record and merge adjacent compatible records.
- `ocfs2_mark_extent_written`: convert unwritten extents to written extents over a range.
- `ocfs2_change_extent_flag`: set/clear extent flags over a range.
- `ocfs2_remove_extent`: remove a logical extent range from a tree.
- `ocfs2_remove_btree_range`: high-level removal path that also handles quota, truncate log, refcount trees, and cached deallocation.
- `ocfs2_num_free_extents`: count free records in the relevant leaf for future metadata planning.

`enum ocfs2_alloc_restarted` communicates why `ocfs2_add_clusters_in_btree` returned a restart condition:

- `RESTART_NONE`;
- `RESTART_TRANS`;
- `RESTART_META`.

`ocfs2_extend_meta_needed` is an inline conservative estimator for the maximum number of new metadata blocks needed by an allocation. It returns `root_el->l_tree_depth + 2`, covering a block per current level, one new depth-zero extent block, and one new top-level block. The comment explicitly requires `root_el` to be the actual root list.

## Dinode, Inline Data, And Truncate Helpers

The header exports helpers for changing dinode storage format:

- `ocfs2_dinode_new_extent_list`: initialize a dinode as an empty extent-list owner.
- `ocfs2_set_inode_data_inline`: initialize inline-data storage in a dinode.
- `ocfs2_convert_inline_data_to_extents`: move inline file data into a real allocated extent.

Truncation-related exports include:

- `ocfs2_zero_range_for_truncate`: zero partial clusters before truncate/hole punch.
- `ocfs2_commit_truncate`: remove extents after inode size has been adjusted.
- `ocfs2_truncate_inline`: zero/truncate inline data.

`struct ocfs2_truncate_context` combines a cached deallocation context with truncate-specific state, including whether the extent allocator is locked and the last extent block buffer. The header notes that parts of it are destroyed once passed to commit-truncate logic.

## Truncate Log API

The header exposes the truncate-log lifecycle and recovery interface:

- `ocfs2_truncate_log_init`;
- `ocfs2_truncate_log_shutdown`;
- `ocfs2_schedule_truncate_log_flush`;
- `ocfs2_flush_truncate_log`;
- `__ocfs2_flush_truncate_log`;
- `ocfs2_begin_truncate_log_recovery`;
- `ocfs2_complete_truncate_log_recovery`;
- `ocfs2_truncate_log_needs_flush`;
- `ocfs2_truncate_log_append`;
- `ocfs2_try_to_free_truncate_log`.

These functions let other OCFS2 code append freed cluster ranges, flush local truncate logs, recover another slot's truncate log during node recovery, and opportunistically flush logs to satisfy allocation pressure.

## Cached Deallocation API

`struct ocfs2_cached_dealloc_ctxt` stores delayed frees:

- `c_first_suballocator`: grouped block frees by system inode type and slot;
- `c_global_allocator`: cluster frees destined for the global allocator/truncate log.

The inline initializer `ocfs2_init_dealloc_ctxt` clears both lists. Exported helpers:

- `ocfs2_cache_cluster_dealloc`: queue cluster-range deallocation;
- `ocfs2_cache_block_dealloc`: queue suballocator block deallocation;
- `ocfs2_dealloc_has_cluster`: test whether cluster frees are queued;
- `ocfs2_run_deallocs`: execute all cached frees later, outside sensitive lock scopes.

The comments explain the intended usage: allocation-tree routines may cache block unlinks locally, and callers should call `ocfs2_run_deallocs` after deallocating routines complete, without open journal handles and after most locks are dropped.

## Extent Record Helpers

The header provides two important inline helpers:

- `ocfs2_rec_clusters`: returns the record cluster count using `e_int_clusters` for interior nodes and `e_leaf_clusters` for leaves. This hides the on-disk format difference caused by leaf extent flags.
- `ocfs2_is_empty_extent`: true when a leaf record has zero `e_leaf_clusters`; the comment notes this is only valid for leaf nodes.

It also declares `ocfs2_search_extent_list`, which finds the record containing a logical cluster in either interior or leaf lists.

## Path Interface

The header defines:

- `struct ocfs2_path_item`: buffer head plus extent list pointer;
- `OCFS2_MAX_PATH_DEPTH` as 5;
- `struct ocfs2_path`: tree depth, root journal access callback, and fixed node array.

Macros expose root and leaf buffer/list access:

- `path_root_bh`, `path_root_el`, `path_root_access`;
- `path_leaf_bh`, `path_leaf_el`;
- `path_num_items`.

Exported path functions:

- `ocfs2_reinit_path`;
- `ocfs2_free_path`;
- `ocfs2_find_path`;
- `ocfs2_new_path_from_path`;
- `ocfs2_new_path_from_et`;
- `ocfs2_path_bh_journal_access`;
- `ocfs2_journal_access_path`;
- `ocfs2_find_cpos_for_right_leaf`;
- `ocfs2_find_cpos_for_left_leaf`;
- `ocfs2_find_subtree_root`.

These are used by allocation, refcount, xattr, and other OCFS2 subsystems that need to navigate or modify extent b-trees while preserving journaling semantics.

## Folio And Trim Entry Points

`ocfs2_map_and_dirty_folio` maps a folio range to physical blocks, optionally zeroes it, marks buffers dirty/uptodate, and integrates ordered-data journaling. It is declared here because allocation/truncation and inline conversion code need the helper across compilation units.

`ocfs2_trim_fs` is the exported fstrim entry point for OCFS2. Its implementation in `alloc.c` scans the global bitmap and uses cluster-wide trim locking to avoid duplicate discard from multiple nodes.

## Research Notes

This header is the contract for OCFS2's generic extent-tree machinery. Its most important design point is that extent editing is not tied directly to `ocfs2_dinode`; callers provide an initialized `ocfs2_extent_tree`, and `alloc.c` dispatches owner-specific root updates through operations installed by the initializer. Consumers must respect the documented sequencing around journaling, metadata reservation, truncate-log locking, and delayed deallocation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/alloc.h -->