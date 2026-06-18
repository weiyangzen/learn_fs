# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_debugfs.h

## Purpose
Declares the debugfs initialization hook for MSM DRM when debugfs is enabled.

## Important APIs, types, and functions
- Include guard `__MSM_DEBUGFS_H__`.
- Conditional declaration `void msm_debugfs_init(struct drm_minor *minor);` under `CONFIG_DEBUG_FS`.

## Control flow
No runtime control flow. It exposes `msm_debugfs_init()` to the DRM driver definition while compiling away the declaration when debugfs is disabled.

## State and persistence
No state is defined.

## Dependencies and integration points
Included by `msm_drv.c` and implemented by `msm_debugfs.c`. The actual fallback for no debugfs is handled by conditional driver fields and other stubs.

## Risks
Signature drift breaks driver initialization builds. The header intentionally stays narrow.

## Test signals
Build MSM DRM with and without `CONFIG_DEBUG_FS`.
