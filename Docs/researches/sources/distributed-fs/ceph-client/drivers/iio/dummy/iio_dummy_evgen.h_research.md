# sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_dummy_evgen.h

Purpose: private header defining the fake register structure and exported event-generator API used by the IIO simple dummy event implementation.

Important APIs/types/functions: `struct iio_dummy_regs` holds `reg_id` and `reg_data`, the two fields the event handler reads to determine which fake event was triggered. The declarations are `iio_dummy_evgen_get_regs(int irq)`, `iio_dummy_evgen_get_irq(void)`, and `iio_dummy_evgen_release_irq(int irq)`.

Control flow: event-enabled dummy instances call `get_irq()`, call `get_regs()` for that IRQ, and later call `release_irq()` during teardown. The header intentionally exposes only slot allocation and register access, leaving sysfs poke implementation private to `iio_dummy_evgen.c`.

State/persistence: no direct state. The returned `struct iio_dummy_regs *` points into the singleton event generator state and is valid only while the IRQ mapping and module state remain alive.

Dependencies/integration: guarded by `_IIO_DUMMY_EVGEN_H_` and included by both producer and consumer C files. The companion C file exports these symbols with GPL visibility.

Risks: the API has no ownership type or lifetime annotation; callers must pair get/release correctly and not retain the register pointer after release. Test signals include compile coverage with `CONFIG_IIO_SIMPLE_DUMMY_EVENTS=y` and symbol availability when `IIO_DUMMY_EVGEN=m`.
