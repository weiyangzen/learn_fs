# sources/distributed-fs/ceph-client/lib/btree.c

## Purpose

`sources/distributed-fs/ceph-client/lib/btree.c` implements a simple in-memory B+tree keyed by 32-bit, 64-bit, or 128-bit integer keys and storing non-NULL pointers. It is a sparse-address-space container similar in role to radix trees but optimized around cacheline-sized nodes.

## Important APIs, Types, and Functions

Important exported geometry objects are `btree_geo32`, `btree_geo64`, and `btree_geo128`. Exported lifecycle and storage functions include `btree_alloc`, `btree_free`, `btree_init_mempool`, `btree_init`, and `btree_destroy`. Core operations are `btree_last`, `btree_lookup`, `btree_update`, `btree_get_prev`, `btree_insert`, `btree_remove`, `btree_merge`, `btree_visitor`, and `btree_grim_visitor`; adapter callbacks include `visitorl`, `visitor32`, `visitor64`, and `visitor128`. Internal helpers manage key arrays, value slots, node growth/shrink, split, merge, rebalance, and traversal.

## Control Flow

Initialization creates or accepts a mempool backed by a `btree_node` slab cache. Lookup descends from `head->node` by scanning a node's sorted key slots until `keycmp() <= 0`, then follows child pointers until the leaf and scans for equality. Insert grows the tree if needed, finds a leaf, rejects duplicate keys through `BUG_ON`, splits full nodes recursively by inserting a new child in the parent, then shifts slots to insert the new pair. Remove finds the level, shifts remaining pairs left, clears the tail slot, and rebalances by merging neighboring nodes when combined fill fits. Merge repeatedly moves the victim's last entry to the target. Visitors recurse in key order and optionally reap nodes.

## State and Persistence Behavior

State is held in caller-owned `struct btree_head`, its mempool, and slab-allocated fixed-size nodes. Nodes store all used pairs on the left and zero-valued unused slots on the right; values cannot be NULL because zero marks empty. There is no locking in this file, so callers own synchronization and lifetime. `btree_grim_visitor()` frees all visited nodes and resets the head.

## Dependencies and Integration Points

The file uses `<linux/btree.h>` ABI types, slab and mempool allocation, module init/exit, cacheline sizing, and `BUG_ON`. It exports GPL symbols for kernel users needing sparse pointer maps, including code that can provide an external mempool for allocation constraints.

## Risks and Edge Cases

The unusual descending key layout and rightmost-lowest convention make parent key updates delicate. Duplicate insertion and NULL values are fatal `BUG_ON` cases. `btree_destroy()` frees only `head->node` plus the mempool, so callers should empty or grim-visit non-empty trees before teardown if nodes remain below the root. No internal locking means concurrent update or traversal is unsafe without external protection.

## Test Signals

Coverage should insert, lookup, update, remove, and iterate 32/64/128-bit keys across split and merge boundaries. Edge tests should cover empty trees, predecessor lookup around zero and gaps, duplicate insert assertions, merge of empty/non-empty trees, grim visitor freeing, and allocation failure during split. Slab init/exit and module link tests confirm lifecycle wiring.

## Read Coverage

Source read size: 795 lines, 19547 bytes.
