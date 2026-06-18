# sources/distributed-fs/ceph-client/tools/lib/rbtree.c

Purpose: User-space tools copy of Linux red-black tree implementation, including insertion, deletion/rebalancing, replacement, ordered traversal, and postorder traversal for `struct rb_root`/`struct rb_node`.

Important APIs/types/functions: Public functions include `rb_insert_color()`, `rb_erase()`, `__rb_insert_augmented()`, `__rb_erase_color()`, `rb_first()`, `rb_last()`, `rb_next()`, `rb_prev()`, `rb_replace_node()`, `rb_first_postorder()`, and `rb_next_postorder()`. Internal helpers include `rb_set_black()`, `rb_red_parent()`, `__rb_rotate_set_parents()`, `__rb_insert()`, and `____rb_erase_color()`.

Control flow: Insert fixes red-red violations using standard red-black cases: root recolor, uncle recolor, parent rotation, and grandparent rotation, mirrored for left/right. Delete delegates structural removal to `__rb_erase_augmented()` and then rebalances black-height violations through sibling cases. Traversal walks left/right extrema or climbs parent pointers. Replacement copies victim metadata and rewires children/root.

State and persistence: Mutates caller-owned tree nodes in memory. Parent and color are packed in `__rb_parent_color`; child pointers are updated with `WRITE_ONCE()` to support lockless lookup constraints described in comments. No allocation or persistence occurs.

Dependencies/integration: Includes `<linux/rbtree_augmented.h>` and `<linux/export.h>`. Augmented users supply rotate callbacks; non-augmented paths use dummy callbacks expected to optimize away.

Risks: Correctness depends on callers linking nodes in sorted order before insertion and providing external locking for updates. Lockless lookups are only guaranteed to terminate and return valid found nodes; they can miss nodes during mutation. Parent-pointer loops are not protected for lockless users. Misusing `rb_replace_node()` with a node already in a tree corrupts structure.

Test signals: Validate tree invariants after randomized insert/delete, in-order traversal, reverse traversal, postorder traversal, replacement, augmented callback invocation, empty tree behavior, and concurrent-reader assumptions under sanitizer or stress tests.
