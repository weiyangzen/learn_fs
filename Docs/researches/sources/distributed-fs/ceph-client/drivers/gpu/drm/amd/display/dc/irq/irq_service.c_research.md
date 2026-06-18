# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/irq_service.c

Purpose: shared implementation of the display core IRQ service. It provides construction/destruction, source lookup, generic enable/ack register programming, hardware-source translation dispatch, and special HPD ack helpers.

Important APIs and functions: `dal_irq_service_construct()` stores `dc_context`; `dal_irq_service_destroy()` frees the heap service; `dal_irq_service_set()` validates a source, acknowledges it first, then invokes a source-specific `set` callback or `dal_irq_service_set_generic()`; `dal_irq_service_ack()` invokes a source-specific `ack` callback or `dal_irq_service_ack_generic()`; `dal_irq_service_to_irq_source()` dispatches to the ASIC-specific mapper; `hpd0_ack()` and `hpd1_ack()` acknowledge HPD and update interrupt polarity from delayed sense state.

Control flow: ASIC-specific create functions allocate `struct irq_service`, call this constructor, and install table/function pointers. Runtime enable goes `set -> find table -> ack current pending state -> callback/generic write`. Runtime ack goes `ack -> find table -> callback/generic write`. Hardware interrupt decode goes through the installed `to_dal_irq_source`.

State and persistence: the object stores `ctx`, `info`, and `funcs`. Generic set/ack mutate persistent hardware register fields through `dm_read_reg()`/`dm_write_reg()`. The service does not copy the IRQ table, so table lifetime must exceed service lifetime.

Dependencies and integration points: depends on `dm_services.h`, logger interface, register helpers, DCE/DCE/DCN service headers, and `irq_service_interface.h`. It is used by all DCE/DCN ASIC interrupt service variants and by display hotplug/page-flip/vblank consumers.

Risks: `dal_irq_service_set()` always acknowledges before enabling/disabling, which can clear pending state unexpectedly if a caller only intended to mask. Dummy callbacks warn and assert, so selecting dummy entries in production indicates an invalid source/hardware mismatch. HPD polarity helpers use hard-coded HPD0/HPD1 field macros and rely on macro compatibility.

Test signals: unit-style MMIO mocks can verify mask/value writes; integration tests are hotplug polarity behavior, vblank/page-flip interrupt delivery, invalid-source logging, and destruction nulling the caller's pointer.
