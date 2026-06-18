# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/Kconfig

## Purpose
Defines kernel configuration options for the etnaviv DRM driver for Vivante GPU IP cores and optional thermal throttling support.

## Important APIs, Types, and Functions
The primary symbol is `DRM_ETNAVIV`, a tristate depending on `DRM` and `MMU`. It selects `SHMEM`, `SYNC_FILE`, `TMPFS`, `WANT_DEV_COREDUMP`, `DRM_SCHED`, and DMA/CMA support when available. `DRM_ETNAVIV_THERMAL` is a bool depending on `DRM_ETNAVIV`, defaulting to enabled.

## Control Flow
Kconfig controls whether `etnaviv.o` is built in, modular, or omitted. Thermal support selection additionally selects `THERMAL` when enabled.

## State and Persistence
No runtime state is present; this file persists build-time configuration.

## Dependencies and Integration Points
Integrates with the DRM subsystem, MMU requirement, GEM shmem/TMPFS backing, sync file fence export, devcoredump, DMA contiguous memory support, DRM scheduler, and kernel thermal framework.

## Risks
Disabling thermal throttling is explicitly warned as potentially unsafe for SoCs. Missing MMU or DRM dependencies excludes the driver. Configuration changes affect availability of runtime features assumed by source files in this directory.

## Test Signals
Validate allmodconfig/allyesconfig and minimal configs, module build/load with `CONFIG_DRM_ETNAVIV=m`, and thermal-enabled versus thermal-disabled builds.
