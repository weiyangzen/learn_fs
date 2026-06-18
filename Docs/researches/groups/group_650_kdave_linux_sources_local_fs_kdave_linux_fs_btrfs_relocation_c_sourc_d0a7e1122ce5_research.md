# Group Research: group_650_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_relocation_c_sourc_d0a7e1122ce5

Scope: `Docs/research_subset_a.md`  
Files read completely: 4/4

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/relocation.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/relocation.c

## Purpose

`relocation.c` implements Btrfs block-group relocation: moving all extents out of a target block group so the block group can be deleted, resized away, balanced, compacted, converted, or otherwise removed from active allocation. It supports two relocation mechanisms:

- The classic relocation-tree path, which creates special reloc roots, moves data through a data relocation inode, rewrites file extent pointers, and merges relocated tree blocks back into source trees.
- The newer remap-tree path, guarded by `REMAP_TREE`, which records logical remappings in the remap tree and copies physical contents while updating block-group/chunk accounting.

The file is central to balance/resize behavior and tightly integrates with transactions, delayed refs, qgroups, free-space tree, block-group state, chunk metadata, extent backrefs, page cache, ordered extents, and crash recovery.

## Main Data Structures

- `struct mapping_node` / `struct mapping_tree`: rb-tree mapping from a tree root block address to its relocation root.
- `struct tree_block`: queued tree block to relocate; stores bytenr, owner, first key, level, and whether the key has been read.
- `struct file_extent_cluster`: batches adjacent data extents for relocation while preserving extent boundaries.
- `enum reloc_stage`: distinguishes `MOVE_DATA_EXTENTS` from `UPDATE_DATA_PTRS`.
- `struct reloc_control`: per-block-group relocation state. It owns the target block group, extent root, relocation data inode, block reservation, backref cache, processed-block extent tree, reloc-root lists, dirty-subvolume list, data cluster, reservation counters, current search offset, current stage, and mode flags.
- `struct space_run`: temporary free/used run representation for remap-tree initialization.
- `struct reloc_io_private`: completion/refcount/status bundle for synchronous remap copy I/O.

## Public Entry Points

- `btrfs_relocate_block_group()`: top-level block-group relocation entry point.
- `btrfs_recover_relocation()`: mount-time recovery for interrupted relocation.
- `btrfs_init_reloc_root()`: transaction hook that creates or refreshes a reloc root for a modified shareable root.
- `btrfs_update_reloc_root()`: updates reloc-root root items, mappings, and dead-reloc-root state.
- `btrfs_reloc_clone_csums()`: clones checksums from old relocated data into ordered extents for the relocation inode.
- `btrfs_reloc_cow_block()`: transaction-time hook that updates relocation backref state when COW creates a relocated block.
- `btrfs_reloc_pre_snapshot()` / `btrfs_reloc_post_snapshot()`: snapshot hooks that reserve merge space and create reloc roots for new snapshots.
- `btrfs_should_cancel_balance()`: cancellation/error-injection point for balance/relocation.
- `find_reloc_root()`, `btrfs_should_ignore_reloc_root()`, `btrfs_get_reloc_bg_bytenr()`: query helpers for other Btrfs subsystems.
- `btrfs_translate_remap()`, `btrfs_remove_extent_from_remap_tree()`, `btrfs_last_identity_remap_gone()`: remap-tree lookup, removal, and final chunk-stripe teardown helpers.

## Classic Relocation Flow

`btrfs_relocate_block_group()` looks up the block group and extent root, waits for unfinished snapshot drops, rejects pinned-by-swapfile groups, allocates `reloc_control`, starts relocation cancellation state, makes the block group read-only, deletes old v1 free-space cache data, and creates a data relocation inode when the filesystem is not using the remap-tree path.

For the non-remap path, `do_nonremap_reloc()` repeatedly calls `relocate_block_group()` until no extents are found. The relocation normally runs in two stages:

1. `MOVE_DATA_EXTENTS`: data extents in the target block group are copied into the data relocation inode.
2. `UPDATE_DATA_PTRS`: metadata leaves containing file extent items are relocated/COWed and their file extent disk bytenrs are rewritten to point to the new data.

`prepare_to_relocate()` allocates and fills a temporary block reservation, installs `fs_info->reloc_ctl`, enables reloc-root creation, and commits a transaction so transaction hooks can create consistent reloc roots.

