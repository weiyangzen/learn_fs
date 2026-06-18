# sources/distributed-fs/ceph-client/drivers/input/touchscreen/wdt87xx_i2c.c

## Purpose
`wdt87xx_i2c.c` is an I2C multitouch driver for Weida HiTech WDT87xx controllers. It reports up to ten contacts and exposes sysfs-triggered firmware/configuration update operations using vendor feature reports.

## Important APIs, Types, And Functions
`struct wdt87xx_sys_param` caches firmware/platform IDs, physical dimensions, scaling factor, logical max coordinates, and USB-style VID/PID. `struct wdt87xx_data` stores client, input, firmware mutex, parameters, and phys string. Descriptor/string/feature helpers implement the vendor protocol over I2C. Firmware helpers validate RIFF/WHIF chunks, unlock flash, erase/write 4 KiB pages, compare MISR checksums, relock, reset, and refresh parameters. `wdt87xx_ts_interrupt()` reads V1 touch packets and `wdt87xx_report_contact()` reports MT slots.

## Control Flow
Probe checks plain I2C, allocates state, reads system parameters from descriptors and strings, creates the MT input device, then requests a threaded IRQ. Sysfs `update_fw` and `update_config` request firmware files, validate them against the chip ID, lock `fw_mutex`, disable IRQ, load the selected chunk, reset, and refresh parameters. Suspend disables IRQ and sends idle/stop; resume waits, restarts reporting, and enables IRQ.

## State And Persistence
Runtime state includes cached controller parameters and firmware metadata. Firmware/config update paths persistently write controller flash. The driver caches no contact state beyond input MT tracking.

## Dependencies And Integration Points
It depends on I2C raw transfers, input MT, firmware loader files `wdt87xx_fw.bin` and `wdt87xx_cfg.bin`, ACPI ID `WDHT0001`, sysfs device attributes, unaligned access helpers, and system sleep PM.

## Risks
Firmware update is high-risk: malformed chunks, checksum mismatch, interrupted writes, or lock/start failure can leave the device unusable. Sysfs update stores ignore input text and trigger immediately. `wdt87xx_report_contact()` drops inactive contacts and relies on `INPUT_MT_DROP_UNUSED` for cleanup. Parameter-derived Y scaling can divide by physical width, so bad descriptor values matter.

## Test Signals
Test descriptor parsing, sysfs read attributes, IRQ packet parsing for valid/invalid contacts, firmware validation failures, page checksum retry logic, IRQ disable during update, suspend/resume command failures, ACPI matching, and recovery after reset/parameter refresh.
