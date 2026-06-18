# sources/distributed-fs/ceph-client/drivers/net/ovpn/tcp.h

Purpose: Declares the ovpn TCP transport API used by socket wrapping and packet transmit code.

Important APIs, types, and functions: The header declares `ovpn_tcp_init()`, `ovpn_tcp_socket_attach()`, `ovpn_tcp_socket_detach()`, `ovpn_tcp_socket_wait_finish()`, `ovpn_tcp_send_skb()`, and `ovpn_tcp_tx_work()`. It includes peer, skb, and socket definitions because TCP state is embedded in `struct ovpn_peer` and work is embedded in `struct ovpn_socket`.

Control flow: Module initialization calls `ovpn_tcp_init()` before TCP sockets can be attached. `socket.c` calls attach/detach/wait during socket lifetime. Crypto/TX completion calls `ovpn_tcp_send_skb()` to prepend the OpenVPN stream length and send/enqueue the skb. Socket write-space schedules `ovpn_tcp_tx_work()`.

State and persistence behavior: No state is defined here directly; declarations operate on per-peer TCP queues and per-socket TX work.

Dependencies and integration points: It integrates ovpn with Linux TCP proto/proto_ops replacement and the shared skbuff control block.

Risks and edge cases: `ovpn_tcp_send_skb()` expects enough headroom for the 2-byte length prefix. Attach/detach must be paired once per TCP wrapper. Header include cycles are possible because `peer.h` includes `socket.h`; build coverage catches ordering issues.

Test signals: Build TCP-enabled ovpn, validate headroom assumptions in encrypted TX, and test attach/detach/send under both IPv4 and IPv6 sockets.
