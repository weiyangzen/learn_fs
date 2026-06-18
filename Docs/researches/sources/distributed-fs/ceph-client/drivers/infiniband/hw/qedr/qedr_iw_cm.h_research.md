# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_iw_cm.h

## Purpose
`qedr_iw_cm.h` declares QEDR iWARP connection-management callbacks that `main.c` installs into `ib_device_ops`.

## Important APIs, Types, And Functions
It exposes active/passive CM functions (`qedr_iw_connect`, `qedr_iw_create_listen`, `qedr_iw_destroy_listen`, `qedr_iw_accept`, `qedr_iw_reject`) and QP reference/lookup hooks (`qedr_iw_qp_add_ref`, `qedr_iw_qp_rem_ref`, `qedr_iw_get_qp`). It includes `<rdma/iw_cm.h>` for `iw_cm_id` and `iw_cm_conn_param`.

## Control Flow
No executable control flow exists. The declarations are consumed by QEDR device registration so the RDMA core can call into `qedr_iw_cm.c` for iWARP devices.

## State And Persistence Behavior
The header stores no state. It defines the cross-file function contract for CM ID and QP lifetime operations.

## Dependencies And Integration Points
It integrates `main.c` with `qedr_iw_cm.c`, and indirectly with the RDMA iWARP CM core. The header has no include guard in the inspected file, so repeated inclusion would rely on compiler tolerance for duplicate prototypes rather than preprocessor protection.

## Risks And Test Signals
Risks are prototype drift and the missing include guard. Test signals include clean builds with warnings enabled, `CONFIG_INFINIBAND_QEDR` iWARP registration, and RDMA core invoking each installed iWARP callback during connection tests.
