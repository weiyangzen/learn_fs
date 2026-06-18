<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_core.c

## Purpose
`st_pressure_core.c` is the shared IIO core for multiple STMicroelectronics pressure sensors. It defines per-chip channel layouts, register settings, full-scale/ODR tables, data-ready interrupt metadata, raw/scale/offset/sample-frequency ABI, trigger ops, settings lookup, and the common probe sequence.

## Important APIs, types, and functions
Channel arrays describe pressure/temp scan layout for generic 24-bit pressure devices, LPS001WP, and LPS22HB-style parts. `st_press_sensors_settings[]` contains WAI IDs, supported names, output data rate registers, power bits, full-scale gains, block-data-update bits, data-ready IRQ registers, SPI mode bits, multiread behavior, and boot times. `st_press_get_settings()` maps a device name to settings. `st_press_read_raw()` delegates raw reads to `st_sensors_read_info_raw()` and returns pressure/temperature scale, offset, and ODR. `st_press_write_raw()` sets ODR. `st_press_common_probe()` verifies ID, initializes common ST sensor state, sets channels/fullscale/ODR, allocates ring/trigger, and registers IIO.

## Control flow
Bus wrappers configure transport-specific `st_sensor_data` and call `st_press_common_probe()`. The common probe verifies WAI, assigns channel tables, selects the first full-scale entry and first ODR, applies default DRDY platform data when appropriate, initializes the sensor through the common ST layer, installs buffered support, optionally allocates a trigger if an IRQ exists, and registers. Runtime sysfs reads either fetch raw data from the hardware or return computed ABI constants from current full-scale and ODR state.

## State and persistence behavior
Mutable state is mostly in `struct st_sensor_data`: current full-scale pointer, selected ODR, IRQ, transport, and common settings. ODR writes persist to hardware registers. Buffer enable and trigger state change sensor power and DRDY IRQs via common helpers. No sampled values are cached in this file.

## Dependencies and integration points
The core imports and exports the `IIO_ST_SENSORS` namespace and depends heavily on the generic ST sensors framework, IIO sysfs, debugfs reg access, triggered buffers, and bus wrappers. Supported devices include LPS331AP, LPS001WP, LPS25H, LPS22HB, LPS33HW, LPS35HW, LPS22HH, and LPS22DF.

## Risks
The settings table is the main risk surface: wrong WAI, ODR mask, BDU bit, multiread bit, or DRDY register silently breaks a whole variant. Temperature offset math is ABI-sensitive. The code casts away constness for channel/settings pointers to match common APIs. New variants must keep name tables, enum values, and settings synchronized.

## Test signals
Build all ST pressure variants, test WAI verification, ODR read/write for each table, raw/scale/offset ABI values, buffer enable/disable, DRDY trigger operation on INT1/INT2-capable parts, SPI multiread behavior, and debugfs register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_core.c -->
