# sources/distributed-fs/ceph-client/include/linux/interval_tree.h

Purpose: This header declares the generic augmented red-black interval tree used to index inclusive unsigned-long ranges and query overlap efficiently.

Important APIs, types, and functions: `struct interval_tree_node` stores an `rb_node`, `start`, inclusive `last`, and augmented `__subtree_last`. Core operations are `interval_tree_insert`, `interval_tree_remove`, `interval_tree_subtree_search`, `interval_tree_iter_first`, and `interval_tree_iter_next`. `struct interval_tree_span_iter` and `interval_tree_for_each_span` classify a requested range into alternating hole and used spans.

Control flow: Insert/remove are implemented elsewhere using augmented rbtree maintenance. Overlap iteration starts at the first intersecting node and advances to the next node whose interval intersects `[start,last]`. Span iteration initializes over a full requested range, greedily merges consecutive covered nodes into used spans, and reports gaps as holes until `is_hole == -1`.

State and persistence: Tree state is caller-owned through `rb_root_cached`; nodes must remain stable while linked. Span iterator keeps private node pointers and the current public span boundaries.

Dependencies and integration points: Depends on `linux/rbtree.h` and is the public concrete instance of the generic template in `interval_tree_generic.h`. Filesystems, memory managers, lock managers, and allocators can use it wherever interval overlap queries are needed.

Risks: The range end is inclusive, so off-by-one bugs are likely when callers convert from length-based ranges. Callers must provide external locking, prevent duplicate node misuse, and keep `start <= last`. Span iterator fields marked private should not be mutated by users.

Test signals: Insert/remove/query tests should cover empty trees, non-overlap fast paths, one-point intervals, adjacent-but-not-overlapping ranges, nested intervals, duplicate starts, span holes at beginning/end, and greedy merge of overlapping used spans.
