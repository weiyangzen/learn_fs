## sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_buffer.h

Purpose: FIFO data structures, bit definitions, inline validators, and function declarations shared by ICM-426xx buffer, gyro, accel, and core code.

Important APIs, types, and functions: defines FIFO source bits `INV_ICM42600_SENSOR_GYRO`, `ACCEL`, and `TEMP`. `struct inv_icm42600_fifo` stores FIFO reference count, enabled sources, internal period, requested/effective watermarks, sample counters, and 2080-byte DMA-aligned data buffer. `struct inv_icm42600_fifo_sensor_data` is a packed xyz BE16 triplet. Inline helpers convert BE16 data and detect the invalid all-`-32768` sentinel. Declarations include packet decode, buffer setup ops, FIFO init, FIFO enable, watermark update, read, parse, and hwfifo flush.

Control flow: core owns `struct inv_icm42600_fifo` inside shared state; common buffer code mutates it; gyro/accel parsers consume decoded packets using the inline validity helpers.

State and persistence behavior: the FIFO struct persists configuration and the most recent FIFO read buffer/counters across the read/parse sequence. Effective watermarks are stored separately from user-requested watermarks because timestamp correction uses the effective values.

Dependencies and integration points: included by `inv_icm42600.h` and buffer/sensor implementations; exposes `inv_icm42600_buffer_ops` to IIO kfifo setup.

Risks and edge cases: all invalid-sentinel detection requires x, y, and z to equal `-32768`; partial invalid axes are treated as valid. The 2080-byte buffer assumes 2048-byte FIFO plus read cache margin and must match hardware limits and read code.

Test signals: unit-style packet validation, invalid sentinel handling, buffer size assumptions, and compile checks for all common objects using the declarations.
