# sources/distributed-fs/ceph-client/net/ipv6/ip6_gre.c

Purpose: implements GRE, GRETAP, and ERSPAN tunneling over IPv6. It registers the IPv6 GRE protocol handler, rtnetlink link kinds, per-net fallback devices, tunnel lookup tables, xmit/receive paths, ioctl compatibility, and netdevice lifecycle.

Important APIs, types, and functions: core helpers include `ip6gre_tunnel_lookup()`, `ip6gre_tunnel_link()`, `ip6gre_tunnel_unlink()`, `ip6gre_tunnel_find()`, `ip6gre_tunnel_locate()`, `gre_rcv()`, `ip6gre_rcv()`, `ip6erspan_rcv()`, `ip6gre_tunnel_xmit()`, `ip6erspan_tunnel_xmit()`, `ip6gre_newlink()`, `ip6gre_changelink()`, `ip6erspan_newlink()`, `ip6erspan_changelink()`, `ip6gre_init()`, and `ip6gre_fini()`. Main state is `struct ip6gre_net` and `struct ip6_tnl`.

Control flow: receive parses GRE headers, strips the GRE header, dispatches ERSPAN or normal GRE, looks up a tunnel by local/remote/key/device type/link specificity, attaches collect-metadata dst info when configured, and hands the skb to `ip6_tnl_rcv()`. Transmit validates the payload, prepares flowi6/tclass/encap-limit from IPv4, IPv6, other payload, or metadata, builds GRE or ERSPAN headers, handles offloads, and calls `ip6_tnl_xmit()`, sending ICMP errors on MTU failures. Netlink create/change parses attributes, validates GRE/ERSPAN constraints, registers netdevices, configures MTU/headroom/features, and links tunnels into per-net hash buckets.

State and persistence: per-net state stores four hash tables for exact/wildcard remote/local matching, collect-metadata tunnel pointers, and fallback device. Tunnel devices hold parameters, dst cache, gro cells, sequence counter, encapsulation settings, and cached flow template. Module init registers pernet ops, protocol handler, and link ops; exit unregisters them.

Dependencies and integration points: depends on IPv6 tunnel core, GRE helpers, ERSPAN helpers, rtnetlink, netdevice ops, dst metadata, XFRM/route/PMTU helpers, ICMPv4/v6 error senders, GRO/GSO offload helpers, and namespace generic storage.

Risks: this snapshot includes duplicate declarations in `ip6gre_rcv()` and duplicate `.flags = INET6_PROTO_FINAL`, suggesting compile-risk source corruption. Normal operation is sensitive to tunnel lookup precedence, collect-metadata uniqueness, ERSPAN version-specific metadata length, and sequence/key flag validation. Teardown must unlink devices from hash/metadata pointers before dst cache cleanup. MTU/headroom calculations vary by GRE, GRETAP, ERSPAN, encap-limit, and metadata modes.

Test signals: module load/unload, creation/change/deletion of `ip6gre`, `ip6gretap`, and `ip6erspan` links; ioctl add/change/delete; keyed and keyless receive lookup precedence; collect-metadata RX/TX; IPv4/IPv6/other payload transmit; ERSPAN v1/v2 metadata; PMTU and ICMP error paths; fallback tunnel behavior; namespace teardown with moved tunnel devices; and offload/GSO tests with checksum and sequence flags.
