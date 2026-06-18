# sources/distributed-fs/ceph-client/net/ipv4/ip_vti.c

## Purpose
Implements IPv4 Virtual Tunnel Interface devices for IPsec/XFRM. VTI maps inbound ESP/AH/IPComp/IPIP packets to tunnel netdevices, uses tunnel keys as policy marks, transmits inner IPv4/IPv6 packets through XFRM tunnel-mode states, handles ICMP errors for associated states, and exposes `vti` rtnetlink and legacy tunnel controls.

## APIs, Types, and Functions
The module is registered through `module_init(vti_init)` and `module_exit(vti_fini)`. Important functions are `vti_input()`, `vti_rcv()`, `vti_rcv_cb()`, `vti_state_check()`, `vti_xmit()`, `vti_tunnel_xmit()`, `vti4_err()`, `vti_tunnel_ctl()`, `vti_tunnel_init()`, `vti_init_net()`, `vti_netlink_parms()`, `vti_newlink()`, `vti_changelink()`, and `vti_fill_info()`. It registers `xfrm4_protocol` handlers for ESP, AH, and IPComp, optional `xfrm_tunnel` handlers for IPIP/IPIP6, `pernet_operations`, and `rtnl_link_ops` kind `vti`.

## Control Flow
Inbound protocol handlers set XFRM SPI metadata and call `vti_input()`, which looks up a keyless VTI tunnel by outer source/destination/link, checks inbound XFRM policy, stores the tunnel in `XFRM_TUNNEL_SKB_CB`, optionally switches `skb->dev`, and enters `xfrm_input()`. After XFRM decapsulation, `vti_rcv_cb()` validates inner mode/family, temporarily applies the tunnel input key as `skb->mark` for policy check, scrubs cross-net packets, assigns the tunnel device, and updates rx stats.

Transmit starts in `vti_tunnel_xmit()`, validates inner IPv4/IPv6, decodes an XFRM flow, overrides the mark with the tunnel output key, and calls `vti_xmit()`. `vti_xmit()` obtains or builds a route, performs `xfrm_lookup_route()`, verifies a tunnel-mode AF_INET state matches configured endpoints, checks MTU and sends ICMP/ICMPv6 errors when needed, then outputs through the XFRM dst. Error handling maps ICMP frag-needed and redirects back to XFRM state lookup using protocol SPI and output key mark.

## State and Persistence
Per-net tunnel state is supplied by the generic `ip_tunnel` library under `vti_net_id`, with fallback device `ip_vti0`. Tunnel keys persist in `parms.i_key` and `parms.o_key` and are used as policy marks rather than GRE keys on the wire. The module persists protocol registrations, optional tunnel handlers, rtnl link ops, fwmark, netdevice stats, and per-device dst retention through `netif_keep_dst()`.

## Dependencies and Integration
VTI sits between netdevices and XFRM: it depends on `ip_tunnel_lookup()`, pernet tunnel lifecycle, XFRM input/output/policy/state lookup, ESP/AH/IPComp headers, IPv4/IPv6 route decoding, ICMP/ICMPv6 PMTU reporting, rtnetlink, namespace capabilities, and legacy private ioctl conversion through `ip_tunnel_siocdevprivate()`.

## Risks
Risks include policy mark confusion between input and output keys, accepting packets for the wrong tunnel when endpoints are wildcarded, XFRM state mismatch causing blackholes, MTU handling for IPv6 minimums, SPI parsing from short ICMP payloads, registration unwind ordering, legacy GRE key compatibility conversion, and receive callback behavior when `x->sel.family` is unspecified.

## Test Signals
Tests should create VTI devices with local/remote/key/fwmark combinations, install matching and nonmatching XFRM tunnel states/policies, verify inbound ESP/AH/IPComp decapsulation and mark-based policy, transmit IPv4 and IPv6 inner packets, exercise PMTU and redirects, cover rtnetlink dump/change and SIOC tunnel controls, and validate namespace teardown plus module registration failure unwind.
