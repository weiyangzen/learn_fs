<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rzn1_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rzn1_wdt.c

Purpose: watchdog-core driver for the Renesas RZ/N1 short-period watchdog, relying on watchdog core heartbeats because hardware cannot provide long timeouts.

Important APIs, types, and functions: `struct rzn1_watchdog` stores watchdog, MMIO base, and clock rate in kHz. Key routines are `max_heart_beat_ms()`, `compute_reload_value()`, `rzn1_wdt_ping()`, `rzn1_wdt_start()`, IRQ handler, and probe.

Control flow: probe maps registers, requests the watchdog IRQ, enables the clock, computes max hardware heartbeat, caps it at one second, initializes a default 60-second logical timeout, and registers. Start writes the one-shot retrigger register with interrupt mode, enable, prescale, and reload value. Ping writes any value to retrigger. IRQ logs a critical timeout and calls `emergency_restart()`.

State and persistence behavior: hardware state is a write-once retrigger/configuration register after start; software state is max hardware heartbeat and logical watchdog timeout. `WATCHDOG_NOWAYOUT_INIT_STATUS` is set.

Dependencies and integration points: depends on platform IRQ, OF node name for IRQ registration, clocks, watchdog core auto-ping for max hardware heartbeat, and reboot emergency restart path.

Risks and edge cases: the hardware register can be written only once, so timeout cannot change after start. Clock changes after start alter real timeout. The maximum period may be below two seconds, making watchdog core scheduling essential.

Test signals: max-heartbeat computation, one-time start behavior, watchdog core auto-ping, IRQ-triggered emergency restart, clock-rate zero handling, and timeout DT initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rzn1_wdt.c -->
