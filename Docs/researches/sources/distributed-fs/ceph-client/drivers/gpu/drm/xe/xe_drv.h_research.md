<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drv.h

## Purpose
`xe_drv.h` provides the Xe DRM driver identity and version macros used by driver registration and userspace-visible metadata.

## Important APIs, types, and functions
It defines `DRIVER_NAME` as `xe`, `DRIVER_DESC` as `Intel Xe2 Graphics`, and interface version macros `DRIVER_MAJOR`, `DRIVER_MINOR`, and `DRIVER_PATCHLEVEL`, currently 1.1.0. The comment records interface history with 1.1 as original.

## Control flow and integration points
There is no control flow. DRM driver setup includes these macros when registering the driver and reporting version information through DRM APIs.

## State and persistence behavior
No runtime state is owned here. The values are compile-time constants that persist as the driver identity for a built kernel/module.

## Dependencies, risks, and test signals
The only direct dependency is `drm/drm_drv.h`. Risks are user-visible identity/version drift and mismatch between UAPI changes and version history. Test signals include module/driver registration, DRM version queries, modinfo output, and userspace feature-detection sanity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drv.h -->
