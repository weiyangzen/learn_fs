## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_mmu.h

### Purpose
`etnaviv_mmu.h` declares the generic MMU abstraction used by Etnaviv GPU, GEM, command-buffer, and dump code.

### Important APIs, Types, And Functions
It defines protection bits, `enum etnaviv_iommu_version`, `struct etnaviv_iommu_ops`, `struct etnaviv_iommu_global`, and `struct etnaviv_iommu_context`. Public functions cover global init/fini, GEM map/unmap/reap, suballocation VA get/put, dump, context init/get/put, restore, v1/v2 context allocation, and MMUv2 MTLB/PTA helpers.

### Control Flow
The header itself only supplies `etnaviv_iommu_context_get()` as a kref increment. The ops table defines the dynamic dispatch used by `etnaviv_mmu.c` for version-specific page-table operations.

### State, Persistence, And Dependencies
`etnaviv_iommu_global` persists the selected MMU version, ops, use count, bad page, memory base, and either MMUv1 shared context or MMUv2 PTA storage. `etnaviv_iommu_context` persists the kref, global pointer, mapping lock/list, `drm_mm`, flush sequence, and command-buffer mapping.

### Integration Points
This header is the contract between MMUv1, MMUv2, generic MMU, GEM mapping, GPU startup, and command-buffer suballocation. Softpin and dump paths rely on fields exposed here.

### Risks
Ops implementations must keep `.map` and `.unmap` semantics consistent, especially return sizes from unmap. Global union fields are mutually exclusive by version; using the wrong member corrupts state. Context users must hold references while mappings or GPU state can still point at the context.

### Test Signals
Compile coverage with both MMU versions, kref lifetime tests, lockdep around context mapping locks, dump helpers, global version mismatch tests, and softpin builds validate this contract.
