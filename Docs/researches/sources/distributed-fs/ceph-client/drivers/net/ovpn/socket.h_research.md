# sources/distributed-fs/ceph-client/drivers/net/ovpn/socket.h

Purpose: Defines the ovpn socket wrapper shared by peer management and TCP/UDP transport code.

Important APIs, types, and functions: `struct ovpn_socket` contains either UDP owner state (`ovpn_priv *ovpn` plus netdev tracker) or TCP owner state (`ovpn_peer *peer`), the underlying `struct sock *sk`, a kref, a generic work item, and a TCP TX work item. The public APIs are `ovpn_socket_new()` and `ovpn_socket_release()`.

Control flow: Netlink creates wrappers from socket fds during peer creation. Peer deletion calls `ovpn_socket_release()` exactly once for the peer. TCP/UDP detach functions are selected from the socket protocol.

State and persistence behavior: The wrapper persists while at least one peer references a UDP socket or while a TCP peer owns a connected socket. It is freed after detach, RCU reader synchronization, and reference drops.

Dependencies and integration points: It depends on kernel socket, kref, and sock APIs. It is included by peer and transport headers, making it the bridge between peer lifetime and socket callback ownership.

Risks and edge cases: The union means callers must branch on `sk_protocol` before interpreting `ovpn` versus `peer`. `work` is documented but not actively used in this subset, while `tcp_tx_work` is transport-specific. Releasing a wrapper twice would corrupt socket ownership, so peer deletion must be idempotent.

Test signals: Build tests for both transports, static analysis for union misuse, runtime refcount checks for UDP multi-peer sharing and TCP single-peer ownership, and teardown while TX work is pending.
