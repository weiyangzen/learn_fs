<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom_interval_tree.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom_interval_tree.c

## Purpose

Implements the mutable interval-set operations used by usNIC UIOM memory tracking. It wraps Linux `INTERVAL_TREE_DEFINE` with higher-level insert, remove, and relative-complement operations that split overlapping intervals, maintain a per-interval `ref_cnt`, and combine flag bits for overlapping registrations.

## Important APIs, Types, And Functions

The file operates on `struct usnic_uiom_interval_node` from the paired header. Important helpers are `usnic_uiom_interval_node_alloc()`, `find_intervals_intersection_sorted()`, `usnic_uiom_get_intervals_diff()`, `usnic_uiom_insert_interval()`, `usnic_uiom_remove_interval()`, and `usnic_uiom_put_interval_set()`. `INTERVAL_TREE_DEFINE(...)` emits the standard insert, remove, subtree-search, first, and next routines declared in the header.

`MAKE_NODE`, `MAKE_NODE_AND_APPEND`, and `MARK_FOR_ADD` centralize allocation and staging of intervals. `FLAGS_EQUAL(flags1, flags2, mask)` lets diff calculation treat matching masked flags as already covered.

## Control Flow

`find_intervals_intersection_sorted()` walks the rb interval tree over a query range, temporarily links matching nodes onto a list, and sorts by start address. `usnic_uiom_get_intervals_diff()` then scans that sorted intersection with a `pivot` and emits new nodes for holes not covered by same-masked flags in the tree.

`usnic_uiom_insert_interval()` first gathers all intersecting intervals. For each overlap, it stages left remnants, newly inserted gaps, overlapped segments with incremented `ref_cnt` and ORed flags, and right remnants. After staging succeeds, it removes and frees the old intersecting nodes and inserts the replacement segments into the rb tree.

`usnic_uiom_remove_interval()` iterates overlapping nodes, decrements `ref_cnt`, adds nodes that reach zero to the caller-supplied `removed` list, then removes those nodes from the rb tree. The caller owns freeing the removed nodes.

## State And Persistence Behavior

State is entirely in caller-owned `struct rb_root_cached` trees and temporary `list_head` collections. Insert mutates the tree by replacing overlapping nodes; remove only removes intervals whose reference count reaches zero. Diff output is allocated as independent nodes and must be freed through `usnic_uiom_put_interval_set()`. Allocations use atomic GFP in this file, implying callers may be in non-sleepable paths.

## Dependencies And Integration Points

Depends on Linux list sorting, slab allocation, rb interval tree generation, and the usNIC interval-node layout. It integrates with UIOM registration code that needs to know which user address ranges are new versus already pinned or tracked.

## Risks And Edge Cases

The implementation temporarily reuses each node's `link` field while it remains in the rb tree, so callers must not expect those list links to carry other concurrent state. Insert error handling frees only staged nodes; the original tree is untouched until all replacements are allocated. Removal only decrements whole intersecting nodes and does not split partially removed ranges, so callers must call it with ranges aligned to prior interval segmentation or rely on the insert-side splitting invariant. Address arithmetic around `last + 1` and `interval->start - 1` must avoid overflow/underflow at boundary values.

## Test Signals

Useful tests insert overlapping ranges with different flags, verify resulting non-overlapping segments and reference counts, compute diffs with selective flag masks, remove ranges until counts reach zero, and inject allocation failures before tree mutation. Concurrency tests should be at the caller layer because this file has no internal tree lock.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom_interval_tree.c -->
