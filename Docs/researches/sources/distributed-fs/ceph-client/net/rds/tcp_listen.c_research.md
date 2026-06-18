# sources/distributed-fs/ceph-client/net/rds/tcp_listen.c

## Purpose
Owns passive TCP listener setup, accept scheduling, accepted socket validation, multipath lane-slot selection, and listener teardown for RDS over TCP.

## Important APIs, Types, and Functions
Key functions are `rds_tcp_keepalive()`, `rds_tcp_conn_slots_available()`, `rds_tcp_accept_one()`, `rds_tcp_listen_data_ready()`, `rds_tcp_listen_init()`, and `rds_tcp_listen_stop()`. Local helpers include `rds_tcp_get_peer_sport()` and `rds_tcp_accept_one_path()`.

## Control Flow
`rds_tcp_listen_init()` creates an IPv4 or IPv6 kernel TCP listener on `RDS_TCP_PORT`, enables reuse and nodelay, replaces the listener data-ready callback, binds wildcard address, and listens with backlog 64. `rds_tcp_listen_data_ready()` queues accept work only for the listen socket and chains to the original callback. `rds_tcp_accept_one()` accepts or reuses a stashed socket, applies keepalive/tuning, derives local and peer addresses, rejects local-address peers except loopback cases, creates or finds an RDS connection, resolves address-ordering rules, assigns an available path based on source-port modulo when supported, installs callbacks, marks the path up, queues receive work, and sends a probe when path count is still unknown. If all slots are busy, it stashes the accepted socket to avoid losing already ACKed data.

## State and Persistence
Per-net state includes the listen socket, accept lock, accept work, and one `rds_tcp_accepted_sock` retained across `-ENOBUFS`. Per-connection state is the target `struct rds_tcp_connection` selected for an accepted path. No persistent storage is used.

## Dependencies and Integration
Depends on kernel accept/listen APIs, TCP keepalive tuning, RDS connection creation, path state transitions, multipath handshake state, netns private `rds_tcp_net`, and the common callback installation functions in `tcp.c`.

## Risks and Test Signals
Risks include losing data if an accepted socket is dropped while no path slot is free, accepting the wrong side of a dueling SYN, source-port/path mismatch during fan-out, listener callback teardown races, and netns deletion with pending accept work. Test signals are incoming connection storms, no-slot stashing and later replay, IPv6 and IPv4 listener fallback, loopback/self-connect rejection behavior, and clean listener stop while data-ready fires.
