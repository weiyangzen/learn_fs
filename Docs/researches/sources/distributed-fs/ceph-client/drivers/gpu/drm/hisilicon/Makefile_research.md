
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/Makefile

## Purpose
`hisilicon/Makefile` routes configured Hisilicon DRM drivers into their subdirectories.

## Important APIs, Types, And Functions
It adds `hibmc/` when `CONFIG_DRM_HISI_HIBMC` is enabled and `kirin/` when `CONFIG_DRM_HISI_KIRIN` is enabled.

## Control Flow
There is no runtime flow. Kbuild uses these conditional object-directory entries to descend into driver-specific builds.

## State And Persistence
The file owns build graph state only.

## Dependencies And Integration Points
It connects the parent Hisilicon DRM directory to child makefiles such as `hibmc/Makefile`, where the `hibmc-drm` object composition is defined.

## Risks
If the symbol names diverge from child Kconfig options, the subdirectory will not build even when configured. Adding or renaming child drivers requires coordinated Kconfig and Makefile updates.

## Test Signals
Build tests should confirm enabling `CONFIG_DRM_HISI_HIBMC` descends into `hibmc/` and produces `hibmc-drm.o` or its module.
