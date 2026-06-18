# sources/distributed-fs/ceph-client/net/l2tp/l2tp_ip6.c

## Purpose
Implements IPv6 plain L2TPv3-over-IP encapsulation using IP protocol 115. It mirrors the IPv4 L2TP/IP module with IPv6-specific bind, routing, flowlabel, control-message, and receive-option handling.

## Important APIs, types, and functions
- Per-net `struct l2tp_ip6_net` stores IPv6 L2TP socket and bind tables.
- `struct l2tp_ip6_sock` extends `inet_sock` with L2TP connection IDs and embeds `ipv6_pinfo`.
- `l2tp_ip6_recv` is the IPv6 protocol handler.
- `l2tp_ip6_bind`, `l2tp_ip6_connect`, `l2tp_ip6_getname`, `l2tp_ip6_sendmsg`, and `l2tp_ip6_recvmsg` implement IPv6 socket operations.
- `l2tp_ip6_push_pending_frames` writes the required zero session-id control prefix before flushing pending IPv6 frames.

## Control flow
Receive classification matches IPv4: nonzero first word is a data session ID delivered through L2TP core; zero first word is a userspace control frame. Control delivery validates header bits, extracts the tunnel ID, finds a bound socket by IPv6 local/remote address, ingress interface, and connection ID, checks XFRM IPv6 policy, resets conntrack, and queues the skb.

Bind rejects mapped and multicast addresses, handles link-local scope IDs and device lookup, checks address ownership, records the local connection ID, and moves the socket to the bind table. Connect rejects multicast peers, supports mapped-address multicast validation, requires prior bind, stores peer connection ID, and refreshes the bind table. Sendmsg builds IPv6 flow state, handles cmsgs, flowlabels, options, scope, route lookup, optional neighbor confirmation, appends data with a 4-byte transport prefix, and pushes pending frames unless `MSG_MORE`.

## State and persistence behavior
State is runtime-only in per-net tables and per-socket IDs, IPv6 addresses, options, pending frames, and normal socket caches. Destroy flushes pending IPv6 frames and requests core tunnel deletion for any tunnel using the socket.

## Dependencies and integration points
Depends on IPv6 protocol registration (`inet6_add_protocol`), IPv6 datagram routing/options/flowlabel helpers, XFRM IPv6 policy checks, L2TP core, net namespaces, and the shared `l2tp_ioctl` from the IPv4 module.

## Risks and test signals
Risks include scope handling for link-local addresses, option/flowlabel lifetime, pending-frame cleanup, mapped-address corner cases, bind table uniqueness, and race-free tunnel deletion on socket destroy. Test signals include AF_INET6/SOCK_DGRAM/IPPROTO_L2TP sockets, link-local bind with and without scope, control send/receive, `MSG_ERRQUEUE`, data delivery, route/no-route errors, XFRM policy behavior, and net namespace cleanup warnings.
