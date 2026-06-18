# Group Research: group_247_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_extent_tree_c_sour_83128535894c

Scope verified against `Docs/research_subset_a.md`: both files are under included source tree `sources/local-fs/btrfs-linux`. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent-tree.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/extent-tree.c

Purpose:
This file implements Btrfs extent-tree management: physical extent allocation, extent/backreference item insertion and deletion, delayed reference execution, pin/unpin and commit-time free-space return, tree block allocation/freeing, snapshot/subtree dropping, discard/TRIM, and related block-group accounting. It is one of the central transaction-time metadata engines for Btrfs.

Major responsibilities:
- Maintains extent items and metadata items in the extent tree.
- Encodes, searches, inserts, updates, and removes inline and keyed backreferences for data and tree extents.
- Runs delayed refs, including add/drop delayed data refs, tree refs, delayed extent ops, and reserved extent insertion.
- Allocates free extents from block groups using clustered allocation on normal filesystems and sequential allocation on zoned filesystems.
- Converts reserved extents into committed extent-tree records for file data and metadata tree blocks.
- Frees extents when their last reference is dropped, including checksum deletion, RAID extent deletion, free-space-tree update, remap-tree handling, quota/simple-quota accounting, and block-group accounting.
- Pins freed/reserved ranges until transaction commit, then unpins them and returns free space or schedules discard.
- Allocates and initializes new tree blocks.
- Drops snapshots and relocation subtrees by walking btree blocks, converting backrefs when needed, and freeing private subtrees.
- Implements synchronous discard and filesystem-wide fstrim over block groups and unallocated device ranges.

Key include dependencies:
- Core Btrfs tree/data structures: `ctree.h`, `fs.h`, `accessors.h`, `root-tree.h`, `file-item.h`.
- Transaction and delayed ref machinery: `transaction.h`, `delayed-inode.h`.
- Extent/block-group allocation: `extent-tree.h`, `block-group.h`, `space-info.h`, `block-rsv.h`, `free-space-cache.h`, `free-space-tree.h`.
- Device/chunk/RAID/zoned support: `volumes.h`, `raid56.h`, `raid-stripe-tree.h`, `zoned.h`, `dev-replace.h`.
- Integrity/accounting helpers: `qgroup.h`, `ref-verify.h`, `tree-checker.h`, `discard.h`, `orphan.h`, `relocation.h`.
- Linux kernel facilities: scheduling, writeback, block device discard, sorting, RCU, kthreads, slab allocation, ratelimits, percpu counters, lockdep, and CRC32C.

Backreference model:
- The file contains a long in-source design comment explaining implicit versus full backrefs.
- Data extents may be referenced by multiple snapshots/subvolumes, multiple files, or multiple offsets in one file.
- Tree blocks may have implicit refs keyed by owner root or full/shared refs keyed by parent block address.
- Data implicit refs use `(root_objectid, inode/objectid, file offset)` plus a count; the key offset is a CRC-derived hash from these fields.
- Shared data refs and shared block refs are used when a parent block address identifies the owner.
- Inline backrefs live inside the extent item when there is room; keyed backref items are used when inline storage is insufficient.
- `BTRFS_EXTENT_OWNER_REF_KEY` is supported for simple quota owner tracking and is skipped or read as needed by inline-ref scans.

Important helper logic:
- `block_group_bits()` checks whether a block group satisfies required allocation flags.
- `btrfs_lookup_data_extent()` searches for an existing data extent item at a logical bytenr/length.
- `btrfs_lookup_extent_info()` returns current ref count, extent flags, and owner root by combining committed extent-tree state with pending delayed refs.
- `btrfs_get_extent_inline_ref_type()` validates inline backref type against expected data/tree context and catches malformed refs.
- `hash_extent_data_ref()` and related helpers compute and compare hashed data ref keys.
- `find_next_key()` locates the next btree key in a path and is reused by inline ref insertion and snapshot drop progress.

