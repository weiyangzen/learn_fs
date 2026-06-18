# sources/distributed-fs/ceph-client/net/rds/ib_mr.h

## Purpose
`ib_mr.h` defines the RDS/IB memory-region pool and FRMR structures used by RDMA registration and invalidation code.

## Important APIs, Types, And Functions
Key constants are `RDS_MR_1M_POOL_SIZE`, `RDS_MR_1M_MSG_SIZE`, `RDS_MR_8K_MSG_SIZE`, `RDS_MR_8K_SCALE`, and `RDS_MR_8K_POOL_SIZE`. Important types are `enum rds_ib_fr_state`, `struct rds_ib_frmr`, `struct rds_ib_mr`, and `struct rds_ib_mr_pool`. Declared APIs include MR pool create/destroy/info, get/sync/free/flush MR, MR init/exit, lkey retrieval, teardown, reuse, flush, FRMR registration/unregistration, and free-list handling.

## Control Flow
The header itself has no executable flow. It defines contracts used by MR pool implementation and `ib_frmr.c`: MRs move between free, in-use, and stale states; pools maintain free/drop/clean lists and delayed flush work; callers can request MR registration for scatterlists and later free or invalidate them.

## State And Persistence
`struct rds_ib_mr` stores work item, owning device/pool/connection, llist/list nodes, scatterlist and DMA lengths, ODP flag, and either FRMR state or direct `ib_mr`. `struct rds_ib_mr_pool` stores item/dirty counts, drop/free/clean lists, flush waitqueue, clean-list lock, pinned-memory accounting, max item/page limits, and delayed flush worker. State is per-device and volatile.

## Dependencies And Integration Points
The header depends on RDS core and `ib.h`, and it is included by IB RDMA/FRMR/device code. It is the shared contract between transport MR operations exposed in `rds_ib_transport` and lower-level pool/FRWR mechanics.

## Risks
Pool sizing constants directly affect pinned memory pressure. State-machine misuse can leak pinned pages, deregister in-use MRs, or leave stale MRs reusable. The delayed flush worker and waitqueue require careful synchronization with connection/device teardown.

## Test Signals
Validation should cover pool limit calculations, state transitions, pinned/free/dirty accounting, flush worker behavior, ODP versus FRMR selection paths, and compile-time consistency with `ib_frmr.c` and transport callbacks.
