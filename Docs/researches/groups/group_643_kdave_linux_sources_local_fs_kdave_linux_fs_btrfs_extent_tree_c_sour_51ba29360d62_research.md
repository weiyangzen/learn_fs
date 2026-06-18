# Group Research: kdave-linux Btrfs Extent Tree

Scope: `Docs/research_subset_a.md`

Files researched:
- `sources/local-fs/kdave-linux/fs/btrfs/extent-tree.c`
- `sources/local-fs/kdave-linux/fs/btrfs/extent-tree.h`

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent-tree.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/extent-tree.c

This file is the core Btrfs extent-tree implementation. It owns on-disk extent reference item manipulation, delayed-reference execution, logical extent allocation, reserved extent insertion, extent freeing, pinned extent commit cleanup, tree block allocation/freeing, snapshot/subtree deletion walks, discard/trim dispatch, and remapped block group completion.

Major responsibilities:
- Looks up extent items and computes committed plus pending reference state through `btrfs_lookup_data_extent()` and `btrfs_lookup_extent_info()`.
- Parses, validates, inserts, updates, and removes inline and keyed backreferences for data and metadata extents.
- Queues and runs delayed refs for data extents, tree blocks, extent operations, simple quota accounting, and remap-tree drops.
- Implements physical/logical extent allocation through `find_free_extent()`, with clustered allocation for normal filesystems and sequential allocation for zoned filesystems.
- Converts reserved bytes into extent-tree records with `alloc_reserved_file_extent()`, `alloc_reserved_tree_block()`, `btrfs_alloc_reserved_file_extent()`, and `btrfs_alloc_logged_file_extent()`.
- Frees data and metadata extents, removes checksums and RAID stripe-tree records, updates free-space tree state, and moves block group counters between reserved, used, pinned, free, readonly, and zone-unusable accounting.
- Allocates initialized tree blocks with correct owner, generation, lockdep class, log dirty tracking, delayed tree refs, and block reserve rollback on failure.
- Drops snapshots and relocation subtrees by walking btree nodes, detecting shared references, converting to full backrefs when needed, and persisting `drop_progress`.
- Issues discard/reset operations for logical extents, block groups, and unallocated device space while avoiding superblock ranges and handling device replace/zoned behavior.

Backreference model:
- The long in-file comment documents Btrfs backref rules: implicit refs encode owner tree or file owner information, while full/shared refs encode the parent block location.
- Data extents use `BTRFS_EXTENT_DATA_REF_KEY` or `BTRFS_SHARED_DATA_REF_KEY`; metadata extents use `BTRFS_TREE_BLOCK_REF_KEY` or `BTRFS_SHARED_BLOCK_REF_KEY`.
- `hash_extent_data_ref()` hashes `(root_objectid, owner, offset)` for implicit data-ref keys, and collision handling is done by comparing full ref payloads and incrementing key offsets on insert.
- Inline backrefs live inside `BTRFS_EXTENT_ITEM_KEY` or `BTRFS_METADATA_ITEM_KEY` items until they no longer fit or a neighboring backref item prevents safe extension.
- `btrfs_get_extent_inline_ref_type()` validates inline ref types against expected data/block context and rejects malformed shared refs whose parent offsets are not sector aligned.
- Simple quota mode may add a leading `BTRFS_EXTENT_OWNER_REF_KEY`; `btrfs_get_extent_owner_root()` reads this owner ref for later free accounting.

Delayed-reference execution:
- Public callers queue work through `btrfs_inc_extent_ref()`, `btrfs_free_extent()`, `btrfs_inc_ref()`, `btrfs_dec_ref()`, `btrfs_alloc_reserved_file_extent()`, and `btrfs_alloc_tree_block()`.
- `btrfs_run_delayed_refs()` skips aborted transactions and free-space-tree creation, then drains selected delayed-ref heads through `__btrfs_run_delayed_refs()`.
- `btrfs_run_delayed_refs_for_head()` selects individual refs, handles sequence deferral with `-EAGAIN`, adjusts head `ref_mod`, transfers `must_insert_reserved` ownership, runs the ref, releases delayed-ref reservations, and merges newly mergeable refs after each step.
- `run_one_delayed_ref()` dispatches to `run_delayed_tree_ref()` or `run_delayed_data_ref()` and pins reserved extents on error when a reserved extent insertion was expected.
- `run_delayed_extent_op()` and `__run_delayed_extent_op()` update extent item flags and, for fat metadata items, tree block keys.
- `cleanup_ref_head()` removes fully processed heads, handles reserved extent fallback, deletes pending csums for data reservations, and releases simple quota reservations.

