# sources/distributed-fs/ceph-client/drivers/watchdog/ts72xx_wdt.c

## Purpose
`ts72xx_wdt.c` drives external CPLD watchdog logic on Technologic Systems TS-72xx boards. It controls separate feed and control MMIO resources and supports coarse timeout choices up to 8 seconds hardware heartbeat.

## Important APIs, types, and functions
`struct ts72xx_wdt_priv` stores control/feed registers, watchdog, and encoded control value. Watchdog ops are `ts72xx_wdt_start()`, `ts72xx_wdt_stop()`, `ts72xx_wdt_ping()`, and `ts72xx_wdt_settimeout()`. Probe maps two resources and registers the watchdog.

## Control flow
Probe maps control and feed registers, initializes watchdog metadata with min timeout 1 and max hardware heartbeat 8000 ms, applies nowayout and optional timeout, stores drvdata, and registers. Timeout setter maps requested seconds to 1, 2, 4, or 8 second control encodings, updates the reported timeout, and if active restarts hardware. Start feeds first, then writes control; stop feeds then writes disable.

## State and persistence behavior
Software caches the current `regval`; hardware state persists in CPLD control and feed side effects. Core may extend user-visible timeouts using `max_hw_heartbeat_ms`.

## Dependencies and integration points
It depends on platform MMIO resources, OF compatible `technologic,ts7200-wdt`, and watchdog core.

## Risks and test signals
Risks include a default timeout larger than hardware heartbeat relying on core keepalives, no explicit stop-on-reboot, and coarse rounding behavior. Tests should cover two-resource mapping, timeout encoding, active restart on timeout change, feed/control write order, nowayout, and core-managed heartbeat for long default timeout.
