## sources/distributed-fs/ceph-client/lib/rbtree.c

Purpose: core Linux red-black tree implementation, including non-augmented insert/erase, augmented callbacks, replacement helpers, inorder traversal, and postorder traversal.

Important APIs/functions: public exports include `rb_insert_color()`, `rb_erase()`, `__rb_insert_augmented()`, `__rb_erase_color()`, `rb_next()`, `rb_prev()`, `rb_replace_node()`, `rb_replace_node_rcu()`, `rb_next_postorder()`, and `rb_first_postorder()`. `rb_erase_linked()` additionally maintains a linked cached-leftmost wrapper.

Control flow: `__rb_insert()` repairs red-black properties after `rb_link_node()` using standard uncle-red color flips and rotations. `____rb_erase_color()` rebalances after deletion through sibling cases, handling symmetric left/right forms. Rotation helpers use `WRITE_ONCE()` for child-pointer changes to support lockless readers that may miss nodes but must not loop or observe invalid objects.

State and persistence: tree shape and node color/parent metadata are stored in caller-owned `rb_node` structures. Augmented callbacks allow users to maintain derived per-subtree state through propagation, copy, and rotate operations.

Dependencies/integration: depends on `linux/rbtree_augmented.h` and export macros. Many kernel subsystems embed `rb_node` in their own objects and provide search/link logic.

Risks/test signals: balancing code is case-heavy and pointer-order sensitive. RCU replacement requires publishing parent-child links last. `rbtree_test.c` provides invariant checks, postorder traversal checks, cached-tree comparisons, augmented propagation checks, and performance timing.
