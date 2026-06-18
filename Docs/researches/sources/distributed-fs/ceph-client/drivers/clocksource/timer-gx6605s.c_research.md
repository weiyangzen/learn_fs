# sources/distributed-fs/ceph-client/drivers/clocksource/timer-gx6605s.c

Purpose: supports the C-SKY GX6605S timer as a 32-bit free-running clocksource/sched_clock and one-shot clockevent using the `timer_of` helper.

Important APIs, types, and functions: register definitions cover status, value, control, config, divider, and initial value; `CLKSRC_OFFSET` selects the source timer area. Main routines are `gx6605s_timer_interrupt()`, `gx6605s_timer_set_oneshot()`, `gx6605s_timer_set_next_event()`, `gx6605s_timer_shutdown()`, the static `struct timer_of to`, `gx6605s_sched_clock_read()`, `gx6605s_clkevt_init()`, `gx6605s_clksrc_init()`, and `gx6605s_timer_init()`.

Control flow: OF init initializes timer resources through `timer_of_init()`, then configures the clockevent side at the base register range and the clocksource side at base plus `CLKSRC_OFFSET`. Clockevent setup clears divider/config and registers the device. Clocksource setup clears divider/initial value, resets and starts the source timer, registers sched_clock, and registers an up-counting MMIO clocksource. A next-event call resets the event timer, writes `ULONG_MAX - delta` to `TIMER_INI` so overflow occurs after the requested delta, and starts the timer. The ISR clears status, writes zero to `TIMER_INI`, and invokes the event handler.

State and persistence: `timer_of` stores base, clock, IRQ, and embedded clockevent. Hardware state is in per-timer value/config/control registers. There is no persistent storage or multi-instance handling beyond the static `timer_of`.

Dependencies and integration points: depends on `timer-of.h`, OF compatible `"csky,gx6605s-timer"`, clocksource MMIO helper, sched_clock, and clockevents.

Risks: event and source timers are separated by a fixed offset, so register-map changes are risky. Shutdown must clear enable/IRQ bits to avoid stale oneshot interrupts. Test signals include source timer monotonicity, one-shot event delivery, status clear behavior, correct clock rate from `timer_of`, and clean init through DT.
