# sources/distributed-fs/ceph-client/drivers/clocksource/dw_apb_timer_of.c

Purpose: Device Tree glue that instantiates DesignWare APB timers as one clockevent and one clocksource/sched_clock.

Important APIs/types/functions: `timer_get_base_and_rate()`, `add_clockevent()`, `add_clocksource()`, `init_sched_clock()`, `read_sched_clock()`, and `dw_apb_timer_init()`.

Control flow: each matching DT timer increments `num_called`. The first discovered timer becomes clockevent; the second becomes clocksource and sched_clock, unless a separate sched-clock compatible node is found. Base/rate setup maps registers, optionally resets hardware, enables optional `pclk`, and derives rate from properties or the `timer` clock.

State and persistence: global `sched_io_base`, `sched_rate`, and `num_called` persist after init. Mapped timer bases and clocks remain live on success.

Dependencies and integration points: consumes `dw_apb_timer.c` exported helpers, OF clock/reset/IRQ/address APIs, sched_clock, and ARM delay timer registration.

Risks: timer role depends on DT probe order. Some failures call `panic()` instead of returning errors. Optional `pclk` enable failures only warn. Successful clock references are intentionally retained.

Test signals: DTs with one/two APB timers, separate `picochip,pc3x2-rtc` sched-clock node, reset-control presence, and event/source role assignment.
