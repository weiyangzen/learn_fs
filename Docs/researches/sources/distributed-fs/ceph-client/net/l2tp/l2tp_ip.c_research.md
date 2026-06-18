# sources/distributed-fs/ceph-client/net/l2tp/l2tp_ip.c

## Purpose
Implements IPv4 plain L2TPv3-over-IP encapsulation using IP protocol 115. It registers an IPv4 datagram socket protocol for userspace control frames and a network protocol handler for incoming L2TP/IP packets.

## Important APIs, types, and functions
- Per-net `struct l2tp_ip_net` holds socket hash and bind tables protected by `l2tp_ip_lock`.
- `struct l2tp_ip_sock` extends `inet_sock` with local and peer L2TP connection IDs.
- `l2tp_ip_recv` is the IPv4 protocol handler for IPPROTO_L2TP.
- `l2tp_ip_bind`, `l2tp_ip_connect`, `l2tp_ip_getname`, `l2tp_ip_sendmsg`, and `l2tp_ip_recvmsg` implement the socket behavior.
- `l2tp_ioctl` implements shared `SIOCOUTQ` and `SIOCINQ` support and is exported for IPv6.

## Control flow
Incoming packets first require at least four bytes. A nonzero first word is a data session ID, so the handler looks up the L2TPv3 session globally, checks optional v3 fields are linear, and calls `l2tp_recv_common`. A zero first word marks a control frame; the handler strips it, validates the L2TP control header shape, extracts the tunnel ID, finds a bound userspace socket by local/remote address, ingress interface, and connection ID, checks XFRM policy, resets conntrack, and queues the skb to the socket.

Userspace must bind before connect because there are no ports and autobind is disabled. Sendmsg creates a packet with a zero session-id word before the user control payload, routes to either a supplied destination or connected peer, and transmits through `ip_queue_xmit`.

## State and persistence behavior
State is per-net socket tables plus per-socket local/peer connection IDs and normal inet socket state. No persistent state is stored. Destroying a socket purges write queue state and asks the core to delete any tunnel using that socket.

## Dependencies and integration points
Depends on IPv4 protocol registration (`inet_add_protocol`), datagram socket registration, route lookup, XFRM IPv4 policy checks, conntrack reset, net namespaces, and L2TP core session lookup/RX handling. Core static tunnel creation uses this socket family for plain IP encapsulation.

## Risks and test signals
Risks include bind-table collisions, incorrect control/data classification, short packets, missing session ref drops on discard paths, route failures in sendmsg, and socket destroy racing with tunnel teardown. Test signals include AF_INET/SOCK_DGRAM/IPPROTO_L2TP socket creation, bind/connect/getname, control-frame send/receive, data-frame delivery to pseudowires, XFRM policy drops, bind duplicate `EADDRINUSE`, and namespace exit table warnings.
