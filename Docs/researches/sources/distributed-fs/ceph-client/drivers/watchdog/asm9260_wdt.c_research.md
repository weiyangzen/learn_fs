# sources/distributed-fs/ceph-client/drivers/watchdog/asm9260_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/asm9260_wdt.c` is a watchdog-core driver for Alphascale ASM9260 watchdog hardware. It supports hardware reset, software-reset-via-interrupt, and debug modes, manages module and AHB clocks, and provides restart support. The complete 376-line source was read for this report.

## Important APIs, Types, and Functions

`struct asm9260_wdt_priv` stores device, watchdog, clocks, reset control, MMIO base, IRQ, watchdog frequency, and selected mode. Operations are `asm9260_wdt_feed()`, `asm9260_wdt_gettimeleft()`, `asm9260_wdt_enable()`, `asm9260_wdt_disable()`, `asm9260_wdt_settimeout()`, and `asm9260_restart()`. Other important functions are `asm9260_wdt_sys_reset()`, `asm9260_wdt_irq()`, `asm9260_wdt_get_dt_clks()`, `asm9260_wdt_get_dt_mode()`, and `asm9260_wdt_probe()`.

## Control Flow

Probe allocates state, maps registers, obtains reset control, enables/configures clocks, initializes watchdog min/max/default, parses `alphascale,mode`, optionally requests an IRQ for software/debug modes, sets restart priority, arranges stop-on-reboot/unregister, and registers the device. Start writes mode bits, updates timeout register, and feeds with the required `0xaa`/`0x55` sequence. Stop asserts/deasserts reset because hardware has no direct disable. Software reset modes use an IRQ handler to call `asm9260_wdt_sys_reset()` unless in debug mode. Restart forces a fast watchdog reset by writing a minimal timeout and bad feed value.

## State and Persistence Behavior

Runtime state includes selected mode, watchdog frequency, and timeout in `watchdog_device`. Hardware state is in WDMOD, WDTC, WDFEED, and WDTV registers. Clock enable state is devm-managed through cleanup actions. No disk persistence exists.

## Dependencies and Integration Points

The driver depends on OF compatible `alphascale,asm9260-wdt`, clock framework, reset controller, optional IRQ, MMIO access, and watchdog core. Kconfig selects both `WATCHDOG_CORE` and `RESET_CONTROLLER`.

## Risks and Edge Cases

Disabling by reset control assumes exclusive reset line access and safe reset semantics. Software/debug modes depend on an optional IRQ; missing IRQ changes behavior. `alphascale,mode` strings outside `hw`, `sw`, and `debug` fall back to hardware reset. The restart path intentionally writes an invalid feed pattern.

## Test Signals

Test clock setup and cleanup failure paths, reset-control disable, mode parsing, IRQ and no-IRQ modes, feed sequence, max-timeout calculation, restart behavior, and stop-on-reboot/unregister.
