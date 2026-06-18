# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/driver.h

## Purpose
Defines the NVIF backend-driver abstraction used by client/object code to call into NVKM or another implementation.

## Important APIs, Types, And Functions
Defines `struct nvif_driver` callbacks for init, suspend, resume, ioctl, map, and unmap; exports `nvif_driver_init` and `nvif_driver_nvkm`.

## Control Flow
Client initialization selects a backend, then object operations dispatch through ioctl/map/unmap callbacks. Suspend/resume forward lifecycle changes.

## State And Persistence
Backend-private state is returned through `priv` during init and persists behind the client until teardown.

## Dependencies And Integration Points
Depends on `nvif/os.h`; bridges NVIF front-end code with the NVKM in-kernel server.

## Risks
Callback ABI mismatches can corrupt object construction or mappings. Map/unmap size mismatches can leak or invalidate MMIO mappings.

## Test Signals
NVKM backend initialization, object ioctl round trips, mapping/unmapping tests, and suspend/resume validate behavior.