Extent insertion and removal:
- `__btrfs_inc_extent_ref()` first tries to add/update an inline backref. On `-EAGAIN`, it increments the main extent item refcount and inserts a keyed data or tree backref item.
- `__btrfs_free_extent()` is the symmetric removal path. It finds the matching inline or keyed backref, locates the owning extent item, validates sizes/refcounts, updates or removes backrefs, deletes the extent item when the last ref is gone, and calls `do_free_extent_accounting()`.
- `do_free_extent_accounting()` removes remap-tree state, deletes csums and RAID stripe extents for data, records simple quota deltas, adds the range to the free-space tree unless remapped handling already did so, and updates block group usage.
- Metadata frees require `refs_to_drop == 1`; tree log extents bypass extent-tree delayed refs and are pinned directly.
- Corruption paths use `-EUCLEAN`, transaction aborts, leaf dumps, and strict extent item size/reference checks.

Allocation path:
- `btrfs_reserve_extent()` chooses an allocation profile from root/data type, fills `struct find_free_extent_ctl`, calls `find_free_extent()`, and retries smaller allocations down to `min_alloc_size` on `-ENOSPC`.
- `find_free_extent()` searches block groups by RAID index and retry loop phase. Phases cover nonblocking cache startup, waiting for caching progress, accepting unset size classes, chunk allocation, wrong size class fallback, and dropping `empty_size`/cluster requirements.
- Clustered allocation uses per-space-info free clusters (`meta_alloc_cluster`, `data_alloc_cluster`), `btrfs_find_space_cluster()`, and `btrfs_alloc_from_cluster()`, falling back to unclustered free-space-cache searches when clusters are fragmented or unavailable.
- Zoned allocation (`do_allocation_zoned()`) is sequential. It respects dedicated tree-log/data-relocation block groups, active-zone limits, zone capacity, `alloc_offset`, and special data-relocation runtime flags.
- Successful allocation reserves bytes in the selected block group with `btrfs_add_reserved_bytes()`, increments block group reservations, and returns `ins->objectid`/`ins->offset`.
- `space_info->max_extent_size` is updated on failure to guide later allocation attempts and report the largest found contiguous/free fallback.

Reserved extent materialization:
- `alloc_reserved_extent()` removes the range from the free-space tree and updates block group used accounting.
- `alloc_reserved_file_extent()` creates the extent item, optional simple quota owner ref, and inline data/shared-data backref, then materializes the reservation.
- `alloc_reserved_tree_block()` creates skinny metadata items when supported, otherwise fat extent items with `btrfs_tree_block_info`, then writes the inline tree/shared-block backref.
- `btrfs_alloc_logged_file_extent()` is log replay specific: it excludes logged ranges from free space, manually accounts reserved bytes, inserts the file extent item, records simple quota delta, and pins the extent on insertion failure.

Tree block lifetime:
- `btrfs_alloc_tree_block()` consumes a block reserve, reserves a metadata extent, initializes an `extent_buffer` via `btrfs_init_new_buffer()`, and queues a delayed tree extent unless allocating for the tree log.
- Relocation tree allocations force full backrefs and use `reloc_src_root` as the owning root for accounting.
- `btrfs_init_new_buffer()` sets generation, level, bytenr, owner, fsid/chunk UUIDs, lockdep class, dirty-log or transaction-dirty tracking, and clears stale/zoned-zeroout state.
- `btrfs_free_tree_block()` queues the tree ref drop, then either pins the block, returns it immediately to free space, or leaves it for delayed cleanup depending on last-ref, generation, tree mod log users, zoned mode, and whether the buffer was written.

Snapshot and subtree deletion:
- `struct walk_control` carries per-level refs, flags, traversal progress, stage, shared level, restart state, and readahead state.
- Deletion alternates between `DROP_REFERENCE` and `UPDATE_BACKREF` stages. Shared young blocks may require converting children to full backrefs before dropping the root's reference.
- `visit_node_for_delete()` decides whether a child must be visited based on reference count, full-backref state, generation relative to snapshot origin generation, update-ref mode, and stored progress.
- `walk_down_tree()` and `walk_up_tree()` implement the traversal. They look up extent refs, read/relock children when stale, queue subtree qgroup tracing, drop references, clear dirty buffers, and free tree blocks.
- `btrfs_drop_snapshot()` persists `drop_progress` and `drop_level`, restarts transactions as needed, handles cleaner throttling with `-EAGAIN`, deletes the root item/orphan item, frees qgroup pertrans metadata reserves, adds dropped/dead roots, and wakes unfinished-drop waiters.
- `btrfs_drop_subtree()` reuses the same walker for relocation-only subtree cleanup under a locked parent/node.

