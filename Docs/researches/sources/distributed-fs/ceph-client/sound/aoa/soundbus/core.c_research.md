# sources/distributed-fs/ceph-client/sound/aoa/soundbus/core.c

## Purpose

This file implements the generic Apple Soundbus driver-model bus. It registers the `aoa-soundbus` bus type, manages soundbus device references, dispatches probe/remove/shutdown to soundbus drivers, emits OF uevents, and exports add/remove/register APIs.

## Important APIs, types, and functions

Public exports are `soundbus_dev_get`, `soundbus_dev_put`, `soundbus_add_one`, `soundbus_remove_one`, `soundbus_register_driver`, and `soundbus_unregister_driver`. Internal callbacks are `soundbus_probe`, `soundbus_uevent`, `soundbus_device_remove`, and `soundbus_device_shutdown`. `soundbus_bus_type` defines bus operations and sysfs groups.

## Control Flow

Bus init registers the bus at `subsys_initcall`. `soundbus_add_one()` validates required fields, names the OF-backed device, assigns the bus, and registers it. Driver registration fills common driver fields and calls `driver_register`. Probe gets an extra device reference before invoking the driver's probe and drops it on failure. Remove invokes the driver's remove callback and drops the reference. Uevent generation exports OF name, type, compatible strings, compatible count, and modalias.

## State and Persistence

The bus type persists until module exit. A static `devcount` names devices monotonically. Bound soundbus devices hold references through probe/remove lifetime.

## Dependencies and Integration Points

It depends on Linux driver core, OF platform device registration, sysfs groups declared elsewhere, and AOA soundbus structures. Layout fabric registers as a soundbus driver; I2S bus code creates soundbus devices.

## Risks and Test Signals

Risks include reference leaks if probe/remove paths mispair, uevent compatible-string length handling, sanity checks rejecting valid devices, and modalias mismatch preventing module autoload. Tests should cover add/remove, driver probe failure, uevent content for multi-string compatible properties, and shutdown/remove callbacks.
