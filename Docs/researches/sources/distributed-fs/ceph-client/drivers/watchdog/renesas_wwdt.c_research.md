<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/renesas_wwdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/renesas_wwdt.c

Purpose: watchdog-core driver for Renesas R-Car Window Watchdog Timer, where firmware is expected to configure the one-shot WWDT setup and Linux adapts to it.

Important APIs, types, and functions: `struct wwdt_priv` contains MMIO base and watchdog. Important routines are `wwdt_start()`, `wwdt_error_irq()`, `wwdt_pretimeout_irq()`, and `wwdt_probe()`.

Control flow: probe maps registers, gets the `cnt` clock, reads run and mode registers, derives interval and closed-window size, sets min/max hardware heartbeat and timeout from firmware configuration, forces nowayout, conditionally requests an error IRQ when ECM reset mode is not selected, conditionally requests a pretimeout IRQ when WIE is set, and registers the watchdog. Start writes the run key to `WDTA0WDTE`.

State and persistence behavior: Linux does not program the full WWDT mode because hardware can be set up only once after boot. State is firmware-defined register configuration, watchdog running bit, calculated heartbeat windows, and optional IRQ subscriptions.

Dependencies and integration points: depends on OF compatibles, a `cnt` clock, named `error` and `pretimeout` IRQ resources, watchdog pretimeout notification, and R-Car ECM behavior.

Risks and edge cases: if firmware did not configure WWDT correctly, Linux has limited ability to repair it. Window size is a closed-window fraction, so early pings can violate hardware timing. `devm_watchdog_register_device()` return is ignored in probe, which is a notable error-handling weakness.

Test signals: firmware-running and stopped cases, all WDTA0OVF/WDTA0WS derived timing values, error and pretimeout IRQ delivery, nowayout behavior, and registration failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/renesas_wwdt.c -->
