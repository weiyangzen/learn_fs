# sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_raw.c

## Purpose
`iptable_raw.c` instantiates the legacy IPv4 `raw` table, used at PREROUTING and LOCAL_OUT before most connection tracking decisions, optionally before defragmentation.

## Important APIs, Types, And Functions
Important objects are `raw_before_defrag`, `packet_raw`, `packet_raw_before_defrag`, `rawtable_ops`, `iptable_raw_table_init()`, and module lifecycle functions.

## Control Flow
Module init chooses the table priority based on `raw_before_defrag`, allocates hook ops with `ipt_do_table()`, registers pernet ops, and registers the template. Table init uses the same selected table metadata. Exit unregisters the template using the normal raw table descriptor and removes pernet state.

## State And Persistence
State is the per-net raw xt table. The module parameter `raw_before_defrag` persists for the module lifetime and affects hook priority for all namespaces.

## Dependencies And Integration Points
It integrates with `ip_tables.c`, IPv4 netfilter priorities `NF_IP_PRI_RAW` and `NF_IP_PRI_RAW_BEFORE_DEFRAG`, and legacy NOTRACK/TRACE style workflows.

## Risks
Risks include priority mismatch with conntrack defrag, module exit unregistering the wrong template descriptor when `raw_before_defrag` is set, and rule behavior differences for fragmented packets.

## Test Signals
Test load with and without `raw_before_defrag`, PREROUTING and LOCAL_OUT traversal, interaction with defrag/conntrack, namespace lifecycle, and module unload cleanup.
