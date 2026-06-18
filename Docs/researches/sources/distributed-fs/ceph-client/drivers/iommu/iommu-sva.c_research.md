<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-sva.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommu-sva.c

Purpose: generic Shared Virtual Addressing helpers. It binds process address spaces to devices with global PASIDs, reuses or allocates SVA domains, manages bind references, handles SVA I/O page faults by faulting CPU page tables, and broadcasts kernel VA invalidations to active SVA mms.

Important APIs/types/functions: exported `iommu_sva_bind_device()`, `iommu_sva_unbind_device()`, `iommu_sva_get_pasid()`, `mm_pasid_drop()`, and `iommu_sva_invalidate_kva_range()`. Internal helpers include `iommu_alloc_mm_data()`, `iommu_sva_domain_alloc()`, `iommu_sva_iopf_handler()`, `iommu_sva_handle_iopf()`, and `iommu_sva_handle_mm()`.

Control flow: bind requires an IOMMU group, locks global SVA state, allocates/reuses `mm->iommu_mm` and PASID, reuses an existing attach handle if present, otherwise tries existing SVA domains for the mm or allocates a driver SVA domain through `ops->domain_alloc_sva`, attaches the device PASID, updates domain/mm lists, and returns a refcounted handle. Unbind decrements handle refs, detaches PASID when last, frees domains with no users, and updates the global active-mm list. Fault handling queues work per IOPF group, checks PASID-valid faults, pins the mm, validates VMA permissions, calls `handle_mm_fault()`, then responds success or invalid/failure.

State and persistence: global `iommu_sva_lock`, `iommu_sva_present`, and `iommu_sva_mms` track active SVA address spaces. Each `iommu_mm_data` stores PASID, mm, domain list, and list node. Domains hold mm references and IOPF handler pointers; handles hold device and refcount.

Dependencies and integration: integrates architecture PASID helpers, global PASID allocator, IOMMU PASID attach/detach, driver `domain_alloc_sva`, mm fault handling, IOPF groups, and mmu notifier secondary TLB invalidation.

Risks: `arch_pgtable_dma_compat()` may reject mms incompatible with device DMA. PASID range is checked against each device `max_pasids`. Fault handling must not outlive mm teardown; domain allocation `mmgrab()` and driver free paths must pair. Access checks must correctly translate IOMMU permissions to VMA/fault flags.

Test signals: repeated bind/unbind reference counting, reuse of domains across devices for one mm, PASID exhaustion/range errors, IOPF read/write/exec/priv faults, mm exit `mm_pasid_drop()`, and `iommu_sva_invalidate_kva_range()` with active and inactive lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-sva.c -->
