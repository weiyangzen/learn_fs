<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/realtek_otto_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/realtek_otto_wdt.c

Purpose: watchdog-core driver for Realtek Otto MIPS SoCs, supporting two watchdog phases, pretimeout notification, configurable reset mode, and restart.

Important APIs, types, and functions: `struct otto_wdt_ctrl` owns the watchdog, device, MMIO base, clock rate, and phase1 IRQ. Key functions are `otto_wdt_start()`, `otto_wdt_stop()`, `otto_wdt_ping()`, `otto_wdt_determine_timeouts()`, timeout/pretimeout setters, `otto_wdt_restart()`, `otto_wdt_phase1_isr()`, and probe helpers for clock and reset mode.

Control flow: probe maps registers, clears stale interrupts, resets control defaults, gets the clock, requests the named `phase1` IRQ, parses optional `realtek,reset-mode`, sets watchdog bounds, programs an initial timeout/pretimeout pair, and registers with watchdog core. Timeout programming searches prescaler values until both phase fields fit. Phase1 IRQ clears the interrupt and calls `watchdog_notify_pretimeout()`. Restart disables phase1 IRQ, picks reset mode from reboot action, programs the shortest enabled timeout, and waits.

State and persistence behavior: state is MMIO control, phase counters, selected reset mode, watchdog timeout/pretimeout, clock rate, and IRQ binding. Pretimeout cannot be fully disabled, so the driver always keeps phase split state.

Dependencies and integration points: depends on clocks, platform IRQ resources, fwnode properties, bitfield helpers, reboot action constants, watchdog core, and OF compatibles for RTL8380/8390/9300/9310.

Risks and edge cases: timeout rounding can change requested values; pretimeout must be less than timeout. Restart disables the IRQ but does not restore it because reset is expected. Bad clock rate makes all time calculations invalid. Hardware cannot be stopped after phase1 according to comments.

Test signals: reset-mode property variants, timeout/pretimeout rounding, phase1 interrupt notification, start/stop/ping MMIO writes, restart actions for soft/warm/default reboot, and invalid clock/property failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/realtek_otto_wdt.c -->
