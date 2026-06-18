# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_cq_copy.h

## Purpose

`vnic_cq_copy.h` provides the specialized completion queue service helper for FNIC copy work queues, where completion descriptors are FCPIO firmware request records rather than generic CQ descriptors.

## Important APIs, types, and data

- `vnic_cq_copy_service()` reads `struct fcpio_fw_req` entries from a `struct vnic_cq` ring.
- It uses `fcpio_color_dec()` to check ownership/color.
- The callback receives the vNIC device, queue index, and firmware request descriptor.

## Control flow

The helper starts at `cq->to_clean`, processes entries while descriptor color differs from `cq->last_color`, invokes the caller callback, advances and wraps the clean pointer, toggles software color on wrap, and honors a work budget.

## State and persistence behavior

State is inherited from `struct vnic_cq`: `to_clean`, `last_color`, and DMA ring memory. No additional state is owned by this header.

## Dependencies and integration points

It depends on FCPIO descriptor definitions in `fcpio.h` and generic CQ state from `vnic_cq.h`. It is used by FNIC firmware completion processing for copy WQs.

## Risks and edge cases

- The helper assumes the ring descriptor size matches `struct fcpio_fw_req`.
- Callback nonzero return leaves the current descriptor unconsumed.
- Color mismatch is the sole ownership test; descriptor initialization ordering depends on hardware and queue barriers.

## Test signals

Synthetic FCPIO completion rings should validate color handling, callback stop, budget exhaustion, and wraparound behavior.
