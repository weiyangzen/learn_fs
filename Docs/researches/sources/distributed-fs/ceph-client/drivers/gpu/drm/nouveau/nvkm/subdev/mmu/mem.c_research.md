# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/mem.c

## Purpose
Implements common host/system memory objects for the MMU and dispatches memory allocation requests to either VRAM backends or host-page allocation.

## Important APIs, Types, and Functions
Key symbols are `nvkm_mem_new_type`, `nvkm_mem_map_host`, `nvkm_mem_new_host`, `nvkm_mem_map_dma`, `nvkm_mem_map_sgl`, and the `nvkm_mem_dma`/`nvkm_mem_sgl` memory function tables. `struct nvkm_mem` stores target, MMU pointer, page count, pages, and DMA or SGL backing.

## Control Flow, State, and Persistence
Host memory creation either wraps caller-provided DMA/SGL arrays from NVIF arguments or allocates zeroed pages, maps them for DMA, and records per-page DMA addresses. Target is coherent HOST only when the selected type is coherent and not uncached; otherwise NCOH. Destruction unmaps DMA and frees pages. `nvkm_mem_new_type` delegates VRAM requests to `mmu->func->mem.vram`.

## Dependencies and Integration Points
Depends on DMA mapping API, `vmap`, NVIF memory argument unpacking, `nvkm_vmm_map`, and chip-specific VRAM allocation functions.

## Risks and Test Signals
Risks include partial allocation leaks on mid-loop failures, DMA mask/GFP mismatch, incorrect coherent/NCOH target selection, and unsafe user-provided arrays. Test host allocation/free under fault injection, DMA mapping errors, host `vmap`, SGL wrapping, VMM mapping, and 32-bit DMA devices.
