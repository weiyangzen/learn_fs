# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_cq.h

## Purpose

`vnic_cq.h` defines vNIC completion queue control registers, software queue state, symbol-renaming aliases for FNIC, and the inline completion service loop.

## Important APIs, types, and data

- `struct vnic_cq_ctrl` maps completion queue MMIO registers.
- `struct vnic_cq` stores queue identity, device pointer, MMIO control pointer, DMA ring, next descriptor to clean, and expected color.
- `vnic_cq_service()` decodes `struct cq_desc` records, calls a supplied queue-service callback, advances the clean index, toggles color on wrap, and stops at a work budget.
- Function prototypes expose allocation, initialization, cleanup, and release.

## Control flow

The service loop reads the descriptor at `to_clean`, decodes type/color/queue/completed index, and processes entries while hardware color differs from software `last_color`. Each accepted completion is passed to the caller's callback, then the consumer advances and wraps as necessary.

## State and persistence behavior

The in-memory `to_clean` and `last_color` fields are the key persistent software state between interrupts or poll cycles. Descriptor contents are device DMA state. The header itself allocates no state.

## Dependencies and integration points

It depends on `cq_desc.h` for descriptor decoding and `vnic_dev.h` for rings. It integrates with WQ, RQ, copy WQ, and FNIC completion paths.

## Risks and edge cases

- `work_done` is incremented after reading the next descriptor, so callbacks must not assume exactly one descriptor is consumed after a break.
- A callback returning nonzero stops service without advancing the current descriptor, which is intentional but can stall if the callback condition is persistent.
- Correct color behavior depends on hardware writing descriptors before flipping color.

## Test signals

Useful tests include synthetic rings with color transitions, budget-limited polling, callback-stop behavior, and wraparound at `desc_count`.
