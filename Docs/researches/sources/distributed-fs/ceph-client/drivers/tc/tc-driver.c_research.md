# sources/distributed-fs/ceph-client/drivers/tc/tc-driver.c

## Purpose
Provides Linux driver-core services for TURBOchannel devices: driver registration/unregistration, device ID matching, and registration of the `tc` bus type.

## Important APIs, Types, and Functions
Exports `tc_register_driver()`, `tc_unregister_driver()`, and `tc_bus_type`. Internal helpers are `tc_match_device()` and `tc_bus_match()`. Matching compares `struct tc_dev` `name` and `vendor` strings with a driver's `struct tc_device_id` table until an all-zero sentinel.

## Control Flow
`tc_driver_init()` registers `tc_bus_type` at `postcore_initcall`. TC drivers call `tc_register_driver()`, which delegates to `driver_register()` on the embedded `device_driver`. When the driver core evaluates a device/driver pair, `tc_bus_match()` converts generic pointers to TC objects and returns true if the ID table has matching name and vendor strings.

## State and Persistence Behavior
The only persistent state is the registered `tc_bus_type` and registered device drivers in the driver core. This file does not own device instances; those are created in `tc.c`.

## Dependencies and Integration Points
Depends on `<linux/tc.h>`, module exports, and the generic driver core. `tc.c` assigns `tdev->dev.bus = &tc_bus_type`, and TC device drivers consume the exported registration helpers.

## Risks and Test Signals
ID matching is exact string matching on fixed firmware strings, so padding/termination from firmware probing must be correct. There are no probe/remove callbacks in `tc_bus_type`; TC driver binding relies on the generic driver callbacks embedded in `tdrv->driver`. Test signals include bus registration before TC devices are registered, module alias matching where available, and successful binding for known vendor/module strings.
