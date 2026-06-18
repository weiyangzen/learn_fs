# sources/distributed-fs/ceph-client/drivers/watchdog/bcm2835_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/bcm2835_wdt.c` is a watchdog-core driver for Broadcom BCM2835 power-management watchdog hardware used by Raspberry Pi-class systems. It also provides restart and a firmware-coordinated poweroff path using reset-status partition bits. The complete 247-line source was read for this report.

## Important APIs, Types, and Functions

`struct bcm2835_wdt` stores the PM base and spinlock. Important globals are singleton watchdog device `bcm2835_wdt_wdd` and optional `bcm2835_power_off_wdt`. Operations are `bcm2835_wdt_start()`, `bcm2835_wdt_stop()`, `bcm2835_wdt_get_timeleft()`, and `bcm2835_restart()`. Helper paths include `bcm2835_wdt_is_running()`, `__bcm2835_restart()`, `bcm2835_power_off()`, `bcm2835_wdt_probe()`, and `bcm2835_wdt_remove()`.

## Control Flow

Probe obtains PM state from the parent device, allocates driver state, initializes a spinlock, uses the parent PM base, initializes timeout/nowayout, marks `WDOG_HW_RUNNING` if the bootloader left full-reset watchdog enabled, sets restart priority, registers the watchdog, and optionally installs `pm_power_off` if the parent is the system power controller. Start writes password-protected timeout and reset-control bits under spinlock. Stop writes reset-control reset value. Restart sets a very short timeout and full-reset mode, then delays. Poweroff writes the Raspberry Pi halt partition marker into reset status before invoking restart.

## State and Persistence Behavior

Runtime state is mostly in watchdog core and password-protected PM registers. `pm_power_off` is a global kernel hook set on probe and cleared on remove if owned. The reset-status halt marker persists long enough for firmware to choose halt behavior after reset.

## Dependencies and Integration Points

It depends on the Broadcom PM MFD parent (`struct bcm2835_pm`), watchdog core, OF system-power-controller indication, global `pm_power_off`, MMIO access, and restart priority handling.

## Risks and Edge Cases

The singleton `bcm2835_wdt_wdd` assumes one hardware instance. Poweroff is implemented as reset plus firmware halt marker, so firmware interpretation is required. Stop uses a reset-control write rather than a separate disable bit. The `start()` timeout conversion is limited by a 20-bit watchdog field.

## Test Signals

Test boot-running detection, password-protected register writes, timeout conversion, restart, poweroff marker behavior, `pm_power_off` ownership cleanup, and watchdog core max-hardware-heartbeat handling.
