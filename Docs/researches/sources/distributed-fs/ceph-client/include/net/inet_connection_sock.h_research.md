# sources/distributed-fs/ceph-client/include/net/inet_connection_sock.h

Purpose: defines the common state and helpers for connection-oriented INET sockets, especially TCP-like protocols. It extends `inet_sock` with accept queue, bind buckets, retransmit/delayed-ACK/keepalive timers, PMTU probing, congestion control, ULP hooks, and address-family operations.

Important APIs/types: `struct inet_connection_sock_af_ops` provides AF-specific transmit, header rebuild, dst set, connection request, SYN receive child creation, socket options, and MTU reduction hooks. `struct inet_connection_sock` holds timers, RTO values, PMTU cookie, congestion-control private area, delayed ACK state, MTU probe state, user timeout, and ULP data. Helpers schedule/clear ACKs, initialize/clear/reset transmit timers, accept children, get ports, route requests/children, manage request queues, start/stop listening, update PMTU, ping-pong mode, and initialize locks.

Control flow and state: listen paths allocate request sockets, hash them, complete hashdance into children, and queue accepted sockets. Established paths manage timers and congestion/ACK state. State is long-lived in the socket and protected by socket locks, timers, memory barriers, and request-queue locks.

Dependencies and integration: depends on inet/request sock, timers, poll, sockptr, congestion control, ULP, TCP states, and IPv4/IPv6 AF ops.

Risks: timer state transitions and request queue accounting are race-prone. Congestion private size is fixed. Tests should cover SYN queue add/drop/hashdance, timer reset/clear, delayed ACK scheduling, PMTU update, accept queue polling, ULP presence, ping-pong counters, and close/destroy cleanup.
