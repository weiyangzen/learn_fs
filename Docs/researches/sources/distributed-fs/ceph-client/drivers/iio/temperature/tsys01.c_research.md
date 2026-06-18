# sources/distributed-fs/ceph-client/drivers/iio/temperature/tsys01.c

Purpose: IIO driver for Measurement Specialties TSYS01 temperature sensor. It reads PROM coefficients, performs conversion, and exposes processed temperature in milli-C.

Important APIs/types/functions: `struct tsys01_dev` stores client pointer, conversion mutex, transport callbacks, and PROM coefficients. Main functions are `tsys01_read_temperature()`, `tsys01_read_raw()`, `tsys01_crc_valid()`, `tsys01_read_prom()`, `tsys01_probe()`, and `tsys01_i2c_probe()`.

Control flow: I2C probe verifies required SMBus/I2C block functionality, allocates the IIO device, binds common Measurement Specialties helper callbacks, resets the chip, reads eight PROM words, validates CRC, and registers one processed temperature channel. Reads lock during conversion, call the common convert-and-read helper with conversion/read commands and delay, shift the ADC result, run the polynomial coefficient algorithm, and return milli-C.

State and persistence: PROM coefficients are cached in `prom[]` for later calculations. There is no writable configuration or PM state. The only persistent data is factory PROM on the sensor.

Dependencies/integration: depends on `../common/ms_sensors/ms_sensors_i2c.h` helpers and imports namespace `IIO_MEAS_SPEC_SENSORS`. Uses IIO direct mode and I2C client matching/OF compatible `meas,tsys01`.

Risks: `tsys01_crc_valid()` sums `n_prom[0]` repeatedly rather than each PROM word, which looks suspicious and can reject or accept devices incorrectly. The polynomial uses large signed intermediate values and depends on exact scaling. Reads block for conversion delay under mutex.

Test signals: hardware probe should log PROM coefficients, CRC failure should reject probe, processed temperature should match datasheet examples, and conversion helper error propagation should be validated.
