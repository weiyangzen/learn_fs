# Group Research: group_1050_linux_stable_sources_os_linux_linux_stable_fs_ocfs2_alloc_c_sources_60090d98d211

Scope: `Docs/research_subset_a.md`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/alloc.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/alloc.c

Purpose: implements OCFS2 extent allocation, generic extent b-tree mutation, truncate-log management, delayed metadata/data deallocation, inline-data conversion, partial-cluster zeroing for truncation and hole punching, and filesystem trim. This is the central extent-tree engine used by regular file dinodes, xattr value roots, xattr tree roots, directory index roots, and refcount trees.

Read coverage: complete file read, 7741 lines.

Key structures and state:
- `struct ocfs2_extent_tree_operations` is the root-type vtable. It abstracts last leaf block access, cluster-count updates, extent-map maintenance, insertion validation, root extent-list discovery, optional leaf-size limits, sanity checks, and custom contiguity rules.
- `struct ocfs2_extent_tree` instances are initialized for dinode, xattr tree, xattr value, dx root, and refcount roots. Dinode trees also update `OCFS2_I(inode)->ip_clusters` under `ip_lock` and keep the inode extent map coherent.
- `struct ocfs2_path` is a root-to-leaf traversal object. Each item owns a buffer-head reference and an extent-list pointer; helpers copy, move, reinitialize, journal, and free paths.
- Insert decisions use `enum ocfs2_contig_type`, `enum ocfs2_append_type`, `enum ocfs2_split_type`, `struct ocfs2_insert_type`, and `struct ocfs2_merge_ctxt` to classify appends, contiguous merges, tree growth, splits, rotations, and full-record replacement.
- Delayed frees use `struct ocfs2_cached_block_free`, `struct ocfs2_per_slot_free_list`, and `struct ocfs2_cached_dealloc_ctxt` to separate block-suballocator frees from global-cluster frees and to postpone lock-heavy deallocation until after tree mutation.

Major logic:
- Extent-tree initialization wires the root buffer, caching info, root journal-access function, backing object, root extent list, optional max leaf cluster limit, and operation table. Refcount trees deliberately disable normal leaf-record coalescing.
- Extent block reads go through `ocfs2_read_extent_block()` and validate metadata ECC, signature, block number, filesystem generation, record capacity, and `l_next_free_rec` before the block is accepted.
- Metadata growth allocates new extent blocks or reuses extent blocks captured in a delayed deallocation context, initializes extent-block headers, shifts root depth, adds branches, links rightmost leaves through `h_next_leaf_blk`, and updates `last_eb_blk`.
- Path search traverses interior records by logical cluster range. The same traversal backend supports full path construction and leaf-only lookup.
- Insert logic computes whether a new record is contiguous, a tail append, or a non-contiguous insertion. It grows the tree when the rightmost leaf has no free slots, then inserts by direct leaf write, merge, append, split, or rotation.
- Right rotations create an empty slot in a target leaf by moving records across adjacent leaves and updating parent edge ranges. Left rotations remove empty slots, rebalance neighboring leaves, and can unlink a now-empty rightmost path.
- Split and merge logic handles left-edge, right-edge, and middle splits. It checks adjacent records in the same leaf and neighboring leaves, prefers merges that avoid tree growth, and repairs cross-leaf parent ranges after movement.
- `ocfs2_change_extent_flag()` and `ocfs2_mark_extent_written()` change extent flags by constructing replacement split records and reusing the split/merge machinery. Mark-written also rejects unwritten extents if the superblock feature bit is missing.
- Range removal uses `ocfs2_remove_extent()` and `ocfs2_truncate_rec()` to delete full records, shrink edge records, or split middle removals into an edge case. `ocfs2_remove_btree_range()` wraps that with quota accounting, refcount-tree handling, truncate-log appends, journal transactions, and delayed deallocation.
- The truncate log batches freed data clusters in a per-slot truncate-log system inode. Append can coalesce adjacent tail records; flush forces a JBD2 journal flush before replay to avoid crash-replay double frees.
- Truncate-log recovery reads another slot's truncate log, stamps it clean in stage one, then replays its copied records into the local truncate log for normal processing.
- Delayed deallocation groups metadata-block frees by system inode type and slot, writes them back later through suballocator inodes, and sends global-cluster frees through the truncate log.
- Folio helpers map file blocks, zero requested byte ranges, mark buffers dirty/uptodate, order data for journaled write modes, and start writeback for partial-cluster truncation.
- Inline-data conversion reserves one cluster when needed, moves inline bytes into the page cache, clears `OCFS2_INLINE_DATA_FL`, initializes an on-disk extent list, inserts the first extent, updates quota/i_blocks, and rolls back quota/cluster allocation on late failure where possible.
- `ocfs2_commit_truncate()` repeatedly walks the rightmost extent path, removes full or partial tail allocation beyond the new file size, handles refcounted extents, schedules truncate-log flushing, and drains delayed deallocations.
- Trim scans the global bitmap group by group under OCFS2 trim cluster locking, issues `sb_issue_discard()` for free runs at least `range->minlen`, releases bitmap locks between groups to avoid starving I/O, and records lock-value-block info so another node can avoid duplicate trim.

