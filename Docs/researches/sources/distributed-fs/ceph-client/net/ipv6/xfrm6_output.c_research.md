# sources/distributed-fs/ceph-client/net/ipv6/xfrm6_output.c

## Purpose
Supplies IPv6-specific XFRM outbound handling, including local PMTU/error reporting, post-routing netfilter integration, tunnel-mode fragmentation decisions, and final handoff to generic `xfrm_output`.

## Important APIs, types, and functions
Public functions are `xfrm6_local_rxpmtu`, `xfrm6_local_error`, and `xfrm6_output`. Internal helpers are `__xfrm6_output_finish`, `xfrm6_noneed_fragment`, and `__xfrm6_output`.

## Control flow
`xfrm6_output` wraps outbound packets in `NF_HOOK_COND` for IPv6 post-routing unless the packet has already been rerouted. `__xfrm6_output` handles the callback. If netfilter rerouted a packet and there is no XFRM state, it marks `IP6SKB_REROUTED` and calls normal `dst_output`. For tunnel-mode XFRM, it selects the correct MTU source, detects non-GSO oversize packets, reports local PMTU if DF behavior requires it, permits a narrow fragment-header case for ESP/AH by setting `ignore_df`, returns local errors for sockets, or fragments with `ip6_fragment` before continuing to `xfrm_output`.

## State and persistence behavior
Only per-packet state is changed: skb flags, `ignore_df`, ICMP/PMTU reporting to socket state, and netfilter routing flags. No persistent state is owned.

## Dependencies and integration points
Depends on IPv6 routing MTU helpers, `dst->xfrm`, generic XFRM output, IPv6 fragmentation, netfilter post-routing, ICMPv6 local error helpers, and socket path-MTU settings. It is the outbound peer of the IPv6 XFRM policy and protocol files.

## Risks and test signals
Risks are PMTU regressions, double post-routing after reroute, fragmenting packets that should report EMSGSIZE, and mishandling pre-existing fragment headers around ESP/AH. Test tunnel and transport mode IPsec, GSO vs non-GSO oversize packets, `IPV6_DONTFRAG`/PMTU settings, post-routing netfilter reroute, local EMSGSIZE delivery, and ESP/AH packets already carrying fragment headers.
