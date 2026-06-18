# Research Group subset-b-005621

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/relocation.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/relocation.c

## Purpose
`relocation.c` implements Btrfs block-group relocation, the mechanism used by balance, device shrink, profile conversion, and compaction to move every extent out of a target block group so the group can be freed or repurposed. It supports two relocation strategies. The classic strategy creates relocation roots, copies or COWs referenced metadata/data to new locations, updates all tree and file-extent pointers, merges relocation roots back into their source roots, and cleans temporary relocation state. When the `REMAP_TREE` incompat feature is available and the block group is eligible, the remap-tree strategy records logical address remaps instead of walking and rewriting every reference immediately.

## Important APIs, Types, and Functions
The central private state is `struct reloc_control`, which tracks the target `block_group`, `extent_root`, temporary data relocation inode, metadata block reservation, backref cache, data extent cluster, processed tree-block bitmap, relocation-root mapping tree, relocation-root and dirty-root lists, merge reservation accounting, search cursor, current `enum reloc_stage`, and flags controlling relocation-root creation and merging.

Classic relocation is built around `build_backref_tree`, `relocate_tree_block`, `do_relocation`, `relocate_tree_blocks`, `relocate_data_extent`, `relocate_file_extent_cluster`, `replace_file_extents`, `prepare_to_merge`, `merge_reloc_roots`, and `merge_reloc_root`. Relocation roots are managed by `create_reloc_root`, `btrfs_init_reloc_root`, `btrfs_update_reloc_root`, `__add_reloc_root`, `__update_reloc_root`, and `__del_reloc_root`. `find_reloc_root`, `btrfs_should_ignore_reloc_root`, `btrfs_reloc_cow_block`, `btrfs_reloc_pre_snapshot`, and `btrfs_reloc_post_snapshot` are integration hooks used by the COW, transaction, snapshot, and backref paths.

The public entry points are `btrfs_relocate_block_group`, `btrfs_recover_relocation`, `btrfs_reloc_clone_csums`, `btrfs_reloc_cow_block`, `btrfs_should_cancel_balance`, `btrfs_get_reloc_bg_bytenr`, `btrfs_translate_remap`, `btrfs_remove_extent_from_remap_tree`, and `btrfs_last_identity_remap_gone`.

The remap-tree implementation centers on `start_block_group_remapping`, `create_remap_tree_entries`, `do_remap_reloc`, `do_remap_reloc_trans`, `add_remap_entry`, `move_existing_remaps`, `move_existing_remap`, `copy_remapped_data`, `btrfs_translate_remap`, and `btrfs_remove_extent_from_remap_tree`. It persists `BTRFS_IDENTITY_REMAP_KEY`, `BTRFS_REMAP_KEY`, and `BTRFS_REMAP_BACKREF_KEY` items in `fs_info->remap_root` and maintains per-block-group `remap_bytes` and `identity_remap_count`.

## Control Flow
`btrfs_relocate_block_group` resolves the block group and extent root, waits for unfinished subvolume drops, rejects swapfile-pinned groups, allocates `reloc_control`, marks relocation running, makes the block group read-only, deletes v1 free-space cache data that could pin extents, waits for reservations/NOCOW writers/ordered roots, finishes zoned block groups, then selects either remap-tree relocation or classic relocation.

In classic relocation, `do_nonremap_reloc` repeatedly calls `relocate_block_group`. The first pass runs in `MOVE_DATA_EXTENTS`, scans extent items with `find_next_extent`, relocates metadata blocks by building backref trees and COWing/relinking paths, and gathers adjacent data extents into `file_extent_cluster`. Data clusters are preallocated in a special orphan inode in the data relocation tree, mapped to the original disk bytes, dirtied through folios, and written back to allocate replacement extents of matching sizes. After ordered extents finish, the stage switches to `UPDATE_DATA_PTRS`; the second pass finds data backrefs, relocates leaves that reference old data, and `replace_file_extents` rewrites file extent items from old bytenrs to the relocation inode's new bytenrs while adding/dropping delayed refs.

Metadata relocation uses backref walks from each target tree block upward to roots. For shareable roots, `btrfs_record_root_in_trans` creates or updates relocation roots and `select_reloc_root` records the path expected by `btrfs_reloc_cow_block`. For non-shareable or COW-only trees, the code COWs down the tree directly. Pending relocated nodes are linked to upper blocks before the transaction completes. Processed blocks are tracked in `processed_blocks` to avoid duplicate work.

