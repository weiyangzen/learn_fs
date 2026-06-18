# subset-b-005732

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/alloc.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/alloc.c

## Purpose

`fs/ocfs2/alloc.c` is the main OCFS2 extent-allocation, extent-tree mutation, truncate-log, delayed-deallocation, inline-data conversion, and fstrim implementation. It abstracts OCFS2 extent trees behind `struct ocfs2_extent_tree` so the same insertion, split, removal, merge, and path-rotation machinery can serve dinode data extents, xattr tree roots, xattr values, indexed-directory roots, and refcount trees. It also manages persistence details for extent blocks, cached metadata frees, truncate-log replay, cluster zeroing around truncation, and global-bitmap discard.

## Important APIs, types, and functions

The central private contract is `struct ocfs2_extent_tree_operations`, with callbacks for last leaf block, cluster-count updates, optional extent-map updates, insert/sanity checks, root-list discovery, leaf extent size limits, and alternate contiguousness checks. Concrete operation tables cover dinodes, xattr values, xattr trees, dx roots, and refcount trees. Public initializers `ocfs2_init_dinode_extent_tree()`, `ocfs2_init_xattr_tree_extent_tree()`, `ocfs2_init_xattr_value_extent_tree()`, `ocfs2_init_dx_root_extent_tree()`, and `ocfs2_init_refcount_extent_tree()` populate the generic tree object.

Tree/path helpers include `ocfs2_read_extent_block()`, `ocfs2_validate_extent_block()`, `ocfs2_new_path_from_et()`, `ocfs2_find_path()`, `ocfs2_find_leaf()`, `ocfs2_search_extent_list()`, `ocfs2_find_cpos_for_left_leaf()`, `ocfs2_find_cpos_for_right_leaf()`, `ocfs2_find_subtree_root()`, `ocfs2_path_bh_journal_access()`, and `ocfs2_journal_access_path()`. They traverse on-disk btrees, validate extent blocks with ECC/signature/generation/count checks, and expose root-to-leaf paths for mutation.

Extent insertion is centered on `ocfs2_insert_extent()` and `ocfs2_add_clusters_in_btree()`. Supporting functions classify inserts (`ocfs2_figure_insert_type()`), coalesce physically/logically adjacent leaf records (`ocfs2_extent_rec_contig()`), grow trees (`ocfs2_grow_tree()`, `ocfs2_shift_tree_depth()`, `ocfs2_add_branch()`), rotate leaves to make room (`ocfs2_rotate_tree_right()`), append to rightmost paths, and finally write a leaf via `ocfs2_insert_at_leaf()`/`ocfs2_insert_path()`.

Extent updates and removal are exposed through `ocfs2_split_extent()`, `ocfs2_change_extent_flag()`, `ocfs2_mark_extent_written()`, `ocfs2_remove_extent()`, and `ocfs2_remove_btree_range()`. They split records, merge adjacent compatible records, update unwritten/refcount flags, update extent maps, reserve extra metadata when record truncation can split extents, and handle refcount-tree coordination before freeing shared extents.

Truncation and deallocation APIs include `ocfs2_commit_truncate()`, `ocfs2_zero_range_for_truncate()`, `ocfs2_truncate_log_append()`, `__ocfs2_flush_truncate_log()`, `ocfs2_flush_truncate_log()`, `ocfs2_begin_truncate_log_recovery()`, `ocfs2_complete_truncate_log_recovery()`, `ocfs2_cache_block_dealloc()`, `ocfs2_cache_cluster_dealloc()`, and `ocfs2_run_deallocs()`. Inline-data support is provided by `ocfs2_dinode_new_extent_list()`, `ocfs2_set_inode_data_inline()`, `ocfs2_convert_inline_data_to_extents()`, and `ocfs2_truncate_inline()`. Discard support is provided by `ocfs2_trim_fs()`, `ocfs2_trim_mainbm()`, `ocfs2_trim_group()`, and `ocfs2_trim_extent()`.

## Control flow

Initialization selects an operation table, root buffer, root extent list, caching info, and root journal-access function. Most mutation paths first build an `ocfs2_path`, traverse to a target or rightmost leaf, reserve journal access for every changed buffer, modify little-endian on-disk records in memory, then dirty the affected buffers. Extent-block reads always pass through `ocfs2_read_extent_block()`, which uses `ocfs2_validate_extent_block()` to reject checksum failures, bad signatures, block-number mismatches, generation mismatches, and invalid list counts.

Insertion begins by building an extent record, running tree-specific insert checks, and calling `ocfs2_figure_insert_type()`. If the new record is contiguous with an existing leaf record and does not exceed any maximum leaf size, insertion can extend that record in place. If it is a tail append, the rightmost path is updated and parent edge lengths are adjusted. If no leaf record slot is free, `ocfs2_grow_tree()` either shifts the root to a deeper tree or adds a rightmost branch before `ocfs2_do_insert_extent()` performs the final leaf insertion.

