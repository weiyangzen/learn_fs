# sources/distributed-fs/ceph-client/net/ipv6/ip6_vti.c

## Purpose
This file implements the IPv6 virtual tunnel interface driver, `vti6`, which binds IPv6 tunnel netdevices to XFRM/IPsec tunnel states. It provides policy-mark based transmit and receive paths for ESP, AH, IPComp, and optional IPv6 tunnel protocol handling, plus rtnetlink/ioctl configuration and per-net fallback device management.

## Important APIs, Types, And Functions
Per-net state is `struct vti6_net`, which contains fallback `ip6_vti0` and endpoint hash tables. The driver reuses `struct ip6_tnl` and `struct __ip6_tnl_parm` from the IPv6 tunnel infrastructure for parameters, keys, link, netdevice, and hash chaining.

Important functions include `vti6_tnl_lookup()`, `vti6_locate()`, `vti6_tnl_link()`, `vti6_tnl_unlink()`, `vti6_input_proto()`, `vti6_rcv()`, `vti6_rcv_cb()`, `vti6_state_check()`, `vti6_xmit()`, `vti6_tnl_xmit()`, `vti6_err()`, `vti6_link_config()`, `vti6_update()`, `vti6_siocdevprivate()`, and rtnetlink handlers `vti6_newlink()`, `vti6_changelink()`, and `vti6_dellink()`.

XFRM registration uses `xfrm6_protocol` handlers for ESP, AH, and COMP with high priority, and, when reachable, `xfrm6_tunnel` handlers for IPv6 tunnel traffic. Netdevice operations are in `vti6_netdev_ops`, and rtnetlink kind is `"vti6"`.

## Control Flow
Receive protocol handlers call `vti6_input_proto()`, which looks up a matching tunnel by outer source/destination, validates the tunnel protocol, runs XFRM input policy, checks local/remote receive capability through `ip6_tnl_rcv_ctl()`, stores the matched tunnel in `XFRM_TUNNEL_SKB_CB`, sets SPI family/destination offset metadata, and calls `xfrm_input()`. After XFRM processing, `vti6_rcv_cb()` validates inner mode/family, temporarily replaces `skb->mark` with the tunnel input key for policy check, scrubs cross-netns metadata, moves the skb to the tunnel device, and updates rx stats.

Transmit starts from `vti6_tnl_xmit()`, which accepts IPv6 and IPv4 payloads, clears protocol-specific skb control blocks, decodes the inner flow, overrides `flowi_mark` with the tunnel output key, and calls `vti6_xmit()`. `vti6_xmit()` ensures there is an skb dst by doing route lookup through the tunnel device if needed, performs `xfrm_lookup_route()`, verifies that the resulting XFRM state is IPv6 tunnel mode and matches configured endpoints, validates xmit capability, rejects local routing loops, enforces PMTU with ICMP/ICMPv6 errors, scrubs the skb, assigns the transformed dst/dev, calls `dst_output()`, and accounts transmit stats.

Control-plane flow mirrors `ip6_tunnel.c` but with VTI-specific parameters: local, remote, link, input key, output key, fwmark, and protocol fixed to IPv6. Ioctls support `SIOCGETTUNNEL`, add/change/delete, and rtnetlink supports new/change/delete/fill_info. Updates relink the tunnel hash under RTNL with `synchronize_net()` and recompute capabilities/MTU.

## State And Persistence
VTI state is runtime-only per net namespace and per netdevice. The tunnel hash tables are RCU-read and RTNL-updated. Each tunnel stores local/remote endpoint addresses, input/output keys, optional link, protocol, fwmark, netdevice tracker, and cached dst state inherited from `struct ip6_tnl`. XFRM security associations and policies are separate system state managed by XFRM; VTI only selects them via mark and endpoint checks.

The fallback device `ip6_vti0` is created per namespace when fallback tunnels are enabled. No settings are persisted by the driver itself.

## Dependencies And Integration Points
`ip6_vti.c` depends on XFRM state/policy lookup and protocol registration, IPv6 tunnel capability helpers from `ip6_tunnel.c`, IPv4 and IPv6 route lookup, ICMP/ICMPv6 PMTU reporting, rtnetlink tunnel attributes, netdevice notifier lifecycle through pernet exit, and generic tunnel header ops. It integrates with userspace `ip link add type vti6`, legacy tunnel ioctls, and IPsec policy/SAs configured outside this file.

## Risks And Edge Cases
The transmit path depends on an XFRM tunnel-mode state; if route lookup returns `DST_XFRM_QUEUE`, packets can queue before state validation. Mark handling is security-sensitive: output uses `o_key`, receive policy check uses `i_key`, and `vti6_err()` looks up XFRM state using the output key. PMTU behavior differs for IPv4 payloads depending on DF, while IPv6 payloads always get packet-too-big with minimum MTU clamping.

Tunnel lookup ignores link in comparison, unlike generic ip6tnl, so endpoint-only matching governs receive. RCU hash relinking must remain synchronized with readers. Fallback devices are deletable only through namespace teardown, while non-fallback tunnel conflicts must be rejected by endpoint tuples. The route-loop check only catches direct `dst_dev == dev`.

## Test Signals
Relevant tests include creating/changing/deleting `vti6` links through rtnetlink and ioctl, duplicate endpoint rejection, ESP/AH/IPComp inbound dispatch to the right tunnel, input/output key policy selection, IPv4 and IPv6 payload transmit through matching XFRM tunnel SAs, PMTU too-big behavior for IPv4 DF and IPv6, XFRM state mismatch drop, route-loop detection, fallback `ip6_vti0` behavior, netns teardown, and lockdep/RCU checks during concurrent traffic and tunnel change.
