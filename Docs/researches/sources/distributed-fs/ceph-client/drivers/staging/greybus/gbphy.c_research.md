# sources/distributed-fs/ceph-client/drivers/staging/greybus/gbphy.c

## Purpose
Implements the Greybus Bridged-PHY bus. It converts a bridged-PHY Greybus bundle into one Linux child `gbphy_device` per CPort and lets protocol-specific `gbphy_driver` instances bind by CPort protocol ID.

## Important APIs, Types, And Functions
`struct gbphy_host` stores the parent bundle and child-device list. The global `gbphy_bus_type` provides match, probe, remove, and uevent callbacks. Exported APIs are `gb_gbphy_register_driver()` and `gb_gbphy_deregister_driver()`. Child creation and teardown are handled by `gb_gbphy_create_dev()`, `gb_gbphy_probe()`, and `gb_gbphy_disconnect()`.

## Control Flow
Module init registers the `gbphy` bus, then the Greybus bridged-PHY bundle driver. Bundle probe allocates a host object, saves it as bundle driver data, creates/registers a `gbphy_device` for each CPort, and drops runtime PM. Bus matching compares the CPort protocol ID against the driver's ID table. Bus probe resumes the parent bundle, enables runtime PM/autosuspend on the child, calls the child driver's probe, and unwinds PM if probe fails. Disconnect resumes the bundle, unregisters all child devices, and frees the host.

## State And Persistence
State is only in kernel device objects and the IDA-allocated gbphy IDs. Each child has a sysfs `protocol_id` attribute and uevent metadata describing bus, module, interface, bundle, and protocol.

## Dependencies And Integration Points
Integrates Greybus bundle discovery with Linux driver core bus/device mechanics and runtime PM. Child drivers in this subset include GPIO, I2C, and PWM. It depends on `gbphy.h` for public structs/macros.

## Risks
Parent/child runtime-PM balance is subtle: child drivers that support PM are expected to put their initial reference before returning from probe. Device registration failures must use `put_device()` so release frees the ID and object. Uevent field changes can affect module autoloading/userspace matching.

## Test Signals
Probe with zero and multiple CPorts, child registration failure mid-loop, driver match/no-match, child probe failure, disconnect while children are bound, sysfs protocol ID, uevent contents, and runtime-PM autosuspend behavior.
