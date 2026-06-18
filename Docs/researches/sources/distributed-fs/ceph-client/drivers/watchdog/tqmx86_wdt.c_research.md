# sources/distributed-fs/ceph-client/drivers/watchdog/tqmx86_wdt.c

## Purpose
`tqmx86_wdt.c` drives the TQMx86 PLD watchdog. The hardware supports power-of-two timeouts from 1 to 4096 seconds and cannot be stopped once started.

## Important APIs, types, and functions
`struct tqmx86_wdt` embeds the watchdog and I/O base. Watchdog ops are `tqmx86_wdt_start()` and `tqmx86_wdt_set_timeout()`. Probe maps an I/O resource, initializes timeout bounds, forces nowayout, programs the initial timeout, and registers.

## Control flow
Probe obtains an `IORESOURCE_IO`, maps it with `devm_ioport_map()`, fills `watchdog_device`, reads optional module/firmware timeout, sets nowayout to Kconfig value, and calls `tqmx86_wdt_set_timeout()` before registration. Timeout requests are rounded up to a power of two; the encoded value is `ilog2(t) | 0x90` plus an offset for sub-second hardware encodings. Start writes `0x81` to the config/status register.

## State and persistence behavior
The driver stores only the rounded timeout and I/O base. Hardware cannot be stopped through this driver, so started state persists until reset or power cycle.

## Dependencies and integration points
It depends on a platform device named `tqmx86-wdt`, I/O port resources, log2 helpers, and watchdog core.

## Risks and test signals
Risks include rounding timeout upward without reporting an error, no stop operation, and encoding assumptions for PLD revisions. Tests should validate I/O resource absence, timeout rounding for edge values, register writes to `WDCFG` and `WDCS`, nowayout behavior, and core acceptance of start-only hardware with `max_hw_heartbeat_ms`.
