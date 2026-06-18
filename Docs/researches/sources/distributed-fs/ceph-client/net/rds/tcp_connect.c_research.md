# sources/distributed-fs/ceph-client/net/rds/tcp_connect.c

## Purpose
Implements active TCP connection establishment, TCP state-change handling, and orderly TCP path shutdown for the RDS TCP transport.

## Important APIs, Types, and Functions
Exports `rds_tcp_state_change()`, `rds_tcp_conn_path_connect()`, and `rds_tcp_conn_path_shutdown()`. It uses `struct rds_conn_path`, `struct rds_connection`, `struct rds_tcp_connection`, kernel socket creation/bind/connect/shutdown APIs, and helpers from `tcp.c`, `tcp_send.c`, and RDS core state management.

## Control Flow
`rds_tcp_conn_path_connect()` refuses secondary multipath lanes until negotiation established multiple paths, serializes with `t_conn_path_lock`, creates an IPv4 or IPv6 TCP socket, tunes it, binds to the local RDS address using a source port whose low bits encode `cp_index`, installs callbacks before nonblocking connect, and keeps the socket on success. `rds_tcp_state_change()` reacts to TCP transitions: established connections either complete RDS path connect or are dropped when address ordering says the peer should reconnect, closing states wake shutdown waiters and drop the path. `rds_tcp_conn_path_shutdown()` sends `SHUT_WR`, repeatedly drains inbound data while waiting up to about five seconds for a closing TCP state and empty receive queue, drops messages already ACKed at TCP level, restores callbacks, releases the socket, and resets partial incoming state.

## State and Persistence
State includes `t_sock`, `t_client_port_group`, `t_recv_done_waitq`, partial incoming tracking, RDS path state, and TCP sequence fields used by ACK cleanup. It is all in-memory and bound to the connection path lifetime.

## Dependencies and Integration
Integrates with TCP state machine callbacks, RDS path transitions, RDS workqueue reconnect policy, multipath source-port encoding, address ordering from `rds_addr_cmp()`, keepalive setup from listen code, and ACK cleanup from `tcp_send.c`/`send.c`.

## Risks and Test Signals
Risks include dueling connect races, source-port exhaustion, waiting too long or not long enough during shutdown drain, callback ownership after failed connect, and IPv6 link-local scope handling. Test signals include simultaneous active connects from both peers, reconnect after RST, multipath lane ports modulo worker count, shutdown with queued receive data, and no callback invocation after socket release.
