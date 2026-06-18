# sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_dummy_evgen.c

Purpose: companion module for the IIO simple dummy driver that simulates event IRQs without hardware. It creates an IIO bus device named `iio_evgen` with `poke_ev0` through `poke_ev9` sysfs write attributes.

Important APIs/types/functions: `struct iio_dummy_eventgen` stores ten fake register records, an in-use bitmap, a mutex, and an IRQ simulation domain. `iio_dummy_evgen_get_irq()`, `iio_dummy_evgen_release_irq()`, and `iio_dummy_evgen_get_regs()` are exported for the dummy event code. `iio_evgen_poke()` parses a numeric event code, writes it into the selected fake register, and marks the mapped IRQ pending with `irq_set_irqchip_state()`.

Control flow: module init allocates singleton state, creates an IRQ sim domain, initializes a static device, names it `iio_evgen`, and adds it to `iio_bus_type`. Clients request an unused IRQ; sysfs poke files then raise the corresponding simulated interrupt. Module exit unregisters the device, whose release path removes the IRQ domain and frees state.

State/persistence: singleton RAM state tracks which fake IRQ slots are allocated and the most recent `reg_id`/`reg_data` per slot. State is not persistent and is cleared on module unload.

Dependencies/integration: depends on IIO bus/sysfs helpers, IRQ domains, IRQ simulation, exported GPL symbols, and dummy event consumers. It bridges user-triggered sysfs writes to kernel IRQ delivery.

Risks: `iio_dummy_evgen_release_irq()` assumes a valid singleton and valid IRQ data; misuse by a stale client can dereference invalid data. `iio_evgen_poke()` does not check whether an IRQ mapping exists before setting pending state. Allocation marks `inuse[i]` true without checking `irq_create_mapping()` failure. Test signals include exhaustion of ten slots, concurrent get/release/poke, module unload with active clients, and sysfs writes for all event codes.
