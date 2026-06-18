# sources/distributed-fs/ceph-client/net/ipv6/ip6_input.c

Purpose: implements IPv6 packet ingress from L2 handoff through header validation, early demux, netfilter prerouting/local-in hooks, route input, protocol delivery, and multicast local/forward split.

Important APIs, types, and functions: `ipv6_rcv()`, `ipv6_list_rcv()`, `ip6_rcv_finish()`, `ip6_input()`, `ip6_mc_input()`, and `ip6_protocol_deliver_rcu()`. Internal helpers include `ip6_rcv_core()`, `tcp_v6_early_demux()`, `ip6_list_rcv_finish()`, and `ip6_input_finish()`.

Control flow: `ip6_rcv_core()` drops otherhost packets, checks device IPv6 state, clears IP6CB, records ingress ifindex, validates header version, ECN stats, loopback/multicast-source/scope rules, payload length, and Hop-by-Hop options, then orphans prefetched sockets as needed. Single-packet receive enters `NF_INET_PRE_ROUTING`, finishes with route input and `dst_input()`. List receive batches by device/net and route destination hints to reduce repeated lookups. Local input enters `NF_INET_LOCAL_IN`, clears delivery time, and delivers by walking extension-header protocol handlers until a final protocol is reached. Multicast input updates stats, optionally clones for multicast routing, and locally delivers only subscribed or MLD packets.

State and persistence: no persistent state, but it updates per-net/per-device IPv6 MIB counters, skb control block fields, skb dst/sk ownership, and drop reasons. It consumes or frees skbs on most paths.

Dependencies and integration points: integrates with netfilter IPv6 hooks, XFRM policy, raw IPv6 sockets, TCP/UDP handlers, early-demux socket lookup, IPv6 routing, l3mdev/VRF, addrconf, multicast routing, dst metadata, and ICMPv6 parameter-problem generation.

Risks: packet ownership is complex: handlers may consume skb, return a next protocol, or require discard. Extension-header recursion is bounded by `IP6_MAX_EXT_HDRS_CNT`; missing bounds would permit pathological packets. Multicast forwarding clone decisions must not double-free. The discard path increments `IPSTATS_MIB_INDISCARDS` twice in this snapshot, which may be intentional in this tree or a stats bug worth checking.

Test signals: malformed header/payload length/drop-reason tests, early demux for TCP/UDP with cached dst, netfilter prerouting/local-in order, extension-header chains and unknown protocols, XFRM policy rejects, multicast subscription and MLD router-alert handling, list receive batching, and VRF/l3mdev ingress.
