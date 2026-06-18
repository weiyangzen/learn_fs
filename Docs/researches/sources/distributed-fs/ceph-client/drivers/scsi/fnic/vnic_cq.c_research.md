# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_cq.c

## Purpose

`vnic_cq.c` implements allocation, initialization, cleanup, and release of vNIC completion queues. Completion queues are DMA rings populated by hardware and consumed by the driver.

## Important APIs, types, and functions

- `vnic_cq_alloc()` binds a CQ to a BAR resource and allocates its descriptor ring.
- `vnic_cq_init()` programs the CQ control registers: ring base/size, flow control, color, head/tail, interrupt controls, completion entry/message settings, and message address.
- `vnic_cq_clean()` resets software consumer state, hardware head/tail/color, and clears ring memory.
- `vnic_cq_free()` releases the coherent descriptor ring.

## Control flow

Probe/setup calls `vnic_cq_alloc()` for each completion queue and later `vnic_cq_init()` with interrupt and ring parameters. Interrupt or poll paths consume completions through the inline service function in `vnic_cq.h`. Reset/shutdown calls `vnic_cq_clean()` or `vnic_cq_free()`.

## State and persistence behavior

Persistent queue state is split between host memory (`cq->ring.descs`, `cq->to_clean`, `cq->last_color`) and memory-mapped control registers. `vnic_cq_clean()` sets software consumption back to descriptor zero and color zero while programming hardware tail color to one.

## Dependencies and integration points

The file depends on `vnic_dev_alloc_desc_ring()`, `vnic_dev_get_res()`, `vnic_dev_clear_desc_ring()`, and `writeq()/iowrite32()` register accessors. It is used by FNIC queue setup and by WQ/RQ completion handlers.

## Risks and edge cases

- Incorrect color initialization causes completions to be skipped or reread.
- Register programming must match the hardware's control layout from `struct vnic_cq_ctrl`.
- The code assumes descriptor memory allocation and MMIO resource discovery already respect device alignment requirements.

## Test signals

Tests should allocate/init/clean CQs under probe and reset, verify completions advance `to_clean` and wrap color correctly, and exercise both interrupt-enabled and CQ-entry/message modes where supported.
