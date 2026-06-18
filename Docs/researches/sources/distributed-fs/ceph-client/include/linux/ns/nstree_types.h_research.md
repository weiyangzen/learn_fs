
# sources/distributed-fs/ceph-client/include/linux/ns/nstree_types.h

Purpose: defines the storage primitives for namespace trees: sorted red-black trees for lookup and matching lists for ordered iteration.

Important APIs/types/functions: `struct ns_tree_root` contains an `rb_root` plus `ns_list_head`. `struct ns_tree_node` contains an `rb_node` and list entry. `struct ns_tree` stores a namespace ID, active reference counter, nodes for global/per-type/owner trees, and a root for namespaces owned by the namespace.

Control flow: namespace initialization embeds an `ns_tree` in `ns_common`; namespace tree code initializes nodes, assigns IDs, inserts nodes into global and per-type roots, and removes them when reference lifetime ends. The list and rbtree represent the same ordering so lookups and sequential listns-style iteration can both be efficient.

State and persistence: state is transient kernel namespace-index state. `ns_id` and tree membership persist while the namespace is alive and tree-visible; they are not a stable on-disk identifier.

Dependencies and integration points: depends on `linux/rbtree.h` and `linux/list.h`. It is consumed by `nstree.h`, `ns_common_types.h`, and namespace lifecycle code.

Risks and test signals: risks include list/rbtree ordering divergence, double insertion/removal, ID reuse assumptions, and active reference counter misuse. Test signals include namespace creation/destruction stress, list iteration under concurrent namespace churn, lookup by ID/type, and debug checks for empty nodes after removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ns/nstree_types.h -->
