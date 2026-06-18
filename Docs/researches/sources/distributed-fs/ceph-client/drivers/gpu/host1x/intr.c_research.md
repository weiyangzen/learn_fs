<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/intr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/intr.c

## Purpose

`intr.c` is the generic syncpoint fence interrupt manager. It maintains ordered fence lists per syncpoint, programs the next threshold into hardware, handles expired fences after IRQs, and requests syncpoint IRQ lines at probe.

## Important APIs, Types, And Functions

- `host1x_intr_add_fence_locked()` inserts a fence in threshold order and updates hardware state.
- `host1x_intr_remove_fence()` removes a queued fence from timeout/cancel paths and reprograms the next threshold.
- `host1x_intr_handle_interrupt()` loads the syncpoint value, signals all expired fences from the head of the list, and re-enables/disables hardware as needed.
- `host1x_intr_init()` initializes all fence lists, disables stale interrupts, allocates IRQ data, and requests each syncpoint IRQ.
- `host1x_intr_start()` initializes host sync hardware using the clock rate; `host1x_intr_stop()` disables all threshold interrupts.

## Control Flow

Fence insertion is done under the syncpoint fence-list spinlock already held by DMA fence code. The list is maintained ascending by threshold so IRQ handling can stop at the first unexpired fence. Hardware is programmed only for the first pending threshold per syncpoint. Probe-time IRQ setup supports multiple named syncpoint IRQs through `dev.c`.

## State And Persistence Behavior

Per-syncpoint fence lists persist in `struct host1x_syncpt`. Hardware threshold and interrupt-enable state mirrors the first pending fence. IRQ data is devm-managed for the host lifetime.

## Dependencies And Integration Points

Depends on `fence.c`, `syncpt.c`, hardware interrupt ops from `dev.h`, Linux IRQ APIs, and host clock for cycles-per-microsecond setup.

## Risks And Test Signals

Threshold ordering must handle 32-bit wrap comparisons consistently. Removing a fence from timeout races with IRQ signaling. Tests should cover multiple fences on one syncpoint, out-of-order threshold insertion, cancellation, timeout removal, suspend/resume interrupt reinitialization, and IRQ sharing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/intr.c -->
