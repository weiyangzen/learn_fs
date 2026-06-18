# sources/distributed-fs/ceph-client/drivers/hwmon/ina2xx.c

## Purpose

`ina2xx.c` is the shared hwmon driver for TI INA219/INA220/INA226/INA230/INA231/INA234/INA260 and Silergy SY24655 current and power monitors. It exposes voltage, current, power, optional alerts/limits, optional update interval, optional average power, and writable shunt resistance for external-shunt devices.

## Important APIs, Types, and Functions

`struct ina2xx_config` captures chip defaults, alert support, internal-shunt status, average-power support, update-interval support, calibration, shifts, divisors, bus-voltage LSB, power factor, and current shift. `struct ina2xx_data` stores config, chip id, shunt resistance, computed current/power LSBs, regmap, and client. `ina2xx_get_value()` converts raw registers. `ina2xx_read_init()` reads values and reinitializes the chip if calibration was lost after reset. Alert helpers program `INA226_MASK_ENABLE` and `INA226_ALERT_LIMIT`. `ina2xx_read()` and `ina2xx_write()` dispatch modern hwmon operations, while `ina2xx_is_visible()` gates features by chip. `ina2xx_init()` configures regulator, shunt scaling, alerts, SY24655 accumulation, and calibration.

## Control Flow

Probe selects config from match data, initializes regmap with cache and volatile register definitions, optionally enables the `vs` regulator, initializes chip registers, then registers hwmon with or without the extra `shunt_resistor` sysfs group depending on internal-shunt status. Measurement reads dispatch by hwmon type. Current input is derived from shunt voltage so it remains meaningful even if the chip current register depends on calibration. Power input uses `ina2xx_read_init()` so a zero reading can trigger calibration-register verification and regcache sync. Alert limit writes disable alert functions first, write the limit, then enable the selected alert mask only for nonzero limits.

## State and Persistence Behavior

The driver maintains computed scaling in memory and writes configuration/calibration into the chip at probe and during reset recovery. Regmap cache stores writable register state and is marked dirty/synced if calibration loss is detected. The `shunt_resistor` sysfs attribute changes software scaling only; it does not rewrite the fixed calibration register. SY24655 average power uses an accumulator register configured to clear after read.

## Dependencies and Integration Points

Dependencies include I2C, regmap with maple cache, optional regulator enable, modern hwmon APIs, firmware properties `shunt-resistor` and `ti,alert-polarity-active-high`, and I2C/OF match data. The driver provides a common ABI over multiple related register layouts.

## Risks and Edge Cases

`ina226_alert_to_reg()` clamps shunt alert values with a formula that should be regression-tested because units differ between shunt voltage and current-derived limits. Reset recovery only triggers when the measured register reads zero; real zero power/current readings cause an extra calibration check. Writes to `shunt_resistor` are protected by the hwmon device lock but alter scaling for all future reads without touching hardware. Alert programming clears all alert functions before setting one, so only one alert function is active at a time. Regulator absence is accepted only for `-ENODEV`; other regulator errors block probe.

## Test Signals

Test all chip variants for visible attributes, shunt scaling and invalid resistor rejection, regulator failure paths, calibration-loss recovery, current derivation from shunt voltage, alert limit enable/disable and alarm reads, update interval conversion for INA226-like chips, SY24655 average-power block read and zero sample count, and internal-shunt INA260 behavior without shunt sysfs.
