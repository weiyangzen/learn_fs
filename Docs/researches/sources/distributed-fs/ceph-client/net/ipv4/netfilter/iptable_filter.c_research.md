# sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_filter.c

## Purpose
`iptable_filter.c` instantiates the legacy IPv4 `filter` table for local input, forwarding, and local output.

## Important APIs, Types, And Functions
Important objects are `packet_filter`, `filter_ops`, module parameter `forward`, `iptable_filter_table_init()`, `iptable_filter_net_init()`, and module init/exit routines.

## Control Flow
Module init allocates hook ops using `ipt_do_table()`, registers pernet ops, and registers an xtables template. Initial table creation adjusts the default FORWARD policy based on the `forward` module parameter. If forwarding default is accept, namespace init can defer table creation until template lookup; if false, it eagerly creates the table.

## State And Persistence
The installed xt table is per-net state. The static `forward` module parameter determines the initial FORWARD policy for newly created tables.

## Dependencies And Integration Points
It depends on `ip_tables.c`, xtables templates, IPv4 netfilter hooks, and module parameters.

## Risks
Risks include surprising default FORWARD policy behavior, init failure cleanup ordering, and per-net table creation differences based on the module parameter.

## Test Signals
Test module load with `forward=1` and `forward=0`, default chain policies, local-in/forward/local-out hook traversal, namespace lifecycle, and cleanup on partial init failures.
