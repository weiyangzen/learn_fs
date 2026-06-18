# sources/distributed-fs/ceph-client/drivers/watchdog/da9063_wdt.c

## Purpose
This driver controls the Dialog DA9063 PMIC watchdog. It supports discrete PMIC timeout selectors, boot-enabled watchdog handoff, optional software power management, and watchdog-based system restart.

## Important APIs, types, and functions
The parent `struct da9063` is used as watchdog driver data. Important helpers are `da9063_wdt_timeout_to_sel`, `da9063_wdt_read_timeout`, `da9063_wdt_disable_timer`, `da9063_wdt_update_timeout`, and `da9063_wdt_restart`. Watchdog ops implement start, stop, ping, set_timeout, and restart.

## Control Flow
Probe obtains the parent MFD object, sets `use_sw_pm` from `dlg,use-sw-pm`, initializes limits and restart priority, reads existing PMIC timeout, applies firmware timeout override, and marks `WDOG_HW_RUNNING` when the hardware was already active. Start/update disables the watchdog, waits 150-300 us, and writes the selector because the timeout field also starts the watchdog. Set-timeout only touches hardware when active. Ping writes `DA9063_WATCHDOG` unless shutdown is in progress. Restart writes `DA9063_SHUTDOWN` via unlocked SMBus and waits.

## State and Persistence
PMIC registers hold actual watchdog state. The driver buffers timeout in `watchdog_device` when inactive because the hardware cannot store a nonzero timeout without starting. Bootloader-enabled state is preserved and reprogrammed.

## Dependencies and Integration Points
It depends on DA9063 MFD/regmap/I2C definitions, platform binding `DA9063_DRVNAME_WATCHDOG`, watchdog restart handling, and optional PM callbacks.

## Risks and Test Signals
Risks include forced disable during active timeout changes, restart path dependence on I2C availability, timeout selector rounding, and inconsistent software PM with always-on watchdog policy. Tests should cover inactive set_timeout buffering, active reprogramming, running-at-probe, restart, suspend/resume with and without `dlg,use-sw-pm`, and regmap failures.
