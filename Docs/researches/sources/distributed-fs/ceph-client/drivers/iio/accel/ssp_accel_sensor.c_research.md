# sources/distributed-fs/ceph-client/drivers/iio/accel/ssp_accel_sensor.c

Purpose: Samsung Sensor Platform accelerometer IIO consumer driver. It exposes the sensorhub accelerometer as a three-axis IIO accelerometer with buffered data and writable sampling frequency.

Important APIs/types/functions: `ssp_accel_read_raw()` reports sampling frequency by reading the sensor delay through `ssp_get_sensor_delay()` and converting time to frequency. `ssp_accel_write_raw()` converts frequency to delay and calls `ssp_change_delay()`. `ssp_process_accel_data()` delegates packet decoding to `ssp_common_process_data()`. `ssp_accel_probe()` allocates and registers the IIO device, kfifo buffer, channel table, scan mask, and SSP consumer registration.

Control flow: the platform driver probes after the SSP sensorhub core creates the platform device. Probe allocates `struct ssp_sensor_data` as IIO private data, sets the process callback and sensor type, configures X/Y/Z plus timestamp channels, installs common buffer postenable/postdisable operations, registers the IIO device, and finally calls `ssp_register_consumer()` so the hub can deliver accelerometer frames.

State and persistence behavior: this file owns no hardware registers. Sampling period state lives in the SSP core and sensorhub firmware. The IIO private state stores only the process callback and sensor type. Buffer lifetime is devm-managed.

Dependencies and integration points: integrates with `linux/iio/common/ssp_sensors.h`, the local `ssp_iio_sensor.h` helpers, kfifo IIO buffers, and the parent SSP device found through `indio_dev->dev.parent->parent`.

Risks: the driver assumes a fixed parent-device hierarchy to find `struct ssp_data`; platform topology changes can break delay reads and writes. Data parsing size is fixed to `SSP_ACCELEROMETER_SIZE`, so hub ABI changes must be synchronized. Sampling-frequency writes log "enable fail" for all negative `ssp_change_delay()` returns, even if the failure is not an enable failure.

Test signals: build with SSP sensor support, instantiate `ssp-accelerometer`, verify three accelerometer channels plus timestamp, read and write `sampling_frequency`, enable/disable the kfifo buffer, and inject SSP frames to confirm `ssp_common_process_data()` pushes expected samples.
