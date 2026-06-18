# Group Research: group_254_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_relocation_c_sourc_2db951ba223d

Scope checked against `Docs/research_subset_a.md`: all listed files are under `sources/local-fs/btrfs-linux`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/relocation.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/relocation.c

This file implements Btrfs block-group relocation. It supports the classic relocation-root/data-relocation-inode algorithm and the newer remap-tree path used when the `REMAP_TREE` incompat feature is enabled for eligible non-system, non-metadata-remap block groups.

Core concepts:
- A `reloc_control` tracks the block group being relocated, extent root, temporary metadata reservation, data relocation inode, backref cache, processed-block state, relocation-root mapping tree, dirty subvolume roots, current data cluster, merge reservation accounting, stage, and mode flags.
- Classic relocation has two data stages: `MOVE_DATA_EXTENTS` moves data bytes into a data relocation tree inode; `UPDATE_DATA_PTRS` updates file extent items to point at the new physical extents.
- Relocation roots are special `BTRFS_TREE_RELOC_OBJECTID` snapshots of fs roots. They hold relocated tree blocks until merge time, when subtrees are swapped back into the real roots.
- The remap-tree path records logical remappings in `fs_info->remap_root` using identity-remap, remap, and remap-backref items instead of rewriting every tree/file reference in the source block group immediately.

Primary public entry points:
- `btrfs_relocate_block_group()` is the main balance/shrink relocation entry. It waits for unfinished drops, makes the target block group read-only, deletes v1 free-space cache data, waits for reservations/NOCOW/ordered IO, finishes the zone if needed, and dispatches either remap-tree relocation or classic relocation.
- `btrfs_recover_relocation()` resumes interrupted relocation after mount by finding relocation roots in the tree root, reattaching them to their fs roots, merging them, cleaning dirty subvolumes, and cleaning the data relocation tree orphan inode for non-remap-tree filesystems.
- `btrfs_init_reloc_root()` creates or refreshes a relocation root when a shareable root is recorded in a transaction during relocation.
- `btrfs_update_reloc_root()` persists relocation-root root items at transaction commit and marks dead relocation trees during merge.
- `btrfs_reloc_cow_block()` is the COW hook used by ctree code to connect newly COWed blocks to relocation backref-cache nodes and, during data-pointer update, rewrite file extent items in newly COWed leaves.
- `btrfs_reloc_clone_csums()` clones existing checksums from the old data extent range into ordered checksums for relocated data.
- `btrfs_reloc_pre_snapshot()` and `btrfs_reloc_post_snapshot()` integrate snapshot creation with in-progress relocation-root merging.
- `btrfs_translate_remap()` translates logical reads through remap-tree items and clamps the requested length to the current remap record.
- `btrfs_remove_extent_from_remap_tree()` removes a freed range from remap-tree records and repairs/splits surrounding mappings.
- `btrfs_last_identity_remap_gone()` handles the point where a remapped chunk has no remaining identity ranges, removing dev extents, clearing chunk allocation bits, detaching the block group from its space info, and truncating chunk stripes.

Classic relocation flow:
- `prepare_to_relocate()` allocates a temporary block reservation, initializes search state, sets `fs_info->reloc_ctl`, joins and commits a transaction so relocation roots can be created consistently.
- `find_next_extent()` scans the commit-root extent tree over the target block group, skipping processed metadata ranges.
- Tree extents are gathered with `add_tree_block()` or `__add_tree_block()`, which derive level, generation, and sometimes owner from extent items/inline refs.
- Data extents are clustered by `relocate_data_extent()` and migrated through `relocate_file_extent_cluster()`, which preallocates matching destination extents, installs pinned extent maps, reads folios, marks delalloc ranges, preserves extent boundaries, and waits for writeback before pointer update.
- `relocate_tree_blocks()` readaheads missing tree blocks, resolves their first keys, and relocates each block through either a COW-only path for non-fs/data-reloc trees or a full backref-tree path for fs trees.
- `build_backref_tree()` builds a breadth-first backref graph from a target tree block to roots, using the backref cache and pruning useless nodes.
- `relocate_tree_block()` chooses whether a block can be handled by root replacement or needs `do_relocation()`, reserving enough metadata first.
- `do_relocation()` COWs or links relocated blocks into upper blocks, updates delayed refs, manages pending backref-cache nodes, and asserts that reservation failures have been prehandled.
- `prepare_to_merge()` marks relocation roots as mergeable/orphaned depending on prior errors, reserves merge metadata, and commits state so recovery can resume.
- `merge_reloc_roots()` and `merge_reloc_root()` walk relocation trees, use `replace_path()` to swap unchanged subtrees between reloc and fs roots, record qgroup swapped-block state, save progress in `drop_progress`, invalidate extent maps after data pointer replacement, and queue dead relocation roots for cleanup.
- `clean_dirty_subvols()` drops merged or orphan relocation roots with `btrfs_drop_snapshot()` and clears root relocation state.

