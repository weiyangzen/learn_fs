# sources/distributed-fs/ceph-client/drivers/watchdog/da9062_wdt.c

## Purpose
`da9062_wdt.c` supports DA9062 and DA9061 PMIC watchdogs. It provides watchdog start/stop/ping, discrete timeout scaling, optional software suspend policy, bootloader handoff, and a high-priority restart handler.

## Important APIs, types, and functions
`struct da9062_watchdog` stores the parent `struct da9062`, watchdog device, and `use_sw_pm` flag. Key helpers are `da9062_wdt_read_timeout`, `da9062_wdt_timeout_to_sel`, `da9062_reset_watchdog_timer`, `da9062_wdt_update_timeout_register`, and `da9062_wdt_restart`. Watchdog ops include start, stop, ping, set_timeout, and restart.

## Control Flow
Probe reads optional `dlg,use-sw-pm`, initializes watchdog limits, reads any active PMIC timeout, applies DT timeout overrides, and marks `WDOG_HW_RUNNING` if firmware left the watchdog enabled. Updating timeout disables the scale bits, waits 150-300 us, then writes the new selector. Ping writes the control-F watchdog bit unless the system is already leaving `SYSTEM_RUNNING`. Restart bypasses regmap with unlocked SMBus transfer to write PMIC shutdown.

## State and Persistence
Runtime state includes selected timeout in watchdog core, PMIC register state, `WDOG_HW_RUNNING`, and the suspend policy flag. PMIC watchdog state can persist across bootloader handoff.

## Dependencies and Integration Points
The driver depends on DA9062 MFD/regmap definitions, I2C client access for restart, firmware property `dlg,use-sw-pm`, OF compatible `dlg,da9062-watchdog`, PM callbacks, and watchdog restart priority.

## Risks and Test Signals
Risks include disabling the watchdog during timeout changes, restart in atomic/shutdown context, ping suppression during reboot, and timeout rounding to supported selectors. Tests should cover boot-enabled handoff, each timeout selector, software PM suspend/resume, restart path failure, active set_timeout, and regmap update errors.
