## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-irqchip.c

### Purpose
`opal-irqchip.c` turns OPAL firmware event bits into Linux IRQs. It builds an IRQ domain for up to 64 OPAL events, handles firmware interrupt sources, records outstanding events, and wakes the OPAL poller thread when work is pending.

### Important APIs, Types, And Functions
Important pieces are `struct opal_event_irqchip`, `opal_handle_events()`, `opal_have_pending_events()`, `opal_interrupt()`, `opal_event_init()`, `opal_event_shutdown()`, and exported `opal_event_request()`. The local `irq_chip` supplies mask, unmask, and level-high type handling.

### Control Flow
Initialization finds `/ibm,opal`, creates a linear IRQ domain, determines OPAL interrupt resources from either standard `interrupts` or legacy `opal-interrupts`, maps them to Linux IRQs, and requests `opal_interrupt()` for each. The interrupt handler calls `opal_handle_interrupt()`, stores returned event bits in `last_outstanding_events`, and wakes `kopald`. The poller drains masked-in bits with `generic_handle_domain_irq()`, clears the cached event word, calls `opal_poll_events()`, and loops while firmware reports more events.

### State, Persistence, And Dependencies
State is global: the event mask, IRQ domain, resource array, IRQ count, and the last outstanding event bitmap. Masking is bit-level and controls which event bits become Linux IRQs. It depends on OPAL interrupt/poll calls, the core PowerNV poller in `opal.c`, Linux IRQ domains, and DT interrupt descriptions.

### Integration Points
`opal_event_init()` is a PowerNV arch initcall. Other OPAL services request event IRQs either through device tree interrupt mappings or the legacy exported `opal_event_request()`. Shutdown is called by `opal_shutdown()` before host reboot sync.

### Risks
`last_outstanding_events` is a single global cache written by interrupt context and drained by the poller, so lost-event resistance depends on polling firmware after clearing the cache. IRQ names allocated with `kasprintf()` are not freed after successful `request_irq()`. Legacy and new interrupt schemes must both stay functional.

### Test Signals
Test event delivery with masked/unmasked events, legacy and standard DT bindings, missing IRQ resources, shutdown from interrupt-disabled contexts, repeated firmware event bits that require level-style rehandling, and `opal_event_request()` before/after domain creation.
