<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure.h -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure.h

## Purpose
`st_pressure.h` is the shared header for STMicroelectronics pressure sensor core and bus drivers. It defines supported device names, enum IDs, default platform data, and buffer/trigger helper declarations.

## Important APIs, types, and functions
`enum st_press_type` names LPS001WP, LPS25H, LPS331AP, LPS22HB, LPS33HW, LPS35HW, LPS22HH, and LPS22DF variants. Device-name macros are used by I2C/SPI ID tables and settings lookup. `default_press_pdata` selects DRDY INT1 by default. When `CONFIG_IIO_BUFFER` is enabled, `st_press_allocate_ring()` and `st_press_trig_set_state()` are declared; otherwise the ring allocator is an inline no-op and trigger state is NULL.

## Control flow
The header has no runtime flow. Bus drivers include it for names and call declarations; the core uses the buffer declarations conditionally.

## State and persistence behavior
No state is stored in the header. `default_press_pdata` is a constant fallback object used during probe when no platform data exists and the sensor has DRDY support.

## Dependencies and integration points
It depends on `linux/iio/common/st_sensors.h` and is internal to the ST pressure driver family.

## Risks
Device-name macros must stay synchronized with settings tables and bus ID tables. Conditional buffer stubs affect build coverage across `CONFIG_IIO_BUFFER` combinations.

## Test signals
Compile with and without IIO buffer support, verify every device-name macro resolves in core settings and bus match tables, and check DRDY default behavior on IRQ-capable sensors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure.h -->
