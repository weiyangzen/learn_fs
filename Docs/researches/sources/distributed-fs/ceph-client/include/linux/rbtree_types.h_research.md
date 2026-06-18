# sources/distributed-fs/ceph-client/include/linux/rbtree_types.h

Purpose: defines the minimal red-black tree node and root types shared by rbtree users without pulling in the full operation API.

Important APIs and types: `struct rb_node` stores parent/color in one aligned word plus left and right children. `struct rb_node_linked` adds prev/next links around an embedded `rb_node`. `struct rb_root`, `struct rb_root_cached`, and `struct rb_root_linked` represent plain, leftmost-cached, and linked-leftmost trees. Initializer macros are `RB_ROOT`, `RB_ROOT_CACHED`, and `RB_ROOT_LINKED`.

Control flow: callers embed one of the node types in their own objects, initialize a root, then use operations from `rbtree.h` or augmented/latch variants.

State and persistence: state is intrusive in-memory tree topology. Color is encoded in parent low bits, relying on node alignment.

Dependencies and integration points: standalone type header used by low-level code that needs declarations without rbtree helper macros.

Risks and test signals: risks include alignment assumptions on unusual architectures, copying live nodes, embedding one node in multiple trees at once, and failing to initialize roots. Test architecture builds, static initializers, linked tree insertion/erase, and debug checks for empty/linked node state.
