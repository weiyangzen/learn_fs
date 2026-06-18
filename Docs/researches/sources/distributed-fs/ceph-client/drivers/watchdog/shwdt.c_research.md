# sources/distributed-fs/ceph-client/drivers/watchdog/shwdt.c

## Purpose
`shwdt.c` drives the integrated watchdog in SuperH processors. The hardware overflow period is extremely short, so the driver uses a kernel timer to keep clearing the hardware while userspace is considered alive, and intentionally stops that internal pinging after the configured userspace heartbeat expires.

## Important APIs, types, and functions
Important state is `clock_division_ratio`, `heartbeat`, `nowayout`, global `next_heartbeat`, and `struct sh_wdt` containing MMIO base, device, optional clock, spinlock, and timer. Watchdog operations are `sh_wdt_start()`, `sh_wdt_stop()`, `sh_wdt_keepalive()`, and `sh_wdt_set_heartbeat()`. `sh_wdt_ping()` is the internal timer callback that clears WOVF/IOVF and reloads the counter. Probe/remove/shutdown are `sh_wdt_probe()`, `sh_wdt_remove()`, and `sh_wdt_shutdown()`.

## Control flow
Module init validates the divisor then registers a platform driver named `sh-wdt`. Probe rejects per-CPU platform IDs, maps the resource, gets an optional clock, initializes the global `sh_wdt_dev`, validates heartbeat, registers the watchdog, sets up the timer, and enables runtime PM. Start resumes PM, enables the clock, schedules the internal timer, sets WTCSR mode/divisor bits, clears the counter and reset status, and enables counting. Userspace pings only extend `next_heartbeat`; the timer performs the real hardware keepalive until that deadline passes.

## State and persistence behavior
The active deadline is global rather than per-device, matching the single global hardware assumption. Timer state, PM usage count, and hardware WTCSR/RSTCSR/CNT registers persist until stop, shutdown, suspend, or reset. There is no durable software state.

## Dependencies and integration points
The driver depends on SuperH watchdog register helpers from `<asm/watchdog.h>`, platform resources, runtime PM, clocks, the watchdog core, and timer infrastructure. It uses a static `struct watchdog_device`, so it is intended for one global watchdog instance.

## Risks and test signals
The main risk is timing: low HZ, slow scheduling, or wrong divisor can allow hardware overflow even when userspace is healthy. Global `next_heartbeat` and static watchdog state would be unsafe for multiple devices, but probe forbids them. Test with valid and invalid divisors/heartbeats, start/stop/ping paths, timer expiry after missed userspace heartbeat, PM suspend/resume, shutdown stop, SH2 reset-status handling, and register traces around WTCSR/CNT writes.
