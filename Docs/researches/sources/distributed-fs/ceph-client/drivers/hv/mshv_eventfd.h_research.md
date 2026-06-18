# sources/distributed-fs/ceph-client/drivers/hv/mshv_eventfd.h

## Purpose

`mshv_eventfd.h` declares the MSHV irqfd/ioeventfd data structures and APIs used by partition ioctl handling, IRQ routing, and SynIC interrupt acknowledgment.

## Important APIs, Types, and Functions

- `struct mshv_irqfd_resampler` tracks a GSI-level resample group and its ack notifier.
- `struct mshv_irqfd` stores one userspace eventfd-to-GSI binding, routing snapshot, wait entry, shutdown work, and optional resamplefd linkage.
- `struct mshv_ioeventfd` stores one MMIO doorbell-to-eventfd binding, including address, length, datamatch, wildcard flag, and Hyper-V doorbell ID.
- Public APIs initialize/release partition eventfd state, manage ack notifiers, set/unset irqfd/ioeventfd bindings, and manage the irqfd cleanup workqueue.

## Control Flow

Partition creation calls `mshv_eventfd_init()`. Partition ioctls copy user arguments and call `mshv_set_unset_irqfd()` or `mshv_set_unset_ioeventfd()`. Routing updates call `mshv_irqfd_routing_update()` via the root header declaration. EOI handling calls `mshv_notify_acked_gsi()` to drive resamplers. Partition release calls `mshv_eventfd_release()`.

## State and Persistence Behavior

The structures are heap allocated by `mshv_eventfd.c` and linked into per-partition hlist heads. Eventfd contexts are reference-counted. Shutdown work separates wait-queue detachment from object freeing.

## Dependencies and Integration Points

The header includes poll/eventfd-facing Linux types, `mshv.h`, and `mshv_root.h`. It is consumed by IRQ routing, root partition ioctl logic, and eventfd implementation.

## Risks and Edge Cases

The structs expose internal lock-sensitive fields; callers outside `mshv_eventfd.c` should not mutate list nodes, seqcounts, or contexts. Lifetime depends on cleanup workqueue initialization at module load and flushing during deassign/release.

## Test Signals

Build tests should catch type drift with `mshv_eventfd.c`. Runtime tests should verify partition init/release initializes all hlist heads and locks, irqfd workqueue lifecycle wraps module init/exit, and ack notifiers fire only for matching GSIs.
