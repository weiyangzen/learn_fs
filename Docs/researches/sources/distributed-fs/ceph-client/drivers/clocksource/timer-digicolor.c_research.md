# sources/distributed-fs/ceph-client/drivers/clocksource/timer-digicolor.c

Purpose: supports Conexant Digicolor timers using Timer B as the down-counting clocksource/sched_clock and Timer C as the periodic/one-shot clockevent. Timer A is intentionally avoided because watchdog support owns it.

Important APIs, types, and functions: `struct digicolor_timer` holds the clockevent, base, `ticks_per_jiffy`, and timer ID. Helper operations are `dc_timer_disable()`, `dc_timer_enable()`, and `dc_timer_set_count()`. Main routines are `digicolor_clkevt_shutdown()`, `digicolor_clkevt_set_oneshot()`, `digicolor_clkevt_set_periodic()`, `digicolor_clkevt_next_event()`, `digicolor_timer_interrupt()`, `digicolor_timer_sched_read()`, and `digicolor_timer_init()`.

Control flow: OF init maps shared timer/watchdog registers non-exclusively, parses the IRQ for Timer C, obtains/enables the timer clock, computes periodic ticks, configures Timer B with `UINT_MAX` and starts it, registers sched_clock and a down-counting MMIO clocksource, requests the Timer C IRQ, assigns cpumask and IRQ, and registers the clockevent. Next-event and periodic callbacks disable Timer C, program count, and enable the desired mode.

State and persistence: singleton state is in `dc_timer_dev`, clockevent core registration, and hardware control/count registers. Timer B remains enabled as free-running source. There is no disk persistence.

Dependencies and integration points: depends on OF clock/address/IRQ parsing, clocksource MMIO helpers, clockevents, sched_clock, and coordination with the watchdog sharing the same register block.

Risks: the register map is shared with watchdog, so exclusive mapping or Timer A use would conflict. Clockevent min delta is registered as zero, so very small deltas depend on hardware behavior. Test signals include watchdog coexistence, Timer B monotonic inverted reads, Timer C event delivery, valid IRQ index for Timer C, and no failed shared register mapping.
