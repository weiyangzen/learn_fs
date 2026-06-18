# sources/distributed-fs/ceph-client/net/ipv4/ip_tunnel.c

## Purpose
Implements the generic IPv4 tunnel netdevice library used by concrete frontends such as IPIP, GRE-derived devices, and VTI. It manages per-net tunnel lookup tables, tunnel creation/deletion/update, common receive decapsulation checks, encapsulation operation registration, transmit routing/PMTU handling, ioctl and rtnetlink support, MTU/headroom calculation, and per-net fallback tunnel lifecycle.

## APIs, Types, and Functions
Exported APIs include `ip_tunnel_lookup()`, `ip_tunnel_rcv()`, `ip_tunnel_encap_add_ops()`, `ip_tunnel_encap_del_ops()`, `ip_tunnel_encap_setup()`, `ip_md_tunnel_xmit()`, `ip_tunnel_xmit()`, `ip_tunnel_ctl()`, `ip_tunnel_parm_from_user()`, `ip_tunnel_parm_to_user()`, `ip_tunnel_siocdevprivate()`, `__ip_tunnel_change_mtu()`, `ip_tunnel_change_mtu()`, `ip_tunnel_dellink()`, `ip_tunnel_get_link_net()`, `ip_tunnel_get_iflink()`, `ip_tunnel_init_net()`, `ip_tunnel_delete_net()`, `ip_tunnel_newlink()`, `ip_tunnel_changelink()`, `__ip_tunnel_init()`, `ip_tunnel_uninit()`, and `ip_tunnel_setup()`. Important state types are `struct ip_tunnel`, `struct ip_tunnel_net`, `struct ip_tunnel_parm_kern`, `struct ip_tunnel_encap`, `struct ip_tunnel_info`, and hash buckets keyed by remote/key.

## Control Flow
Receive frontends call `ip_tunnel_lookup()` with link, flags, remote/local/key. Lookup tries exact local+remote+key, wildcard local, local-only/multicast, wildcard fallback, metadata tunnel, then fallback device. `ip_tunnel_rcv()` validates checksum and sequence flags, decapsulates ECN, resets inner protocol/device context, attaches metadata dst when present, updates stats, scrubs cross-net packets, and hands the skb to GRO cells.

Transmit through `ip_tunnel_xmit()` derives an outer destination from configured params, tunnel metadata, inner IPv4 route, or IPv6-compatible neighbour; applies TOS/TTL inheritance; performs optional UDP/GUE/FOU-style encapsulation; uses per-tunnel or per-metadata dst cache when safe; blocks self-recursion to the same device; updates PMTU and sends ICMP/ICMPv6 feedback for oversized inner packets; then calls `iptunnel_xmit()`. `ip_md_tunnel_xmit()` is the metadata-only variant driven by `skb_tunnel_info()`.

Create/update paths allocate or register netdevices, bind them to an egress device to derive headroom and MTU, add/remove them from RCU hash tables, reset dst caches, and expose both legacy private ioctls and rtnetlink newlink/changelink/dellink operations.

## State and Persistence
Per-network-namespace state is held in `ip_tunnel_net`: hash buckets, fallback tunnel device, collect-metadata tunnel pointer, device type, and rtnl ops. Each `ip_tunnel` persists params, input sequence number, error count/time, fwmark, net pointer, dst cache, GRO cells, encap settings, headroom lengths, and collect-md mode. Hash membership is RCU-protected and modified under RTNL. Encapsulation ops live in the global `iptun_encaps` table using cmpxchg and `synchronize_net()`.

## Dependencies and Integration
The library depends on netdevice/rtnetlink, namespaces, RCU hlist traversal, routing, dst cache, neighbour lookup, XFRM policy callers, ECN helpers, GRO cells, ICMP/ICMPv6 PMTU reporting, metadata dst, tunnel encapsulation ops, l3mdev/link binding, and concrete rtnl link ops provided by frontend modules.

## Risks
Risks include ambiguous wildcard lookup precedence, collect-metadata singleton conflicts, RCU hash removal races, sequence-number wrap handling, PMTU calculations with Ethernet vs tunnel devices, route cache invalidation, tunnel recursion, metadata tunnel address-family mismatches, user/kernel tunnel parameter conversion overflow, MTU clamping, and cleanup of fallback devices across namespace teardown.

## Test Signals
Test with multiple tunnels differing by local/remote/key/link, wildcard and fallback devices, collect-md exclusivity, rtnetlink create/change/delete, legacy SIOC* ioctls, PMTU and ICMP generation for IPv4 and IPv6 payloads, TOS/TTL inheritance, UDP encapsulation ops, dst-cache invalidation after route/link changes, GRO receive, namespace create/destroy, and lockdep/RCU checks around concurrent lookup and deletion.
