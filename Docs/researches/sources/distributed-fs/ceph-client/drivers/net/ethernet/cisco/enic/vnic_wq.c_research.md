# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_wq.c

## Purpose
`vnic_wq.c` manages low-level Cisco vNIC work queues: software buffer ring allocation, resource binding, devcmd2 WQ allocation, MMIO initialization, enable/disable, error status, and cleanup.

## Important APIs, types, and functions
- `vnic_wq_alloc_bufs()` allocates block-based `struct vnic_wq_buf` arrays and links them into a circular doubly linked ring.
- `vnic_wq_alloc_with_type()` hooks a WQ control resource, disables the queue, allocates coherent descriptors, and allocates software buffers.
- `vnic_wq_alloc()` selects `RES_TYPE_WQ`.
- `enic_wq_devcmd2_alloc()` allocates a WQ backed by `RES_TYPE_DEVCMD2` for firmware command transport.
- `enic_wq_init_start()` writes ring base/size, fetch/post indices, CQ index, error interrupt settings, and error status.
- `vnic_wq_enable()` / `vnic_wq_disable()` control hardware running state.
- `vnic_wq_clean()` frees used buffers with a callback, resets cursors and hardware fetch/post/error registers, and clears descriptor memory.

## Control flow and state
Allocation mirrors RQ setup but WQ buffers include SOP/EOP completion ownership metadata and a `prev` pointer. Disable writes enable 0 and polls `running` with 10 microsecond delays. Clean walks only descriptors still used by hardware/software accounting, returns descriptor availability, then resets both hardware and software queue pointers.

## Dependencies and integration points
This file depends on `vnic_dev` ring/resource helpers and is used by ENIC TX resource allocation plus devcmd2 initialization in `vnic_dev.c`. Higher-level ENIC TX code encodes Ethernet descriptors before calling `vnic_wq_post()`.

## Risks and test signals
Risks include WQ disable timeout, incomplete cleanup on allocation failure, descriptor availability inconsistency, and devcmd2 WQ resource confusion with regular TX WQ resources. Test TX setup/teardown, devcmd2 command operation, repeated reset, TX ring wrap, and allocation-failure unwinding.
