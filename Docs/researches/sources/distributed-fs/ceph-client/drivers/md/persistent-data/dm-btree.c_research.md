<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree.c

## Purpose
Implements creation, deletion, lookup, insertion, walking, key discovery, and cursor iteration for immutable persistent B+ trees with 64-bit keys and fixed-size values. It supports nested btrees where each level indexes the next root.

## Important APIs, Types, And Functions
Exported APIs include `dm_btree_empty()`, `dm_btree_del()`, `dm_btree_lookup()`, `dm_btree_lookup_next()`, `dm_btree_insert()`, `dm_btree_insert_notify()`, `dm_btree_find_lowest_key()`, `dm_btree_find_highest_key()`, `dm_btree_walk()`, and cursor functions. Internal array/node helpers include `array_insert()`, `lower_bound()`, `upper_bound()`, `insert_at()`, `calc_max_entries()`, `copy_entries()`, `move_entries()`, `redistribute2()`, `redistribute3()`, `split_one_into_two()`, `split_two_into_three()`, `btree_split_beneath()`, `rebalance_left()`, `rebalance_right()`, and `rebalance_or_split()`.

The deletion of whole trees uses an explicit heap-allocated `del_stack` to avoid recursive kernel stack growth. `btree_insert_raw()` performs copy-on-write descent and preemptive space creation. `btree_get_overwrite_leaf()` exposes a shadowed leaf for overwrite-only users such as space-map overflow counts.

## Control Flow
`dm_btree_empty()` allocates a leaf node with capacity based on block size and value size. Lookup descends through read-only spines, requiring exact key matches at each nested level. `lookup_next` resolves upper levels exactly and then finds the next leaf key at the bottom level.

Insertion descends one level at a time. For missing intermediate keys it creates a new empty subtree and inserts its root. Along the descent, full nodes are split or rebalanced before insertion. When overwriting an existing leaf value, the old value's `dec` callback is called unless an `equal` callback says old and new values are equivalent; new insertions assume the caller already owns the value reference. Whole-tree deletion walks all nodes, skips children of shared nodes by decrementing the shared node reference, and decrements leaf values for unshared leaves.

Cursor iteration pushes btree nodes to the leftmost leaf, optionally prefetches leaf values that are block numbers, and advances/backtracks in sorted order.

## State And Persistence
Btree state is persisted in checksummed nodes managed by the transaction manager. Mutations return a new root and never modify shared blocks in place. Value-type callbacks are the bridge between btree structure changes and external reference-counted objects. Internal-node values are child block pointers with `le64` callbacks that maintain child refs.

## Dependencies And Integration Points
This file depends on btree internal/spine helpers, transaction manager refcount and shadowing, block-manager block size, and dm logging. It underpins arrays, bitsets, space-map bitmap indexes, and overflow refcount trees.

## Risks
Btree correctness is highly sensitive to separator-key updates, split/rebalance decisions, and value callback usage. Monotonic insertion paths use different split heuristics than middle insertions. `dm_btree_walk()` is recursive and restricted to single-level trees, so stack use matters. Cursor depth is capped by `DM_BTREE_CURSOR_MAX_DEPTH`; malformed or unexpectedly deep trees can fail traversal.

## Test Signals
Tests should cover empty trees, exact and next lookup, overwrite versus insert-notify, nested btrees, monotonically increasing/decreasing insert streams, random insert/remove churn, tree deletion with shared roots, cursor skip/next behavior, value callback counts, and corruption tests that trip validators before logic sees bad nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree.c -->
