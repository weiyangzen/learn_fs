# sources/distributed-fs/ceph-client/drivers/iio/position/Makefile

## Purpose
Kbuild rules for IIO position drivers.

## Important APIs, Types, And Functions
Maps `CONFIG_HID_SENSOR_CUSTOM_INTEL_HINGE` to `hid-sensor-custom-intel-hinge.o` and `CONFIG_IQS624_POS` to `iqs624-pos.o`.

## Control Flow
Kbuild includes each object when the corresponding config symbol is enabled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Pairs with the position Kconfig file.

## Risks And Test Signals
Compile with module and built-in variants for both symbols.
