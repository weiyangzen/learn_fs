# sources/distributed-fs/ceph-client/drivers/watchdog/wm831x_wdt.c

## Purpose
`wm831x_wdt.c` implements a watchdog-core platform driver for WM831x PMIC watchdog blocks, using the parent MFD register APIs and optional platform data.

## Important APIs, types, and functions
`struct wm831x_wdt_drvdata` holds a `watchdog_device`, parent `struct wm831x`, mutex, and unused `update_state`. Timeout table `wm831x_wdt_cfgs` maps supported second values to `WDOG_TO` register codes. Ops are `wm831x_wdt_start`, `wm831x_wdt_stop`, `wm831x_wdt_ping`, and `wm831x_wdt_set_timeout`; probe configures platform data and registers the device.

## Control flow
Probe reads the watchdog register, warns if paused in debug mode, allocates driver data, initializes watchdog core fields and nowayout, reads the current timeout code, applies optional primary/secondary/software reset action platform data under security unlock, and calls `devm_watchdog_register_device`. Start/stop unlock protected registers and set or clear `WM831X_WDOG_ENA`. Ping verifies software reset/update support through `WM831X_WDOG_RST_SRC`, sets `WM831X_WDOG_RESET`, and writes the watchdog register.

## State and persistence
Driver state is devm-managed. PMIC watchdog configuration persists in PMIC registers until changed. The mutex serializes protected register unlock/write/lock sequences.

## Dependencies and integration points
It depends on WM831x MFD core/pdata/watchdog headers, platform bus, watchdog core, and module parameter `nowayout`.

## Risks and test signals
Risks include unsupported hardware update mode, security unlock failures, timeout table rejecting valid-looking values, stale timeout if register read returns unknown code, and platform data bit-shift mistakes. Test signals include all supported timeouts, debug-paused hardware, software reset source disabled, start/stop/ping errors, platform-data action programming, and devm removal.
