# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/mem.h

## Purpose
Declares MMU memory allocation and BAR/user mapping helpers shared by generic, NV04, NV50, and GF100 memory implementations.

## Important APIs, Types, and Functions
Declarations include `nvkm_mem_new_type`, `nvkm_mem_map_host`, `nv04_mem_new/map`, `nv50_mem_new/map`, and `gf100_mem_new/map`.

## Control Flow, State, and Persistence
No executable flow. The prototypes define the contract used by `nvkm_mmu_func.mem` descriptors and user memory objects.

## Dependencies and Integration Points
Includes `priv.h` and is consumed by MMU chip descriptors, `umem.c`, and VMM mapping paths.

## Risks and Test Signals
Risks are signature drift and inconsistent argument ABI handling across generations. Build all MMU variants and test user memory allocation/map classes.
