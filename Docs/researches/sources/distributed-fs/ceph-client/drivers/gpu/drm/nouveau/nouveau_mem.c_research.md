
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_mem.c

## Purpose
Implements Nouveau's wrapper around TTM resource allocations and NVIF memory objects. It constructs VRAM or host memory objects, maps them into NVIF VMMs with generation-specific arguments, and provides TTM placement range compatibility helpers.

## Important APIs, Types, and Functions
External functions are `nouveau_mem_new()`, `nouveau_mem_del()`, `nouveau_mem_fini()`, `nouveau_mem_vram()`, `nouveau_mem_host()`, `nouveau_mem_map()`, `nouveau_mem_intersects()`, and `nouveau_mem_compatible()`. The implementation uses `struct nouveau_mem`, which embeds `struct ttm_resource` and owns an `nvif_mem` plus two `nvif_vma` slots.

## Control Flow
`nouveau_mem_new()` allocates and initializes the wrapper. `nouveau_mem_vram()` creates an NVIF VRAM memory object using GF100 or NV50 argument formats, respecting contiguity, page size, bankswizzle, and `drm->ttm.type_vram`, then stores the resource start from the NVIF memory address. `nouveau_mem_host()` chooses coherent or non-coherent host memory type based on MMU capabilities and `nouveau_drm_use_coherent_gpu_mapping()`, drops kind/compression if unsupported, and constructs an NVIF RAM object from an sg list or DMA address array. `nouveau_mem_map()` selects VMM map argument formats for NV50 and GF100+ VMM classes and maps the NVIF memory into a VMA. `nouveau_mem_del()` tears the NVIF state down, finalizes the TTM resource, and frees the wrapper.

## State and Persistence
Persistent state is one `struct nouveau_mem` per TTM resource. It stores kind/compression metadata, NVIF memory object, VMA slots used by the BO/VMM code, and a pointer back to the DRM device. The underlying memory is owned by NVIF/NVKM and TTM.

## Dependencies and Integration Points
Depends on DRM TTM resources/TTM TT, NVIF MMU/MEM/VMM classes, and Nouveau BO/DRM helpers. It is used by BO allocation, TTM memory managers, and VMM mapping paths.

## Risks and Test Signals
Risks include wrong memory type selection for coherent versus non-coherent mappings, unsupported compression/kind handling, page-size alignment errors, VMM class argument mismatch, and resource-range eviction checks. Test signals include VRAM and GART BO allocation, imported sg-table BOs, compressed/tiled formats, coherent mapping behavior on affected platforms, eviction placement constraints, and suspend/unload teardown of mapped resources.
