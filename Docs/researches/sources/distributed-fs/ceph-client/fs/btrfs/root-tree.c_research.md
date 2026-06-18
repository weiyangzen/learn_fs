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
