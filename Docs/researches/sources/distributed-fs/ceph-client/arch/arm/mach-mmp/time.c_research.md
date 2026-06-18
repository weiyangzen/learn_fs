# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/time.c

Purpose: MMP/PXA timer clocksource, sched_clock, and one-shot clockevent driver.

Important APIs/types/functions: Defines `timer_read()`, `mmp_read_sched_clock()`, `timer_interrupt()`, `timer_set_next_event()`, `timer_set_shutdown()`, `timer_config()`, `mmp_timer_init()`, `mmp_dt_init_timer()`, clockevent `ckevt`, clocksource `cksrc`, and `TIMER_OF_DECLARE(mmp_timer, ...)`.

Control flow: DT init gets and enables the timer clock if present, otherwise falls back to 6.5 MHz for PJ4 or 3.25 MHz, maps the IRQ and registers, configures timer 1 as free-running clocksource/sched_clock and timer 0 as a one-shot match clockevent. `timer_read()` triggers a CVWR latch and reads it after a small delay because direct CR reads have metastability issues. The interrupt clears match status, disables timer 0, and calls the clockevent handler.

State and persistence: Global state is `mmp_timer_base`, registered sched_clock/clocksource/clockevent objects, and requested timer IRQ. Hardware state includes TMR_CCR, CMR, PLCR, ICR, IER, match registers, CER, and CVWR latch.

Dependencies and integration points: Depends on `regs-timers.h`, OF clock/IRQ/address APIs, clocksource/clockevents core, sched_clock, and MMP CPU type helpers.

Risks: Clock fallback rates are hard-coded and must match silicon. Timer register programming uses raw MMIO and assumes the mapped timer is stable. Failure after enabling a clock or mapping can leak partial state. Bad CVWR handling breaks timekeeping.

Test signals: Boot with `mrvl,mmp-timer`, verify sched_clock monotonicity, clockevent interrupts, one-shot timer accuracy, and fallback-rate platforms.
