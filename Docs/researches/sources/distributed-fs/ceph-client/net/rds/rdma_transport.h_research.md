# sources/distributed-fs/ceph-client/net/rds/rdma_transport.h

## Purpose
`rdma_transport.h` declares the RDMA CM listener constants and module-level interfaces shared by `rdma_transport.c` and the IB transport implementation.

## Important APIs, Types, and Functions
It defines `RDS_CM_PORT`, `RDS_RDMA_RESOLVE_TIMEOUT_MS`, and `RDS_RDMA_REJ_INCOMPAT`. It declares `rds_rdma_cm_event_handler()`, `rds6_rdma_cm_event_handler()`, external `rds_ib_transport`, and `rds_ib_init()`/`rds_ib_exit()`.

## Control Flow
The header supports the flow where module init brings up IB transport support, installs RDMA CM listeners using the handlers declared here, and dispatches CM events back into IB connection-management callbacks.

## State and Persistence
No state is owned by this header. Constants influence listener port selection, route resolution timeout, and legacy rejection handling.

## Dependencies and Integration Points
The header includes RDMA verbs/CM headers and `rds.h`. It is included by `rdma_transport.c` and `ib.h`, binding the generic RDMA CM module to the IB transport object.

## Risks
Port constants are compatibility-sensitive: `RDS_PORT` remains in `rds.h` for legacy IPv4 while `RDS_CM_PORT` is used for IPv6/RDMA CM. Changing these values breaks wire compatibility. Reject reason encoding is explicitly legacy and should not be expanded casually.

## Test Signals
Build tests should validate IPv6 conditional handler declarations. Integration tests should confirm listener ports and route resolve timeout behavior.