The rotation paths preserve btree ordering and parent ranges. Right rotation starts from the rightmost leaf and moves records rightward until the target leaf has an empty first slot or enough space. Left rotation removes empty first slots after deletion by pulling records from the right, possibly unlinking an empty rightmost subtree and updating `last_eb_blk`. Parent records are repaired with `ocfs2_complete_edge_insert()`, `ocfs2_adjust_adjacent_records()`, `ocfs2_adjust_root_records()`, `ocfs2_update_edge_lengths()`, and `ocfs2_adjust_rightmost_records()`.

Splitting and flag changes find the leaf containing `cpos`, verify the requested subrange lies inside the existing record, synthesize a replacement `split_rec`, and then either replace the whole record, split the old record, or merge into compatible neighbors. `ocfs2_mark_extent_written()` first validates the unwritten-extents feature bit and truncates the dinode extent map before clearing `OCFS2_EXT_UNWRITTEN`.

Range removal uses `ocfs2_remove_btree_range()`. It handles refcounted extents by locking/preparing the refcount tree, reserves metadata needed for possible splits, serializes with the truncate-log inode, flushes a full truncate log, starts a journal transaction, removes the extent range, decrements tree cluster counts, updates fsync transaction state, and either appends freed physical clusters to the truncate log or decreases refcounts. `ocfs2_commit_truncate()` loops over the rightmost leaf until all extents beyond the new size are removed, scheduling truncate-log flush and running cached metadata deallocations at the end.

The truncate log is append-optimized and recovery-aware. Appends coalesce adjacent cluster ranges when possible. Flushing first forces a JBD2 journal flush to avoid replay double-free hazards, locks the global bitmap inode, and replays records from tail to head by clearing each truncate-log entry before freeing clusters. Node recovery copies and clears a dead slot's truncate log in stage one, then appends copied ranges into the local truncate log in stage two.

Delayed metadata deallocation accumulates extent-block and cluster frees in `struct ocfs2_cached_dealloc_ctxt`. `ocfs2_run_deallocs()` later locks each relevant suballocator inode and frees cached bits in independent transactions, then appends cached cluster frees to the truncate log. Tree growth can opportunistically reuse extent blocks cached in the dealloc context through `ocfs2_reuse_blk_from_dealloc()`.

Inline-data conversion reserves one cluster when the inode has inline bytes, copies inline data into a locked folio, maps and dirties it, clears `OCFS2_INLINE_DATA_FL`, reinitializes the dinode extent list, and inserts a single extent for the newly allocated cluster. Fstrim takes a cluster-wide trim lock, avoids duplicate shared-device discard if another node just completed the same request, walks global bitmap groups, finds free bitmap runs at least `minlen`, and calls `sb_issue_discard()`.

## State and persistence behavior

Persistent state mutated here includes dinode extent lists, extent blocks, `i_last_eb_blk`, dinode/xattr/dx/refcount cluster counters, extent record flags, `h_next_leaf_blk` leaf chains, extent-block suballocator metadata, truncate-log dinodes, global bitmap suballocator bits, inline-data/extents layout, inode size/timestamps for inline truncate, and fstrim lock result information. The implementation stores all on-disk fields in little-endian form and updates ECC/check fields where direct recovery writes bypass the journal.

In-memory state includes `ocfs2_path` buffer references, extent maps, inode `ip_clusters` and `ip_dyn_features`, local allocation reservations, quota reservations, cached deallocation lists, delayed work for truncate-log flushing, `osb->truncated_clusters`, folio cache state, and DLM-backed trim lock state. Journal access calls are the persistence boundary for normal metadata changes; buffers are dirtied only after the correct root, dinode, extent-block, truncate-log, or bitmap access mode has been obtained.

Cluster frees are intentionally staged. Data clusters removed from trees are usually appended to the truncate log rather than immediately returned to the global bitmap, and the truncate log is flushed later or under pressure. Metadata extent blocks removed during rotations are cached until locks can be acquired without deadlock. Refcounted extent deletion updates the refcount tree instead of freeing physical clusters directly.

## Dependencies and integration points

This file depends on OCFS2 core layout definitions, metadata cache helpers, JBD2 journaling, buffer-head IO, DLM lock glue, extent maps, local/global allocation, suballocator/system-file helpers, quota accounting, refcount-tree helpers, xattr structures, indexed directory roots, page-cache folio APIs, ordered-data journaling, Linux discard APIs, tracepoints from `ocfs2_trace.h`, and error-reporting helpers that can remount on corruption. It is called by file write/extend, fallocate, hole punch, truncate, xattr, refcount/COW, directory indexing, mount/recovery, shutdown, and FITRIM paths.

