# sources/distributed-fs/ceph-client/drivers/iio/chemical/scd4x.c

Purpose: full I2C IIO driver for Sensirion SCD40/SCD41 CO2 sensors. It handles command transport, CRC8 framing, measurement polling, pressure and temperature compensation, automatic and forced calibration sysfs attributes, triggered-buffer capture, regulator power management, and PM stop/start.

Important APIs, types, and functions: `struct scd4x_state` holds the I2C client, mutex, and regulator. `scd4x_i2c_xfer()`, `scd4x_send_command()`, `scd4x_read()`, `scd4x_write()`, and `scd4x_write_and_fetch()` implement command sequencing and CRC. `scd4x_read_poll()` waits for `CMD_GET_DATA_READY` then reads three 16-bit measurements. `scd4x_read_raw()` exposes CO2 raw plus scale, temperature raw/scale/offset/calibbias, humidity raw/scale, and pressure compensation output. `scd4x_write_raw()` writes temperature offset or ambient pressure. Sysfs attributes expose automatic self calibration and forced recalibration. `scd4x_probe()` powers the device, stops any running measurement, sets up triggered buffering, starts measurement, registers cleanup, and registers the IIO device.

Control flow: many commands require measurement to be stopped, a 500 ms execution delay, and measurement restarted afterward. Measurement reads and data-ready queries are exceptions; ambient pressure can be written/read without stopping. Direct reads claim direct mode before polling. Buffer trigger handler reads a full measurement under the mutex and pushes CO2/temp/humidity plus timestamp.

State and persistence: only mutex, client, and regulator are cached. Calibration, pressure, and temperature offset live in the sensor after writes. The driver does not cache measurement interval; polling uses fixed one-second sleeps with six tries.

Dependencies and integration: depends on I2C, IIO buffers/triggers, CRC8 polynomial 0x31, regulator framework, and OF compatibles `sensirion,scd40` and `sensirion,scd41`.

Risks and test signals: stop/start sequencing around calibration is timing-sensitive and can leave the device stopped on error, though forced calibration tries to restart on failure. The `cmd` parameter to `scd4x_write_and_fetch()` is unused and currently hardwired to FRC. Tests should cover CRC mismatch, data-ready timeout restart, pressure range 700-1200 mbar, FRC failure value, buffer/direct-mode exclusion, regulator cleanup, and suspend/resume measurement restart.
