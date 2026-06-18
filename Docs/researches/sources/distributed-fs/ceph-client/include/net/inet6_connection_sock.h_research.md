# sources/distributed-fs/ceph-client/include/net/inet6_connection_sock.h

Purpose: declares IPv6-specific helpers for connection-oriented INET sockets. It complements `inet_connection_sock.h` with IPv6 route and transmit operations.

Important APIs: `inet6_csk_route_socket()` resolves a route for an existing socket and flow. `inet6_csk_route_req()` resolves a route for a request socket/child creation path. `inet6_csk_xmit()` transmits an skb for a connected IPv6 socket using a generic `flowi`.

Control flow and state: TCP/connection-oriented IPv6 code builds a `flowi6`, resolves dst entries for sockets or SYN requests, then transmits through `inet6_csk_xmit()`. Persistent state lives in the `sock`, request socket, dst cache, and IPv6 cork/options structures.

Dependencies and integration: forward-declares flow, request, skb, sock, and sockaddr types. It integrates with TCPv6, MPTCP/ULP paths, route lookup, request socket creation, and common inet connection timers/state.

Risks: wrong flow construction or route reuse can send with stale source address, mark, or bound device. Tests should cover IPv6 connect/listen/SYN-ACK routing, bound device and l3mdev behavior, PMTU changes, flow-label/tclass propagation, and transmit errors.