## Risks and edge cases

The highest-risk code is structural btree mutation: empty extents are legal only as the first leaf record, parent `e_cpos` and interior cluster ranges must mirror child boundaries, and `h_next_leaf_blk` plus `last_eb_blk` must be kept consistent when rightmost leaves are added or deleted. Left-contiguous inserts at leaf boundaries, cross-extent-block merges, and split ranges that move during rotation are specifically guarded by path re-searches and parent repair routines.

Persistence risks include missing journal access before buffer mutation, insufficient transaction credits during rotations, freeing clusters before truncate-log safety requirements are met, and reusing cached deallocation blocks with stale buffer contents. Refcounted extents add locking and accounting risk because deletion may become refcount decrement rather than physical free. Inline-data conversion has a narrow failure window after copying data to the page cache and before inserting the extent; the code tracks quota and allocation rollback with `need_free`/`did_quota`.

Geometry-sensitive paths include maximum xattr leaf size, non-sparse versus sparse allocation checks, cluster-to-block conversions, folio ranges that straddle EOF, first global bitmap group discard offsets, partial last trim groups, and `OCFS2_MAX_PATH_DEPTH`. Many corruption branches call `ocfs2_error()` and return `-EROFS`/`-EFSCORRUPTED`, while internal invariant failures are `BUG_ON()` or `mlog_bug_on_msg()`, so malformed trees can be fatal.

## Test signals

Test insertion into empty root lists, contiguous left/right merges, noncontiguous inserts that grow depth from 0 to 1 and beyond, tail appends, full-leaf rotations, and xattr tree leaf-size limits. Exercise split-left, split-right, left-right split, whole-record replacement, unwritten-to-written conversion, and cross-leaf merge cases. Removal tests should cover full record deletion, left-edge and right-edge truncation, middle punch requiring split, rightmost branch deletion, and cleanup of empty extent blocks.

Truncate-log tests should fill the log, coalesce adjacent records, flush under allocation pressure, replay after simulated crash, and recover another slot's truncate log without double-freeing clusters. Refcount tests should remove shared extents with and without a prelocked refcount tree. Inline-data tests should convert empty and nonempty inline files, validate quota rollback on allocation failure, and truncate inline byte ranges. Deallocation tests should verify cached extent-block reuse and eventual suballocator free ordering. Fstrim tests should cover duplicate trim suppression across nodes, first cluster group offsets, `minlen` filtering, fatal signal interruption, and partial-range trimming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/alloc.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/alloc.h

## Purpose

`fs/ocfs2/alloc.h` declares the public OCFS2 allocation and extent-tree API implemented by `alloc.c`. It is the interface used by OCFS2 file, xattr, directory-index, refcount, truncate, and trim code to initialize generic extent trees, insert/remove/split extents, manage truncate logs, run delayed deallocations, convert inline data, and traverse extent btrees.

## Important APIs, types, and functions

`OCFS2_MAX_XATTR_TREE_LEAF_SIZE` caps xattr tree leaf extent size at 64 KiB. `struct ocfs2_extent_tree` is the generic extent-tree handle: it carries the private operation table, root buffer, root extent list, caching info, root journal access function, typed backing object, optional maximum leaf clusters, and optional cached-deallocation context. Initializers are declared for dinode, xattr tree, xattr value, dx root, and refcount extent trees.

The header exposes extent IO and mutation APIs: `ocfs2_read_extent_block()`, `ocfs2_insert_extent()`, `ocfs2_add_clusters_in_btree()`, `ocfs2_split_extent()`, `ocfs2_mark_extent_written()`, `ocfs2_change_extent_flag()`, `ocfs2_remove_extent()`, `ocfs2_remove_btree_range()`, and `ocfs2_num_free_extents()`. `enum ocfs2_alloc_restarted` tells callers whether an allocation retry is due to transaction exhaustion or missing metadata reservation.

Inline and truncate APIs include `ocfs2_dinode_new_extent_list()`, `ocfs2_set_inode_data_inline()`, `ocfs2_convert_inline_data_to_extents()`, `ocfs2_zero_range_for_truncate()`, `ocfs2_commit_truncate()`, and `ocfs2_truncate_inline()`. Truncate-log APIs include initialization/shutdown, scheduling, flushing, recovery begin/complete, fullness checks, append, direct flush, and pressure-relief helpers.

Delayed deallocation is described by `struct ocfs2_cached_dealloc_ctxt`, `ocfs2_init_dealloc_ctxt()`, `ocfs2_cache_cluster_dealloc()`, `ocfs2_cache_block_dealloc()`, `ocfs2_dealloc_has_cluster()`, and `ocfs2_run_deallocs()`. `struct ocfs2_truncate_context` bundles cached deallocation, allocator lock state, and the last extent-block buffer for truncate commit setup. `ocfs2_trim_fs()` is the exported FITRIM entry point.

