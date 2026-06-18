# sources/distributed-fs/ceph-client/drivers/clocksource/timer-tegra.c

## Purpose

`timer-tegra.c` is the legacy NVIDIA Tegra clocksource and per-CPU clockevent driver for Tegra20-era through Tegra210 timer blocks, plus a suspend-nonstop RTC clocksource. It programs the timer microsecond counter to 1 MHz, registers `timer_us` as the sched clock and generic clocksource, and creates per-CPU clockevent devices backed by timer instances and DT IRQs.

## APIs And Flow

Core state is `usec_config`, `timer_reg_base`, per-CPU `struct timer_of tegra_to`, and `suspend_rtc_to`. `tegra_init_timer()` is shared by `nvidia,tegra210-timer` and `nvidia,tegra20-timer`. It initializes `timer_of`, selects a `TIMERUS_USEC_CFG` divider for supported parent rates, maps per-CPU IRQs, requests them, registers sched_clock and `timer_us`, installs the ARM delay timer when applicable, and registers CPU hotplug callbacks. Clockevent callbacks program PTV using the hardware n+1 convention, clear PCR interrupts, and call the event handler.

## State, Dependencies, Risks, Tests

Hardware registers retain timer programming; resume rewrites the microsecond divider. RTC suspend time uses shadow seconds and millisecond registers and must avoid races with the RTC driver. Dependencies include OF address/IRQ parsing, `timer-of`, clocksource/clockevents, CPU hotplug, cpumasks, sched_clock, and ARM delay timer support. Risks are unsupported parent rates, DT IRQ ordering, n+1 off-by-one mistakes, RTC shadow races, and SoC rating choices. Test boot logs, clocksource selection, CPU hotplug, suspend/resume, sched_clock monotonicity, and per-CPU timer interrupt affinity.
