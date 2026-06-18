# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_proxy.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_proxy.c

### Purpose
`intel_gsc_proxy.c` implements the i915 software proxy that relays messages between GT-integrated GSC firmware and CSME through the MEI GSC proxy component.

### Important APIs, Types, And Functions
Exports are `intel_gsc_proxy_init()`, `intel_gsc_proxy_fini()`, `intel_gsc_proxy_request_handler()`, and `intel_gsc_proxy_irq_handler()`. Internal pieces include `struct intel_gsc_proxy_header`, `struct gsc_proxy_msg`, `proxy_channel_alloc/free()`, `proxy_send_to_gsc()`, `proxy_send_to_csme()`, `validate_proxy_header()`, `proxy_query()`, and component bind/unbind callbacks.

### Control Flow
Initialization allocates a two-buffer GuC VMA channel and registers a typed component. Bind enables HECI2 interrupts and stores the MEI component; unbind clears it and disables interrupts. IRQ handling queues GSC work. The request handler waits for component binding, clears the HECI2 status bit, and runs `proxy_query()`: send query or CSME reply to GSC, wait for GSC output marker, validate GSC-to-CSME proxy header, send payload through MEI, receive CSME reply, validate CSME-to-GSC header, and repeat until GSC emits `PROXY_END`.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state lives in `gsc->proxy`: component pointer, component-added flag, channel VMA, two mapped buffers, and mutex. Dependencies include Linux component framework, MEI proxy ops, GSC HECI submit, runtime PM, uncore HECI2 registers, and ordered GSC workqueue. Integration includes firmware-load proxy establishment and later proxy interrupts. Risks include component bind timeout, invalid message sizes, header source/destination mismatches, marker visibility/order, MEI send/recv failures, and interrupt handling before binding. Test signals are proxy init FWSTS normal state, HECI2 IRQ flow, MEI exchange success, and firmware status transition to running.
