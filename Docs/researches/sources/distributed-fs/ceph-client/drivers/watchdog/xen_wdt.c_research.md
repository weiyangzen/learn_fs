# sources/distributed-fs/ceph-client/drivers/watchdog/xen_wdt.c

## Purpose
`xen_wdt.c` exposes the Xen hypervisor scheduler watchdog as a Linux watchdog-core device when running inside a Xen domain.

## Important APIs, types, and functions
Global state includes the synthetic platform device, `struct sched_watchdog wdt`, and `wdt_expires`. Watchdog ops are `xen_wdt_start`, `xen_wdt_stop`, `xen_wdt_kick`, and `xen_wdt_get_timeleft`. Probe verifies hypervisor support with `SCHEDOP_watchdog`, initializes timeout and nowayout, and registers. Suspend/resume preserve the Xen watchdog id around stop/restart.

## Control flow
Module init exits outside Xen, registers a platform driver, then creates a simple platform device. Probe sends a sentinel watchdog request expecting `-EINVAL` to indicate support, configures watchdog core policies, and registers. Start sets the requested timeout and asks Xen to allocate a watchdog id. Ping updates the existing id. Stop sends timeout zero and clears the id. Resume re-creates the watchdog if it was active before suspend.

## State and persistence
The Xen watchdog id is hypervisor state. `wdt_expires` is a kernel-side approximation used for `GETTIMELEFT`. State is global, so the driver supports one watchdog instance.

## Dependencies and integration points
It depends on Xen domain detection, `HYPERVISOR_sched_op`, Xen `sched_watchdog` ABI, platform bus, and watchdog core.

## Risks and test signals
Risks include unexpected hypervisor return codes, `BUG_ON(!err)` in start if the hypervisor returns zero without assigning an id, stale `wdt_expires`, suspend/resume id preservation, and unsigned underflow in timeleft after expiry. Test signals include Xen with and without watchdog op support, start/stop/ping, timeout module parameter, suspend/resume with active and inactive watchdogs, and hypercall failure injection.
