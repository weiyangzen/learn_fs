# sources/distributed-fs/ceph-client/drivers/clocksource/timer-davinci.c

Purpose: supports TI DaVinci timers as clocksource, sched_clock, and one-shot clockevent providers. Standard mode uses TIM12 for events and TIM34 for source; a compare-offset mode uses TIM12 for both to avoid touching TIM34 when it may be used by DSP firmware.

Important APIs, types, and functions: `struct davinci_clockevent` wraps the event device, base, and compare offset. Global `davinci_clocksource` holds the source device, base, and counter offset for sched_clock. Important functions include `davinci_timer_init()`, `davinci_clockevent_set_next_event_std()`, `davinci_clockevent_set_next_event_cmp()`, `davinci_timer_irq_timer()`, `davinci_clocksource_init_tim34()`, `davinci_clocksource_init_tim12()`, `davinci_timer_register()`, and `of_davinci_timer_register()`.

Control flow: OF init collects MMIO and IRQ resources plus the clock, then calls the exported registration routine. Registration enables the clock, requests the memory region, maps it, resets the timer block into dual 32-bit unchained mode, allocates and configures a clockevent, requests the event IRQ, initializes the clocksource mode based on `cmp_off`, registers the clockevent, registers the clocksource, and installs sched_clock. Standard next-event mode reprograms TIM12 period and starts oneshot; compare mode writes a compare value at current time plus cycles.

State and persistence: runtime state is global source state, allocated event state, MMIO resource ownership, enabled clock, and timer control registers. There is no remove path for successful early registration.

Dependencies and integration points: integrates with `clocksource/timer-davinci.h`, OF address/IRQ tables, common clock framework, clocksource, clockevents, sched_clock, and external board code through `davinci_timer_register()`.

Risks: standard mode preserves TIM34 periodic operation while changing TIM12; compare mode must not disturb DSP-owned TIM34. IRQ resource indexes must match `DAVINCI_TIMER_CLOCKEVENT_IRQ`. Test signals include both standard and compare-offset configurations, TIM34 free-running source, TIM12 one-shot events, memory-region exclusion, and clean error unwinds on clock/IRQ/map failures.
