# sources/distributed-fs/ceph-client/net/ipv6/datagram.c

## Purpose
Contains common IPv6 datagram socket support shared by UDP and raw sockets. It handles connected datagram routing state, IPv4-mapped connect compatibility, asynchronous ICMP/local error queue delivery, path-MTU notification delivery, receive ancillary control messages, send ancillary control parsing, and `/proc` socket display formatting.

## Important APIs, Types, and Functions
Core exported functions include `ip6_datagram_dst_update()`, `ip6_datagram_release_cb()`, `__ip6_datagram_connect()`, `ip6_datagram_connect()`, `ip6_datagram_connect_v6_only()`, `ipv6_icmp_error()`, `ipv6_local_error()`, `ipv6_local_rxpmtu()`, `ipv6_recv_error()`, `ipv6_recv_rxpmtu()`, `ip6_datagram_recv_ctl()`, `ip6_datagram_send_ctl()`, and `__ip6_dgram_sock_seq_show()`.

## Control Flow
Connect builds a `flowi6` from socket state, handles AF_INET fallback for IPv4-mapped destinations, resolves scope IDs, saves old peer state, performs route lookup with source selection, updates socket source/receive addresses, caches the dst, marks reuseport connection state, and sets the socket established. Error producers clone or allocate skbs with `sock_extended_err` metadata; consumers dequeue via `MSG_ERRQUEUE`, copy payload, attach timestamps, offender addresses, IPv6/IP control messages, and return copied length. Send control parsing iterates cmsghdrs for pktinfo, flowinfo, hop/destination/routing headers, hoplimit, traffic class, and dontfrag, validating sizes, capabilities, address ownership, and option ordering.

## State and Persistence
State is socket-local: cached dst/cork flow, `np->saddr`, `sk_v6_daddr`, receive source, flow label, `np->rxpmtu`, error queue skbs, and transient `ipcm6_cookie` options. No persistent storage exists.

## Dependencies and Integration Points
Depends on route lookup, flowlabel lookup, XFRM/security flow classification, IPv4 datagram fallback, anycast address validation, IPv6 extension option formats, socket error queue helpers, timestamp/cmsg code, and procfs seq output. UDP/raw send paths call `ip6_datagram_send_ctl()`.

## Risks and Test Signals
Risks include inconsistent socket state after failed connect, incorrect scope/device checks, ancillary option length bugs, capability bypass for raw extension headers, stale dst refresh behavior, and mismatched RFC4884/error cmsg formatting. Test signals include v4-mapped connect, scoped link-local connect, pktinfo source validation including anycast, route invalidation release callbacks, `MSG_ERRQUEUE` reads, `IPV6_RECVPATHMTU`, old RFC2292 cmsgs, and malformed cmsghdr rejection.
