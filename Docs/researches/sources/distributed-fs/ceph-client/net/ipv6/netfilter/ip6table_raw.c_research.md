# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_raw.c

Purpose: Implements the legacy IPv6 iptables `raw` table for early packet classification, primarily to mark traffic as untracked before conntrack. It can run at the standard raw priority or, via module parameter, before defragmentation.

Important APIs, types, and functions: `packet_raw` and `packet_raw_before_defrag` are two `xt_table` definitions with the same name and hooks but different priorities. `raw_before_defrag` is a read-mostly module parameter. `ip6table_raw_table_init()` selects the table variant, allocates an initial table, and registers it with `rawtable_ops`. Module init allocates hooks through `xt_hook_ops_alloc()` and registers pernet/template lifecycle hooks.

Control flow: During module init, the module parameter selects the hook priority and emits an informational log if before-defrag mode is enabled. A namespace init uses the same table choice to create the empty ruleset. Runtime hook handling is direct `ip6t_do_table()` at prerouting and local-output.

State and persistence: Global state includes `raw_before_defrag` and `rawtable_ops`; per-net state is the xtables ruleset. The module parameter is fixed at load time. Rule state is in kernel memory only.

Dependencies and integration: Integrates with xtables, net namespace lifecycle, and netfilter hook ordering. The before-defrag variant interacts closely with IPv6 fragment handling and conntrack defrag because rule evaluation may see fragments that would otherwise be reassembled first.

Risks and test signals: The `ip6table_raw_fini()` unregisters the template using `&packet_raw`; this relies on xtables template handling by table name despite possible before-defrag registration. Tests should cover both module parameter values, `NOTRACK` behavior before conntrack, fragmented traffic visibility, per-net registration, and unload after active rules.
