# sources/distributed-fs/ceph-client/drivers/clocksource/timer-gxp.c

Purpose: HPE GXP boot-time timer driver providing a 32-bit MMIO timestamp clocksource/sched_clock and a one-shot clockevent backed by timer0. It also exposes the shared timer register block to a watchdog child device through a later platform-driver probe.

Important APIs/types/functions: `struct gxp_timer` stores counter/control MMIO and `clock_event_device`; `gxp_timer_init()` is registered by `TIMER_OF_DECLARE("hpe,gxp-timer")`; `gxp_time_set_next_event()` arms timer0; `gxp_timer_interrupt()` acknowledges terminal-count state and dispatches `event_handler`; `gxp_timer_probe()` creates a `gxp-wdt` platform device. It uses `clocksource_mmio_init()`, `sched_clock_register()`, `clockevents_config_and_register()`, `request_irq()`, `of_iomap()`, and CCF clock APIs.

Control flow: init allocates the singleton, enables the DT clock, maps registers, initializes `system_clock`, registers the clocksource/sched_clock at the hardware clock rate, configures clockevents at fixed `TIMER0_FREQ`, then requests a shared timer IRQ. On an event, it clears TC, writes the count, enables the timer, and the ISR verifies TC before acknowledging and invoking the clockevent core.

State/persistence: global `gxp_timer` and `system_clock` are boot-lifetime state. The clock reference is not retained for later disable, and the watchdog child receives the timer counter base as platform data.

Dependencies/integration: device tree compatible `hpe,gxp-timer`, one clock, one IRQ, Linux clocksource/clockevents/sched_clock, platform bus, and watchdog driver naming contract.

Risks: duplicate `irq_of_parse_and_map()` call, no cleanup after a successful clocksource if later IRQ request fails, fixed clockevent frequency may diverge from `clk_get_rate()`, singleton lifetime, and shared IRQ requires correct TC filtering. Test signals include DT boot logs, `/proc/timer_list`, clocksource selection, one-shot tick operation, and watchdog child creation.
