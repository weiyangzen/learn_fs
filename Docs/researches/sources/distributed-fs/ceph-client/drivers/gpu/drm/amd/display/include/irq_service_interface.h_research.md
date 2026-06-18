# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/irq_service_interface.h

Purpose: Declares the display IRQ service abstraction for enabling, acknowledging, destroying, and translating hardware interrupt sources into `dc_irq_source` values.

Important APIs and types: `struct irq_service_init_data` carries `dc_context`; `struct irq_service` is opaque. `dal_irq_service_set` enables/disables an IRQ source, `dal_irq_service_ack` acknowledges it, `dal_irq_service_to_irq_source` maps low-level `src_id`/`ext_id` pairs, and `dal_irq_service_destroy` releases the service.

Control flow: ASIC-specific code creates an IRQ service elsewhere, users call set/ack around interrupt registration and handling, and hardware interrupt IDs are translated before dispatching DC event logic.

State and persistence: State is held in the opaque service, likely including register tables, enabled masks, and context. The header itself is stateless.

Dependencies and integration points: Requires `dc_context` and `dc_irq_source` declarations from surrounding include context. Integrates with GPIO HPD IRQ creation, DC interrupt handlers, hotplug, vblank, and link event processing.

Risks: Wrong source translation can acknowledge or enable the wrong interrupt. The interface returns `bool`, so detailed failure cause is not exposed. Callers must not use a destroyed service or pass invalid enum sources.

Test signals: ASIC table tests for source translation, enable/disable register programming, ack idempotency, invalid source handling, and HPD/CPIRQ event propagation.
