# sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag.c

## Purpose
`rcbag.c` implements an in-memory refcount bag: a multiset of reverse mapping extents keyed by start block and length, backed by the in-memory rcbag btree. It is used by scrub/repair algorithms that need to synthesize refcount edges from rmap streams.

## Important APIs, Types, And Functions
`struct rcbag` owns the mount, an `xfbtree`, and `nr_items`. Public functions are `rcbag_init`, `rcbag_free`, `rcbag_add`, `rcbag_count`, `rcbag_next_edge`, `rcbag_remove_ending_at`, and `rcbag_dump`.

## Control Flow
Initialization allocates the bag and initializes an in-memory btree. `rcbag_add` opens a btree cursor, looks for a record matching an rmap, increments its refcount if present, or inserts a new record otherwise, then commits the xfbtree transaction and increments the item count. `rcbag_next_edge` scans the bag and the next rmap candidate to find the next block at which the refcount changes. `rcbag_remove_ending_at` walks from the right edge, deletes records ending at the target block, and decrements `nr_items` by their stored refcount.

## State And Persistence Behavior
All state is in memory and associated with repair/scrub temporary buftarg storage. The btree uses transaction-like commit/cancel semantics but does not persist filesystem metadata.

## Dependencies And Integration Points
It depends on `rcbag_btree.c` cursor operations, `xfbtree`, xfs btree APIs, rmap records, and trace/debug infrastructure. It is a helper for higher-level refcount/rmap repair code.

## Risks And Edge Cases
Corruption-style returns happen if btree lookup says a record exists but cannot retrieve it, insertion does not insert, or no next edge can be found. The `nr_items` field counts multiplicities for additions and removals, not merely btree record count, so callers must interpret it carefully.

## Test Signals
Tests should add duplicate rmaps, add overlapping but differently sized rmaps, compute next edges with and without a pending next rmap, remove records ending at a boundary, and exercise xfbtree transaction cancel paths.
