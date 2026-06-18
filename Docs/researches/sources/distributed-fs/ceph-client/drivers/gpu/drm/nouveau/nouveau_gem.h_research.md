
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_gem.h

## Purpose
Declares Nouveau GEM APIs and PRIME hooks, and provides the conversion helper from `drm_gem_object` to the containing `nouveau_bo`.

## Important APIs, Types, and Functions
`nouveau_gem_object()` is the key inline container conversion. The header exposes `nouveau_gem_object_funcs`, object lifecycle functions, GEM ioctls, `nouveau_gem_new()`, and PRIME functions `nouveau_gem_prime_pin()`, `nouveau_gem_prime_unpin()`, `nouveau_gem_prime_get_sg_table()`, `nouveau_gem_prime_import_sg_table()`, and `nouveau_gem_prime_export()`.

## Control Flow
This header routes DRM GEM callbacks and ioctls to Nouveau implementations. The function table declared here is installed by GEM/PRIME allocation paths and later called by DRM core.

## State and Persistence
No state is stored in the header. It defines the interface to persistent BO/GEM state owned by `struct nouveau_bo`.

## Dependencies and Integration Points
Includes `nouveau_drv.h` and `nouveau_bo.h`, so it is part of the common object/memory interface consumed by DRM device setup, GEM implementation, PRIME import/export, and callers that need BO conversion.

## Risks and Test Signals
Risk is interface drift between GEM, BO, and PRIME implementations. Build and runtime tests should cover GEM object open/close/free callbacks, PRIME import/export, and ioctl registration paths.
