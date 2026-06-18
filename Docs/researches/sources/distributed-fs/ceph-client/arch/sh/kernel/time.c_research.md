# sources/distributed-fs/ceph-client/arch/sh/kernel/time.c

Purpose: initializes SH clocksource/clockevent infrastructure and late earlytimer probing.

Important APIs and control flow: `time_init()` calls generic `timer_probe()`, initializes SH clocks with `clk_init()`, and assigns `late_time_init` to `sh_late_time_init()`. The late function registers all `earlytimer` platform drivers and probes two devices, allowing clockevent and clocksource devices to appear while tolerating a missing clocksource by falling back to jiffies.

State, dependencies, and risks: state includes clock framework registration and the `late_time_init` callback pointer. Dependencies include early platform driver infrastructure, SH clock code, RTC/timex integration, and generic timer probing. Risks include timer init ordering, only probing two earlytimers, and clocksource fallback hiding platform timer failures. Test signals are boot timer logs, clocksource selection, tick delivery, and earlytimer driver probe counts.
