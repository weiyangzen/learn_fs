# sources/distributed-fs/ceph-client/drivers/net/phy/mdio_device.c

## Purpose
`mdio_device.c` implements the driver-core object model for MDIO devices other than the bus itself. It creates/registers/removes generic MDIO devices, manages PHY reset GPIO/reset-controller resources, maps devices into `mii_bus->mdio_map`, and registers `mdio_driver` instances on the `mdio_bus_type`.

## Important APIs, Types, And Functions
- `mdio_device_create()` allocates and initializes a `struct mdio_device`, attaches it to a bus, assigns release/remove/free callbacks, sets the address, and initializes the device name.
- `mdio_device_register()` inserts the device into the bus map and calls `device_add()`.
- `mdio_device_remove()` performs `device_del()` and unregisters the address mapping.
- `mdio_device_free()` drops the device reference; `mdio_device_release()` frees the object and fwnode reference at final release.
- `mdiobus_register_device()` and `mdiobus_unregister_device()` own `bus->mdio_map[addr]` and reset-resource setup/teardown.
- `mdio_device_reset()` asserts/deasserts optional reset GPIO and reset controller signals with configured delays.
- `mdio_driver_register()` and `mdio_driver_unregister()` connect `struct mdio_driver` callbacks to driver-core probe/remove/shutdown wrappers.

## Control Flow And State Behavior
Device creation initializes the embedded `struct device` but does not publish it. Registration first rejects occupied addresses. For PHY-flagged devices, it obtains optional `reset` GPIO and exclusive `phy` reset control, reads `reset-assert-us` and `reset-deassert-us`, and asserts reset before mapping the device into the bus. `device_add()` then triggers matching/probe. The MDIO probe wrapper deasserts reset before calling the driver probe and reasserts it on probe failure. Remove calls the driver remove hook and reasserts reset.

Persistent state is the `struct mdio_device` itself: bus pointer, address, reset GPIO/control pointers, reset state, delay values, flags, and driver callbacks. There is no disk persistence; firmware properties and reset providers are the external source of reset behavior.

## Dependencies And Integration Points
The file depends on Linux device core, GPIO descriptors, reset controller APIs, firmware property helpers, `linux/mdio.h`, `linux/phy.h`, and phylib internals. It integrates directly with `mdio_bus_provider.c` via `mdio_bus_type` and `mii_bus->mdio_map`, with PHY creation/registration paths, and with non-PHY MDIO drivers through `mdio_driver_register()`.

## Risks And Edge Cases
- Address registration is not internally locked here; callers rely on bus registration/lifecycle serialization.
- Reset resources are only acquired for devices flagged as PHYs. Non-PHY MDIO devices need their own reset handling if required.
- Probe failure reasserts reset, but drivers must still clean up any resources allocated before returning an error.
- `mdiobus_unregister_device()` returns `-EINVAL` if the map does not point to the same object, protecting against double or wrong-device removal.
- Reset delays use firmware-provided microsecond values; missing or incorrect properties can expose hardware timing issues.

## Test Signals
Test creation/register/remove/free ordering, duplicate address returning `-EBUSY`, reset GPIO/control assertion on registration and removal, deassertion before probe, reassertion on probe failure, property-driven reset delays, driver registration/unregistration, shutdown callback dispatch, and `mdio_map` clearing after remove.
