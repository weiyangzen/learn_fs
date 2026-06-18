<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/marvell_gti_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/marvell_gti_wdt.c`

Purpose: Marvell GTI central watchdog driver for CN9670/CN10K-style timers, using a selected GTI timer in interrupt/pretimeout/reset mode.

Important APIs, types, and functions: `struct gti_wdt_priv` stores watchdog core state, GTI base, clock, selected timer index, and match data. `gti_wdt_settimeout()` makes pretimeout one third of timeout and programs CNT/LEN fields in 1024-cycle units. `gti_wdt_start()` clears pending interrupt, enables interrupt, and sets mode 3. `gti_wdt_interrupt()` clears pending status and calls `watchdog_notify_pretimeout()`.

Control flow: probe maps GTI MMIO, enables/reads clock, selects the last timer unless `marvell,wdt-timer-index` overrides it, computes maximum pretimeout/timeout from counter fields, programs initial timeout, installs stop-on-reboot/unregister, registers watchdog, then requests the IRQ.

State and persistence: selected GTI timer registers hold mode, reload, and interrupt enable state. Hardware mode uses first timeout as kernel pretimeout, second SCP event effectively ignored by configuration, and third timeout as reset. Start sets `WDOG_HW_RUNNING`.

Dependencies and integration points: depends on OF compatibles `marvell,cn9670-wdt` and `marvell,cn10624-wdt`, GTI clock, MMIO, platform IRQ, optional timer-index property, and watchdog core pretimeout semantics.

Risks and test signals: risks include requesting IRQ after watchdog registration, timer index conflicts, 1/3 pretimeout policy surprises, and counter rounding/saturation. Test timer-index bounds, IRQ pretimeout, max timeout math by clock, stop disabling interrupts/mode, and full reset after missed pings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/marvell_gti_wdt.c -->
