# sources/distributed-fs/ceph-client/net/netfilter/core.c

## Purpose

`core.c` implements the central netfilter hook registry and slow-path verdict execution. It manages per-network-namespace hook arrays for IPv4, IPv6, ARP, bridge, netdev ingress/egress, and inet ingress, exposes registration APIs used by protocol modules, and initializes per-net netfilter state and procfs directories.

## Important APIs And Types

Important exports include `nf_register_net_hook`, `nf_unregister_net_hook`, `nf_register_net_hooks`, `nf_unregister_net_hooks`, `nf_hook_entries_insert_raw`, `nf_hook_entries_delete_raw`, `nf_hook_slow`, and `nf_hook_slow_list`. It also exports hook indirection pointers such as `nfnl_ct_hook`, `nf_ct_hook`, `nf_defrag_v4_hook`, `nf_defrag_v6_hook`, and, when conntrack is enabled, `nf_nat_hook`, `nf_ct_attach`, `nf_conntrack_destroy`, `nf_ct_set_closing`, `nf_ct_get_tuple_skb`, and `nf_ct_zone_dflt`.

The core data structure is `struct nf_hook_entries`, a compact allocation containing hook entries, original `nf_hook_ops` pointers, and an RCU head. `nf_hook_mutex` serializes hook table replacement. `dummy_ops` and `accept_all()` are used during unregistration so removing a hook cannot fail while concurrent readers still traverse the old array. With `CONFIG_JUMP_LABEL`, `nf_hooks_needed[NFPROTO_NUMPROTO][NF_MAX_HOOKS]` is exported as static keys for fast hook-presence checks.

## Control Flow

Hook registration calls `nf_register_net_hook`, which expands `NFPROTO_INET` into IPv4 and IPv6 registration except for `NF_INET_INGRESS`. `__nf_register_net_hook` validates netdev/ingress/egress constraints, finds the correct per-net or per-device hook head with `nf_hook_entry_head`, creates a priority-sorted replacement array with `nf_hook_entries_grow`, publishes it with `rcu_assign_pointer`, updates ingress/egress queue counters and jump labels, and frees the old array after RCU.

Unregistration marks the matching entry as `dummy_ops` through `nf_remove_net_hook`, decrements static keys and queue counters, then tries to shrink the array with `__nf_hook_entries_try_shrink`. If all hooks are removed the hook head becomes `NULL`; otherwise a new compact array is published. Queued packets are dropped with `nf_queue_nf_hook_drop` before the old table is released.

`nf_hook_slow` iterates from a supplied hook index. `NF_ACCEPT` continues, `NF_DROP` frees the skb and returns an error, `NF_QUEUE` delegates to `nf_queue`, `NF_STOLEN` returns ownership-derived status, and unexpected verdicts warn and stop. `nf_hook_slow_list` applies the same path to skb lists and rebuilds a list of accepted packets.

## State And Persistence

Hook tables are per network namespace in `net->nf.*` and per device for netdev ingress/egress. Updates are copy-on-write plus RCU; readers can traverse without taking `nf_hook_mutex`. Procfs state is created under each namespace at `net/netfilter` when `CONFIG_PROC_FS` is enabled. There is no disk persistence, but hook registration state persists for the lifetime of modules, namespaces, and devices.

## Dependencies And Integration

The file depends on core networking, net namespaces, RCU, skbuff handling, netdevices, nfqueue, procfs, jump labels, and optional conntrack/NAT. It is consumed by IPv4/IPv6 netfilter paths, nf_tables, xtables, BPF netfilter links, lwtunnel support, conntrack, defragmentation modules, and queue/logging backends.

## Risks

Hook ordering and RCU lifetime are the main risks. `nf_hook_entries_grow` enforces sorted priority order and disallows duplicate-priority BPF hooks, so changes here can reorder packet policy. Unregistration must not fail; replacing hooks with `dummy_ops` avoids allocation failure but requires careful shrink logic. Device namespace checks prevent hooks from attaching to the wrong namespace. Missing static key updates can leave fast paths disabled or incorrectly hot. Verdict handling must preserve skb ownership exactly.

## Test Signals

Signals include module load/unload loops for hooks, nf_tables and xtables rule insertion/removal, BPF hook attach attempts with duplicate priorities, ingress and egress rule tests on netdevices, namespace creation/destruction, nfqueue verdict paths, conntrack/NAT module unload, KASAN/KCSAN/lockdep runs, and packet tests verifying accepted, dropped, queued, and stolen verdict behavior.
