# sources/distributed-fs/ceph-client/drivers/clocksource/mps2-timer.c

Purpose: supports ARM MPS2 timers as one free-running down-counting clocksource/sched_clock and one interrupt-driven clockevent. Multiple matching DT nodes are consumed one at a time: the first successful node becomes clocksource, and another becomes clockevent.

Important APIs, types, and functions: `struct clockevent_mps2` stores the register base, per-tick reload count, and clockevent. `mps2_sched_read()`, `mps2_timer_shutdown()`, `mps2_timer_set_next_event()`, `mps2_timer_set_periodic()`, `mps2_timer_interrupt()`, `mps2_clockevent_init()`, `mps2_clocksource_init()`, and `mps2_timer_init()` are the main routines.

Control flow: init first attempts `mps2_clocksource_init()`, using either `clock-frequency` or a DT clock. It maps registers, disables the timer, loads `0xffffffff` into value and reload, starts it, registers a down-counting MMIO clocksource, and registers sched_clock. Later matching calls initialize the clockevent by mapping a register block, parsing IRQ, allocating `clockevent_mps2`, disabling the timer, requesting the IRQ, and registering periodic plus one-shot clockevents. The ISR checks the interrupt status register, clears it, and invokes the event handler.

State and persistence: the static booleans `has_clocksource` and `has_clockevent` prevent duplicate registration. Clocksource base is stored in `sched_clock_base`; clockevent state is heap allocated and effectively permanent after early init. Hardware state is in control, value, reload, and interrupt registers.

Dependencies and integration points: uses OF clocks or `clock-frequency`, OF IRQ/address mapping, `clocksource_mmio_init()`, sched_clock, clockevents, and IRQF_TIMER handling.

Risks: DT must expose enough compatible timer instances because a single node cannot become both source and event in one call path. The clocksource and event timers may use separate clock resources, so mismatched rates are possible. The interrupt handler returns `IRQ_NONE` for a zero status, making spurious interrupts visible. Test signals include two MPS2 timer nodes registering both roles, monotonic down-count clocksource reads, periodic and one-shot event delivery, and no failed clock or IRQ messages.
