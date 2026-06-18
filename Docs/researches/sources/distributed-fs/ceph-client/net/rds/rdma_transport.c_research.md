# sources/distributed-fs/ceph-client/net/rds/rdma_transport.c

## Purpose
`rdma_transport.c` is the module entry point and RDMA CM event dispatcher for the RDS RDMA/IB transport. It initializes IB transport support, creates IPv4 and IPv6 RDMA listeners, dispatches CM events to transport callbacks, and tears down listeners on module exit.

## Important APIs, Types, and Functions
The file defines `rds_rdma_cm_event_handler()`, `rds6_rdma_cm_event_handler()`, `rds_rdma_listen_init_common()`, `rds_rdma_listen_init()`, `rds_rdma_listen_stop()`, module `rds_rdma_init()`, and module `rds_rdma_exit()`. Listener state is in `rds_rdma_listen_id` and, when IPv6 is enabled, `rds6_rdma_listen_id`.

## Control Flow
The common CM handler resolves the transport from the RDMA device node type, locks `conn->c_cm_lock` when a connection context exists, bails out safely if disconnecting, and switches on CM event type. Connect requests call `cm_handle_connect`; address resolution sets service type/min RNR timer and resolves route; route resolution verifies the cm_id still belongs to the connection, sets service level from TOS, and calls `cm_initiate_connect`; established events call `cm_connect_complete`; reject/error/disconnect/timewait events generally drop the connection.

Listener setup creates an RDMA CM id in `init_net` with `RDMA_PS_TCP` and `IB_QPT_RC`, binds to the supplied sockaddr, and listens with backlog 128. IPv4 listens on `RDS_PORT` for compatibility. IPv6, when compiled, listens on `RDS_CM_PORT` and logs but tolerates failure. Module init calls `rds_ib_init()` first, then starts listeners; failure after IB init unwinds with `rds_ib_exit()`. Exit stops listeners before shutting down IB.

## State and Persistence
Listener CM ids are module-lifetime global state. Per-connection CM progress lives in `struct rds_connection` and transport-private IB connection state. No persistent storage is used.

## Dependencies and Integration Points
This file depends on RDMA CM APIs, IB transport callbacks in `rds_ib_transport`, and connection management helpers from RDS core. It includes `rds_single_path.h` because connection state macros expect single-path compatibility in some CM paths.

## Risks
The local `trans` variable is assigned only for `RDMA_NODE_IB_CA`; unexpected node types would leave it undefined before use. CM event handling must avoid destroying cm_ids while shutdown is in progress, hence the lock and disconnecting checks. Rejection compatibility logic resets proposed protocol version only in specific cases. Listener bind behavior may associate ids with devices, limiting failover as noted by the comment.

## Test Signals
Cover module load/unload, IPv4 and IPv6 listener creation, connect request handling, address/route/established event sequences, rejection with legacy incompat data, device removal, disconnect/timewait events, and route resolution races where a cm_id no longer matches connection private state.
