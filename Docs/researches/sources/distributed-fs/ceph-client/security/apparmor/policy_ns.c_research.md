# sources/distributed-fs/ceph-client/security/apparmor/policy_ns.c

Purpose: manages AppArmor policy namespaces, including root namespace allocation, namespace visibility/name virtualization, lookup, creation, recursive teardown, and the special unconfined labels for root and kernel contexts.

Important APIs, types, and functions: global state is `root_ns`, `kernel_t`, and `aa_hidden_ns_name`. Public helpers include `aa_ns_visible()`, `aa_ns_name()`, `aa_free_ns()`, `__aa_lookupn_ns()`, `aa_lookupn_ns()`, `__aa_find_or_create_ns()`, `aa_prepare_ns()`, `__aa_remove_ns()`, `aa_alloc_root_ns()`, and `aa_free_root_ns()`. Allocation flows through `alloc_ns()` and `alloc_unconfined()`; teardown flows through `destroy_ns()` and `__ns_list_release()`.

Control flow: namespace lookup walks hierarchical names split on `"//"` under RCU. Creation requires the parent namespace lock, allocates initialized namespace state, creates AppArmorFS namespace directories, links the namespace into the parent `sub_ns` list with RCU, and returns a counted reference. Removal unlinks from the parent, destroys profiles and child namespaces recursively, redirects unconfined proxy labels to the parent, removes AppArmorFS nodes, and drops list refs.

State and persistence: namespace objects hold profile lists, child namespace lists, raw load data, labels, wait queues, locks, parent refs, and an unconfined profile. Persistent user-visible state is exposed through AppArmorFS directories, but this file itself only creates/removes those nodes via `__aafs_ns_mkdir()` and `__aafs_ns_rmdir()`.

Dependencies and integration: depends on AppArmor policy/list primitives, labelsets, AppArmorFS namespace layout, RCU list traversal, mutex nesting by namespace level, and profile allocation/freeing. It is used by policy load/unload and label display logic.

Risks and test signals: refcount/list ownership is subtle: `ns->unconfined` shares namespace lifetime assumptions, and RCU readers require correct lock/ref rules. Namespace visibility affects procattr/secctx disclosure. Test signals include namespace creation depth enforcement, duplicate namespace rejection, recursive unload, visible/hidden namespace names, and AppArmorFS cleanup.
