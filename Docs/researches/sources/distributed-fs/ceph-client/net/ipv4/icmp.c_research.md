# sources/distributed-fs/ceph-client/net/ipv4/icmp.c

## Purpose
`icmp.c` implements IPv4 ICMP send, receive, error delivery, echo/timestamp replies, rate limiting, RFC 4884/5837 extensions, ping socket delivery, NAT-aware error sends, and per-net ICMP sysctl defaults.

## Important APIs, Types, And Functions
`struct icmp_bxm` carries reply build state. `icmp_err_convert` maps destination-unreachable codes to socket errno/fatal behavior. `struct icmp_control` and `icmp_pointers` dispatch received ICMP types.

Important exported or externally used functions include `__icmp_send`, `icmp_ndo_send`, `icmp_rcv`, `icmp_err`, `icmp_out_count`, `icmp_global_allow`, `icmp_global_consume`, `icmp_build_probe`, `ip_icmp_error_rfc4884`, and `icmp_init`. Internal helpers include `icmp_xmit_lock`, `icmpv4_global_allow`, `icmpv4_xrlim_allow`, `icmp_route_lookup`, `icmp_ext_append`, `icmp_socket_deliver`, `icmp_unreach`, `icmp_redirect`, `icmp_echo`, and `icmp_timestamp`.

## Control Flow
Outgoing errors through `__icmp_send` validate route/device context, reject replies to non-host, broadcast/multicast, non-initial fragments, and ICMP errors about ICMP errors, then apply global and peer rate limits. It selects source address, echoes IP options, builds route lookup state, runs XFRM-aware route lookup, caps payload to the RFC 576-byte limit, optionally appends ICMP extensions, and emits the packet through a per-CPU raw ICMP control socket. Echo and timestamp replies use `icmp_reply`, which performs similar routing and rate limiting for replies.

Incoming `icmp_rcv` first performs XFRM policy checks, validates checksum, pulls the ICMP header, updates SNMP counters, handles extended echo separately, enforces broadcast/multicast rules, delivers echo replies to ping sockets, discards unknown types, and dispatches known types through `icmp_pointers`. Destination unreachable, time exceeded, source quench, and parameter problem messages are handled by `icmp_unreach`, which validates embedded IP header, handles PMTU update policy, rejects bogus broadcast errors, and delivers the error to raw sockets and protocol error handlers. Redirects are delivered through `icmp_socket_deliver`; echo and timestamp requests build replies.

RFC 4884 parsing reports extension offsets and invalid checksums to sockets. RFC 5837 interface information objects can be appended to generated errors when enabled by sysctl. Extended echo probe support resolves devices by name, index, IPv4, or IPv6 address and returns interface status bits.

## State And Persistence
The file owns one per-CPU raw ICMP socket in `ipv4_icmp_sk`, initialized once for init net and temporarily rebound to the target net namespace while sending. Per-net ICMP sysctls, token bucket stamp/credit, and peer rate limiting state govern emission. No packet state persists beyond skb lifetime except socket error delivery and PMTU/redirect updates in routing subsystems.

## Dependencies And Integration Points
It integrates with IPv4 routing, XFRM, netfilter/NAT conntrack, raw sockets, ping sockets, protocol `err_handler`s in `inet_protos`, PMTU and redirect handlers, SNMP MIB counters, tracepoints, L3 master devices, IP options, security flow classification, netdevice lookup, IPv6 helpers for extended echo address queries, and per-net sysctl storage.

## Risks
ICMP has many RFC and security guardrails. Risks include replying when forbidden, rate-limit bypass or over-throttling, route lookup with stale or local routes, nested ICMP error loops, insufficient embedded-header validation before protocol delivery, checksum/extension length errors, and per-CPU socket locking recursion during link failures. Extended echo has device reference and input validation risks.

## Test Signals
Signals include ICMP send suppression for multicast, broadcast, fragments, and ICMP-error loops; PMTU behavior for all `ip_no_pmtu_disc` modes; global and peer rate-limit counters; echo ignore sysctls; broadcast ping rules; timestamp replies; ping socket delivery; raw/protocol error delivery to TCP/UDP; NAT-adjusted `icmp_ndo_send`; RFC 4884 extension validation; RFC 5837 interface extension emission; XFRM policy handling; and per-net sysctl default checks at namespace creation.
