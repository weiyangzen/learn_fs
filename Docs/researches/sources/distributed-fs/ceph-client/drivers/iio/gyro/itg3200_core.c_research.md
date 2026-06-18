# sources/distributed-fs/ceph-client/drivers/iio/gyro/itg3200_core.c

## Purpose
I2C IIO driver core for InvenSense ITG3200 3-axis gyroscope, exposing temperature, XYZ angular velocity, scale, offset, sample frequency, mount matrix, optional buffers, triggers, and sleep PM.

## Important APIs, Types, And Functions
Exports `itg3200_write_reg_8` and `itg3200_read_reg_8` for buffer code. Important functions include `itg3200_read_reg_s16`, `itg3200_read_raw`, `itg3200_write_raw`, reset, full-scale enable, initial setup, mount-matrix extension, probe/remove, suspend, and resume.

## Control Flow
Probe reads mount matrix, sets up IIO metadata, configures buffer and optional trigger, resets and validates device address register, enables full scale, initializes the mutex, and registers the IIO device. Sample-frequency writes read DLPF config, compute divider, and write sample-rate divisor under lock.

## State And Persistence
Hardware state includes reset, IRQ configuration, full-scale DLPF bits, power-management sleep, and sample-rate divisor. Software state includes I2C client, mount matrix, mutex, and optional trigger from the shared header.

## Dependencies And Integration Points
Depends on I2C, `linux/iio/gyro/itg3200.h`, optional IIO buffer object, OF compatible `invensense,itg3200`, and simple PM ops.

## Risks
The source shows a duplicated function declaration line for `itg3200_initial_setup`, which should fail compilation if present verbatim. `itg3200_read_reg_s16` sets the register auto-increment bit after filling the first I2C message buffer, so review byte ordering/address behavior carefully. Power management is marked TODO and only system sleep is implemented.

## Test Signals
Build with and without IIO_BUFFER, probe ID/address check, read temp and axes, read/write sample frequency, enable buffer and data-ready IRQ, suspend/resume, and validate mount matrix sysfs.
