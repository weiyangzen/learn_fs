# sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/resource.c

## Purpose

`resource.c` provides local resource allocation for the cxgb4 iWARP driver. It manages ID tables for TPT/STag, QP/CQ queue IDs, PD IDs, and SRQ indices, plus generic-allocator pools for adapter PBL memory, RQT memory, and on-chip QP memory.

## Important APIs, Types, and Functions

- `c4iw_init_resource` / `c4iw_destroy_resource`: initialize and free resource ID tables.
- `c4iw_get_resource` / `c4iw_put_resource`: thin wrappers around driver ID allocation that use zero as the public failure sentinel.
- `c4iw_get_cqid`, `c4iw_put_cqid`, `c4iw_get_qpid`, `c4iw_put_qpid`: allocate QIDs while sharing groups of IDs that map to one doorbell/GTS page.
- Pool allocators: `c4iw_pblpool_alloc/free/create/destroy`, `c4iw_rqtpool_alloc/free/create/destroy`, and `c4iw_ocqp_pool_alloc/free/create/destroy`.
- SRQ index APIs: `c4iw_alloc_srq_idx` and `c4iw_free_srq_idx`.

## Control Flow

Resource initialization allocates the TPT table with randomization, builds a QID table from the adapter virtual resource window while freeing IDs that do not align with `qpmask`, then creates PDID and SRQ tables. CQID/QPID allocation first tries the per-ucontext cached list. If empty, it allocates a base QID from the global table, accounts the whole `qpmask + 1` group, and populates both CQ and QP lists because all IDs in the group share one doorbell page.

PBL, RQT, and OCQP pools are Linux `gen_pool` regions backed by adapter virtual-resource address ranges. Creation attempts to add the full range and halves chunks on failure until a minimum threshold; allocation/free update stats and, for PBL/RQT, hold a kref so pool destruction waits until outstanding allocations are returned.

## State and Persistence Behavior

ID tables persist for the rdev lifetime. QID leftovers persist in per-ucontext `cqids` and `qpids` lists protected by `uctx->lock`. Pool allocations return adapter-relative addresses used in firmware resource commands, not CPU pointers. Usage/failure/max counters persist in `rdev->stats` under `stats.lock`. PBL and RQT pool destruction is reference-counted and completes via `pbl_compl`/`rqt_compl`; OCQP destruction directly destroys the pool.

## Dependencies and Integration Points

The file depends on driver ID-table helpers from `iw_cxgb4.h`, Linux `genalloc`, and low-level virtual resource descriptors in `rdev->lldi.vr`. `qp.c` consumes QIDs, RQT memory, SRQ indices, and OCQP memory; MR code consumes PBL pool allocations; `provider.c` consumes PDIDs.

## Risks and Edge Cases

- `c4iw_get_cqid` and `c4iw_get_qpid` can partially populate per-ucontext lists if `kmalloc` fails after a base QID is allocated, returning a QID while not caching the full group.
- QID stats increment by `qpmask + 1` when a base group is allocated but do not appear to decrement when cached IDs are later recycled to lists; stats are high-water/resource-use indicators, not exact global table occupancy.
- `c4iw_destroy_resource` frees TPT/QID/PDID tables but omits `srq_table`, which may leak table storage or rely on a separate lifecycle not visible in this file.
- Pool create functions may return success after only part of a hardware range is added, trading capacity for probe success.
- Address arithmetic uses 32-bit `unsigned` for virtual resource windows; larger adapter windows would need audit.

## Test Signals

Exercise power-of-two and zero SRQ resource initialization, QID allocation/free across multiple ucontexts, allocation failure in the middle of group-list population, PBL/RQT/OCQP exhaustion and stats, pool create with fragmented add failures, kref-delayed destroy while allocations are outstanding, and SRQ index allocation/free with unsupported SRQ hardware.