Important entry points:
- Extent-tree setup: `ocfs2_init_dinode_extent_tree()`, `ocfs2_init_xattr_tree_extent_tree()`, `ocfs2_init_xattr_value_extent_tree()`, `ocfs2_init_dx_root_extent_tree()`, `ocfs2_init_refcount_extent_tree()`.
- Tree/path utilities: `ocfs2_read_extent_block()`, `ocfs2_num_free_extents()`, `ocfs2_find_path()`, `ocfs2_find_leaf()`, `ocfs2_search_extent_list()`, `ocfs2_find_cpos_for_left_leaf()`, `ocfs2_find_cpos_for_right_leaf()`, `ocfs2_find_subtree_root()`.
- Allocation and mutation: `ocfs2_insert_extent()`, `ocfs2_add_clusters_in_btree()`, `ocfs2_split_extent()`, `ocfs2_change_extent_flag()`, `ocfs2_mark_extent_written()`, `ocfs2_remove_extent()`, `ocfs2_remove_btree_range()`.
- Truncate and deallocation: `ocfs2_truncate_log_append()`, `ocfs2_flush_truncate_log()`, `ocfs2_begin_truncate_log_recovery()`, `ocfs2_complete_truncate_log_recovery()`, `ocfs2_cache_cluster_dealloc()`, `ocfs2_cache_block_dealloc()`, `ocfs2_run_deallocs()`, `ocfs2_commit_truncate()`.
- Data-shape transitions and cleanup: `ocfs2_zero_range_for_truncate()`, `ocfs2_dinode_new_extent_list()`, `ocfs2_set_inode_data_inline()`, `ocfs2_convert_inline_data_to_extents()`, `ocfs2_truncate_inline()`, `ocfs2_trim_fs()`.

Integration points:
- File growth and fallocate paths call `ocfs2_add_clusters_in_btree()`, `ocfs2_insert_extent()`, `ocfs2_remove_btree_range()`, `ocfs2_zero_range_for_truncate()`, and inline conversion helpers.
- Writeback paths call `ocfs2_mark_extent_written()` when unwritten extents become initialized and drain deallocation contexts after write-cluster operations.
- Xattr, directory indexing, refcount, reflink, and move-extents code all reuse the same generic extent-tree operations with their own root initializers.
- Mount and unmount paths initialize and shut down the truncate log; ioctl trim calls `ocfs2_trim_fs()`.

Concurrency and lifetime:
- Callers are expected to hold the appropriate inode, allocator, metadata, refcount, and cluster locks before entering exported mutation paths. This file handles journaling and some local inode mutex ordering but not the full high-level lock protocol.
- Buffer-head lifetime is explicit: paths own references until `ocfs2_reinit_path()` or `ocfs2_free_path()`, while metadata allocation helpers pass initialized buffer heads upward for the caller to link and dirty.
- Tree rotations extend journal credits dynamically and then re-journal paths that may have been touched before the extension.
- Dinode cluster counts update both on-disk fields and in-memory `ip_clusters` under `ip_lock`; extent-map updates are rooted in dinode extent-tree callbacks.
- Truncate-log append and flush serialize on `osb_tl_inode`'s inode mutex. Flush locks JBD2 updates and checkpoints the journal before freeing clusters to the global bitmap.
- Refcounted extent removal can acquire the refcount-tree lock unless the caller declares it already held.
- Partial truncate zeroing locks folios while mapping/dirtying and starts writeback before the inode page truncation path later waits.
- Fstrim uses OCFS2 DLM trim lock resources so cluster nodes do not issue duplicate discard for the same requested range.

Important dependencies:
- OCFS2 journaling, metadata-cache, suballocator, local allocator, truncate-log, extent-map, refcount tree, xattr, inode, quota, and sysfile APIs.
- JBD2 transaction credit accounting, journal flush, and commit wait primitives.
- Linux folio/page-buffer APIs, filemap writeback, quota accounting, and block-device discard via `sb_issue_discard()`.
- OCFS2 on-disk validation helpers and tracepoints from `ocfs2_trace.h`.

Risk and edge cases:
- Extent tree invariants are strict: corrupt depth, empty interior nodes, zero child block pointers, invalid extent-block headers, and lost records usually become `ocfs2_error()` or `BUG_ON()`.
- Empty extent records are legal only in tightly controlled leaf positions, normally slot 0; rotation and merge code depend on there being at most one such record.
- Left-contiguous insertion at the first record of a leaf is deliberately downgraded because updating the neighboring left path is more complex.
- Cross-leaf merge and split operations must journal both paths and repair parent edge lengths; stale paths are often reinitialized after tree shape changes.
- `last_eb_blk`, `h_next_leaf_blk`, rightmost parent ranges, and root depth must remain synchronized or later appends and truncates target the wrong edge.
- Truncate-log append and flush are separate transactions, so flush must force a journal checkpoint boundary before replaying log records to prevent double freeing after crash recovery.
- Delayed deallocation reduces lock-ordering risk, but callers must run `ocfs2_run_deallocs()` after sensitive locks and handles are dropped.
- Inline-data conversion has a narrow late-failure window after data is moved into folios and the dinode is converted; the code compensates with quota and cluster rollback where it still can.
- Trim intentionally releases and reacquires the global bitmap lock between groups, so completion is incremental and may return after signal interruption or group-level discard failure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/alloc.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/alloc.h

