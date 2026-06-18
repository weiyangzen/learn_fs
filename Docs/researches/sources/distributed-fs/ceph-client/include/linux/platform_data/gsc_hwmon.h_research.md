
# sources/distributed-fs/ceph-client/include/linux/platform_data/gsc_hwmon.h

## Purpose
This header defines platform data for the Gateworks System Controller hwmon driver. It describes ADC/fan channels, conversion modes, voltage references, and channel names.

## Important APIs And Types
`enum gsc_hwmon_mode` distinguishes temperature, 24-bit voltage, raw voltage, 16-bit voltage, fan, and max modes. `struct gsc_hwmon_channel` contains I2C register offset, mode, name, voltage offset, and two-resistor divider values. `struct gsc_hwmon_platform_data` contains channel count, ADC resolution, voltage reference, fan register base, and a counted flexible array of channels.

## Control Flow, State, And Persistence
The hwmon driver reads the channel array at probe, then periodically reads I2C registers and converts raw values according to mode, reference, resolution, divider, and offset. State is static channel description plus live sensor readings.

## Dependencies And Integration Points
It integrates platform data with hwmon sysfs, I2C register access, and board-specific voltage/fan monitoring topology.

## Risks And Test Signals
Risks include wrong channel count for the flexible array, incorrect voltage divider math, bad ADC resolution/reference, and register overlap. Test signals include hwmon channel enumeration, temperature/voltage/fan conversion checks against known inputs, boundary ADC values, and counted-by build diagnostics.
