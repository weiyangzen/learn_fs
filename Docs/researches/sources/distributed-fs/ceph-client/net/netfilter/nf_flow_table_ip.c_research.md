
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_ip.c

Purpose: Implements the software fast path for IPv4 and IPv6 flowtable forwarding. It parses tuples from incoming packets, validates packet eligibility, applies NAT rewrites, pops and pushes VLAN/PPPoE/IP tunnel encapsulation, updates counters, and transmits by direct L2, neighbour lookup, or xfrm output.

Important APIs and functions: Exported hooks are `nf_flow_offload_ip_hook()` and `nf_flow_offload_ipv6_hook()`. Tuple builders `nf_flow_tuple_ip()` and `nf_flow_tuple_ipv6()` parse TCP/UDP/GRE tuples. `nf_flow_offload_forward()` and `nf_flow_offload_ipv6_forward()` perform common validation, state checks, NAT, TTL/hop-limit decrement, and accounting. Encapsulation helpers include `nf_flow_encap_pop()`, `nf_flow_encap_push()`, `nf_flow_vlan_push()`, `nf_flow_pppoe_push()`, `nf_flow_tunnel_ipip_push()`, and `nf_flow_tunnel_ip6ip6_push()`.

Control flow: A hook builds a context from input device and possible tunnel/encap offset, extracts a tuple, and calls `flow_offload_lookup()`. On a hit, it checks MTU/GSO, TCP FIN/RST/SYN closing state, dst cache validity, and skb writability. It refreshes the flow timeout, removes ingress encapsulation, applies SNAT/DNAT address and port rewrites, decrements TTL/hop-limit, updates conntrack accounting when enabled, and sends the skb through xfrm, neighbour-derived L2, or direct cached L2 addresses. Misses and non-offloadable packets continue through normal netfilter.

State and persistence: Packet-local state lives in `struct nf_flowtable_ctx` and `struct nf_flow_xmit`; persistent flow state is in `struct flow_offload_tuple` fields created by the core/path code. The datapath mutates skb headers and may set flow teardown/closing flags.

Dependencies and integration: Uses conntrack accounting, route/dst/neighbour APIs, GSO segmentation, IPv4/IPv6 tunnel helpers, VLAN/PPPoE helpers, and NAT port helpers exported by core. It is invoked by `nf_flow_table_inet.c` and referenced by nftables flowtable types.

Risks: This is a critical packet mutation path. Risk areas include checksum correctness for NAT, skb linearity/writability, handling of fragments/options/extension headers, tunnel MTU adjustments, GSO segmentation when adding encapsulation, neighbour lifetime, xfrm skb control block setup, and returning `NF_STOLEN` only after ownership transfer. Test signals should cover IPv4/IPv6 TCP and UDP with SNAT/DNAT, VLAN and PPPoE ingress/egress, IPIP/IP6IP6 tunnels, xfrm flows, PMTU/GSO boundaries, TCP FIN/RST teardown, and malformed/truncated packets.
