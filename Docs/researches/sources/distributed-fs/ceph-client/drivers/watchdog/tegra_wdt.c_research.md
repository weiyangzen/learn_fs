# sources/distributed-fs/ceph-client/drivers/watchdog/tegra_wdt.c

## Purpose
`tegra_wdt.c` drives the Tegra watchdog by pairing watchdog ID 0 with timer 5 in the Tegra timer block. It programs a fixed 1 MHz periodic timer and configures the watchdog to reset after multiple expirations.

## Important APIs, types, and functions
`struct tegra_wdt` stores watchdog plus watchdog and timer register bases. Watchdog ops are `tegra_wdt_start()`, `tegra_wdt_stop()`, `tegra_wdt_ping()`, `tegra_wdt_set_timeout()`, and `tegra_wdt_get_timeleft()`. Probe and PM handlers are `tegra_wdt_probe()`, `tegra_wdt_suspend()`, and `tegra_wdt_resume()`.

## Control flow
Probe maps the timer block, allocates state, derives watchdog and timer base offsets, initializes 1..255 second timeout bounds, applies nowayout, sets stop-on-unregister, registers, and saves drvdata. Start programs timer 5 for a quarter-second-equivalent cadence, writes watchdog config with timeout and reset enable, and starts the counter. Stop unlocks watchdog, disables it, and stops the timer. Timeout changes restart the active watchdog.

## State and persistence behavior
The device state is per-platform-device. Hardware state persists in watchdog config/status/cmd and timer PTV registers. Suspend stops active hardware; resume restarts it if the core still marks it active.

## Dependencies and integration points
It depends on DT compatible `nvidia,tegra30-timer`, platform MMIO, watchdog core, and PM sleep ops. It assumes timer 5 is unused by clocksource code.

## Risks and test signals
Risks include conflicts if timer 5 is repurposed, time-left arithmetic around expiration count, no boot-running takeover, and direct fixed-clock assumption. Tests should cover register offsets, start/stop/ping writes, timeout restart while active, suspend/resume, time-left decoding, and interaction with Tegra clocksource allocation.
