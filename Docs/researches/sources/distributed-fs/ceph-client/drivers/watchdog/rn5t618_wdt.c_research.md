<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rn5t618_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rn5t618_wdt.c

Purpose: watchdog-core driver for the Ricoh RN5T618 PMIC watchdog using the parent regmap.

Important APIs, types, and functions: `struct rn5t618_wdt` holds the watchdog and parent PMIC pointer. Important routines are `rn5t618_wdt_set_timeout()`, `rn5t618_wdt_start()`, `rn5t618_wdt_stop()`, `rn5t618_wdt_ping()`, and probe.

Control flow: probe gets the parent PMIC, initializes watchdog bounds from a four-entry hardware timeout map, reads `RN5T618_POFFHIS` to set bootstatus, applies module/DT timeout, and registers. Set-timeout selects the smallest hardware map entry whose timeout plus the one-second interrupt grace period covers the requested value. Start programs timeout, enables repower-on, enables watchdog, and enables watchdog interrupt. Ping reads and rewrites the watchdog register to restart the counter, then clears the pending interrupt.

State and persistence behavior: persistent hardware state is in PMIC registers: watchdog enable/time, repower-on, interrupt enable, IRQ pending, and power-off history. Driver state is selected timeout and nowayout.

Dependencies and integration points: depends on RN5T618 MFD definitions, regmap, platform parent data, watchdog core, and PMIC power-off history semantics.

Risks and edge cases: timeout selection intentionally rounds up and reports the hardware-supported value, not the user value. Multi-step start can leave partial enablement if later regmap updates fail. Ping depends on read/write side effects documented by the PMIC.

Test signals: all timeout map selections, bootstatus for VINDET and WDG, regmap error injection during start/ping, interrupt clearing, stop disable, and nowayout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rn5t618_wdt.c -->
