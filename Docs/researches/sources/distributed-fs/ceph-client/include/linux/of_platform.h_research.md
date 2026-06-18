<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_platform.h -->
# sources/distributed-fs/ceph-client/include/linux/of_platform.h

## Purpose
This header declares OF platform-device creation, population, depopulation, and auxiliary naming/platform-data overrides.

## Important APIs, types, and functions
`struct of_dev_auxdata` maps compatible plus physical address to an override device name and platform data, with `OF_DEV_AUXDATA()` initializer. Device APIs include `of_device_alloc()`, `of_device_add()`, `of_device_register()`, `of_device_unregister()`, and `of_find_device_by_node()`. Population APIs include `of_platform_bus_probe()`, `of_platform_device_create()`, `of_platform_device_destroy()`, `of_platform_populate()`, `of_platform_default_populate()`, `of_platform_depopulate()`, `devm_of_platform_populate()`, and `devm_of_platform_depopulate()`.

## Control flow
Platform or bus code walks DT children, matches bus nodes, creates platform devices, assigns resources and optional auxdata, and marks nodes populated. Depopulate tears child devices back down. Devm variants tie populate/depopulate to device lifetime. Address support disabled makes population/device creation unavailable with `-ENODEV` or `NULL`.

## State and persistence
Created platform devices persist in the device model. OF node flags such as populated/populated bus are managed by implementation code. Auxdata provides non-DT platform data for legacy consumers.

## Dependencies and integration points
It integrates OF nodes with the platform bus, resource/address parsing, driver core, and legacy board conversion paths. It depends on `CONFIG_OF` and `CONFIG_OF_ADDRESS`.

## Risks and test signals
Risks include duplicate device creation, stale populated flags, auxdata overuse or wrong physical address matching, partial populate rollback leaks, and devm depopulate order bugs. Test recursive DT population, default bus matches, auxdata overrides, probe failure cleanup, depopulation on driver remove, and disabled address builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_platform.h -->
