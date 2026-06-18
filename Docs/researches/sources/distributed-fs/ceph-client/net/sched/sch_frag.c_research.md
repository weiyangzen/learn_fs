# sources/distributed-fs/ceph-client/net/sched/sch_frag.c

## Purpose
`sch_frag.c` provides `sch_frag_xmit_hook()`, a helper for qdisc/action transmit paths that need to fragment packets when `tc_skb_cb(skb)->mru` is set and the skb exceeds that MRU plus link header length.

## Important APIs, Types, And Functions
The exported API is `sch_frag_xmit_hook(struct sk_buff *skb, int (*xmit)(struct sk_buff *skb))`. Per-CPU scratch state is `struct sch_frag_data`, storing original dst ref, qdisc skb cb, VLAN state, inner protocol, L2 header copy, and the original xmit callback. Internal helpers are `sch_fragment()`, `sch_frag_prepare_frag()`, `sch_frag_xmit()`, and `sch_frag_dst_get_mtu()`.

## Control Flow
The hook sends directly through `xmit` unless MRU is nonzero and packet length exceeds MRU plus hard header length. Fragmentation rejects unexpectedly long L2 headers, then handles IPv4 with a temporary `rtable` and `ip_do_fragment()` or IPv6 with a temporary `rt6_info` and `ip6_fragment()`. Before fragmenting it copies L2/qdisc/VLAN/protocol state into per-CPU storage, pulls the L2 header, resets IP control block fields, installs a temporary dst whose MTU callback returns device MTU, and sets `frag_max_size` to MRU. Each produced fragment enters `sch_frag_xmit()`, which restores dst, qdisc cb, VLAN tag state, inner protocol, and MAC header before calling the original xmit callback.

## State And Persistence
State is per-CPU and protected by `local_lock_nested_bh()`. It lives only during the fragmentation call chain. The original dst reference is restored/dropped after fragmentation via `refdst_drop(orig_dst)`. There is no netlink state or qdisc registration in this file.

## Dependencies And Integration Points
The file integrates with IPv4/IPv6 fragmentation APIs, dst ops, VLAN acceleration helpers, qdisc skb control blocks, tc MRU metadata, and the caller’s transmit callback. It is exported GPL-only for scheduler/action users.

## Risks
The per-CPU scratch area assumes fragmentation callbacks occur under the local lock; nested misuse could corrupt state. Non-IP packets over MRU are dropped with a rate-limited warning. L2 headers longer than `VLAN_ETH_HLEN` cannot be reconstructed and are dropped. Correct restoration of qdisc cb and VLAN metadata is critical because fragments re-enter downstream transmit paths. Temporary dst use and `refdst_drop()` must remain balanced.

## Test Signals
Test direct transmit when MRU is zero or packet fits, IPv4 and IPv6 fragmentation when over MRU, non-IP drop path, long-L2-header drop path, VLAN-tag preservation, qdisc skb cb preservation, MAC header reconstruction, checksum adjustment after `skb_push()`, and callback error propagation from fragment xmit.
