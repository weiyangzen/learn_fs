# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/qp.h

## Purpose
`qp.h` is the local rdmavt QP interface used by `vt.c`, `srq.c`, provider-facing code, and other rdmavt modules. It exposes QP lifecycle verbs, send/receive posting entry points, receive-queue allocation, and working-set-size initialization.

## Important APIs, types, and functions
The header includes `<rdma/rdmavt_qp.h>` and declares `rvt_driver_qp_init()`, `rvt_qp_exit()`, `rvt_create_qp()`, `rvt_modify_qp()`, `rvt_destroy_qp()`, `rvt_query_qp()`, `rvt_post_recv()`, `rvt_post_send()`, `rvt_post_srq_recv()`, `rvt_wss_init()`, `rvt_wss_exit()`, and `rvt_alloc_rq()`.

## Control flow
This header does not execute control flow. It defines the compilation contract that lets `vt.c` install QP operations into `ib_device_ops`, lets `srq.c` reuse receive-queue allocation, and lets the module registration path initialize and tear down QP-related global device state.

## State and persistence
No state is stored in the header. Its declarations govern in-memory state owned by `qp.c`, especially QP hash tables, QPN maps, per-QP rings, and WSS tables.

## Dependencies and integration points
The header is an internal bridge between rdmavt's public RDMA structures and local implementation files. It depends on RDMA core QP type definitions and is included by modules that need the QP verbs to be available without including `qp.c` internals.

## Risks
Prototype drift here breaks `ib_device_ops` initialization and provider builds. Since the header exports functions used from multiple rdmavt compilation units, signature changes must be coordinated with `vt.c`, `srq.c`, and all provider references.

## Test signals
Build coverage of `CONFIG_INFINIBAND_RDMAVT` consumers is the primary signal. Compile failures in `vt.c`, `srq.c`, or provider drivers catch most contract mismatches.
