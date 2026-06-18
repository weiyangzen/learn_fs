# sources/distributed-fs/ceph-client/net/ipv4/datagram.c

## Purpose
`datagram.c` contains common IPv4 datagram socket connect and route-cache refresh logic used by UDP and raw-style datagram protocols.

## Important APIs, types, and functions
It exports `__ip4_datagram_connect()`, `ip4_datagram_connect()`, and `ip4_datagram_release_cb()`.

## Control flow
`__ip4_datagram_connect()` validates a `sockaddr_in`, resets the cached dst, chooses an output interface and source address from bound-device, multicast, or unicast socket settings, performs `ip_route_connect()`, rejects broadcast routes unless `SOCK_BROADCAST` is enabled, updates destination/source address and port fields, rehashes if the receive source address becomes known, marks reuseport sockets as connected, sets `TCP_ESTABLISHED`, picks a transmit hash, randomizes the IP ID base, and installs the route dst. `ip4_datagram_connect()` wraps that sequence with socket locking. `ip4_datagram_release_cb()` runs when releasing the socket lock; if the cached dst is obsolete and fails validation, it builds a flow from current inet state, performs a new route lookup, and updates the socket dst cache with `sk_dst_set()`.

## State and persistence
State changes are per-socket: `inet_daddr`, `inet_dport`, `inet_saddr`, `inet_rcv_saddr`, `inet_id`, `sk_state`, transmit hash, reuseport connected flag, and `sk_dst_cache`. There is no durable persistence.

## Dependencies and integration points
The file depends on IPv4 route lookup, multicast socket fields, l3 master detection, socket reuseport state, dst cache APIs, TCP state constants reused for datagram connected state, and IP statistics for `OUTNOROUTES`.

## Risks and invariants
Broadcast connect must remain gated by `SOCK_BROADCAST`. Rehashing after `inet_rcv_saddr` is assigned is required for socket lookup correctness. The release callback deliberately uses `sk_dst_set()` despite holding the socket lock because UDP transmit paths can manipulate the dst cache locklessly. Route errors must not leave partially connected socket state.

## Test signals
Tests should connect UDP sockets to unicast, multicast, broadcast with and without `SO_BROADCAST`, bound-device and multicast-interface cases, unreachable routes with IP stats increments, reuseport connected behavior, source address selection, socket rehash on first receive address assignment, and route-cache refresh after device or route changes.
