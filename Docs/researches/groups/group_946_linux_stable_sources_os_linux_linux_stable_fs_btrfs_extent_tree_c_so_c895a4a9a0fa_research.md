# Group Research: group_946_linux_stable_sources_os_linux_linux_stable_fs_btrfs_extent_tree_c_so_c895a4a9a0fa

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux-stable`; this report covers only the two requested Btrfs extent-tree files.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent-tree.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/extent-tree.c

## Role

`extent-tree.c` is the central Btrfs implementation for extent ownership, extent reference accounting, physical/logical extent allocation, block-group pinning/unpinning, discard/trim, tree block allocation/freeing, and snapshot/subtree deletion. It sits below higher-level inode, file, relocation, log replay, transaction, qgroup, free-space, RAID stripe tree, and zoned-device code, and is responsible for keeping extent-tree items, backreferences, free-space records, and block-group accounting consistent.

The file implements both metadata and data extent lifecycles. Data extents are tracked by `BTRFS_EXTENT_ITEM_KEY` plus data backrefs; metadata can use old "fat" extent items or `SKINNY_METADATA` `BTRFS_METADATA_ITEM_KEY`s. The code has many compatibility paths for old extent formats, mixed block groups, simple quotas, relocation roots, tree-log roots, zoned filesystems, async/sync discard, and remapped block groups.

## Main Responsibilities

- Look up extent items and merge committed extent-tree state with pending delayed-reference state (`btrfs_lookup_data_extent()`, `btrfs_lookup_extent_info()`).
- Validate, locate, insert, update, and remove inline and keyed backreferences for data and tree blocks.
- Queue and run delayed refs, including extent-item creation, ref-count changes, last-ref frees, qgroup/simple-quota accounting, csum deletion, RAID extent deletion, free-space-tree updates, and transaction abort handling.
- Allocate physical extents from block groups with clustered allocation on regular filesystems and sequential allocation on zoned filesystems.
- Reserve, free, pin, unpin, and commit extents while maintaining block-group and `space_info` counters.
- Allocate and initialize new tree blocks and create their delayed extent refs.
- Free tree blocks, file extents, snapshots, and relocation subtrees while preserving Btrfs backreference rules.
- Issue discard/TRIM across mapped stripes, block groups, and device unallocated space.
- Finalize block-group remapping by discarding remapped ranges and removing now-unused remapped chunks/device extents.

## Backreference Model

The long in-file comment documents the Btrfs backreference rules:

- Backrefs distinguish all holders of an extent, support corruption/owner discovery, and enable shrinking/relocation.
- Implicit tree backrefs identify owner root and lowest key/level for non-shared owner-tree pointers.
- Full tree backrefs identify the parent block address, used when a tree block is not referenced by its owner tree or when shared state requires full backrefs.
- Data backrefs can be implicit `BTRFS_EXTENT_DATA_REF_KEY` entries keyed by a hash of `(root, owner inode, file offset)`, or full/shared `BTRFS_SHARED_DATA_REF_KEY` entries keyed by parent.
- Tree block refs are `BTRFS_TREE_BLOCK_REF_KEY` or `BTRFS_SHARED_BLOCK_REF_KEY`.
- Simple quotas may add an inline `BTRFS_EXTENT_OWNER_REF_KEY` before the real backrefs to record the allocating root.

Important helpers:

- `btrfs_get_extent_inline_ref_type()` validates inline ref type against expected data/tree context and prints the leaf on corruption.
- `hash_extent_data_ref()` builds the 64-bit data-ref key hash from CRC32C pieces.
- `match_extent_data_ref()` compares the full `(root, objectid, offset)` payload because hash collisions are possible.
- `extent_ref_type()` selects data/tree and shared/implicit ref key type from `parent` and `owner`.
- `lookup_inline_extent_backref()` searches an extent item's inline refs in their on-disk order, supports skinny metadata fallback to fat extent items, can reserve item growth for insertion, skips simple-quota owner refs, and returns `-EAGAIN` when a keyed ref is needed instead of another inline ref.
- `setup_inline_extent_backref()` and `update_inline_extent_backref()` grow/shrink the extent item, shift inline ref bytes, update aggregate extent refs, and apply delayed extent ops.
- `lookup_extent_backref()` first tries inline refs, then keyed tree/data refs.
- `insert_extent_data_ref()`, `remove_extent_data_ref()`, `insert_tree_block_ref()`, and `lookup_tree_block_ref()` handle non-inline backref items.

## Delayed References

Public entry points such as `btrfs_inc_extent_ref()`, `btrfs_free_extent()`, `btrfs_inc_ref()`, `btrfs_dec_ref()`, `btrfs_alloc_reserved_file_extent()`, and `btrfs_alloc_tree_block()` usually queue delayed refs instead of mutating the extent tree immediately. Running delayed refs is the main mutation pipeline:

- `run_delayed_data_ref()` handles data add/drop nodes. `BTRFS_ADD_DELAYED_REF` either inserts a newly reserved extent item or increments refs on an existing extent; `BTRFS_DROP_DELAYED_REF` frees refs through `__btrfs_free_extent()`.
- `run_delayed_tree_ref()` handles metadata add/drop nodes, enforces one ref per tree-block ref node, supports remap-tree drops, and records simple-quota deltas for new tree blocks.
- `run_one_delayed_ref()` dispatches by ref key type and pins reserved extents on errors when necessary.
- `btrfs_run_delayed_refs_for_head()` selects nodes from a delayed-ref head, merges refs, updates `head->ref_mod`, clears `must_insert_reserved` at the ownership handoff point, runs the ref, releases delayed-ref reservation bytes, and frees the delayed extent op.
- `cleanup_ref_head()` runs any leftover extent op, removes empty heads, pins abandoned reserved extents, deletes csums for abandoned new data extents, releases accounting, unlocks the head, and drops the head ref.
- `__btrfs_run_delayed_refs()` repeatedly selects heads until requested byte work is processed or all current heads are handled.
- `btrfs_run_delayed_refs()` wraps the loop, skips work during free-space-tree creation, aborts transactions on hard errors, and for `U64_MAX` keeps looping through pending block-group creation and newly added refs.

Delayed extent ops carry tree-block flag/key updates. `__run_delayed_extent_op()` sets extent flags and, for fat metadata items, stores tree block key/level information. `cleanup_extent_op()` discards ops that are superseded by inserting the reserved extent item.

## Freeing Extents

`__btrfs_free_extent()` is the authoritative on-disk ref drop routine. It:

- Locates the matching inline or keyed backref.
- Locates the owning `EXTENT_ITEM` or `METADATA_ITEM`, with quick neighbor lookup and slow fallback.
- Validates item size, metadata owner/level, and ref counts.
- Decrements aggregate refs and the matching backref when refs remain.
- Deletes the extent item and possible adjacent keyed shared ref when the last ref is dropped.
- For last data refs, recovers the simple-quota owner root from the inline owner ref if present.
- Calls `do_free_extent_accounting()` to remove remap-tree records, delete csums, delete RAID stripe tree extent records, record simple-quota delta, add free-space-tree entries, and update block-group usage.

`check_ref_cleanup()` opportunistically removes delayed-ref heads for just-freed blocks when no pending refs remain and reports whether an uninserted reserved extent needs further handling.

`btrfs_free_tree_block()` queues a delayed tree-ref drop except for tree-log blocks, then decides whether the physical tree block can be returned immediately or must be pinned. It pins written blocks, blocks visible to tree-mod-log users, and zoned blocks; otherwise it can return newly allocated, unwritten tree blocks directly to free space and free reserved bytes.

## Extent Allocation

`btrfs_reserve_extent()` is the public allocator. It chooses an allocation profile with `get_alloc_profile_by_root()`, fills `struct find_free_extent_ctl`, and calls `find_free_extent()`. If `-ENOSPC` reports a smaller largest hole and `num_bytes > min_alloc_size`, it retries with a smaller rounded size down to `min_alloc_size`.

`find_free_extent()`:

- Selects `space_info` by block-group profile, with zoned sub-space-info overrides for tree-log and data-relocation allocations.
- Chooses `BTRFS_EXTENT_ALLOC_CLUSTERED` for normal filesystems or `BTRFS_EXTENT_ALLOC_ZONED` for zoned filesystems.
- Uses hints from allocation clusters, active zoned block groups, dedicated tree-log block group, or dedicated data-relocation block group.
- Iterates block groups by RAID index under `groups_sem`, skipping readonly/remapped/incompatible block groups.
- Starts free-space caching for uncached groups and may wait once for cache progress in later loops.
- Applies size-class filtering until relaxed by later allocation loops.
- Allocates from a cluster, unclustered free space, or a zoned block group's sequential `alloc_offset`.
- Validates stripe alignment and block-group bounds, returns unused fragments, reserves bytes in the block group, increments reservation counters, and returns the found logical address in `ins`.
- Runs retry phases: no-wait caching, wait on caching, allow unset size class, force chunk allocation, ignore wrong size class, and finally drop empty-size/cluster hints.

Clustered allocation uses `btrfs_find_space_cluster()` and `btrfs_alloc_from_cluster()` via `find_free_extent_clustered()`, falling back to unclustered allocation when fragmented. `find_free_extent_unclustered()` marks the cluster fragmented and calls `btrfs_find_space_for_alloc()`.

Zoned allocation in `do_allocation_zoned()` is sequential-only. It enforces dedicated tree-log and data-relocation block groups, activates data block groups before use, checks zone capacity, advances `block_group->alloc_offset`, updates free-space control, and sets dedicated block-group state when needed.

## Reserved Extent and Tree Block Creation

`alloc_reserved_extent()` removes an already reserved range from the free-space tree and updates block-group used bytes.

`alloc_reserved_file_extent()` inserts the data extent item, optional simple-quota owner inline ref, and the first data/shared data inline ref, then calls `alloc_reserved_extent()`.

`alloc_reserved_tree_block()` inserts a metadata extent item unless it belongs to the remap tree, supports skinny and fat metadata formats, records tree-block info for fat metadata, writes the first tree/shared block inline ref, then calls `alloc_reserved_extent()`.

`btrfs_alloc_tree_block()` uses a block reservation, reserves a physical extent, initializes a new `extent_buffer`, and queues a delayed tree extent ref unless the target is the tree-log root. Relocation tree blocks are marked `BTRFS_BLOCK_FLAG_FULL_BACKREF` and use the relocation source root as the owning root.

## Snapshot and Subtree Deletion

The `walk_control` state machine drives snapshot deletion:

- `DROP_REFERENCE`: traverse blocks owned by the root being deleted, drop references to children that do not need visiting, and free blocks once children are processed.
- `UPDATE_BACKREF`: entered when a shared block must be walked to convert child refs to full backrefs before dropping the root's normal ref.

`btrfs_drop_snapshot()` starts or joins a transaction, runs delayed inode items, marks the root deleting, resumes from `drop_progress` if present, walks the tree while periodically updating root drop progress and ending/restarting transactions, deletes the root item and orphan item, frees qgroup metadata reservations, moves the dropped root to the dropped-root list or releases it, cleans qgroup state, wakes unfinished-drop waiters, and requeues unfinished non-relocation drops as dead roots.

`btrfs_drop_subtree()` is the relocation-only variant for a subtree below a known parent.

## Discard, Trim, and Commit

- `btrfs_issue_discard()` aligns ranges, skips superblock mirrors, chunks large discards, tolerates unsupported discard, and stops on interruption.
- `btrfs_discard_extent()` maps logical ranges to device stripes and handles missing/non-writeable devices.
- `btrfs_finish_extent_commit()` discards pinned ranges when requested, clears pinned state, unpins ranges, schedules async discard, and processes deleted block groups.
- `btrfs_trim_fs()` trims free block-group ranges first, then unallocated device ranges.
- `btrfs_complete_bg_remapping()` and `btrfs_handle_fully_remapped_bgs()` finish remapped block-group cleanup.

## Integrity Notes

The file treats extent-tree inconsistencies as corruption: missing roots, impossible item sizes, zero refs, invalid inline ref types, ref underflows, mismatched owners/levels, and impossible slot layouts return `-EUCLEAN` and often abort the transaction. Many partial-failure paths pin extents so space is not reused unsafely.

## Research Notes

This file is a cross-cutting consistency layer for Btrfs copy-on-write storage: allocation reserves space, delayed refs describe ownership changes, delayed-ref execution makes extent-tree/free-space/qgroup/csum/RAID state durable, commit unpins reusable space, and snapshot deletion drives large-scale reference drops and backref conversion. Any change here has broad blast radius across ENOSPC behavior, snapshot deletion, relocation, log replay, quotas, zoned mode, device replace, and discard.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent-tree.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/extent-tree.h

## Role

`extent-tree.h` is the public internal header for `extent-tree.c`. It declares the allocator control structure, inline-ref type enum, allocation policy enum, and the extent-tree APIs used by other Btrfs subsystems. It intentionally forward-declares most structures so callers do not need the full extent-tree implementation dependencies.

## Types

`enum btrfs_extent_allocation_policy` selects the allocation engine:

- `BTRFS_EXTENT_ALLOC_CLUSTERED`: regular free-space-cache based allocation, optionally using metadata/data allocation clusters.
- `BTRFS_EXTENT_ALLOC_ZONED`: sequential allocation for zoned filesystems.

`struct find_free_extent_ctl` is the state object passed through `find_free_extent()` and its helpers. Fields include request parameters, search position, cluster state, allocation context, cache retry state, loop/index state, result diagnostics, allocation policy, and block-group size-class preference.

`enum btrfs_inline_ref_type` is a local validation selector for inline backrefs:

- `BTRFS_REF_TYPE_INVALID`: invalid decoded inline ref.
- `BTRFS_REF_TYPE_BLOCK`: caller requires a tree-block ref.
- `BTRFS_REF_TYPE_DATA`: caller requires a data ref.
- `BTRFS_REF_TYPE_ANY`: caller accepts either tree or data refs.

## Declared API Groups

Lookup and inline-ref helpers:

- `btrfs_get_extent_inline_ref_type()`
- `hash_extent_data_ref()`
- `btrfs_lookup_data_extent()`
- `btrfs_lookup_extent_info()`
- `btrfs_get_extent_owner_root()`
- `btrfs_cross_ref_exist()`

Delayed refs and ref accounting:

- `btrfs_run_delayed_refs()`
- `btrfs_cleanup_ref_head_accounting()`
- `btrfs_inc_extent_ref()`
- `btrfs_free_extent()`
- `btrfs_inc_ref()`
- `btrfs_dec_ref()`
- `btrfs_set_disk_extent_flags()`

Allocation, reserved extents, and tree blocks:

- `btrfs_reserve_extent()`
- `btrfs_alloc_tree_block()`
- `btrfs_free_tree_block()`
- `btrfs_alloc_reserved_file_extent()`
- `btrfs_alloc_logged_file_extent()`
- `btrfs_free_reserved_extent()`
- `btrfs_pin_reserved_extent()`
- `btrfs_pin_extent()`
- `btrfs_pin_extent_for_log_replay()`
- `btrfs_finish_extent_commit()`

Snapshot/subtree deletion:

- `btrfs_drop_snapshot()`
- `btrfs_drop_subtree()`

Discard, trim, log replay exclusion, and block-group remap:

- `btrfs_exclude_logged_extents()`
- `btrfs_error_unpin_extent_range()`
- `btrfs_discard_extent()`
- `btrfs_trim_fs()`
- `btrfs_handle_fully_remapped_bgs()`
- `btrfs_complete_bg_remapping()`

## Dependencies and Include Shape

The header includes only `<linux/types.h>`, `block-group.h`, and `locking.h`, then forward-declares Btrfs structures used in prototypes. The direct include of `block-group.h` is needed for `enum btrfs_block_group_size_class` in `find_free_extent_ctl`; `locking.h` is needed for `enum btrfs_lock_nesting` in `btrfs_alloc_tree_block()`.

## Research Notes

The header exposes a broad surface because extent-tree management is shared by tree modification, file extent allocation, transaction commit, log replay, relocation, snapshot deletion, discard, and quotas. Most callers should use the high-level APIs here rather than directly manipulating extent items or delayed refs. `find_free_extent_ctl` is declared in the header but is effectively an implementation control block for the allocator rather than a general-purpose external contract.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/extent-tree.h -->