Backref search/update paths:
- `lookup_inline_extent_backref()` searches inline refs in an extent item, validates item sizes, handles skinny metadata fallback to old-style extent items, and identifies insertion positions.
- `setup_inline_extent_backref()` extends an extent item and inserts a new inline backref in sorted order while updating total refs and delayed extent ops.
- `update_inline_extent_backref()` adjusts extent and inline-ref counts, removes inline ref records when their count reaches zero, and detects invalid drops.
- `lookup_extent_backref()` first searches inline refs, then falls back to keyed tree/data backref items.
- `insert_inline_extent_backref()` inserts or increments inline refs, returning `-EAGAIN` when a keyed backref is needed.
- `insert_extent_data_ref()`, `remove_extent_data_ref()`, `lookup_extent_data_ref()`, `insert_tree_block_ref()`, and `lookup_tree_block_ref()` handle keyed backref items.

Delayed refs:
- Public `btrfs_inc_extent_ref()` queues delayed tree or data ref additions and records ref-verify state.
- `run_delayed_data_ref()` handles data ref add/drop. For newly reserved extents it creates the extent item via `alloc_reserved_file_extent()`; otherwise it increments or frees existing refs.
- `run_delayed_tree_ref()` mirrors that for metadata/tree refs and handles remap-tree drops specially.
- `run_one_delayed_ref()` dispatches by delayed ref node type and pins reserved extents if an insert path fails or the transaction is aborted.
- `btrfs_run_delayed_refs_for_head()` selects refs under one delayed ref head, merges refs, runs them, releases delayed-ref reservation accounting, and recalculates bytes processed.
- `cleanup_ref_head()` removes completed heads, frees checksum reservation accounting, pins uninserted reserved extents, deletes checksums for abandoned data extents, and releases delayed ref head locks/references.
- `__btrfs_run_delayed_refs()` and `btrfs_run_delayed_refs()` drive delayed ref processing by bytes or by all ready heads; `U64_MAX` means also handle newly created refs until no heads remain.
- `btrfs_cleanup_ref_head_accounting()` releases delayed checksum reservation accounting and simple quota reservations when heads are discarded.

Delayed extent ops:
- `btrfs_set_disk_extent_flags()` creates a delayed extent op to set extent flags later.
- `__run_delayed_extent_op()` applies delayed flag updates and tree block key updates to an extent item.
- `run_delayed_extent_op()` finds the appropriate extent/metadata item, including skinny metadata fallback, and applies the operation.
- `cleanup_extent_op()` discards redundant ops for reserved extents that will be inserted with final flags/key data.

Cross-reference detection:
- `btrfs_cross_ref_exist()` checks whether a data extent has refs other than a given inode/offset.
- `check_committed_ref()` performs a fast committed extent-tree check designed to avoid false negatives, though it may return false positives.
- `check_delayed_ref()` checks currently running delayed refs while coordinating with delayed ref head locks to avoid racing with delayed ref execution.
- This path is intended for write paths such as delalloc flushing and direct I/O, so it deliberately favors quick conservative answers.

Reference propagation through tree blocks:
- `__btrfs_mod_ref()` walks items in a tree block and queues add/drop refs for all child tree blocks or referenced data extents.
- `btrfs_inc_ref()` and `btrfs_dec_ref()` wrap that helper.
- It skips inline file extents, holes, test mode, and non-shareable leaf cases.
- Full backrefs use the parent block address; implicit refs use root ownership.

Pinning and commit cleanup:
- `pin_down_extent()` moves a range from reserved to pinned accounting and marks it dirty in the transaction pinned extent tree.
- `btrfs_pin_extent()` pins a reserved range by block group.
- `btrfs_pin_extent_for_log_replay()` caches the block group, pins a log replay tree block, and removes it from free-space cache so replay does not reuse it.
- `btrfs_exclude_logged_extents()` removes logged data extents from free-space cache for mixed block group replay.
- `unpin_extent_range()` returns pinned ranges to block-group/free-space accounting at commit, with special handling for read-only block groups and zoned unusable bytes.
- `btrfs_finish_extent_commit()` optionally performs sync discard, unpins all transaction-pinned ranges, schedules async discard, and processes deleted block groups.

