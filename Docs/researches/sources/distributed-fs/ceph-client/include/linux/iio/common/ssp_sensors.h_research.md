# `sources/distributed-fs/ceph-client/include/linux/iio/common/ssp_sensors.h`

Purpose: Samsung Sensor Platform common IIO definitions for sensor type IDs, sample sizes, per-sensor data callbacks, and enable/delay control.

Important APIs/types/functions: sample-size constants, `enum ssp_sensor_type`, `struct ssp_sensor_data`, `ssp_register_consumer`, `ssp_enable_sensor`, `ssp_disable_sensor`, `ssp_get_sensor_delay`, and `ssp_change_delay`.

Control flow and state: sensor consumer state stores a process-data callback, sensor type, and buffer pointer. Runtime SSP state lives in `struct ssp_data` outside the header; functions enable/disable sensors and configure polling/report delay.

Dependencies/integration: depends on IIO core and SSP hub driver internals.

Risks: fixed sample sizes must match firmware protocol; callback timestamp context must be safe; delay changes must synchronize with enabled sensors; enum values are protocol identifiers.

Test signals: register each sensor consumer type, enable/disable, delay read/change, sample buffer length validation, and callback data parsing for accelerometer/gyro/HRM variants.
