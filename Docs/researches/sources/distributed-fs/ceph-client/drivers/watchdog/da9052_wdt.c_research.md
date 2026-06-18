# sources/distributed-fs/ceph-client/drivers/watchdog/da9052_wdt.c

## Purpose
`da9052_wdt.c` controls the watchdog inside Dialog DA9052 PMICs. It maps supported PMIC watchdog scales to user-visible seconds, reports PMIC fault-log boot causes, and observes a minimum feed window.

## Important APIs, types, and functions
`struct da9052_wdt_data` stores the embedded watchdog, parent `struct da9052`, and `jpast` timestamp. Core ops are `da9052_wdt_start`, `da9052_wdt_stop`, `da9052_wdt_ping`, and `da9052_wdt_set_timeout`. Register access goes through `da9052_reg_update` and `da9052_reg_read`, with timeout selection in `DA9052_CONTROL_D_REG`.

## Control Flow
Set-timeout first disables the watchdog scale bits, waits at least 150 microseconds when enabling, maps requested seconds to a scale value, programs the PMIC, and updates the watchdog timeout. Start calls set-timeout with the cached timeout; stop passes zero. Ping waits for the watchdog minimum window, toggles the watchdog bit high then low, and returns register errors.

## State and Persistence
The driver caches `jpast` to avoid early feeds and maps `da9052->fault_log` into `bootstatus`. PMIC control registers can be left enabled by firmware; probe detects this, reinitializes the watchdog, and sets `WDOG_HW_RUNNING`.

## Dependencies and Integration Points
It integrates with the DA9052 MFD core, PMIC register definitions, fault log fields, Linux jiffies timing, module timeout/nowayout parameters, and watchdog core.

## Risks and Test Signals
Risks include the `mdelay(msec)` logic when `msec < DA9052_TWDMIN`, exact timeout mapping failures, boot-enabled handoff, and failure while toggling the feed bit. Tests should cover every supported timeout map value, invalid timeout, fault-log bootstatus bits, early ping timing, start/stop register failures, and running-at-probe behavior.
