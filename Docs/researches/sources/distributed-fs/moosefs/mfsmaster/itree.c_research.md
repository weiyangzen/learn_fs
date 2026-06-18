# sources/distributed-fs/moosefs/mfsmaster/itree.c

## Purpose
`itree.c` implements a compact interval tree for mapping unsigned 32-bit ranges to nonzero ids. In the MooseFS master it is used by `topology.c` to map IP address ranges to rack/location ids.

The implementation is a binary-search tree over non-overlapping intervals. Adding an interval with an id overwrites any overlapping existing intervals; adding with id `0` deletes the interval. Lookup returns the id associated with a point or `0` when no interval covers it.

## Important APIs, Types, And Functions
The internal `itnode` stores inclusive `from` and `to` bounds, an `id`, and left/right child pointers. Public API uses `void *` root handles so consumers do not see `itnode`.

`itree_add_interval` normalizes reversed endpoints, then either calls `itree_add` for nonzero ids or `itree_delete` for id `0`. It returns the possibly changed root pointer.

`itree_find` walks the tree comparing the point to interval bounds and returns the matched id or `0`. `itree_freeall` recursively frees the whole tree. `itree_rebalance` converts the tree to a sorted linked list, merges adjacent intervals with the same id, and rebuilds a more balanced tree.

Internal `itree_add` handles overwriting overlaps by splitting existing intervals around the new range or deleting covered child ranges. `itree_delete` removes an interval by shrinking, splitting, or removing nodes. `itree_remove` removes a single node and chooses either predecessor or successor based on local branch-chain lengths, using endpoint parity as a tie breaker. `itree_tolist`, `itree_simplify`, and `itree_totree` implement the simple rebalance pass.

## Control Flow
The tree invariant is that left intervals are strictly below the current interval and right intervals are strictly above it. `itree_add` and `itree_delete` preserve non-overlap by recursively deleting or moving covered ranges before replacing the current node's bounds/id.

When a new interval lies inside an existing node, the existing node can split into up to three regions: preserved left remainder, new middle interval, and preserved right remainder. The code chooses which side to allocate first depending on overlap shape and parity to keep behavior deterministic.

Rebalance is intentionally simple and documented as square-time. It flattens the tree in sorted order by reusing the `left` pointer as a next-list pointer, merges adjacent same-id intervals, and recursively selects midpoint-ish list elements to rebuild.

## State And Persistence Behavior
The module owns only heap-allocated tree nodes under a caller-held root pointer. It has no global state, no persistence, and no serialization. Callers are responsible for keeping the root returned by `itree_add_interval` and `itree_rebalance`, and for calling `itree_freeall`.

The special id `0` means absence/delete and is also the lookup miss value. Valid mappings must therefore use nonzero ids.

## Dependencies And Integration Points
The module includes `massert.h` for `passert` allocation checks and its own `itree.h`. Reference searches show `topology.c` uses `itree_add_interval` while loading topology ranges, `itree_find` to compare or classify IP addresses, `itree_rebalance` after reload, and `itree_freeall` during cleanup or reload failure.

The 32-bit bounds align naturally with IPv4 addresses. There is no IPv6 support in this data structure as written.

## Risks
Worst-case unbalanced trees can degrade add/delete/find performance, and the rebalance routine is documented as square-time. Very large topology files or adversarial insertion orders could be expensive.

The code uses recursive add/delete/free/rebuild operations. Deeply skewed trees can risk stack growth before rebalance runs.

The `void *` API hides type details but also removes compile-time type safety. Callers must not mix this root pointer with unrelated data.

Endpoint arithmetic around `n->from - 1`, `n->to + 1`, `t + 1`, and `f - 1` relies on branch conditions preventing underflow/overflow in normal cases. Boundary ranges at `0` or `UINT32_MAX` deserve tests because they are natural IP range endpoints.

## Test Signals
Useful unit tests include adding non-overlapping intervals, overwriting partial overlaps, overwriting complete coverage, deleting middle segments, deleting ranges that span multiple nodes, reversed endpoint normalization, lookup misses returning zero, adjacent same-id merge after rebalance, and boundary ranges at `0.0.0.0` and `255.255.255.255`.

Topology integration tests should load a representative topology map, rebalance it, and verify rack lookup and same-rack comparisons for IPs at range starts, middles, ends, and outside all ranges.
