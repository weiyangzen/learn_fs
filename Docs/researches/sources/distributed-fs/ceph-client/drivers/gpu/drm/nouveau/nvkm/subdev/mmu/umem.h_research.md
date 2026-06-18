# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/umem.h

## Purpose
Declares the private user memory object structure and constructor.

## Important APIs, Types, and Functions
`struct nvkm_umem` embeds `nvkm_object`, stores MMU pointer, type flags, `mappable`/`io` state, backing `nvkm_memory`, client list node, and either BAR VMA or CPU map pointer. `nvkm_umem_new` is declared for user class construction.

## Control Flow, State, and Persistence
No executable flow. The structure persists user object map state and backing memory until object destruction.

## Dependencies and Integration Points
Includes `core/object.h` and `mem.h`; consumed by `umem.c`, `ummu.c`, and `uvmm.c`.

## Risks and Test Signals
Risks are union misuse between BAR and CPU mappings and stale list state. Build coverage plus user memory map/unmap/destruction tests validate it.
