# `sources/distributed-fs/ceph-client/include/linux/iio/common/st_sensors.h`

Purpose: common STMicroelectronics IIO sensor support for accelerometer, gyroscope, magnetometer, and pressure drivers, including channel macros, register setting descriptors, runtime state, trigger/buffer helpers, power/ODR/fullscale controls, and probe helpers.

Important APIs/types/functions: device-name constants, buffer/channel macros, sampling/scale sysfs attribute macros, ODR/power/axis/fullscale/SIM/BDU/DAS/DRDY descriptors, `struct st_sensor_settings`, `struct st_sensor_data`, optional trigger handler/allocation/validation, sensor init, enable, axis enable, power, debugfs register access, ODR, data-ready IRQ, fullscale, raw read, settings lookup, ID verification, sysfs avail emitters, device-name probe, and common probe functions per sensor class.

Control flow and state: persistent `st_sensor_data` owns trigger, mount matrix, selected settings, current fullscale, regmap, enable state, ODR, data channel count, interrupt pin/open-drain/IRQ mode flags, hardware timestamp, ODR mutex, and aligned buffer data. Common helpers program registers through regmap and coordinate trigger/buffer operation.

Dependencies/integration: depends on I2C/SPI, IRQ, IIO core/trigger, bitops, regulator, regmap, and platform data. Bus-specific headers call into this core after configuring transport.

Risks: per-chip settings tables must match register maps and WAI IDs; ODR/fullscale changes need locking; data-ready IRQ polarity/open-drain and pin selection must match hardware; buffer data alignment and boot-time discarded samples are easy to mishandle.

Test signals: common probe for each sensor class, WAI verification, ODR/fullscale sysfs read/write, trigger allocation/validation, data-ready IRQ enable/disable, buffered capture with timestamp, suspend/power regulator behavior, and I2C/SPI transport parity.
