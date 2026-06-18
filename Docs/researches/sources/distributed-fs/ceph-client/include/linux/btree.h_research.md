## sources/distributed-fs/ceph-client/include/linux/btree.h

**Purpose:** This is the public generic B+Tree interface for mapping unsigned integer keys of several widths to non-NULL pointers.

**Important APIs/types/functions:** `struct btree_head` stores the root node, mempool, and tree height. Generic functions include `btree_alloc`, `btree_free`, `btree_init_mempool`, `btree_init`, `btree_destroy`, `btree_lookup`, `btree_insert`, `btree_update`, `btree_remove`, `btree_merge`, `btree_last`, `btree_get_prev`, `btree_visitor`, and `btree_grim_visitor`. The header then includes `btree-128.h` and `btree-type.h` to produce typed `l`, `32`, and `64` wrappers plus safe reverse-iteration macros.

**Control flow, state, persistence:** The generic implementation stores sorted key/value pairs in mempool-allocated nodes laid out as keys followed by values. Insert/update/remove/merge mutate the tree and may allocate/free nodes; lookup and reverse iteration read current tree state. Persistence is in memory only.

**Dependencies/integration:** Depends on `linux/kernel.h` and `linux/mempool.h`. Users must provide external synchronization if the tree is shared across threads.

**Risks and test signals:** Risks include inserting duplicate keys, inserting `NULL` values, ignoring partial `btree_merge()` failure semantics, using the wrong typed geometry, and unsafe iteration while mutating. Test signals include generic and typed CRUD tests, memory-pressure injection, reverse traversal ordering, visitor/grim visitor cleanup, and lockdep/KASAN runs around concurrent users.
