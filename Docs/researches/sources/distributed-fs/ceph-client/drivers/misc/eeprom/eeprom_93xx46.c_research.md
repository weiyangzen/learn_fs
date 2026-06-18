# sources/distributed-fs/ceph-client/drivers/misc/eeprom/eeprom_93xx46.c

## Purpose
SPI nvmem provider for 93xx46-family Microwire EEPROMs, covering 93c46, 93c56, 93c66, Atmel AT93C46D, and Microchip 93LC46B variants. It exposes the EEPROM through nvmem and, when writable, a sysfs-only whole-device erase trigger.

## Important APIs, Types, And Functions
`struct eeprom_93xx46_platform_data` carries data width, size, read-only flag, per-device quirks, and an optional select GPIO. `struct eeprom_93xx46_dev` holds the SPI device, nvmem config/device, address length, size, and mutex. `eeprom_93xx46_read()` and `eeprom_93xx46_write()` implement nvmem callbacks. `eeprom_93xx46_ew()` toggles erase/write enable, `eeprom_93xx46_write_word()` emits one byte or word write, and `eeprom_93xx46_eral()` performs erase-all. Probe parses `data-size`, `read-only`, `select-gpios`, and match-data quirks before registering nvmem.

## Control Flow
Probe builds platform data from firmware properties, computes byte size and address length, initializes nvmem callbacks, and optionally creates `erase`. Reads clamp the requested range, assert the select GPIO, send an OP_READ command/address transfer, receive data, delay for chip-select timing, and repeat for single-word-read variants. Writes clamp range, align 16-bit devices to even byte counts, enable writes, assert select, loop over words, disable writes, and return the first SPI error. The erase sysfs path parses a boolean and sequences EWEN, ERAL, EWDS.

## State, Persistence, And Dependencies
Persistent state is the EEPROM contents; driver state is only the mutex, geometry, quirks, and nvmem registration. It depends on SPI core, firmware property APIs, GPIO descriptors, nvmem-provider, delay helpers, and device-tree/SPI ID tables.

## Integration Points
Device tree compatibles and SPI IDs map to chip geometry and quirks. Consumers access data via nvmem; legacy users may see nvmem compatibility files. The `erase` attribute is writable only when the device is not read-only.

## Risks
All write and erase paths are destructive and guarded only by firmware read-only configuration plus root-only nvmem configuration. Offsets must match the configured 8-bit or 16-bit addressing mode. Single-word-read and extra-cycle quirks are timing-sensitive. SPI transfer `bits_per_word` is nonstandard and adapter support matters. The 6 ms fixed program/erase delay may be insufficient for slow parts or overly conservative for fast parts.

## Test Signals
Useful checks are probe success for each compatible, nvmem read boundary clamping, 16-bit write alignment, read-only suppression of write/erase, GPIO select transitions around transactions, SPI adapter behavior with unusual command bit widths, and erase/write/readback validation on hardware or an SPI EEPROM emulator.
