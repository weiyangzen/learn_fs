# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_nat.c

Purpose: Provides the legacy IPv6 iptables `nat` table and wires table lookups into the IPv6 NAT hook registration API. It enables destination NAT in prerouting/local-output and source NAT in postrouting/local-input for legacy ip6tables users.

Important APIs, types, and functions: `struct ip6table_nat_pernet` stores per-net duplicated NAT hook ops. `nf_nat_ipv6_table` declares the table. `nf_nat_ipv6_ops[]` defines four hooks using `ip6t_do_table()` at NAT priorities. `ip6t_nat_register_lookups()` finds the table, duplicates hook ops, sets `priv` to the xt table, and registers each with `nf_nat_ipv6_register_fn()`. `ip6t_nat_unregister_lookups()` unregisters and RCU-frees them. `ip6table_nat_table_init()` registers the table then hook lookups.

Control flow: Module init registers pernet storage before template registration so `net_generic()` state exists during table creation. Namespace init allocates/registers the initial nat table and then registers NAT lookup hooks. Runtime NAT hook dispatch calls `ip6t_do_table()` with the xt table as `priv`. On partial registration failure, previously registered hooks are unwound and the ops array is `kfree_rcu()`'d. Teardown unregisters hook lookups first, then unregisters the xt table in pre-exit/exit phases.

State and persistence: Per-net state stores `nf_nat_ops`; the xt table holds the current ruleset. Hook ops are dynamically duplicated because `priv` points at a namespace-specific table. Rules and ops are volatile kernel state.

Dependencies and integration: Depends on `nf_nat`, `ip6_tables`, pernet generic IDs, RCU lifetime, and `nf_nat_ipv6_register_fn()` rather than direct `nf_register_net_hooks()`. Integrates with legacy ip6tables NAT targets and conntrack/NAT core.

Risks and test signals: Main risks are lifetime bugs around table lookup, hook op duplication, and RCU freeing; NAT also requires correct priority ordering relative to conntrack. Tests should exercise module load/unload across multiple netns, failure injection for hook registration, DNAT/SNAT/MASQUERADE-style rules, and concurrent packet traversal while a namespace exits.
