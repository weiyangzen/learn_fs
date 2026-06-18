<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/surface_aggregator/device.h -->
# sources/distributed-fs/ceph-client/include/linux/surface_aggregator/device.h

## Purpose

`device.h` defines the SSAM bus and client-device interface. It lets non-ACPI/non-platform Surface Aggregator clients appear as Linux driver-model devices with stable SSAM UIDs, match tables, driver callbacks, child-device registration, request helper macros, and notifier wrappers. It is the main bridge between the controller-level command API and individual Surface subsystem drivers.

## Important APIs, types, and functions

Core identifiers are `enum ssam_device_domain`, `enum ssam_virtual_tc`, and `struct ssam_device_uid`. `SSAM_DEVICE()`, `SSAM_VDEV()`, and `SSAM_SDEV()` build match table entries with `SSAM_MATCH_TARGET`, `SSAM_MATCH_INSTANCE`, and `SSAM_MATCH_FUNCTION` derived from wildcard values. `struct ssam_device` embeds `struct device`, controller pointer, UID, and flags. `struct ssam_device_driver` wraps `device_driver`, a match table, `probe`, and `remove`. Helpers cover type conversion, matching, allocation/add/remove, refcounting, driver data, driver registration, firmware-node child registration, client-device request macros (`SSAM_DEFINE_SYNC_REQUEST_CL_*`), and device-scoped notifier register/unregister.

## Control flow

Firmware-described or virtual clients are allocated with a controller and UID, added to the SSAM bus, matched against driver tables, then probed via `ssam_device_driver`. Client request macros reuse controller multi-device request wrappers but fill target and instance IDs from `sdev->uid`. Child registration walks firmware nodes below a parent and instantiates SSAM children. Notifier registration first checks whether the device is hot-removed and then delegates to controller notifier registration.

## State and persistence behavior

Device lifetime follows the embedded `struct device` refcount. The `ctrl` pointer binds all client communication to one controller. The `flags` word stores hot-removal state; once `SSAM_DEVICE_HOT_REMOVED_BIT` is set, drivers should avoid EC traffic because it may time out. Driver data persists in the normal `dev_get_drvdata()` slot.

## Dependencies and integration points

The header depends on the Linux device model, module tables, firmware properties, and `controller.h`. It integrates with `CONFIG_SURFACE_AGGREGATOR_BUS`, module driver registration, firmware-node child enumeration, controller request APIs, and controller notifiers.

## Risks and test signals

Risks include invalid wildcard use in `SSAM_DEVICE()` arguments, stale controller references, assuming `is_ssam_device()` works when the bus is disabled, communication after hot removal, and mismatched target/category/function IDs that silently prevent binding. Tests should cover match-table wildcard behavior, bus-disabled stubs, device add/remove and refcount lifetimes, child enumeration from firmware nodes, client request macro expansion, and notifier behavior before and after `ssam_device_mark_hot_removed()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/surface_aggregator/device.h -->
