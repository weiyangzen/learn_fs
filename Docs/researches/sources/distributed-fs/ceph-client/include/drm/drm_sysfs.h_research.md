# sources/distributed-fs/ceph-client/include/drm/drm_sysfs.h

## Purpose
`drm_sysfs.h` declares DRM sysfs registration and event helpers for DRM class devices, connector hotplug, and connector property notifications.

## Important APIs, types, and functions
APIs are `drm_class_device_register`, `drm_class_device_unregister`, `drm_sysfs_hotplug_event`, `drm_sysfs_connector_hotplug_event`, and `drm_sysfs_connector_property_event`. The header forward-declares `drm_device`, `device`, `drm_connector`, and `drm_property`.

## Control flow
DRM devices register class devices with sysfs, unregister them during teardown, and emit uevents when global hotplug, connector hotplug, or connector property changes need to be visible to userspace.

## State and persistence
State lives in the Linux device model and connector objects. The header itself has no storage. Sysfs entries persist only while devices are registered.

## Dependencies and integration points
It integrates DRM device registration with sysfs, udev/hotplug userspace, connector property changes, and the Linux class device model.

## Risks and test signals
Risks include missing unregister calls, emitting uevents after connector removal, property event storms, userspace relying on event ordering, and null/stale connector or property pointers. Test signals include DRM device register/unregister, hotplug uevent observation, connector-specific hotplug, property change uevents, suspend/resume hotplug, and teardown race tests.
