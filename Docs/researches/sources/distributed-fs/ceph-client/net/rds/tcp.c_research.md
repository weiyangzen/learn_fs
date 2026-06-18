# sources/distributed-fs/ceph-client/net/rds/tcp.c

## Purpose
Registers and owns the RDS TCP transport, including per-net namespace listen sockets and sysctls, TCP socket callback replacement/restoration, transport allocation/free, transport info export, unload handling, and lifecycle teardown.

## Important APIs, Types, and Functions
Defines `struct rds_transport rds_tcp_transport` and `int rds_tcp_netid`. Important functions include `rds_tcp_write_seq()`, `rds_tcp_snd_una()`, `rds_tcp_set_callbacks()`, `rds_tcp_reset_callbacks()`, `rds_tcp_restore_callbacks()`, `rds_tcp_laddr_check()`, `rds_tcp_tune()`, `rds_tcp_accept_work()`, pernet callbacks `rds_tcp_init_net()` and `rds_tcp_exit_net()`, sysctl handlers for `rds_tcp_sndbuf` and `rds_tcp_rcvbuf`, and module init/exit. Internal lists `rds_tcp_tc_list` and `rds_tcp_conn_list` track active callback-installed sockets and allocated TCP transport objects.

## Control Flow
Module init creates the TCP connection slab, initializes receive allocation, registers pernet state, registers the RDS transport, and registers TCP socket info providers. Per-net init creates a netns-private sysctl table, then creates an IPv6 listener or falls back to IPv4. Connection allocation creates one `struct rds_tcp_connection` per multipath lane, attaches each to an `rds_conn_path`, and links all objects on the global cleanup list. Callback setup saves original TCP callbacks, stores the RDS path in `sk_user_data`, installs RDS data-ready/write-space/state-change hooks, and adds the object to the info list. Reset handles dueling SYN cases by forcing path state to resetting, waiting out transmitters, cancelling send/recv work, restoring and releasing the old socket, resetting RDS send state, then installing callbacks on the new socket. Exit marks unloading, drains RCU, deregisters info and pernet state, destroys connections, unregisters transport, exits receive support, and destroys the slab.

## State and Persistence
Global state includes active TCP connection lists, counts for IPv4 and IPv6 info reporting, unloading flag, and the connection slab. Per-net `struct rds_tcp_net` stores accept lock, listen socket, one stashed accepted socket, accept work, sysctl header/table, and configured socket buffer sizes. Per-connection state lives in `struct rds_tcp_connection`. All state is runtime-only.

## Dependencies and Integration
Integrates the generic RDS transport API with kernel TCP sockets, net namespaces, sysctl, RDS info, RDS workqueue, and IPv6 address checks. The transport supplies send, receive, connect, shutdown, local-address validation, stats, and path-slot callbacks used by the RDS core.

## Risks and Test Signals
Risks include callback restoration races, stale sockets during netns teardown, incorrect list count updates, sysctl-triggered reconnect storms, and deadlocks if reset waits while holding a socket lock in the wrong order. Test signals are module load/unload, per-net listener creation and fallback, sysctl writes causing connection drops and reconnects, `RDS_INFO_TCP_SOCKETS`/`RDS6_INFO_TCP_SOCKETS` counts, dueling SYN reset, and clean netns deletion with no leaked sockets.
