# sources/distributed-fs/ceph-client/drivers/input/touchscreen/hycon-hy46xx.c

## Purpose
`hycon-hy46xx.c` is an I2C/regmap driver for HYCON HY46xx capacitive touch controllers. It reports up to 11 multitouch contacts and exposes controller tuning/status registers through per-attribute sysfs files.

## Important APIs, types, and functions
- `struct hycon_hy46xx_data` stores I2C/input/regmap state, regulator/reset GPIO, mutex, touchscreen properties, and cached tuning/status fields.
- `hycon_hy46xx_check_checksum()` verifies the report checksum using the packet-supplied length.
- `hycon_hy46xx_isr()` reads a 0x44-byte report, validates checksum, decodes 6-byte touch records, and reports active MT slots.
- `struct hycon_hy46xx_attribute` plus `HYCON_ATTR_U8`/`HYCON_ATTR_BOOL` generate sysfs attributes for threshold, glove, report speed, filters, gain, edge offset, versions, and chip IDs.
- `hycon_hy46xx_setting_show()` and `_store()` synchronize cache and hardware register values under a mutex.
- `hycon_hy46xx_get_defaults()` writes optional device-property defaults to hardware.
- `hycon_hy46xx_get_parameters()` reads current hardware settings into the cache.
- `hycon_hy46xx_probe()` powers, resets, initializes regmap/input/sysfs/IRQ, and registers input.

## Control flow
Probe enables the `vcc` regulator with devm cleanup, optionally pulses reset, allocates input, initializes regmap, applies default properties, caches parameters, configures touchscreen properties and 11 MT slots, stores client data, requests IRQ, and registers input. IRQ reads the whole report from register 0, validates checksum, skips reserved touches, uses the top bits as event type, extracts 12-bit X/Y and slot ID, reports non-UP contacts, and syncs.

## State and persistence
Controller tuning writes through sysfs and default properties persist in hardware until reset/power cycle. The driver mirrors each sysfs field in `hycon_hy46xx_data` and warns if hardware reads differ. No firmware state is managed.

## Dependencies and integration points
The driver uses I2C, regmap, regulators, GPIO descriptors, input/MT, touchscreen properties, sysfs device groups, IRQ threading, OF/I2C matching, and asynchronous probe preference.

## Risks
- Default property writes do not enforce the same range limits as sysfs stores.
- Checksum length comes from the packet; malformed lengths can affect validation semantics.
- Sysfs attributes expose mutable controller tuning that can degrade usability without a reset path.
- Input axes are initially configured with max `-1` and rely on touchscreen properties for useful bounds.

## Test signals
- Probe all listed compatibles with and without reset GPIO and default properties.
- IRQ tests should cover checksum failure, reserved/up/down/contact event types, maximum point count, and invalid slot IDs.
- Sysfs tests should cover range enforcement, bool handling, read/cache mismatch warnings, and read-only version/chip attributes.
