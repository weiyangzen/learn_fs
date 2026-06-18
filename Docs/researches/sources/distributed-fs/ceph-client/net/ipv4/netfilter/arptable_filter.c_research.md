# sources/distributed-fs/ceph-client/net/ipv4/netfilter/arptable_filter.c

## Purpose
`arptable_filter.c` instantiates the legacy ARP `filter` table over ARP input, output, and forward hooks.

## Important APIs, Types, And Functions
The main objects are `packet_filter`, `arpfilter_ops`, `arptable_filter_table_init()`, `arptable_filter_net_pre_exit()`, `arptable_filter_net_exit()`, `arptable_filter_init()`, and `arptable_filter_fini()`.

## Control Flow
Module init allocates hook ops with `xt_hook_ops_alloc()` using `arpt_do_table()`, registers per-net exit hooks, and registers an xtables template. Each namespace gets an initial filter table through the template callback. Exit unregisters the template, pernet ops, and hook ops.

## State And Persistence
State is per namespace through the registered xt table. The module holds one static hook-ops array pointer shared as template data.

## Dependencies And Integration Points
It depends on `arp_tables.c`, xtables templates, ARP netfilter family hooks, and kfree-managed hook ops.

## Risks
Risks are init/exit ordering mistakes, hook-op allocation failure handling, and unregistering a table while hooks may still observe it.

## Test Signals
Test module load/unload, namespace creation/destruction, default table availability, ARP input/output/forward hooks, and cleanup under failed `register_pernet_subsys()` or `xt_register_template()`.
