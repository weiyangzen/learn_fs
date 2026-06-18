# sources/distributed-fs/ceph-client/drivers/power/supply/rx51_battery.c

## Purpose
Nokia RX-51/N900 platform battery driver. It exposes a simple battery power supply backed by IIO ADC channels for VBAT voltage, temperature, and BSI-derived design capacity.

## Important APIs, Types, and Functions
`struct rx51_device_info` stores the device, registered battery, descriptor, and three IIO channels. `rx51_battery_read_adc()` wraps `iio_read_channel_average_raw()`. Conversion helpers are `rx51_battery_read_voltage()`, `rx51_battery_read_temperature()`, and `rx51_battery_read_capacity()`. `rx51_battery_get_property()` maps those readings to power_supply properties.

## Control Flow
Probe allocates state, fills `bat_desc`, obtains `temp`, `bsi`, and `vbat` IIO channels, and registers `rx51-battery`. Property reads synchronously sample the required ADC. Temperature uses a direct table for low raw ADC values and binary search over an inverse lookup table for the rest.

## State and Persistence
The driver keeps no dynamic cached battery state and writes no hardware state. All exported values are computed on demand from ADC readings and fixed conversion tables.

## Dependencies and Integration Points
It is a platform driver matched by `nokia,n900-battery`, depends on IIO consumer channels named by firmware, and integrates only with the power_supply class.

## Risks and Test Signals
`POWER_SUPPLY_PROP_PRESENT` treats any nonzero return from voltage conversion as present, so negative ADC errors may be reported as present before final `INT_MAX/INT_MIN` filtering. The BSI capacity formula divides by `1024 - capacity`, so a raw value at or above 1024 is hazardous. Test ADC error propagation, raw temperature boundaries, BSI near 1024, and registration failure paths for missing IIO channels.