Data pointer and cache handling:
- `replace_file_extents()` scans a leaf for non-inline file extent items pointing into the target block group, drops in-memory extent maps for live regular inodes where possible, replaces disk bytenrs with the data relocation inode’s new locations, and updates old/new data refs.
- `get_new_location()` looks up the matching file extent in the data relocation inode and validates size and encoding assumptions.
- `delete_v1_space_cache()` and `delete_block_group_cache()` remove v1 space-cache inodes whose data extents would otherwise block data relocation.
- `invalidate_extent_cache()` drops affected extent maps after relocated file extent leaves are swapped back into fs roots.

Remap-tree relocation flow:
- `start_block_group_remapping()` caches the block group, runs delayed refs so the free-space tree is current, creates initial identity-remap items from free-space tree holes, marks the chunk and block group as remapped, removes block-group free-space records, and removes the old free-space cache.
- `create_remap_tree_entries()` converts free-space extent/bitmap records into identity-remap ranges representing currently used logical space.
- `do_remap_reloc()` repeatedly calls `do_remap_reloc_trans()` to find the next identity-remap range, reserve a destination logical range, physically copy data with remap bios, remove destination free-space records, replace the identity range with remap/backref items, and mark the source block group fully remapped when the identity count reaches zero.
- `copy_remapped_data()` copies data in bounded chunks using `copy_remapped_data_io()`; remap bios set `bbio->is_remap` and use completion/refcount tracking in `reloc_io_private`.
- `move_existing_remaps()` and `move_existing_remap()` move remap-tree entries that already point into a block group being relocated again, including physical copy, remap/backref updates, free-space tree updates, and remap byte accounting.
- `adjust_block_group_remap_bytes()` and `adjust_identity_remap_count()` update block-group remap counters, dirty block groups in the transaction, and mark unused or fully-remapped block groups when counters reach zero.
- `remove_range_from_remap_tree()` deletes or splits identity/remap records around a hole, removes backrefs for non-identity mappings, updates destination remap bytes, and returns the removed overlap length.

Concurrency and cancellation:
- `reloc_chunk_start()`/`reloc_chunk_end()` serialize cancellable relocation through `BTRFS_FS_RELOC_RUNNING` and `reloc_cancel_req`.
- `set_reloc_control()`/`unset_reloc_control()` publish or clear `fs_info->reloc_ctl` under `reloc_mutex`.
- Remap-tree mutations are serialized with `fs_info->remap_mutex`.
- Classic relocation takes `cleaner_mutex` around `relocate_block_group()` so cleaner/drop interactions stay ordered.
- `btrfs_should_cancel_balance()` checks balance cancellation, relocation cancellation, and fatal signals, and is explicitly error-injection enabled.

Error handling and invariants:
- Many structural inconsistencies return `-EUCLEAN` with diagnostics, especially missing roots, mismatched relocation roots, malformed backrefs, or impossible remap-tree state.
- Mutations after reference changes abort the transaction on failure.
- Relocation-root lifetime is reference-count sensitive: relocation roots can be held by `root->reloc_root`, `rc->reloc_roots`, dirty cleanup lists, and recovery lists.
- Processed tree blocks are tracked in an extent IO tree to avoid duplicate relocation work.
- Simple quota mode records the source owner root on the data relocation root so replacement allocations are attributed to the eventual owner.
- Qgroup subtree-swap accounting is deliberately delayed by recording swapped blocks before exchanging fs and relocation subtrees.
- Remap-tree block groups must maintain coherent `remap_bytes`, `identity_remap_count`, free-space tree contents, chunk flags, and block-group runtime flags.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/relocation.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/relocation.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/relocation.h

This header declares the Btrfs relocation interface used by balance, transaction commit, COW, snapshot, inode writeback, extent-freeing, and volume mapping code.

Public helper:
- `should_relocate_using_remap_tree()` returns true only when the filesystem has the `REMAP_TREE` incompat feature and the block group is not system and not `BTRFS_BLOCK_GROUP_METADATA_REMAP`.

Declared relocation APIs:
- `btrfs_relocate_block_group()` relocates all extents in a block group.
- `btrfs_init_reloc_root()` and `btrfs_update_reloc_root()` create/update relocation roots during transactions.
- `btrfs_recover_relocation()` resumes interrupted relocation on mount.
- `btrfs_reloc_clone_csums()` attaches cloned checksum records to relocated ordered extents.
- `btrfs_reloc_cow_block()` lets COW code notify relocation about newly COWed tree blocks.
- `btrfs_reloc_pre_snapshot()` and `btrfs_reloc_post_snapshot()` adjust snapshot reservations and create relocation roots for snapshots created during relocation.
- `btrfs_should_cancel_balance()` exposes the relocation/balance cancellation predicate.
- `find_reloc_root()` looks up a relocation root by the source root block bytenr.
- `btrfs_should_ignore_reloc_root()` tells backref lookup when an old relocation root should be ignored.
- `btrfs_get_reloc_bg_bytenr()` reports the currently relocating block group start while holding `reloc_mutex`.
- `btrfs_translate_remap()` maps logical addresses through the remap tree.
- `btrfs_remove_extent_from_remap_tree()` removes freed ranges from remap-tree records.
- `btrfs_last_identity_remap_gone()` performs final chunk/block-group cleanup after the last identity remap disappears.

