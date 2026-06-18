# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_proxy.h

## Purpose
Declares the GSC-to-CSME proxy interface used by GSC firmware load/startup code and the IRQ layer.

## Important APIs
- `xe_gsc_proxy_init` allocates buffers and registers the MEI component.
- `xe_gsc_proxy_start` enables interrupts and triggers the first proxy exchange.
- `xe_gsc_proxy_init_done` and `xe_gsc_wait_for_proxy_init_done` inspect/wait for firmware proxy-normal state.
- `xe_gsc_proxy_request_handler` processes a pending software proxy transaction.
- `xe_gsc_proxy_irq_handler` bridges HECI2 interrupts into GSC workqueue actions.

## Integration and Risks
The header exposes no state, so users rely on `struct xe_gsc` internals from `xe_gsc_types.h`. Correct caller ordering is essential: init before start, start only after GSC firmware load, and IRQ handling only after component registration and workqueue setup.
