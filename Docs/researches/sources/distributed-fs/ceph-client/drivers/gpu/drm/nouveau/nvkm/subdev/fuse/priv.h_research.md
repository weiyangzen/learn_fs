<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/priv.h

## Purpose
Declares the private fuse subdevice function-table contract.

## Important APIs, Types, And Functions
Defines `nvkm_fuse(p)`, `struct nvkm_fuse_func` with `read`, and `nvkm_fuse_new_`.

## Control Flow
No runtime control flow. Generation files include it to provide constructors and read hooks.

## State And Persistence
No state is stored in the header. The function pointer persists in constructed fuse objects.

## Dependencies And Integration Points
Includes public `subdev/fuse.h` and is used by base and generation implementations.

## Risks And Edge Cases
The interface exposes only a raw `u32 addr` read hook; policy and address validation are external.

## Test Signals
Compile/link correctness and successful dispatch from `nvkm_fuse_read`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/priv.h -->
