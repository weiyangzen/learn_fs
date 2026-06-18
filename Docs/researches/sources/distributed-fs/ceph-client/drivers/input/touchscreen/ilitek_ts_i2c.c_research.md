# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ilitek_ts_i2c.c

## Purpose
`ilitek_ts_i2c.c` is an I2C driver for ILITEK 23xx, 25xx, and Lego-series touch ICs using protocol v6-style reports. It initializes protocol metadata, reports multitouch contacts, exposes firmware/product information, and supports basic sleep/wake PM commands.

## Important APIs, types, and functions
- `struct ilitek_ts_data` stores client, reset GPIO, input device, touchscreen properties, protocol callback table/version, product ID, MCU/firmware versions, IC mode, reset timing, screen bounds, and max touch count.
- `struct ilitek_protocol_map` maps logical command indexes to protocol command bytes and handler functions.
- `ilitek_i2c_write_and_read()` implements combined or delayed write/read I2C command transactions.
- `ilitek_process_and_report_v6()` reads 64-byte report packets, fetches additional packets as needed, validates report ID and max-point count, bounds-checks coordinates, and reports active contacts.
- Protocol handlers read protocol, MCU, firmware, screen resolution, touch resolution/max touch, IC mode, sleep, and wake commands.
- `ilitek_protocol_init()` rejects unsupported protocol v3 and older bootloader versions.
- `ilitek_read_tp_info()` populates metadata used by input setup and sysfs.
- `ilitek_input_dev_init()` configures the MT input device from screen bounds and touchscreen properties.
- `ilitek_suspend()`/`ilitek_resume()` disable IRQ and send sleep/wake/reset when the device is not configured as a wake source.

## Control flow
Probe checks I2C functionality, allocates state, gets optional reset GPIO, performs a reset, initializes protocol callbacks/version, reads panel and firmware metadata, registers input, and requests a threaded IRQ. IRQ reads and reports v6 touch data. Sysfs read-only attributes present cached firmware version and product/module strings.

## State and persistence
The driver caches controller metadata at probe. It does not update firmware or persistent configuration. Sleep/wake commands affect controller runtime mode across PM transitions, and reset timing is cached in `reset_time`.

## Dependencies and integration points
The driver integrates with I2C, GPIO reset, input/MT, touchscreen properties, ACPI/OF matching, sysfs groups, wakeup policy, and PM helpers.

## Risks
- `ilitek_i2c_write_and_read()` treats nonnegative short `i2c_transfer()` counts as success; short transfers can lead to stale or incomplete metadata/report data.
- Report buffering assumes a 512-byte stack buffer and 5-byte points; protocol changes or high point counts must remain within bounds.
- If suspend sends sleep and that command fails after IRQ disable, the function returns error without re-enabling IRQ.
- The driver relies on firmware-reported screen bounds and max touch; invalid metadata can prevent input registration or drop touches.

## Test signals
- Probe supported OF/ACPI compatibles and reject unsupported protocol/bootloader versions.
- IRQ tests should cover multi-packet reports, bad report IDs, too-large reported point counts, invalid coordinates, and release frames.
- PM tests should cover wakeup-enabled and wakeup-disabled paths, sleep/wake command failures, and reset after resume.
- Sysfs tests should verify firmware/product formatting from cached probe data.
