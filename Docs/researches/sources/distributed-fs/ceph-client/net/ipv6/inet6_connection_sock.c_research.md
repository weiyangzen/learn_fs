# sources/distributed-fs/ceph-client/net/ipv6/inet6_connection_sock.c

Purpose: provides IPv6 helpers for connection-oriented sockets, mainly route construction for requests and established sockets plus the common transmit path used by TCP-like IPv6 connection sockets.

Important APIs, types, and functions: `inet6_csk_route_req()` builds a `flowi6` for a request socket; `inet6_csk_route_socket()` builds and caches a route for an established socket; `inet6_csk_xmit()` transmits a corked skb via `ip6_xmit()`. `inet_request_sock`, `ipv6_pinfo`, `inet_sock`, and `flowi6` are the central data structures.

Control flow: route helpers zero and fill `flowi6` with protocol, addresses, ports, mark, output interface, uid, flowlabel, ECN, and security classification. They call `fl6_update_dst()` under RCU to account for routing-header final destinations, then call `ip6_dst_lookup_flow()`. `inet6_csk_xmit()` first checks the cached dst cookie, refreshes routing on miss, attaches the dst without taking another ref, and calls `ip6_xmit()` with socket options and traffic class.

State and persistence: no long-lived state is defined here; it uses socket route cache state through `ip6_dst_store()` and `__sk_dst_check()`. Soft route errors are persisted into `sk_err_soft`, and route caps are cleared when lookup fails.

Dependencies and integration points: integrates with IPv6 route lookup, security hooks, flowlabel/extension options, ECN, sock reuseport headers, and the generic inet connection-socket layer. `inet6_csk_xmit()` is exported GPL for protocol users.

Risks: incorrect `fl6_update_dst()` handling can route to a final destination but must restore `fl6->daddr` for later socket use. Route lookup errors free the skb and return a negative errno, so callers must not reuse it. Cached dst correctness depends on `np->dst_cookie`.

Test signals: request-socket SYN/ACK routing with source routing options, established TCP transmit after route invalidation, bound-device and mark-based routing, security classification hooks, and error-path tests where route lookup fails and skb ownership is consumed.
