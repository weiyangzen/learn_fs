
# sources/distributed-fs/ceph-client/include/linux/nstree.h

Purpose: declares namespace tree roots and operations for ID generation, insertion, removal, lookup, and adjacent iteration across namespace types.

Important APIs/types/functions: global roots include `cgroup_ns_tree`, `ipc_ns_tree`, `mnt_ns_tree`, `net_ns_tree`, `pid_ns_tree`, `time_ns_tree`, `user_ns_tree`, and `uts_ns_tree`. Node/root helpers initialize and modify tree entries. `to_ns_tree()` maps concrete namespace pointers to the correct root. `ns_tree_gen_id()`, `ns_tree_add_raw()`, `ns_tree_add()`, `ns_tree_remove()`, `ns_tree_lookup_rcu()`, `ns_tree_adjoined_rcu()`, and `ns_tree_active()` expose tree behavior.

Control flow: namespace creation assigns or preserves an ID, inserts nodes into the per-type tree, and later removes them during teardown. RCU lookup and adjacent traversal support namespace discovery/listing without taking heavy locks in readers.

State and persistence: tree roots hold in-memory namespace indexes sorted by ID/type. IDs are runtime identifiers with special initial namespace IDs; they are not stable persistence across boot.

Dependencies and integration points: depends on namespace tree types, nsproxy definitions, rbtree, seqlock, RCU lists, cookie helpers, and nsfs UAPI constants. It integrates namespace lifetime management with listns/open-by-handle style discovery.

Risks and test signals: risks include RCU lookup use without active/main refs, duplicate ID insertion, removing inactive nodes twice, and `_Generic` tree mapping omissions. Test signals include namespace list ordering checks, concurrent creation/destruction lookup stress, init namespace ID preservation, and debug validation of `ns_tree_active()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nstree.h -->
