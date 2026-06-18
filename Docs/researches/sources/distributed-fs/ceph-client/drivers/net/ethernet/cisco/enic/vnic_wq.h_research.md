# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_wq.h

## Purpose
`vnic_wq.h` defines the vNIC work queue MMIO layout, software WQ/ring buffer structures, devcmd2 controller structure, inline posting/service helpers, and WQ management prototypes.

## Important APIs, types, and functions
- `struct vnic_wq_ctrl` mirrors WQ hardware registers.
- `struct vnic_wq_buf` stores per-descriptor OS buffer, DMA address, length, index, SOP, descriptor pointer, write ID, completion request, skip count, compressed-send flag, and previous pointer.
- `struct vnic_wq` stores queue index, vdev, control pointer, descriptor ring, buffer blocks, `to_use`, `to_clean`, and packet accounting.
- `struct devcmd2_controller` stores devcmd2 command WQ state, result ring, posted/result/color cursors, and result size.
- `vnic_wq_doorbell()` writes the posted index after a write barrier.
- `vnic_wq_post()` records buffer metadata and advances `to_use`/availability.
- `vnic_wq_service()` walks buffers until the completed index is reached and calls a completion callback.

## Control flow and state
WQ posting is split between descriptor encoding by callers, software buffer metadata update, and explicit doorbell write. Completion service returns one descriptor at a time until the completion index is reached. Devcmd2 reuses the same WQ hardware format for firmware commands.

## Dependencies and integration points
The header is used by ENIC TX, `vnic_wq.c`, and `vnic_dev.c` devcmd2. It depends on `vnic_dev.h`, `vnic_cq.h`, and PCI declarations.

## Risks and test signals
Missing doorbells, wrong skip-count accounting, or completion callback ownership mistakes can stall TX or leak SKBs. Test TX with SG/TSO, queue stop/wake, devcmd2 command ring operation, and ring wrap.
