# sources/distributed-fs/ceph-client/drivers/clocksource/clps711x-timer.c

Purpose: supports Cirrus Logic CLPS711X timers as either a 16-bit down-counting clocksource or a periodic clockevent depending on DT alias id.

Important APIs/types/functions: `clps711x_clksrc_init()`, `_clps711x_clkevt_init()`, `clps711x_timer_interrupt()`, and `clps711x_timer_init()`.

Control flow: DT init maps the timer, resolves IRQ and clock, then switches on `of_alias_get_id(np, "timer")`. Alias 0 registers a 16-bit down-counting MMIO clocksource and sched_clock; alias 1 programs a prescaler and registers a periodic C3STOP clockevent.

State and persistence: global `tcd` stores the clocksource register for sched_clock. Clockevent device is heap-allocated and registered with its IRQ.

Dependencies and integration points: depends on OF aliases, OF IRQ/address, CCF, sched_clock, clocksource MMIO helpers, and clockevents.

Risks: the init function unmaps `base` even after successful registration, leaving registered clocksource/clockevent callbacks with unmapped MMIO. Clockevent only supports periodic mode. Alias configuration is required for correct role selection.

Test signals: DT alias role split, clocksource reads after init, periodic interrupt delivery, and memory mapping lifetime checks.
