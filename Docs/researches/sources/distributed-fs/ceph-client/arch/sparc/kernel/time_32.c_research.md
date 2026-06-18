# sources/distributed-fs/ceph-client/arch/sparc/kernel/time_32.c

Purpose: implements sparc32 timer interrupt handling, clocksource/clockevent setup, per-CPU SMP clockevents, profile-PC correction, RTC platform registration, and time initialization.

Important APIs/types/functions: `profile_pc()`, `timer_interrupt()`, `setup_timer_ce()`, `timer_cs_read()`, `setup_timer_cs()`, `register_percpu_ce()`, Mostek RTC accessors, `clock_probe()`, `clock_init()`, `sparc32_late_time_init()`, `sbus_time_init()`, and `time_init()`. Globals include `timer_cs_lock`, `timer_cs_internal_counter`, `timer_ce`, `sparc32_clockevent`, `rtc_lock`, and `master_l10_counter`.

Control flow: platform IRQ code sets `sparc_config`; `time_init()` chooses PCI or SBUS timer setup and installs late init. Timer interrupts clear the platform clock IRQ, increment the software clocksource counter under seqlock when enabled, and invoke the global clockevent handler if enabled. Clocksource reads combine the interrupt count with the current L10 counter offset. SMP per-CPU clockevents program profile/L14 timers for periodic or oneshot events.

State and persistence: maintains in-memory clocksource counter, clockevent enabled flags, per-CPU clockevent devices, and RTC platform devices. RTC persistence is delegated to the RTC driver.

Dependencies and integration points: depends on platform `sparc_config` callbacks from sun4m/sun4d/PCI code, SBUS counters, clocksource/clockevents frameworks, M48T59 RTC driver, OF platform devices, and profiling.

Risks: timer counter read races are protected by seqlock; wrong offset calculation loses time around limit hits. SMP timer feature flags must match hardware. RTC probe only accepts primary address-bearing EEPROM.

Test signals: clocksource monotonicity, periodic tick delivery, per-CPU timer registration on SMP, oneshot profile timers where available, `udelay`/timekeeping stability, RTC registration for `mk48t02`/`mk48t08`, and profiling PC adjustment inside copy/zero/lock functions.
