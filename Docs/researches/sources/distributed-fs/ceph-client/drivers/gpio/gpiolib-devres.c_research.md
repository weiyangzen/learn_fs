# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-devres.c

## Purpose
`gpiolib-devres.c` provides device-managed GPIO descriptor and GPIO chip APIs. It wraps descriptor acquisition, arrays, optional lookups, firmware-node lookup, explicit put/unhinge operations, and gpiochip registration with devres cleanup actions so resources are released automatically on driver detach or probe failure.

## Important APIs, Types, And Functions
Exported descriptor helpers include `devm_gpiod_get()`, `devm_gpiod_get_optional()`, `devm_gpiod_get_index()`, `devm_fwnode_gpiod_get_index()`, `devm_gpiod_get_index_optional()`, `devm_gpiod_get_array()`, `devm_gpiod_get_array_optional()`, `devm_gpiod_put()`, `devm_gpiod_unhinge()`, and `devm_gpiod_put_array()`. Managed chip registration is `devm_gpiochip_add_data_with_key()`.

Internal cleanup callbacks are `devm_gpiod_release()`, `devm_gpiod_release_array()`, and `devm_gpio_chip_release()`.

## Control Flow
Each get function calls the corresponding unmanaged GPIO acquisition helper. On success it registers a devres action with `devm_add_action_or_reset()`. If action registration fails, the reset behavior immediately releases the acquired GPIO. Optional variants convert not-found descriptors into `NULL`.

`devm_gpiod_get_index()` has special handling for nonexclusive descriptors: if the same descriptor is already managed by the device, it returns the existing descriptor without registering a duplicate cleanup action. `devm_gpiod_unhinge()` removes devres management without releasing the descriptor, tolerating `-ENOENT` for nonexclusive repeated calls.

`devm_gpiochip_add_data_with_key()` registers a gpiochip and installs a devres action that calls `gpiochip_remove()` when the owning device is detached.

## State And Persistence
State is tracked in the device core devres stack, not in this file. Each successful managed acquisition persists until explicit devm put/unhinge or device teardown. The GPIO subsystem descriptor state is modified by the underlying unmanaged calls.

## Dependencies And Integration Points
The file depends on Linux devres, GPIO consumer APIs, GPIO chip registration, and exported symbol infrastructure. It is a primary integration point for drivers that want probe-error-safe GPIO resource management.

## Risks
Incorrect action registration or duplicate nonexclusive handling can produce double-free or leaked descriptors. `devm_gpiod_unhinge()` is explicitly deprecated and exists for ownership handoff edge cases; misuse can make descriptor lifetime difficult to reason about.

## Test Signals
Test probe failure cleanup, driver detach cleanup, optional missing GPIO returns, nonexclusive repeated get/unhinge behavior, firmware-node managed lookup, array get/put cleanup, and managed gpiochip removal when the parent device unbinds.
