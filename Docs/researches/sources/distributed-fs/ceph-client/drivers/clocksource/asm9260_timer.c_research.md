# sources/distributed-fs/ceph-client/drivers/clocksource/asm9260_timer.c

Purpose: supports the AlphaScale ASM9260 timer block as a clocksource and system clockevent.

Important APIs/types/functions: global `priv`, `asm9260_timer_set_next_event()`, state callbacks for oneshot/periodic/shutdown, interrupt handler, and `asm9260_timer_init()`.

Control flow: DT init maps registers, enables the clock, requests the IRQ, configures all counters for count-up timer mode, registers TC1 as a 32-bit MMIO clocksource, sets MR1 to max and starts TC1, then configures TC0 as a clockevent.

State and persistence: global MMIO base and `ticks_per_jiffy` persist. TC0 is used for events; TC1 is used for free-running clocksource.

Dependencies and integration points: depends on OF address/IRQ/clock helpers, clockevents, and `clocksource_mmio_init`.

Risks: some error paths after mapping/clock acquisition do not fully release earlier resources. The driver assumes TC1 cannot run without a match register and sets MR1 to max. Clockevent cpumask is CPU0 only.

Test signals: DT compatible probing, periodic and oneshot timer interrupts, TC1 monotonic reads, clock enable failure paths, and CPU0-only event behavior.
