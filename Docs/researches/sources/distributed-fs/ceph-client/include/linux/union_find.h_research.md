<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/union_find.h -->
# sources/distributed-fs/ceph-client/include/linux/union_find.h

Purpose: declares a generic disjoint-set union-find data structure for kernel code that groups nodes into equivalence classes.

Important APIs and types: `struct uf_node` stores a parent pointer and rank. `UF_INIT_NODE(node)` and `uf_node_init()` initialize a singleton set. `uf_find()` returns the representative root, and `uf_union()` merges two sets, likely using rank and path compression in the implementation.

Control flow: embedding code initializes one `uf_node` per object, calls `uf_union()` when two objects become equivalent, and calls `uf_find()` to compare representatives or compress paths.

State and persistence: state is entirely in embedded `uf_node` parent/rank fields. It persists only as long as the owning objects and must be reinitialized if objects are reused.

Dependencies and integration points: the header has no includes; documentation is in `Documentation/core-api/union_find.rst`. It can be embedded in graph, component, clustering, or allocation algorithms needing disjoint sets.

Risks and test signals: risks include using uninitialized nodes, freeing a node still referenced as another node's parent, missing locking around concurrent unions/finds, and assuming deterministic representatives. Test singleton initialization, repeated union idempotence, path compression, rank behavior, and concurrent caller locking in each consumer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/union_find.h -->
