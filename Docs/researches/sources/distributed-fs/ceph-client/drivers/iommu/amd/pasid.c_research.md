# sources/distributed-fs/ceph-client/drivers/iommu/amd/pasid.c

Purpose: implements AMD SVA PASID binding. It binds process page tables into a device GCR3 table, handles mmu-notifier invalidations, and removes PASID mappings when the mm exits or the IOMMU core detaches a PASID.

Important APIs, types, and functions: `iommu_sva_set_dev_pasid()` is the domain op for binding a PASID; `amd_iommu_remove_dev_pasid()` clears a binding; `amd_iommu_domain_alloc_sva()` allocates SVA domains; `iommu_sva_domain_free()` unregisters the notifier; notifier callbacks are `sva_arch_invalidate_secondary_tlbs()` and `sva_mn_release()`. Binding records use `struct pdom_dev_data`.

Control flow: allocation creates a `protection_domain`, marks it SVA, installs `sva_mn`, and registers with the target `mm_struct`. Binding rejects replacement (`old`), PASID zero/out-of-range, and devices without enabled PASID/GCR3 state, then writes `domain->mm->pgd` into the device GCR3 table with `amd_iommu_set_gcr3()` and links a binding record. Invalidation iterates records and flushes each PASID range. mm release removes every binding and clears device GCR3 entries.

State and persistence: the SVA domain owns an mmu notifier and a `dev_data_list` of PASID/device bindings. Device GCR3 tables are persistent until explicit clear or mm release. `pasid_cnt` in `gcr3_info` tracks installed PASIDs.

Dependencies and integration points: depends on `amd_iommu_set_gcr3()`, `amd_iommu_clear_gcr3()`, `amd_iommu_dev_flush_pasid_pages()`, generic `IOMMU_DOMAIN_SVA` operations, mmu notifier infrastructure, and GCR3 allocation done during device attach in `iommu.c`.

Risks: PASID zero is reserved for non-PASID traffic and must stay rejected. The code assumes binding removal runs under the protection-domain lock. `domain->mm` must be valid for the SVA domain; failures in notifier registration or GCR3 updates must not leave partial list entries.

Test signals: bind/unbind SVA PASIDs, invalid PASID rejection, mm exit while DMA may still be active, range invalidation propagation to all bound devices, and detach through the blocked-domain PASID path.
