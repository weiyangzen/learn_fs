# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6table_security.c

Purpose: Implements the legacy IPv6 iptables `security` table for Mandatory Access Control policy rules that should be evaluated separately from ordinary discretionary filtering.

Important APIs, types, and functions: `security_table` defines the `xt_table` name, IPv6 family, valid hooks (`LOCAL_IN`, `FORWARD`, `LOCAL_OUT`), and `NF_IP6_PRI_SECURITY` priority. `sectbl_ops` stores allocated hook operations. `ip6table_security_table_init()` allocates the initial table and registers it. Pernet callbacks unregister in pre-exit/exit phases.

Control flow: Module init allocates hook ops using `ip6t_do_table()` as the hook, registers pernet operations, and registers an xtables template. Namespace initialization creates the default empty ruleset. Runtime packets at valid hooks run through `ip6t_do_table()`. Module exit reverses template, pernet, and hook-op allocation.

State and persistence: Only module-level hook ops and per-net xtables rulesets are kept. No on-disk persistence; userspace policy reload is required after reboot/module reload.

Dependencies and integration: Depends on ip6tables/xtables and MAC/security policy users such as SECMARK/CONNSECMARK workflows. Hook priority places it after normal filtering semantics expected by the security table.

Risks and test signals: Risks are mostly hook coverage and ordering. Tests should verify security table rule hits on local input, forwarding, and local output; namespace teardown with rules; and expected interaction with labels/marks used by LSM policy.