The path API defines `struct ocfs2_path_item`, `OCFS2_MAX_PATH_DEPTH`, `struct ocfs2_path`, path accessor macros, and traversal/journaling helpers such as `ocfs2_reinit_path()`, `ocfs2_free_path()`, `ocfs2_find_path()`, `ocfs2_new_path_from_path()`, `ocfs2_new_path_from_et()`, `ocfs2_path_bh_journal_access()`, `ocfs2_journal_access_path()`, `ocfs2_find_cpos_for_right_leaf()`, `ocfs2_find_cpos_for_left_leaf()`, and `ocfs2_find_subtree_root()`.

## Control flow

Callers normally initialize an `ocfs2_extent_tree` from the object they are modifying, reserve data and metadata alloc contexts as needed, start a journal transaction, and call insert/split/remove helpers. When adding clusters through `ocfs2_add_clusters_in_btree()`, callers pass `logical_offset` by reference so partial allocation can advance it before returning `-EAGAIN` with a restart reason. Range removal may require an initialized `ocfs2_cached_dealloc_ctxt` so metadata blocks deleted during rotations can be freed after the journaled tree update completes.

Tree traversal uses `struct ocfs2_path` as a root-to-leaf buffer-head stack. The root is stored at index 0 and the leaf at `p_tree_depth`; the macros hide those index calculations. Callers that modify any path buffer must first call `ocfs2_path_bh_journal_access()` or `ocfs2_journal_access_path()`, using the path's root-specific journal function for index 0 and extent-block journal access for deeper nodes.

Truncate callers use zeroing helpers before shrinking visible size, then `ocfs2_commit_truncate()` to remove extents after inode sizes are already adjusted. Delayed frees are accumulated in the context and later released through `ocfs2_run_deallocs()` after broad filesystem locks and journal handles are no longer held.

## State and persistence behavior

The header defines the state containers but not the persistence implementation. `struct ocfs2_extent_tree` binds an on-disk root buffer to a journal access function and typed object, so callers do not need to know whether the tree belongs to a dinode, xattr block/value, dx root, or refcount block. `et_dealloc` allows tree operations to coordinate with delayed metadata free state without immediately locking suballocator inodes.

`ocfs2_extend_meta_needed()` deliberately returns a conservative worst-case metadata requirement of current tree depth plus two blocks: one for each existing level, one new leaf extent block, and one new top-of-tree block. This lets callers reserve enough metadata before complex insert/split operations without walking and locking the whole tree.

`ocfs2_rec_clusters()` encodes an important on-disk layout distinction: interior records use `e_int_clusters`, while leaf records use `e_leaf_clusters` because leaf records reserve space for flags such as unwritten/refcounted state. `ocfs2_is_empty_extent()` is valid only on leaves, where a zero leaf cluster count marks the special empty record used by rotation logic.

## Dependencies and integration points

The declarations rely on OCFS2 layout structures such as `ocfs2_dinode`, `ocfs2_extent_list`, `ocfs2_extent_rec`, `ocfs2_xattr_value_buf`, and `ocfs2_super`; Linux VFS types such as `inode`, `super_block`, `buffer_head`, `folio`, and `fstrim_range`; JBD2 `handle_t`; OCFS2 caching and journal access function types; allocation contexts; and cached deallocation internals. This header is included by OCFS2 allocation users across file data, xattr, directory index, refcount tree, truncate, and mount/recovery code.

## Risks and edge cases

The interface requires callers to pass a root extent list when using `ocfs2_extend_meta_needed()`; passing an interior or leaf list can under-reserve metadata. `OCFS2_MAX_PATH_DEPTH` is a hard structural limit for btree traversal and must match on-disk maximum depth assumptions. Misusing `ocfs2_rec_clusters()` on the wrong tree depth or `ocfs2_is_empty_extent()` on an interior record can corrupt logical range calculations. Many APIs assume locks, quota reservations, alloc contexts, and journal handles were prepared by the caller.

Delayed deallocation APIs separate cache population from actual freeing; callers must eventually invoke `ocfs2_run_deallocs()` or cached metadata/cluster frees will not be returned. Truncate-log functions require the truncate-log inode locking protocol documented in the implementation. Path objects hold buffer references, so every successful allocation via `ocfs2_new_path_from_*()` must be released with `ocfs2_free_path()`.

## Test signals

Compile-test all OCFS2 users after signature or struct changes. Runtime tests should exercise each extent-tree initializer, path traversal on depth-0 and multi-level trees, path reinitialization with and without root preservation, journal access over mixed root/extent-block paths, conservative metadata reservation for full trees, empty-extent detection during rotations, delayed dealloc lifecycle, truncate-log append/flush/recovery, inline-data conversion/truncation, and FITRIM entry from VFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/alloc.h -->
