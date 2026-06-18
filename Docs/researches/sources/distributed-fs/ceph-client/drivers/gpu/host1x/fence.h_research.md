<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/fence.h

## Purpose

`fence.h` defines the host1x syncpoint fence and per-syncpoint fence-list structures used by `fence.c` and `intr.c`.

## Important APIs, Types, And Functions

- `struct host1x_syncpt_fence`: embedded `dma_fence`, atomic signaling guard, syncpoint pointer, threshold, timeout flag, delayed timeout work, and list node.
- `struct host1x_fence_list`: spinlock plus ordered list of pending fences.
- `host1x_fence_signal()` is the interrupt-facing signal hook.

## Control Flow

The header has no direct flow. Fences are inserted under the list spinlock, signaled from threshold interrupts, or cancelled via delayed work.

## State And Persistence Behavior

Fence objects persist until all DMA fence references are dropped. Fence lists persist in each syncpoint.

## Dependencies And Integration Points

It relies on DMA fence, delayed work, list, and spinlock types through includers. It is included by syncpoint and interrupt code.

## Risks And Test Signals

The list node must be initialized/deleted exactly once per queueing cycle. Build tests and fence race tests validate this small but central contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/fence.h -->
