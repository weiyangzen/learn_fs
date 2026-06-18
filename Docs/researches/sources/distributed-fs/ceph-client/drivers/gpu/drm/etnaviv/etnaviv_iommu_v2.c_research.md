## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_iommu_v2.c

### Purpose
`etnaviv_iommu_v2.c` implements MMUv2 page-table contexts. MMUv2 supports per-context master/second-level page tables, optional security-mode PTA loading, 4 GiB minus first-page virtual address space, and softpin-capable addressing.

### Important APIs, Types, And Functions
`struct etnaviv_iommuv2_context` embeds the generic context and owns a PTA id, one MTLB page, and lazily allocated STLB pages. Important functions are `etnaviv_iommuv2_context_alloc()`, `etnaviv_iommuv2_map()`, `etnaviv_iommuv2_unmap()`, `etnaviv_iommuv2_ensure_stlb()`, dump helpers, `etnaviv_iommuv2_restore_nonsec()`, `etnaviv_iommuv2_restore_sec()`, `etnaviv_iommuv2_get_mtlb_addr()`, and `etnaviv_iommuv2_get_pta_id()`.

### Control Flow
Allocation chooses a free PTA id under the global lock, allocates and initializes an MTLB page with exception entries, records the MTLB DMA in the global PTA array, and initializes the generic address manager. Mapping validates 4 KiB size, computes MTLB/STLB indexes, lazily allocates the STLB, encodes present/write/upper-physical bits, and writes the STLB entry. Unmap restores the exception entry. Nonsecure restore configures MMUv2 through a command buffer and enables `VIVS_MMUv2_CONTROL`; secure restore programs PTA and safe addresses, loads the selected PTA id through the FE, and enables secure MMU control.

### State, Persistence, And Dependencies
State persists in per-context MTLB/STLB DMA pages, PTA allocation bitmap, global PTA memory, bad page DMA, and GPU `mmu_context`. Dependencies include Etnaviv command-buffer helpers, generated MMUv2 registers, DMA WC allocation, vmalloc, and GPU security mode.

### Integration Points
Generic mapping and submit code call the ops through `etnaviv_mmu.c`. Softpin submit support is gated on `ETNAVIV_IOMMU_V2`. GPU reset/security logic in `etnaviv_gpu.c` selects secure versus nonsecure restore behavior.

### Risks
PTA id leaks or stale PTA entries can cross-wire contexts. Unmap assumes the STLB exists for mapped IOVA. Restore exits early if hardware MMU is already enabled, so reset paths must clear hardware state. Secure-mode register programming must agree with hardware security ownership.

### Test Signals
Tests should cover PTA exhaustion, map/unmap across multiple MTLB slots, write-protection bit encoding, 64-bit physical address encoding, dump sizing with sparse STLBs, nonsecure and secure restore paths, and softpin submissions at fixed addresses.