`find_next_extent()` scans the committed extent tree for unprocessed extent items inside the target block group, skipping ranges marked in `processed_blocks`.

Tree extents are added to an rb-tree via `add_tree_block()` or `__add_tree_block()`. `relocate_tree_blocks()` reads missing first keys, then relocates each block. COW-only roots and the data reloc tree use `relocate_cowonly_block()`; normal filesystem tree blocks build a backref tree with `build_backref_tree()` and relocate references through `relocate_tree_block()` / `do_relocation()`.

Data extents are batched by `relocate_data_extent()`. `relocate_file_extent_cluster()` preallocates matching extents in the data relocation inode, installs pinned extent maps pointing at the source disk range, reads/dirty-marks folios via `relocate_one_folio()`, and relies on writeback to allocate replacement extents. Extent boundaries are explicitly preserved with `EXTENT_BOUNDARY`.

After moving data, ordered ranges are waited via `btrfs_wait_ordered_range()`, the relocation inode mapping is invalidated, and the stage advances to `UPDATE_DATA_PTRS`.

During pointer update, `replace_file_extents()` scans relocated leaves for file extent items still pointing into the target block group, finds the corresponding new location in the relocation inode, updates the file extent disk bytenr, increments refs for the new extent, drops refs for the old extent, and drops extent maps from live inodes where needed.

## Reloc Roots And Merge

Reloc roots are special roots with objectid `BTRFS_TREE_RELOC_OBJECTID` and offset equal to the source root id. `create_reloc_root()` copies a root block, inserts a root item in the tree root, and returns a shareable reloc root. `__add_reloc_root()`, `__del_reloc_root()`, and `__update_reloc_root()` maintain both the rb-tree lookup and relocation root list.

`btrfs_init_reloc_root()` is called through transaction root recording. It skips dead reloc roots, existing reloc roots, non-create phases, and reloc roots themselves. Otherwise it creates a reloc root and stores it on `root->reloc_root`.

`btrfs_update_reloc_root()` updates the on-disk root item for a reloc root, refreshes the mapping if the node changed, and marks reloc roots dead when merge state has set refs to zero.

`prepare_to_merge()` reserves worst-case merge metadata, marks reloc roots with refs so recovery can resume merging, sets `merge_reloc_tree`, updates root items, and commits. `merge_reloc_roots()` then processes all reloc roots. For live roots, `merge_reloc_root()` walks relocated blocks in the reloc tree and calls `replace_path()` to swap matching unchanged subtrees between the source tree and reloc tree. For orphan/dead reloc roots it queues them for cleanup.

`clean_dirty_subvols()` drops merged reloc roots and orphan relocation roots. It carefully clears `root->reloc_root` and `BTRFS_ROOT_DEAD_RELOC_TREE` with memory barriers matching readers such as `have_reloc_root()`.

## Backref And COW Integration

The relocation algorithm depends on the backref cache to discover every parent path from a target block up to roots. `walk_up_backref()` and `walk_down_backref()` enumerate paths. `handle_useless_nodes()` prunes useless backref subtrees and marks blocks processed.

`select_one_root()` determines whether a block can be relocated through one root, needs full shared relocation, or is already a reloc-root block. `select_reloc_root()` records the owning root in the current transaction, substitutes the reloc root, updates `new_bytenr`, and populates `rc->backref_cache.path[]` for COW hooks.

`btrfs_reloc_cow_block()` is the hook used when Btrfs COWs a block while relocation is active. For reloc roots during reloc-tree creation it validates that the COWed buffer matches the expected backref node, stores the new buffer, queues pending upper-link work, marks first-COW blocks processed, and accounts relocated nodes. For leaves in `UPDATE_DATA_PTRS`, it calls `replace_file_extents()`.

## Remap-Tree Relocation

When `should_relocate_using_remap_tree()` allows remap relocation, the flow avoids the data relocation inode and classic reloc-tree merge.

`start_block_group_remapping()` caches the block group, runs delayed refs to make the free-space tree current, creates identity-remap items for used ranges with `create_remap_tree_entries()`, marks the block group/chunk as remapped, removes free-space-tree entries for the source group, and removes the in-memory free-space cache.

`create_remap_tree_entries()` scans the free-space tree under `bg->free_space_lock`, handles both extent and bitmap free-space entries, converts free-space holes into used identity-remap ranges, and batch-inserts `BTRFS_IDENTITY_REMAP_KEY` items into the remap root. It initializes `bg->identity_remap_count`.

