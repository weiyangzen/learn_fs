# sources/distributed-fs/ceph-client/drivers/dma/idxd/bus.c

## Purpose
`bus.c` defines the internal `dsa` bus used by IDXD config devices and subdrivers.

## Important APIs, Types, And Functions
It exports `__idxd_driver_register()`, `idxd_driver_unregister()`, and `dsa_bus_type`. Match logic compares each `idxd_dev` type with a subdriver type array.

## Control Flow
Module init registers the bus. IDXD subdrivers register through `idxd_driver_register()`. Device binding calls the match function, then the subdriver probe callback; removal calls the subdriver remove callback.

## State And Persistence Behavior
Runtime state is the registered bus and registered drivers. Each device carries an embedded `idxd_dev` with a type.

## Dependencies And Integration Points
It depends on the Linux driver core and `idxd.h` helpers. `init.c`, `device.c`, `dma.c`, `cdev.c`, and `compat.c` all create or bind bus objects.

## Risks And Test Signals
Type arrays must be terminated by `IDXD_DEV_NONE`. Test `/sys/bus/dsa`, driver binding to IDXD/WQ devices, and clean bus unregister.
