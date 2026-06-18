# sources/distributed-fs/ceph-client/drivers/base/attribute_container.c

## Purpose
Implements the legacy attribute-container mechanism that lets class-like containers attach generated class devices and sysfs attributes to arbitrary devices selected by a match callback. It is used by transport/class infrastructure to avoid embedding class-device storage in every device.

## Important APIs, Types, And Functions
- Private `struct internal_container` binds a klist node, `struct attribute_container`, and generated class device.
- Registration: `attribute_container_register()` and `attribute_container_unregister()`.
- Device lifecycle: `attribute_container_add_device()`, `attribute_container_remove_device()`, `attribute_container_add_class_device()`, and `attribute_container_class_device_del()`.
- Triggering: `attribute_container_device_trigger()` and safe all-or-undo variant `attribute_container_device_trigger_safe()`.
- Sysfs helpers: `attribute_container_add_attrs()` and `attribute_container_remove_attrs()`.

## Control Flow
Registered containers sit on a global list under a mutex. Adding a device iterates matching containers, allocates/internalizes a class device, sets parent/class/name/release, invokes an optional callback or directly adds the class device, then links it into the container klist. Removal finds matching generated devices, removes them from the klist, and either calls caller removal logic or removes attrs and unregisters.

## State And Persistence
Global state is the container list and mutex. Each container owns a klist of generated class devices, and each generated device holds a parent reference released by `attribute_container_release()`. Attribute groups or arrays are stored in the external `struct attribute_container`.

## Dependencies And Integration Points
Depends on the driver core device model, classes, klist, sysfs, and private `base.h`. Exported symbols are consumed by transport-class style code.

## Risks And Edge Cases
The klist iterator macro has FIXME comments about break/exit discipline, and some loops manually call `klist_iter_exit()`. Container unregister refuses while class devices remain. Safe trigger undo must correctly reverse only prior successes. `cont->class->dev_release` is assigned during add and affects class behavior globally.

## Test Signals
Multiple matching containers per device, no-classdev containers, add/remove with custom callbacks, safe trigger failure and undo ordering, unregister while busy, attr-array versus attr-group creation/removal, and parent reference release on final put.
