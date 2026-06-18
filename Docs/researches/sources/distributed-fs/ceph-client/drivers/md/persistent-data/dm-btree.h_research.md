<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree.h

## Purpose
Declares the public persistent btree API for device-mapper metadata. It provides immutable B+ trees with 64-bit keys, arbitrary fixed-size little-endian values, nested tree support, and ordered cursors.

## Important APIs, Types, And Functions
`struct dm_btree_value_type` defines value size and optional callbacks: `inc` for duplicated values, `dec` for deleted values, and `equal` for overwrite comparisons. `struct dm_btree_info` binds a transaction manager, number of nested levels, and value type.

Lifecycle and mutation APIs are `dm_btree_empty()`, `dm_btree_del()`, `dm_btree_insert()`, `dm_btree_insert_notify()`, `dm_btree_remove()`, and `dm_btree_remove_leaves()`. Lookup and traversal APIs are `dm_btree_lookup()`, `dm_btree_lookup_next()`, `dm_btree_find_lowest_key()`, `dm_btree_find_highest_key()`, and `dm_btree_walk()`. The cursor API uses `struct dm_btree_cursor` and supports begin, end, next, skip, and current-value access.

Sparse annotations such as `__dm_written_to_disk()` document that callers pass on-disk-format data to insert/update APIs.

## Control Flow
Callers initialize `dm_btree_info`, create or load a root, and perform lookups/mutations through the transaction manager. Mutations return new roots. Multi-level btrees use one key per level, where non-leaf values point to subtrees and the final value comes from the caller's value type.

## State And Persistence
The btree is persistent and immutable across transactions. Old roots can coexist with updated roots when their reference counts are preserved. Value callbacks are required for correct persistence of referenced blocks and external resource counts.

## Dependencies And Integration Points
The API depends on `dm-block-manager.h` and an external transaction manager. It is the core index type for the persistent-data library and is consumed by arrays, bitsets, and space maps.

## Risks
The public contract places reference-count responsibility on value callbacks and caller behavior. Passing CPU-endian values where little-endian disk values are expected corrupts persisted metadata. `dm_btree_walk()` is limited to single-level trees and is recursive. `remove_leaves()` only removes a contiguous bottom-level range and does not imply full subtree deletion.

## Test Signals
API tests should validate value callbacks, nested key arrays, old/new root immutability, lookup missing-key `-ENODATA`, cursor depth limits, and removal/range-removal semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree.h -->
