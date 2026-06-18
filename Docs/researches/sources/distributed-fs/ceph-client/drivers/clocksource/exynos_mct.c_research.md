# sources/distributed-fs/ceph-client/drivers/clocksource/exynos_mct.c

Purpose: implements Samsung Exynos Multi-Core Timer support with a global free-running clocksource, optional global comparator, and per-CPU local clockevents.

Important APIs/types/functions: `exynos4_mct_write()`, `exynos4_read_count_64/32()`, `exynos4_clocksource_init()`, global comparator callbacks, per-CPU tick callbacks, `exynos4_timer_resources()`, `exynos4_timer_interrupts()`, `mct_init_dt()`, `mct_init_spi()`, and `mct_init_ppi()`.

Control flow: DT init reads local timer mapping, maps resources and clocks, parses global and local IRQs as SPI or PPI, installs CPU hotplug callbacks for local timers, starts/registers the global clocksource and sched_clock, and registers a global comparator clockevent unless the FRC is shared.

State and persistence: global MMIO base, clock rate, IRQ array, interrupt type, and per-CPU `mct_clock_event_device` objects persist. Hardware write-status polling ensures register writes have landed.

Dependencies and integration points: depends on OF, CCF, per-CPU IRQs or SPI affinity, CPU hotplug, sched_clock, delay timer, and clockevents.

Risks: several fatal resource failures call `panic()`. Write completion polling can panic if hardware hangs. Interrupt topology and `samsung,local-timers` must match CPU layout. Shared FRC mode disables the global comparator path.

Test signals: Exynos4210 SPI and Exynos4412 PPI compatibles, CPU hotplug, local timer mapping property, global clocksource monotonicity, global comparator periodic/oneshot behavior, and write-status timeout tests.
