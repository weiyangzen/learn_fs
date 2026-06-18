
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ioctl.h

## Purpose
Declares Nouveau's normal and compat file ioctl entry points.

## Important APIs, Types, and Functions
The header declares `nouveau_compat_ioctl()` and `nouveau_drm_ioctl()`.

## Control Flow
No runtime control flow is implemented. `nouveau_drm.c` uses these declarations for file operations, and `nouveau_ioc32.c` calls back into the normal handler when no compat-specific translator is present.

## State and Persistence
No state is defined.

## Dependencies and Integration Points
It provides the small interface between file operations in `nouveau_drm.c` and compat ioctl handling in `nouveau_ioc32.c`.

## Risks and Test Signals
Risk is low, but prototype changes must stay synchronized with DRM file operation signatures. Test signals are compile coverage with and without `CONFIG_COMPAT` and basic ioctl dispatch tests.
