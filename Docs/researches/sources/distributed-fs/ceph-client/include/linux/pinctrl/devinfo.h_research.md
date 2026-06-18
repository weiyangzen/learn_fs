# sources/distributed-fs/ceph-client/include/linux/pinctrl/devinfo.h

## Purpose
Device-core pinctrl metadata container used to associate a device with its pinctrl handle and common pin states.

## Important APIs, Types, and Functions
When pinctrl is enabled, defines `struct dev_pin_info` containing the device pinctrl handle plus default, init, and PM sleep/idle states. Declares `pinctrl_init_done()` and inline `dev_pinctrl()`. Disabled builds provide no-op/NULL stubs.

## Control Flow
Device core initializes pin information, calls `pinctrl_init_done()` when probe-time pinctrl setup is complete, and drivers/core code use `dev_pinctrl()` to access the associated handle.

## State and Persistence
`struct dev_pin_info` persists under `struct device::pins` and tracks selected/found pinctrl states for the device lifetime.

## Dependencies and Integration Points
Depends on device model, pinctrl consumer API, and PM. It is an internal bridge between pinctrl core and generic device structures.

## Risks
Consumers must handle `dev->pins == NULL`. PM-only fields are conditional, so code must respect `CONFIG_PM`.

## Test Signals
Device probe tests with pinctrl states, PM state tests, disabled pinctrl build coverage, and device teardown leak checks.
