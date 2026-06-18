# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_debugfs.h

## Purpose
This header declares the Xe debugfs registration hook and provides a stub when debugfs is disabled.

## Important APIs, Types, and Functions
The only public function is `xe_debugfs_register(struct xe_device *xe)`, guarded by `CONFIG_DEBUG_FS`.

## Control Flow
There is no executable flow except the disabled-config inline stub. Device probe can call `xe_debugfs_register` unconditionally.

## State and Persistence Behavior
The header owns no state. The implementation creates debugfs files that mutate runtime state, but when debugfs is disabled no debugfs state exists.

## Dependencies and Integration Points
It forward-declares `struct xe_device` and is consumed from device probe after DRM registration and sysfs/PMU setup.

## Risks
The main risk is configuration skew: callers must not assume debugfs files exist when `CONFIG_DEBUG_FS` is off. Signature drift is caught by build coverage.

## Test Signals
Build with debugfs enabled and disabled, and probe devices in both configurations to ensure no missing-symbol or registration-order regressions.
