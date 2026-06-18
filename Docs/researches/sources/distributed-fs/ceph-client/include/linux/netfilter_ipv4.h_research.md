# sources/distributed-fs/ceph-client/include/linux/netfilter_ipv4.h

Purpose: Declares IPv4-specific netfilter route and checksum helpers used after packet mangling or queue reinjection.

Important APIs, types, and functions: Important types/APIs are `struct ip_rt_info`, `ip_route_me_harder()`, `nf_ip_route()`, and `nf_ip_checksum()`. Detected source surface: 41 lines; includes `uapi/linux/netfilter_ipv4.h`; macros `__LINUX_IP_NETFILTER_H`; structs `flowi`, `ip_rt_info`, `nf_queue_entry`; enums none; typedefs none; function-like declarations/helpers `ip_route_me_harder`, `nf_ip_checksum`, `nf_ip_route`.

Control flow: After a hook modifies an IPv4 packet, callers reroute it with `ip_route_me_harder()` or `nf_ip_route()` and recompute/check checksums with `nf_ip_checksum()` as needed.

State and persistence behavior: The header owns no persistent state; route results are dst entries attached to skbs or returned through pointers.

Dependencies and integration points: Depends on UAPI IPv4 netfilter, routing flow keys, sk_buff, and IP checksum helpers.

Risks and test signals: Risks are stale route cache after NAT/mark changes and checksum coverage mistakes. Test DNAT/SNAT, policy routing, local output reroute, and fragmented packets.
