# sources/distributed-fs/ceph-client/drivers/net/ovpn/socket.c

Purpose: Wraps user-provided TCP/UDP sockets in `struct ovpn_socket`, attaches transport-specific callbacks, and manages shared socket lifetime.

Important APIs, types, and functions: `ovpn_socket_new()` validates ownership and attaches sockets. `ovpn_socket_release()` detaches a peer from its socket, drops references, waits for TCP work, and frees the wrapper when the kref reaches zero. Internal helpers include `ovpn_socket_release_kref()`, `ovpn_socket_put()`, `ovpn_socket_hold()`, and `ovpn_socket_attach()`.

Control flow: Netlink passes a looked-up socket to `ovpn_socket_new()`. TCP sockets must be unowned and become unique to one peer. UDP sockets may already be owned by the same ovpn instance, in which case the wrapper kref is incremented for sharing. A new wrapper stores either the peer (TCP) or ovpn instance and dev tracker (UDP), takes a sock reference, and calls `ovpn_tcp_socket_attach()` or `ovpn_udp_socket_attach()`. Release swaps `peer->sock` to NULL, drops wrapper kref under the socket lock, synchronizes RCU readers, then performs transport-specific final cleanup.

State and persistence behavior: `struct ovpn_socket` is runtime state anchored in `sk_user_data` and peer RCU pointers. UDP wrappers hold a netdev reference while shared; TCP wrappers hold a peer reference and work item.

Dependencies and integration points: It depends on UDP and TCP transport attach/detach implementations, socket locks, RCU `sk_user_data`, netdev reference tracking, and krefs. Netlink owns socket fd lookup; this layer owns encapsulation state.

Risks and edge cases: UDP `ovpn_udp_socket_attach()` can return `-EALREADY` when the same instance already owns the socket; the caller treats an already-held wrapper as success before attach. Release must avoid racing a new attach against a partially detached socket, hence the socket lock and RCU sync. TCP cleanup can sleep and therefore is intentionally outside global peer locks.

Test signals: Test TCP double-attach `-EBUSY`, UDP sharing across peers in one instance, UDP sharing across instances rejected, unknown protocols rejected, release after transport-side detach, concurrent new/release on same socket, TCP work cancellation, and sock/netdev/peer refcount balance.
