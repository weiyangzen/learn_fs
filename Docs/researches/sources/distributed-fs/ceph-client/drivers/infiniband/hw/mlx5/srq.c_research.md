# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/srq.c

## Purpose
`srq.c` implements RDMA core shared receive queue verbs for mlx5. It creates, modifies, queries, destroys, and posts receives to basic, XRC, and tag-matching SRQs, handling both userspace-backed and kernel-backed SRQ buffers.

## Important APIs, types, and functions
- `mlx5_ib_create_srq()`, `mlx5_ib_modify_srq()`, `mlx5_ib_query_srq()`, and `mlx5_ib_destroy_srq()` are the RDMA core SRQ operations.
- `create_srq_user()` parses `struct mlx5_ib_create_srq`, validates reserved fields, obtains optional user index, pins user buffer memory, maps the user doorbell, and sets UID/user-index fields.
- `create_srq_kernel()` allocates a kernel doorbell, fragmented buffer, next-WQE ring, PAS array, and WRID array.
- `destroy_srq_user()` and `destroy_srq_kernel()` release the resources created by the two creation paths.
- `mlx5_ib_srq_event()` converts mlx5 SRQ limit and catastrophic events into RDMA `IB_EVENT_SRQ_LIMIT_REACHED` and `IB_EVENT_SRQ_ERR` callbacks.
- `mlx5_ib_post_srq_recv()` posts receive WRs to kernel SRQs by filling WQE data segments, maintaining the free-list head, and updating the doorbell record.
- `mlx5_ib_free_srq_wqe()` returns completed kernel SRQ WQEs to the free list.

## Control flow
Creation validates SRQ type (`BASIC`, `XRC`, or `TM`), max WR/SGE against device limits, initializes locks, rounds queue depth to a power of two with one spare entry, computes descriptor size and gather capacity, then builds either user or kernel backing resources. It fills `mlx5_srq_attr` with queue geometry, flags, XRC domain/default XRCD, tag-matching parameters, CQ number, PD, and doorbell DMA, then calls `mlx5_cmd_create_srq()`. On success it installs the event callback, returns the SRQN to userspace if needed, and normalizes reported max WR.

Modify rejects resizing and only supports arming the SRQ low-watermark limit through `mlx5_cmd_arm_srq()`. Query allocates an attribute object, calls `mlx5_cmd_query_srq()`, and reports SRQ limit/max WR/max SGE. Destroy calls `mlx5_cmd_destroy_srq()` before freeing user or kernel backing resources.

Kernel receive posting is protected by `srq->lock` with IRQ save. It rejects internal-error devices, too many SGEs, and full queues, records WRIDs, consumes the next free WQE, writes scatter segments and a terminate-scatter-list marker when room remains, increments `wqe_ctr`, orders descriptor writes with `wmb()`, and updates the doorbell record.

## State and persistence
Persistent hardware state includes the SRQ/XRC/XRQ/RMP object, low-watermark arm state, doorbell address, PD/CQ/XRCD linkage, and PAS-backed queue memory. In-memory state includes the SRQ mutex, posting spinlock, WQE head/tail free list, WRID array, WQE counter, signature flag, user memory mapping, doorbell mapping, and fragmented kernel buffer.

## Dependencies and integration points
This file integrates with RDMA SRQ verbs, mlx5 SRQ command wrappers in `srq_cmd.c`, PD/CQ/XRCD helpers, mlx5 doorbell and fragment-buffer utilities, userspace ABI structs, tag matching capabilities, and device resource initialization (`mlx5_ib_dev_res_cq_init()`).

## Risks
- Queue depth uses a spare WQE and power-of-two masking; mistakes can make full and empty states ambiguous.
- Descriptor-size calculations mix next segments, data segments, signatures, and hardware maximum WQE size; overflow checks are important.
- Userspace creation depends on exact reserved-field and user-index ABI handling.
- Tag-matching SRQ list size uses `ilog2(max_num_tags) + 1` and must stay within hardware capability.
- Kernel posting assumes callers use kernel SRQs with allocated `wrid`; userspace SRQs are posted by userspace, not this path.
- Doorbell updates require correct memory ordering before writing the counter.

## Test signals
- Create/query/destroy tests should cover basic, XRC, and tag-matching SRQ types, user and kernel creation, invalid reserved fields, invalid sizes, and max capability boundaries.
- Modify tests should verify low-watermark arming and reject resize requests or limits greater than/equal to queue max.
- Kernel post tests should cover full queue, too many SGEs, zero-SGE receives, terminate-scatter-list insertion, internal-error return, and WQE free/reuse.
- Event tests should inject SRQ limit and catastrophic events and verify RDMA event callbacks.
- Tag-matching tests should cover `max_num_tags` capability limits and RNDV flag programming.
