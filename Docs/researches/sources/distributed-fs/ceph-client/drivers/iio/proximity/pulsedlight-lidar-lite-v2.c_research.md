<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/pulsedlight-lidar-lite-v2.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/pulsedlight-lidar-lite-v2.c

Purpose: I2C IIO driver for PulsedLight/ Garmin LIDAR-Lite v2/v3 distance sensors. It exposes one `IIO_DISTANCE` channel with raw centimeter counts and scale, supports triggered-buffer capture, and uses runtime PM to power the sensor down between measurements.

Important APIs, types, and functions: `struct lidar_data` holds the client, IIO device, selected transfer function, and I2C-vs-SMBus mode. `lidar_i2c_xfer()` uses a two-message I2C transfer with STOP after address write; `lidar_smbus_xfer()` emulates the device's required STOP behavior byte by byte. `lidar_get_measurement()` resumes runtime PM, starts acquisition, polls status, handles invalid/out-of-range status, reads the big-endian result, and autosuspends. `lidar_read_raw()` and `lidar_trigger_handler()` expose direct and buffered reads.

Control flow: probe selects raw I2C transfer when available or SMBus fallback otherwise, sets up the triggered buffer manually, registers the IIO device, initializes runtime PM as active, enables autosuspend, and idles the device. Removal unregisters IIO/buffer and disables runtime PM. Runtime suspend writes power control `0x0f`; resume writes `0` and waits 15-20 ms for settling.

State and persistence: software state is minimal: bus-transfer mode and runtime PM state. The sensor is explicitly acquired for each sample and may be powered down afterward. No calibration state is cached.

Dependencies and integration points: depends on I2C or SMBus byte operations, IIO direct mode, triggered buffers, and runtime PM. It matches `pulsedlight,lidar-lite-v2`, `grmn,lidar-lite-v3`, and I2C IDs.

Risks and test signals: test raw I2C and SMBus fallback, runtime suspend/resume timing, invalid status handling, status polling timeout, buffer cleanup on probe error, and direct read while buffers are active. Risks include no explicit mutex around measurements, fixed 10-poll acquisition window, and manual non-devm buffer/device registration requiring correct remove/error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/pulsedlight-lidar-lite-v2.c -->
