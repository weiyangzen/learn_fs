# sources/distributed-fs/ceph-client/drivers/clocksource/timer-lpc32xx.c

Purpose: NXP LPC32xx/18xx/43xx timer driver that uses separate DT timer nodes/instances for one free-running clocksource and one match-based clockevent.

Important APIs/types/functions: `struct lpc32xx_clock_event_ddata` holds clockevent base and ticks-per-jiffy. `lpc32xx_clocksource_init()` configures a free-running timer and registers clocksource, sched_clock, and delay timer. `lpc32xx_clockevent_init()` configures match channel 0, registers clockevent, and requests IRQ.

Control flow: `lpc32xx_timer_init()` tracks static `has_clocksource` and `has_clockevent`; first compatible node successfully becomes clocksource, second becomes clockevent. Clockevent next-event resets the counter, writes MR0, and enables the timer; periodic mode enables interrupt/reset-on-match; one-shot adds stop-on-match. ISR clears MR0 interrupt and invokes handler.

State/persistence: global `clocksource_timer_counter` supports sched_clock and delay reads. Static flags control role assignment across compatible nodes. Clockevent state lives in the global ddata object.

Dependencies/integration: compatible `nxp,lpc3220-timer`, named `timerclk`, DT IRQ for event timer, clocksource/clockevents/sched_clock/current-timer-delay.

Risks: role assignment depends on DT probe order and successful init; no direct source/event distinction in compatible; cleanup on partial failures is present but boot-lifetime resources are retained. Test signals include two timer nodes, one selected clocksource, one clockevent IRQ, MR0 interrupt clearing, and delay timer registration.
