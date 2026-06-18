# sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-interrupt.c

Purpose: Platform driver that turns an arbitrary platform IRQ resource into an IIO trigger.

Important APIs/types/functions: `struct iio_interrupt_trigger_info` stores IRQ number. `iio_interrupt_trigger_probe()` allocates trigger state, requests the IRQ, and registers the trigger. `iio_interrupt_trigger_poll()` calls `iio_trigger_poll()`.

Control flow: probe obtains IRQ resource 0, combines resource trigger flags with `IRQF_SHARED`, allocates trigger named `irqtrig%d`, requests IRQ with trigger as private data, registers the trigger, and stores it as platform data. Remove unregisters the trigger, frees IRQ, state, and trigger object.

State and persistence: only runtime trigger object and IRQ binding.

Dependencies/integration: platform-device resources, Linux IRQ subsystem, and IIO trigger core.

Risks: shared IRQs can generate polls from unrelated interrupt sources if hardware does not filter. No `validate_device` callback limits consumers. Manual allocation/unwind paths must remain ordered.

Test signals: platform device with IRQ resource should create `irqtrigN`, interrupt should poll attached buffers, and remove should free shared IRQ cleanly.
