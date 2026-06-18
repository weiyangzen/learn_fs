# sources/distributed-fs/ceph-client/drivers/clocksource/timer-tegra186.c

## Purpose

`timer-tegra186.c` is a platform driver for Tegra186 and Tegra234 timer-controller blocks. It registers three continuous clocksources from shared TKE registers (`tsc`, `osc`, `usec`) and exposes watchdog 0 through the Linux watchdog framework using a preconfigured timer as source.

## APIs And Flow

`struct tegra186_timer_soc` describes timer/watchdog counts. `struct tegra186_timer` stores device, MMIO base, SoC data, watchdog, and clocksources. `struct tegra186_tmr` and `struct tegra186_wdt` model timer/watchdog windows. Probe maps resource 0, validates IRQ 0, creates watchdog 0, then registers fixed-rate TSC at 31.25 MHz, OSC at 38.4 MHz, and USEC at 1 MHz. Watchdog ops start, stop, ping, set timeout, and compute time left. Enable unmasks TKE watchdog IRQ, clears timer interrupt, selects microsecond source, programs a one-fifth timeout period, optionally updates WDTCR if unlocked, and starts the counter.

## State, Dependencies, Risks, Tests

State is mostly hardware-backed. Firmware may lock WDTCR; if so, only timer and command registers are changed. Suspend disables an active watchdog and resume re-enables it. Dependencies include platform devices, OF match data, watchdog core, clocksource core, PM ops, and MMIO. Risks are fixed-rate assumptions, changed window offsets, locked watchdog configuration, and timeleft math. Test clocksource registration/unregistration, `/dev/watchdog` operations, suspend/resume with active watchdog, and reset timing when pings stop.
