<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/imu/adis.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/imu/adis.h

Purpose: Common library interface for Analog Devices ADIS IMU sensors, wrapping SPI register access, reset/status handling, triggers, buffers, and common channel declarations.

Important APIs/types/functions: `struct adis_timeout`, `adis_data`, `adis_ops`, and `adis` describe variant delays, register map, status masks, burst/FIFO behavior, custom bus ops, SPI buffers, paging, IRQ, and locking. APIs initialize/reset devices, read/write 8/16/32-bit registers, update masked fields, check status, enable IRQs, run single conversions, set up buffer/trigger support, and expose debugfs register access. Channel macros build voltage, supply, aux ADC, temp, accel, gyro, inclination, and rotation channel specs.

Control flow: Driver probe calls `adis_init()`, performs startup/status checks, uses locked public helpers for normal access or `__adis_*` helpers under explicit `state_lock`, then optionally installs managed buffer and trigger support.

State/persistence: `struct adis` owns SPI transfer state, current page, DMA-safe buffers, IRQ flags, burst length, and mutex-protected register state.

Dependencies/integration: Depends on SPI, interrupts, IIO core/types, cleanup guards, optional `CONFIG_IIO_ADIS_LIB_BUFFER`, and debugfs.

Risks: Mixing locked/unlocked helpers incorrectly can corrupt shared SPI message/page state; wrong value width in update macros is compile-time guarded but macro constants can still surprise.

Test signals: Register read/write by width, paged-register access, reset timing, status error masks, IRQ enable, buffered capture, scan mode update, and debugfs register read/write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/imu/adis.h -->
