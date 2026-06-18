## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_mmu.c

### Purpose
`etnaviv_mmu.c` is the version-independent MMU manager. It allocates GPU virtual address ranges, maps GEM scatterlists and command-buffer suballocations, reaps idle mappings under pressure, tracks flush sequence numbers, and owns global MMU state shared by one or more GPU devices.

### Important APIs, Types, And Functions
Key functions include `etnaviv_iommu_map_gem()`, `etnaviv_iommu_unmap_gem()`, `etnaviv_iommu_reap_mapping()`, `etnaviv_iommu_context_init()`, `etnaviv_iommu_context_put()`, `etnaviv_iommu_restore()`, `etnaviv_iommu_get_suballoc_va()`, `etnaviv_iommu_put_suballoc_va()`, `etnaviv_iommu_global_init()`, and `etnaviv_iommu_global_fini()`. Internal helpers map/unmap page ranges and manage `drm_mm` insertion.

### Control Flow
GEM mapping locks the object, then the context, optionally uses an MMUv1 contiguous-linear shortcut, inserts either an exact softpin node or a free IOVA, maps each DMA scatterlist segment page-by-page through version ops, records the mapping, and increments `flush_seq`. If space is unavailable, it scans idle mappings and reaps enough nodes before retry. Unmapping removes page-table entries and `drm_mm` nodes unless another thread already reaped the mapping. Context init selects v1/v2 allocation and maps the shared command-buffer suballocation. Global init detects MMU version from chip features, allocates the bad page and optional PTA, and enforces one global version.

### State, Persistence, And Dependencies
Persistent state includes `etnaviv_iommu_global`, bad page, optional PTA, per-context `drm_mm`, mapping lists, mapping use counts, and command-buffer mapping lifetime. Dependencies include GEM scatter-gather tables, DMA APIs, DRM memory manager scanning, cmdbuf suballocation, and MMUv1/MMUv2 ops.

### Integration Points
Submit pinning calls through GEM mapping helpers into this layer. GPU FE startup restores contexts through `etnaviv_iommu_restore()`. Dump code can query and copy page tables. The global MMU object is stored in `etnaviv_drm_private`.

### Risks
Mapping lifetime is subtle: active mappings are protected by `mapping->use`, while idle mappings can be reaped to satisfy address-space pressure. Exact softpin insertion must reject overlapping live mappings but may reap idle ones. MMUv1 linear shortcut bypasses page tables and depends on `memory_base`. Error unroll must not leave partial page-table entries.

### Test Signals
Signals include fragmented address-space pressure, idle mapping reaping, exact softpin overlap with live and idle mappings, scatterlist alignment failures, partial map failure unroll, MMUv1 contiguous shortcut, command-buffer mapping limits, global version mismatch across GPUs, and global refcount cleanup.