Freeing extents:
- `__btrfs_free_extent()` is the core drop path. It locates the matching backref, removes or decrements it, updates extent refs, deletes the extent item when the last ref is gone, and then calls `do_free_extent_accounting()`.
- It supports inline backrefs, keyed shared refs, skinny metadata, owner refs for simple quotas, and corruption checks for impossible ref counts or inconsistent item layout.
- `do_free_extent_accounting()` removes ranges from the remap tree if needed, deletes checksums and RAID extent records for data, records simple quota deltas, adds the range to the free-space tree unless already handled by remap removal, and updates block-group usage.
- `check_ref_cleanup()` opportunistically removes an empty delayed ref head when freeing a tree block and returns whether a reserved extent still needs special handling.
- `btrfs_free_tree_block()` queues metadata ref drops, then either pins recently written or unsafe-to-reuse blocks, or immediately returns an unneeded new tree block to free space.
- `btrfs_free_extent()` is the public data/metadata free entry point; tree-log blocks are not inserted into the extent tree and are just pinned.

Allocation policy:
- `find_free_extent()` is the allocator core. It chooses `BTRFS_EXTENT_ALLOC_CLUSTERED` normally and `BTRFS_EXTENT_ALLOC_ZONED` for zoned filesystems.
- It prepares allocation hints, selects the correct `space_info`, honors dedicated zoned subgroups for tree-log and data relocation allocations, iterates block groups by RAID index, handles caching states, respects size classes, retries uncached block groups when useful, can allocate new chunks, and reports largest available holes on `-ENOSPC`.
- Allocation search phases are represented by `enum btrfs_loop_type`: cache nowait, wait for caching, allow unset size class, allocate chunk, ignore wrong size class, and retry without `empty_size`.
- `find_free_extent_check_size_class()` prefers block groups matching the request's size class until later fallback loops.
- `prepare_allocation_clustered()` uses remembered cluster windows and fragmentation/max-extent hints.
- `find_free_extent_clustered()` uses `btrfs_free_cluster` state to allocate from/refill clusters, then falls back to unclustered allocation.
- `find_free_extent_unclustered()` searches the free-space cache directly and marks clusters fragmented when appropriate.
- `do_allocation_zoned()` allocates sequentially from `alloc_offset`, enforces tree-log/data-relocation dedicated block groups, respects active zone constraints, updates free-space counters, and uses zone capacity rather than arbitrary free-space holes.
- `can_allocate_chunk_zoned()` handles active-zone limits and may finish a zone, return `-EAGAIN`, or suppress chunk allocation when existing active space should be used first.
- `btrfs_reserve_extent()` is the public allocator entry point. It determines the allocation profile from the root and data/metadata type, calls `find_free_extent()`, and on fragmentation retries progressively smaller extents down to `min_alloc_size`.

Reserved extent conversion:
- `btrfs_free_reserved_extent()` returns an allocated-but-unused reserved range to free space and block-group accounting.
- `btrfs_pin_reserved_extent()` pins a reserved tree block range.
- `alloc_reserved_extent()` removes the range from the free-space tree and increments block-group usage.
- `alloc_reserved_file_extent()` inserts a new data extent item with initial inline backref, optional simple quota owner ref, generation, flags, and ref count, then finalizes reserved extent accounting.
- `alloc_reserved_tree_block()` inserts a new metadata/tree extent item or skinny metadata item with tree-block backref and optional full-backref flags/key data, then finalizes reserved extent accounting.
- `btrfs_alloc_reserved_file_extent()` queues delayed data ref insertion for a reserved file extent, adjusting owning root for data relocation.
- `btrfs_alloc_logged_file_extent()` is used by tree-log recovery: it excludes the range from free space, reserves block-group bytes, inserts the file extent item immediately, records simple quota delta, and pins on failure.