Integration notes:
- The header forward-declares the heavy Btrfs structures but relies on callers already having definitions for `struct btrfs_block_group`, `struct btrfs_path`, and `struct btrfs_chunk_map` through surrounding includes.
- The remap-tree APIs are coupled to volume mapping, extent freeing, block-group cleanup, and chunk/device extent maintenance.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/relocation.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/root-tree.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/root-tree.c

This file implements root-tree item lookup, insertion, update, deletion, root reference/backreference items, orphan-root discovery, root-item compatibility initialization, root timestamp updates, and metadata reservation for subvolume operations.

Root item compatibility:
- `btrfs_read_root_item()` reads a root item from a leaf and handles old on-disk root item sizes.
- If the item is shorter than the current structure, or `generation` and `generation_v2` disagree, fields from `generation_v2` onward are cleared and a new random UUID is generated.
- This preserves mount compatibility for roots last written by older kernels that did not know newer root-item fields.
- `btrfs_check_and_init_root_item()` handles older subvolumes that did not initialize `root_item->flags` and `root_item->byte_limit`, using `BTRFS_INODE_ROOT_ITEM_INIT` in the embedded inode flags as the migration marker.

Root item operations:
- `btrfs_find_root()` searches the root tree for a `BTRFS_ROOT_ITEM_KEY`. If the search key offset is `-1ULL`, it finds the highest offset for the objectid. It can return the decoded `btrfs_root_item` and the actual found key.
- `btrfs_set_root_node()` copies a root node extent buffer’s bytenr, level, and generation into a root item.
- `btrfs_update_root()` searches for an existing root item, enlarges old short items by deleting/reinserting them when needed, synchronizes `generation_v2`, and writes the full root item back to the tree.
- `btrfs_insert_root()` inserts a new root item and sets `generation_v2` to match `generation`.
- `btrfs_del_root()` deletes an exact root item from the tree root and treats a missing expected key as filesystem corruption (`-EUCLEAN`).

Orphan root recovery:
- `btrfs_find_orphan_roots()` scans `BTRFS_ORPHAN_OBJECTID/BTRFS_ORPHAN_ITEM_KEY` items in the tree root.
- If an orphan item points to a missing root, it joins a transaction and deletes the stale orphan item.
- If the root exists and has zero refs, it marks the root as dead, adds it to dead-root cleanup, and detects nonzero `drop_progress`.
- Roots with nonzero drop progress set `BTRFS_FS_UNFINISHED_DROPS` and `BTRFS_ROOT_UNFINISHED_DROP`, which blocks relocation until incomplete snapshot deletion is finished.

Root reference operations:
- `btrfs_add_root_ref()` inserts both the backref (`BTRFS_ROOT_BACKREF_KEY`) and forward ref (`BTRFS_ROOT_REF_KEY`) items, storing parent dirid, sequence, name length, and name bytes.
- `btrfs_del_root_ref()` deletes the matching backref and forward ref, validating dirid, name length, and name bytes, and returns the stored sequence to the caller.
- These functions encode the subvolume/snapshot directory relationship in both lookup directions.

Timestamps and reservation:
- `btrfs_update_root_times()` updates root ctransid and ctime under `root_item_lock` using current real time.
- `btrfs_subvolume_reserve_metadata()` reserves metadata for subvolume/snapshot create/delete style operations that touch multiple roots and the root tree.
- When qgroups are enabled, it pre-reserves qgroup metadata for the parent inode and directory entries, then reserves block-rsv metadata with full flushing and optionally migrates from the global reserve.
- On failure it releases qgroup preallocation; on success it records the qgroup reservation in the supplied block reservation.

Error handling:
- Missing mandatory root items and failed root-ref insertions abort the current transaction where appropriate.
- Root lookup releases paths before returning in all normal cases.
- Orphan cleanup logs failures to join transactions or delete stale orphan items.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/root-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/root-tree.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/root-tree.h

This header declares the root-tree API implemented by `root-tree.c`.

Public interface:
- `btrfs_subvolume_reserve_metadata()` reserves block and qgroup metadata for subvolume/snapshot operations.
- `btrfs_add_root_ref()` and `btrfs_del_root_ref()` create/delete paired root ref and root backref items for subvolume directory references.
- `btrfs_del_root()` deletes a root item by key.
- `btrfs_insert_root()` inserts a new root item.
- `btrfs_update_root()` updates an existing root item, including old-item-size migration.
- `btrfs_find_root()` searches for a root item and optionally returns both decoded item and found key.
- `btrfs_find_orphan_roots()` scans orphan root items at mount/recovery time and queues dead roots.
- `btrfs_set_root_node()` copies extent-buffer root node identity into a root item.
- `btrfs_check_and_init_root_item()` initializes legacy root item flags/limits.
- `btrfs_update_root_times()` updates root ctime and ctransid.

Integration notes:
- The header forward-declares Btrfs transaction, path, root, root item, block reservation, key, fs info, extent buffer, and encrypted-name string structures.
- It is used by transaction, subvolume/snapshot, orphan cleanup, root loading, and relocation code that must manipulate root-tree metadata without depending on the implementation details.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/root-tree.h -->