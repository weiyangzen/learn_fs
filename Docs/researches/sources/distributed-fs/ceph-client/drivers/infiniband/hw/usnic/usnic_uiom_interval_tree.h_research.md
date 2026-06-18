<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom_interval_tree.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom_interval_tree.h

## Purpose

Declares the usNIC UIOM interval tree node and public interval-set operations. It is the contract for tracking pinned or registered user memory ranges by inclusive start/end address, reference count, and flags.

## Important APIs, Types, And Functions

`struct usnic_uiom_interval_node` embeds an rb node, a list link, inclusive `start`/`last` addresses, `__subtree_last` for interval-tree augmentation, `ref_cnt`, and `flags`. The header exposes generated interval-tree primitives plus `usnic_uiom_insert_interval()`, `usnic_uiom_remove_interval()`, `usnic_uiom_get_intervals_diff()`, and `usnic_uiom_put_interval_set()`.

## Control Flow

Consumers initialize an `rb_root_cached`, insert ranges as they are acquired, ask for diffs before new acquisition, and remove ranges when references are released. Removed and diff nodes are passed through lists so callers can batch follow-up unpin/free work.

## State And Persistence Behavior

The rb tree persists in the caller. Node ownership is explicit: tree nodes are owned by the tree until removed; diff-set nodes are caller-owned and released by `usnic_uiom_put_interval_set()`; remove returns zero-ref nodes for caller cleanup.

## Dependencies And Integration Points

Depends on Linux `rbtree.h` and the interval-tree generated functions from the implementation file. It is expected to be used by usNIC UIOM memory registration code and any code that must compare requested user ranges against existing tracked ranges.

## Risks And Edge Cases

The list link is dual-purpose and should only be used by these helpers while a node is in operation-specific lists. The API uses inclusive `last`, so off-by-one handling is important. No locking is declared; callers must serialize access to the tree and returned lists.

## Test Signals

Compile coverage should confirm generated function declarations match `INTERVAL_TREE_DEFINE`. Behavioral tests should verify insertion, removal, and diff ownership semantics and that callers free all returned lists.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom_interval_tree.h -->
