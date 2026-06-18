# sources/distributed-fs/ceph-client/drivers/watchdog/ziirave_wdt.c

## Purpose
`ziirave_wdt.c` is an I2C watchdog-core driver for the Zodiac/ZII RAVE switch watchdog processor. It also exposes sysfs attributes for firmware/bootloader versions, reset reason, reset duration configuration, and firmware update.

## Important APIs, types, and functions
`struct ziirave_wdt_data` holds a sysfs mutex, watchdog device, firmware and bootloader revisions, and reset reason. Watchdog ops are `ziirave_wdt_start`, `ziirave_wdt_stop`, `ziirave_wdt_ping`, `ziirave_wdt_set_timeout`, and `ziirave_wdt_get_timeleft`. Firmware helpers include `ziirave_firm_read_ack`, `ziirave_firm_set_read_addr`, `ziirave_firm_write_pkt`, `ziirave_firm_verify`, and `ziirave_firm_upload`. Sysfs handlers expose firmware, bootloader, reset reason, and trigger update from `ziirave_wdt.fw`.

## Control flow
Probe checks SMBus byte, byte-data, and block-write support, allocates state, initializes watchdog limits and groups, obtains timeout from module/OF or device register, writes it back, sets nowayout, handles initial unconfigured state by stopping the watchdog, programs optional reset duration, reads revisions and reset reason, validates the reason string, then registers. Firmware update jumps to bootloader, starts download, writes ihex records in 16-byte packets split at 128-byte pages, sends an empty packet, verifies by reading back bytes, ends download, resets the processor, rereads firmware version, and restores timeout.

## State and persistence
Device timeout, state, reset duration, revisions, and firmware live in the external watchdog processor. Kernel state caches version and reset reason for sysfs and serializes firmware updates with `sysfs_mutex`.

## Dependencies and integration points
It depends on I2C SMBus APIs, Intel HEX firmware loader, OF property `reset-duration-ms`, watchdog core, device sysfs groups, and `linux/unaligned.h` for packet formatting.

## Risks and test signals
Risks include destructive firmware update failures, read-only flash range filtering, checksum/page split bugs, stale cached revisions, reset reason array validation, missing `devm` unregister because manual `watchdog_register_device` is used, and I2C adapters lacking required SMBus operations. Test signals include valid and invalid timeouts, reset-duration property bounds, firmware update success/failure/verify mismatch, reset reason values, initial state handling, I2C error injection, and remove path unregister.
