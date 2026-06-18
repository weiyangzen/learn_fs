# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3-sva.c

Purpose: implements SVA domains for Arm SMMU v3. It builds context descriptors for process page tables, registers mmu notifiers, invalidates SMMU TLBs on CPU page-table changes, binds PASIDs, and cleans up ASIDs safely.

Important APIs, types, and functions: `arm_smmu_make_sva_cd()` creates SVA context descriptors and is exported for KUnit; `arm_smmu_sva_supported()` gates feature support; `arm_smmu_sva_domain_alloc()` allocates an SVA domain and ASID; `arm_smmu_sva_set_dev_pasid()` binds a PASID; `arm_smmu_sva_domain_free()` frees through mmu-notifier SRCU; notifier callbacks are `arm_smmu_mm_arch_invalidate_secondary_tlbs()`, `arm_smmu_mm_release()`, and `arm_smmu_mmu_notifier_free()`.

Control flow: support detection checks SMMU coherency/VAX/BBML/page-size/output-address/ASID requirements against sanitized CPU features. Allocation creates a domain, assigns stage SVA, allocates an ASID in `arm_smmu_asid_xa`, registers the notifier, and returns the domain. Binding takes a temporary mm ref, builds a CD pointing at `mm->pgd`, and calls `arm_smmu_set_pasid()`. mm release rewrites bound CDs into valid faulting descriptors with translation disabled, then invalidates the domain.

State and persistence: SVA domains retain ASID, mmu notifier, SMMU pointer, device list, and per-CD descriptor state. ASID xarray membership persists until domain free erases it; actual memory free is deferred through `mmu_notifier_put()` and the notifier free callback.

Dependencies and integration points: uses Arm64 CPU feature registers, `vabits_actual`, MAIR, mmu notifier infrastructure, core SMMU CD write and invalidation helpers, PASID installation, and io-pgtable Arm definitions for TCR encodings.

Risks: SVA ignores CPU permission overlays/GCS and emits a warning. mm release must keep CDs valid to avoid C_BAD_CD event storms while DMA may continue. ASID reuse is allowed after domain invalidation even if notifier invalidations race, relying on harmless extra invalidations.

Test signals: KUnit covers `arm_smmu_make_sva_cd()` transitions. Runtime signals include SVA feature gating on varied page sizes/ASID widths, PASID bind/unbind, mm exit during DMA, secondary TLB invalidation ranges, and ASID reuse stress.
