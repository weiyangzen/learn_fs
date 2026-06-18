# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ili210x.c

## Purpose
`ili210x.c` is an I2C touchscreen driver for Ilitek ILI210x/ILI2117/ILI2120/ILI251x controllers. It abstracts chip-specific report formats, supports IRQ or polling input, exposes calibration/version/mode sysfs attributes, and implements ILI251x firmware update from Intel HEX firmware.

## Important APIs, types, and functions
- `struct ili2xxx_chip` provides per-chip register read, touch-data read, touch parser, polling continuation policy, max touches, resolution, and feature flags.
- `struct ili210x` stores client/input/reset GPIO, touchscreen properties, chip data, cached firmware/kernel/protocol versions, IC mode, and a `stop` flag.
- Chip parsers handle ILI210x, ILI211x checksumed packets, ILI212x, and ILI251x split touch reports and optional pressure.
- `ili210x_process_events()` reads reports and loops at 15 ms while the chip-specific continuation callback says contact polling should continue.
- Firmware metadata helpers cache resolution, firmware version, kernel version, protocol version, and boot mode for ILI251x.
- `ili210x_calibrate()` writes `REG_CALIBRATE` for capable chips.
- Firmware update helpers parse IHEX to a 64 KiB buffer, switch application/bootloader modes, poll busy, write dataflash and application blocks, verify CRC readback, reset, and refresh cached state.
- `ili210x_i2c_probe()` selects chip data, resets hardware, configures input, sets up IRQ or polling, installs a stop action, and registers input.

## Control flow
Probe resolves chip data from OF or I2C ID, optionally asserts a reset GPIO with devm power-down action, allocates state/input, sets default MT axes, caches firmware metadata if supported, parses touchscreen properties, initializes slots, and chooses interrupt or polling mode. Runtime input processing reads one or more reports, reports each chip's active contacts into stable slots, and repeats if the protocol needs continued polling for contact release.

Firmware update is exposed through `firmware_update` only on ILI251x. The store path requests `ilitek/ili251x.bin` as IHEX, flattens it, disables IRQ if present, hardware resets, switches to bootloader, writes DF and AC areas in 32-byte chunks with busy polling and CRC checks, switches back to application mode, refreshes cached metadata, and resets again.

## State and persistence
Normal touch state is runtime-only. Calibration and firmware update commands mutate controller state; ILI251x firmware writes are persistent. Cached version/mode/resolution fields reflect the last successful metadata refresh. The `stop` flag is a devm cleanup signal for a potentially looping polling/event path.

## Dependencies and integration points
The driver uses I2C, input/MT, touchscreen properties, GPIO reset, firmware and IHEX loaders, CRC-CCITT, sysfs attribute visibility, IRQ or input polling, and OF/I2C matching.

## Risks
- ILI251x firmware update is complex and persistent; mode switching, address ranges, CRC lengths, and reset recovery all need hardware validation.
- `ili251x_read_reg_common()` returns `ret` rather than normalized `error` in one failure path, which can leak positive short-transfer counts.
- The IHEX flattening buffer is not explicitly initialized before sparse records are copied, so gaps depend on allocator contents unless firmware is dense.
- Event polling can loop while contacts remain active; cleanup relies on the `stop` flag.
- Firmware-update sysfs has no input value semantics; any write attempts an update.

## Test signals
- Probe all supported chip IDs with IRQ and no-IRQ polling.
- Report tests should cover each chip parser, ILI211x checksum failures, pressure reporting, release polling, and touchscreen property transforms.
- Sysfs tests should verify attribute visibility by feature flag, calibration input validation, and cached version/mode formatting.
- Firmware tests should cover malformed IHEX, oversize records, sparse records, bootloader switch retries, busy timeout, CRC mismatch, and recovery after failed update.