Tree block allocation:
- `btrfs_init_new_buffer()` finds/creates an extent buffer, validates debug lock ownership, assigns lockdep class, locks it, clears stale/zeroout state, zeros the header, initializes Btrfs header fields, and marks it dirty in either transaction dirty pages or log dirty pages.
- `btrfs_alloc_tree_block()` consumes a block reservation, reserves an extent, initializes the new buffer, creates the appropriate delayed tree ref and delayed extent op, handles relocation roots/full backrefs, and rolls back buffer/reserved extent/block reservation state on failure.

Snapshot and subtree deletion:
- `struct walk_control` stores per-level refs/flags, progress keys, stage, current level, shared level, readahead state, and restart flags for snapshot deletion.
- Deletion has two stages:
  - `DROP_REFERENCE`: drop references to private blocks and free them.
  - `UPDATE_BACKREF`: convert children under shared blocks to full backrefs where required before dropping the snapshot's reference.
- `visit_node_for_delete()` decides whether a child must be visited based on ref count, full-backref state, generation relative to root origin generation, and update progress.
- `reada_walk_down()` dynamically readaheads child nodes likely to be visited.
- `walk_down_proc()` processes the current node, looks up extent info when needed, and performs full-backref conversion by adding shared refs, dropping implicit refs, and setting disk extent flags.
- `do_walk_down()` locks/reads child blocks, looks up their ref info and owner root, transitions to `UPDATE_BACKREF` for shared private descendants, or drops skippable refs.
- `maybe_drop_reference()` queues the child ref drop and traces shared subtrees for qgroup accounting.
- `walk_up_proc()` frees blocks when all children are handled, decrements data refs from leaves, handles qgroup leaf tracing, validates owners, and calls `btrfs_free_tree_block()`.
- `walk_down_tree()` and `walk_up_tree()` implement iterative btree traversal without recursion.
- `btrfs_drop_snapshot()` coordinates transaction lifecycle, delayed item flushing, root deletion state, restart from `drop_progress`, periodic progress persistence, throttled transaction restarts, root item deletion, orphan cleanup, qgroup cleanup, and dead-root requeue on incomplete drops.
- `btrfs_drop_subtree()` reuses the walk machinery for relocation subtrees and keeps parent/node locking semantics required by relocation.

Block-group remap handling:
- `btrfs_complete_bg_remapping()` completes a remapped block group by removing chunk stripes/device extents and marking the group unused when no extents remain.
- `btrfs_handle_fully_remapped_bgs()` discards fully remapped block groups and completes their remapping from the queued list.
- `drop_remap_tree_ref()` returns remapped extents to the free-space tree and updates block-group accounting.
- `do_free_extent_accounting()` avoids double free-space-tree updates when remap-tree removal already handled the free-space change.

Discard and TRIM:
- `btrfs_issue_discard()` aligns discard ranges to sectors, skips Btrfs superblock mirror ranges, chunks large discards, and treats `-EOPNOTSUPP` as non-fatal in appropriate callers.
- `do_discard_extent()` maps logical discard stripes to devices, uses zone reset on zoned filesystems when possible, and mirrors reset/discard to device replace targets when required.
- `btrfs_discard_extent()` maps logical ranges into discard stripes under a blocked bio counter to avoid device replace races, skips missing/non-writable devices, and returns actual discarded bytes.
- `btrfs_error_unpin_extent_range()` unpins in error contexts without returning free space and ignores errors.
- `btrfs_trim_fs()` trims free ranges inside each block group, then trims unallocated ranges on devices.
- `btrfs_trim_free_extents_throttle()` trims unallocated device ranges in bounded chunks under `chunk_mutex`, marks device allocation-state ranges as trimmed, and returns `-EAGAIN` to continue later.
- `btrfs_trim_free_extents()` iterates devices in UUID order, tolerates per-device failures, handles throttling/interruption, and reports first error.

