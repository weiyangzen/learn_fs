<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_drv.c

## Purpose
Implements the Lima DRM render driver: module parameters, IOCTL dispatch, per-file open/close state, platform probe/remove, runtime PM registration, error-state sysfs dump access, and DRM driver registration.

## Important APIs, types, and functions
IOCTL handlers include `lima_ioctl_get_param()`, `lima_ioctl_gem_create()`, `lima_ioctl_gem_info()`, `lima_ioctl_gem_submit()`, `lima_ioctl_gem_wait()`, `lima_ioctl_ctx_create()`, and `lima_ioctl_ctx_free()`. File callbacks are `lima_drm_driver_open()` and `lima_drm_driver_postclose()`. Error dump helpers are `lima_error_state_read()` and `lima_error_state_write()`. Platform lifecycle is `lima_pdev_probe()` and `lima_pdev_remove()`.

## Control flow
Probe initializes scheduler slabs, allocates `struct lima_device`, reads compatible data, allocates a DRM device, initializes hardware, initializes devfreq, enables runtime PM/autosuspend, registers DRM, and creates a binary sysfs error file. Open creates a per-file VM and context manager. Submit validates pipe, flags, frame size, BO list, user frame copy, task frame validation, context handle, and delegates scheduling to GEM. Remove unregisters sysfs/DRM, disables runtime PM, tears down devfreq/device, drops DRM, and finalizes scheduler slabs.

## State and persistence
Module parameters persist globally: scheduler timeout, heap initial pages, max saved error tasks, and hang limit. Per-file state is `struct lima_drm_priv` with VM and context manager. Device state is in `struct lima_device`. Error-state data persists in `ldev->dump` and `error_task_list` until read or cleared by writing sysfs.

## Dependencies and integration points
Depends on DRM IOCTL/render node infrastructure, sync objects, GEM shmem, Lima GEM/VM/context/device code, platform OF compatible strings `arm,mali-400` and `arm,mali-450`, runtime PM, and sysfs bin attributes.

## Risks
User-copy size validation is safety critical for BO arrays and task frames. IOCTL ABI checks must reject padding/invalid flags. Probe failure unwinding must free scheduler slabs exactly once. Error dump read concatenates variable-size task blobs and requires mutex protection. Runtime PM state must be active before DRM exposes render nodes.

## Test signals
Use render-node IOCTL tests for get-param, GEM create/info/wait, context create/free, valid and invalid submits, explicit fence syncobjs, file close cleanup, sysfs error read/write, probe deferral/failure injection, and runtime autosuspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_drv.c -->
