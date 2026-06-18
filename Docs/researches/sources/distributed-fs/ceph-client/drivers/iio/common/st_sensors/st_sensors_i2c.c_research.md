
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_i2c.c

## Purpose
`st_sensors_i2c.c` provides the common I2C bus setup helper for ST IIO sensor drivers. It initializes an 8-bit register/8-bit value regmap and records I2C device identity/IRQ into the IIO device state.

## Important APIs, types, and functions
- `st_sensors_i2c_regmap_config` is the default 8-bit regmap.
- `st_sensors_i2c_regmap_multiread_bit_config` adds `read_flag_mask = 0x80` for sensors that require a multi-read bit.
- `st_sensors_i2c_configure()` creates the regmap, stores client data, sets `indio_dev->name`, and copies `client->irq` to `sdata->irq`.
- The configure helper is exported in namespace `IIO_ST_SENSORS`.

## Control flow
Sensor-specific I2C probe code allocates/configures its `iio_dev` and `st_sensor_data`, then calls `st_sensors_i2c_configure()`. The helper chooses the regmap configuration based on `sensor_settings->multi_read_bit`, initializes regmap, and binds the IIO device to the I2C client.

## State and persistence behavior
Runtime state stored here is `sdata->regmap`, `sdata->irq`, `indio_dev->name`, and I2C client driver data. No hardware registers are modified directly by this file.

## Dependencies and integration points
It depends on I2C core, regmap I2C, IIO core, and public `linux/iio/common/st_sensors_i2c.h`. Downstream core helpers use the regmap configured here.

## Risks and edge cases
The helper assumes `sdata->sensor_settings` is populated before call. Incorrect `multi_read_bit` metadata causes multi-byte reads to use the wrong register address protocol.

## Test signals
Probe an ST sensor over I2C with and without `multi_read_bit`, verify regmap reads use the expected read flag, client data points to the IIO device, and IRQ is propagated for trigger allocation.
