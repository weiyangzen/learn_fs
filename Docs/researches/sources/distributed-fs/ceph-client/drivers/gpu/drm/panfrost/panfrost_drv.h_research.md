# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_drv.h

## Purpose
This small header exposes the transparent hugepage module setting to Panfrost GEM code.

## Important APIs, Types, and Functions
It declares `extern bool panfrost_transparent_hugepage` when the header is included. No functions or types are defined.

## Control Flow
There is no executable flow. `panfrost_gem_init` reads the variable to decide whether to create a hugepage-enabled GEM mount when transparent hugepage support is configured.

## State and Persistence Behavior
The actual state is defined in `panfrost_drv.c` under `CONFIG_TRANSPARENT_HUGEPAGE` as a read-only module parameter. This header only provides access to that state.

## Dependencies and Integration Points
It connects the driver module parameter defined by the platform/DRM entry file to the GEM initialization implementation.

## Risks
The declaration is only valid when the corresponding definition is compiled; callers should keep use guarded consistently with `CONFIG_TRANSPARENT_HUGEPAGE`. Any future settings added here become cross-file driver configuration surface.

## Test Signals
Build with and without transparent hugepage support and boot with `panfrost.transparent_hugepage=0/1` to verify GEM initialization follows the setting.
