# sources/distributed-fs/ceph-client/drivers/watchdog/gxp-wdt.c

## Purpose
This driver supports the HPE GXP watchdog timer. It is created as a child of the timer driver and receives a shared register base through platform data because the timer/watchdog register area is interleaved.

## Important APIs, types, and functions
`struct gxp_wdt` stores the base pointer and watchdog object. Core functions are `gxp_wdt_start`, `gxp_wdt_stop`, `gxp_wdt_ping`, `gxp_wdt_set_timeout`, `gxp_wdt_get_timeleft`, and `gxp_restart`. `gxp_wdt_enable_reload` sets enable and reload bits in the control register.

## Control Flow
Probe allocates private data, takes `dev->platform_data` as MMIO base, initializes a 30-second watchdog with 655.35-second hardware heartbeat, detects already-enabled hardware, sets restart priority, and registers. Start writes count as seconds times 100 ticks and enables reload. Set-timeout updates core timeout and writes a count clamped to hardware heartbeat. Ping just enables reload. Restart writes a count of one, reloads, and waits briefly.

## State and Persistence
State is in the shared timer/watchdog registers and the watchdog core object. If enable is set at probe, `WDOG_HW_RUNNING` is recorded for handoff. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on platform data supplied by the GXP timer driver, raw MMIO byte/word access, watchdog core, restart priority, and reboot stop handling.

## Risks and Test Signals
Risks include trusting platform_data without validation, shared register ownership with the timer driver, tick/second truncation, and nowayout always using `WATCHDOG_NOWAYOUT`. Tests should cover parent-created device, already-running detection, timeout clamping, get_timeleft conversion, restart assertion, and missing/invalid platform data.
