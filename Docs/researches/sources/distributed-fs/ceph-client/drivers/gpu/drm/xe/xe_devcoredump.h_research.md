# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_devcoredump.h

## Purpose
This header declares Xe devcoredump hooks and the ASCII85 blob printer, with no-op fallbacks when `CONFIG_DEV_COREDUMP` is disabled.

## Important APIs, Types, and Functions
It exposes `xe_devcoredump`, `xe_devcoredump_init`, and `xe_print_blob_ascii85`. Forward declarations cover DRM printer, Xe device, exec queue, and scheduler job types.

## Control Flow
With devcoredump enabled, callers can initialize the coredump lock/cleanup and trigger snapshots. With it disabled, trigger/init calls compile to no-op success, while ASCII85 printing remains available.

## State and Persistence Behavior
The header owns no state. Enabled builds operate on `xe->devcoredump`; disabled builds never capture or retain dump state.

## Dependencies and Integration Points
It is included by GuC submit/capture/log paths and device probe. The stub design lets callers avoid local `#ifdef CONFIG_DEV_COREDUMP` guards.

## Risks
Disabled builds silently skip coredump capture, so debugging expectations differ by config. Function signatures must remain synchronized with the implementation and call sites.

## Test Signals
Build both devcoredump-enabled and disabled kernels, trigger GuC timeout paths, and verify ASCII85 blob users compile independently of devcoredump support.
