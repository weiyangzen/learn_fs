# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/event_sources.c

Purpose: Provides a small helper to request all interrupts described by a pseries `/event-sources` device-tree node.

Important APIs/types/functions: Implements `request_event_sources_irqs(struct device_node *np, irq_handler_t handler, const char *name)`.

Control flow: Iterates interrupt indexes 0 through 15, calls `of_irq_get()`, stops when no more IRQs are described, warns and continues on zero virq, and requests each valid IRQ with the supplied handler and name. Any `request_irq()` failure warns and stops.

State and persistence: No local state. Persistent effects are requested IRQ handlers owned by the interrupt subsystem.

Dependencies and integration points: Used by pseries event-source clients such as IO event IRQ setup. Depends on OF IRQ translation and Linux IRQ request APIs.

Risks: The helper has a hard limit of 16 IRQs and does not unwind already requested IRQs if a later request fails. It passes `NULL` as dev_id, so handlers/freeing must be compatible with that ownership model.

Test signals: Event-source node IRQ enumeration, IO event interrupt initialization, warning paths for bad OF IRQs, and interrupt delivery to registered handlers are relevant.

Source read size: 30 lines, 676 bytes.
