# sources/distributed-fs/ceph-client/drivers/watchdog/booke_wdt.c

## Purpose
`booke_wdt.c` implements the PowerPC Book-E CPU watchdog using per-CPU timer control/status SPRs. It exposes a global watchdog device for Book-E systems and supports optional boot-time enable through module parameters.

## Important APIs, types, and functions
The central object is the static `booke_wdt_dev`. Operations are `booke_wdt_start`, `booke_wdt_stop`, `booke_wdt_ping`, and `booke_wdt_set_timeout`. Low-level helpers run on every CPU through `on_each_cpu`: `__booke_wdt_set`, `__booke_wdt_ping`, `__booke_wdt_enable`, and `__booke_wdt_disable`. On E500, `period_to_sec` and `sec_to_period` translate between watchdog period encodings and seconds.

## Control Flow
Module init sets firmware version from `cur_cpu_spec`, maps the configured period into seconds, applies nowayout, optionally starts the watchdog, and registers the device. Starting clears TSR status and writes TCR with watchdog interrupt/restart control and the encoded period on all CPUs. Ping clears TSR watchdog status on all CPUs. Stopping clears WIE and period fields where hardware permits effective disable.

## State and Persistence
State is held in CPU SPRs, so each CPU must be programmed consistently. There is no storage persistence. On some Book-E hardware, restart-control bits cannot be fully undone once set, so stop is implemented by clearing enable/period fields as far as the architecture permits.

## Dependencies and Integration Points
The driver depends on PowerPC Book-E SPR definitions, timebase frequency, SMP callbacks, and watchdog core registration. E500-specific timeout math uses `ppc_tb_freq` and 64-bit division.

## Risks and Test Signals
Risks include timeout conversion overflow, SMP CPU hotplug assumptions, partial disable semantics, and misconfigured `booke_wdt_period`. Tests should cover E500 and non-E500 builds, start-before-register parameter behavior, ping across CPUs, set_timeout range boundaries, and reboot/reset behavior under real hardware or architecture emulation.
