# sources/distributed-fs/ceph-client/drivers/base/isa.c

## Purpose
`isa.c` implements a simple ISA bus wrapper for legacy ISA drivers that create a fixed number of logical devices and bind them to a driver-specific callback table.

## Important APIs, Types, And Functions
It defines root `isa_bus`, `struct isa_dev`, `isa_bus_type`, and callbacks for match, probe, remove, shutdown, suspend, and resume. Public APIs are `isa_register_driver()` and `isa_unregister_driver()`. Init function `isa_bus_init()` registers the bus and root device at `postcore_initcall`.

## Control Flow, State, And Persistence
Driver registration assigns the ISA bus to the embedded driver, registers it, then allocates `ndev` `isa_dev` objects named `<driver>.<id>`. Each device stores the `isa_driver` in `platform_data`, has the ISA root as parent, 24-bit DMA mask, and a release callback. Matching succeeds only for devices whose `platform_data` points to the probing `isa_driver`, optionally filtered by `isa_driver->match`; a failed optional match clears `platform_data`.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include driver core bus registration, DMA masks, legacy `struct isa_driver`, and platform_data. Risks include partial registration unwind, linked-list lifetime during unregister, clearing platform_data after failed match, no devices returning `-ENODEV`, and legacy PM callbacks. Test signals include multi-device registration, match rejection, probe/remove/shutdown callbacks with IDs, 24-bit DMA mask setup, registration failure rollback, and postcore root bus presence.
