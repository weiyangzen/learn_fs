# sources/distributed-fs/ceph-client/drivers/iio/accel/dmard09.c

Purpose: minimal I2C IIO driver for the Domintech DMARD09 3-axis accelerometer. It validates the chip ID and exposes direct raw axis reads through a required block-read sequence.

Important APIs and flow: probe allocates state, reads `DMARD09_REG_CHIPID`, rejects non-`0x95` devices, sets direct-mode IIO channels, and registers the device. `dmard09_read_raw()` reads an 8-byte block starting at `DMARD09_REG_STAT` because individual axis registers are cached/stale, extracts little-endian axis data at per-channel offsets, drops lower three bits by shifting, sign-extends, and returns integer raw values.

State, dependencies, risks, and tests: state is just the I2C client pointer. Dependencies are I2C block read support, unaligned little-endian helpers, and IIO direct mode. The channel spec advertises scale but `read_raw` only implements raw, so scale reads return `-EINVAL`; that is a visible behavioral gap. Other risks are missing PM handling, reliance on block read from status, and no OF/ACPI table. Test signals include chip ID rejection, full block-read raw extraction for all axes, behavior of scale sysfs if exposed, and module autoload from I2C ID.
