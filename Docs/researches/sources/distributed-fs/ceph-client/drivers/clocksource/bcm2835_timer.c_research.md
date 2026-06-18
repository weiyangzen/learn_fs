# sources/distributed-fs/ceph-client/drivers/clocksource/bcm2835_timer.c

Purpose: supports the BCM2835 system timer as a 32-bit clocksource/sched_clock and one compare channel as a oneshot clockevent.

Important APIs/types/functions: `struct bcm2835_timer`, `bcm2835_sched_read()`, `bcm2835_time_set_next_event()`, `bcm2835_time_interrupt()`, and `bcm2835_timer_init()`.

Control flow: DT init maps registers, reads `clock-frequency`, registers sched_clock and a 32-bit MMIO clocksource from the low counter, maps the default timer IRQ, allocates a timer object, requests a shared IRQ, and registers a oneshot clockevent using compare channel 3.

State and persistence: `system_clock` global points to the counter low register; allocated timer object stores control/compare addresses and event device state.

Dependencies and integration points: depends on OF register/IRQ parsing, sched_clock, MMIO clocksource helpers, and shared interrupt handling.

Risks: only the low 32 bits are used despite a high counter register. Default channel 3 and IRQ index are hardcoded. Event handler is read with `READ_ONCE()` to tolerate early interrupts. Successful resources are permanent.

Test signals: Raspberry Pi DT boot, compare interrupt delivery, shared IRQ behavior, sched_clock monotonicity, and 32-bit wrap handling.
