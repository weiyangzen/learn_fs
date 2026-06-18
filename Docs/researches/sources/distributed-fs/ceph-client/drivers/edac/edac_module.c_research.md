# sources/distributed-fs/ceph-client/drivers/edac/edac_module.c

## Purpose
This is the EDAC core module entry point. It creates the common EDAC sysfs bus at `/sys/devices/system/edac`, initializes EDAC memory-controller sysfs, debugfs, and the shared EDAC workqueue, and clears pre-existing PCI parity status during startup.

## Important APIs and Functions
`edac_set_debug_level()` validates the optional debug level module parameter when `CONFIG_EDAC_DEBUG` is enabled. `edac_debug_level` is exported for other EDAC code. `edac_op_state_to_string()` translates EDAC runtime states into stable strings for logs. `edac_get_sysfs_subsys()` exports the `edac` `bus_type` to sysfs helpers. `edac_init()` and `edac_exit()` are the module lifecycle gates.

## Control Flow
Initialization prints the EDAC version, registers the EDAC system bus, clears PCI parity errors, initializes memory-controller sysfs, initializes debugfs, then creates the workqueue. Error unwind is ordered in reverse: debugfs and memory-controller sysfs are removed if workqueue setup fails, and the subsystem bus is unregistered if earlier setup fails. Exit tears down the workqueue, memory-controller sysfs, debugfs, and subsystem bus.

## State and Persistence
Persistent module state is the static `edac_subsys` bus and optional exported `edac_debug_level`. No on-disk persistence exists; state is kernel runtime state exposed through sysfs/debugfs and module parameters.

## Dependencies and Integration
The file depends on `linux/edac.h`, `edac_mc.h`, and `edac_module.h`. It integrates with EDAC memory-controller sysfs, EDAC PCI parity helpers, debugfs helpers, and the EDAC workqueue implementation elsewhere in the core.

## Risks
`edac_init()` clears only PCI devices present at module initialization; the source comment notes hotplugged devices are not initially cleared here. The init order means failures in later subsystems must keep unwind symmetry. Debug level validation rejects values above 4 but only exists under debug builds.

## Test Signals
Boot/module-load tests should observe `/sys/devices/system/edac`, EDAC version logging, successful creation/removal of memory-controller sysfs and debugfs, and no leaked workqueue after module unload. PCI parity boot-clearing behavior is visible through parity counters and PCI status registers.
