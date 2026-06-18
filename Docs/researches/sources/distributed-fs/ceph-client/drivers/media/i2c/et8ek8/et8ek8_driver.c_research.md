# sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/et8ek8_driver.c

## Purpose
`et8ek8_driver.c` implements a V4L2 subdevice driver for the Toshiba ET8EK8 5 MP camera sensor. It powers the sensor, imports and selects register-list modes from `meta_reglist`, exposes format/frame-interval controls, reads OTP/private memory, and provides gain, exposure, pixel-rate, and test-pattern controls.

## Important APIs, Types, and Functions
`struct et8ek8_sensor` stores subdev, source pad, active format, reset GPIO, analog regulator, external clock, sensor revision, controls, current register list, OTP buffer, and power-count lock. I2C helpers implement 8/16-bit reads, buffered register-list writes, single writes, and delay entries. Register-list helpers select modes by type, closest format/size, and frame interval. Control helpers program analog/digital gain table values, exposure register `0x1243`, and multiple test-pattern registers. Subdev operations cover streaming, pad enumeration/format, frame intervals, power, registered/open/close, and system sleep PM.

## Control Flow
Probe acquires reset GPIO, `vana`, and legacy sensor clock, initializes the media source pad and V4L2 subdev, then registers as a sensor. The internal `registered()` callback creates the `priv_mem` sysfs file, powers the device, reads revision registers, imports/sorts the mode lists, selects the first mode, writes POWERON registers, temporarily streams to read OTP memory, powers off, and initializes controls. Opening the subdev sets a try format and increments power; closing decrements power. Starting stream writes the current mode list, applies saved control values with `v4l2_ctrl_handler_setup()`, and writes stream-on; stopping writes stream-off.

## State and Persistence
`current_reglist` and `format` are the active mode state. `power_count` reference-counts users under `power_lock`; system suspend powers down only when nonzero and resume restores power. `priv_mem` caches 128 bytes of OTP data read at registration and exposed read-only through sysfs. Control values persist in V4L2 control state while hardware is off and are applied before streaming.

## Dependencies and Integration Points
The driver depends on I2C, regulators, reset GPIO, legacy V4L2 sensor clock helpers, V4L2 controls/subdev/media entity APIs, `et8ek8_reg.h`, and the linked `et8ek8_mode.o` register tables. It matches `toshiba,et8ek8` and I2C ID `et8ek8`.

## Risks and Edge Cases
The power-on path contains a warning that reset polarity is historically misinterpreted and should not be copied. Streaming does not manage power itself; callers must have powered/opened the subdev. TRY frame interval support is explicitly missing. Register-list correctness is critical because mode programming is table-driven. OTP reads poll a status bit up to 1000 times and can delay or fail registration. `remove()` calls both `v4l2_device_unregister_subdev()` and `v4l2_async_unregister_subdev()`, which is a cleanup detail worth regression testing.

## Test Signals
Validate probe/registered initialization, revision reads for known and unknown versions, register-list import sorting, mode selection by closest format and requested frame interval, pixel-rate/exposure range updates per mode, stream-on/off register writes, saved controls applied before streaming, gain and test-pattern register programming, OTP sysfs `priv_mem` length/content, power reference counting through open/close and `s_power`, suspend/resume with active users, and builds with the paired mode object.
