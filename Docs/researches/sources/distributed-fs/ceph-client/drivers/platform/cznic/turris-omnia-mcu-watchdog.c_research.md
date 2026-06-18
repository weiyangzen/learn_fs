<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-watchdog.c -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-watchdog.c

## Purpose

This optional feature exposes the Turris Omnia MCU watchdog through the Linux watchdog subsystem.

## Important APIs, Types, And Functions

Module parameters `timeout` and `nowayout` configure default timeout and stop behavior. Watchdog ops start, stop, ping, set timeout, and get time left through MCU commands. `omnia_mcu_register_watchdog()` initializes `struct watchdog_device`, applies timeout, reads current hardware running state, sets nowayout and stop-on-reboot policy, and registers the device.

## Control Flow

Registration is skipped unless the MCU advertises `OMNIA_FEAT_WDT_PING`. The driver sets a default 120-second timeout, lets watchdog core apply a module-parameter override, writes the timeout to the MCU in deciseconds, checks if hardware is already running, and registers with devm.

## State And Persistence

Kernel state is the watchdog device struct. The actual watchdog timer, running state, timeout, and countdown live in the MCU and can persist across driver binding if hardware was already running.

## Dependencies And Integration Points

It depends on watchdog core, module parameters, MCU I2C command helpers, and watchdog feature bits.

## Risks

`omnia_wdt_set_timeout()` writes `timeout * DECI`, so max timeout is constrained to `65535 / DECI`. Registration writes the timeout before checking running state. If command errors occur during get-timeleft, the watchdog core sees zero.

## Test Signals

Test start/stop/ping, timeout set bounds, module timeout override, nowayout behavior, already-running hardware detection, stop-on-reboot, command error propagation, and get-timeleft conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-watchdog.c -->
