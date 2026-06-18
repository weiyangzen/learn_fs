# sources/distributed-fs/ceph-client/drivers/mfd/smpro-core.c

## Purpose
`smpro-core.c` is the Ampere Altra SMPro I2C MFD parent. It creates a custom regmap for SMPro command formatting, validates the manufacturer ID, and registers hardware monitor, error monitor, and miscellaneous child devices.

## Important APIs, Types, and Functions
`smpro_core_write()` wraps `i2c_master_send()`. `smpro_core_read()` sends a register plus requested length and then reads the value in a two-message I2C transfer. `smpro_regmap_bus` declares big-endian value formatting. `smpro_core_readable_noinc_reg()` marks error-data registers as no-increment readable. `smpro_core_probe()` initializes the regmap, reads `MANUFACTURER_ID_REG`, checks `AMPERE_MANUFACTURER_ID`, and registers `smpro_devs`.

## Control Flow
Probe requires OF match data containing a regmap config. It creates the regmap with the device as bus context, reads the ID, rejects non-Ampere devices with `-ENODEV`, and uses `devm_mfd_add_devices()` for three fixed child cells.

## State and Persistence
No global state exists. Runtime state is the devm regmap and child devices. Error monitor data is read directly from hardware through no-increment registers.

## Dependencies and Integration Points
The file depends on I2C, regmap custom bus hooks, OF matching for `ampere,smpro`, and child drivers `smpro-hwmon`, `smpro-errmon`, and `smpro-misc`.

## Risks and Edge Cases
Partial I2C transfers return `-EIO`. Read transactions depend on the device protocol accepting a two-byte command `{reg, val_size}`. Manufacturer-ID mismatch prevents all children. No remove path is needed because devm handles children.

## Test Signals
Validate big-endian 16-bit reads, no-increment error data reads, manufacturer-ID rejection, child-device creation, and I2C short-transfer handling.
