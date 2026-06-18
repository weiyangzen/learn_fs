# sources/distributed-fs/ceph-client/drivers/iio/orientation/Makefile

## Purpose
Kbuild rules for IIO orientation drivers.

## Important APIs, Types, And Functions
Maps `CONFIG_HID_SENSOR_INCLINOMETER_3D` to `hid-sensor-incl-3d.o` and `CONFIG_HID_SENSOR_DEVICE_ROTATION` to `hid-sensor-rotation.o`.

## Control Flow
Objects are built only when the corresponding Kconfig symbols are enabled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Pairs with the orientation Kconfig file.

## Risks And Test Signals
Compile with each symbol independently to catch missing dependency selections.
