# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/ummu.h

## Purpose
Declares the private user MMU object wrapper.

## Important APIs, Types, and Functions
`struct nvkm_ummu` embeds `nvkm_object` and points to the owning `nvkm_mmu`. `nvkm_ummu_new` constructs the object from a device and object class.

## Control Flow, State, and Persistence
No executable flow. The object pointer persists to route user methods and child-object constructors to the correct MMU.

## Dependencies and Integration Points
Includes `core/object.h` and `priv.h`; consumed by user memory and user VMM wrappers.

## Risks and Test Signals
Risks are stale MMU pointers and constructor signature drift. Build and NVIF MMU object creation tests cover it.
