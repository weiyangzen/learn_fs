# sources/distributed-fs/ceph-client/drivers/net/ovpn/udp.h

Purpose: Declares the ovpn UDP transport API used by socket wrapping and packet transmit code.

Important APIs, types, and functions: `ovpn_udp_socket_attach()` links an ovpn socket wrapper and kernel socket to an ovpn instance. `ovpn_udp_socket_detach()` removes UDP tunnel callbacks. `ovpn_udp_send_skb()` transmits an encrypted skb to a peer over the associated UDP socket.

Control flow: `socket.c` calls attach/detach according to `sk_protocol`. The crypto/TX path calls `ovpn_udp_send_skb()` after encryption has produced an outer OpenVPN packet.

State and persistence behavior: No state is defined here; functions operate on `struct ovpn_socket`, `struct ovpn_priv`, `struct ovpn_peer`, and `struct sock` runtime objects.

Dependencies and integration points: It depends on the kernel socket layer and the ovpn peer/socket types. It is the UDP-specific boundary between generic socket wrapping and transport implementation.

Risks and edge cases: Callers must only pass UDP sockets. Send requires a valid peer bind; otherwise the implementation drops the skb. Attach may find the socket already owned by the same ovpn instance or a different user.

Test signals: Build inclusion with socket/peer declarations, UDP attach/detach lifecycle, send without bind, send after route cache reset, and shared socket refcount behavior.
