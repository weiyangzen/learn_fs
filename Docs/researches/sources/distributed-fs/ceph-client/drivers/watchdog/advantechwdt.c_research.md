# sources/distributed-fs/ceph-client/drivers/watchdog/advantechwdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/advantechwdt.c` is a legacy miscdevice watchdog driver for Advantech single-board computers. It controls a watchdog by writing a 1-63 second timeout value to a start I/O port and disabling by reading a stop I/O port. The complete 337-line source was read for this report.

## Important APIs, Types, and Functions

Module parameters are `wdt_stop`, `wdt_start`, `timeout`, and `nowayout`. Core helpers are `advwdt_ping()`, `advwdt_disable()`, and `advwdt_set_heartbeat()`. File operations are `advwdt_write()`, `advwdt_ioctl()`, `advwdt_open()`, and `advwdt_close()`. Platform lifecycle functions are `advwdt_probe()`, `advwdt_remove()`, `advwdt_shutdown()`, `advwdt_init()`, and `advwdt_exit()`.

## Control Flow

Module init creates a synthetic platform device and probes it. Probe reserves start/stop I/O ports, validates or resets the timeout, and registers `/dev/watchdog`. Open enforces single access and immediately pings. Writes scan for magic close `V` when stoppable and ping the hardware. Ioctls expose support/status, enable/disable, keepalive, set timeout, and get timeout. Close disables only when the magic close flag was set; otherwise it pings and leaves the device armed. Shutdown disables on soft shutdown.

## State and Persistence Behavior

State is held in `timeout`, `advwdt_is_open`, and `adv_expect_close`. Hardware state persists in the board watchdog until the port write refreshes it, the stop port disables it, or a timeout resets the machine.

## Dependencies and Integration Points

It depends on x86 I/O port access, platform driver helpers, miscdevice registration on `WATCHDOG_MINOR`, watchdog ioctl constants, and user-space watchdog daemon conventions. Kconfig symbol `ADVANTECH_WDT` maps to `advantechwdt.o`.

## Risks and Edge Cases

The board is not safely probeable, so incorrect ports can affect unrelated hardware. The timeout range is narrow and driver-enforced; out-of-range module parameters silently fall back to default. Legacy miscdevice code does not participate in watchdog core boot-running management or sysfs. Unexpected close intentionally keeps the watchdog active.

## Test Signals

Check port reservation and cleanup, timeout validation at 0/1/63/64 seconds, `WDIOC_SETTIMEOUT` fallthrough to get timeout, magic close behavior, nowayout behavior, and shutdown disable.
