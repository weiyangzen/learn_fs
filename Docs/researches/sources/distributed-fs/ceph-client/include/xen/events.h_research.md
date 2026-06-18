<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/events.h -->
# sources/distributed-fs/ceph-client/include/xen/events.h

## Purpose
This header declares Linux Xen event-channel APIs that bind Xen ports, VIRQ/IPI/PIRQ sources, and interdomain channels to Linux IRQs and handlers.

## Important APIs, Types, And Functions
- Binding APIs include `bind_evtchn_to_irq*`, `bind_evtchn_to_irqhandler*`, `bind_virq_to_irq*`, `bind_ipi_to_irqhandler()`, and interdomain late-EOI helpers.
- `unbind_from_irqhandler()` tears down IRQ bindings and closes the event channel.
- `xen_irq_lateeoi()` sends delayed EOI with `XEN_EOI_FLAG_SPURIOUS` where appropriate.
- Priority APIs map to FIFO event priorities.
- `evtchn_make_refcounted()`, `evtchn_get()`, and `evtchn_put()` manage userspace-exposed channel references.
- `notify_remote_via_evtchn()` sends `EVTCHNOP_send`; `notify_remote_via_irq()` maps from IRQ.
- Resume, pending/poll, callback vector, upcall, PIRQ/GSI/MSI, destroy, and debug interrupt APIs provide the rest of event lifecycle.
- `xen_evtchn_close()` closes a port and `BUG()`s on hypercall failure.
- `xen_fifo_events` reports FIFO ABI usage.

## Control Flow
Drivers bind a Xen port or virtual/physical interrupt to a Linux IRQ, optionally register a handler, receive upcalls through `xen_evtchn_do_upcall()`, notify peers via event sends, and unbind on teardown. Late-EOI channels require explicit `xen_irq_lateeoi()` after handling. Resume code rebinds or reconstructs event-channel state.

## State And Persistence
State is maintained by the Xen event subsystem: port-to-IRQ mappings, refcounts, IRQ priority, pending/masked bits in Xen shared structures, FIFO/2-level mode, and PIRQ/GSI/MSI allocations. The header declares interfaces only.

## Dependencies And Integration Points
It depends on Linux IRQ/MSI infrastructure, Xen event-channel public ABI, architecture hypercalls/events, Xenbus devices, PCI/MSI when enabled, and Xen callback/upcall setup.

## Risks And Edge Cases
Event-channel teardown must avoid use-after-close when userspace refcounts exist. Late EOI must not be omitted or events can stall. `xen_evtchn_close()` treats close failure as fatal. MSI/PIRQ paths require Dom0 privileges and correct sharing semantics.

## Test Signals
Signals include successful bind/unbind for evtchn/VIRQ/IPI/interdomain/PIRQ/MSI, delivery through handlers, late-EOI completion, pending poll behavior, remote notifications, resume rebinding, priority changes under FIFO mode, and refcounted userspace channels surviving expected lifetimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/events.h -->
