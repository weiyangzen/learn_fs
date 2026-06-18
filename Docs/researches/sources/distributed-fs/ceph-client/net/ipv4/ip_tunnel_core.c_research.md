# sources/distributed-fs/ceph-client/net/ipv4/ip_tunnel_core.c

## Purpose
Provides shared tunnel primitives not tied to one IPv4 tunnel netdevice: outer IPv4 header transmit, tunnel header pull/offload preparation, metadata reply construction, PMTU checking with synthetic ICMP/ICMPv6 replies for bridged tunnels, lightweight tunnel netlink state parsing/filling for IPv4 and IPv6 encap routes, metadata static-key accounting, protocol parsing, and common netlink parameter extraction.

## APIs, Types, and Functions
Exports the global encap operation tables `iptun_encaps` and `ip6tun_encaps`, plus `iptunnel_xmit()`, `__iptunnel_pull_header()`, `iptunnel_metadata_reply()`, `iptunnel_handle_offloads()`, `skb_tunnel_check_pmtu()`, `ip_tunnel_core_init()`, `ip_tunnel_metadata_cnt`, `ip_tunnel_need_metadata()`, `ip_tunnel_unneed_metadata()`, `ip_tunnel_parse_protocol()`, `ip_tunnel_header_ops`, `ip_tunnel_netlink_encap_parms()`, and `ip_tunnel_netlink_parms()`. Local lwtunnel handlers build/fill/compare `struct lwtunnel_state` containing `struct ip_tunnel_info` and options for Geneve, VXLAN GBP, and ERSPAN.

## Control Flow
`iptunnel_xmit()` enforces recursion limits, scrubs packets for cross-net transmission, installs a fresh outer IPv4 header, selects an ID, calls `ip_local_out()`, and updates tunnel tx stats. `__iptunnel_pull_header()` removes outer tunnel bytes, determines inner protocol including Ethernet payloads, clears VLAN/queue/hash state, scrubs, and normalizes offloads. `iptunnel_handle_offloads()` marks encapsulation and updates GSO type or disables risky checksum offload assumptions.

PMTU checking compares inner packet length against destination MTU minus headroom, updates PMTU, and when requested rewrites the original skb into an ICMPv4 fragmentation-needed or ICMPv6 packet-too-big response while avoiding invalid sources, multicast/broadcast, fragments, and ICMP error loops. LWT build functions parse nested netlink attributes, validate option families are not mixed, allocate state and dst caches, fill keys/options/flags, and later serialize or compare the same state.

## State and Persistence
Persistent state includes the global RCU encap op arrays, registered lwtunnel encap ops for `LWTUNNEL_ENCAP_IP` and `LWTUNNEL_ENCAP_IP6`, optional per-lwtunnel dst caches, and the `ip_tunnel_metadata_cnt` static key tracking whether metadata tunnel users exist. Most other state is transient skb rewriting, netlink parse output, and `ip_tunnel_info` instances stored in lwtunnel route state.

## Dependencies and Integration
Integrates with IPv4 output, dst/routing, lwtunnel infrastructure, static keys, Geneve/VXLAN/ERSPAN metadata formats, ICMP and ICMPv6, Ethernet header helpers, VLAN/offload/GSO helpers, XFRM/tunnel headers, netlink attribute policy validation, and frontend devices that use `ip_tunnel_header_ops` and metadata mode.

## Risks
Risk centers on destructive skb rewriting in PMTU reply builders, bounds validation of variable-length Geneve options, mutually exclusive option-family enforcement, checksum correctness for synthetic ICMPv6, recursion accounting balance, GSO/offload flag combinations, dst-cache lifetime in lwtunnel state, and memcmp-based lwtunnel comparison over fields that must remain fully initialized.

## Test Signals
Useful coverage includes lwtunnel route add/dump/compare for IPv4 and IPv6 encap, Geneve/VXLAN/ERSPAN option validation including malformed nesting and max option length, PMTU reply synthesis for bridged IPv4/IPv6 payloads, GSO and non-GSO offload transitions, tunnel recursion-limit drops, metadata static-key refcounting, and protocol parsing on valid/invalid IPv4/IPv6 network headers.
