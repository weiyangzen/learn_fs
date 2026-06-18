# sources/distributed-fs/ceph-client/drivers/watchdog/twl4030_wdt.c

## Purpose
`twl4030_wdt.c` drives the TWL4030 PM receiver watchdog over the TWL I2C API. It exposes start/stop/set-timeout operations for a 1..30 second PMIC watchdog.

## Important APIs, types, and functions
The hardware access wrapper is `twl4030_wdt_write()`. Watchdog ops are `twl4030_wdt_start()`, `twl4030_wdt_stop()`, and `twl4030_wdt_set_timeout()`. Probe allocates a `watchdog_device`, stops hardware, and registers. Platform PM callbacks stop/resume active hardware.

## Control flow
Probe allocates and fills a watchdog with default 30 seconds, min 1, max 30, applies nowayout, saves drvdata, stops hardware by writing zero, and registers. Start writes `timeout + 1` to the watchdog config register; stop writes zero. Timeout setter only updates software; the new value takes effect on next start or resume.

## State and persistence behavior
Software state is the allocated watchdog. Hardware state resides in the TWL PM receiver register. Suspend stops active watchdogs and resume starts them again if the core still marks them active.

## Dependencies and integration points
It depends on the TWL MFD API `twl_i2c_write_u8()`, platform devices, OF compatible `ti,twl4030-wdt`, and watchdog core.

## Risks and test signals
Risks include off-by-one timeout encoding, no ping operation despite advertising keepalive through start semantics, and stop-on-probe changing bootloader state. Tests should cover I2C write errors, timeout boundaries, suspend/resume active behavior, start/stop register values, and nowayout behavior.