After scanning, `prepare_to_merge` reserves metadata, marks relocation roots as merge candidates by setting refs or orphaning them on error, commits a transaction, and `merge_reloc_roots` swaps relocated subtrees from relocation roots into the original filesystem roots. `merge_reloc_root` walks the relocation tree by generation, calls `replace_path` to exchange block pointers and delayed refs, records progress in `drop_progress`, invalidates extent caches for rewritten data pointers, and finally queues merged roots for cleanup. `clean_dirty_subvols` drops merged or orphan relocation roots.

In remap-tree relocation, `move_existing_remaps` first moves any remap entries that currently point into the target group. `start_block_group_remapping` caches free space, creates identity remap entries for all allocated regions not represented as free space, marks the block group and chunk as remapped, removes free-space records/cache for the source group, and commits. `do_remap_reloc` repeatedly reserves new logical ranges, copies bytes from the identity-mapped old range to the new range using direct remap bios, removes the destination from the free-space tree, replaces the identity entry with remap/backref entries, updates block-group accounting, and marks the source fully remapped when no identity entries remain.

Crash recovery starts in `btrfs_recover_relocation`. It scans the root tree for `BTRFS_TREE_RELOC_OBJECTID` roots, marks dangling ones as garbage, reconstructs `reloc_control`, reconnects live reloc roots to their source fs roots, commits, resumes `merge_reloc_roots`, cleans dirty roots, and finally cleans orphan inodes from the data relocation tree for non-remap filesystems.

## State and Persistence
Classic relocation persists temporary relocation roots in the root tree as `BTRFS_TREE_RELOC_OBJECTID` root items. Their `root_refs`, `drop_progress`, and `drop_level` fields encode whether merge should resume or cleanup should drop them after a crash. The source root's in-memory `reloc_root` pointer and `BTRFS_ROOT_DEAD_RELOC_TREE` state coordinate normal merge and avoid stale access. The data relocation inode is an orphan inode under `data_reloc_root`; its extents are temporary but must survive transactions until file extent pointers are updated.

Remap-tree relocation persists mapping state in `remap_root`, modifies chunk item flags (`BTRFS_BLOCK_GROUP_REMAPPED`), and updates block-group runtime and on-disk accounting for `remap_bytes`, `identity_remap_count`, and fully-remapped state. `btrfs_translate_remap` is the read/write integration point that maps old logical addresses to the current physical logical address span and clamps requests to remap item boundaries.

In-memory state includes the current `fs_info->reloc_ctl`, `BTRFS_FS_RELOC_RUNNING`, cancellation atomics, backref cache nodes, processed extent bits, and relocation-root mapping rb-tree. The code uses transaction commits as durability boundaries between creation, scanning, merging, and cleanup.

## Dependencies and Integration Points
This file depends on the Btrfs extent tree, root tree, transaction layer, delayed refs, qgroups/simple quotas, backref walking, block-group/cache management, free-space tree/cache, ordered extents, folios/page cache, zoned support, chunk/device mapping, RAID stripe tree behavior, and checksum trees. It integrates with COW through `btrfs_reloc_cow_block`, snapshots through pre/post snapshot hooks, reads through `btrfs_translate_remap`, extent deletion through `btrfs_remove_extent_from_remap_tree`, balance cancellation through `btrfs_should_cancel_balance`, and mount recovery through `btrfs_recover_relocation`.

## Risks and Edge Cases
The classic path has a large transactional state machine. ENOSPC handling is delicate because metadata reservations are estimated from backref trees, expanded on `-EAGAIN`, and later reused while merging. Backref corruption or incomplete paths are treated as `-EUCLEAN` because wrong roots or duplicate root references can cause unsafe block swapping. `replace_file_extents` deliberately skips live inodes whose extent ranges cannot be try-locked, so repeated passes must eventually revisit them. Cache invalidation must serialize with readpage and reflink through extent locks and `i_mmap_lock`. Subpage and large-folio relocation avoid padding corruption by invalidating the relocation inode cache before preallocation.

Relocation-root lifecycle is sensitive to reference ownership: list membership, `root->reloc_root`, and rb-tree mappings each imply different refs. Memory barriers around `BTRFS_ROOT_DEAD_RELOC_TREE` protect readers that test the bit before dereferencing `root->reloc_root`. Recovery relies on root item fields not being partially updated without transaction abort.

