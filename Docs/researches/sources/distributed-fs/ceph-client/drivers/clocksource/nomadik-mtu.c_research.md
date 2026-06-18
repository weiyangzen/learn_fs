# sources/distributed-fs/ceph-client/drivers/clocksource/nomadik-mtu.c

Purpose: configures the ST-Ericsson/Nomadik MTU block with timer 0 as a free-running down-counting clocksource/sched_clock/delay timer and timer 1 as a periodic or one-shot clockevent.

Important APIs, types, and functions: global state includes `mtu_base`, `clkevt_periodic`, `clk_prescale`, `nmdk_cycle`, and `mtu_delay_timer`. Main operations are `nomadik_read_sched_clock()`, `nmdk_clkevt_next()`, `nmdk_clkevt_reset()`, `nmdk_clkevt_shutdown()`, `nmdk_clksrc_reset()`, `nmdk_timer_interrupt()`, `nmdk_timer_init()`, and `nmdk_timer_of_init()`.

Control flow: OF init maps registers, obtains APB and timer clocks, parses the IRQ, and calls common init. Common init enables both clocks, chooses prescale 16 only for high input rates over 32 MHz, computes the periodic cycle count, starts timer 0 in free-running 32-bit mode, registers a down-count MMIO clocksource and sched_clock, requests timer 1 IRQ, configures the clockevent, and registers a current timer delay source. A next-event call unmasks timer 1, loads the value, and starts oneshot mode; the ISR clears timer 1 and calls the event handler.

State and persistence: state is mostly global and assumes one MTU instance. The `clkevt_periodic` flag drives resume/reset behavior. Hardware state is in MTU load/background-load/control/interrupt registers. No disk persistence exists.

Dependencies and integration points: uses OF clocks named `apb_pclk` and `timclk`, MMIO clocksource helpers, sched_clock, ARM delay timer registration, and Linux clockevent infrastructure.

Risks: rate and prescale selection directly affect timer range and resolution. Timer 1 supports both modes but resume synthesizes behavior based on `clkevt_periodic`, so state transitions must keep that flag correct. Test signals include stable clocksource reads, working delay timer calibration, one-shot and periodic ticks, suspend/resume reprogramming, and no missing clock or IRQ messages.
