# sources/distributed-fs/ceph-client/drivers/watchdog/smsc37b787_wdt.c

## Purpose
`smsc37b787_wdt.c` is a legacy misc-device watchdog driver for the SMSC 37B787 Super I/O watchdog. It unlocks the chip configuration port, selects logical device 8, configures GPIO pins for watchdog output, programs timeout units and values, and implements `/dev/watchdog` ioctls directly.

## Important APIs, types, and functions
Low-level helpers are `open_io_config()`, `close_io_config()`, `select_io_device()`, `write_io_cr()`, and `read_io_cr()`. Medium-level helpers program GPIO and watchdog registers: `gpio_bit12()`, `gpio_bit13()`, `wdt_timer_units()`, `wdt_timeout_value()`, `wdt_timer_conf()`, and `wdt_timer_ctrl()`. High-level controls include `wb_smsc_wdt_initialize()`, `wb_smsc_wdt_shutdown()`, `wb_smsc_wdt_set_timeout()`, `wb_smsc_wdt_reset_timer()`, `wb_smsc_wdt_open()`, `wb_smsc_wdt_write()`, `wb_smsc_wdt_ioctl()`, and reboot notifier `wb_smsc_wdt_notify_sys()`.

## Control flow
Module init reserves ports `0x3f0..0x3f1`, clamps timeout, initializes pin and watchdog register state, registers the reboot notifier, and registers misc `/dev/watchdog`. Opening is single-user, optionally pins the module for nowayout, and enables the current timeout. Writes parse magic close when allowed and always reload. Ioctls expose support/status, enable/disable options, keepalive, and timeout conversion between seconds and optional minutes mode. Release disables only on expected close; unexpected close resets the timer.

## State and persistence behavior
Global state tracks units, timeout, open flag, close expectation, and nowayout. Hardware state is in Super I/O configuration registers and GPIO function bits and persists until explicitly reset or power-cycled. `io_lock` serializes multi-port unlock/select/write sequences.

## Dependencies and integration points
The driver uses direct x86-style port I/O, misc watchdog minor, reboot notifiers, and user access helpers. It is not integrated with the modern watchdog core.

## Risks and test signals
Risks include fixed I/O address assumptions, no chip ID probing, unit-minute support compiled out as unreliable, and potential board pin side effects. Test by reserving conflicts, open/write/magic-close semantics, `WDIOC_SETOPTIONS`, timeout range and unit conversion, reboot notifier shutdown, and register trace validation for GPIO selection and watchdog reset on real SMSC hardware.
