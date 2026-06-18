# sources/distributed-fs/ceph-client/drivers/watchdog/wm8350_wdt.c

## Purpose
`wm8350_wdt.c` is a watchdog-core platform driver for the WM8350 PMIC watchdog.

## Important APIs, types, and functions
It uses one static `watchdog_device` and a global `wdt_mutex`. Timeout table `wm8350_wdt_cfgs` maps 1, 2, and 4 seconds to register values. Ops are `wm8350_wdt_set_timeout`, `wm8350_wdt_start`, `wm8350_wdt_stop`, and `wm8350_wdt_ping`; probe binds parent MFD data, sets defaults, and registers with devm.

## Control flow
Probe retrieves `struct wm8350` from platform driver data, sets nowayout and driver data, assigns the parent device, programs a default 4 second timeout, and registers. Start/stop unlock system control register 2, update watchdog mode bits, write, and relock. Ping rewrites the current system control register value, which refreshes the watchdog.

## State and persistence
The watchdog device is static, so the driver effectively assumes one instance. PMIC register state persists across driver lifetime. The mutex serializes register access.

## Dependencies and integration points
It depends on WM8350 MFD core functions, platform bus, watchdog core, and the module parameter `nowayout`.

## Risks and test signals
Risks include static-device multi-instance unsafety, no read-error checks in several paths, narrow timeout support, protected register lock/unlock sequencing, and default timeout programming failures. Test signals include probe with missing platform data, 1/2/4 second timeouts and invalid values, start/stop/ping under injected MFD errors, and module reload on boards with the PMIC.
