<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu_context.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu_context.h

### Purpose
`ivpu_mmu_context.h` declares the per-context page table and virtual-address allocator structures plus the API used by GEM, context lifecycle, and MMU descriptor code.

### Important APIs, Types, And Functions
`IVPU_MMU_PGTABLE_ENTRIES` is 512 entries per level. `struct ivpu_mmu_pgtable` stores the root DMA pointer and nested CPU pointer arrays for PUD/PMD/PTE pages. `struct ivpu_mmu_context` stores the lock, `drm_mm`, page table, CD-valid flag, and context ID. Exported operations initialize/finalize contexts, manage global/reserved contexts, insert/remove address nodes, map/unmap SG tables, and set pages read-only.

### Control Flow
No executable flow exists in the header. The API implies context lock protection for address allocation and page-table mutation.

### State, Persistence, And Dependencies
The context persists for a DRM file/private context or device global/reserved context. It depends on `drm_mm`, DMA page-table roots, and hardware SSID identity.

### Integration Points
GEM BO allocation/binding and job submission depend on correct VPU virtual mappings from this API. MMU descriptor code consumes `pgd_dma` when installing context descriptors.

### Risks
The nested pointer layout is memory-heavy and assumes page-table levels are lazily allocated. Callers must keep BO lifetime, SG lifetime, and mapping lifetime synchronized with context teardown.

### Test Signals
Compile tests, lockdep on concurrent BO operations, leak checks after context close, and map/unmap stress with many sparse VPU ranges are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu_context.h -->
