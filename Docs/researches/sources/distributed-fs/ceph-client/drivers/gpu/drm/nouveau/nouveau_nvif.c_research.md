
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_nvif.c

## Purpose
Provides the NVIF driver backend that directly links the DRM driver to NVKM in-kernel services. It adapts NVIF client operations to NVKM client, object, event, ioctl, and BAR mapping functions.

## Important APIs, Types, and Functions
The exported object is `const struct nvif_driver nvif_driver_nvkm`. Its callbacks are implemented by `nvkm_client_driver_init()`, `nvkm_client_suspend()`, `nvkm_client_resume()`, `nvkm_client_ioctl()`, `nvkm_client_map()`, and `nvkm_client_unmap()`. `nvkm_client_event()` bridges NVKM event delivery into `struct nvif_event` callbacks.

## Control Flow
NVIF initialization calls `nvkm_client_driver_init()`, which creates an NVKM client and installs the event bridge. NVIF ioctls call `nvkm_ioctl()`. NVIF map/unmap operations use `ioremap()` and `iounmap()`. Suspend/resume finish or initialize the root NVKM object with runtime versus system suspend state. Events reinterpret the token as an NVIF object, recover the containing event, call its function, and translate keep/drop return values.

## State and Persistence
State is mostly owned by NVKM clients and NVIF objects. This file stores no mutable global state beyond the constant driver descriptor.

## Dependencies and Integration Points
Depends on NVKM core client/ioctl/object APIs and NVIF client/driver/event/ioctl definitions. `nouveau_drm.c` initializes the DRM NVIF client through this backend.

## Risks and Test Signals
Risks include pointer-token assumptions in event delivery, direct kernel virtual mapping lifetime, and suspend state mismatch between runtime and system PM. Test signals include NVIF ioctl coverage, event delivery and drop/keep behavior, runtime PM suspend/resume, module unload with active events, and error paths during client creation.
