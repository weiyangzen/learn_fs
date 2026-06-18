<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ie6xx_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/ie6xx_wdt.c`

Purpose: Intel Atom E6xx platform watchdog driver using an I/O-port resource supplied by a platform device. It exposes the watchdog through the watchdog core, programs preload registers derived from the 33 MHz PCI clock, and optionally exposes a debugfs register dump.

Important APIs, types, and functions: `ie6xx_wdt_dev` is a singleton `struct watchdog_device`; `ie6xx_wdt_ops` implements start, stop, ping, and set_timeout. Module parameters `timeout`, `nowayout`, and `resetmode` shape initial policy and hardware reset behavior. The register unlock sequence is centralized in `ie6xx_wdt_unlock_registers()` and protected by `ie6xx_wdt_data.unlock_sequence`; `ie6xx_wdt_set_timeout()` writes `WDTCR`, clears `PV1`, writes `PV2`, and reloads/clears timeout via `RR1`.

Control flow: `late_initcall()` registers the platform driver after validating the timeout range. Probe reserves the I/O region, records `sch_wdtba`, warns if `WDTLR` is locked, initializes debugfs, and registers the watchdog. Start programs the timeout then writes `WDT_ENABLE`; stop refuses a locked watchdog and clears `WDTLR`; ping performs the unlock sequence and writes `WDT_RELOAD`. Remove stops, unregisters, removes debugfs, and releases the I/O range.

State and persistence: live state is held in hardware registers plus singleton driver globals. A locked `WDTLR` persists until reboot and can prevent stop. `WDOG_HW_RUNNING` is not inferred on probe, so pre-enabled hardware is only surfaced through lock warnings/debugfs, not as core-running state.

Dependencies and integration points: depends on platform I/O resources, watchdog core, raw in/out port access, debugfs when enabled, and platform alias `ie6xx_wdt`. It integrates with user space through `/dev/watchdog*` via watchdog core and with debugfs as `/sys/kernel/debug/ie6xx_wdt`.

Risks and test signals: risks include register unlock sequence interruption, incorrect `resetmode`, preload rounding errors, and stop failures when locked. Test by validating module parameter bounds, start/ping/stop behavior, debugfs register visibility, locked-register handling, and reboot behavior for warm/cold reset settings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ie6xx_wdt.c -->
