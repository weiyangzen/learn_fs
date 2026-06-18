<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pm.h

## Purpose

`xe_pm.h` declares the Xe power-management interface and scope-guard helpers used by callers that need device wake references.

## Important APIs

The header exports system PM, runtime PM, initialization/finalization, D3cold threshold/toggle, reclaim-safety, callback-task, suspend-blocking, and module-init functions. `DEFAULT_VRAM_THRESHOLD` is 300 MiB. Scope helpers are defined with `DEFINE_GUARD`: `xe_pm_runtime`, `xe_pm_runtime_noresume`, conditional `xe_pm_runtime_ioctl`, and `xe_pm_runtime_release_only`.

## Control Flow and State

The declarations represent functions implemented in `xe_pm.c`. The guard macros automatically pair get/put calls across C scopes and are used by IOCTLs, sysfs/debugfs paths, SR-IOV code, and other outer-level call sites.

## Dependencies and Integration Points

It includes Linux cleanup and runtime PM headers. It is a broad driver contract for safe register and memory access while runtime PM can suspend the device.

## Risks and Test Signals

Incorrect use of noresume or release-only guards can leak or drop wakerefs incorrectly. Test signals include sparse/compile coverage for guard use, runtime PM balance checks, and lockdep coverage for callers that might resume under memory-management locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pm.h -->
