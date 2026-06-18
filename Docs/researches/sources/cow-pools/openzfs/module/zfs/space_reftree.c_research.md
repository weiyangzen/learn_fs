# File Research: sources/cow-pools/openzfs/module/zfs/space_reftree.c

## Role

`space_reftree.c` implements space reference trees, a small helper abstraction for combining range trees with reference counts. A normal range tree represents membership as present or absent. A reference tree records signed reference-count deltas at segment boundaries, making unions and intersections of multiple maps easy to derive.

The main documented consumer is `vdev_dtl_reassess()`, which computes missing/outage regions for interior vdevs. For example, RAID-Z outage regions are where the reference count reaches parity plus one, while mirror outage regions are where all children are missing.

## Data Structure

The tree is an AVL tree of `space_ref_t` records ordered by `sr_offset`, with pointer comparison as a tie breaker. Tie-breaking allows multiple delta records at the same offset rather than coalescing them during insertion.

Each segment contributes two nodes: a positive reference-count delta at the start and a negative delta at the end. A running sum over the ordered tree yields the active reference count for every interval.

## API

`space_reftree_create()` initializes an AVL tree with the local comparator and `space_ref_t` layout. `space_reftree_destroy()` destroys all nodes with `avl_destroy_nodes()` and frees each `space_ref_t` before destroying the tree.

`space_reftree_add_seg()` adds one segment by inserting start and end delta nodes. `space_reftree_add_map()` walks a `zfs_range_tree_t` and adds every range segment with the supplied signed reference count.

`space_reftree_generate_map()` converts the reference tree back into a normal range tree. It vacates the output tree, walks delta nodes in order, maintains a running `refcnt`, opens an output range when `refcnt >= minref`, closes it when the count falls below `minref`, and adds non-empty intervals to the output range tree.

## Risks And Invariants

The sum of all deltas must return to zero by the end of generation, and no output interval may remain open. `space_reftree_generate_map()` asserts both conditions.

Because duplicate offsets are allowed through pointer tie-breaking, correctness depends on processing all same-offset deltas before interpreting the next nonzero-length interval. Zero-length output intervals are skipped. Consumers should treat the tree as a temporary computation structure and destroy it after generating the desired map.
