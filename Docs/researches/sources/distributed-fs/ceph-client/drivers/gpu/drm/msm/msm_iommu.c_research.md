# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_iommu.c

## Purpose
Implements MSM MMU backends for display and GPU IOMMUs, including base domain mapping and Adreno per-process TTBR0 page tables used by GPU private VMs and VM_BIND. It also handles page-table preallocation, PRR MAP_NULL support, TLB flushing, fault routing, and crash diagnostic page-table walking.

## Important APIs, Types, and Functions
- `struct msm_iommu` wraps a parent `iommu_domain`, init lock, per-process page-table count, PRR page, and page-table slab cache.
- `struct msm_iommu_pagetable` wraps a child `msm_mmu`, io-pgtable ops, TLB ops, TTBR, ASID, page-size bitmap, and root page-table pointer.
- `msm_iommu_new()`, `msm_iommu_gpu_new()`, and `msm_iommu_disp_new()` create attached IOMMU domains and install GPU/display fault handlers.
- `msm_iommu_pagetable_create()` clones Adreno SMMU TTBR1 config into TTBR0 per-process page tables, optionally enabling custom alloc/free and PAGE_SIZE-only mappings for userspace-managed VM_BIND.
- `msm_iommu_pagetable_map()` and `msm_iommu_pagetable_unmap()` map/unmap SG tables or PRR pages using io-pgtable ops.
- `msm_iommu_pagetable_prealloc_count()`, `_allocate()`, and `_cleanup()` support async VM_BIND page-table page reservation.
- `msm_iommu_pagetable_params()` and `msm_iommu_pagetable_walk()` expose TTBR/ASID/PTE data for crash dumps.
- `msm_gpu_fault_handler()` and `msm_disp_fault_handler()` route faults to registered MSM handlers.

## Control Flow
Base IOMMU creation allocates a paging domain, applies quirks, attaches the device, and returns `msm_mmu` ops. GPU creation additionally creates a page-table cache from TTBR config, installs a fault handler, and enables SMMU stall if available. Per-process page-table creation obtains TTBR1 config from Adreno SMMU private hooks, builds TTBR0 config, optionally sets custom page-table allocation for VM_BIND, allocates io-pgtable ops, and on the first pagetable enables TTBR0 in the arm-smmu driver plus PRR page support. Map paths iterate SG entries, select the largest valid page size with `calc_pgsize()`, and roll back partial mappings on failure. Unmap loops over page sizes and flushes IOTLB. Destroy tears down TTBR0/PRR on the last pagetable.

## State and Persistence
State is in-memory: IOMMU domain attachment, page-table cache, active per-process pagetable count, PRR page, child page tables, preallocation arrays, root page-table memory, TTBR, and ASID. Fault handler callbacks are stored in `msm_mmu`. No disk persistence.

## Dependencies and Integration Points
Depends on Linux IOMMU, io-pgtable ARM LPAE, Qualcomm Adreno SMMU private hooks, kmem_cache, kmemleak, runtime PM for TLB flushes, and MSM MMU abstractions. It is consumed by GPU VM creation, display KMS VM creation, VM_BIND map/unmap, crashstate capture, and fault handling.

## Risks
High-risk areas include partial map rollback, sign-extension for 49-bit IOVAs, TTBR0 lifecycle across multiple page tables, PRR page allocation/cleanup, page-table preallocation over/under-counting, and fault handling while the device is runtime suspended. VM_BIND restricts to PAGE_SIZE to avoid unsafe block-split behavior.

## Test Signals
Test IOMMU probe/attach failures, GPU and display fault callbacks, VM_BIND sparse mappings, MAP_NULL PRR mappings, TLB flush with runtime PM inactive/active, forced map failures and rollback, devcoredump TTBR/PTE output, and clean TTBR0 disable when last private VM is destroyed.
