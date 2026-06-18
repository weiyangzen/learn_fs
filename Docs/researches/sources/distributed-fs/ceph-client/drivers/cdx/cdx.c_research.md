# sources/distributed-fs/ceph-client/drivers/cdx/cdx.c

## Purpose
This is the CDX bus core. It registers the `cdx` bus type, matches CDX devices to CDX drivers, exposes sysfs/debugfs management files, maps device resources to user space, integrates DMA/IOMMU/MSI setup, and provides controller-facing APIs for adding buses and devices.

## Important APIs, Types, and Functions
Public bus APIs include `cdx_dev_reset()`, `cdx_set_master()`, `cdx_clear_master()`, `__cdx_driver_register()`, `cdx_driver_unregister()`, `cdx_device_add()`, `cdx_bus_add()`, `cdx_register_controller()`, and `cdx_unregister_controller()`. Important globals are `cdx_bus_type`, `cdx_controller_ida`, `cdx_controller_lock`, and `cdx_debugfs_dir`.

Sysfs attributes include device identity (`vendor`, `device`, `subsystem_*`, `revision`, `class`, `modalias`), `remove`, `reset`, `driver_override`, bus-device `enable`, and bus-level `rescan`. Per-resource binary files `resource<N>` support `mmap()` through `cdx_mmap_resource()`.

## Control Flow
`postcore_initcall(cdx_bus_init)` registers the bus and creates debugfs. Controllers call `cdx_register_controller()`, which allocates an ID, runs the controller `scan()` callback, and marks the controller registered. Scanning code calls `cdx_bus_add()` for each bus and `cdx_device_add()` for each device. `device_add()` then triggers normal driver-core matching through `cdx_bus_match()` and `cdx_probe()`.

Device reset, bus enable/disable, MSI configuration, and bus-master changes are delegated to controller callbacks via `cdx->ops`. Bus rescan removes existing CDX devices, walks OF compatible controller nodes, and invokes each registered controller's scan method.

## State and Persistence Behavior
The bus core persists runtime device objects, controller IDs, device resources, driver override strings, bus enabled state, MSI metadata, and debugfs/sysfs files. Per-device lifetime is tied to `device_initialize()`/`device_add()`/`put_device()` and `cdx_device_release()`. No state is saved across reboot; all topology is rediscovered from controller firmware.

## Dependencies and Integration Points
It depends on Linux driver core, OF platform lookup, IDA, sysfs, debugfs, irq/MSI domain APIs, IOMMU DMA configuration, and public CDX headers. Controllers supply `struct cdx_controller` and operations. CDX device drivers bind through `struct cdx_driver` ID tables and callback methods.

## Risks
Recursive device removal must preserve child-before-parent ordering and avoid freeing `cdx_device` before release. Resource binary attributes are allocated with `GFP_ATOMIC` and must be removed on all error and unregister paths. `driver_override_show()` prints a potentially NULL string with `%s`, which depends on `sysfs_emit()`/format behavior tolerating NULL on the target kernel. `rescan_store()` can return early after `of_find_device_by_node()` failure while holding scoped node iteration but under a mutex; partial rescans are possible. DMA configuration must undo IOMMU default-domain use on failure. `cdx_mmap_resource()` relies on resource size and exclusivity checks to prevent invalid user mappings.

## Test Signals
Test with a mock or real controller exposing multiple buses and devices: bus registration, uevents/modalias matching, driver probe/remove, reset sysfs behavior, driver override binding, resource file creation/mmap bounds checks, debugfs resource listing, rescan after topology change, bus enable/disable, IOMMU stream ID mapping, and MSI setup when enabled.
