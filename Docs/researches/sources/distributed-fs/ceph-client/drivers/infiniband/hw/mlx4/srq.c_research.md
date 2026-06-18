# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/srq.c

## Purpose
This file implements mlx4 shared receive queue verbs. It creates, modifies, queries, destroys, posts receives to, and recycles WQEs for basic and XRC SRQs while translating mlx4 SRQ events to RDMA core events.

## Important APIs, types, and functions
The public functions are `mlx4_ib_create_srq`, `mlx4_ib_modify_srq`, `mlx4_ib_query_srq`, `mlx4_ib_destroy_srq`, `mlx4_ib_free_srq_wqe`, and `mlx4_ib_post_srq_recv`. Internally, `get_wqe` computes WQE addresses in either a kernel mlx4 buffer or user-backed MTT address space, and `mlx4_ib_srq_event` maps `MLX4_EVENT_TYPE_SRQ_LIMIT` and `MLX4_EVENT_TYPE_SRQ_CATAS_ERROR` to `IB_EVENT_SRQ_LIMIT_REACHED` and `IB_EVENT_SRQ_ERR`.

## Control flow
Creation rejects unsupported SRQ types and oversized capabilities, initializes mutex/spinlock state, rounds the WQE count to a power of two with one reserved entry, computes descriptor size, then chooses a user or kernel allocation path. User SRQs copy the create command, pin user memory, build an MTT, and map the user doorbell. Kernel SRQs allocate a doorbell, buffer, initialize the WQE free-list through next-index segments, invalidate unused data segments, build an MTT, and allocate the WRID array. Both paths call `mlx4_srq_alloc` with PD, optional CQ number, XRC domain, MTT, and doorbell DMA, then return the SRQN to userspace when requested.

Modification only supports arming the limit watermark with `mlx4_srq_arm`; resizing is rejected. Query calls `mlx4_srq_query` and returns limit, max WR, and max SGE. Destroy frees the firmware SRQ, MTT, user or kernel backing resources, doorbell, and umem.

Posting receives is serialized by `srq->lock`. It rejects internal-error devices, validates SGE count and free-list availability, records WRIDs, pops WQEs from the free-list, fills data segments, invalidates the first unused segment, increments the producer counter, uses a write barrier, and updates the doorbell record. Completed WQEs are returned through `mlx4_ib_free_srq_wqe`, which pushes the index onto the tail of the free-list.

## State and persistence behavior
The SRQ state is runtime-only: `msrq.max`, `max_gs`, WQE shift, head/tail free-list pointers, WQE counter, WRID array, umem/buffer, MTT, and doorbell record. Firmware persists the SRQ until `mlx4_srq_free`; no state survives driver teardown.

## Dependencies and integration points
The file depends on mlx4 SRQ/QP core APIs, mlx4 buffer/MTT helpers, RDMA uverbs ABI copy helpers, XRC objects, CQs for XRC/event delivery, PDs, DMA/umem memory pinning, and RDMA event callbacks.

## Risks
Important risks are free-list corruption under concurrent post/complete, incorrect WQE descriptor sizing, missing invalid LKEY termination, user umem/doorbell cleanup leaks on partial creation failure, unsupported resize expectations, and incorrect behavior during `MLX4_DEVICE_STATE_INTERNAL_ERROR`.

## Test signals
Exercise basic and XRC SRQ create/destroy, boundary max WR/SGE, user and kernel SRQ posting, limit arming and event delivery, free-WQE recycling under completion load, invalid SGE rejection, no-resize rejection, and fault-injection cleanup for MTT, doorbell, umem, and firmware allocation failures.