`do_remap_reloc()` repeatedly calls `do_remap_reloc_trans()`. Each transaction finds the next identity-remap range, reserves a destination logical range, optionally aligns metadata ranges to nodesize, copies data directly from old to new logical addresses using remap I/O, removes destination free-space-tree entries, inserts `BTRFS_REMAP_KEY` and `BTRFS_REMAP_BACKREF_KEY` records, adjusts block-group remap accounting, and marks source bytes readonly.

`copy_remapped_data()` performs bounded synchronous read/write copying using page arrays and `btrfs_bio` with `is_remap = true`. It caps copy chunks to 1 MiB and one bio worth of pages.

`move_existing_remaps()` and `move_existing_remap()` handle remap entries that already point into a block group being relocated. They allocate new destination space, copy remapped data, rewrite the old remap item/backref, update free-space-tree state, and adjust source/destination `remap_bytes`.

`btrfs_translate_remap()` maps a logical address through either identity or non-identity remap items and clamps the caller-provided length to the item boundary.

`btrfs_remove_extent_from_remap_tree()` removes a deallocated range from remap-tree coverage. It finds the covering remap item, calls `remove_range_from_remap_tree()` to delete/split/reinsert affected items, adjusts identity counts and destination remap bytes, and returns `1` when a remap item was changed.

`btrfs_last_identity_remap_gone()` is called when a chunk has no identity mappings left. It removes device extents, updates devices, clears `CHUNK_ALLOCATED`, removes the block group from space-info accounting, clears pending stripe-removal state, truncates chunk stripes from the chunk item, and commits.

## Recovery And Snapshot Hooks

`btrfs_recover_relocation()` scans the tree root for `BTRFS_TREE_RELOC_OBJECTID` root items. It reloads reloc roots, marks missing source roots as garbage by zeroing refs, installs a new `reloc_control`, reattaches valid reloc roots to source roots, commits, merges reloc roots, commits again, cleans dirty subvolumes, and cleans orphan inodes from the data relocation tree on non-remap filesystems.

`btrfs_reloc_pre_snapshot()` adds metadata reservation when snapshotting while reloc roots are being merged. `btrfs_reloc_post_snapshot()` migrates reservation into the relocation block reservation when needed and creates a reloc root for the newly created snapshot.

## Error Handling And Concurrency

The file relies heavily on transaction aborts for metadata-update failures after on-disk state changes. Errors before mutations generally return directly. Several paths convert impossible-but-corruption-observable cases into `-EUCLEAN`, `-EINVAL`, or `-ENOENT`.

Important synchronization points include:

- `fs_info->reloc_mutex` for `fs_info->reloc_ctl`, reloc-root list transitions, and remap-tree mutation.
- `fs_info->cleaner_mutex` around classic block-group relocation.
- `fs_info->remap_mutex` around remap tree and remapped block-group state.
- block-group locks for `remap_bytes`, `identity_remap_count`, flags, and dirty-list insertion.
- memory barriers around dead reloc root state and `root->reloc_root`.
- `BTRFS_FS_RELOC_RUNNING` and `reloc_cancel_req` for cancellation coordination.
- extent locks and inode mmap locks when dropping extent maps during pointer replacement.

## Integration Points

This file integrates with:

- extent tree and delayed refs for extent reference replacement.
- root tree for reloc root insert/update/delete.
- transaction machinery for root recording and commit-time updates.
- backref walking for shared metadata relocation.
- qgroups/simple quotas for swapped subtree accounting and relocation source ownership.
- free-space cache/free-space tree for removing obsolete cache data and remap source/destination accounting.
- block-group and chunk code for read-only state, remapped flags, stripe removal, device extent removal, and space-info updates.
- page cache/writeback/ordered extents for relocating data extents.
- checksum tree for checksum cloning.
- zoned mode via `btrfs_zone_finish()`.
- RAID stripe tree behavior in relocation folio handling.

## Invariants And Risks

- Relocation must not start while unfinished snapshot drops exist, because partially dropped roots can have ambiguous extent references.
- Reloc roots intentionally hold multiple references: one from `root->reloc_root` and one from the relocation root list.
- Data relocation requires replacement extents to preserve source extent sizes and boundaries.
- `UPDATE_DATA_PTRS` must not race with unfinished relocation inode writeback from `MOVE_DATA_EXTENTS`.
- Backref resolution must reach valid shareable roots for shared tree relocation; failures usually indicate corruption or a backref bug.
- Remap-tree operations must keep forward remap items, backref items, identity counts, destination remap bytes, free-space-tree state, and chunk/block-group flags consistent.
- Many helper paths are recovery-sensitive; interrupted relocation is expected and handled through reloc root refs/drop progress and mount-time recovery.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/relocation.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/relocation.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/relocation.h

