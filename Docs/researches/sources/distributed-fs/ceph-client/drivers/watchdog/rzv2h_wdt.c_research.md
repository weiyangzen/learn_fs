<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rzv2h_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rzv2h_wdt.c

Purpose: watchdog-core driver for Renesas RZ/V2H(P), RZ/T2H, and RZ/N2H watchdogs, with optional debug-control register support and restart.

Important APIs, types, and functions: `struct rzv2h_of_data` describes clock source/dividers/TOPS/debug-control support. `struct rzv2h_wdt_priv` stores MMIO windows, clocks, reset control, watchdog, and OF data. Key routines are `rzv2h_wdt_ping()`, debug count start/stop helpers, `rzv2h_wdt_setup()`, start/stop/restart, `rzt2h_wdt_wdtdcr_init()`, and probe.

Control flow: probe selects OF data, maps base, gets prepared clocks, optional reset, chooses count clock, computes max hardware heartbeat, enables runtime PM, optionally initializes WDTDCR count-stop state, sets watchdog fields, nowayout, stop-on-unregister, timeout, and registers. Start resumes PM, deasserts reset, delays, writes WDTCR/WDTRCR/WDTSR, starts optional debug count, and refreshes via 0x00/0xff. Stop asserts reset, stops optional debug count, and runtime-suspends. Restart handles inactive clocks manually or resets active hardware, programs shortest window, refreshes, and waits.

State and persistence behavior: state spans reset/clock/PM state, optional WDTDCR counter-stop bit, watchdog control/status/reset registers, and selected OF data. No bootstatus is read.

Dependencies and integration points: uses prepared clocks, optional reset controls, PM runtime, OF match data, watchdog core, and SoC-specific window semantics.

Risks and edge cases: WDTCR and WDTRCR are writable only once between reset release and first refresh, so restart must reset active hardware. Optional `oscclk` must be present for LOCO-source SoCs. Manual `clk_enable()` in restart assumes clocks are already prepared.

Test signals: both OF data variants, optional WDTDCR path, start-stop PM/reset balance, inactive and active restart, refresh sequence ordering, and max hardware heartbeat calculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rzv2h_wdt.c -->
