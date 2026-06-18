# sources/distributed-fs/ceph-client/drivers/clocksource/jcore-pit.c

Purpose: implements the J-Core programmable interval timer as a 32-bit MMIO clocksource, sched_clock provider, and per-CPU clockevent device. It also reads a seconds/nanoseconds pair from the PIT for stable high-level time reads.

Important APIs, types, and functions: `struct jcore_pit` contains a `clock_event_device`, per-CPU MMIO base, periodic delta, and precomputed enable word. `jcore_sched_clock_read()` reads `SECLO` and `NSEC` with retry against second rollover. `jcore_pit_set()`, `jcore_pit_disable()`, state callbacks, `jcore_timer_interrupt()`, `jcore_pit_local_init()`, and `jcore_pit_init()` are the main control paths.

Control flow: OF init maps the first PIT resource, parses the IRQ, registers the clocksource through `clocksource_mmio_init()` using `jcore_clocksource_read()`, registers sched_clock at `NSEC_PER_SEC`, allocates per-CPU PIT state, requests a percpu IRQ, computes the PIT enable register fields from the mapped hardware IRQ and priority bits, maps a PIT region for every present CPU, initializes each `clock_event_device`, and registers a CPU hotplug startup/teardown state. CPU startup derives frequency from `REG_BUSPD`, configures the device, and enables the percpu IRQ. The ISR disables the timer in oneshot mode and calls the event handler.

State and persistence: state is per-CPU allocated memory plus hardware throttle, enable, and bus-period registers. The IRQ programming value is static after init. There is no persistent state outside the kernel lifetime.

Dependencies and integration points: depends on OF address/IRQ parsing, percpu IRQs, CPU hotplug, `clocksource_mmio_init()`, sched_clock, and architecture IRQ mapping details exposed through `irq_get_irq_data()`.

Risks: the hardware IRQ encoding is unusual and mixes trap number and priority into the PIT enable word; interrupt-controller changes can break timer delivery. The driver maps one resource per present CPU and only logs if a CPU mapping is missing, so partial DT resources can leave CPUs without usable timer MMIO. Test signals include per-CPU hotplug tick setup, correct bus-period-derived rate, sched_clock monotonicity around second rollover, and no missing CPU PIT mappings.
