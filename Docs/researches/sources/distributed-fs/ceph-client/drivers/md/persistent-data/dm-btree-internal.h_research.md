<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-internal.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-internal.h

## Purpose
Declares internal btree structures and helpers shared by insertion, deletion, removal, and spine implementations. It captures the on-disk node layout and the rolling-lock abstractions used by the persistent btree implementation.

## Important APIs, Types, And Functions
`enum node_flags` distinguishes `INTERNAL_NODE` and `LEAF_NODE`. `struct node_header` stores checksum, flags, expected block number, entry count, max entries, and value size. `struct btree_node` starts with that header followed by sorted little-endian 64-bit keys and a separate value area.

Accessors `key_ptr()`, `value_base()`, `value_ptr()`, and `value64()` compute key/value locations inside a node. Shared helpers include `bn_read_lock()`, `new_block()`, `unlock_block()`, `inc_children()`, `lower_bound()`, `init_le64_type()`, and `btree_get_overwrite_leaf()`.

`struct ro_spine` and `struct shadow_spine` hold at most two rolling locks while descending a btree. Read-only spine APIs handle lookup traversal; shadow spine APIs perform copy-on-write traversal and track the new root.

## Control Flow
Btree readers descend with `ro_step()` and release old ancestors as they move down. Mutators descend with `shadow_step()`, which shadows blocks through the transaction manager and lets the caller update parent pointers to new shadow locations. Removal and insertion code use the same node layout and accessor helpers to split, rebalance, merge, and overwrite nodes.

## State And Persistence
The node layout is persistent and little-endian. Checksums and block-number stamping are validated by `btree_node_validator` in the spine implementation. Internal values of multi-level btrees are `__le64` block references whose reference counts are managed by the `le64` value type.

## Dependencies And Integration Points
This header depends on `dm-btree.h` and the transaction manager abstractions. It is private to the persistent-data btree implementation and should not be used by external dm targets.

## Risks
The risks are layout and arithmetic sensitive: `value_base()` assumes `max_entries` and `value_size` were validated, and all callers must preserve sorted keys and correct parent boundary keys. Misusing ro versus shadow spine APIs can break lock ordering or mutate shared nodes without copy-on-write.

## Test Signals
Structural tests should validate node checksum/block-number errors, lower-bound behavior, sorted-key invariants after insert/remove, shadow-root updates, and correct child reference increments when shared nodes are shadowed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-internal.h -->
