# sources/distributed-fs/ceph-client/drivers/watchdog/pseries-wdt.c

## Purpose
`pseries-wdt.c` exposes IBM POWER pSeries hypervisor watchdog support through the watchdog core. It uses the `H_WATCHDOG` hypercall to query capabilities, start, and stop a hypervisor-managed timer.

## Important APIs, types, and functions
`struct pseries_wdt` embeds `watchdog_device`, selected timeout action, and one-based watchdog number. Key functions are `pseries_wdt_start`, `pseries_wdt_stop`, `pseries_wdt_probe`, suspend, and resume. Hypercall flags encode start/stop/query and expiry actions.

## Control flow
Probe queries capabilities with `H_WATCHDOG`, allocates driver state, currently selects watchdog number 1, validates module `action`, computes min timeout from hypervisor milliseconds, seeds timeout from module parameter, applies nowayout and stop-on-reboot/unregister, then registers. Start sends `H_WATCHDOG` with start action, watchdog number, and timeout milliseconds. Stop sends stop and accepts `H_NOOP`. Suspend stops if active; resume restarts if active.

## State and persistence
The hypervisor owns actual timer state. The driver keeps selected watchdog number/action and core timeout state. No bootstatus is decoded.

## Dependencies and integration points
It depends on pSeries platform device `pseries-wdt`, POWER `plpar_hcall` APIs, watchdog core, and module parameters `action`, `timeout`, and `nowayout`.

## Risks and test signals
Risks include support for only watchdog number 1, no ping op so core keepalive depends on start/stop semantics, min/max unit conversion, hypervisor busy/hardware errors collapsed to `-EIO`, and advertised pretimeout option without set_pretimeout or event path. Test signals include unsupported hypervisor, action validation, min timeout handling, H_NOOP stop, suspend/resume active watchdog, stop-on-reboot, and hypercall error injection.
