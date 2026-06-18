# sources/distributed-fs/ceph-client/net/ipv4/udp_diag.c

## Purpose
This module exposes UDP sockets through the inet sock_diag netlink interface. It supports dumping all matching UDP sockets, looking up a single socket, reporting queue sizes, and optionally destroying sockets when `CONFIG_INET_DIAG_DESTROY` is enabled.

## Important APIs, Types, and Functions
Key functions are `udp_diag_dump()`, `udp_diag_dump_one()`, `sk_diag_dump()`, `udp_diag_get_info()`, and `udp_diag_destroy()`. The file registers `udp_diag_handler`, uses `struct inet_diag_req_v2`, `inet_sk_diag_fill()`, `inet_diag_bc_sk()`, `sock_diag_check_cookie()`, `sock_diag_destroy()`, `__udp4_lib_lookup()`, and optionally `__udp6_lib_lookup()`.

## Control Flow
Dump requests iterate the UDP primary hash table from callback cursor state, hold each bucket lock, filter by namespace, family, state, source port, and destination port, then emit inet_diag netlink records. Single-socket lookup runs under RCU, takes a socket reference if still live, validates the diagnostic cookie, allocates a reply skb, fills it, and unicasts it to the requester. Destroy performs a similar lookup and cookie check, then aborts the socket with `ECONNABORTED`.

## State and Persistence Behavior
The module persists only its registered inet_diag handler. Cursor progress is stored in `cb->args`, while sockets remain owned by the UDP tables. It does not mutate UDP state except through the optional destroy path.

## Dependencies and Integration Points
It depends on inet_diag netlink, UDP hash-table locking, socket refcounts, net namespace ownership, CAP_NET_ADMIN checks for privileged diagnostic fields, and IPv6 lookup helpers when enabled.

## Risks
Lookup argument ordering differs between historical dump-one and destroy paths; mistakes can miss sockets or destroy the wrong one. Iteration must not hold bucket locks while netlink output overflows indefinitely. Cookie checks and refcount acquisition are the main protection against stale or reused socket pointers.

## Test Signals
Exercise `ss`/sock_diag dumps with filters, dump-one for IPv4 and IPv6, v4-mapped IPv6 destroy, cookie mismatch, netns isolation, queue-size reporting, CAP_NET_ADMIN attribute differences, and concurrent socket close during dump/destroy.
