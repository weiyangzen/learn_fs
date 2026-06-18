# sources/distributed-fs/ceph-client/net/ieee802154/sysfs.h

## Purpose
`sysfs.h` is the small public header for the IEEE 802.15.4 sysfs class implementation.

## Important APIs, types, and functions
It declares `wpan_phy_sysfs_init()`, `wpan_phy_sysfs_exit()`, and the external `wpan_phy_class` object.

## Control flow
There is no executable control flow in the header. Callers use the declarations to register the class during subsystem initialization and unregister it during teardown.

## State and persistence
The header owns no state. It exposes access to the class object defined in `sysfs.c`.

## Dependencies and integration points
The include guard `__IEEE802154_SYSFS_H` protects repeated inclusion. Integration is with the local IEEE802154 core and any code that needs the driver-core class for WPAN PHY devices.

## Risks and invariants
The main invariant is that the function declarations and the class object stay in sync with `sysfs.c`. Because `wpan_phy_class` is a `const struct class`, consumers should not mutate it.

## Test signals
Compilation is the primary signal. Link failures would reveal declaration/definition drift; init/exit tests for `sysfs.c` indirectly validate this header.
