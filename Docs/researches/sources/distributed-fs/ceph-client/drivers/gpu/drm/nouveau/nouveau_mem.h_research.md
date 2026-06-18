
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_mem.h

## Purpose
Declares the Nouveau TTM resource/NVIF memory wrapper and memory management helpers.

## Important APIs, Types, and Functions
`struct nouveau_mem` embeds `struct ttm_resource`, stores a `nouveau_drm` pointer, kind/compression bytes, `struct nvif_mem`, and two `struct nvif_vma` slots. `nouveau_mem()` converts a TTM resource to the wrapper. The header declares allocation, deletion, placement range, VRAM/host construction, fini, and map functions, plus `nouveau_mem_map_fixed()`.

## Control Flow
The header provides the common interface used by BO and TTM managers to allocate a resource wrapper first, then initialize it as VRAM or host memory, map it into a VMM, and finally tear it down.

## State and Persistence
The defined wrapper persists for the lifetime of a TTM resource. VMA slots are used by mapping code and must be released by `nouveau_mem_fini()`.

## Dependencies and Integration Points
Depends on TTM BO/resource headers and NVIF memory/VMM headers. It is included by BO, GEM, DMEM, and memory-manager implementation code.

## Risks and Test Signals
Risks include callers forgetting to finalize NVIF VMAs/memory, stale declarations such as `nouveau_mem_map_fixed()` needing implementation elsewhere, and incorrect container conversions. Test signals include build/link coverage, BO allocation/free under memory pressure, and VMM map/unmap paths.
