# sources/distributed-fs/ceph-client/drivers/watchdog/wafer5823wdt.c

## Purpose
`wafer5823wdt.c` is a legacy misc-device watchdog driver for ICP Wafer 5823 single-board computers. It uses two configurable I/O ports: one to start/restart with a timeout value and one to stop/pat the watchdog.

## Important APIs, types, and functions
Global state includes configurable `wdt_stop`, `wdt_start`, `timeout`, `nowayout`, `wafwdt_is_open`, `expect_close`, and `wafwdt_lock`. Hardware helpers are `wafwdt_start()`, `wafwdt_stop()`, and `wafwdt_ping()`. User operations are `wafwdt_open()`, `wafwdt_close()`, `wafwdt_write()`, and `wafwdt_ioctl()`. Reboot notifier is `wafwdt_notify_sys()`.

## Control flow
Init validates timeout, reserves start/stop ports, registers reboot notifier, and registers misc `/dev/watchdog`. Open claims the device and starts hardware by writing timeout to start port then reading it. Writes scan for magic close when allowed and ping by reading stop then start under lock. Ioctl supports support/status/bootstatus, enable/disable options, keepalive, and timeout changes that stop then restart. Close stops only with magic close; unexpected close pings and leaves it running.

## State and persistence behavior
Software state is global and volatile. Hardware state persists through I/O port side effects until stopped or reset. There is no probing; users must know the correct ports.

## Dependencies and integration points
It uses fixed/configurable x86 I/O ports, misc watchdog minor, reboot notifiers, spinlocks, and watchdog ioctl constants.

## Risks and test signals
Risks include wrong port parameters touching unrelated hardware, no module pinning for nowayout, no bootstatus, and legacy misc implementation. Tests should cover port reservation for same/different start-stop ports, timeout range 1..255, open/write/close semantics, ioctl options, reboot notifier stop, and correct read/write port ordering on real hardware.
