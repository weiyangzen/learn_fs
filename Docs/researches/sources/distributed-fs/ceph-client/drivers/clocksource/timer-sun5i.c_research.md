# sources/distributed-fs/ceph-client/drivers/clocksource/timer-sun5i.c

Purpose: Allwinner high-speed timer platform driver for sun5i/sun7i, providing timer1 clocksource and timer0 clockevent with clock-rate notifier support.

Important APIs/types/functions: `struct sun5i_timer` stores base, clock, notifier, ticks-per-jiffy, clocksource, and clockevent. `sun5i_rate_cb()` unregisters/re-registers clocksource and updates event frequency around clock changes. Setup functions initialize source and event. Probe uses devm resources and optional reset.

Control flow: probe allocates state, maps MMIO, gets IRQ and enabled clock, validates rate, registers clock notifier, deasserts optional reset, sets up source, then event. Source loads timer1 with max and starts reload mode. Event enables timer0 IRQ, registers clockevent, then requests IRQ. Event callbacks stop/sync timer0, program interval low register, and start one-shot or periodic; ISR clears IRQ status and dispatches.

State/persistence: platform driver state is stored as drvdata and removed by unregistering clocksource. Clock notifier mutates framework registrations and `ticks_per_jiffy`.

Dependencies/integration: compatibles `allwinner,sun5i-a13-hstimer` and `allwinner,sun7i-a20-hstimer`, CCF notifier, reset controller, platform driver, clocksource/clockevents.

Risks: event interrupt is enabled before `devm_request_irq()`; clock-rate changes during active events can race with event programming; sync polling assumes timer1 running; remove only unregisters clocksource, relying on devm for IRQ/resources. Tests include rate-change notifier, reset deassert, min-delta underflow boundary, remove path, and one-shot/periodic events.
