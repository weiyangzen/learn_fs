# sources/distributed-fs/ceph-client/drivers/iio/position/Kconfig

## Purpose
Kconfig menu for linear/angular position IIO drivers.

## Important APIs, Types, And Functions
Defines `IQS624_POS` for Azoteq IQS624/625 angular position sensors and `HID_SENSOR_CUSTOM_INTEL_HINGE` for Intel custom HID hinge sensors.

## Control Flow
`IQS624_POS` depends on `MFD_IQS62X || COMPILE_TEST`. The HID hinge driver depends on `HID_SENSOR_HUB` and selects IIO buffer, triggered buffer, and HID sensor IIO helpers.

## State And Persistence
No runtime state; build-time selection only.

## Dependencies And Integration Points
Connects platform/MFD and HID sensor implementations to the IIO position directory.

## Risks And Test Signals
Build-test both options independently and verify module names from help text match produced objects.
