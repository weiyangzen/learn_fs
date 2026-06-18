# sources/distributed-fs/ceph-client/net/rds/ib_rdma.c

## Purpose
`ib_rdma.c` implements RDS/IB device address tracking and the transport-specific memory-region (MR) backend used by generic RDS RDMA operations. It maps local IPv4 addresses to `struct rds_ib_device`, moves connections between the global nodev list and per-device connection lists, and manages pooled fast-registration MRs plus on-demand paging (ODP) MRs. The file is the bridge between `rdma.c` socket-level MR objects and low-level IB verbs helpers in `ib_mr.h`.

## Important APIs, Types, and Functions
Key external entry points are `rds_ib_get_device()`, `rds_ib_update_ipaddr()`, `rds_ib_add_conn()`, `rds_ib_remove_conn()`, `rds_ib_destroy_nodev_conns()`, `rds_ib_get_mr()`, `rds_ib_free_mr()`, `rds_ib_sync_mr()`, `rds_ib_flush_mrs()`, `rds_ib_get_lkey()`, `rds_ib_create_mr_pool()`, `rds_ib_destroy_mr_pool()`, `rds_ib_mr_init()`, and `rds_ib_mr_exit()`. The main state carriers are `struct rds_ib_device`, `struct rds_ib_mr`, and `struct rds_ib_mr_pool`, with clean, free, and drop MR lists implemented as lockless `llist_head`s. `rds_ib_odp_mr_worker()` is the deferred deregistration path for ODP MRs.

## Control Flow
IP address lookup walks `rds_ib_devices` under RCU and increments the device refcount on a match. `rds_ib_update_ipaddr()` either adds a new address to the current device or removes it from the old device before adding it to the new one. Connection attach/detach moves `ic->ib_node` between `ib_nodev_conns` and `rds_ibdev->conn_list` under the relevant spinlocks, updating `ic->rds_ibdev` and device references.

MR allocation enters through `rds_ib_get_mr()`. For ODP modes, the function checks device capability, calls `ib_reg_user_mr()`, stores the returned `ib_mr`, advertises/prefetches it, and returns a heap-allocated `rds_ib_mr`. For normal fast-registration, it validates the connection/QP and calls `rds_ib_reg_frmr()` against the 8K or 1M pools. MR freeing places reusable FRMRs on pool lists, tracks pinned-page pressure, queues delayed pool flushes, and optionally performs immediate invalidation if the caller requested it.

MR pool flushing is serialized by `pool->flush_lock`. It drains `drop_list`, `free_list`, and optionally `clean_list` into a temporary list, calls `rds_ib_unreg_frmr()` to unmap/free enough entries, returns reusable entries to `clean_list`, updates `free_pinned`, `dirty_count`, and `item_count`, and wakes waiters. `rds_ib_try_reuse_ibmr()` first attempts clean reuse, then reserves `item_count`, and finally triggers a flush if the pool limit is reached.

## State and Persistence
All state is kernel memory only. Device address and connection lists persist for the life of the IB device/connection. MR pools persist per `rds_ib_device` and are bounded by sysctl/device-derived limits. Pinned pages are accounted through pool counters and page references; ODP MRs are not pinned the same way and are deregistered asynchronously on the MR workqueue. The MR flush workqueue `rds_ib_mr_wq` is module-lifetime state.

## Dependencies and Integration Points
This file depends on RCU list traversal, spinlocks, delayed work, InfiniBand DMA/MR verbs, and helpers declared in `ib.h` and `ib_mr.h`. Generic `rdma.c` calls the transport callbacks exposed here via `struct rds_transport`: `get_mr`, `sync_mr`, `free_mr`, and `flush_mrs`. `rds_ib_get_mr_info()` feeds RDS info snapshots. `rds_ib_dev_put()` and global device lists are provided by the broader IB transport.

## Risks
MR lifetime is refcount- and list-sensitive: a missed `rds_ib_dev_put()`, stale list node, or incorrect `free_pinned` update can leak device references or pinned memory. The code marks all torn-down pages dirty because it does not distinguish read-only and writable MRs, which is conservative but expensive. `rds_ib_get_mr()` returns ODP MRs without setting the `device` pointer in the shown path, so call sites must only use fields valid for ODP. Pool flushing has subtle lockless-list batching and wait behavior; regressions can cause depletion, use-after-free, or stalls.

## Test Signals
Useful tests include MR allocation/free under 8K and 1M pool pressure, repeated `RDS_RDMA_USE_ONCE` and invalidate workloads, device removal with live nodev connections, ODP capable and non-ODP devices, and sysctl limit stress. Runtime signals include `s_ib_rdma_mr_*_reused`, `*_pool_flush`, `*_pool_wait`, `*_pool_depleted`, and warnings from pool destroy checks for nonzero `item_count` or `free_pinned`.
