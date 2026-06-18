# sources/distributed-fs/ceph-client/fs/btrfs/extent-tree.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/extent-tree.h` is the public interface for Btrfs extent-tree allocation, reference accounting, freeing, pinning, discard/trim, and remapping helpers implemented by `extent-tree.c`. It exposes the allocator control structure used internally by the extent allocator, reference type enums, and the cross-subsystem function prototypes needed by transaction, tree modification, logging, relocation, discard, and cleanup code. The source was read as a complete 169-line file for this report.

## Important APIs, Types, and Functions

`enum btrfs_extent_allocation_policy` selects `BTRFS_EXTENT_ALLOC_CLUSTERED` for normal clustered free-space allocation or `BTRFS_EXTENT_ALLOC_ZONED` for sequential zoned block groups. `struct find_free_extent_ctl` carries allocator inputs (`ram_bytes`, `num_bytes`, `min_alloc_size`, `empty_size`, `flags`, `hint_byte`, `delalloc`, tree-log/data-relocation booleans), block-group search state (`search_start`, RAID `index`, `loop`, caching booleans, retry state, hinted state), clustered allocator state (`empty_cluster`, `last_ptr`, `use_cluster`), result/diagnostic fields (`found_offset`, `max_extent_size`, `total_free_space`), selected policy, and preferred block-group size class. `enum btrfs_inline_ref_type` is used to validate whether an inline backref is block, data, any, or invalid.

Lookup/reference APIs include `btrfs_get_extent_inline_ref_type`, `hash_extent_data_ref`, `btrfs_lookup_data_extent`, `btrfs_lookup_extent_info`, `btrfs_cross_ref_exist`, and `btrfs_get_extent_owner_root`. Delayed-ref and ref mutation APIs include `btrfs_run_delayed_refs`, `btrfs_cleanup_ref_head_accounting`, `btrfs_inc_extent_ref`, `btrfs_inc_ref`, `btrfs_dec_ref`, `btrfs_set_disk_extent_flags`, and `btrfs_free_extent`. Allocation/free APIs include `btrfs_alloc_tree_block`, `btrfs_free_tree_block`, `btrfs_alloc_reserved_file_extent`, `btrfs_alloc_logged_file_extent`, `btrfs_reserve_extent`, `btrfs_free_reserved_extent`, and `btrfs_pin_reserved_extent`. Commit, snapshot, discard, and remap APIs include `btrfs_pin_extent`, `btrfs_pin_extent_for_log_replay`, `btrfs_exclude_logged_extents`, `btrfs_finish_extent_commit`, `btrfs_drop_snapshot`, `btrfs_drop_subtree`, `btrfs_error_unpin_extent_range`, `btrfs_discard_extent`, `btrfs_trim_fs`, `btrfs_handle_fully_remapped_bgs`, and `btrfs_complete_bg_remapping`.

## Control Flow

The header itself has no executable control flow, but it defines the API flow used by the rest of Btrfs. Callers reserve logical space through `btrfs_reserve_extent`, materialize reserved data or metadata through delayed refs and allocation helpers, mutate references with `btrfs_inc_ref`/`btrfs_dec_ref`/`btrfs_free_extent`, flush delayed refs with `btrfs_run_delayed_refs`, and complete commit-time unpin/discard cleanup through `btrfs_finish_extent_commit`. Snapshot and relocation callers enter long-running tree deletion through `btrfs_drop_snapshot` or `btrfs_drop_subtree`. Filesystem trim and explicit discard callers use `btrfs_trim_fs` and `btrfs_discard_extent`.

## State and Persistence Behavior

`struct find_free_extent_ctl` is transient allocator state, not persisted directly. Its fields mirror persistent and transaction state managed elsewhere: block-group profiles, free-space cache status, zoned allocation mode, cluster selection, delayed allocation locking, tree-log/data-relocation block-group selection, and the largest hole found for ENOSPC reporting. The function prototypes govern persistent extent-tree state indirectly: extent items/backrefs are changed inside transactions, delayed refs persist intent until flushed, pinned extents protect old transaction views until commit, and snapshot drop progress/remap completion updates durable root/block-group metadata in the implementation.

## Dependencies and Integration Points

The header includes `<linux/types.h>`, `block-group.h`, and `locking.h`, and forward-declares extent buffers, free clusters, roots, paths, delayed refs, generic refs, disk keys, and inline refs to minimize include coupling. It is included by code that needs extent allocation/reference operations without pulling in the full implementation. Integration points include Btrfs transaction handles, block groups and space-info accounting, free-space clustering, tree locking nests, qgroup/simple quota owner references, tree-log replay, relocation/remap roots, discard/trim, zoned block groups, and device/block-layer discard behavior.

## Risks and Edge Cases

The main header risk is contract drift between declared semantics and the implementation. `find_free_extent_ctl` is broad mutable state shared across many allocator helper phases, so adding fields or changing meanings can break clustered versus zoned allocation behavior. Boolean flags such as `delalloc`, `for_treelog`, `for_data_reloc`, `retry_uncached`, and `hinted` encode lock and search policy; misuse can cause deadlocks, wrong block-group selection, or ENOSPC regressions. The public prototypes expose transaction-sensitive operations where callers must pass valid roots, refs, extent buffers, sizes, and lock nesting. Inline ref type validation is part of on-disk format safety; wrong data-vs-block classification can turn corruption into incorrect accounting.

## Test Signals

Useful validation signals are compile coverage for all Btrfs users of this header, sparse/clang warnings for forward declaration and const mismatches, lockdep coverage for `enum btrfs_lock_nesting` callers, xfstests that allocate/free data and metadata extents, snapshot/drop and relocation tests, qgroup/simple quota tests, log replay tests, zoned allocation tests, ENOSPC/fragmentation tests, and trim/discard tests. ABI-like structure risk for `find_free_extent_ctl` is internal rather than on-disk, so tests should focus on allocator behavior, tracepoint field sanity, and no regressions in largest-hole reporting and fallback loop progression.
