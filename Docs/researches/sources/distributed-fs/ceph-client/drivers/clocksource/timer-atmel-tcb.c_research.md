# sources/distributed-fs/ceph-client/drivers/clocksource/timer-atmel-tcb.c

Purpose: uses an Atmel Timer Counter Block as a high-resolution clocksource, sched_clock, delay timer, and optional channel-2 clockevent. Older 16-bit hardware chains channels 0 and 1 into a 32-bit source; newer 32-bit hardware uses channel 0 alone.

Important APIs, types, and functions: global `tcaddr`, `tcb_cache`, and `bmr_cache` support timer access and suspend state. Clocksource functions are `tc_get_cycles()`, `tc_get_cycles32()`, `tc_clksrc_suspend()`, and `tc_clksrc_resume()`. Clockevent functions include `tc_shutdown()`, `tc_set_oneshot()`, `tc_set_periodic()`, `tc_next_event()`, `ch2_irq()`, and `setup_clkevents()`. Setup helpers are `tcb_setup_dual_chan()`, `tcb_setup_single_chan()`, and `tcb_clksrc_init()`.

Control flow: init runs once, maps the parent TCB, obtains channel and slow clocks, parses an IRQ, matches counter width, disables all interrupts, enables channel 0 clock, chooses the best divisor over roughly 5 MHz, configures either single-channel or chained dual-channel clocksource, registers the clocksource, sets up channel 2 clockevents, then registers sched_clock and delay timer. Channel 2 uses RC compare in periodic or oneshot mode.

State and persistence: suspend caches CMR/IMR/RC/clock-enable state for all three channels plus BMR, and resume restores channels and synchronizes them. `tcaddr` is the singleton guard. Runtime state also lives in TC registers and enabled clocks.

Dependencies and integration points: depends on Atmel TCB SoC definitions, OF parent-node clocks/IRQs, clocksource, clockevents, sched_clock, delay timer, and syscore-style clocksource suspend callbacks.

Risks: divisor selection, 16-bit chaining, and channel-2 clock choice differ by hardware. For 16-bit event mode, channel 2 may use slow clock while the clocksource uses divided master clock. Test signals include both 16-bit and 32-bit compatible coverage, stable chained reads, clockevent periodic and oneshot operation, suspend/resume register restoration, and delay timer calibration.
