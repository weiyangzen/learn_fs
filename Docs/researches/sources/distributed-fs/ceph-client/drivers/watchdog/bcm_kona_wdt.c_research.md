# sources/distributed-fs/ceph-client/drivers/watchdog/bcm_kona_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/bcm_kona_wdt.c` is a watchdog-core platform driver for Broadcom Kona secure watchdog hardware. It programs a secure watchdog control register with timeout, enable, reset-enable, and resolution fields, and optionally exposes debugfs diagnostics. The complete 339-line source was read for this report.

## Important APIs, Types, and Functions

`struct bcm_kona_wdt` stores MMIO base, resolution, spinlock, and optional debugfs state. Hardware helpers are `secure_register_read()`, `bcm_kona_wdt_ctrl_reg_modify()`, `bcm_kona_wdt_set_resolution_reg()`, and `bcm_kona_wdt_set_timeout_reg()`. Watchdog operations are `bcm_kona_wdt_set_timeout()`, `bcm_kona_wdt_get_timeleft()`, `bcm_kona_wdt_start()`, and `bcm_kona_wdt_stop()`. Debug helpers are `bcm_kona_show()`, `bcm_kona_wdt_debug_init()`, and `bcm_kona_wdt_debug_exit()`. Probe/remove functions are `bcm_kona_wdt_probe()` and `bcm_kona_wdt_remove()`.

## Control Flow

Probe allocates state, maps registers, sets default resolution, writes the resolution field, stores driver data, binds a singleton watchdog device to the instance, writes an initial timeout with the watchdog disabled, arranges stop-on-reboot/unregister, registers the watchdog, and creates debugfs if enabled. Start writes timeout plus enable and system-reset-enable bits. Stop clears enable and reset-enable bits. Set-timeout only updates the watchdog-core field; the new value is programmed on the next start. Get-timeleft reads the secure count register and converts ticks to seconds.

## State and Persistence Behavior

The resolution determines tick conversion and is programmed into hardware. The watchdog-core timeout is mirrored to hardware only through `bcm_kona_wdt_set_timeout_reg()`. `secure_register_read()` tracks debug busy count when debugfs is enabled. Hardware may temporarily set `SECWDOG_WD_LOAD_FLAG` while count fields are updating.

## Dependencies and Integration Points

It depends on OF compatible `brcm,kona-wdt`, platform MMIO resources, spinlocks, watchdog core, optional debugfs, and secure watchdog register semantics.

## Risks and Edge Cases

`secure_register_read()` can return `-ETIMEDOUT`; `bcm_kona_wdt_get_timeleft()` returns that negative value as an unsigned int, which can appear as a very large timeleft. The singleton `bcm_kona_wdt_wdd` assumes one instance. There is no nowayout module parameter. Set-timeout does not reprogram active hardware, so runtime timeout changes may not take effect until restart/start depending on watchdog core behavior.

## Test Signals

Test secure read timeout behavior, resolution programming, start/stop bit masking, active timeout changes, debugfs info output under `CONFIG_BCM_KONA_WDT_DEBUG`, singleton behavior, and stop-on-reboot/unregister cleanup.
