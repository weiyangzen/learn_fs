# sources/distributed-fs/ceph-client/drivers/thermal/thermal-generic-adc.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/thermal-generic-adc.c` is a generic thermal sensor driver that reads an IIO ADC channel and exposes the value as a thermal zone, optionally converting ADC readings through a Device Tree lookup table. It also registers an IIO temperature channel that reads back the thermal value. The source was read as a complete 230-line file.

## Important APIs, Types, and Functions

The core state type is `struct gadc_thermal_info`. Important functions are `gadc_thermal_probe()`, `gadc_thermal_get_temp()`, `gadc_thermal_adc_to_temp()`, `gadc_thermal_read_linear_lookup_table()`, `gadc_iio_register()`, and `gadc_thermal_read_raw()`. The thermal ops provide `.get_temp`; the IIO info provides `.read_raw`.

## Control Flow

Probe requires a DT node, obtains IIO channel `sensor-channel`, reads optional `temperature-lookup-table`, registers thermal zone index 0 through `devm_thermal_of_zone_register()`, adds hwmon sysfs, then registers a direct-mode IIO device exposing processed temperature. Runtime temperature reads call `iio_read_channel_processed()`, then either return the raw processed value as milliCelsius or interpolate between lookup-table pairs. The IIO read path calls back into the thermal get-temp path.

## State and Persistence Behavior

State is devm-managed and device-lifetime scoped. The lookup table is copied from DT into memory. No persistent state is written.

## Dependencies and Integration Points

The driver depends on IIO consumer/provider APIs, Device Tree property parsing, thermal zone registration, hwmon thermal sysfs, and platform-driver matching on `generic-adc-thermal`. It assumes lookup-table entries are alternating temperature and ADC values.

## Risks and Edge Cases

Lookup-table ordering matters: the conversion loop assumes ADC values are ordered so `val >= adc` finds the correct bracket. Without a lookup table, non-temperature IIO channels trigger only a notice and raw processed readings are treated as milliCelsius. Odd-length tables fail probe. Interpolation divides by `adc_lo - adc_hi`, so duplicate ADC values would be dangerous if not prevented by data quality.

## Test Signals

Test with no table and IIO_TEMP channels, no table and non-temperature ADC channels, valid descending/ascending table examples matching driver expectation, odd-length table rejection, boundary clamping to first/last temperature, thermal sysfs reads, and IIO processed reads.
