# sources/distributed-fs/ceph-client/drivers/watchdog/at91rm9200_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/at91rm9200_wdt.c` is a legacy miscdevice watchdog driver for the Atmel AT91RM9200 system timer watchdog. It accesses watchdog registers through a parent syscon regmap, exposes `/dev/watchdog`, and registers a restart handler. The complete 332-line source was read for this report.

## Important APIs, Types, and Functions

Module parameters are `wdt_time` and conditionally `nowayout`. Hardware helpers are `at91_wdt_stop()`, `at91_wdt_start()`, `at91_wdt_reload()`, and `at91_wdt_settimeout()`. File operations include `at91_wdt_open()`, `at91_wdt_close()`, `at91_wdt_ioctl()`, and `at91_wdt_write()`. Platform and restart functions are `at91rm9200_restart()`, `at91wdt_probe()`, `at91wdt_remove()`, `at91wdt_shutdown()`, `at91wdt_suspend()`, `at91wdt_resume()`, `at91_wdt_init()`, and `at91_wdt_exit()`.

## Control Flow

Module init validates `wdt_time` and registers the platform driver. Probe ensures only one miscdevice parent, obtains the parent syscon regmap, registers `/dev/watchdog`, and registers a restart handler. Open starts the watchdog; writes reload; ioctls support enable/disable, keepalive, set/get timeout, and status. Close stops only if not nowayout. Shutdown and suspend stop the watchdog; resume restarts if the device was open. The restart handler writes mode and control registers to force a reset, delays, then logs failure if reset did not occur.

## State and Persistence Behavior

State is global: `wdt_time`, `nowayout`, `regmap_st`, and `at91wdt_busy`. Hardware mode is programmed into system timer registers and persists until changed or reset. The driver does not track magic close; close behavior is controlled directly by nowayout.

## Dependencies and Integration Points

It depends on MFD syscon for Atmel system timer registers, miscdevice watchdog ABI, reboot restart handler API, platform/OF binding `atmel,at91rm9200-wdt`, and watchdog ioctl constants.

## Risks and Edge Cases

The driver is legacy and not watchdog-core based, so behavior differs from newer AT91 watchdogs. Global singleton state prevents multiple instances. Timeout conversion assumes a 256 Hz watchdog clock and caps at 256 seconds. Suspend stops the watchdog even if userspace expects continuous monitoring.

## Test Signals

Test syscon lookup, single-instance guard, timeout boundaries, close under nowayout and stoppable modes, restart handler reset, suspend/resume open-state handling, and misc ioctl behavior.
