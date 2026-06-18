# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/srq.h

## Purpose
`srq.h` is the local interface for rdmavt shared receive queue lifecycle support.

## Important APIs, types, and functions
It includes `<rdma/rdma_vt.h>` and declares `rvt_driver_srq_init()`, `rvt_create_srq()`, `rvt_modify_srq()`, `rvt_query_srq()`, and `rvt_destroy_srq()`.

## Control flow
The header has no runtime control flow. Its declarations are consumed by `vt.c` when installing SRQ verbs and by `qp.c` when posting to and consuming from shared receive queues.

## State and persistence
No state is stored here. It exposes operations over `struct rvt_srq` state allocated and managed by the RDMA core object model.

## Dependencies and integration points
The header binds rdmavt SRQ support to RDMA core objects and internal implementation files. It should stay in sync with `srq.c` and `vt.c`.

## Risks
Prototype drift causes build failures or incorrect `ib_device_ops` wiring. Since SRQ objects interact with user mmap state, changes to signatures carrying `ib_udata` or attributes require careful ABI review.

## Test signals
Compile coverage for rdmavt and provider drivers catches header/implementation mismatch. Runtime SRQ verbs tests validate that the functions exposed through this header are correctly installed.
