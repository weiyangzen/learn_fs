# sources/distributed-fs/ceph-client/net/sctp/ipv6.c

## Purpose
`ipv6.c` provides SCTP's IPv6 address-family and protocol-family implementation. It mirrors IPv4 support in `protocol.c` but handles IPv6 route lookup, address validation, link-local scope IDs, v4-mapped address behavior for dual-stack sockets, ICMPv6 errors, UDP encapsulation, proc address dumping, and registration with the IPv6 protocol and socket layers.

## Important APIs, Types, And Functions
Public registration hooks are `sctp_v6_pf_init()`, `sctp_v6_pf_exit()`, `sctp_v6_protosw_init()`, `sctp_v6_protosw_exit()`, `sctp_v6_add_protocol()`, `sctp_v6_del_protocol()`, and UDP error entry `sctp_udp_v6_err()`. The core AF/PF tables are `sctp_af_inet6` and `sctp_pf_inet6`.

Important helpers include `sctp_inet6addr_event()`, `sctp_v6_err()`, `sctp_v6_err_handle()`, `sctp_v6_xmit()`, `sctp_v6_get_dst()`, `sctp_v6_get_saddr()`, `sctp_v6_copy_addrlist()`, `sctp_v6_from_skb()`, `sctp_v6_from_addr_param()`, `sctp_v6_cmp_addr()`, `sctp_v6_available()`, `sctp_v6_addr_valid()`, `sctp_v6_addr_to_user()`, `sctp_inet6_bind_verify()`, `sctp_inet6_send_verify()`, and `sctp_getname()`.

## Control Flow
IPv6 address notifier events add/remove `sctp_sockaddr_entry` records from the per-net local address list under `local_addr_lock`, mark entries invalid before RCU removal, and enqueue ASCONF address-management events through `sctp_addr_wq_mgmt()`. Receive registration uses `sctp6_rcv()`, which clears encapsulation metadata and delegates to common `sctp_rcv()`.

ICMPv6 handling resets skb headers to the embedded SCTP packet, calls common `sctp_err_lookup()` for verification-tag validation and association lookup, then maps packet-too-big to PMTU updates, unknown-next-header to proto-unreachable handling, redirects to route redirect handling, and other ICMPv6 errors to socket hard/soft errors.

Transmit uses `sctp_v6_xmit()`. It applies DSCP overrides, ECN marking, PMTUD `ignore_df`, and either calls `ip6_xmit()` for native SCTP or wraps SCTP in UDP with `udp_tunnel6_xmit_skb()` when both local and remote encapsulation ports are set. Route selection in `sctp_v6_get_dst()` prefers a route-selected source address that is in the association bind list; if that fails, it walks bound IPv6 source addresses by scope and prefix match, taking link-local scope and flowlabel options into account.

## State And Persistence
IPv6 state is in static AF/PF tables, protosw registrations, the IPv6 address notifier, route/dst caches on transports, and per-net local address entries. No data is persisted outside memory. Socket-visible behavior persists through socket options such as `IPV6_V6ONLY`, `SCTP_I_WANT_MAPPED_V4_ADDR`, IPv6 tx options, flowlabel settings, DSCP, PMTUD flags, and UDP encapsulation ports.

## Dependencies And Integration Points
The file integrates with IPv6 core protocol registration, `inet6_register_protosw()`, `proto_register(&sctpv6_prot)`, IPv6 address notifiers, route lookup, flow labels, extension options, ICMPv6, UDP tunnels, dual-stack SCTP socket operations, and common SCTP input/output helpers. It also consumes the IPv4 AF table when translating v4-mapped addresses.

## Risks
Subtle risks include v4-mapped address policy mismatches, link-local addresses without scope IDs, route source selection outside the association bind list, stale dst cookies, ICMPv6 spoofing if common validation is bypassed, UDP-encapsulation checksum/GSO metadata mistakes, and notifier races with RCU readers of the local address list.

## Test Signals
Exercise native IPv6 SCTP, dual-stack sockets with and without `IPV6_V6ONLY`, v4-mapped address conversion, link-local bind/send validation with scope IDs, IPv6 address add/delete notifier updates, ASCONF auto-address queueing, ICMPv6 packet-too-big PMTU changes, unknown-next-header abort behavior, UDP-encapsulated IPv6 SCTP, flowlabel use, proc address formatting, and protosw/protocol register-unregister failure rollback.
