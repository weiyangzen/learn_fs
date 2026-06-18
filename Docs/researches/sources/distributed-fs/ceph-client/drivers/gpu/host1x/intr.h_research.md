<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/intr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/intr.h

## Purpose

`intr.h` declares the generic host1x syncpoint interrupt lifecycle and fence-list manipulation APIs.

## Important APIs, Types, And Functions

- `struct host1x_intr_irq_data`: per-IRQ host pointer plus status-register offset.
- Init/deinit/start/stop functions for syncpoint IRQ management.
- `host1x_intr_handle_interrupt()` dispatches one syncpoint's pending threshold.
- `host1x_intr_add_fence_locked()` and `host1x_intr_remove_fence()` connect fences to interrupt hardware.

## Control Flow

The header has no direct flow. Hardware ISRs call `host1x_intr_handle_interrupt()`; fence code queues and removes fences through the declared helpers.

## State And Persistence Behavior

No state is stored here. The declared structures are used for devm IRQ callback data.

## Dependencies And Integration Points

It is shared by `intr.c`, `intr_hw.c`, `fence.c`, `syncpt.h`, and `dev.h`.

## Risks And Test Signals

Function signatures are cross-file contracts between generic and hardware interrupt code. Build coverage plus runtime fence signaling validate them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/intr.h -->
