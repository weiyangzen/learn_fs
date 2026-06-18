# sources/distributed-fs/ceph-client/drivers/mfd/gateworks-gsc.c

## Purpose
`gateworks-gsc.c` is the I2C MFD core for the Gateworks System Controller. It wraps unreliable I2C accesses with retries, exposes firmware sysfs attributes and timed powerdown, installs a regmap IRQ chip, creates a secondary hwmon I2C client, and populates child devices from device tree.

## Important APIs, Types, and Functions
Exported `gsc_write()` and `gsc_read()` are custom regmap bus callbacks with retry loops for `-EAGAIN` and `-EIO`. `gsc_powerdown()` programs a little-endian sleep duration and sleep control bits. `gsc_show()` and `gsc_store()` implement `fw_version`, `fw_crc`, and `powerdown` sysfs attributes. `gsc_irq_chip` maps eight GSC IRQ bits with inverted ACK semantics. `gsc_probe()` initializes all runtime pieces.

## Control Flow
Probe allocates `struct gsc_dev`, initializes a custom regmap over the I2C client, reads firmware version and CRC, creates a dummy I2C hwmon client at `GSC_HWMON`, installs a low-triggered shared oneshot regmap IRQ chip, logs firmware info, creates sysfs attributes, and populates OF child devices. Remove deletes the sysfs group.

## State and Persistence
State includes firmware version/CRC, primary and hwmon I2C clients, and regmap. Powerdown programming writes persistent controller sleep registers that affect board power. IRQ state is in GSC status/enable registers.

## Dependencies and Integration Points
The driver depends on I2C SMBus byte operations, custom regmap bus, regmap-irq, sysfs, OF platform population, and Gateworks GSC register definitions. Child drivers use the parent regmap and child OF nodes.

## Risks and Edge Cases
`gsc_write()` and `gsc_read()` always return 0 even if the final retry still failed; `gsc_read()` also masks a negative error into an 8-bit value. This can hide I2C failures and corrupt firmware/version or control writes. Sysfs `powerdown` ignores `gsc_powerdown()` errors. The hwmon dummy client is mandatory for probe success.

## Test Signals
Exercise retry behavior under injected `-EAGAIN`/`-EIO`, verify final errors are observable or note current masking, read firmware sysfs values, trigger powerdown register sequence, deliver each regmap IRQ, validate hwmon dummy client creation, and check sysfs cleanup on remove.
