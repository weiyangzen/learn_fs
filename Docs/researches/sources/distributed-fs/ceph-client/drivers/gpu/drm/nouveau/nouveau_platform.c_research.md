
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_platform.c

## Purpose
Implements Nouveau platform-driver support for Tegra GPUs such as GK20A, GM20B, and GP10B. It binds device-tree compatible strings to Tegra NVKM device configuration and delegates DRM device creation/removal to the core driver.

## Important APIs, Types, and Functions
The platform driver object is `nouveau_platform_driver`. Internal functions are `nouveau_platform_probe()`, `nouveau_platform_remove()`, and PM sleep callbacks `nouveau_platform_suspend()`/`nouveau_platform_resume()` when enabled. Static platform data describes IOMMU address width and power/clock requirements for GK20A, GM20B, and GP10B.

## Control Flow
Probe obtains `nvkm_device_tegra_func` match data from OF, calls `nouveau_platform_device_create()`, and returns `PTR_ERR_OR_ZERO()`. Remove retrieves the stored `nouveau_drm` pointer and calls `nouveau_drm_device_remove()`. PM sleep callbacks delegate to GK20A devfreq suspend/resume. The OF match table registers compatible strings and data.

## State and Persistence
Persistent platform state is stored in the DRM/NVKM device created by the core path and in static match-data structs. The file itself owns no dynamic allocations beyond what the core creation path performs.

## Dependencies and Integration Points
Depends on platform bus/OF matching, NVKM Tegra device functions, GK20A devfreq helpers, and the core platform device creation/removal APIs declared in `nouveau_drv.h`. Registered from module init when `CONFIG_NOUVEAU_PLATFORM_DRIVER` is enabled.

## Risks and Test Signals
Risks include missing or incorrect OF match data, PM domain/regulator/clock requirement mismatches, removal assumptions about driver data, and devfreq-only PM handling diverging from PCI PM. Test signals include boot/probe on supported Tegra compatibles, deferred probe for resources, suspend/resume with devfreq, remove/unbind, and builds with OF or platform driver disabled.
