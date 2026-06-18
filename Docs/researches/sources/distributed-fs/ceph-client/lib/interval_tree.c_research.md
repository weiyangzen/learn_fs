# sources/distributed-fs/ceph-client/lib/interval_tree.c

## Purpose
`interval_tree.c` instantiates the generic augmented red-black interval tree for `struct interval_tree_node` and optionally implements span iteration over used and hole ranges. It provides efficient intersection queries over unsigned long `[start, last]` intervals.

## Important APIs, Types, and Functions
The `INTERVAL_TREE_DEFINE()` macro generates `interval_tree_insert()`, `interval_tree_remove()`, `interval_tree_subtree_search()`, `interval_tree_iter_first()`, and `interval_tree_iter_next()`, all exported GPL. Under `CONFIG_INTERVAL_TREE_SPAN_ITER`, the file exports `interval_tree_span_iter_first()`, `interval_tree_span_iter_next()`, and `interval_tree_span_iter_advance()`. Span iteration uses `struct interval_tree_span_iter` with `nodes[0]` for the current merged used span and `nodes[1]` for the next used span.

## Control Flow, State, and Persistence
The generated interval tree maintains each node's `__subtree_last` augmentation so searches can skip subtrees that cannot intersect a query. Span iteration starts from the first intersecting node and alternates between hole and used states within `[first_index, last_index]`. `interval_tree_span_iter_next_gap()` merges contiguous or overlapping used intervals by advancing until a gap appears. `interval_tree_span_iter_advance()` updates an existing iterator to a new index when possible, otherwise reinitializes from the tree.

## Dependencies and Integration Points
It depends on `<linux/interval_tree.h>` and `<linux/interval_tree_generic.h>`, red-black tree cached roots, and compiler/export helpers. Consumers include memory managers and range-tracking subsystems that need interval intersection or used/hole span walks.

## Risks and Test Signals
Risks include off-by-one errors around inclusive `last`, overflow at `last + 1` or `nodes[0]->last + 1`, incorrect merging of adjacent spans, stale iterators after tree mutation, and configuration skew when span iteration is disabled. Tests should cover overlapping, adjacent, disjoint, leading-hole, trailing-hole, whole-hole, whole-used, single-point, and near-`ULONG_MAX` ranges, plus advancing within and across current spans.
