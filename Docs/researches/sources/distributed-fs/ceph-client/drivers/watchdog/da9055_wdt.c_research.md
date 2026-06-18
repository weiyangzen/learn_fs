# sources/distributed-fs/ceph-client/drivers/watchdog/da9055_wdt.c

## Purpose
This driver manages the Dialog DA9055 PMIC watchdog through DA9055 MFD register helpers. It exposes discrete PMIC timeout scale values and a simple keepalive operation to the watchdog core.

## Important APIs, types, and functions
`struct da9055_wdt_data` contains the watchdog and parent `struct da9055`. Important functions are `da9055_wdt_set_timeout`, `da9055_wdt_ping`, `da9055_wdt_start`, `da9055_wdt_stop`, and `da9055_wdt_probe`. Timeout scales are defined by `da9055_wdt_maps` and programmed through `DA9055_REG_CONTROL_B`; pings write `DA9055_REG_CONTROL_E`.

## Control Flow
Probe allocates state, sets default timeout, configures nowayout, stops the watchdog to leave a known idle state, and registers the watchdog. Start programs the current timeout; stop maps timeout zero; ping waits `DA9055_TWDMIN` milliseconds then sets the watchdog reset bit. Set-timeout validates the requested seconds against the map before updating the PMIC and watchdog core.

## State and Persistence
The driver maintains no separate persistent cache beyond watchdog core timeout and parent pointer. PMIC registers hold enabled/timeout state until changed. Unlike DA9052, this driver does not expose PMIC fault-log bootstatus.

## Dependencies and Integration Points
It depends on the DA9055 MFD core/register helpers, platform device binding `da9055-watchdog`, module nowayout, delay helpers, and watchdog core.

## Risks and Test Signals
Risks include mandatory 256 ms delay in ping paths, unsupported timeout values, register update failures during probe stop, and lack of running-at-probe handoff. Tests should cover all mapped timeouts including 0, 32/33 and 65/66 aliases, invalid timeout rejection, start/stop sequencing, ping timing, and regmap/MFD error propagation.
