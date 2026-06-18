# sources/distributed-fs/ceph-client/net/rds/loop.c

## Purpose
`loop.c` implements the in-kernel RDS loopback transport used when source and destination resolve to the same host. It bypasses wire transport and feeds an outgoing `rds_message` directly into the generic receive path.

## Important APIs, Types, and Functions
The file defines `struct rds_loop_connection`, global `rds_loop_transport`, and lifecycle functions `rds_loop_net_init()`, `rds_loop_net_exit()`, and `rds_loop_exit()`. Transport callbacks include `rds_loop_xmit()`, `rds_loop_inc_free()`, `rds_loop_recv_path()`, `rds_loop_conn_alloc()`, `rds_loop_conn_free()`, `rds_loop_conn_path_connect()`, and `rds_loop_conn_path_shutdown()`.

## Control Flow
Connection allocation stores a small loopback-private object in `conn->c_transport_data` and links it onto the global `loop_conns` list under `loop_conns_lock`. Connect completion simply calls `rds_connect_complete()`. Transmit validates that no partial-fragment state is passed, initializes the embedded `rm->m_inc` incoming object, takes an extra message reference so the embedded incoming remains valid, calls `rds_recv_incoming()` with local/foreign address roles adjusted for loopback, drops acked send state with the message sequence, and releases the incoming. Congestion bitmaps are not sent to loopback; they directly mark the peer map uncongested.

Module exit sets an unloading flag, waits for RCU readers, moves all loopback connections to a temporary list, and destroys them outside the spinlock. Per-net namespace exit filters loopback connections by `c_net` and destroys matching entries.

## State and Persistence
The global `loop_conns` list tracks active loopback connections. `rds_loop_unloading` is an atomic module-lifetime flag consulted by `t_unloading`. No state persists beyond module/net namespace lifetime. Message lifetime is managed by pairing the extra loopback addref with `rds_loop_inc_free()`.

## Dependencies and Integration Points
Loopback integrates with the generic transport table through `struct rds_transport`. It reuses `rds_message_inc_copy_to_user()` for delivery and generic connection/send/receive helpers for state transitions. `rds_single_path.h` maps legacy single-path fields to `c_path[0]`.

## Risks
Because the incoming object is embedded in the outgoing message, refcount pairing is critical. Address role inversion must remain correct or sockets will see wrong source/destination metadata. Exit destroys connections and assumes passive loopback connections are not present. Loopback intentionally omits RDMA transmit callbacks, so code paths must avoid selecting it for RDMA offload.

## Test Signals
Test local send/recv delivery, source address/port reporting, congestion bitmap short-circuiting, socket close while loopback incoming is queued, namespace teardown, and module unload with active loopback connections.
