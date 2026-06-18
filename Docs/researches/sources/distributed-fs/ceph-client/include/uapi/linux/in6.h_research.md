
# sources/distributed-fs/ceph-client/include/uapi/linux/in6.h

## Purpose

`in6.h` defines IPv6 socket UAPI types, address structures, flow-label management, extension-header constants, socket option numbers, PMTU modes, source-address preferences, and multicast request layout. The complete 302-line file was read.

## Important APIs, Types, and Functions

Key types are `in6_addr`, `sockaddr_in6`, `ipv6_mreq`, and `in6_flowlabel_req`. Constants include flow-label actions/flags/share values, `IPV6_FLOWINFO_*`, obsolete priority values, extension header protocol numbers, TLV option IDs including IOAM, many `IPV6_*` socket options, PMTU discovery modes, RFC5014 source preference flags, original-destination/freebind/transparent options, and multicast option references shared with IPv4.

## Control Flow

No local flow is defined. IPv6 sockets and routing code use these values during bind/connect, flow-label management, setsockopt/getsockopt, ancillary data, multicast membership, PMTU handling, and extension-header processing.

## State and Persistence Behavior

Socket options, flow labels, multicast membership, and address preferences are kernel state. The header defines stable layouts and option IDs.

## Dependencies and Integration Points

It includes `linux/types.h` and `linux/libc-compat.h`, and coordinates with libc, AF_INET6 sockets, IPv6 routing, multicast, netfilter, IOAM TLVs, XFRM/IPsec, and advanced IPv6 API consumers.

## Risks and Edge Cases

Conditional libc-compat definitions and address union aliases are ABI-sensitive. Risks include flowinfo host/network byte-order confusion, scope-id handling, obsolete priority constants, PMTU mode semantics, and option-number gaps shared with netfilter/multicast routing.

## Test Signals

IPv6 socket option tests, flow-label manager tests, multicast join/leave tests, scope-id binding tests, ancillary data tests, libc include compatibility tests, and struct layout checks on 32/64-bit builds.
