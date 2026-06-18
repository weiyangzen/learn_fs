# sources/distributed-fs/ceph-client/drivers/clocksource/timer-ep93xx.c

Purpose: supports Cirrus EP93xx timers using Timer 4, a 40-bit free-running down-counter, as clocksource/sched_clock and Timer 3, a 32-bit interrupting timer, as one-shot clockevent.

Important APIs, types, and functions: `struct ep93xx_tcu` holds the MMIO base and global `ep93xx_tcu` exposes it to callbacks. Main functions are `ep93xx_clocksource_read()`, `ep93xx_read_sched_clock()`, `ep93xx_clkevt_set_next_event()`, `ep93xx_clkevt_shutdown()`, `ep93xx_timer_interrupt()`, and `ep93xx_timer_of_init()`.

Control flow: OF init allocates state, maps registers, parses one IRQ, enables Timer 4 high-byte latching, registers a 40-bit clocksource using a custom read callback, registers sched_clock, requests the Timer 3 IRQ, and registers the one-shot clockevent at the fixed Timer 1/2/3 rate. Next-event programming disables/clears Timer 3, writes the load value, and enables it with mode and clock-select bits. The ISR clears Timer 3 by writing its clear register and dispatches the event handler.

State and persistence: state is global and singleton. Timer rates are fixed constants, not DT clocks. Runtime state is in Timer 3/4 control/value registers and the registered devices.

Dependencies and integration points: uses OF address/IRQ, non-atomic low-high 64-bit MMIO helper, clocksource MMIO wrapper with a callback that ignores the passed base, sched_clock, and clockevents.

Risks: Timer 4 read depends on the hardware low-read latching high byte. Fixed frequencies must match silicon. The clockevent name is `"timer1"` despite using Timer 3, which is harmless but confusing. Test signals include 40-bit monotonic source reads, Timer 3 interrupt delivery, no IRQ parse failure, and sched_clock stability.
