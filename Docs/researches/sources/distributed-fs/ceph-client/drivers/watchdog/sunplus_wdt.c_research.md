# sources/distributed-fs/ceph-client/drivers/watchdog/sunplus_wdt.c

## Purpose
`sunplus_wdt.c` drives the Sunplus SP7021 watchdog/timer block. It handles magic command words for stop/resume/unlock/lock, max hardware heartbeat constraints, get-timeleft, and restart using a minimal count.

## Important APIs, types, and functions
`struct sp_wdt_priv` stores watchdog, MMIO base, clock, and reset control. Watchdog ops are `sp_wdt_start()`, `sp_wdt_stop()`, `sp_wdt_ping()`, `sp_wdt_get_timeleft()`, and `sp_wdt_restart()`. Probe is `sp_wdt_probe()` and reset cleanup is `sp_reset_control_assert()`.

## Control flow
Probe enables the clock, gets/deasserts shared reset, maps MMIO, initializes timeout defaults and `max_hw_heartbeat_ms`, applies nowayout and stop-on-reboot, sets restart priority, and registers. Ping writes either `WDT_CONMAX` for too-large core timeout under max-hw-heartbeat management or unlocks, writes a count derived from `timeout * 90000 >> 4`, and locks. Start writes resume; stop writes stop. Restart stops, unlocks, writes count 1, locks, resumes, and lets hardware reset.

## State and persistence behavior
Hardware state is in WDT control/count registers and shared reset. Software state is per-device. Because the hardware maximum is about 11 seconds, the watchdog core may need to ping periodically for larger user timeouts via `max_hw_heartbeat_ms`.

## Dependencies and integration points
It depends on DT compatible `sunplus,sp7021-wdt`, clock and reset frameworks, MMIO, and watchdog restart priority.

## Risks and test signals
Risks include `get_timeleft()` returning raw ticks rather than seconds, shared reset side effects, count truncation, and core reliance for long timeouts. Tests should validate magic command order, max-hw heartbeat behavior, restart reset, timeout count calculations, stop-on-reboot, and clock/reset cleanup.
