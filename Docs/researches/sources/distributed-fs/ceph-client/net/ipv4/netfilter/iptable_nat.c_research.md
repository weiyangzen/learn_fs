# sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_nat.c

## Purpose
`iptable_nat.c` instantiates the legacy IPv4 `nat` table and registers NAT lookup hooks that execute `ipt_do_table()` at destination and source NAT priorities.

## Important APIs, Types, And Functions
Key pieces are `struct iptable_nat_pernet`, `nf_nat_ipv4_table`, `nf_nat_ipv4_ops[]`, `ipt_nat_register_lookups()`, `ipt_nat_unregister_lookups()`, `iptable_nat_table_init()`, and pernet/module lifecycle functions.

## Control Flow
Table initialization registers the `nat` xt table, then clones the NAT hook templates, sets each hook `priv` to the xt table, and registers them through `nf_nat_ipv4_register_fn()`. On failure it unregisters previously installed hooks and tears down the table. Per-net pre-exit unregisters hooks before table removal.

## State And Persistence
Per namespace state stores the cloned hook ops pointer in `iptable_nat_pernet`; table entries are normal xtables state. Hooks are freed via RCU after unregister.

## Dependencies And Integration Points
It depends on `ip_tables.c`, `nf_nat`, pernet generic storage, xtables templates, and NAT priorities for PREROUTING, POSTROUTING, LOCAL_OUT, and LOCAL_IN.

## Risks
Risks include hook/table lifetime ordering, partial registration leaks, RCU freeing of hook arrays, NAT priority regressions, and failures when the table cannot be found after registration.

## Test Signals
Test module load/unload, namespace lifecycle, PREROUTING/LOCAL_OUT DNAT and POSTROUTING/LOCAL_IN SNAT paths, partial hook registration failure, and table unregister after NAT hook unregister.
