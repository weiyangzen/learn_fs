# sources/distributed-fs/ceph-client/drivers/clocksource/timer-loongson1-pwm.c

Purpose: Loongson-1 PWM timer driver exposing one PWM timer as both clockevent and an emulated 24-bit clocksource.

Important APIs/types/functions: `ls1x_to` is a `timer_of` with base/clock/IRQ. `struct ls1x_clocksource` wraps a `clocksource` plus MMIO base and ticks-per-jiffy. Clockevent helpers set HRC/LRC period, clear/start/stop counter, acknowledge IRQ, and callbacks implement periodic, shutdown, resume, and next-event.

Control flow: init calls `timer_of_init()`, registers the clockevent with min 1 and 24-bit max, points the clocksource at the same base, stores period, and registers `ls1x_clocksource`. The ISR acknowledges, clears, restarts the PWM timer, then dispatches. Clocksource read combines `jiffies * ticks_per_jiffy` with the current PWM counter and uses a raw spinlock plus static old values to avoid apparent backward movement before jiffies catches up.

State/persistence: shared raw spinlock protects clockevent programming and clocksource read side effects. Static `old_count`/`old_jifs` inside the read function persist across calls.

Dependencies/integration: compatible `loongson,ls1b-pwmtimer`, `timer-of`, jiffies, clocksource/clockevents, IRQ.

Risks: clocksource read has side effects, making retry semantics delicate; the 24-bit mask may not represent the larger jiffies-composed value; sharing the same PWM hardware for event and source is sensitive to restarts. Tests should stress monotonic time, missed IRQ handling, periodic and one-shot mode, and lockdep/interrupt latency.
