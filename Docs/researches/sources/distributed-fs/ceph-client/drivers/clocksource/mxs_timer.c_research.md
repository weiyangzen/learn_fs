# sources/distributed-fs/ceph-client/drivers/clocksource/mxs_timer.c

Purpose: supports Freescale MXS TIMROT blocks on MX23 and MX28, using one timer for clockevents and another for clocksource. It handles the v1 16-bit hardware and v2 32-bit hardware differences.

Important APIs, types, and functions: static state includes `mxs_timrot_base`, `timrot_major_version`, and `mxs_clockevent_device`. Version-specific paths are `timrotv1_get_cycles()`, `timrotv1_set_next_event()`, and `timrotv2_set_next_event()`. Common paths include `timrot_irq_disable()`, `timrot_irq_enable()`, `timrot_irq_acknowledge()`, `mxs_irq_clear()`, `mxs_clockevent_init()`, `mxs_clocksource_init()`, and `mxs_timer_init()`.

Control flow: OF init maps the TIMROT block, obtains and enables the clock, resets the block with `stmp_reset_block()`, reads the major version from the appropriate offset, programs timer 0 as the event timer and timer 1 as the source timer, loads the source timer with max count, registers the clocksource, registers the clockevent, parses IRQ, and requests it with `IRQF_TIMER | IRQF_IRQPOLL`. The event IRQ acknowledges the timer interrupt and calls the clockevent handler.

State and persistence: runtime state is global and single-instance. Counter direction is down-counting, with inverted reads for clocksource. For v2, sched_clock is registered against the running count; v1 only registers a 16-bit clocksource. There is no dynamic cleanup after successful early registration.

Dependencies and integration points: depends on OF, clock framework, STMP reset helpers, `clocksource_mmio_init()`, clockevents, IRQ handling, and sched_clock for v2.

Risks: v1 and v2 use different register layouts and select values; wrong compatible/version offset breaks both source and event channels. `mxs_set_oneshot()` only clears IRQ state when already oneshot, so mode transitions rely on clockevent core ordering. Test signals include MX23 and MX28 boot coverage, correct counter width/range, no stale interrupt after shutdown, one-shot event delivery, and stable sched_clock on v2.
