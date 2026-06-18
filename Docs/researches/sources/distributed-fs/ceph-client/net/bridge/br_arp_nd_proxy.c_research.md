<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_arp_nd_proxy.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_arp_nd_proxy.c

Purpose: implements bridge ARP proxy, IPv6 Neighbor Discovery suppression/proxy behavior, and helper logic for per-port or per-VLAN neighbor suppression.

Important APIs, types, and functions: `br_recalculate_neigh_suppress_enabled` updates the bridge-level optimization bit. IPv4 helpers include `br_do_proxy_suppress_arp`, `br_arp_send`, and local-address checks. IPv6 helpers include `br_is_nd_neigh_msg`, `br_do_suppress_nd`, `br_nd_send`, and local IPv6 address checks. `br_is_neigh_suppress_enabled` is the exported predicate for port and VLAN suppress state.

Control flow: ingress ARP or ND processing starts from bridge input/transmit paths when `BROPT_NEIGH_SUPPRESS_ENABLED` is set. ARP handling validates header lengths and address types, skips loopback/multicast targets, suppresses floods for gratuitous/duplicate cases, checks local bridge or VLAN IP ownership, then looks up a neighbor entry and matching FDB entry. If the destination port is proxy/suppress eligible, it crafts an ARP reply and either transmits through the port path or injects locally for bridge-originated traffic. ND handling validates ICMPv6 neighbor solicitation/advertisement, suppresses unsolicited advertisements and invalid source cases, checks local IPv6 ownership, then replies with a Neighbor Advertisement based on neighbor and FDB state.

State and persistence: no persistent tables are owned here. It reads bridge port flags, VLAN private flags, neighbor tables, FDB entries, bridge options, and writes `BR_INPUT_SKB_CB(skb)->proxyarp_replied` to guide later flooding decisions.

Dependencies and integration points: integrates with ARP, IPv6 addrconf, neighbor tables, VLAN devices, bridge FDB/VLAN helpers, SKB control block state, and bridge forwarding paths. IPv4 code is gated by `CONFIG_INET`; IPv6 ND code is gated by `CONFIG_IPV6`.

Risks: packet parsing and skb linearization must be conservative. Incorrect suppression can blackhole neighbor discovery or leak broadcasts to suppressed ports. VLAN PVID/tag handling affects whether replies are tagged correctly. Local-address detection walks upper devices, so RCU context and device references matter. ND option parsing must avoid malformed option loops.

Test signals: ARP/ND proxy and suppression selftests with per-port and per-VLAN settings, VLAN-tagged requests, local bridge IP targets, gratuitous ARP, unsolicited NA, invalid ND options, neighbor table validity changes, and FDB-known versus unknown destinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_arp_nd_proxy.c -->
