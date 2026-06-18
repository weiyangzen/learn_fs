# sources/distributed-fs/ceph-client/include/linux/interval_tree_generic.h

Purpose: This header is a macro template for generating type-specific interval tree implementations backed by augmented cached red-black trees.

Important APIs, types, and functions: `INTERVAL_TREE_DEFINE(ITSTRUCT, ITRB, ITTYPE, ITSUBTREE, ITSTART, ITLAST, ITSTATIC, ITPREFIX)` expands to callbacks and functions named `<prefix>_insert`, `<prefix>_remove`, `<prefix>_subtree_search`, `<prefix>_iter_first`, and `<prefix>_iter_next`. It uses `RB_DECLARE_CALLBACKS_MAX` to maintain each node's maximum interval end in its subtree.

Control flow: Insert descends by interval start, updates ancestor subtree maxima opportunistically, links the node, and calls `rb_insert_augmented_cached`. Remove erases with augmented callbacks. `iter_first` uses root subtree max and cached leftmost start to reject non-overlapping queries in O(1), then calls subtree search. `iter_next` tries the right subtree, then climbs until a parent from a left branch can intersect.

State and persistence: The generated tree persists in a caller-supplied `rb_root_cached`. Each node must include an rbtree member and a maintained max-end field. The template does not allocate or free nodes.

Dependencies and integration points: Depends on `linux/rbtree_augmented.h`. It underpins the concrete `interval_tree` API and any subsystem needing custom interval endpoint types or struct layouts.

Risks: This macro assumes valid interval ordering and a correct subtree field. Supplying expressions with side effects for `ITSTART` or `ITLAST` can be dangerous because they are evaluated multiple times. External synchronization is required. The generated functions trust that removed nodes are linked in the target tree.

Test signals: Type-specific users should test insertion order permutations, cached leftmost correctness, subtree max maintenance after rotations/removes, inclusive boundary overlap, no-overlap fast paths, and iteration after deleting root or leftmost nodes.
