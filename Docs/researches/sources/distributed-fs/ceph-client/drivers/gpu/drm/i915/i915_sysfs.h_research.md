<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sysfs.h

## Purpose
Declares i915 sysfs setup/teardown helpers and a device-to-i915 lookup utility.

## Important APIs, types, and functions
- Forward declares `struct device` and `struct drm_i915_private`.
- Exports `kdev_minor_to_i915()`, `i915_setup_sysfs()`, and `i915_teardown_sysfs()`.

## Control flow
No runtime control flow exists in the header. It provides the setup/cleanup contract to driver initialization.

## State and persistence
No state is defined here. The implementation stores sysfs state in `drm_i915_private` and kernel sysfs objects.

## Dependencies and integration points
Included by i915 driver load/remove paths and the sysfs implementation.

## Risks
The lookup helper assumes the device has DRM minor driver data installed. Calling it on unrelated devices would produce invalid results.

## Test signals
Build coverage and probe/remove sysfs setup/teardown tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sysfs.h -->