Purpose: declares the OCFS2 allocation, extent-tree, truncate-log, delayed-deallocation, inline-data conversion, truncation, path traversal, and trim APIs implemented primarily by `alloc.c`.

Read coverage: complete file read, 308 lines.

Key structures and constants:
- `OCFS2_MAX_XATTR_TREE_LEAF_SIZE` caps xattr tree leaf payload size at 64 KiB.
- `struct ocfs2_extent_tree` is the public context for generic extent-tree manipulation. It carries operation callbacks, root buffer, root extent list, caching info, root journal-access function, root object, max leaf cluster limit, and an optional delayed-deallocation context.
- `enum ocfs2_alloc_restarted` reports why `ocfs2_add_clusters_in_btree()` returned `-EAGAIN`: no restart, transaction restart, or metadata reservation restart.
- `struct ocfs2_cached_dealloc_ctxt` stores delayed block-suballocator and global-cluster frees.
- `struct ocfs2_truncate_context` groups delayed deallocation, extent allocator lock state, and a last extent-block buffer used by truncate setup.
- `struct ocfs2_path_item` and `struct ocfs2_path` describe a bounded root-to-leaf b-tree path. `OCFS2_MAX_PATH_DEPTH` is 5.
- Path macros expose root/leaf buffer heads, root/leaf extent lists, root access function, and item count.

Declared behavior:
- Extent-tree initialization functions cover dinodes, xattr trees, xattr values, directory index roots, and refcount trees.
- `ocfs2_read_extent_block()` performs cached reads and implementation-side extent-block validation.
- Extent mutation APIs cover insertion, cluster allocation into a b-tree, splitting, marking unwritten extents written, generic flag changes, single-range removal, and b-tree range removal with optional refcount-tree lock ownership.
- `ocfs2_extend_meta_needed()` returns a conservative maximum metadata-block reservation for tree growth: current root depth plus two.
- Dinode layout helpers initialize a normal extent list, switch an inode to inline data, and convert inline file data to extents.
- Truncate-log APIs initialize/shut down the per-slot log, schedule flush work, append records, flush synchronously, recover another slot's log, and try freeing truncate-log space to satisfy allocation pressure.
- Delayed-deallocation APIs initialize contexts, cache cluster and block frees, test for pending cluster frees, and run cached frees.
- Truncate helpers zero partial ranges, commit extent truncation, and truncate inline data.
- Path helpers allocate/reuse/free paths, find paths or leaves, journal path buffers, find adjacent leaf cpos values, and identify the subtree root for rotations.
- `ocfs2_trim_fs()` is the exported filesystem trim entry point.

Inline helpers:
- `ocfs2_init_dealloc_ctxt()` clears delayed-free list heads.
- `ocfs2_dealloc_has_cluster()` reports whether a delayed context has pending global-cluster frees.
- `ocfs2_rec_clusters()` reads `e_int_clusters` for interior nodes and `e_leaf_clusters` for leaf nodes, reflecting OCFS2's different record layouts.
- `ocfs2_is_empty_extent()` treats a leaf record with zero `e_leaf_clusters` as empty.

Important dependencies:
- Requires OCFS2 on-disk structures including `ocfs2_extent_list`, `ocfs2_extent_rec`, and `ocfs2_dinode`, plus OCFS2 caching and journal-access types.
- Exposes APIs consumed by file growth/truncate paths, address-space/writeback code, xattr code, directory indexing, refcount/reflink code, move-extents code, mount/unmount truncate-log handling, and trim ioctl handling.

Concurrency and lifetime:
- Callers supply journal handles, allocation contexts, buffer heads, and path objects; the header exposes the ownership split but leaves high-level locking to surrounding OCFS2 code.
- Prepared paths own buffer-head references until `ocfs2_reinit_path()` or `ocfs2_free_path()`.
- Delayed-deallocation contexts must be initialized before use and drained after mutating operations complete with no active journal handle and after sensitive locks have been dropped.
- Truncate-log functions rely on implementation-side lock ordering around the truncate-log inode, global bitmap inode, and JBD2 journal flushing.

Risk and edge cases:
- `ocfs2_extend_meta_needed()` intentionally over-reserves for simplicity; callers may reserve more metadata than an operation consumes.
- `ocfs2_rec_clusters()` must be called with the correct node depth or it reads the wrong union field.
- `ocfs2_is_empty_extent()` is meaningful only for leaf records; using it on interior records would be semantically wrong.
- Path depth is fixed at `OCFS2_MAX_PATH_DEPTH`; corrupt on-disk depths beyond that are rejected by implementation checks.
- Mutation APIs require correct metadata reservations, refcount lock ownership, quota handling, and delayed-deallocation draining from callers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/alloc.h -->