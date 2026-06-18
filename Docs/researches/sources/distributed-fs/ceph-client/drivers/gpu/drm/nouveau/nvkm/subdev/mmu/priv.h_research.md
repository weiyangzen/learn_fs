# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/priv.h

## Purpose
Defines the private MMU backend contract, constructors, kind-table exports, and page-table allocation structures.

## Important APIs, Types, and Functions
`struct nvkm_mmu_func` groups lifecycle hooks, DMA width, user classes, memory allocation/mapping hooks, VMM constructor/global settings, kind table callback, system-kind support, and optional VMM promotion. `struct nvkm_mmu_pt` tracks cached/suballocated page-table memory. The header declares R535, base constructors, kind callbacks, and PTC helpers.

## Control Flow, State, and Persistence
No executable flow. The descriptor selected by a chip file determines MMU behavior for all memory and VMM objects. `nvkm_mmu_pt` state persists while VMMs reference page tables.

## Dependencies and Integration Points
Includes public `subdev/mmu.h`; consumed by MMU descriptors, base.c, memory code, VMM code, and R535 glue.

## Risks and Test Signals
Risks include incomplete function tables, wrong DMA bit widths, and page-table cache contract changes. Build all MMU variants and test memory allocation, VMM creation, page-table allocation/free, and R535 paths.
