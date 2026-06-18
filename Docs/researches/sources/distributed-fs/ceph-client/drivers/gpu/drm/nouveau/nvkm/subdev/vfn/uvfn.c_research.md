# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/vfn/uvfn.c

## Purpose
Implements the user-visible VFN object that maps the GPU usermode register aperture.

## Important APIs, Types, And Functions
`struct nvkm_uvfn` embeds `nvkm_object` and stores a VFN pointer. `nvkm_uvfn_new()` creates the object, and `nvkm_uvfn_map()` returns BAR0 physical address, size, and IO mapping type.

## Control Flow
Object creation rejects non-empty constructor arguments, stores `device->vfn`, and returns the object. Mapping adds `vfn->addr.user` to the BAR0 PRI resource base and exposes `func->user.size`.

## State, Persistence, And Dependencies
State is the per-object VFN pointer and nvkm object lifetime state.

## Integration Points
Integrates with VFN base user class metadata and nvkm object mapping APIs.

## Risks
Assumes `device->vfn` exists and BAR0 PRI resource address is valid. No argument ABI is supported yet.

## Test Signals
Signals include successful user object construction with zero args and correct mmap address/size reported to userspace.