The remap-tree path introduces new accounting risks: identity/remap entries must stay non-overlapping and synchronized with free-space tree updates, destination reservations, `bytes_readonly`, `remap_bytes`, chunk flags, and backrefs. Copying remapped data through bios must use `is_remap` and handle partial allocations. Removing a range from the remap tree must split both identity and non-identity items and maintain reverse backrefs. `btrfs_translate_remap` intentionally returns `-ENOENT` when no mapping covers a logical address, so callers must distinguish no-remap from corruption.

## Test Signals
Useful tests include balance/device-shrink/profile conversion on metadata-only, data-only, mixed, system, and zoned block groups; cancellation before and during relocation; ENOSPC during scan, data writeback, and merge; crash/recovery after reloc-root creation, after `prepare_to_merge`, and during `merge_reloc_root`; snapshot creation while relocation roots are being merged; subpage/large-folio data relocation; simple quota owner attribution for relocated data; qgroup swapped-block accounting; v1 free-space cache deletion; swapfile-pinned block group rejection; remap-tree relocation with preexisting remaps, partial destination allocation, range deletion, translation boundary clamping, and last identity-remap removal; and fsck/mount checks for orphan reloc roots and remap-root consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/relocation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/relocation.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/relocation.h

## Purpose
`relocation.h` declares the public Btrfs relocation interface used outside `relocation.c`. It exposes block-group relocation, relocation-root lookup/update hooks, recovery, data checksum cloning, COW integration, snapshot integration, remap-tree translation/removal, and the eligibility helper for remap-tree relocation.

## Important APIs, Types, and Functions
The inline helper `should_relocate_using_remap_tree` returns true only when the filesystem has the `REMAP_TREE` incompat feature and the target block group is neither system space nor metadata-remap space. Its callers use it to choose the remap-tree path instead of classic relocation.

Primary declarations include `btrfs_relocate_block_group`, `btrfs_recover_relocation`, `btrfs_init_reloc_root`, `btrfs_update_reloc_root`, `find_reloc_root`, `btrfs_should_ignore_reloc_root`, `btrfs_reloc_cow_block`, `btrfs_reloc_clone_csums`, `btrfs_reloc_pre_snapshot`, `btrfs_reloc_post_snapshot`, `btrfs_should_cancel_balance`, `btrfs_get_reloc_bg_bytenr`, `btrfs_translate_remap`, `btrfs_remove_extent_from_remap_tree`, and `btrfs_last_identity_remap_gone`.

The header forward-declares common Btrfs structures used by pointer prototypes, while the inline helper requires the including translation unit to already know `struct btrfs_block_group` fields and relocation feature constants.

## Control Flow
Callers enter relocation through `btrfs_relocate_block_group`. Transaction/COW code calls `btrfs_init_reloc_root` when a shareable root is recorded in a transaction during relocation and `btrfs_update_reloc_root` when committing root item updates. COW of tree blocks calls `btrfs_reloc_cow_block` so relocation can connect newly COWed blocks into its backref cache and optionally rewrite data pointers in leaves. Snapshot creation calls the pre/post hooks to reserve merge metadata and create relocation roots for newly created snapshots. Mount or recovery paths call `btrfs_recover_relocation` to resume interrupted merges. Remap-tree users call `btrfs_translate_remap` to resolve logical ranges and `btrfs_remove_extent_from_remap_tree` when extents are removed from remapped block groups.

## State and Persistence
The header itself stores no state. Its API controls persistent relocation state in the root tree, remap tree, chunk tree, block-group items, orphan relocation inodes, and transaction metadata. The exported functions also coordinate in-memory state under `fs_info->reloc_ctl`, root `reloc_root` pointers, relocation cancellation atomics, and block-group remap flags.

## Dependencies and Integration Points
`relocation.h` is included by core Btrfs modules that need relocation hooks: transaction/root code, COW/block code, snapshot creation, checksum/ordered extent handling, balance/device management, and remap-tree read or extent-removal paths. It depends on Linux integer types and Btrfs declarations/macros available from surrounding headers.

## Risks and Edge Cases
Because `should_relocate_using_remap_tree` dereferences `bg`, include ordering matters for any file using the inline. The remap-tree eligibility check must remain aligned with the implementation; allowing system or metadata-remap block groups into remap relocation would bypass assumptions in chunk and metadata handling. The prototypes expose functions that are valid only under specific locks or transaction contexts, especially `btrfs_get_reloc_bg_bytenr` requiring `reloc_mutex`, root update hooks requiring a transaction, and remap removal requiring a caller-supplied writable path.

