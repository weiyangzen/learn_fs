# sources/distributed-fs/ceph-client/drivers/watchdog/stpmic1_wdt.c

## Purpose
`stpmic1_wdt.c` is the watchdog driver for the STPMIC1 PMIC. It controls watchdog start, stop, ping, and timeout through PMIC regmap registers exposed by the parent MFD.

## Important APIs, types, and functions
`struct stpmic1_wdt` stores a parent `struct stpmic1 *` and embedded `watchdog_device`. Watchdog ops are `pmic_wdt_start()`, `pmic_wdt_stop()`, `pmic_wdt_ping()`, and `pmic_wdt_set_timeout()`. Probe is `pmic_wdt_probe()`.

## Control flow
Probe requires a parent device and parent driver data, allocates state, fills watchdog metadata with 1..256 second bounds and default 30 seconds, reads optional timeout, applies nowayout, stores drvdata, and registers. Start/stop update `WCHDG_CR` start bit, ping sets the ping bit, and timeout writes `timeout - 1` to `WCHDG_TIMER_CR`.

## State and persistence behavior
Software state is per-device. Hardware state persists in PMIC watchdog control and timer registers and may survive across SoC resets depending on PMIC power behavior.

## Dependencies and integration points
The file integrates with the STPMIC1 MFD, regmap, OF compatible `st,stpmic1-wdt`, platform devices, and the watchdog core.

## Risks and test signals
Risks include parent-data absence, regmap write failures, timeout off-by-one encoding, and PMIC reset behavior differing from SoC-local watchdogs. Tests should cover parent validation, min/max/default timeout, timeout register values for 1 and 256 seconds, start/stop/ping bit updates, nowayout behavior, and devm unregister.
