# sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/bus.c

## Purpose
Implements the Linux bus type for Arm FF-A partitions. It provides FF-A device/driver matching, sysfs attributes, modalias generation, driver registration helpers, device registration helpers, and bus lifecycle.

## APIs, Types, And Functions
Exports `ffa_bus_type`, `ffa_driver_register()`, `ffa_driver_unregister()`, `ffa_devices_unregister()`, `ffa_device_is_valid()`, `ffa_device_register()`, and `ffa_device_unregister()`. Devices expose read-only `partition_id`, `uuid`, and `modalias` attributes. Device IDs are allocated from a global `DEFINE_IDA(ffa_bus_id)`.

## Control Flow
`arm_ffa_bus_init()` registers the `arm_ffa` bus at `subsys_initcall`. Driver registration requires a probe callback, assigns bus/name/owner metadata, and calls `driver_register()`. Device registration allocates an ID, allocates `struct ffa_device`, populates VM ID/properties/ops/UUID, and calls `device_register()`. Removal unregisters devices, frees IDs in the release callback, then unregisters the bus at module exit.

## State, Persistence, And Dependencies
Runtime state is the bus registry, registered `struct ffa_device` instances, and IDA allocation state. There is no persistence beyond sysfs/kobject state. Dependencies include the driver core, module infrastructure, UUID helpers, and `linux/arm_ffa.h` types.

## Integration Points
`driver.c` registers discovered FF-A partitions via `ffa_device_register()`. FF-A client drivers bind through `ffa_driver_register()` and module autoloading via `arm_ffa:%04x:%pUb` modaliases. For FF-A v1.0, devices with null UUIDs match temporarily and the driver path later resolves UUIDs through the bus notifier in `driver.c`.

## Risks And Test Signals
Risks include null UUID matching binding too broadly, IDA leaks on registration failure, and invalid device validation if bus iteration sees transient devices. Signals are sysfs attribute checks, modalias/module autoload tests, driver bind/unbind, and FF-A partition enumeration on real or emulated firmware.
