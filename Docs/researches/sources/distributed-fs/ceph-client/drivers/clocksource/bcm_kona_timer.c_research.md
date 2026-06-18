# sources/distributed-fs/ceph-client/drivers/clocksource/bcm_kona_timer.c

Purpose: registers the Broadcom Kona peripheral timer as a oneshot clockevent source.

Important APIs/types/functions: `struct kona_bcm_timers`, `kona_timer_get_counter()`, `kona_timer_set_next_event()`, `kona_timer_shutdown()`, `kona_timer_interrupt()`, and `kona_timer_init()`.

Control flow: DT init gets rate from a clock or `clock-frequency`, maps IRQ and registers, disables pending compare state, registers a CPU0 oneshot clockevent, requests the timer IRQ, and arms the first event.

State and persistence: global `timers` holds IRQ and MMIO base; `arch_timer_rate` stores the event rate. Compare register 0 drives events.

Dependencies and integration points: depends on OF clocks/address/IRQ and clockevents.

Risks: `of_iomap()` and IRQ parse results are not checked before use. `clk_prepare_enable()` return is ignored. The 64-bit counter read retries only three times and returns `-ETIMEDOUT` on instability. The driver notes possible skew between interrupt and next-event programming.

Test signals: compatible strings `brcm,kona-timer` and deprecated `bcm,kona-timer`, IRQ delivery, counter-read retry failures, and clock-frequency fallback.