## Test Signals
Compile coverage should include every translation unit that includes this header with `REMAP_TREE` enabled and disabled. Behavioral tests should confirm remap-tree eligibility for data block groups only, classic fallback for system and metadata-remap groups, COW hook invocation during relocation, snapshot hook behavior during merge, mount recovery of reloc roots, and remap translation/removal on remapped chunks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/relocation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/root-tree.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/root-tree.c

## Purpose
`root-tree.c` implements root tree item management for Btrfs. The root tree stores `BTRFS_ROOT_ITEM_KEY` records for subvolumes, snapshots, special trees, and relocation roots, plus root forward/back references that represent subvolume directory links. This file provides lookup, insert, update, delete, orphan discovery, compatibility initialization, timestamp updates, and metadata reservation helpers for subvolume operations.

## Important APIs, Types, and Functions
`btrfs_find_root` searches the root tree for an exact root item or the highest-offset root item for an objectid when the search offset is `-1ULL`, then reads the root item with `btrfs_read_root_item`. The static reader handles old on-disk root item sizes and mismatched `generation`/`generation_v2` by zeroing newer fields and assigning a new UUID.

`btrfs_set_root_node` copies an extent buffer's bytenr, level, and generation into a root item. `btrfs_update_root` updates an existing root item, expanding old short items to the current `struct btrfs_root_item` size when needed and setting `generation_v2` before writing. `btrfs_insert_root` inserts a new root item with matching generation fields. `btrfs_del_root` removes a root item by key and treats a missing expected key as filesystem corruption.

`btrfs_find_orphan_roots` scans `BTRFS_ORPHAN_OBJECTID` items, loads referenced roots, deletes stale orphan items whose roots no longer exist, and queues roots with zero refs for dead-root cleanup. `btrfs_add_root_ref` and `btrfs_del_root_ref` maintain paired `BTRFS_ROOT_BACKREF_KEY` and `BTRFS_ROOT_REF_KEY` items containing directory id, sequence, and encrypted/name bytes. `btrfs_check_and_init_root_item` initializes root flags/limits for old subvolumes using `BTRFS_INODE_ROOT_ITEM_INIT`. `btrfs_update_root_times` updates root ctime and transaction id under `root_item_lock`. `btrfs_subvolume_reserve_metadata` reserves metadata and qgroup space for snapshot/subvolume creation and deletion.

## Control Flow
Lookup starts with `btrfs_search_slot` on the tree root. Exact lookups return a positive miss unchanged; highest-offset lookups step back one slot after a miss and validate objectid/type. Paths are released before returning.

Root updates search with write intent. If the existing item is shorter than the current root item, `btrfs_update_root` releases the path, deletes the old item, inserts a correctly sized empty item, and then writes the full structure. Any unexpected failure in the delete/insert/update path aborts the transaction because root item inconsistency is not recoverable within the active transaction.

Root ref insertion writes both backref and forward-ref items in sequence, releasing the path between the two keys. Deletion first validates and deletes the backref keyed by child root id and parent ref id, returns the stored sequence, then deletes the mirrored forward ref keyed by parent root id and child root id. A name, dirid, or length mismatch returns `-ENOENT`.

Orphan root discovery iterates orphan items by increasing offset. If `btrfs_get_fs_root` returns `-ENOENT`, it joins a transaction to delete the orphan item. Existing roots with `root_refs == 0` are marked dead and queued for cleanup; if `drop_progress` is nonzero, the filesystem and root are marked as having unfinished drops so later relocation/balance waits until deletion completes.

Metadata reservation first reserves qgroup metadata for parent inode and directory entries when quotas are enabled, then reserves calculated insert metadata in the supplied block reservation. If normal reservation fails and `use_global_rsv` is true, it can migrate from the global reservation. On success it records qgroup-reserved bytes in the reservation; on failure it frees qgroup prealloc.

## State and Persistence
Root items, root refs, root backrefs, and orphan items are persistent B-tree records in the tree root. Compatibility handling updates in-memory root items read from older on-disk formats and later `btrfs_update_root`/`btrfs_insert_root` persist matching `generation_v2`. Orphan discovery mutates persistent orphan items and queues dead roots for asynchronous snapshot/subvolume deletion. Root ctime and ctransid are persistent fields in `root_item`. `btrfs_subvolume_reserve_metadata` updates in-memory block reservation and qgroup reservation counters; the actual metadata changes are persisted by the transaction using the reservation.

