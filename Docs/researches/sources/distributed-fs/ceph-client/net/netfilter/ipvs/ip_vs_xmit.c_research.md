# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_xmit.c

## Purpose
`ip_vs_xmit.c` implements the packet transmit side of IPVS forwarding. It turns an `ip_vs_conn` decision into a concrete packet action for null, bypass, NAT/masquerade, direct-routing, IP tunnel, and ICMP forwarding modes for IPv4 and, when enabled, IPv6. It is responsible for route lookup, destination-route caching, TTL/hop-limit handling, MTU/PMTU checks, header rewriting, encapsulation, conntrack handoff, and final submission to netfilter output or the local stack.

## Important APIs, Types, And Functions
Key state is `struct ip_vs_dest_dst`, cached behind `ip_vs_dest->dest_dst` with RCU and updated under `dest->dst_lock`. `__ip_vs_dst_set()` installs or clears cached dst entries, while `__ip_vs_dst_check()` validates cached route obsolescence. Route behavior is controlled by local `IP_VS_RT_MODE_*` flags.

The central route helpers are `__ip_vs_get_out_rt()` and `__ip_vs_get_out_rt_v6()`. They resolve or reuse routes, enforce local/non-local boundary rules, decrement TTL, compute tunnel-adjusted MTU, call `ensure_mtu_is_adequate()`, and replace the skb dst. Transmit entry points include `ip_vs_nat_xmit()`, `ip_vs_tunnel_xmit()`, `ip_vs_dr_xmit()`, `ip_vs_bypass_xmit()`, `ip_vs_null_xmit()`, `ip_vs_icmp_xmit()`, plus IPv6 variants. Tunnel helpers include `ip_vs_prepare_tunneled_skb()`, `ipvs_gue_encap()`, `ipvs_gre_encap()`, and `ip_vs_tunnel_xmit_prepare()`.

## Control Flow
Transmitters first obtain an output route for `cp->daddr` or the original packet destination. NAT paths allow local and non-local destinations and optionally redirect remote traffic to local addresses; direct-routing and bypass paths use a known or packet destination route; tunnel paths reserve outer-header headroom and encapsulate. NAT transmitters ensure writable headers, run the protocol `dnat_handler`, rewrite destination addresses, set `ignore_df`, and call `ip_vs_nat_send_or_cont()`. Direct and bypass paths mostly preserve packet headers after TTL/MTU validation and call `ip_vs_send_or_cont()`. Tunnel paths build an outer IPv4 or IPv6 header, optionally insert GUE or GRE, configure GSO/offload metadata, and call `ip_local_out()` or `ip6_local_out()` after conntrack confirmation/reset.

## State And Persistence
Persistent runtime state is kernel in-memory route cache state on `ip_vs_dest`, with RCU-delayed freeing, and per-connection flags in `struct ip_vs_conn`. SKB state is heavily mutated: `skb->ipvs_property`, dst, checksum state, timestamp, `ignore_df`, network/transport headers, and optional conntrack references are changed. There is no durable storage.

## Dependencies And Integration Points
The file integrates with routing, XFRM, netfilter hooks, IPVS protocol handlers, conntrack/IPVS glue, tunnel/offload helpers, and ICMP/ICMPv6 error reporting.

## Risks
Highest-risk areas are route cache lifetime and invalidation, local/non-local boundary checks, MTU accounting for nested GUE/GRE/remcsum headers, checksum/offload metadata correctness, and NAT-to-local duplicate conntrack protection for synced connections. Changes to skb ownership, early-demux socket orphaning, or `skb_dst_set_noref()` can create leaks, use-after-free, or incorrect delivery.

## Test Signals
Test IPVS NAT, DR, tunnel, bypass, and local-node traffic over IPv4/IPv6; GUE/GRE with checksum/remcsum and GSO; PMTU/DF too-big behavior; TTL/hop-limit expiry; NAT to loopback rejection; synced DNAT-to-local protection; ICMP/ICMPv6 forwarding; route cache invalidation; and conntrack-enabled versus notrack flows.
