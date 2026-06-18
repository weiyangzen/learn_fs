# sources/distributed-fs/ceph-client/net/l2tp/l2tp_ppp.c

## Purpose
`l2tp_ppp.c` implements the PPPoX protocol endpoint for PPP over L2TP. It exposes `PX_PROTO_OL2TP` sockets, binds those sockets to L2TP tunnel/session objects, registers PPP channels for data sessions, supports special session-id-zero tunnel-management sockets, and wires the module into per-net proc output, L2TP netlink session creation, and PPP/L2TP statistics.

## Important APIs, Types, and Functions
The main private type is `struct pppol2tp_session`, stored in `l2tp_session->priv[]`, containing the owning pid plus an RCU-protected PPPoX socket pointer guarded by `sk_lock`. `pppol2tp_create()`, `pppol2tp_connect()`, `pppol2tp_release()`, `pppol2tp_sendmsg()`, `pppol2tp_recvmsg()`, `pppol2tp_setsockopt()`, `pppol2tp_getsockopt()`, and `pppol2tp_ioctl()` implement the socket API. `pppol2tp_xmit()` is the PPP channel transmit callback, while `pppol2tp_recv()` is installed as the L2TP session receive callback. The module registers `struct pppox_proto`, `struct proto_ops`, `struct proto`, and, when L2TPv3 is enabled, `struct l2tp_nl_cmd_ops`.

## Control Flow
Socket creation allocates a `struct pppox_sock`, sets `SOCK_RCU_FREE`, installs backlog receive through `l2tp_udp_encap_recv()`, and leaves the socket unconnected. `connect()` parses one of the IPv4/IPv6 L2TPv2/L2TPv3 sockaddr layouts into `l2tp_connect_info`, resolves or creates a tunnel, resolves or creates a PPP pseudowire session, then either registers a PPP channel or attaches a tunnel-management socket for id-zero sessions. User `sendmsg()` allocates a fresh skb with IP/UDP/L2TP/PPP headroom and calls `l2tp_xmit_skb()`. PPP core transmit uses `skb_cow_head()`, prepends PPP address/control bytes, and also calls `l2tp_xmit_skb()`. Receive strips optional PPP address/control bytes, then either feeds `ppp_input()` for bound PPP channels or queues the skb to the socket receive queue.

## State and Persistence
State is volatile kernel state: socket state bits, `sk_user_data`, L2TP tunnel/session refcounts, session sequence options, reorder timeout, statistics counters, and optional proc/debugfs views. Lifetime depends on RCU and refcounts: `pppol2tp_sock_to_session()` grabs a session reference, `pppol2tp_session_close()` clears `ps->sk`, clears socket user data, and drops the socket-held session reference, and `pppol2tp_release()` deletes the L2TP session before final socket put.

## Dependencies and Integration Points
This file sits between PPP (`ppp_register_net_channel()`, `ppp_input()`), PPPoX, L2TP core (`l2tp_tunnel_*`, `l2tp_session_*`, `l2tp_xmit_skb()`), UDP/IP sockets, net namespaces, procfs, and optional L2TPv3 netlink creation. Userspace interacts through AF_PPPOX sockets, ioctls such as `PPPIOCGL2TPSTATS`, and `SOL_PPPOL2TP` socket options.

## Risks and Edge Cases
The highest-risk areas are lifetime races between socket close, L2TP session deletion, PPP unbind, and RCU socket lookup. Headroom sizing must remain consistent with L2TP header length changes caused by send-sequence settings. The id-zero management socket path deliberately bypasses PPP registration and should stay isolated from data-session operations. Stats and proc paths read shared tunnel/session objects and must keep reference discipline. IPv6 conditional branches in `getname()` are another compatibility-sensitive area.

## Test Signals
Useful signals include AF_PPPOX connect/send/recv tests for L2TPv2 and L2TPv3, PPP channel attach/detach tests, id-zero management socket ioctl/sockopt tests, namespace proc visibility, stats copy correctness, receive of PPP frames with and without `0xff03`, close/unregister race tests under KASAN/KCSAN, and L2TPv3 netlink session-create/delete coverage.
