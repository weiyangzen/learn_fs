# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_buffer.h

Purpose: declares FIFO state, sensor bit masks, packet data format, validity helper, and buffer API prototypes for the ICM45600 driver.

Important types and APIs: `INV_ICM45600_SENSOR_GYRO`, `ACCEL`, and `TEMP` are FIFO enable bits. `struct inv_icm45600_fifo` tracks FIFO reference count, enabled bits, period, requested/effective watermarks, byte count, sample counts, and data buffer. `struct inv_icm45600_fifo_sensor_data` stores little-endian x/y/z words. `inv_icm45600_fifo_is_data_valid()` rejects all-axis sentinel data. Prototypes expose packet decoding, IIO setup ops, init, enable, watermark, read, parse, and flush.

Control flow and state: no standalone control flow. It defines the state contract used by the core, buffer implementation, and accel/gyro parsers.

Dependencies and integration: relies on IIO, byteorder helpers, and a forward declaration of `struct inv_icm45600_state`. It is included by the core header and buffer users.

Risks and tests: structure field changes affect shared logic across IRQ and child devices. Endianness is little-endian unlike older ICM42600/MPU FIFO formats. Test signals include compile coverage, FIFO validity checks, buffer alignment/record sizing, and correct sample counts for packets containing only one sensor.
