# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_irq.c

## Purpose
`hvc_irq.c` provides reusable IRQ notifier callbacks for HVC backends. It lets transports that have a conventional Linux IRQ wake the generic HVC polling core when input or output progress is available.

## Important APIs, Types, and Functions
`notifier_add_irq()` requests an IRQ for an `hvc_struct` using `hvc_handle_interrupt()`. `notifier_del_irq()` frees it when present, and `notifier_hangup_irq()` delegates to delete. `hvc_handle_interrupt()` calls `hvc_poll()` on the device and kicks `khvcd` when polling requests more work.

## Control Flow
The generic HVC core calls backend notifier callbacks during tty open, close, and hangup. Backends that reuse this file pass an IRQ number as `hp->data`. If the IRQ is zero, `notifier_add_irq()` reports success and leaves the device in non-IRQ/polling mode. On interrupt, the handler polls the device immediately, then wakes the HVC thread if further read/write polling is needed.

## State and Persistence Behavior
The only persistent per-device state changed here is `hp->irq_requested`. IRQ handler lifetime is bound to tty open/close/hangup rather than backend probe/remove.

## Dependencies and Integration Points
It depends on Linux interrupt APIs and the HVC core. OPAL, VIO, Xen, and other IRQ-capable backends use these callbacks in their `hv_ops`.

## Risks and Edge Cases
Returning `IRQ_HANDLED` unconditionally is intentional because `khvcd` scans all devices, but it can obscure shared-IRQ diagnostics. Passing a stale or invalid IRQ number risks request/free mismatch. `hp->flags` is used as request flags, so backends must set it before open if shared IRQs are needed.

## Test Signals
Useful checks include request/free balance across open/close/hangup, shared-IRQ OPAL behavior, zero-IRQ fallback to polling, and interrupts causing HVC input to appear without waiting for the polling backoff.
