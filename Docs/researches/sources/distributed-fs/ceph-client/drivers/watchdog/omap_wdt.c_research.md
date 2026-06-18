# sources/distributed-fs/ceph-client/drivers/watchdog/omap_wdt.c

## Purpose
`omap_wdt.c` controls TI OMAP 16xx/24xx/34xx non-secure 32 kHz watchdogs. It uses the watchdog core with runtime PM, posted-write synchronization, bootstatus reporting, and optional early enable.

## Important APIs, types, and functions
`struct omap_wdt_dev` stores the watchdog object, MMIO base, device, user-active flag, trigger pattern, and mutex. Important helpers are `omap_wdt_reload`, `omap_wdt_enable`, `omap_wdt_disable`, `omap_wdt_set_timer`, plus ops `start`, `stop`, `ping`, `set_timeout`, and `get_timeleft`.

## Control flow
Probe maps registers, sets default/min/max timeouts, initializes runtime PM, optionally reads platform reset sources, disables hardware unless `early_enable` is requested, registers the watchdog, and drops runtime PM. Start takes the mutex, marks users active, resumes the device, disables the watchdog to allow programming, sets prescaler and load, reloads, and enables. Stop disables and runtime-suspends. Set-timeout disables, writes load, enables, reloads, and updates core timeout. Shutdown/suspend disable only when users had started it; resume re-enables and reloads.

## State and persistence
Runtime state tracks active users and trigger pattern. Hardware count/load/control registers persist while powered. Bootstatus is derived from platform reset-source callback. No on-disk persistence exists.

## Dependencies and integration points
It depends on `omap_wdt.h`, platform data `omap-wd-timer`, OF compatible `ti,omap3-wdt`, runtime PM, watchdog core, and module parameters `nowayout`, `timer_margin`, and `early_enable`.

## Risks and test signals
Risks include busy-wait loops on posted-write status, runtime PM reference imbalance on error paths, early-enable double start, set-timeout interactions while inactive, and suspend behavior noted as questionable for nowayout. Test signals include bootstatus callback, early_enable, timeout min/max, runtime PM start/stop balance, suspend/resume active watchdog, and get-timeleft conversion.