## Purpose

`relocation.h` declares the public Btrfs relocation interface used by balance, resize, transaction, snapshot, remap-tree, ordered-extent, and COW paths.

## Exposed Policy Helper

`should_relocate_using_remap_tree()` returns true only when:

- the filesystem has the `REMAP_TREE` incompat feature;
- the block group is not system metadata;
- the block group is not marked `BTRFS_BLOCK_GROUP_METADATA_REMAP`.

This keeps remap-tree relocation out of system chunks and metadata-remap chunks while allowing eligible data and metadata block groups to use the newer remap path.

## Declared APIs

- `btrfs_relocate_block_group()`: relocate all extents out of a block group.
- `btrfs_init_reloc_root()` / `btrfs_update_reloc_root()`: transaction-time reloc-root lifecycle hooks.
- `btrfs_recover_relocation()`: recover interrupted relocations at mount time.
- `btrfs_reloc_clone_csums()`: clone checksums for relocation ordered extents.
- `btrfs_reloc_cow_block()`: COW hook for relocation bookkeeping and data-pointer replacement.
- `btrfs_reloc_pre_snapshot()` / `btrfs_reloc_post_snapshot()`: snapshot integration hooks.
- `btrfs_should_cancel_balance()`: balance/relocation cancellation check.
- `find_reloc_root()`: lookup reloc root by original tree root bytenr.
- `btrfs_should_ignore_reloc_root()`: backref lookup helper for stale/dead reloc roots.
- `btrfs_get_reloc_bg_bytenr()`: report currently relocating block group.
- `btrfs_translate_remap()`: translate a logical range through remap-tree items.
- `btrfs_remove_extent_from_remap_tree()`: remove a freed range from remap-tree coverage.
- `btrfs_last_identity_remap_gone()`: finalize chunk/block-group metadata after the last identity remap disappears.

## Dependencies And Integration

The header forward-declares Btrfs core types and includes only `<linux/types.h>`, making it a low-overhead interface header. It depends on `struct btrfs_block_group` being visible to callers using the inline helper, so including files must already have the block-group definition available.

## Risk Notes

The inline helper encodes an important feature-policy gate. Any caller bypassing it could accidentally use remap-tree relocation for block groups that must stay on the classic path, especially system or metadata-remap groups.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/relocation.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/root-tree.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/root-tree.c

## Purpose

`root-tree.c` implements root-tree item and root-reference manipulation for Btrfs. The root tree records filesystem roots, snapshots/subvolumes, orphan roots, root refs/backrefs, and root item metadata. This file provides lookup, insert, update, delete, orphan discovery, reference management, root item compatibility initialization, timestamp updates, and metadata reservation for subvolume operations.

## Root Item Reading And Compatibility

`btrfs_read_root_item()` reads a root item from an extent buffer and handles older on-disk root item formats. If the item is smaller than the current structure, or if `generation` and `generation_v2` do not match, it zeroes fields from `generation_v2` onward and generates a fresh UUID. This lets newer kernels mount roots last written by older kernels while detecting partially initialized new fields.

`btrfs_check_and_init_root_item()` handles even older subvolume root items whose `flags` and `byte_limit` fields were not initialized. It uses `BTRFS_INODE_ROOT_ITEM_INIT` in the embedded inode flags as the compatibility marker, then initializes root flags and limit to zero.

## Lookup And Mutation APIs

`btrfs_find_root()` searches a root tree for a `BTRFS_ROOT_ITEM_KEY`. If `search_key->offset` is `-1ULL`, it finds the highest offset for a given root objectid. It returns the root item and/or actual found key when requested, releases the path before returning, and treats an impossible exact `-1ULL` root item as corruption.

`btrfs_set_root_node()` copies a root node extent buffer’s bytenr, level, and generation into a `btrfs_root_item`.

`btrfs_update_root()` finds an existing root item and rewrites it. If the old item is smaller than the current structure, it deletes and reinserts the item at the new size before writing. It updates `generation_v2` to match `generation` before writing, and aborts the transaction if the expected root key is missing or metadata mutation fails.