Pinned, remapped, discard, and trim handling:
- `btrfs_pin_extent()` and `pin_down_extent()` move reserved bytes to pinned state and mark the transaction pinned extent range dirty.
- `btrfs_finish_extent_commit()` unpins all transaction pinned ranges, optionally issues synchronous discard, returns space to free-space/block-group accounting, schedules async discard, and discards/deletes removed block groups.
- `btrfs_complete_bg_remapping()` finalizes a remapped block group by removing chunk stripe/device extent state and marking it unused if no extents remain.
- `btrfs_handle_fully_remapped_bgs()` discards fully remapped block groups and completes their remapping.
- `btrfs_discard_extent()` maps logical ranges to discard stripes, blocks device replacement races with the bio counter, handles missing/non-writable devices, resets zones when possible, and sends discard to replace targets when needed.
- `btrfs_issue_discard()` sector-aligns ranges, avoids superblock mirrors, chunks requests, and treats unsupported discard as nonfatal.
- `btrfs_trim_fs()` trims free ranges inside block groups first, then unallocated device regions via `btrfs_trim_free_extents()`, continuing across failures while reporting the first block-group or device error.

Cross-reference checks:
- `btrfs_cross_ref_exist()` combines committed extent-tree inspection with delayed-ref inspection to determine whether a data extent is shared by anything other than a given inode/offset.
- The committed check is intentionally conservative and can return false positives to avoid expensive full non-inline backref searches in write paths.
- Lock ordering is important: the extent-tree leaf remains locked while the delayed-ref head is checked to avoid missing refs racing with delayed-ref flushing.

Concurrency and locking:
- Delayed refs use `delayed_refs->lock`, per-head `head->lock`, and per-head `head->mutex`; contended heads are refcounted and retried after waiting.
- Block group allocator iteration uses `space_info->groups_sem`, block group refs, optional `data_rwsem` for delalloc, free cluster locks, and per-space/block-group counter locks.
- Zoned tree-log and data-relocation dedicated block groups are protected by `fs_info->treelog_bg_lock` and `fs_info->relocation_bg_lock`.
- Pinned extent commit cleanup serializes with `unused_bg_unpin_mutex`.
- Discard protects device mappings from replacement/removal with `btrfs_bio_counter_inc_blocked()` and device list iteration with `device_list_mutex`.

Important invariants:
- Extent item sizes must be large enough for `struct btrfs_extent_item` and, for fat metadata, `struct btrfs_tree_block_info`.
- Metadata/tree refs are single-count drops/adds; data refs can carry ref counts.
- A zero extent refcount is corruption.
- Inline refs are ordered compatibly with keyed backref ordering and must not overrun the item.
- Extents must be accounted through free-space tree and block group counters exactly once, with remap-tree paths avoiding double free-space insertion.
- Reserved extent insertion must either create the extent item and update block group accounting or pin/free the reservation on failure.
- Zoned allocation must remain sequential and must not mix normal data writes with dedicated relocation writes in the same zone.

Key local dependencies:
- `block-group.c/.h` for block group lookup, reservation, free-space accounting, cache state, and allocation profiles.
- `delayed-ref.c/.h` for delayed ref heads/nodes, merging, selection, and queueing.
- `free-space-cache.c/.h` and `free-space-tree.c/.h` for allocator search and persistent free-space updates.
- `qgroup.c/.h` for simple quota owner refs, deltas, and subtree tracing.
- `raid-stripe-tree.c/.h` for data extent RAID stripe record deletion.
- `zoned.c/.h` for zone activation, reset, finish, and sequential allocation constraints.
- `relocation.c/.h`, `root-tree.c`, `tree-log.c`, and `extent_io.c` for snapshot/drop, root persistence, log replay, and extent buffer IO/locking interactions.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent-tree.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/extent-tree.h

This header publishes the Btrfs extent-tree interface used by allocation, delayed refs, backref validation, tree-block lifetime, snapshot deletion, discard/trim, remapping, and reserved extent handling.

