# sources/distributed-fs/ceph-client/drivers/watchdog/cadence_wdt.c

## Purpose
This platform driver supports the Cadence/Xilinx watchdog used by Zynq-class SoCs. It programs the zero-mode, counter-control, restart, and status registers to provide reset-on-timeout or interrupt-on-timeout operation.

## Important APIs, types, and functions
`struct cdns_wdt` stores MMIO base, clock, prescaler selection, reset-vs-IRQ mode, spinlock, and embedded watchdog. Main ops are `cdns_wdt_start`, `cdns_wdt_stop`, `cdns_wdt_reload`, and `cdns_wdt_settimeout`. Probe handles `devm_platform_ioremap_resource`, optional IRQ registration, `devm_clk_get_enabled`, `watchdog_init_timeout`, and `devm_watchdog_register_device`. PM callbacks stop/restart the device around suspend.

## Control Flow
Probe maps registers, reads `reset-on-timeout`, optionally registers an IRQ handler when reset is not used, enables the input clock, chooses a prescaler from the clock rate, and registers the watchdog. Start disables the timer, computes and clamps the counter value, writes the protected CCR and ZMR registers with access keys, selects reset or IRQ output, and kicks the counter. Set-timeout updates `wdd->timeout` and restarts hardware.

## State and Persistence
Runtime state includes selected prescaler, clock handle, MMIO registers, and watchdog core timeout. Hardware registers are volatile and are reprogrammed on resume if the watchdog was active. `watchdog_stop_on_unregister` and reboot stop are requested.

## Dependencies and Integration Points
The driver uses the platform bus, OF compatible `cdns,wdt-r1p2`, Linux clock framework, IRQ subsystem, MMIO accessors, and the watchdog core.

## Risks and Test Signals
Risks include clock-rate based timeout rounding, use of interrupt mode without a valid IRQ, lock coverage around protected register writes, and suspend/resume clock sequencing. Tests should cover reset and interrupt DT modes, 75 MHz threshold selection, max timeout clamping, reload while active, timeout changes, and system suspend with active/inactive watchdog states.
