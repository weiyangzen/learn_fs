# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_rq.c

## Purpose
`vnic_rq.c` manages low-level Cisco vNIC receive queues: software buffer ring allocation, resource binding, MMIO initialization, enable/disable, error status, and cleaning.

## Important APIs, types, and functions
- `vnic_rq_alloc_bufs()` allocates block-based `struct vnic_rq_buf` arrays and links them into a circular ring.
- `vnic_rq_alloc_with_type()` hooks the RQ control resource, disables the queue, allocates the coherent descriptor ring, and allocates software buffers.
- `vnic_rq_alloc()` selects `RES_TYPE_RQ`.
- `vnic_rq_init()` writes ring base/size, CQ index, error interrupt settings, fetch/post indices, and resets dropped/error status.
- `vnic_rq_enable()` / `vnic_rq_disable()` control hardware running state.
- `vnic_rq_clean()` invokes a caller cleanup callback for every buffer, resets descriptor availability, repositions cursors from hardware `fetch_index`, syncs posted index, writes enable 0 to resync internal VIC state, and clears descriptor memory.

## Control flow and state
The software buffer ring is circular and tracks `to_use` and `to_clean`. Disable writes enable 0 twice and waits for `running` to clear each time because of a hardware mini-cache race. Clean handles surprise removal by treating `fetch_index == 0xFFFFFFFF` as zero.

## Dependencies and integration points
This file depends on `vnic_dev` resource/ring helpers and is used by ENIC receive setup and teardown. Higher-level `enic_rq.c` owns actual page allocation and packet indication callbacks.

## Risks and test signals
Risks include partial buffer allocation cleanup, RQ disable timeout, fetch-index wrap or surprise removal, descriptor availability reset to `count - 1`, and hardware stale mini-cache behavior. Test probe/remove, RQ reset, repeated up/down, RX ring wrap, and fault injection for allocation failure and disable timeout.
