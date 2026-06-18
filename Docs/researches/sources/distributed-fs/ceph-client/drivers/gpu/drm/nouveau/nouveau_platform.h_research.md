
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_platform.h

## Purpose
Declares the Nouveau platform driver for optional Tegra platform-device registration.

## Important APIs, Types, and Functions
The only declaration is `extern struct platform_driver nouveau_platform_driver`.

## Control Flow
No runtime logic is implemented. `nouveau_drm.c` registers and unregisters this driver during module init/exit when platform support is configured.

## State and Persistence
No state is owned by the header.

## Dependencies and Integration Points
Includes `nouveau_drv.h` so the platform driver declaration shares the common Nouveau device definitions. It is included by platform implementation and core DRM module code.

## Risks and Test Signals
Risk is limited to build configuration and symbol visibility. Test signals include compile coverage with `CONFIG_NOUVEAU_PLATFORM_DRIVER` enabled/disabled and platform probe registration.