Concurrency and locking:
- Extent tree btree operations use `btrfs_path` locking rules and sometimes keep locks while checking delayed ref heads to avoid races.
- Delayed refs use delayed ref root spinlocks, per-head spinlocks, per-head mutexes, refcounts, and selected/unselected head states.
- Block group allocation paths use `space_info->groups_sem`, block group refs, `block_group->lock`, `space_info->lock`, free-space control locks, cluster refill locks, and optional `data_rwsem` for delalloc allocations.
- Zoned allocator uses `treelog_bg_lock`, `relocation_bg_lock`, `zone_active_bgs_lock`, and block group locks to coordinate dedicated block-group selection.
- Commit unpin and deleted block-group processing uses `unused_bg_unpin_mutex` and `unused_bgs_lock`.
- Device trim uses `device_list_mutex` and `chunk_mutex` to avoid races with chunk/device changes.

Error handling and integrity checks:
- The code returns standard negative errno values and aborts transactions on metadata corruption or unrecoverable update failures.
- Many paths explicitly check for missing extent roots, missing checksum roots, invalid extent item sizes, impossible ref drops, zero ref counts, unexpected delayed ref types, owner mismatches, and malformed inline refs.
- `abort_and_dump()` aborts the transaction and prints the leaf for severe extent-tree inconsistencies.
- Several paths use `WARN_ON`, `ASSERT`, and debug-only lock-owner checks to catch logic errors and corruption early.
- ENOSPC handling reports largest found contiguous free space via `ins->offset`, with optional `ENOSPC_DEBUG` dumps.

External behavioral surface:
- Exports functions declared in `extent-tree.h`, including extent reservation/freeing, tree block allocation/freeing, delayed ref running, extent info lookup, cross-ref detection, snapshot/subtree dropping, commit unpin completion, discard, trim, and remap completion.
- The file is deeply coupled to transaction commit, COW tree updates, qgroup/simple quota accounting, relocation, zoned mode, and free-space-tree correctness.

Implementation notes:
- Skinny metadata support causes many lookup paths to first search `BTRFS_METADATA_ITEM_KEY` and fall back to legacy `BTRFS_EXTENT_ITEM_KEY`.
- Simple quota mode stores an owner ref as the first inline ref and must be skipped when scanning normal data/tree refs.
- Tree-log blocks are treated specially because they do not enter the normal extent allocation tree.
- The allocator records `max_extent_size` to avoid repeated expensive searches when fragmentation prevents the requested size.
- Snapshot deletion is intentionally iterative and restartable, persisting `drop_progress` so long drops can resume after transaction boundaries or interruption.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent-tree.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/extent-tree.h

Purpose:
This header declares the Btrfs extent-tree API implemented by `extent-tree.c` and exposes the allocator control structure and inline-ref type enum needed by related Btrfs subsystems.

Key includes and forward declarations:
- Includes Linux integer types plus Btrfs `block-group.h` and `locking.h`.
- Forward declares core Btrfs structures used by the API: extent buffers, free clusters, filesystem info, roots, paths, refs, disk keys, delayed ref heads/roots, and inline refs.
- Uses additional types by declaration context, including `btrfs_trans_handle`, `btrfs_inode`, `btrfs_key`, `fstrim_range`, and lock nesting enum from included Btrfs headers.

Key data structures:
- `enum btrfs_extent_allocation_policy`
  - `BTRFS_EXTENT_ALLOC_CLUSTERED`: normal free-space-cache/cluster allocator.
  - `BTRFS_EXTENT_ALLOC_ZONED`: sequential allocator for zoned filesystems.
