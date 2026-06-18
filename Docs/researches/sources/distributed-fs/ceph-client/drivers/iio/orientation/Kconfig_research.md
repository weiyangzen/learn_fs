# sources/distributed-fs/ceph-client/drivers/iio/orientation/Kconfig

## Purpose
Kconfig menu for HID orientation/inclinometer IIO drivers.

## Important APIs, Types, And Functions
Defines `HID_SENSOR_INCLINOMETER_3D` and `HID_SENSOR_DEVICE_ROTATION`. Both depend on `HID_SENSOR_HUB` and select common HID sensor IIO support, trigger support, and IIO buffering.

## Control Flow
Selecting either option enables the matching Makefile object. Device rotation exposes quaternion orientation; inclinometer exposes 3D tilt.

## State And Persistence
No runtime state; build-time selection only.

## Dependencies And Integration Points
Connects HID sensor hub drivers to the IIO orientation directory.

## Risks And Test Signals
Build-test each option as module and built-in, ensuring required HID/IIO helper selections are sufficient.
