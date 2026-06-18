# sources/distributed-fs/ceph-client/drivers/watchdog/db8500_wdt.c

## Purpose
This driver exposes the ST-Ericsson DB8500 A9 watchdog controlled through PRCMU firmware calls. It uses a single static watchdog device for all CPU watchdog operations.

## Important APIs, types, and functions
Operations are `db8500_wdt_start`, `db8500_wdt_stop`, `db8500_wdt_keepalive`, and `db8500_wdt_set_timeout`, each wrapping `prcmu_*_a9wdog` functions. The static `db8500_wdt` stores watchdog info, ops, and min/max limits. PM callbacks are `db8500_wdt_suspend` and `db8500_wdt_resume`.

## Control Flow
Probe sets the parent, nowayout, disables auto-off on sleep for CPU1, loads a default 10-minute timeout into all watchdogs, and registers the device. Start/stop/kick call PRCMU for `PRCMU_WDOG_ALL`. Set-timeout stops, loads a millisecond timeout, and restarts. Suspend/resume reconfigure auto-off policy and reload/restart the watchdog when active.

## State and Persistence
State is primarily in PRCMU-managed watchdog hardware plus the static watchdog object and module timeout parameter. There is no per-device allocation or persistent storage.

## Dependencies and Integration Points
The driver depends on DBx500 PRCMU MFD APIs, platform bus name `db8500_wdt`, watchdog core, and legacy platform suspend/resume callbacks.

## Risks and Test Signals
Risks include static singleton assumptions, timeout module parameter being overwritten to 600 during probe, ignored PRCMU return values in set_timeout, min_timeout allowing zero, and sleep auto-off behavior. Tests should cover PRCMU failure injection, active suspend/resume, timeout bounds, stop/start sequencing, and platform probe/register errors.
