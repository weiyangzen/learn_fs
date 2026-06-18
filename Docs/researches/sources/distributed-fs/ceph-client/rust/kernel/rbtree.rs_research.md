## sources/distributed-fs/ceph-client/rust/kernel/rbtree.rs

Purpose: provides an owned Rust wrapper around Linux `rb_root`/`rb_node`, exposing map-like red-black-tree operations while preserving kernel allocation and pointer layout. It is generic over ordered keys and values and supports preallocation through `RBTreeNodeReservation` for contexts that cannot sleep while inserting.

Important APIs/types/functions: `RBTree<K,V>` owns the root and drops all nodes in postorder. `try_create_and_insert`, `insert`, `entry`, `find_mut`, `get`, `get_mut`, `remove_node`, `remove`, and lower-bound cursor constructors are the main map APIs. `Cursor` and `CursorMut` provide bidirectional traversal, peeking, and node removal. `Iter`, `IterMut`, and `IntoIterator` expose sorted iteration. `RBTreeNode` owns one boxed `Node`, and `RBTreeNodeReservation` stores uninitialized boxed node memory for later initialization.

Control flow: lookup and insertion walk raw child pointers by comparing keys. Vacant insertion links a node with `rb_link_node` and rebalances with `rb_insert_color`; duplicate insertion replaces with `rb_replace_node`. Removal calls `rb_erase` before converting the raw node back into a `KBox`. Cursor movement delegates to `rb_prev`/`rb_next`, and cursor removal selects the next neighbor first, then the previous one.

State/persistence: state is purely in-memory kernel heap plus embedded C rb links. Ownership of each allocation transfers between `RBTreeNode`, the live tree, and removed/replaced return values. No persistent storage or serialization exists.

Dependencies/integration: depends on `bindings` rbtree functions, `container_of!`, `KBox`, allocator `Flags`, `MaybeUninit`, `NonNull`, and Rust ordering traits. Integrates with locking externally; the tree itself has no internal synchronization.

Risks: all safety rests on rb link pointers always referring to `Node<K,V>::links`, and on no concurrent mutation during iteration/cursor use. Replacement requires equal keys but only call-site lookup enforces that. Iterator raw pointers become invalid if the tree is mutated outside the borrow model through unsafe aliases. `Drop` breaks invariants internally while freeing nodes, so postorder traversal must obtain next before dropping current.

Test signals: extensive doctests cover insertion, replacement, iteration, mutable access, removal, preallocation, reservations, cursors, lower-bound search, and cursor-adjacent removal. Additional stress should cover duplicate keys, drop order of key/value destructors, and lock-protected insertions in non-sleepable contexts.
