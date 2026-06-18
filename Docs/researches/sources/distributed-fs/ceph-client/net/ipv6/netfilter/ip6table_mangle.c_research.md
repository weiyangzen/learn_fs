# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_mangle.c

Purpose: Implements the legacy IPv6 iptables `mangle` table module. It registers the table for all major IPv6 netfilter hooks so rules can alter packet metadata and selected IPv6 header fields before normal forwarding, input, output, or postrouting handling.

Important APIs, types, and functions: `packet_mangler` describes the `xt_table` named `mangle`, valid hooks, IPv6 family, module owner, and `NF_IP6_PRI_MANGLE` priority. `ip6t_mangle_out()` is the local-output special case. `ip6table_mangle_hook()` dispatches either to that special handling or directly to `ip6t_do_table()`. `ip6table_mangle_table_init()` allocates the initial `ip6t_replace` blob and registers the table per network namespace. Module setup uses `xt_hook_ops_alloc()`, `register_pernet_subsys()`, and `xt_register_template()`.

Control flow: module init allocates hook operations for the table and registers pernet/template callbacks. A namespace table init creates the empty initial ruleset and binds it to the preallocated hook ops. Runtime packets call `ip6table_mangle_hook()`. For `NF_INET_LOCAL_OUT`, the code snapshots source, destination, mark, hop limit, and the first 32 bits containing version/traffic class/flow label, runs the table, then calls `ip6_route_me_harder()` if routing-sensitive fields changed and the packet was not dropped or stolen. Other hooks just execute `ip6t_do_table()`.

State and persistence: Global module state is limited to `mangle_ops`. Per-net state is the registered xtables table/ruleset managed by ip6tables core. No durable persistence exists; rules live in kernel memory and are removed by namespace/module teardown.

Dependencies and integration: Depends on `ip6_tables`, generic xtables template registration, net namespace lifecycle, IPv6 routing repair via `ip6_route_me_harder()`, and netfilter hook priorities. It integrates with userspace through legacy ip6tables rule management.

Risks and test signals: Critical risk is failing to reroute after local-output mangling of addresses, mark, hop limit, traffic class, or flow label. Tests should cover local-output rules changing `MARK`, destination/source address, hop limit, and traffic class with route changes, plus namespace creation/destruction and module unload. Hook ordering should be checked against raw, conntrack, nat, and security priorities.
