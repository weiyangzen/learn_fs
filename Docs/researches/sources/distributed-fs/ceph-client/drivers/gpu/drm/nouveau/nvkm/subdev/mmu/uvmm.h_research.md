# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/uvmm.h

## Purpose
Declares the private user VMM object structure and constructor.

## Important APIs, Types, and Functions
`struct nvkm_uvmm` embeds `nvkm_object` and owns a referenced `nvkm_vmm`. `nvkm_uvmm_new` is declared for user VMM class construction.

## Control Flow, State, and Persistence
No executable flow. The referenced VMM persists until object destruction and is used by all VMM user methods.

## Dependencies and Integration Points
Includes `core/object.h` and `vmm.h`; consumed by `uvmm.c` and `ummu.c`.

## Risks and Test Signals
Risks are VMM reference leaks or premature unrefs. Build coverage and user VMM create/destroy stress validate it.
