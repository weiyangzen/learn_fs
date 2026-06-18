# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_rq.h

## Purpose
`vnic_rq.h` defines the vNIC receive queue MMIO layout, software RQ/ring buffer structures, cursor/posting inline helpers, and RQ management prototypes.

## Important APIs, types, and functions
- `struct vnic_rq_ctrl` mirrors hardware RQ control registers.
- `struct vnic_rq_buf` stores per-descriptor OS buffer pointer, DMA address, length, index, descriptor pointer, write ID, page offset, and truesize.
- `struct vnic_rq` stores index, vdev, control pointer, descriptor ring, block-allocated buffer arrays, `to_use`, `to_clean`, and packet accounting.
- `vnic_rq_desc_avail()`, `vnic_rq_desc_used()`, `vnic_rq_next_desc()`, and `vnic_rq_next_index()` expose queue state.
- `vnic_rq_post()` records buffer metadata, advances `to_use`, decrements `desc_avail`, and periodically writes `posted_index` after a write memory barrier.
- `vnic_rq_service()` walks cleaned buffers until a completed index is reached.
- `vnic_rq_fill()` calls a refill callback while descriptors are available.

## Control flow and state
RQ software ownership is tracked by descriptor availability and the `to_use`/`to_clean` circular buffer pointers. Hardware ownership is communicated by writing `posted_index` every `VNIC_RQ_RETURN_RATE` descriptors after descriptors have been initialized.

## Dependencies and integration points
ENIC RX refill and completion code uses these helpers. The header depends on `vnic_dev.h`, `vnic_cq.h`, PCI, and netdevice declarations.

## Risks and test signals
Incorrect availability math or missing write barrier can let hardware fetch stale descriptors. Test with RX refill pressure, ring wrap, skipped completions, and queue reset while traffic is active.
