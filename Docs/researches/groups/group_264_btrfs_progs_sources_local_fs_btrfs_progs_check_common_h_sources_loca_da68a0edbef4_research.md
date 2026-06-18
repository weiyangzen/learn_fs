# Group Research: group_264_btrfs_progs_sources_local_fs_btrfs_progs_check_common_h_sources_loca_da68a0edbef4

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/local-fs/btrfs-progs/check` files. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/check/common.h -->
# File Research: sources/local-fs/btrfs-progs/check/common.h

## Scope

This header defines shared in-memory records and cache/tree containers used by Btrfs check code for chunk, block-group, and device-extent validation.

## Public APIs And Data Structures

- Declares global `gfs_info`.
- `struct block_group_record` tracks an on-disk block group item plus actual/disk usage and list/cache links.
- `struct block_group_tree` wraps the block-group cache tree, pending extents tree, and block-group list.
- `struct stripe` records one chunk stripe’s devid, offset, and device UUID.
- `struct chunk_record` records a chunk item, stripes, type/profile fields, block-group linkage, device-extents list, and alignment status.
- `struct device_extent_record` records a device extent and its links into chunk/device orphan lists.
- `struct device_extent_tree` stores device extents plus orphan lists for extents missing chunk or device ownership.
- Inline helpers initialize block-group and device-extent trees, compute flexible `chunk_record` size, and validate `num_stripes`.
- Declares insertion/free helpers, record constructors from tree leaves, `calc_stripe_length()`, and `check_chunks()`.

## Dependencies

- Uses Btrfs core types from `kernel-shared/ctree.h`.
- Uses `cache_tree`/`cache_extent`, `extent_io_tree`, and kernel-style lists.
- Consumed by chunk/device/block-group check and repair paths.

## Risks And Invariants

- `check_num_stripes()` prevents divide-by-zero and invalid RAID5/RAID6 stripe counts.
- Chunk and device-extent orphan lists are part of correctness reporting; moving records between lists must preserve ownership semantics.
- `chunk_record` uses a flexible trailing stripe array, so allocations must use `btrfs_chunk_record_size()`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/check/common.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/check/mode-common.c -->
# File Research: sources/local-fs/btrfs-progs/check/mode-common.c

## Scope

This file implements repair and validation utilities shared by original and low-memory Btrfs check modes: checksum range counting/reconstruction, inode-item creation and mode repair, lost+found linking, tree-child validation, metadata exclusion, device/super repairs, and subvolume orphan repair.

## Public APIs Covered

- `check_prealloc_extent_written()` detects whether a preallocated extent has been written through another reference.
- `count_csum_range()` counts csum-covered bytes in a logical range.
- `insert_inode_item()` creates an inode item with current timestamps and conservative metadata.
- `link_inode_to_lostfound()` creates `lost+found` and links otherwise unreferenced inodes into it.
- `check_dev_size_alignment()`, `check_child_node()`, `reada_walk_down()`.
- Metadata allocation safety helpers: `reset_cached_block_groups()`, `pin_metadata_blocks()`, `exclude_metadata_blocks()`, `cleanup_excluded_extents()`.
- Directory and inode-mode repair helpers: `delete_corrupted_dir_item()`, `detect_imode()`, `reset_imode()`, `repair_imode_common()`, `check_repair_free_space_inode()`.
- Repair helpers: `recow_extent_buffer()`, `get_extent_item_generation()`, `repair_dev_item_bytes_used()`, `fill_csum_tree()`, `check_and_repair_super_num_devs()`, `repair_subvol_orphan_item()`.

## Control Flow And Behavior

- Prealloc csum validation walks inline and keyed extent refs, then consults referenced file extents to distinguish truly odd prealloc csums from valid shared written extents.
- `count_csum_range()` searches the csum tree, steps across csum items, and accumulates only overlapping covered bytes.
- Lost+found repair chooses a new inode number, creates `lost+found`, links the inode, and appends `.INO` suffixes when names conflict.
- Child-node validation compares parent key, block pointer, and generation against the child header/first key.
- Inode mode detection uses root-inode special handling, inode refs plus matching dir items/indexes, directory/file extent hints, and rdev fallback.
- Checksum tree rebuild can traverse fs trees or extent trees. It reads data sectors, inserts csums, then removes csums for NODATASUM or preallocated ranges.
- Super `num_devices` repair counts device items in the chunk tree and writes all superblocks without a transaction.
- Device item bytes-used repair updates in-memory device accounting before starting a transaction to avoid allocation side effects.

## State And Dependencies

- Defines global `g_task_ctx`.
- Uses global check state from `mode-common.h`: `gfs_info`, options such as `opt_check_repair`, and accounting globals.
- Depends on Btrfs transaction, tree search, extent/backref, csum, device, and repair APIs.

## Risks And Invariants

- Repair helpers frequently release and reacquire paths because COW can invalidate old paths.
- Csum reconstruction must avoid adding invalid checksums for NODATASUM and unwritten prealloc extents.
- `insert_inode_item()` is intentionally incomplete and warns users to inspect permissions/content.
- Metadata exclusion and pinning are repair-safety mechanisms; failing them risks overwriting metadata during fsck repair.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/check/mode-common.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/check/mode-common.h -->
# File Research: sources/local-fs/btrfs-progs/check/mode-common.h

## Scope

This header declares shared state, task/progress structures, utility predicates, and repair/check helpers used by both Btrfs check modes.

## Public APIs And Data Structures

- `struct node_refs` caches bytenr/ref/check/full-backref state per B-tree level for shared-node traversal.
- `enum task_position` and `struct task_ctx` track fsck progress phases and item counts.
- Declares global accounting and control state: bytes used, csum bytes, btree bytes, fs/extent tree bytes, data allocated/referenced, duplicate/delete lists, `no_holes`, `init_extent_tree`, `check_data_csum`, `gfs_info`, and `roots_info_cache`.
- `imode_to_type()` maps POSIX inode modes to Btrfs dir-entry file types.
- `fs_root_objectid()` identifies subvolume/data-reloc/tree-reloc roots.
- Declares shared repair/check functions implemented in `mode-common.c`.
- `is_valid_imode()` validates file-type bits and rejects unused mode bits.
- `btrfs_check_subpage_eb_alignment()` warns about tree blocks not aligned to nodesize.

## Dependencies

- Uses Btrfs tree constants, access types, list helpers, and message helpers.
- Couples check modes to global fsck options and Btrfs transaction/root/path APIs.

## Risks And Invariants

- `node_refs` is central to avoiding repeated shared-tree checks and deciding full-backref expectations.
- `imode_to_type()` assumes valid `S_IFMT` bits; invalid modes are filtered separately by `is_valid_imode()`.
- Subpage alignment warnings are conservative because the checker cannot know every future page size.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/check/mode-common.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/check/mode-lowmem.c -->
# File Research: sources/local-fs/btrfs-progs/check/mode-lowmem.c

## Scope

This file implements the low-memory Btrfs checker. It walks trees directly rather than building full in-memory indexes, validates fs-root item relationships, file extents, checksums, extent-tree backrefs, chunks, block groups, devices, and performs scoped repairs when `opt_check_repair` is enabled.

## Public Entry Points

- `check_fs_roots_lowmem()` checks fs/subvolume roots and root refs/backrefs.
- `check_chunks_and_extents_lowmem()` checks chunk, tree, extent, device, block-group, and backref consistency, then reconciles block accounting in repair mode.

## Major Internal Workflows

- Shared-node handling: `calc_extent_flag()`, `need_check()`, and `update_nodes_refs()` decide whether shared blocks need checking and whether full backrefs are expected.
- Repair safety: `avoid_extents_overwrite()` can allocate a fresh metadata chunk or exclude metadata blocks; `end_avoid_extents_overwrite()` cleans this state.
- Directory/ref validation: `find_dir_index()`, `find_dir_item()`, `find_inode_ref()`, `check_inode_ref()`, `check_inode_extref()`, and `check_dir_item()` cross-check dir items, dir indexes, inode refs/extrefs, inode items, file types, hashes, and duplicate names.
- Inode repair: recreates missing inode items, repairs mode, nlink, nbytes, dir isize, orphan items, generation/transid, and missing root-dir inode/ref cases.
- File extent validation: checks inline extent sizes, regular/prealloc types, generation bounds, checksum coverage, NODATASUM/compression rules, holes, alignment, symlink constraints, and data backrefs.
- Extent/backref validation: checks tree block refs, shared refs, data refs, inline-ref ordering, referencer existence, extent generation, crossing stripe boundaries, chunk type compatibility, and subpage alignment.
- Chunk/device/block-group validation: validates chunk stripes, dev extents, block-group items, device bytes used, device size boundaries, dev extent overlap, and super bytes-used accounting.
- Tree traversal: `walk_down_tree()` and `walk_up_tree()` perform bounded low-memory traversal with block validation, child-node checks, optional full tree item checks, and accounting.

## Repair Behavior

- Missing tree-block or data backrefs can be recreated by inserting extent items and incrementing refs.
- Bad referencer backrefs can be removed with `btrfs_free_extent()` or item deletion.
- Missing block-group items for chunks can be recreated.
- Missing device extents can be removed when repair is enabled.
- Block-group/super bytes-used errors are ultimately reconciled by `repair_block_accounting()`.
- Paths are re-searched after COW-affecting repairs.

## State And Accounting

- Static state: `last_allocated_chunk`, `total_used`, and `found_free_ino_cache`.
- Updates shared globals such as `bytes_used`, `total_btree_bytes`, `total_csum_bytes`, `data_bytes_allocated`, and `data_bytes_referenced`.
- Uses `g_task_ctx.item_count` during root traversal.

## Dependencies

- Depends heavily on Btrfs core tree search, extent/backref, transaction, csum, chunk/device, tree-checker, and repair APIs.
- Uses shared helpers from `mode-common.c` for csum counting, prealloc-written detection, imode repair, child validation, metadata exclusion, and device/super repair.

## Risks And Invariants

- Low-memory checking trades global indexes for careful tree walking; path validity after repair is a recurring concern.
- Shared tree blocks must only be fully checked/accounted once, while still validating referential integrity.
- Repair operations must avoid overwriting metadata being checked.
- Backref strictness changes for shared snapshots and full-backref parents; false strictness would misclassify valid shared extents.
- Some errors are fatal because continuing could loop, follow corrupt blocks, or operate on invalid item sizes.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/check/mode-lowmem.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/check/mode-lowmem.h -->
# File Research: sources/local-fs/btrfs-progs/check/mode-lowmem.h

## Scope

This header defines low-memory checker error-bit constants and declares the two lowmem check entry points.

## Public APIs And Constants

- Fs-tree error bits include root-dir errors, missing/mismatched dir items, inode refs, inode items, file extents, csums, link counts, nbytes/isize, orphan items, root refs, dir indexes, block-group accounting, inode flags, dir hash mismatch, bad inode mode, invalid generation, super bytes-used mismatch, duplicate filename, and unknown key.
- Low-level extent/backref error bits include missing/mismatched backrefs, unaligned bytes, missing/mismatched referencers, crossing stripe boundaries, item-size mismatch, unknown type, accounting mismatch, chunk type mismatch, and out-of-order inline backrefs.
- Declares `check_fs_roots_lowmem()` and `check_chunks_and_extents_lowmem()`.

## Dependencies And Role

- Used by `mode-lowmem.c` and callers that need aggregate lowmem error classification.

## Risks And Invariants

- Error bits are used both for reporting and repair dispatch; overlapping or misused bits can trigger the wrong repair path.
- `REFERENCER_MISMATCH` and `CROSSING_STRIPE_BOUNDARY` share the same bit value in different internal contexts, so interpretation depends on the checker path.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/check/mode-lowmem.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/check/mode-original.h -->
# File Research: sources/local-fs/btrfs-progs/check/mode-original.h

## Scope

This header defines the in-memory record model used by the original Btrfs checker mode: extent records, inode records, root records, backrefs, shared-node caches, and error-bit constants.

## Public Data Structures

- `struct extent_backref`, `data_backref`, and `tree_backref` model extent-tree backrefs in rbtrees/lists.
- `struct extent_record` tracks one extent’s size, refs, generation, owner info, flags, duplicate records, and validation state.
- `struct inode_backref` and `struct inode_record` track inode refs, dir-item/index state, inode item state, file extent holes, nlink/nbytes/isize accounting, checksum state, mismatch dir hashes, and unaligned extents.
- `struct root_backref` and `struct root_record` track subvolume root ref/backref consistency and root ref counts.
- `struct root_item_record`, `root_item_info`, and `bad_item` preserve root item and bad-item metadata.
- `struct shared_node`, `ptr_node`, `block_info`, and `walk_control` support shared tree walking and per-node inode/root caches.
- `struct file_extent_hole` and `unaligned_extent_rec_t` represent extent holes and unaligned extent records.

## Error Constants

- `REF_ERR_*` bits classify missing, duplicate, mismatched, too-long, and root-ref/root-backref errors.
- `I_ERR_*` bits classify inode-item, orphan, dir-index, dir-item, file-extent, csum, link-count, inode-flag, hash, imode, generation, nlink, xattr, deprecated free-inode, and duplicate filename problems.
- `FLAG_UNSET` explicitly initializes `extent_record::flag_block_full_backref`.

## Dependencies

- Uses kernel rbtrees/lists, Btrfs tree constants, cache extents, and rbtree utility helpers.
- Provides the structural vocabulary for original-mode checker implementation files outside this group.

## Risks And Invariants

- The original mode depends on these records being merged and cross-referenced correctly; stale `found_*` or error bits can cause false repairs or missed corruption.
- Flexible trailing name buffers require exact allocation sizes.
- Extent and inode accounting fields distinguish on-disk refs from discovered refs; conflating them would hide metadata inconsistencies.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/check/mode-original.h -->