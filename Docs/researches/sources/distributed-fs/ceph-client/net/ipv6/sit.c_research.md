# sources/distributed-fs/ceph-client/net/ipv6/sit.c

## Purpose
`sit.c` implements the SIT tunnel driver: IPv6, IPv4, and optionally MPLS carried over IPv4, with compatibility support for 6to4, 6rd, and ISATAP. It registers the `"sit"` rtnetlink kind, per-net fallback `sit0` device, xfrm tunnel protocol handlers, ioctl controls, and transmit/receive paths for protocol 41-style tunnels.

## Important APIs, types, and functions
Per-net state is `struct sit_net`, which stores four tunnel hash tables: wildcard, local-only, remote-only, and local+remote, plus the fallback device. Lookup and registration helpers are `ipip6_tunnel_lookup()`, `__ipip6_bucket()`, `ipip6_tunnel_link()`, `ipip6_tunnel_unlink()`, `ipip6_tunnel_create()`, and `ipip6_tunnel_locate()`.

Control interfaces include `ipip6_tunnel_ctl()`, `ipip6_tunnel_siocdevprivate()`, `ipip6_newlink()`, `ipip6_changelink()`, `ipip6_fill_info()`, and `ipip6_validate()`. PRL/ISATAP helpers include `ipip6_tunnel_get_prl()`, `ipip6_tunnel_add_prl()`, `ipip6_tunnel_del_prl()`, `ipip6_tunnel_prl_ctl()`, and `isatap_chksrc()`. 6rd support is handled by `check_6rd()`, `try_6rd()`, and `ipip6_tunnel_update_6rd()` when configured.

Data-path functions include `ipip6_rcv()`, `sit_tunnel_rcv()`, `ipip_rcv()`, optional `mplsip_rcv()`, `ipip6_tunnel_xmit()`, `sit_tunnel_xmit__()`, and `sit_tunnel_xmit()`. Device lifecycle is wired through `ipip6_netdev_ops`, `ipip6_tunnel_setup()`, `ipip6_tunnel_init()`, `ipip6_tunnel_uninit()`, and `ipip6_dev_free()`.

## Control flow
Module initialization registers per-net state, xfrm4 tunnel handlers for IPv6-in-IPv4, IPv4-in-IPv4, optional MPLS-in-IPv4, and then the rtnetlink link kind. Per netns initialization creates `sit0` when fallback tunnels are enabled and places it in the wildcard bucket.

Receive flow starts in the xfrm handler. `ipip6_rcv()` looks up a matching tunnel by outer source/destination and ingress scope, verifies that the tunnel accepts IPv6 or any protocol, reassigns the skb to the tunnel device, checks spoofing rules, pulls the IPv4 outer header, decapsulates ECN, updates tunnel rx stats, and injects the inner IPv6 packet via `netif_rx()`. `sit_tunnel_rcv()` handles inner IPv4 and MPLS by checking xfrm policy, pulling the outer header with the correct inner protocol, and delegating to generic `ip_tunnel_rcv()`.

Transmit flow in `sit_tunnel_xmit()` dispatches by skb protocol. IPv6 uses `ipip6_tunnel_xmit()`, which chooses an outer IPv4 destination from configured remote, ISATAP neighbor, embedded 6rd/6to4 address, or IPv4-compatible neighbor; routes the outer packet; enforces PMTU/DF rules; handles ECN encapsulation; prepares headroom and offloads; optional UDP tunnel encapsulation; and calls `iptunnel_xmit()`. IPv4 and MPLS use generic `ip_tunnel_xmit()` through `sit_tunnel_xmit__()`.

Configuration through ioctl or rtnetlink validates IP header version, header length, protocol, DF/TTL behavior, link directionality, duplicate tunnel keys, encapsulation parameters, fwmark, MTU, and optional 6rd attributes. Updating a tunnel unlinks it from hash buckets, synchronizes readers, changes endpoint/link/fwmark fields, relinks it, resets the dst cache, recalculates device binding, and emits a state change.

## State and persistence
Tunnel state is in `struct ip_tunnel` instances attached to netdevices. Per-net hash tables expose active tunnel lookup under RCU; updates are protected by RTNL and use `synchronize_net()` where endpoint keys move. Each tunnel owns parameters, fwmark, dst cache, optional PRL list, optional 6rd config, error counters/timestamps, and netdevice stats. The fallback `sit0` is per-netns and immutable across netns moves. No state is persistent after device/netns/module teardown.

## Dependencies and integration points
The driver depends on netdevice core, rtnetlink, xfrm4 tunnel registration, IPv4 routing and ICMP handling, IPv6 address and neighbor logic, PMTU helpers, ECN helpers, generic IP tunnel helpers, pernet operations, net namespace fallback tunnel policy, optional MPLS, optional 6rd, and L3 master scope handling. It exposes `MODULE_ALIAS_RTNL_LINK("sit")` and `MODULE_ALIAS_NETDEV("sit0")`.

## Risks and edge cases
Tunnel lookup priority must preserve exact local+remote matches before partial and wildcard matches. ISATAP PRL reads and deletes rely on RCU lifetime and `prl_count` consistency. 6rd spoofing checks can reject NATed protocol-41 traffic unless `only_dnatted()` finds an address on the tunnel device. PMTU logic must not emit impossible IPv6 MTUs below `IPV6_MIN_MTU`, and tunnel self-routing must detect loops. Updating endpoint keys must avoid concurrent readers seeing inconsistent hash placement. Netlink and ioctl paths must keep directionality of point-to-point versus multipoint devices consistent. Module cleanup waits for RCU callbacks because PRL entries can be freed asynchronously.

## Test signals
Coverage should create/delete/change SIT devices by `ip link` and ioctl, test duplicate local/remote/link keys, fallback `sit0` behavior, IPv6/IPv4/MPLS encapsulation where configured, PMTU too-big generation, ECN error logging, dst cache invalidation after link/fwmark changes, ISATAP PRL add/change/delete/get, 6rd parameter validation, 6to4 embedded destination selection, spoofed source/destination detection, L3 master ingress lookup, netns teardown, and module unregister failure cleanup paths.
