# sources/distributed-fs/ceph-client/net/ipv6/icmp.c

## Purpose
Implements ICMPv6 protocol receive, transmit, error generation, echo replies, upper-protocol notifications, per-net sysctls, and error-code conversion. It is the IPv6 control-message hub for PMTU, redirects, destination/time/parameter errors, neighbor discovery dispatch, ping sockets, and raw socket error reporting.

## Important APIs, Types, and Functions
Global state is per-CPU `ipv6_icmp_sk` control sockets. Main functions include `icmp6_send()`, `icmpv6_param_prob_reason()`, `ip6_err_gen_icmpv6_unreach()`, `icmpv6_echo_reply()`, `icmpv6_notify()`, `icmpv6_rcv()`, `icmpv6_flow_init()`, `icmpv6_init()`, `icmpv6_cleanup()`, `icmpv6_err_convert()`, and sysctl helpers `ipv6_icmp_sysctl_init()`/`ipv6_icmp_sysctl_table_size()`. Internal routing/rate helpers include `icmpv6_route_lookup()`, `icmpv6_xrlim_allow()`, and `icmpv6_global_allow()`.

## Control Flow
Receive validates XFRM policy, checksum, and header availability, updates ICMP stats, then dispatches echo requests to reply generation, echo replies to ping sockets, errors to `icmpv6_notify()`, and NDISC/MLD messages to their subsystems. `icmp6_send()` enforces RFC rules against replying to ICMP errors, multicast/anycast restrictions, source validity, global and per-destination rate limits, MIPv6 HAO source swapping, route/XFRM lookup, optional RFC4884/RFC5837 extensions, checksum construction, and pending-frame output. Notification parses inner extension headers, calls registered protocol error handlers, and reports to raw sockets.

## State and Persistence
Per-CPU raw control sockets carry outbound ICMP traffic and are temporarily rebound to the target net namespace under a socket spinlock. Per-net sysctls control ratelimit, echo ignore behavior, ratemask, anycast-as-unicast, and extension masks. Runtime stats are per-net/per-device ICMP/IP counters.

## Dependencies and Integration Points
Depends on IPv6 routing, XFRM, rawv6, ping, NDISC, MLD, SEG6 ICMP handling, netfilter conntrack attachment, l3mdev, sysctl, and socket/IP6 output APIs. Registers as final `IPPROTO_ICMPV6` inet6 protocol.

## Risks and Test Signals
Risks include recursive ICMP generation, rate-limit bypass or overdrop, wrong source/device selection for loopback/l3mdev/link-local traffic, extension object sizing, XFRM reverse-policy handling, and error notification for fragments/truncated packets. Test signals include checksum failures, echo sysctls, multicast/anycast echo behavior, PMTU and redirect delivery, RFC4884 extensions, protocol error callbacks, raw socket errors, per-net sysctl cloning, and namespace cleanup.
