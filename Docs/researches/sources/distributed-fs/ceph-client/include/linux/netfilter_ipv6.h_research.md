# sources/distributed-fs/ceph-client/include/linux/netfilter_ipv6.h

Purpose: Declares IPv6-specific netfilter helpers for address checks, routing, bridge fragmentation, route repair, TCP syncookie sequence helpers, and hop-by-hop length validation.

Important APIs, types, and functions: Key exports are `nf_ipv6_chk_addr()`, `__nf_ip6_route()`, `nf_ip6_route()`, `br_ip6_fragment()`, `nf_br_ip6_fragment()`, `ip6_route_me_harder()`, `nf_ip6_route_me_harder()`, `nf_ipv6_cookie_init_sequence()`, `nf_cookie_v6_check()`, and `nf_ip6_check_hbh_len()`. Detected source surface: 121 lines; includes `net/addrconf.h`, `net/netfilter/ipv6/nf_defrag_ipv6.h`, `net/tcp.h`, `uapi/linux/netfilter_ipv6.h`; macros `__LINUX_IP6_NETFILTER_H`; structs `flowi`, `in6_addr`, `ip6_rt_info`, `nf_bridge_frag_data`, `nf_queue_entry`, `sk_buff`; enums none; typedefs none; function-like declarations/helpers `__cookie_v6_check`, `__cookie_v6_init_sequence`, `__nf_ip6_route`, `br_ip6_fragment`, `ip6_route_me_harder`, `ipv6_chk_addr`, `nf_br_ip6_fragment`, `nf_cookie_v6_check`, `nf_ip6_check_hbh_len`, `nf_ip6_checksum`, `nf_ip6_ext_hdr`, `nf_ip6_route`, `nf_ip6_route_me_harder`, `nf_ipv6_chk_addr`, `nf_ipv6_cookie_init_sequence`.

Control flow: Netfilter users call these helpers after modifying IPv6 packets, when routing queued packets, when bridge hooks need fragmentation, or when validating TCP syncookies through IPv6 headers.

State and persistence behavior: No global state is defined; helpers operate on net namespaces, dst pointers, sockets, skbs, and parsed headers.

Dependencies and integration points: Depends on IPv6 UAPI, TCP helpers, addrconf, defrag, bridge fragments, and route APIs.

Risks and test signals: Risks are extension header length errors, reroute failures after NAT/mark changes, and fragmentation behavior across bridge hooks. Test IPv6 NAT/mangle paths, HBH headers, syncookies, fragmented bridged traffic, and disabled IPv6 builds.
