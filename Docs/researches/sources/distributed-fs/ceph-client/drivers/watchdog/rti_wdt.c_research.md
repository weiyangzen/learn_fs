<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rti_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rti_wdt.c

Purpose: watchdog-core driver for Texas Instruments K3 RTI windowed watchdog modules, including always-nowayout behavior and optional reserved-memory bootstatus handoff.

Important APIs, types, and functions: `struct rti_wdt_device` holds MMIO base, source frequency, and watchdog. Key routines are `rti_wdt_start()`, `rti_wdt_ping()`, `rti_wdt_setup_hw_hb()`, `rti_wdt_get_timeleft_ms()`, `rti_wdt_get_timeleft()`, probe, and remove.

Control flow: probe gets the clock rate, enables runtime PM, maps registers, initializes watchdog bounds and nowayout, detects already-enabled hardware, derives heartbeat/window settings from hardware, optionally reads a reserved memory magic sequence to set `WDIOF_CARDRESET`, initializes timeout, registers, records last hardware keepalive when applicable, and runtime-suspends if not running. Start resumes PM, programs preload, NMI reaction, 50 percent open window, min hardware heartbeat, and enable key. Ping writes the two-key service sequence.

State and persistence behavior: state includes runtime PM state, watchdog enabled bit, preload/window registers, min heartbeat, last-ping estimate, timeout, and reserved-memory reset-cause words that are cleared after read.

Dependencies and integration points: uses clocks, PM runtime, reserved-memory OF mapping, `memremap()`, watchdog core last keepalive, and K3 RTI register protocol.

Risks and edge cases: windowed watchdog pings too early can be fatal; min heartbeat must match hardware window. Reserved memory must be at least 12 bytes and trusted. If already running, heartbeat configuration is ignored. Nowayout is forced.

Test signals: already-running detection, last-ping calculation, reserved-memory magic and clearing, window size cases, early/late ping behavior, runtime PM balance, and get-timeleft at timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rti_wdt.c -->
