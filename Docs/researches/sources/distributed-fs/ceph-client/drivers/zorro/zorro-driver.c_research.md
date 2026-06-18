<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro-driver.c -->
# sources/distributed-fs/ceph-client/drivers/zorro/zorro-driver.c

## Purpose
`zorro-driver.c` implements Linux driver-core services for the Zorro bus: device/driver matching, probe/remove dispatch, driver registration, uevents, and bus registration.

## Important APIs, types, and functions
Exports are `zorro_register_driver`, `zorro_unregister_driver`, and `zorro_bus_type`. Internal helpers include `zorro_match_device`, `zorro_device_probe`, `zorro_device_remove`, `zorro_bus_match`, and `zorro_uevent`.

## Control flow
`postcore_initcall` registers the bus. Drivers register with a name, id table, and probe/remove callbacks. The bus match function selects exact IDs or `ZORRO_WILDCARD`; probe rechecks the matching ID and calls the driver probe. Uevents publish ID, slot name/address, and modalias.

## State and persistence
State is managed by the driver core. Zorro devices are boot-discovered and remain in memory; driver binding state is runtime-only.

## Dependencies and integration points
It integrates with the generic device model, module autoload modaliases, `struct zorro_driver`, sysfs attribute groups, and `zorro.c` device registration.

## Risks and test signals
Risks include missing id tables, probe return normalization, modalias formatting mismatches, and remove callbacks assuming resources still exist. Test signals include wildcard and exact matches, module autoload, bind/unbind, and device/driver sysfs state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro-driver.c -->
