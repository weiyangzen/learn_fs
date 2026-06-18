# sources/distributed-fs/ceph-client/arch/m68k/coldfire/dma_timer.c

Purpose: exposes ColdFire DMA timer 0 as a free-running clocksource and `sched_clock()` provider. It is used on parts where the DMA timer gives a stable 32-bit counter independent of the regular tick timer.

Important APIs and functions: `cf_dt_get_cycles()` reads `DTCN0`; `clocksource_cf_dt` names the source `coldfire_dma_timer`; `init_cf_dt_clocksource()` programs `DTXMR0`, clears events, sets no reference reload, enables `DTMR0` with divide-by-16, and registers the clocksource at `DMA_FREQ`; `sched_clock()` reads the same counter and scales cycles to nanoseconds with `cycles2ns()`.

Control flow and state: `arch_initcall(init_cf_dt_clocksource)` initializes timer registers once. State is entirely hardware counter state plus static clocksource metadata. No persistence exists across reset or suspend unless hardware preserves the counter.

Dependencies and integration: Linux clocksource and scheduler clock interfaces, raw MMIO helpers, `MCF_CLK`, `MCF_IPSBAR`, and DMA timer register layout. It complements, rather than replaces, `hw_timer_init()` tick devices.

Risks and test signals: the fixed frequency calculation assumes `(MCF_CLK / 2) / 16`; bad clock constants cause time drift. The 32-bit counter wraps in minutes, which the clocksource mask handles but `sched_clock()` consumers must tolerate. Test by verifying clocksource registration, monotonic reads across wrap, scheduler timestamp sanity, and no conflict with another user of DMA timer 0.
