# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/double_span.h

## Purpose
This header declares a double interval-tree span iterator used to compute spans over the union of two interval trees. IOMMUFD uses it for IOVA allocation where both reserved ranges and mapped areas must be considered.

## Important APIs And Types
`struct interval_tree_double_span_iter` stores two input interval tree roots, two regular span iterators, hole/used start and end fields, and an `is_used` state: `0` for hole, `1` for a used span from the first tree, `2` for a used span from the second tree, and `-1` for done.

`interval_tree_double_span_iter_first()`, `interval_tree_double_span_iter_update()`, and `interval_tree_double_span_iter_next()` are implemented in `pages.c`.

`interval_tree_double_span_iter_done()` checks for the terminal state.

`interval_tree_for_each_double_span()` wraps initialization, done testing, and iteration in a `for` loop.

## Control Flow
Callers initialize the iterator with two interval trees and a range. Each iteration reports either a hole or a used span, preferring the first tree when both trees cover the same region. The iterator is greedy and avoids emitting consecutive spans with the same `is_used` class.

## State And Persistence
The iterator is stack/local state only. It references caller-owned interval trees and does not allocate or persist memory.

## Dependencies And Integration Points
It depends on Linux interval tree and span iterator helpers. `io_pagetable.c` uses it in `iopt_alloc_iova()` to search holes that are inside allowed ranges but outside both reserved and already mapped IOVA intervals.

## Risks
The first-tree priority is semantically important; changing it can alter IOVA allocation around reserved ranges. Iterator boundary bugs can create off-by-one allocation holes, overlap existing mappings, or skip valid ranges.

## Test Signals
Tests should cover empty trees, overlapping first/second intervals, adjacent intervals, first-tree priority, full-range coverage, holes at boundaries, and IOVA allocation with reserved plus mapped intervals.
