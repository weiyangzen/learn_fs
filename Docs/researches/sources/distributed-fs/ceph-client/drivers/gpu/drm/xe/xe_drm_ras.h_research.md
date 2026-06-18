<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras.h

## Purpose
`xe_drm_ras.h` is the public Xe RAS declaration header. It provides the severity iteration macro and the initialization entry point.

## Important APIs, types, and functions
The header forward-declares `struct xe_device`, defines `for_each_error_severity(i)` as a loop over `DRM_XE_RAS_ERR_SEV_MAX`, and declares `int xe_drm_ras_init(struct xe_device *xe);`.

## Control flow and integration points
There is no executable control flow. Device probe code includes this header to register DRM RAS nodes; implementation code uses the macro to initialize and unregister severity nodes consistently.

## State and persistence behavior
The header owns no state. Initialization populates `xe->ras` as defined in `xe_drm_ras_types.h`.

## Dependencies, risks, and test signals
It relies on DRM Xe UAPI severity constants being visible through included implementation contexts. Risks are macro drift if severity enumeration changes. Test signals are build coverage and successful RAS init/unregister paths for every defined severity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras.h -->
