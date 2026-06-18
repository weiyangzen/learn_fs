# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_filter.c

Purpose: Registers the legacy IPv6 `filter` table and its local-in, forward, and local-out hooks.

Important APIs/types/functions: Defines `packet_filter`, `filter_ops`, module parameter `forward`, `ip6table_filter_table_init`, pernet ops, `ip6table_filter_init`, and `ip6table_filter_fini`. It calls `ip6t_alloc_initial_table`, `ip6t_register_table`, `ip6t_unregister_table_exit`, `xt_hook_ops_alloc`, and xt template registration.

Control flow: Init allocates hook ops using `ip6t_do_table`, registers pernet state, then registers a template so namespaces get the filter table lazily or at init. Table init creates the standard initial table and sets the default FORWARD verdict from module parameter `forward`. Net pre-exit unregisters the table from hooks before final exit frees it. Module exit unregisters template/pernet ops and frees hook ops.

State and persistence: Per-net registered filter table and static hook ops persist while module is loaded. The `forward` parameter is read at table creation and controls initial FORWARD policy.

Dependencies/integration: Depends on legacy ip6tables core and x_tables hook/template APIs. Built by `CONFIG_IP6_NF_FILTER`.

Risks and test signals: Risks include hook-op allocation failure cleanup, namespace lifecycle ordering, default policy surprises from `forward`, and template registration rollback. Tests should load/unload module, create/destroy net namespaces, inspect initial policies with `forward=0/1`, replace rules under traffic, and verify pre-exit prevents hook use after table teardown.
