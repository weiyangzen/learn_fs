# sources/distributed-fs/ceph-client/drivers/watchdog/bcm47xx_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/bcm47xx_wdt.c` is a watchdog-core wrapper for Broadcom BCM47xx platform watchdog operations supplied as platform data. It chooses direct hardware mode or a software extension timer when the hardware maximum interval is too short for requested timeouts. The complete 233-line source was read for this report.

## Important APIs, Types, and Functions

The driver consumes `struct bcm47xx_wdt` from platform data, which provides hardware callbacks such as `timer_set()` and `timer_set_ms()` plus fields like `max_timer_ms`, `soft_timer`, and `soft_ticks`. Hard-mode callbacks are `bcm47xx_wdt_hard_keepalive()`, `bcm47xx_wdt_hard_start()`, `bcm47xx_wdt_hard_stop()`, and `bcm47xx_wdt_hard_set_timeout()`. Soft-mode callbacks are `bcm47xx_wdt_soft_timer_tick()`, `bcm47xx_wdt_soft_keepalive()`, `bcm47xx_wdt_soft_start()`, `bcm47xx_wdt_soft_stop()`, and `bcm47xx_wdt_soft_set_timeout()`. Shared restart is `bcm47xx_wdt_restart()`, and probe is `bcm47xx_wdt_probe()`.

## Control Flow

Probe obtains platform data, selects soft mode if hardware max is below 60 seconds, installs the corresponding ops, validates module timeout, applies nowayout and restart priority, arranges stop-on-reboot, and registers the watchdog. Hard mode pings by programming the full timeout directly. Soft mode maintains `soft_ticks` in seconds and uses a kernel timer to refresh hardware each second until the software count expires; then it logs that hardware will fire soon. Restart programs a one-tick hardware timeout.

## State and Persistence Behavior

State is mostly owned by the platform-data structure supplied by lower BCM47xx code. Soft mode persists a countdown in `atomic_t soft_ticks` and a kernel timer. Hardware state is abstracted behind platform callbacks.

## Dependencies and Integration Points

It depends on `<linux/bcm47xx_wdt.h>` platform data, watchdog core, kernel timers, jiffies, and module parameters. Kconfig selects `WATCHDOG_CORE` for `BCM47XX_WDT`.

## Risks and Edge Cases

The driver is only as correct as platform-provided callbacks and `max_timer_ms`. Soft mode extends short hardware timeouts but depends on kernel scheduling each second. Timeout validation logs "using new_time" even while returning `-EINVAL`, which can be confusing. There is no OF discovery in this file; missing platform data returns `-ENXIO`.

## Test Signals

Test platform-data absence, hard/soft mode selection boundary, soft timer countdown and expiration, hardware callback invocation, restart programming, timeout validation, and stop-on-reboot.
