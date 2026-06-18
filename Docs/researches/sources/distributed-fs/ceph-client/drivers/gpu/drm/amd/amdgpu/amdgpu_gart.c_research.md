# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gart.c

## Purpose
`amdgpu_gart.c` implements common internal GART management. It allocates dummy pages and GART page tables in system RAM or VRAM, maps and unmaps CPU/VRAM pages into the GPU aperture, handles gfx9 MQD memory-type differences, and invalidates GPU TLBs after table changes.

## Important APIs, types, and functions
Public functions include `amdgpu_gart_init()`, `amdgpu_gart_dummy_page_fini()`, `amdgpu_gart_table_ram_alloc()`, `amdgpu_gart_table_ram_free()`, `amdgpu_gart_table_vram_alloc()`, `amdgpu_gart_table_vram_free()`, `amdgpu_gart_map()`, `amdgpu_gart_bind()`, `amdgpu_gart_unbind()`, `amdgpu_gart_map_vram_range()`, `amdgpu_gart_map_gfx9_mqd()`, and `amdgpu_gart_invalidate_tlb()`.

## Control flow
Initialization verifies `PAGE_SIZE >= AMDGPU_GPU_PAGE_SIZE`, DMA maps the global TTM dummy page, and derives CPU/GPU page counts from `adev->gmc.gart_size`. System-RAM table allocation allocates pages, assigns them to the device mapping, DMA maps them, builds an SG table, creates an SG BO, pins it in GTT, stores the CPU pointer, and allocates VMID0 GART backing. VRAM table allocation uses `amdgpu_bo_create_kernel()` and initializes entries to default PTE flags. Mapping functions write GPU PTE/PDE entries with `amdgpu_gmc_set_pte_pde()`, expanding each CPU page into 4 KiB GPU pages when needed. Unbind replaces entries with the dummy page and invalidates TLBs.

## State and persistence behavior
Runtime state lives in `adev->gart`: BO, CPU pointer, page counts, table size, and default PTE flags, plus `adev->dummy_page_addr`. There is no persistence across driver unload. The GART page table is hardware-visible memory and must be reinitialized after teardown/reset as required by ASIC code.

## Dependencies and integration points
It depends on DMA mapping, TTM dummy pages, SG BOs, AMDGPU BO creation/pinning, GMC PTE formatting, reset-domain locking, HDP flush, VM hub masks, and DRM hot-unplug guards. TTM memory management and VMID0 access depend on these mappings.

## Risks and edge cases
System table allocation has many cleanup paths involving pages, SG tables, BOs, pinning, and DMA mappings. TLB invalidation skips HDP flush if the reset-domain read lock cannot be acquired. Hot-unplug guards prevent MMIO access but can leave mapping calls as no-ops. PTE flags must distinguish system memory from VRAM; `amdgpu_gart_map_vram_range()` warns if system flags are used. gfx9 MQD mapping uses UC for the first page and NC for control stack pages, so off-by-one handling matters.

## Test signals
Signals include GART init page counts, RAM-table and VRAM-table allocation/free, dummy-page unmap, BO pin/unpin, CPU-page to GPU-page PTE expansion, unbind to dummy page, TLB flushes on all VM hubs, gfx9 MQD mapping memory types, hot-unplug no-op behavior, and allocation-failure unwind testing.