## Dependencies and Integration Points
This file depends on core Btrfs B-tree search/update helpers, transaction handling, root loading, qgroup accounting, block reservations, orphan item helpers, dead-root cleanup, accessors for on-disk structures, UUID generation, and fscrypt string names for root refs. It is used by subvolume and snapshot creation/deletion, relocation-root creation and update, mount-time orphan cleanup, transaction commit/root item updates, and quota-aware metadata reservation.

## Risks and Edge Cases
Old root item compatibility is a recurring edge case: short items and mismatched generation fields must be normalized without reading uninitialized fields as valid state. `btrfs_find_root` with offset `-1ULL` must not accept an actual `-1ULL` offset item, because that key is outside the valid range. Root ref add/delete must keep the forward and backward items paired; insertion aborts the transaction on any failure after the first insert, and deletion can leave callers handling partial failure if the second mirrored item is corrupt or missing. Orphan cleanup joins transactions while scanning and must release paths before mutating the tree. `btrfs_del_root` treats an expected missing root item as `-EUCLEAN`, making corruption visible rather than silently ignoring it.

## Test Signals
Tests should cover exact and highest-offset root lookup, reading short legacy root items, generation/generation_v2 mismatch repair, updating a short root item to full size, insert/update/delete root item transaction abort paths, paired root ref insertion and deletion including name mismatch, orphan item deletion for missing roots, dead-root queuing for zero-ref roots, unfinished-drop flagging from nonzero `drop_progress`, qgroup-enabled and disabled subvolume reservation, global reservation fallback, and root timestamp updates under concurrent root item readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/root-tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/root-tree.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/root-tree.h

## Purpose
`root-tree.h` declares the root tree API for Btrfs modules that create, find, update, delete, reference, orphan-clean, and reserve metadata for roots. It is the public interface for the implementation in `root-tree.c`.

## Important APIs, Types, and Functions
The declarations expose `btrfs_find_root`, `btrfs_insert_root`, `btrfs_update_root`, `btrfs_del_root`, `btrfs_add_root_ref`, `btrfs_del_root_ref`, `btrfs_find_orphan_roots`, `btrfs_set_root_node`, `btrfs_check_and_init_root_item`, `btrfs_update_root_times`, and `btrfs_subvolume_reserve_metadata`.

The header forward-declares `fscrypt_str`, `extent_buffer`, `btrfs_key`, `btrfs_root`, `btrfs_root_item`, `btrfs_path`, `btrfs_fs_info`, `btrfs_block_rsv`, and `btrfs_trans_handle`, keeping callers decoupled from full structure definitions when only pointer types are needed.

## Control Flow
Callers use this API inside transaction-backed workflows. Root creation usually reserves metadata, fills a root item, calls `btrfs_insert_root`, and adds root refs if the root is linked into a parent. Root updates copy a live root node into the root item with `btrfs_set_root_node` and persist it with `btrfs_update_root`. Subvolume deletion or orphan cleanup removes refs with `btrfs_del_root_ref`, deletes root items with `btrfs_del_root`, and discovers incomplete deletions with `btrfs_find_orphan_roots`. Mount/open paths call `btrfs_check_and_init_root_item` to normalize legacy fields, and transaction paths call `btrfs_update_root_times` when root metadata changes.

## State and Persistence
The header has no state, but its functions operate on persistent tree-root records: root items, root refs/backrefs, orphan items, and root item time/generation fields. `btrfs_subvolume_reserve_metadata` operates on in-memory block reservations and qgroup counters that protect later persistent modifications.

## Dependencies and Integration Points
`root-tree.h` is included by relocation, transaction, disk I/O/root loading, subvolume, snapshot, orphan cleanup, and quota-related code. It depends only on Linux types plus forward declarations, allowing broad use without forcing every caller to include full root-tree implementation details.

## Risks and Edge Cases
Most functions require the caller to pass the correct tree root, transaction, and writable path context. Ref operations must be called in pairs consistent with directory entries or the root tree can retain dangling forward/back references. `btrfs_find_root` can return positive miss, zero found, or negative error; callers must not collapse positive miss into success. Metadata reservation callers must free or transfer qgroup reservation state consistently on later failure paths.

## Test Signals
Build coverage should verify all root-tree consumers compile through forward declarations. Behavioral tests should exercise root insert/update/delete, exact and inexact root lookup, root ref/backref pairing, orphan root scan at mount, legacy root item initialization, root timestamp persistence, and qgroup/global-reservation behavior during subvolume and snapshot operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/root-tree.h -->
