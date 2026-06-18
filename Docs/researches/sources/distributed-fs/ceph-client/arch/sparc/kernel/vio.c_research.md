<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/vio.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/vio.c

## Purpose
Implements the SPARC64 VIO bus and machine-description discovery layer for LDOM virtual I/O devices. It registers the `vio` bus, creates `vio_dev` objects from MDESC channel-device nodes, handles hotplug matching, and tracks dynamic add/remove notifications.

## Important APIs, Types, And Functions
Important functions include `vio_match_device`, `vio_hotplug`, `vio_bus_match`, `vio_device_probe`, `vio_device_remove`, `__vio_register_driver`, `vio_unregister_driver`, `vio_vdev_node`, `vio_set_intr`, `vio_create_one`, `vio_add`, `vio_remove`, `vio_add_ds`, and initcall `vio_init`. Global state includes `vio_bus_type`, `root_vdev`, `cdev_node`, and `cdev_cfg_handle`.

## Control Flow
`vio_init` registers the bus, locates and validates the MDESC `channel-devices` root and matching OBP node, creates a root VIO device, then registers MDESC notifiers for virtual-device and domain-service ports. Device creation reads type, compatible data, IDs, cfg handles, channel IDs, and interrupt numbers, sets a Linux device name, attaches sysfs attributes, and registers the device. Driver probe matching compares `type` and OF-style compatible lists, builds virtual IRQs unless suppressed, and calls the driver probe.

## State And Persistence
The bus and devices persist in the Linux device model. Each `vio_dev` stores MD node identity, channel IDs, tx/rx INOs and IRQs, cfg handle, OF node pointer, port/dev IDs, type, compatible strings, and node info for later MD updates. Global `cdev_cfg_handle` is used for interrupt control.

## Dependencies And Integration Points
Depends on Linux driver core, sysfs attributes, MDESC APIs, OF node lookup, Sun4v virtual interrupt hypercalls, and VIO driver structures from `asm/vio.h`. Downstream virtual network, disk, console, and domain-service drivers bind through this bus.

## Risks And Edge Cases
MD node numbers can change, so removal must re-resolve by saved node identity. IRQ allocation has no corresponding deallocation support in remove. Overlong MD strings are rejected. Domain-service ports are filtered to avoid OBP-reserved ports. `vio_init` returns `0` even when no MDESC root exists, so absence of VIO hardware is non-fatal.

## Test Signals
Signals include boot on Sun4v/LDOM systems, sysfs `type`, `modalias`, `devspec`, and `obppath`, module autoload aliases, hot add/remove MDESC events, successful vnet/vdisk driver probe, and `vio_set_intr` hypercall behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/vio.c -->
