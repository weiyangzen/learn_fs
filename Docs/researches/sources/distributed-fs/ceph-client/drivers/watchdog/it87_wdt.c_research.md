<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/it87_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/it87_wdt.c`

Purpose: watchdog-core driver for many ITE IT87xx EC/LPC Super I/O chips, replacing older miscdevice patterns with watchdog core registration.

Important APIs, types, and functions: chip detection uses Super I/O `CHIPID`/`CHIPREV` and a large supported-ID switch. `_wdt_update_timeout()` writes GPIO watchdog config and timeout bytes, choosing seconds or minute units and optional test mode. `_wdt_running()` checks nonzero timeout registers. `wdt_start()` and `wdt_stop()` rewrite timeout to requested value or zero; `wdt_set_timeout()` rounds minute-mode timeouts.

Control flow: init reads chip ID/revision, applies DMI quirks, determines 8- or 16-bit timeout capacity, configures GPIO watchdog control, applies PWRGD routing quirks, detects firmware-running state, clamps/rounds the module timeout, sets max timeout, installs stop-on-reboot, and registers the watchdog. Exit unregisters it.

State and persistence: state is mostly hardware register state plus global `timeout`, `testmode`, `nowayout`, `max_units`, and `chip_type`. Firmware-left-running watchdogs are marked `WDOG_HW_RUNNING`. There is no explicit ping operation; watchdog core keepalive relies on start/set_timeout behavior and hardware semantics.

Dependencies and integration points: depends on Super I/O ports, DMI quirks, watchdog core, ITE GPIO/EC register layout, and module parameters for timeout/test/nowayout.

Risks and test signals: risks include unsupported/unknown chip IDs, DMI-specific output routing, minute rounding surprises, testmode disabling reset output, and lack of a conventional ping op. Test detection for each supported ID class, firmware-running handoff, timeout rounding, DMI Qotom PWRGD quirk, stop-on-reboot, and hardware reset output in normal versus test mode.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/it87_wdt.c -->
