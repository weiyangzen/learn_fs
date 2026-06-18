# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_defrag_ipv4.c

## Purpose
`nf_defrag_ipv4.c` provides IPv4 netfilter defragmentation hooks, enabling conntrack and related modules to request per-namespace fragment reassembly at PREROUTING and LOCAL_OUT.

## Important APIs, Types, And Functions
Exports are `nf_defrag_ipv4_enable()` and `nf_defrag_ipv4_disable()`. Runtime helpers are `nf_ct_ipv4_gather_frags()`, `nf_ct_defrag_user()`, and `ipv4_conntrack_defrag()`. The global hook descriptor is `defrag_hook`.

## Control Flow
Enable increments a per-net user count under `defrag4_mutex`, registering hooks on the first user and detecting overflow. The hook skips sockets marked `NODEFRAG`, already tracked/untracked packets in relevant configs, and non-fragments. Fragments are passed to `ip_defrag()` with a user id derived from hook, bridge prerouting status, and conntrack zone. Disable decrements and unregisters hooks when the count reaches zero.

## State And Persistence
Persistent state is per-net `net->nf.defrag_ipv4_users` and the global RCU pointer `nf_defrag_v4_hook`. Fragment queues live in the IPv4 defrag subsystem.

## Dependencies And Integration Points
It integrates with conntrack, bridge netfilter, conntrack zones, IPv4 defrag, pernet exit cleanup, and generic defrag hook registration.

## Risks
Risks include user-count underflow/overflow, hooks left registered after namespace exit, wrong zone-specific defrag user, stealing skb ownership incorrectly on reassembly, and NODEFRAG bypass regressions.

## Test Signals
Test enable/disable reference counting, overflow guard, fragment reassembly in PREROUTING and LOCAL_OUT, bridge prerouting, conntrack zones, untracked/already-tracked packets, NODEFRAG sockets, and namespace exit with active users.
