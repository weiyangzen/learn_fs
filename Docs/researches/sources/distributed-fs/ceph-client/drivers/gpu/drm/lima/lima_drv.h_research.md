<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_drv.h

## Purpose
Declares Lima driver-wide module parameters, per-file DRM private state, submit aggregation state, compatible data, and helper accessors.

## Important APIs, types, and functions
Exports extern module parameters, `struct lima_drm_priv`, `struct lima_submit`, `struct lima_compatible`, and `to_lima_drm_priv()`. `struct lima_submit` carries context, pipe id, flags, BO arrays, syncobj handles, and scheduler task pointer.

## Control flow
No executable flow except the inline file-private accessor.

## State and persistence
Per-file state persists while a DRM file is open. `lima_submit` is transient per IOCTL submission and bridges IOCTL parsing to GEM/scheduler code.

## Dependencies and integration points
Includes DRM file, Lima context, and Lima device definitions. Used by GEM, driver, and VM submit paths.

## Risks
The submit structure sits on a trust boundary after user data is copied and before jobs are queued; field semantics must stay aligned with IOCTL ABI and scheduler expectations.

## Test signals
Build coverage and IOCTL submit tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_drv.h -->
