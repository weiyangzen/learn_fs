<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/nstree.c -->
# sources/distributed-fs/ceph-client/kernel/nstree.c

Purpose: Maintains global namespace id indexes and implements `listns(2)`, allowing namespace ids to be looked up and enumerated globally, by type, or by owning user namespace.

Important APIs/types/functions: namespace roots `mnt_ns_tree`, `net_ns_tree`, `uts_ns_tree`, `user_ns_tree`, `ipc_ns_tree`, `pid_ns_tree`, `cgroup_ns_tree`, `time_ns_tree`, plus `ns_tree_node_init()`, `ns_tree_root_init()`, `ns_tree_node_empty()`, `ns_tree_node_add()`, `ns_tree_node_del()`, `__ns_tree_add_raw()`, `__ns_tree_remove()`, `ns_tree_lookup_rcu()`, `__ns_tree_adjoined_rcu()`, `__ns_tree_gen_id()`, and `SYSCALL_DEFINE4(listns)`.

Control flow: Each namespace is inserted into a type-specific rbtree/list, a unified rbtree/list, and, if it has an owning user namespace, that owner's `ns_owner_root`. `ns_tree_lock` is a seqlock: writers take write seqlock; lookup readers retry on sequence changes; listns point lookups use exclusive read seqlock helpers when they need a stable tree walk. Lookup supports unified or type-specific ids. `listns()` copies and validates `struct ns_id_req`, checks flags and user buffer size, prepares a `klistns`, then either enumerates namespaces owned by a user namespace or enumerates unified/type-specific trees.

State and persistence: All state is volatile kernel memory in rbtrees and RCU lists. Namespace ids come from a static atomic64 cookie after `NS_LAST_INIT_ID` unless a fixed initial id is supplied. `klistns` temporarily holds userspace output pointers, requested type mask, pagination id, optional user namespace, and a pinned first namespace.

Dependencies/integration: Depends on `struct ns_common`, namespace proc operations for get/put, owner user namespace roots, RCU list helpers, rbtrees, `copy_struct_from_user()`, `put_user()`, namespace visibility helpers, and `ns_get_unless_inactive()`.

Risks: The file mixes seqlock-protected rbtrees with RCU list iteration; insertion/deletion order and grace-period assumptions must remain consistent. `ns_tree_node_add()` adds to the list after `rb_find_add_rcu()` and warns on duplicate only after all inserts, so duplicate-id bugs can corrupt multiple indexes before warning. `listns()` permission filtering is subtle: current namespace, owner capability, and global visibility are separate paths. Pagination uses `last_ns_id + 1`, so overflow and sparse id behavior need attention.

Test signals: namespace id generation uniqueness, insertion/removal from all three indexes, RCU lookup while namespaces are destroyed, `listns()` with unified/type masks, owner-restricted listing, pagination from `ns_id`, invalid `ns_id_req` sizes/spare bits/type masks, inaccessible namespaces, and inactive namespace filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/nstree.c -->
