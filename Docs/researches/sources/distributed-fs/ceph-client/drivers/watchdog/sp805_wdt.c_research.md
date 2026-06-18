# sources/distributed-fs/ceph-client/drivers/watchdog/sp805_wdt.c

## Purpose
`sp805_wdt.c` drives ARM PrimeCell SP805 watchdog blocks on AMBA. It supports timeout/load conversion from clock rate, time-left reporting, restart handling, suspend/resume, optional ACPI-style `clock-frequency`, and preserving boot-enabled hardware.

## Important APIs, types, and functions
`struct sp805_wdt` embeds the watchdog, spinlock, MMIO base, optional clock, clock rate, AMBA device, and current load value. Key helpers are `wdt_is_running()`, `wdt_setload()`, `wdt_timeleft()`, `wdt_restart()`, `wdt_config()`, `wdt_ping()`, `wdt_enable()`, and `wdt_disable()`. Probe/remove and PM handlers are `sp805_wdt_probe()`, `sp805_wdt_remove()`, `sp805_wdt_suspend()`, and `sp805_wdt_resume()`.

## Control flow
Probe maps the AMBA resource, obtains rate from clock or property, deasserts optional reset, initializes watchdog metadata, computes default load, and if hardware is already running, reprograms it and marks `WDOG_HW_RUNNING`. Start enables the clock and calls `wdt_config(false)`, which unlocks registers, writes load, clears interrupt, enables interrupt/reset, relocks, and flushes posted writes. Ping rewrites load and clears interrupt without re-enabling the clock. Stop disables control and the clock. Restart writes a minimal load and enables reset for rapid reboot.

## State and persistence behavior
`load_val` and `timeout` cache the programmed period; hardware load/control/interrupt/lock registers persist until changed. Active watchdogs are stopped during suspend and restored on resume. Clock enable state follows start/stop.

## Dependencies and integration points
The file integrates with AMBA IDs, PrimeCell resources, optional clocks and resets, device properties, watchdog core restart priority, and PM ops.

## Risks and test signals
Risks include wrong clock-rate source, load overflow/rounding, disabling clocks while hardware is active, and time-left interpretation around the two-stage interrupt/reset cycle. Tests should cover clock property fallback, load clamping, running-hardware takeover, start/ping/stop register traces, restart path, suspend/resume only when active, and AMBA ID matching.
