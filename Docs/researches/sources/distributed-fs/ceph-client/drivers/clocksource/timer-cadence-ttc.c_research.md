# sources/distributed-fs/ceph-client/drivers/clocksource/timer-cadence-ttc.c

Purpose: supports the Cadence Triple Timer Counter, using timer 1 as clocksource/sched_clock and timer 2 as clockevent. It handles 16- or 32-bit timer width and clock-rate change notifications.

Important APIs, types, and functions: `struct ttc_timer`, `struct ttc_timer_clocksource`, and `struct ttc_timer_clockevent` wrap per-timer MMIO, clocks, notifiers, and core devices. Important functions include `ttc_set_interval()`, `ttc_clock_event_interrupt()`, `__ttc_clocksource_read()`, `ttc_set_next_event()`, `ttc_shutdown()`, `ttc_set_periodic()`, `ttc_rate_change_clocksource_cb()`, `ttc_setup_clocksource()`, `ttc_rate_change_clockevent_cb()`, `ttc_setup_clockevent()`, and `ttc_timer_probe()`.

Control flow: built-in platform probe runs once, maps the TTC block, parses interrupt 1 for timer 2, reads optional `timer-width`, selects clock inputs based on each timer's clock-source bit, initializes timer 1 as a prescaled free-running clocksource, then initializes timer 2 as a prescaled interval clockevent and requests its IRQ. Event programming disables the counter, writes interval, resets, and re-enables it. The clocksource notifier adjusts the prescaler around power-of-two clock-rate changes; the event notifier updates clockevents frequency after rate changes.

State and persistence: state is heap allocated per role and retained for the kernel lifetime. Clocksource notifier caches old/new clock-control register values for abort handling. Hardware state is in TTC clock-control, count-control, interval, ISR, and IER registers.

Dependencies and integration points: uses platform driver probing, OF clocks/IRQ, clock notifiers, clocksource, clockevents, sched_clock, and module OF matching.

Risks: the clocksource prescaler notifier only accepts near-exact power-of-two rate ratios and must update before or after the parent change depending on direction. Event registration uses a fixed max delta of `0xfffe`, which may be too low for 32-bit mode. Test signals include probe-once behavior, correct timer-width mask, clock-rate change acceptance/rejection, periodic and oneshot events, and stable clocksource after clock changes.
