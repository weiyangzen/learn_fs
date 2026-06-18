# sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_i2c.c

## Purpose
I2C bus driver for STMicroelectronics gyroscopes using the shared ST gyro core.

## Important APIs, Types, And Functions
Defines OF match table, `st_gyro_i2c_probe`, I2C ID table, and `i2c_driver`. Uses `st_sensors_dev_name_probe`, `st_gyro_get_settings`, `st_sensors_i2c_configure`, `st_sensors_power_enable`, and `st_gyro_common_probe`.

## Control Flow
Probe normalizes device name from firmware/I2C, looks up settings, allocates IIO state, stores settings, configures I2C transfer layer, powers the sensor, and calls common probe.

## State And Persistence
Bus-local state is in allocated `st_sensor_data`; hardware power is enabled before common initialization.

## Dependencies And Integration Points
Depends on I2C, ST sensors common I2C helpers, OF compatibles for all supported ST gyro variants, and shared core exports.

## Risks
Name lookup is strict; mismatch between compatible data, client name, and settings table yields `-ENODEV`. No explicit remove function is present, relying on devm/common cleanup.

## Test Signals
Probe all I2C IDs/OF compatibles, verify transport configuration, power-enable failures, settings lookup failures, and common sysfs/buffer behavior over I2C.
