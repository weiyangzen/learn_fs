# sources/distributed-fs/ceph-client/drivers/clocksource/timer-atmel-pit.c

Purpose: supports the AT91SAM926x Periodic Interval Timer as a combined periodic clockevent and software-extended clocksource running from master clock divided by 16.

Important APIs, types, and functions: `struct pit_data` holds the clockevent, clocksource, MMIO base, cycle length, accumulated count, IRQ, and master clock. Main paths are `read_pit_clk()`, `pit_clkevt_shutdown()`, `pit_clkevt_set_periodic()`, `at91sam926x_pit_reset()`, suspend/resume callbacks, `at91sam926x_pit_interrupt()`, and `at91sam926x_pit_dt_init()`.

Control flow: DT init allocates state, maps registers, gets/enables the master clock, parses IRQ, computes `pit_rate` and the HZ cycle value, resets and starts the PIT without IRQ, registers a clocksource whose mask combines PICNT and interval width, requests the shared timer IRQ, and registers a periodic-only clockevent. Periodic mode updates the software count using `PIVR`, then enables PIT interrupts. The ISR checks PIT status, folds elapsed hardware intervals into `cnt`, and invokes the event handler.

State and persistence: persistent runtime state is `data->cnt`, which extends the PIT's interval counter into a clocksource. Hardware mode register controls whether IRQs are enabled. Suspend disables the timer; resume resets it without enabling IRQ until periodic mode is selected again.

Dependencies and integration points: depends on OF address/IRQ/clock parsing, shared IRQ handling, clocksource, clockevents, and raw local IRQ save around clocksource reads.

Risks: this is periodic-only and uses software accumulation, so delayed interrupts and status reads must be correct or timekeeping drifts. `cycle - 1` must fit the PIT interval field. Test signals include stable periodic ticks, correct accumulated clocksource under delayed interrupts, suspend/resume reset, shared IRQ returning `IRQ_NONE` when appropriate, and no cycle-size warnings.
