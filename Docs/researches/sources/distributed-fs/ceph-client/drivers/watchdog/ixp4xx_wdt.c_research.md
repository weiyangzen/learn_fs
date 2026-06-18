<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ixp4xx_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/ixp4xx_wdt.c`

Purpose: watchdog-core driver for Intel IXP4xx network processors, including a restart-only fallback for the broken Rev A0 IXP42x watchdog.

Important APIs, types, and functions: `struct ixp4xx_wdt` stores watchdog core state, timer base, and clock rate. `ixp4xx_wdt_start()` unlocks with `IXP4XX_WDT_KEY`, loads timeout ticks, enables count/reset, and relocks. Stop unlocks and clears enable. `ixp4xx_wdt_restart()` loads zero and enables reset. A dummy ops table supports only restart on affected CPUs.

Control flow: probe chooses full or restart-only ops based on CPU revision helpers, gets timer base from platform data, obtains parent clock or falls back to 66.666 MHz, computes max timeout, reads warm-reset bootstatus, registers the watchdog, and logs availability.

State and persistence: hardware status register exposes warm reset cause as `WDIOF_CARDRESET`. The driver does not mark pre-enabled hardware running; it configures on user start. Timeout updates restart the watchdog if active.

Dependencies and integration points: depends on platform data containing the base address, parent fixed clock when available, IXP4xx CPU helpers, watchdog core, and MMIO raw writes.

Risks and test signals: risks include wrong platform-data base, Rev A0 behavior, clock fallback mismatch, and warm-reset status interpretation. Test both CPU revision paths, max timeout calculation from clock, restart-only watchdog semantics, bootstatus after warm reset, and active timeout updates.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ixp4xx_wdt.c -->
