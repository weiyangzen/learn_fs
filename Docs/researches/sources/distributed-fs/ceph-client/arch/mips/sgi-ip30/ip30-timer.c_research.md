# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-timer.c

Purpose: IP30 timer support. It uses the MIPS CP0 compare interrupt for clock events and the HEART counter as a high-quality clocksource and sched_clock.

Important APIs and control flow: `ip30_heart_counter_read()` and `ip30_heart_read_sched_clock()` read `heart_regs->count`. `ip30_heart_clocksource_init()` registers a 52-bit HEART clocksource at `HEART_CYCLES_PER_SEC` and sched_clock. `plat_time_init()` installs the CP0 compare interrupt as a percpu clockevent, requests `c0_compare_interrupt`, enables it, and initializes HEART clocksource.

State, persistence, and integration: state includes `cp0_timer_irq_installed`, registered percpu IRQ, and the global `ip30_heart_clocksource`. Dependencies include initialized HEART registers and generic MIPS R4k clockevent. Risks include warning-only request failure, fixed HEART frequency, and needing per-CPU IRQ enablement during SMP finish. Test signals are HEART clocksource in `/sys/devices/system/clocksource`, timer IRQ counts, and stable sched_clock.
