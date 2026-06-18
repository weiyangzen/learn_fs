# sources/distributed-fs/ceph-client/drivers/watchdog/sl28cpld_wdt.c

## Purpose
`sl28cpld_wdt.c` is the watchdog client for Kontron SL28 CPLD watchdog blocks. It accesses a parent MFD regmap at an offset supplied by firmware, supports timeout programming, get-timeleft, optional WDT timeout pin assertion, nowayout lock behavior, and preservation of already-running hardware.

## Important APIs, types, and functions
`struct sl28cpld_wdt` embeds `struct watchdog_device`, a parent `regmap`, block offset, and `assert_wdt_timeout`. Watchdog ops are `sl28cpld_wdt_ping()`, `sl28cpld_wdt_start()`, `sl28cpld_wdt_stop()`, `sl28cpld_wdt_set_timeout()`, and `sl28cpld_wdt_get_timeleft()`. Probe reads properties `reg` and `kontron,assert-wdt-timeout-pin`.

## Control flow
Probe requires a parent device and regmap, allocates state, reads the register offset, initializes min/max timeout of 1..255 seconds, then reads `WDT_CTRL` and `WDT_TIMEOUT` before modifying hardware. A zero hardware timeout is replaced with `WDT_DEFAULT_TIMEOUT`; device-tree or module timeout can override through `watchdog_init_timeout()`. If the CPLD lock bit was set, nowayout is forced. If hardware was already enabled, start is called to normalize mode and `WDOG_HW_RUNNING` is set before managed registration.

## State and persistence behavior
State is split between per-device data and CPLD registers. The lock bit can make stop impossible after start when nowayout sets `WDT_CTRL_LOCK`. Existing enabled hardware is treated as running state and surfaced to the watchdog core.

## Dependencies and integration points
The file depends on platform-device probing under the SL28 CPLD MFD, firmware properties, regmap read/write/update_bits, and standard watchdog helpers including `watchdog_stop_on_reboot()`.

## Risks and test signals
Risks include global module parameter `nowayout` being updated when one device is locked, write failures leaving timeout/core state diverged, and enabling lock bits too early. Tests should exercise property errors, default timeout fallback for zero, lock-bit detection, already-running hardware, timeout writes, ping writes of `0x6b`, get-timeleft reads, and optional timeout-pin assertion.
