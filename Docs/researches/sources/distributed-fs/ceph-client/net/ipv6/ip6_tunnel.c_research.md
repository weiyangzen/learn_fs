# sources/distributed-fs/ceph-client/net/ipv6/ip6_tunnel.c

## Purpose
This file implements the generic IPv6 tunnel netdevice driver for IPv4-over-IPv6, IPv6-over-IPv6, and optionally MPLS-over-IPv6 under the `ip6tnl` rtnetlink kind. It manages tunnel device lookup/creation, fallback `ip6tnl0`, encapsulation and decapsulation, PMTU/error propagation, optional collect-metadata mode, tunnel encapsulation offloads, ioctl compatibility, and module/per-net registration.

## Important APIs, Types, And Functions
The per-net state is `struct ip6_tnl_net`, which holds the fallback device, wildcard and remote/local hash tables, and one collect-metadata tunnel pointer. Tunnel devices use `struct ip6_tnl` and `struct __ip6_tnl_parm`.

Externally visible helpers include `ip6_tnl_parse_tlv_enc_lim()`, `ip6_tnl_get_cap()`, `ip6_tnl_rcv_ctl()`, `ip6_tnl_rcv()`, `ip6_tnl_xmit_ctl()`, `ip6_tnl_xmit()`, `ip6_tnl_change_mtu()`, `ip6_tnl_get_iflink()`, `ip6_tnl_encap_add_ops()`, `ip6_tnl_encap_del_ops()`, `ip6_tnl_encap_setup()`, and `ip6_tnl_get_link_net()`. Netdevice and rtnetlink operations are wired through `ip6_tnl_netdev_ops` and `ip6_link_ops`.

Core internal flows are `ip6_tnl_lookup()`, `ip6_tnl_locate()`, `ip6_tnl_link()`, `ip6_tnl_unlink()`, `ipxip6_rcv()`, `__ip6_tnl_rcv()`, `ipxip6_tnl_xmit()`, `ip6_tnl_start_xmit()`, `ip6_tnl_link_config()`, `ip6_tnl_update()`, and `ip6_tnl_siocdevprivate()`.

## Control Flow
Receive handlers are registered as XFRM IPv6 tunnel handlers for AF_INET, AF_INET6, and AF_MPLS. `ipxip6_rcv()` looks up a tunnel by outer source/destination and ingress link, validates configured protocol, runs XFRM input policy, checks local/remote address validity with `ip6_tnl_rcv_ctl()`, pulls the outer header, optionally creates metadata dst state, and calls `__ip6_tnl_rcv()`. The decap helper validates optional checksum/sequence flags, converts Ethernet-style tunnels with `eth_type_trans()` when needed, resets inner headers, applies DSCP/ECN decapsulation, scrubs cross-netns skb metadata, attaches collect-metadata dst, updates tunnel stats, and injects into GRO cells.

Transmit starts at `ip6_tnl_start_xmit()`, which accepts only IPv4, IPv6, or MPLS payloads and rejects obvious IPv6 source/tunnel conflicts. `ipxip6_tnl_xmit()` builds the outer `flowi6` either from collect-metadata tunnel info or from configured tunnel parameters, handles encapsulation-limit decrement for inner IPv6, chooses traffic class/flowlabel/fwmark policy, applies ECN encapsulation, and delegates to `ip6_tnl_xmit()`. `ip6_tnl_xmit()` resolves NBMA remotes when configured remote is any, optionally uses `dst_cache`, validates xmit capability, performs IPv6 route and XFRM lookup, selects a source address for collect-metadata mode if needed, checks routing loops and PMTU, reallocates headroom, applies optional tunnel encapsulation, pushes tunnel-encapsulation-limit options, builds the outer IPv6 header, and sends through `ip6tunnel_xmit()`.

Control-plane flow supports legacy `SIOC*Tunnel` ioctls and rtnetlink creation/change/delete. Newlink rejects duplicate endpoint/link tuples and allows a single collect-metadata tunnel. Changelink prevents most mutation of fallback `ip6tnl0`, updates encap state, relinks tunnel hash entries under RTNL with `synchronize_net()`, recomputes capabilities and MTU/headroom, and emits netdevice state changes.

## State And Persistence
Tunnel state is in memory per net namespace and per netdevice. Hash-table membership is RCU-protected and updated under RTNL. Each tunnel stores parameters, flow template, encapsulation settings, header lengths, sequence state, error counters/time, GRO cells, dst cache, and a netdevice tracker. No on-disk persistence exists; userspace recreates tunnels through rtnetlink or ioctls.

The fallback `ip6tnl0` is created per namespace when fallback tunnels are enabled and is netns-immutable. `collect_md_tun` is a singleton pointer per namespace. Module parameter `log_ecn_error` persists only as runtime module/sysfs state.

## Dependencies And Integration Points
The file integrates with rtnetlink `ip6tnl`, XFRM tunnel dispatch, IPv6 route lookup, PMTU update/redirect handling, DSCP/ECN helpers, MPLS optional build support, metadata dst/tunnel-info APIs, tunnel encapsulation operations in `ip6tun_encaps`, GRO cells, netdevice stats, and legacy `ip_tunnel_header_ops`. It calls `ip6_output`-side helpers such as `ip6_dst_hoplimit()` and `ip6_tnl_parse_tlv_enc_lim()` is reused by VTI-like paths.

## Risks And Edge Cases
Loop avoidance is spread across address conflict checks, local/remote address validation, destination device comparison, and encap-limit processing. NBMA remote resolution depends on existing skb dst/neighbour or IPv4 route gateway state and can fail as link failure. PMTU math must account for Ethernet tunnel devices, IPv6 header, optional tunnel encap header, tunnel header, and 8-byte tunnel encapsulation-limit option.

Collect-metadata mode bypasses some configured tunnel state and requires valid `skb_tunnel_info`; it rejects additional tunnel encap on transmit. Error handling for ICMPv6 converts outer errors to inner ICMP/ICMPv6 only for specific conditions and depends on enough quoted packet bytes. Hash relinking must use `synchronize_net()` so concurrent RCU receive lookups do not see freed or inconsistent chains.

## Test Signals
Useful signals include `ip -6 tunnel add/change/del` and legacy ioctl coverage; IPv4, IPv6, and MPLS payload transmit/receive; fallback `ip6tnl0` protocol-only mutation; collect-metadata VXLAN/OVS-like tunnel metadata paths; ECN error logging; tunnel encapsulation-limit decrement and zero-limit ICMPv6 parameter-problem; PMTU too-big propagation to inner IPv4/IPv6; dst-cache invalidation after parameter change; duplicate tunnel rejection; netns teardown; and route-loop detection when egress resolves back to the same tunnel device.
