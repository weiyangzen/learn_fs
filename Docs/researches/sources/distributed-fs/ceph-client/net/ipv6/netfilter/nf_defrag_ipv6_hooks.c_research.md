# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_defrag_ipv6_hooks.c

Purpose: Registers IPv6 netfilter defragmentation hooks on demand and connects them to `nf_ct_frag6_gather()`. It lets conntrack and other users share defrag hooks with per-network-namespace reference counting.

Important APIs, types, and functions: `nf_ct6_defrag_user()` derives the fragment cache user from hook, conntrack zone, and bridge prerouting state. `ipv6_defrag()` is the hook callback. `ipv6_defrag_ops[]` registers prerouting and local-output hooks at `NF_IP6_PRI_CONNTRACK_DEFRAG`. `nf_defrag_ipv6_enable()` and `nf_defrag_ipv6_disable()` are exported reference-counted enable/disable APIs. `defrag_hook` is published through `nf_defrag_v6_hook`.

Control flow: Module init initializes conntrack fragment reassembly, registers pernet exit cleanup, and publishes the defrag hook pointer via RCU. Enabling locks `defrag6_mutex`, checks overflow, increments existing users, or registers both hooks and sets users to one. Runtime skips already tracked non-template packets and untracked packets, then calls `nf_ct_frag6_gather()`. `-EINPROGRESS` means the fragment was queued and returns `NF_STOLEN`; zero accepts; other errors drop. Disable decrements and unregisters hooks when the count reaches zero.

State and persistence: Per-net `net->nf.defrag_ipv6_users` is the reference count. Fragment queues live in `nf_conntrack_reasm.c`. The RCU-published global hook pointer has module lifetime.

Dependencies and integration: Depends on conntrack when enabled, bridge netfilter, conntrack zones, netfilter hook registration, RCU hook publication, and net namespace exit cleanup. It is the main integration point by which conntrack requests IPv6 defrag.

Risks and test signals: Risks include reference-count leaks, overflow behavior, stale hooks on netns exit, and incorrect skip logic for untracked or already tracked packets. Tests should repeatedly enable/disable from multiple users, run fragmented prerouting/local-output traffic, use conntrack zones and bridge prerouting, and unload while namespaces with active users exit.
