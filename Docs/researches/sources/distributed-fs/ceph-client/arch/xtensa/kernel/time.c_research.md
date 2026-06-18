# sources/distributed-fs/ceph-client/arch/xtensa/kernel/time.c

Purpose: Implements Xtensa `ccount` clocksource, per-CPU clockevent timers, sched_clock registration, CPU frequency calibration, and delay calibration.

Important APIs, types, and functions: `ccount_freq`, `ccount_read()`, `ccount_sched_clock_read()`, `struct ccount_timer`, `ccount_timer_set_next_event()`, `ccount_timer_shutdown()`, `ccount_timer_set_oneshot()`, `timer_interrupt()`, `local_timer_setup()`, `calibrate_ccount()`, `time_init()`, and `calibrate_delay()`.

Control flow: `time_init()` initializes clocks, derives `ccount_freq` from OF clock or platform/config, registers the 32-bit `ccount` clocksource, sets up CPU0 clockevent, requests the timer IRQ, registers sched_clock, and calls `timer_probe()`. Per-CPU setup maps `LINUX_TIMER_INT`, configures clockevents, and later enables/disables IRQs using balanced state tracking.

State and persistence: Exports global CPU clock frequency and maintains per-CPU timer device state (`irq_enabled`, IRQ number, cpumask, name). `loops_per_jiffy` is preset from `ccount_freq`.

Dependencies and integration: Depends on `get_ccount()`, `set_linux_timer()`, OF clocks, clocksource/clockevents, IRQ mapping, scheduler clock, platform calibration, SMP local timer setup, and generic timer probing.

Risks: Incorrect or zero `ccount_freq` breaks timekeeping and delay loops; `set_next_event()` detects already-expired deadlines with wrap-sensitive subtraction; timer IRQ cannot be disabled at device level, so nested IRQ enable/disable accounting matters.

Test signals: Boot time calibration logs, clocksource registration, tick delivery on CPU0 and secondary CPUs, high-resolution timer behavior, suspend/tick resume if applicable, and delay-loop sanity.
