# sources/distributed-fs/ceph-client/drivers/iio/common/scmi_sensors/scmi_iio.c

Purpose: bridge driver that exposes suitable ARM SCMI protocol sensors as IIO devices. It currently supports three-axis accelerometers and gyroscopes, with direct raw reads, sample frequency control/availability, buffered updates through SCMI notifications, scale handling, and raw-available ext-info.

Important APIs, types, and functions: `struct scmi_iio_priv` stores SCMI protocol ops/handle, sensor info, IIO device, mutex, buffer, notifier block, and frequency availability array. `scmi_iio_sensor_update_cb()` receives SCMI sensor-update events and pushes timestamped IIO buffers. Buffer ops enable/disable the SCMI sensor. `scmi_iio_set_odr_val()` converts IIO Hz/uHz to SCMI update interval fields; `scmi_iio_get_odr_val()` reverses that. `scmi_iio_read_channel_data()` temporarily enables the sensor and reads timestamped values for direct mode. Channel helpers map SCMI axis names/types to IIO modifiers/types and build data/timestamp channels. `scmi_alloc_iiodev()` allocates one IIO device per supported SCMI sensor and registers a notifier. `scmi_iio_dev_probe()` iterates discovered SCMI sensors and registers supported devices.

Control flow: probe obtains SCMI sensor protocol ops, scans all sensors, skips non-3-axis and unsupported unit types, allocates channels/frequency tables, sets up kfifo buffer, and registers IIO devices. Buffered operation enables the sensor and relies on notifier events; direct raw reads claim direct mode and perform an on-demand read.

State and persistence: per-sensor runtime state includes frequency availability, current SCMI config in firmware, and IIO buffer data. ODR and enable state are written to SCMI firmware.

Dependencies and integration: depends on SCMI protocol sensor ops, IIO kfifo buffers, notifier events, mutex, time/unit helpers, and `module_scmi_driver()`.

Risks and test signals: ODR conversion uses decimal string length to choose multiplier, which needs boundary tests. Direct read enables the sensor but if `reading_get_timestamped()` fails, the sensor disable path is skipped. Tests should cover segmented/list intervals, timestamped and non-timestamped notifications, accel/gyro type filtering, axis-name modifier parsing, scale exponents, raw_available formatting, direct-read failure cleanup, and multi-sensor probe returning at least one success.
