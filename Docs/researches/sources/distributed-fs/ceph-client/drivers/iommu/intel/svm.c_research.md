<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/svm.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/svm.c

Purpose: Intel Shared Virtual Memory domain support. It verifies SVM capability, creates SVA domains bound to process `mm_struct`s, installs first-level PASID entries, invalidates secondary IOMMU TLBs on mmu notifier callbacks, and tears PASIDs down when an address space exits.

Important APIs/types/functions: `intel_svm_check()` marks IOMMUs SVM-capable. `intel_svm_domain_alloc()` allocates an `IOMMU_DOMAIN_SVA` domain and registers mmu notifiers. `intel_svm_set_dev_pasid()` attaches a device PASID to an mm. `intel_mm_release()`, `intel_arch_invalidate_secondary_tlbs()`, and `intel_mm_free_notifier()` implement notifier behavior.

Control flow: SVM capability requires PASID support and compatibility with CPU 1GiB pages and LA57. Domain allocation first checks device SVA support, initializes lists/locks/cache tags, and registers `intel_mmuops`. PASID attach validates PASID/ATS/PRI state, adds dev-pasid info, optionally replaces IOPF routing for PRI devices, programs a first-level PASID entry using `mm->pgd` with FL5LP/PWSNP flags, and removes the old domain association. MMU invalidation flushes all or range cache tags. MM release tears down every dev PASID with fault-ignore to prevent hardware walks after mm notifier removal.

State and persistence: SVA domain state includes `domain->mm`, `dev_pasids`, cache tags, notifier, lock, and `qi_batch`. Device PASID table entries persist until detach or mm release.

Dependencies and integration: relies on generic SVA core, Intel PASID programming, mmu_notifier, PCI ATS/PRI, cache-tag flushes, IOPF routing, and x86 CPU feature checks.

Risks: mm release occurs before page tables are cleared and after invalidate callbacks are removed, so PASID teardown ordering is safety-critical. Non-PRI devices are allowed only if their driver handles IOPF itself. The default first-level DID and page-table physical pointer must match VT-d expectations for the process address space.

Test signals: SVA bind/unbind through generic API, mm exit with active PASIDs, LA57 and 1GiB-page capability mismatch, PRI and non-PRI device behavior, mmu notifier range invalidation, and PASID replacement unwind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/svm.c -->
