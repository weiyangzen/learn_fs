# sources/distributed-fs/ceph-client/include/linux/rbtree.h

Purpose: exposes Linux's intrusive red-black tree API, including core insertion/erase/replacement, traversal, cached-leftmost trees, linked-node trees, and generic find/add helpers that let users supply comparison callbacks without per-node virtual dispatch.

Important APIs and types: `rb_parent()`, `rb_entry()`, `RB_EMPTY_ROOT()`, and node clear/empty macros manage node state. Core externs include `rb_insert_color()`, `rb_erase()`, `rb_erase_linked()`, `rb_next()`, `rb_prev()`, postorder traversal, `rb_replace_node()`, and RCU replacement. Inline helpers include `rb_first()`, `rb_last()`, `rb_link_node()`, `rb_link_node_rcu()`, cached insert/erase/replace, `rb_add()`, `rb_add_cached()`, `rb_add_linked()`, `rb_find_add()`, `rb_find_add_cached()`, `rb_find_add_rcu()`, `rb_find()`, `rb_find_rcu()`, `rb_find_first()`, `rb_next_match()`, and `rb_for_each()`.

Control flow: callers implement comparison/search logic, link a node under the located parent, then rebalance with insert helpers. Erase removes and rebalances. Cached roots maintain O(1) leftmost access. RCU helpers publish pointers with release semantics but still require serialized writers and grace-period-safe object lifetime.

State and persistence: state is caller-owned intrusive tree nodes and roots in memory. Linked nodes add prev/next ordering links; cached roots store leftmost. No persistence is provided.

Dependencies and integration points: depends on container macros, rbtree type definitions, RCU, and standard kernel macros. It is used broadly for ordered indexes such as VMAs, timers, extents, and scheduler structures.

Risks and test signals: risks include double insertion without `RB_CLEAR_NODE`, comparison functions that violate ordering, RCU false negatives during rotations, missing writer serialization, stale cached leftmost, and freeing nodes before readers finish. Test insert/find/erase ordering, duplicate-key handling, cached leftmost updates, postorder destruction, RCU lookup under concurrent replacement, and linked-node prev/next consistency.
