# sources/distributed-fs/ceph-client/net/x25/af_x25.c

Purpose: implements the AF_X25 `SOCK_SEQPACKET` socket family, global socket list, address conversion, call setup/acceptance, userspace send/receive, X.25 ioctls, netdevice integration, and module lifecycle.

Important APIs/functions: externally used helpers include `x25_parse_address_block()`, `x25_addr_ntoa()`, `x25_addr_aton()`, `x25_find_socket()`, `x25_rx_call_request()`, `x25_destroy_socket_from_timer()`, and `x25_kill_by_neigh()`. Socket operations include `x25_create()`, `x25_bind()`, `x25_connect()`, `x25_listen()`, `x25_accept()`, `x25_release()`, `x25_sendmsg()`, `x25_recvmsg()`, `x25_ioctl()`, and compat ioctl support.

Control flow: outbound sockets must bind, route a destination, get a neighbour, choose an LCI, send `X25_CALL_REQUEST`, and wait for state 3/TCP_ESTABLISHED unless nonblocking. Incoming call requests parse addresses, facilities, and call user data, find a listener by address/CUD, optionally forward, negotiate facilities, create a child socket, optionally send `CALL_ACCEPTED`, queue it for `accept()`, and start heartbeat. Send builds data or interrupt packets, handles optional Q-bit-included payloads, queues through `x25_output()`, and kicks transmit. Receive strips PLP headers, restores optional Q-bit byte, and returns record-oriented data.

State and persistence: global `x25_list` tracks bound/connected sockets under `x25_list_lock`. Per-socket state includes addresses, neighbour reference, LCI, PLP state, timers, facilities, DTE facilities, call user data, cause/diagnostic, queues, sequence variables, and flags. Runtime sysctl defaults seed new sockets; no durable persistence exists.

Dependencies and integration: integrates Linux proto registration, `sock_register(AF_X25)`, packet type `ETH_P_X25`, netdevice notifier events, route/neighbour/facilities/timer/proc/sysctl helpers, capabilities for route/subscription ioctls, and init_net-only operation.

Risks and test signals: important risks are reference lifetime for neighbours/routes/sockets, partial usercopy paths, listen queue ownership via `skb->sk`, state transitions during signals/nonblocking connect, and ioctl validation for facilities and CUD matching. Tests should cover bind validation, route lookup, connect timeout/refusal, incoming call accept approval, forwarding fallback, Q-bit send/recv, OOB interrupts, clear/reset races, device down cleanup, compat ioctls, and module unload with live references.
