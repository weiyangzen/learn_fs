# sources/distributed-fs/ceph-client/net/ipv6/netfilter.c

Purpose: Supplies IPv6-specific netfilter core helpers for rerouting modified packets, performing route lookups for netfilter users, and fragmenting bridged IPv6 packets after netfilter processing.

Important APIs/types/functions: Exports `ip6_route_me_harder`, `__nf_ip6_route`, and `br_ip6_fragment`. It uses `flowi6`, `fib6_rules_early_flow_dissect`, `ip6_route_output`, XFRM session decoding/lookup, bridge fragment metadata, and IPv6 fragmentation helpers.

Control flow: `ip6_route_me_harder` builds a route key from the skb IPv6 header, mark, UID, l3mdev, socket binding, flow label, and strict output-interface rules for multicast/link-local destinations; replaces `skb_dst`; optionally applies XFRM; then ensures enough headroom for the new device header. `__nf_ip6_route` wraps `ip6_route_output`, using a fake bound socket for strict interface lookups. `br_ip6_fragment` validates bridge fragment size, finds the first fragmentable option, computes MTU and fragment ID, handles checksum completion, then either uses frag-list fast path or slow linear fragmentation and calls an output callback for each fragment.

State and persistence: No persistent ownership beyond skb route/dst mutation and fragment skb production. It consumes/drops skb ownership on fragmentation paths.

Dependencies/integration: Integrates with netfilter queue/bridge code, IPv6 routing, XFRM, l3mdev, bridge private skb control blocks, and exported netfilter IPv6 helpers.

Risks and test signals: Risks include incorrect strict interface routing, route/XFRM reference handling, headroom expansion failures, blackhole semantics hiding fragmentation errors, and preserving timestamps through fragments. Tests should mutate packet addresses/marks before reroute, cover link-local/multicast output selection, XFRM transformed versus untransformed skbs, bridge frag-list and slow-path fragmentation, invalid MTU/frag sizes, checksum-partial skbs, and output callback errors.
