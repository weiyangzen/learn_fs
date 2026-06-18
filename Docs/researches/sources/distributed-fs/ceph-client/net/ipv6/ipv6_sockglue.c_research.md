# sources/distributed-fs/ceph-client/net/ipv6/ipv6_sockglue.c

## Purpose
This file implements the IPv6 socket option interface: `setsockopt()` and `getsockopt()` handling for SOL_IPV6, router-alert raw socket registration, sticky extension-header options, multicast and source-filter APIs, packet-info and ancillary option state, flowlabel/IPsec policy delegation, IPv4 address-form conversion, and netfilter sockopt fallback.

## Important APIs, Types, And Functions
Global router-alert state is `ip6_ra_chain` protected by `ip6_ra_lock`; `ip6_min_hopcount` is a static key enabled when any socket sets a positive minimum hop count. Exported entry points are `ipv6_setsockopt()`, `ipv6_getsockopt()`, `do_ipv6_setsockopt()`, `do_ipv6_getsockopt()`, `ip6_ra_control()`, and `ipv6_update_options()`.

Multicast helpers include `ipv6_mcast_join_leave()`, `compat_ipv6_mcast_join_leave()`, `do_ipv6_mcast_group_source()`, `ipv6_set_mcast_msfilter()`, `compat_ipv6_set_mcast_msfilter()`, `ipv6_get_msfilter()`, and `compat_ipv6_get_msfilter()`. Sticky extension-header handling is in `ipv6_set_opt_hdr()` and `ipv6_getsockopt_sticky()`.

The code mutates `struct ipv6_pinfo` fields such as hop limits, multicast interface/hops, unicast interface, PMTU discovery, fragment size, traffic class, source preferences, sticky packet info, receive option bitfields, and RCU-managed `ipv6_txoptions`.

## Control Flow
`ipv6_setsockopt()` delegates SOL_IP options for non-raw sockets to IPv4, rejects non-SOL_IPV6, calls `do_ipv6_setsockopt()`, and on generic `-ENOPROTOOPT` tries netfilter IPv6 sockopts except for XFRM/IPsec policy options. `do_ipv6_setsockopt()` first handles multicast-routing options through `ip6_mroute_setsockopt()`. It then processes several lockless per-socket options with direct `WRITE_ONCE()` or bit updates, including hop limits, multicast loop/hops/all/interface, PMTU discovery, MTU/frag size, autoflowlabel, dontfrag, receive errors, router-alert isolate, min hop count, flowinfo send, unicast interface, and address preferences.

Options that require socket serialization take the socket lock and recheck that the socket is still AF_INET6. The locked switch handles `IPV6_ADDRFORM` conversion of connected v4-mapped TCP/UDP sockets to IPv4, v6-only, receive ancillary toggles, traffic class, transparent/freebind, original destination, sticky extension headers, packet-info, legacy 2292 packet options, multicast membership/source filters, anycast membership, router alert, flowlabel manager, XFRM/IPsec policy, and receive fragment size.

Sticky extension-header updates validate privilege for hop-by-hop and destination options, option length and alignment, routing header type, and SRH format, then replace the socket's RCU txoptions through `ipv6_update_options()`, which also refreshes TCP MSS/ext header length for connected sockets. Router alert registration adds or removes the raw socket from `ip6_ra_chain` and holds/drops a socket reference.

`ipv6_getsockopt()` mirrors the level/fallback logic, calls `do_ipv6_getsockopt()`, and optionally falls back to netfilter. Getsockopt handles multicast routing, multicast source filters, legacy packet options, current MTU/path MTU, sticky options, flowlabel lookup, and the scalar socket fields. It writes truncated integer lengths according to the supplied optlen.

## State And Persistence
State is socket-local except for `ip6_ra_chain`, `ip6_min_hopcount`, and multicast-routing state delegated to `ip6mr.c`. Socket state lives in `struct ipv6_pinfo`, `struct inet_sock`, `struct sock` flags, multicast/anycast membership lists, flowlabel tables, XFRM policies, and RCU-managed `struct ipv6_txoptions`. No state persists after socket close, although external XFRM policies or flowlabels may have their own lifetimes.

`IPV6_ADDRFORM` permanently converts an eligible established v4-mapped TCP/UDP IPv6 socket to IPv4 protocol/socket ops and cleans up IPv6 multicast/anycast/options. Router-alert registration holds a reference on the raw socket until removed.

## Dependencies And Integration Points
The file integrates with IPv6 datagram ancillary control parsing/emission, multicast listener/source-filter code, anycast membership, IPv6 flowlabel manager, XFRM user policy, TCP MSS recalculation, UDP pending state, netfilter sockopts, IPv4 socket ops for `IPV6_ADDRFORM`, netdevice/l3mdev validation for interface options, Segment Routing Header validation, PSP overhead, and multicast routing options from `ip6mr.c`. `ip6_output.c` reads `ip6_ra_chain` for forwarded router-alert delivery.

## Risks And Edge Cases
The option surface is broad and compatibility-sensitive. Lockless options can race with address-form conversion; the code explicitly rechecks family after taking the lock for locked options, but some UDP send and PMTU paths are documented as still having races after disabling IPv6 options during conversion. Sticky option memory accounting uses `sk_omem_alloc` and txoption refcounts and must release old options after replacement.

Multicast filter APIs must defend against optlen overflows, compat layout differences, and `sysctl_mld_max_msf` limits. `IPV6_UNICAST_IF` uses network-byte-order integer API semantics, validates device existence, and conflicts with bound devices. Router-alert registration is raw-socket-only and duplicate registrations return `-EADDRINUSE`; removal with no entry returns `-ENOBUFS`, matching legacy behavior. Privileged options require namespace capabilities.

## Test Signals
Useful tests include scalar set/get for hop limits, PMTU discovery, multicast loop/hops/all/interface, unicast interface, tclass, transparent/freebind permissions, dontfrag, autoflowlabel, min hop count static key, receive error queue purge, receive ancillary toggles, sticky hop/dst/routing/SRH options, legacy 2292 packet options, multicast join/leave and source filters in native and compat modes, anycast join/leave, router-alert registration and forwarded delivery, flowlabel manager get/set, XFRM/IPsec policy permission paths, `IPV6_ADDRFORM` conversion of connected v4-mapped TCP/UDP sockets, and netfilter sockopt fallback.
