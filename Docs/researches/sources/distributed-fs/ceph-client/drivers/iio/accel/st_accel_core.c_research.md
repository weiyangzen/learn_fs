# sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_core.c

Purpose: common IIO core for a large family of ST-compatible accelerometers. It provides channel layouts, per-chip register settings, scale and sampling-frequency handling, mount-matrix support, trigger integration, and the common probe used by I2C and SPI wrappers.

Important APIs/types/functions: `st_accel_sensors_settings[]` is the main device database, mapping supported names and WAI ids to channel widths, output registers, ODR tables, power bits, axis-enable registers, full-scale gains, block-data-update bits, data-ready IRQ wiring, SPI mode bits, multiread flags, and boot delays. `st_accel_read_raw()` and `st_accel_write_raw()` implement raw, scale, and sampling-frequency IIO operations through shared ST helpers. `apply_acpi_orientation()` converts ST `_ONT` ACPI orientation packages to an IIO mount matrix. `st_accel_get_settings()` and `st_accel_common_probe()` are exported in the `IIO_ST_SENSORS` namespace.

Control flow: bus wrappers identify a chip by device name, configure bus access, power supplies, and call `st_accel_common_probe()`. The common probe verifies chip id, assigns channels, reads ACPI or generic firmware orientation, initializes default full-scale and ODR from the first table entries, initializes the sensor registers, allocates the ring buffer, optionally allocates a trigger when an IRQ exists, and registers the IIO device.

State and persistence behavior: `struct st_sensor_data` holds the selected settings table, current full-scale entry, current ODR, mount matrix, bus accessors, and IRQ data. Hardware registers retain configured ODR, power, full-scale, BDU, data alignment, axis, and IRQ settings until changed or reset.

Dependencies and integration points: depends on `linux/iio/common/st_sensors.h`, IIO sysfs/debugfs/trigger APIs, ACPI, firmware mount matrices, and the buffer helper in `st_accel_buffer.c`. It is consumed by both `st_accel_i2c.c` and `st_accel_spi.c`.

Risks: most behavior is table-driven, so a wrong mask, gain, WAI id, multiread flag, or IRQ bit affects a whole chip family. Some table comments mark guessed boot times or uncertain gains. `_ONT` translation is ST-specific and intentionally applies an extra matrix transform before generic mount-matrix fallback. The common code assumes three data channels plus timestamp.

Test signals: build all transports, probe every id-table name against expected settings, validate WAI verification including parts with no WAI register, check raw sign/shift for 8/12/16-bit layouts, verify available scale and ODR sysfs values, test ACPI `_ONT` and generic mount matrices, run triggered-buffer paths with data-ready IRQs, and use debugfs register access for bus read/write coverage.
