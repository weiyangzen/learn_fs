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
