# sources/distributed-fs/ceph-client/net/bridge/netfilter/nf_conntrack_bridge.c

## Purpose
Provides native bridge-family IPv4/IPv6 connection tracking, including bridge prerouting defragmentation/tracking, local-in clone handling, postrouting confirmation, and refragmentation after conntrack processing.

## Important APIs, Types, And Functions
Key functions include `nf_ct_bridge_pre`, `nf_ct_bridge_in`, `nf_ct_bridge_post`, `nf_ct_br_defrag4`, `nf_ct_br_defrag6`, `nf_br_ip_fragment`, `nf_ct_bridge_refrag`, `nf_ct_bridge_frag_save`, `nf_ct_bridge_frag_restore`, and `nf_ct_bridge_refrag_post`. Registration uses `nf_ct_bridge_info` with three `nf_hook_ops`.

## Control Flow
Prerouting skips already-tracked or untracked packets, trims and validates IPv4/IPv6 payloads, defragments fragments while preserving bridge skb control block state, then invokes `nf_conntrack_in` using IPv4 or IPv6 protocol family. Local-in clears unconfirmed conntrack from non-host clones so inet prerouting can track again. Postrouting confirms conntrack and, when `frag_max_size` indicates defragmentation happened, saves L2/VLAN data, fragments IPv4 or IPv6 output, restores the bridge L2/VLAN header per fragment, and queues through bridge transmit.

## State And Persistence Behavior
State lives in skb conntrack pointers, bridge skb control block fields, defrag queues, and conntrack tables owned by nf_conntrack. The module registers bridge hooks globally through `nf_ct_bridge_register`; no disk persistence exists.

## Dependencies And Integration Points
Depends on nf_conntrack core/helper APIs, IPv4/IPv6 defrag and fragmentation helpers, bridge output `br_dev_queue_push_xmit`, VLAN tag helpers, skb control block layout from `br_private.h`, and module alias `nf_conntrack-AF_BRIDGE`.

## Risks And Test Signals
Risks include skb control block save/restore mistakes, fragment geometry loss, VLAN tag/header restoration, confirmed clone handling for multicast/broadcast, IPv6 defrag optionality, and silent blackhole behavior on fragmentation failure. Tests should cover fragmented IPv4/IPv6 bridge traffic, VLAN-tagged fragments, multicast clones, untracked non-IP traffic, postrouting refragmentation MTU behavior, conntrack zone behavior, and netns/module unload.