`btrfs_insert_root()` sets `generation_v2` and inserts a full-size root item.

`btrfs_del_root()` deletes a root item from the tree root, returning `-EUCLEAN` if the key was expected but not found.

## Orphan Root Handling

`btrfs_find_orphan_roots()` scans `BTRFS_ORPHAN_OBJECTID` / `BTRFS_ORPHAN_ITEM_KEY` items in the tree root. For each orphan item:

- If the referenced root no longer exists, it joins a transaction and removes the stale orphan item.
- If the root exists and has zero refs, it checks `drop_progress`.
- Nonzero drop progress marks `BTRFS_FS_UNFINISHED_DROPS` and `BTRFS_ROOT_UNFINISHED_DROP`.
- The root is marked `BTRFS_ROOT_DEAD_TREE` and queued with `btrfs_add_dead_root()`.

This is important for mount-time cleanup and for preventing relocation from running while partially dropped snapshots remain.

## Root Ref And Backref Management

`btrfs_add_root_ref()` inserts both a `BTRFS_ROOT_BACKREF_KEY` and matching `BTRFS_ROOT_REF_KEY`. Each item stores directory id, sequence, name length, and name bytes. Any insertion failure aborts the transaction.

`btrfs_del_root_ref()` deletes both directions. It validates directory id, name length, and name bytes before deleting the backref, returns the stored sequence, then deletes the forward ref. Missing or mismatched items return `-ENOENT`.

These functions keep subvolume/snapshot name references bidirectional in the root tree.

## Timestamps And Reservations

`btrfs_update_root_times()` updates a root item’s ctransid and ctime under `root_item_lock` using real time and the current transaction id.

`btrfs_subvolume_reserve_metadata()` reserves metadata for subvolume create/delete operations. It separately handles qgroup preallocation because subvolume operations affect multiple trees and do not fit normal transaction reservation accounting. It reserves qgroup metadata, reserves block-rsv metadata, optionally falls back to the global block reservation, and records qgroup reservation bytes in the block reservation.

## Dependencies And Integration

This file integrates with:

- tree search/insert/delete helpers from ctree code.
- transaction joining and abort paths.
- disk I/O root loading through `btrfs_get_fs_root()`.
- orphan item deletion and dead-root queues.
- qgroup metadata reservation and release.
- space-info and block reservation accounting.
- root tree consumers such as relocation, snapshots, subvolume creation/deletion, and mount recovery.

## Error Handling And Risks

- Missing expected root items during update/delete are treated as filesystem corruption.
- Root item resizing is transactional and aborts on failure after mutation.
- Root ref deletion validates the user-visible name and directory metadata before deleting to avoid removing the wrong reference.
- Orphan root scanning intentionally marks unfinished drops so relocation can block until cleanup completes.
- Qgroup reservation failures are unwound when block reservation fails.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/root-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/root-tree.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/root-tree.h

## Purpose

`root-tree.h` declares the public interface for Btrfs root-tree operations implemented in `root-tree.c`.

## Declared APIs

- `btrfs_subvolume_reserve_metadata()`: reserve metadata and qgroup accounting for subvolume operations.
- `btrfs_add_root_ref()` / `btrfs_del_root_ref()`: maintain bidirectional root refs/backrefs for subvolume and snapshot directory entries.
- `btrfs_del_root()`: delete a root item from the tree root.
- `btrfs_insert_root()`: insert a new root item.
- `btrfs_update_root()`: update an existing root item, including old-format resizing.
- `btrfs_find_root()`: lookup root items by key, including highest-offset lookup.
- `btrfs_find_orphan_roots()`: scan and queue orphan roots during mount/recovery.
- `btrfs_set_root_node()`: copy extent-buffer node identity into a root item.
- `btrfs_check_and_init_root_item()`: initialize compatibility fields for older root items.
- `btrfs_update_root_times()`: update root ctime and transaction id.

## Dependencies And Integration

The header forward-declares the needed Btrfs and fscrypt types and includes only `<linux/types.h>`. It is used by code that creates, updates, deletes, recovers, or references Btrfs roots, including relocation and snapshot/subvolume paths.

## Risk Notes

The functions declared here mutate core namespace and root metadata. Callers must hold appropriate transaction context and pass root-tree keys that match the intended root item or reference direction.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/root-tree.h -->