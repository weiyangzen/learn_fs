# sources/distributed-fs/ceph-client/arch/m68k/coldfire/pit.c

Purpose: Programmable Interrupt Timer clockevent and clocksource support for ColdFire parts with PIT hardware.

Important APIs and data: `cf_pit_set_periodic()`, `cf_pit_set_oneshot()`, `cf_pit_shutdown()`, `cf_pit_next_event()`, `cf_pit_clockevent`, `pit_tick()`, `pit_read_clk()`, `pit_clk`, and `hw_timer_init()`.

Control flow and state: `hw_timer_init()` configures clockevent timing parameters, registers the clockevent, requests `MCF_IRQ_PIT1`, and registers a 32-bit clocksource. Periodic mode reloads `PIT_CYCLES_PER_JIFFY`; oneshot mode enables interrupt without reload and `set_next_event` programs PMR. The IRQ handler clears PIF, advances `pit_cnt`, and calls the clockevent handler. Clocksource reads combine `pit_cnt` and the down-counter under local IRQ disable.

Dependencies and integration: Linux clockevents/clocksources, IRQ core, `mach_sched_init` assignment from SoC BSP files, and PIT register definitions.

Risks and test signals: frequency assumes `(MCF_CLK/2)/64`; oneshot minimum/maximum are 16-bit hardware limits. `pit_cnt` must remain coherent with IRQ clearing. Test periodic tick, oneshot high-res timers, clocksource monotonicity around interrupts, and failed IRQ request logging.