Major declarations:
- Forward declares Btrfs core structures used by extent-tree APIs without forcing broad include dependencies.
- Includes `block-group.h` and `locking.h` because exported allocation control and tree block allocation interfaces depend on block group size class and lock nesting types.
- Defines the allocation policy enum used by the allocator implementation.
- Defines `struct find_free_extent_ctl`, the large per-allocation control block consumed by `find_free_extent()` and helpers.
- Defines inline-ref validation categories with `enum btrfs_inline_ref_type`.
- Declares public extent-tree functions implemented in `extent-tree.c`.

Allocation data model:
- `enum btrfs_extent_allocation_policy` distinguishes normal clustered allocation from zoned sequential allocation.
- `struct find_free_extent_ctl` carries requested sizes (`ram_bytes`, `num_bytes`, `min_alloc_size`, `empty_size`), block group profile flags, and the current search position.
- Clustered allocation fields include `empty_cluster`, `last_ptr`, and `use_cluster`.
- Retry/search state fields include `have_caching_bg`, `orig_have_caching_bg`, `retry_uncached`, `hinted`, RAID `index`, `loop`, cache state, `max_extent_size`, and `total_free_space`.
- Special allocation context fields include `delalloc`, `for_treelog`, and `for_data_reloc`.
- Result and preference fields include `found_offset`, `hint_byte`, selected `policy`, and desired block group `size_class`.

Backref and extent metadata APIs:
- `btrfs_get_extent_inline_ref_type()` validates and classifies an inline ref in a specific data/block/any context.
- `hash_extent_data_ref()` exposes the hash used for implicit data backref keys.
- `btrfs_lookup_data_extent()` searches for an extent item at a logical address and length.
- `btrfs_lookup_extent_info()` returns delayed-ref-aware refs, flags, and owner root for an extent.
- `btrfs_get_extent_owner_root()` extracts the simple-quota owner ref from an extent item when present.
- `btrfs_cross_ref_exist()` checks whether a data extent has references other than a specified inode/offset, conservatively including delayed refs.

Delayed-ref and refcount APIs:
- `btrfs_run_delayed_refs()` drains delayed ref heads for a transaction.
- `btrfs_cleanup_ref_head_accounting()` releases csum and simple quota reservations associated with a delayed-ref head.
- `btrfs_inc_extent_ref()` queues an explicit generic ref increment.
- `btrfs_free_extent()` queues or directly handles an extent reference drop depending on ref type and tree-log status.
- `btrfs_inc_ref()` and `btrfs_dec_ref()` walk an extent buffer and queue child data/tree ref changes.
- `btrfs_set_disk_extent_flags()` queues extent item flag updates.

Allocation and reservation APIs:
- `btrfs_reserve_extent()` is the public logical allocator entry point. It returns the chosen range in a `struct btrfs_key`.
- `btrfs_free_reserved_extent()` returns an unused reservation to free space.
- `btrfs_pin_reserved_extent()` moves a reserved tree block extent to pinned state.
- `btrfs_alloc_reserved_file_extent()` queues materialization of an already reserved file extent.
- `btrfs_alloc_logged_file_extent()` materializes an extent discovered during log replay and excludes it from free space.
- `btrfs_alloc_tree_block()` reserves, initializes, locks, and returns a new metadata extent buffer.
- `btrfs_free_tree_block()` queues or completes metadata block free handling.

Commit, deletion, discard, and remap APIs:
- `btrfs_finish_extent_commit()` finalizes pinned extent ranges after transaction commit and handles removed block group cleanup.
- `btrfs_drop_snapshot()` deletes a root/snapshot tree with optional backref updates and relocation mode.
- `btrfs_drop_subtree()` drops a relocation subtree rooted at a locked node.
- `btrfs_error_unpin_extent_range()` unpins an extent range during error cleanup without returning it to free space.
- `btrfs_discard_extent()` discards or resets the physical stripes backing a logical range.
- `btrfs_trim_fs()` implements filesystem-wide FITRIM behavior.
- `btrfs_handle_fully_remapped_bgs()` and `btrfs_complete_bg_remapping()` finish block groups whose extents have been remapped away.

Interface boundaries:
- This header is not a data-structure owner for extent items themselves; on-disk item definitions come from Btrfs format/accessor headers.
- The exported allocator control struct exposes internal allocator state, so callers in this tree can trace allocation behavior, but normal external callers use `btrfs_reserve_extent()`.
- APIs consistently operate under an explicit transaction handle for persistent metadata changes, except lookup/check helpers and discard/trim routines that have separate synchronization requirements.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent-tree.h -->