- `struct find_free_extent_ctl`
  - Central per-allocation state passed through `find_free_extent()` and helpers.
  - Stores basic request fields: `ram_bytes`, `num_bytes`, `min_alloc_size`, `empty_size`, and allocation `flags`.
  - Stores search state: `search_start`, `hint_byte`, `found_offset`, RAID `index`, loop phase, caching status, and whether the search follows a hint.
  - Stores clustered allocation state: `empty_cluster`, `last_ptr`, `use_cluster`.
  - Stores context flags: `delalloc`, `for_treelog`, `for_data_reloc`, retry/caching booleans.
  - Stores fragmentation/availability feedback: `max_extent_size` and `total_free_space`.
  - Stores selected policy and preferred block-group size class.
- `enum btrfs_inline_ref_type`
  - Classifies inline refs as invalid, block, data, or any, for validation by inline-ref parsing.

Declared API groups:
- Inline/data ref helpers:
  - `btrfs_get_extent_inline_ref_type()` validates inline backref type in an extent buffer.
  - `hash_extent_data_ref()` computes the key hash for implicit data extent refs.
- Delayed refs and accounting:
  - `btrfs_run_delayed_refs()` processes queued delayed reference updates.
  - `btrfs_cleanup_ref_head_accounting()` releases delayed ref head reservation/accounting state.
- Lookup helpers:
  - `btrfs_lookup_data_extent()` searches for a data extent item.
  - `btrfs_lookup_extent_info()` returns ref count, flags, and owner root while considering delayed refs.
  - `btrfs_cross_ref_exist()` checks whether a data extent is cross-referenced by another owner.
  - `btrfs_get_extent_owner_root()` extracts simple-quota owner root from an extent item.
- Pinning and log replay:
  - `btrfs_pin_extent()` pins a reserved/freed range in the current transaction.
  - `btrfs_pin_extent_for_log_replay()` pins a log replay tree block and removes it from free-space cache.
  - `btrfs_exclude_logged_extents()` excludes logged extents from mixed block group free-space reuse.
  - `btrfs_error_unpin_extent_range()` unpins in error handling without restoring free space.
- Allocation/freeing:
  - `btrfs_reserve_extent()` reserves a physical extent and returns its key.
  - `btrfs_free_reserved_extent()` returns an unused reserved extent.
  - `btrfs_pin_reserved_extent()` pins a reserved tree block extent.
  - `btrfs_alloc_tree_block()` allocates and initializes a new tree block.
  - `btrfs_free_tree_block()` queues/free-handles tree block release.
  - `btrfs_alloc_reserved_file_extent()` queues insertion of a newly reserved file extent.
  - `btrfs_alloc_logged_file_extent()` records a file extent recovered from tree-log replay.
  - `btrfs_free_extent()` queues a delayed data/tree extent drop.
  - `btrfs_inc_extent_ref()` queues a delayed extent ref increment.
  - `btrfs_inc_ref()` and `btrfs_dec_ref()` update references for children of a tree block.
  - `btrfs_set_disk_extent_flags()` queues a delayed extent flag update.
- Transaction commit and cleanup:
  - `btrfs_finish_extent_commit()` unpins transaction-pinned extents and handles discard/deleted block groups.
- Snapshot/relocation:
  - `btrfs_drop_snapshot()` drops a subvolume/snapshot root.
  - `btrfs_drop_subtree()` drops a relocation subtree.
- Discard/TRIM/remap:
  - `btrfs_discard_extent()` issues discard or zone reset for a logical range.
  - `btrfs_trim_fs()` implements filesystem-wide fstrim.
  - `btrfs_handle_fully_remapped_bgs()` processes fully remapped block groups.
  - `btrfs_complete_bg_remapping()` finalizes a remapped block group.

Relationship to `extent-tree.c`:
- The header exposes only the functions and state needed by other Btrfs modules; most implementation details in `extent-tree.c` remain private static helpers.
- `find_free_extent_ctl` mirrors the internal allocator phases and is defined here because allocation tracing or nearby helpers need structured access to allocator state.
- The API forms the boundary between high-level Btrfs operations such as COW, relocation, log replay, snapshot deletion, and low-level extent-tree/block-group accounting.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent-tree.h -->