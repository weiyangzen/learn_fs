# sources/distributed-fs/ceph-client/include/linux/auxiliary_bus.h

## Purpose
Defines the Linux auxiliary bus interface, used when one physical or logical parent device exposes smaller subdevices that should bind to separate auxiliary drivers. The header documents the device lifetime model and declares registration, sysfs IRQ, driver, and device-managed creation helpers.

## Important APIs, Types, And Functions
`struct auxiliary_device` embeds `struct device`, has a match `name`, unique `id`, and sysfs IRQ tracking state containing an xarray, mutex, and directory-exists flag. `struct auxiliary_driver` embeds `struct device_driver` and supplies `probe`, `remove`, `shutdown`, `suspend`, `resume`, a driver `name`, and an `id_table`. Helpers include `auxiliary_get_drvdata()`, `auxiliary_set_drvdata()`, `to_auxiliary_dev()`, `to_auxiliary_drv()`, `auxiliary_device_init/add/delete/uninit`, `auxiliary_driver_register/unregister`, creation/destruction helpers, devm creation, `dev_is_auxiliary()`, sysfs IRQ add/remove, and `module_auxiliary_driver()`.

## Control Flow
Registering a device is a three-step sequence: fill name/id/release/parent, call `auxiliary_device_init()`, then call `auxiliary_device_add()` through the `KBUILD_MODNAME` macro wrapper. Teardown mirrors this with `auxiliary_device_delete()` followed by `auxiliary_device_uninit()`. Drivers register with `auxiliary_driver_register()`, after which the bus matches `id_table` names against device match names and invokes probe/remove through the driver core.

## State And Persistence
Auxiliary device memory is owned by the registering parent driver, not the bus. The embedded `struct device` reference count controls when the release callback frees memory. Sysfs IRQ state persists in the device's xarray/mutex until uninit. Shared objects referenced by auxiliary drivers must outlive or equal the auxiliary device lifetime.

## Dependencies And Integration Points
The header depends on `linux/device.h` and `linux/mod_devicetable.h`, plus xarray, mutex, module, and driver-core types pulled through those headers. It integrates with module autoloading through auxiliary device IDs, sysfs for IRQ metadata when `CONFIG_SYSFS` is enabled, driver power management, shutdown, and devm cleanup on parent devices.

## Risks
Lifetime mistakes are the dominant risk. The registering driver must unregister auxiliary devices before its own remove path completes and must keep shared objects valid while devices remain registered. Missing release callbacks cause device-core registration failure or leaks. Duplicate match-name/id combinations cause `device_add()` failure. Operations must tolerate being called after unregister and return errors rather than dereferencing freed parent state.

## Test Signals
Signals include probe/remove bind tests, parent-driver remove tests with devm cleanup, duplicate-id failure tests, module autoload checks from `MODULE_DEVICE_TABLE(auxiliary, ...)`, suspend/resume/shutdown smoke tests, and sysfs IRQ add/remove checks under `CONFIG_SYSFS` and no-op checks without it.
