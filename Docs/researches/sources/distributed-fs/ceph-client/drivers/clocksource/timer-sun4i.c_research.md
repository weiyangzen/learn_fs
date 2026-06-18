# sources/distributed-fs/ceph-client/drivers/clocksource/timer-sun4i.c

Purpose: Allwinner A10/A23/V3s/Suniv timer driver using timer1 as down-counting clocksource and timer0 as clockevent.

Important APIs/types/functions: static `timer_of to`; helpers stop/setup/start timer channels and synchronize after disable by polling timer1 for `TIMER_SYNC_TICKS`. `sun4i_timer_sched_read()` reads inverted timer1. Clockevent callbacks implement shutdown, periodic, one-shot, and next-event.

Control flow: init acquires base/clock/IRQ through `timer_of_init()`, programs timer1 reload/value as free-running OSC24M source, conditionally registers sched_clock on older SoCs without better arch timer, registers down-counting clocksource, configures timer0 source, stops it, clears interrupt, registers clockevent, and enables timer0 IRQ. Next-event subtracts sync ticks from delta before programming.

State/persistence: one static `timer_of` and source timer1 state. Interrupt enable register persists event routing.

Dependencies/integration: multiple Allwinner compatibles, `timer-of`, machine compatibility checks for sched_clock, MMIO clocksource/clockevents.

Risks: sync polling depends on timer1 running at same effective frequency; `evt - TIMER_SYNC_TICKS` underflows if event is too small but min delta is set to sync ticks; fixed OSC24M mux programming may conflict with clock description. Tests include old/new SoC sched_clock behavior, min-delta boundaries, IRQ clear/enable, and clocksource down-count conversion.
