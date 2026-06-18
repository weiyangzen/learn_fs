# sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_driver.c

## Purpose

`mdev_driver.c` defines the mdev bus type and exported driver registration helpers.

## Important APIs, Types, and Functions

`mdev_bus_type` has name `mdev`, probe/remove callbacks, and a `match` callback that always returns 0. `mdev_register_driver()` validates `device_api`, assigns the bus, and registers the driver. `mdev_unregister_driver()` unregisters it. Probe/remove dispatch to optional `mdev_driver` callbacks.

## Control Flow

Mdev devices are not auto-bound by matching. Instead, `mdev_device_create()` explicitly calls `device_driver_attach()` with the parent-selected driver. During attach, `mdev_probe()` invokes the driver probe callback. During device removal or driver unregistration, `mdev_remove()` invokes the optional remove callback.

## State and Persistence Behavior

The file defines bus/driver registration state only. Per-device lifecycle state is in `mdev_core.c`.

## Dependencies and Integration Points

It integrates Linux driver core bus registration with mdev parent/device APIs. `mdev_bus_type` is exported via private header for core device initialization.

## Risks and Edge Cases

The no-auto-match design is intentional; changing it could bind mdev devices to unintended drivers. `device_api` is required because userspace and VFIO need to know what kind of device API the mdev implements.

## Test Signals

Register a driver without `device_api` and expect `-EINVAL`; create an mdev and verify explicit attach calls probe; remove and unregister drivers to verify remove callback ordering.
