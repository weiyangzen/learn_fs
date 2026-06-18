<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/gk20a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/gk20a.c

## Purpose
Implements instance memory for Tegra GK20A, which lacks dedicated VRAM, using either IOMMU-flattened system pages or physically contiguous DMA memory, with write-combined CPU mappings and L2 cache maintenance.

## Important APIs, Types, And Functions
Important types include gk20a_instobj, gk20a_instobj_dma, gk20a_instobj_iommu, and gk20a_instmem. Important functions include target/page/addr/size callbacks, acquire/release for DMA/IOMMU, vaddr GC/recycle, rd32/wr32/map, DMA/IOMMU destructors, constructors, gk20a_instobj_new, gk20a_instmem_dtor, and gk20a_instmem_new.

## Control Flow
Constructor selects IOMMU if the Tegra device has a domain, otherwise DMA API with weak-ordering/write-combine attrs. Allocation rounds size/align to pages, creates either contiguous DMA memory or individual pages mapped into the GPU IOMMU address space, sets nvkm_memory callbacks, and returns NCOH memory. IOMMU acquire flushes LTC, reuses or creates vmap write-combined mappings, maintains use counts, and enforces a 1 MiB vaddr LRU budget; release moves idle mappings to LRU and invalidates LTC. DMA acquire/release returns the persistent DMA vaddr and flushes/invalidates LTC. Destructors free DMA memory or unmap/free IOMMU pages and address-space nodes.

## State, Persistence, Dependencies, And Integration
State includes GPU address node, CPU vaddr, IOMMU pages/dma_addrs/use count/LRU links, vaddr usage counters, Tegra IOMMU domain/mm/bit/pgshift, DMA attrs, and common instmem lists. Dependencies are core Tegra device data, nvkm_mm, iommu API, DMA API, vmap/vunmap, nvkm_ltc_flush/invalidate, nvkm_vmm_map, and nv04 suspend/resume helpers. Integration points are GK20A MMU/FIFO/GR instance allocations and coherent access on integrated-memory GPUs.

## Risks And Test Signals
Risks: IOMMU bit manipulation and pgshift must match Tegra addressing; vaddr LRU must not recycle mappings in use; cache maintenance is conservative but essential for correctness; error unwind in IOMMU allocation must free partially mapped pages. Test signals include operation with and without IOMMU, instmem read/write/map correctness, vaddr budget recycling, suspend/resume through nv04 helpers, and no DMA/IOMMU leaks on allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/gk20a.c -->
