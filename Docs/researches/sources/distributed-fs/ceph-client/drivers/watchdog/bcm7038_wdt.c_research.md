# sources/distributed-fs/ceph-client/drivers/watchdog/bcm7038_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/bcm7038_wdt.c` is a watchdog-core driver for Broadcom BCM63xx/BCM7038-style watchdog blocks. It programs timeout and command registers with required start/stop sequences and supports both OF and platform-device IDs. The complete 234-line source was read for this report.

## Important APIs, Types, and Functions

`struct bcm7038_watchdog` stores MMIO base, watchdog device, clock rate, and optional clock. Helper functions are `bcm7038_wdt_write()`, `bcm7038_wdt_read()`, `bcm7038_wdt_set_timeout_reg()`, and internal `bcm7038_wdt_ping()`. Watchdog operations wired into `watchdog_ops` are `bcm7038_wdt_start()`, `bcm7038_wdt_stop()`, `bcm7038_wdt_set_timeout()`, and `bcm7038_wdt_get_timeleft()`. Lifecycle and PM functions are `bcm7038_wdt_probe()`, `bcm7038_wdt_suspend()`, and `bcm7038_wdt_resume()`.

## Control Flow

Probe allocates state, maps registers, obtains an optional named clock from platform data, falls back to a 27 MHz default if no usable clock exists, initializes watchdog core limits, arranges stop-on-reboot/unregister, and registers the device. Start writes the timeout register and then pings with the two-word start sequence. Stop writes the two-word stop sequence. `set_timeout()` stops the watchdog, updates `wdd->timeout`, and restarts because hardware cannot modify timeout while running. Suspend stops active watchdogs; resume restarts active watchdogs.

## State and Persistence Behavior

Timeout state is stored in `wdd->timeout` and the hardware timeout register. Clock rate controls timeout conversion and max timeout. The hardware command register also reports time left. No persistent storage exists beyond active hardware registers.

## Dependencies and Integration Points

It depends on platform resources, optional `struct bcm7038_wdt_platform_data`, clock framework, OF compatibles `brcm,bcm6345-wdt` and `brcm,bcm7038-wdt`, platform id `bcm63xx-wdt`, MMIO, PM, and watchdog core.

## Risks and Edge Cases

Big-endian MIPS requires raw read/write access to match CPU-native peripheral byte order. If clock retrieval fails, the default rate may be wrong for a board, affecting timeout accuracy. Timeout changes stop and restart the watchdog, creating a transition window. The file declares a `nowayout` module parameter but never applies it with `watchdog_set_nowayout()`, so it appears ineffective in this version. The helper named `bcm7038_wdt_ping()` is used by start but is not exposed as the watchdog-core `.ping` callback.

## Test Signals

Test endian-specific register access, start/stop command sequences, clock fallback and zero-rate handling, timeout-change restart, get-timeleft conversion, suspend/resume active handling, and whether nowayout behavior matches expectations.
