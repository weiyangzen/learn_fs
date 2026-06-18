# sources/distributed-fs/ceph-client/drivers/power/supply/twl4030_madc_battery.c

## Purpose
`twl4030_madc_battery.c` is a simple Li-Ion battery monitor using TWL4030 MADC/IIO channels. It estimates charge state from platform-provided voltage calibration curves and exposes a battery power-supply device.

## Important APIs, Types, And Functions
`struct twl4030_madc_battery` stores the power supply, platform calibration data, and IIO channels for temperature, charge current, and battery voltage. `madc_read()` wraps `iio_read_channel_processed()`. `twl4030_madc_bat_get_*()` helpers read voltage/current/temp/status. `twl4030_madc_bat_voltscale()` selects charging or discharging calibration and linearly interpolates capacity. `twl4030_madc_bat_get_property()` implements the battery property set.

## Control Flow
Probe allocates state, obtains `temp`, `ichg`, and `vbat` IIO channels, sorts charging/discharging calibration tables descending by voltage, stores platform data, and registers `twl4030_battery`. Property reads synchronously sample IIO channels, derive charging status from positive `ichg`, interpolate capacity, estimate charge and time-to-empty, and return fixed technology/presence.

## State, Persistence, And Dependencies
State is mostly platform calibration data plus IIO channel handles. Probe mutates the platform calibration arrays in-place by sorting them. There is no persisted state and no polling worker. Dependencies are platform data from `linux/power/twl4030_madc_battery.h`, IIO channels, sorting helpers, and power-supply core.

## Integration Points
The platform driver binds as `twl4030_madc_battery`. The descriptor uses `external_power_changed = power_supply_changed`, making external supply notifications trigger a battery change event without internal recalculation storage.

## Risks
Probe assumes non-NULL platform data; dereferencing `pdata` would fail if the platform omits it. Calibration arrays must include a sentinel with negative voltage; malformed arrays can read out of bounds. Charge status treats any `ichg` read error as non-charging because `madc_read() > 0` is false. Time-to-empty uses a fixed 400 mA discharge assumption and may be only a coarse estimate.

## Test Signals
Validate all IIO channel acquisition paths, sorted calibration interpolation at table bounds and between points, error handling for channel read failures, missing/malformed platform data, charging-vs-discharging curves, and unit conversions for voltage/current/temp/charge.
