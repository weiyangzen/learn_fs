# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/srq.c

## Purpose
`srq.c` implements rdmavt shared receive queue lifecycle verbs: driver initialization, create, modify/resize, query, and destroy. It shares receive queue allocation and mmap mechanisms with QP receive queues.

## Important APIs, types, and functions
The exported functions are `rvt_driver_srq_init()`, `rvt_create_srq()`, `rvt_modify_srq()`, `rvt_query_srq()`, and `rvt_destroy_srq()`. Core state lives in `struct rvt_srq`, `struct rvt_rq`, `struct rvt_rwq`, `struct rvt_krwq`, and `struct rvt_mmap_info`.

## Control flow
Device registration initializes `n_srqs_lock` and the allocated count. Create accepts only `IB_SRQT_BASIC`, validates max WR/SGE against device limits, allocates a one-extra-entry circular queue via `rvt_alloc_rq()`, creates mmap metadata for user SRQs, initializes the SRQ limit, enforces `max_srq`, and appends mmap info to the pending list. Modify can resize the queue by allocating a temporary ring, verifying the requested size and current head/tail values, copying outstanding RWQEs from old tail to head, swapping in the new ring under `c_lock`, updating mmap metadata, and freeing the old ring. Limit-only modification just updates `srq->limit` under the queue lock.

## State and persistence
SRQ state is in memory: queue size, max SGE, head/tail/count, limit threshold, user mmap metadata, and the device SRQ allocation count. Resize preserves outstanding WR IDs and SGEs. User queues expose head/tail through mmap and therefore require validation before resize.

## Dependencies and integration points
The file depends on `rvt_alloc_rq()`, `rvt_create_mmap_info()`, `rvt_update_mmap_info()`, `rvt_release_mmap_info()`, RDMA udata copying, and QP receive consumption in `rvt_get_rwqe()`, which emits SRQ limit events.

## Risks
Resize is the sensitive path: it copies live queue entries while userspace may own ring indices, swaps pointers under lock, and updates mmap state after old mappings may exist. The limit-only branch lacks braces around the `else` body but assigns the same value once; this should be kept clear if edited. Cleanup must preserve kref semantics for user mappings.

## Test signals
Test SRQ create limits, unsupported SRQ types, posting and consuming from QPs sharing an SRQ, resize larger/smaller with queued WRs, invalid user head/tail values, mmap offset updates after resize, SRQ limit events, and allocation count under repeated create/destroy.
