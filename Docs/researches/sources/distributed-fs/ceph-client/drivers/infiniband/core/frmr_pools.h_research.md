# sources/distributed-fs/ceph-client/drivers/infiniband/core/frmr_pools.h

## Purpose
This internal header declares the FRMR pool data structures used by `frmr_pools.c` and exposes tuning helpers for pinned handles and aging period. It bridges the RDMA core pool implementation with public FRMR pool definitions in `<rdma/frmr_pools.h>`.

## Important APIs, Types, And Functions
`NUM_HANDLES_PER_PAGE` computes page capacity for 32-bit FRMR handles. `struct frmr_handles_page` stores one page of handles. `struct frmr_queue` represents a page-list-backed stack. `struct ib_frmr_pool` stores rb-tree membership, pool key, queue lock, regular and inactive queues, delayed work, owning device, and usage counters. `struct ib_frmr_pools` stores the rb-root, rb-tree lock, provider ops, aging workqueue, and aging period. The declared APIs are `ib_frmr_pools_set_pinned()` and `ib_frmr_pools_set_aging_period()`.

## Control Flow
The header has no executable flow, but defines the hierarchy: an `ib_device` owns `ib_frmr_pools`; it owns rb-tree-indexed pools; each pool owns active and inactive queues; each queue owns one or more handle pages. Delayed work is embedded per pool for key-local aging.

## State And Persistence
All state described here is in-memory and tied to the owning `ib_device`. Queue indexes and page lists must remain consistent under `ib_frmr_pool::lock`; rb-tree membership is protected by `ib_frmr_pools::rb_lock`.

## Dependencies And Integration Points
It depends on RDMA FRMR public types, rb-tree types, spinlocks, workqueues, page size, and integer types. It is private to RDMA core internals and must stay aligned with `struct ib_frmr_key`, provider `struct ib_frmr_pool_ops`, and `struct ib_mr::frmr` use.

## Risks And Test Signals
Changing queue fields or handle-page sizing can break accounting in `frmr_pools.c`. Adding fields can affect delayed-work teardown assumptions. Build tests should cover private and public FRMR pool users; runtime signals come from queue boundary, aging, pinned-count, and cleanup tests.
