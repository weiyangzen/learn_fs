<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/pasid.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/pasid.c

Purpose: Intel scalable-mode PASID directory/table management and PASID entry programming. It allocates per-device PASID tables, programs first-level, second-level, pass-through, dirty-tracking, and nested translation entries, tears entries down with required invalidations, and installs PASID directory pointers in context entries.

Important APIs/types/functions: exported functions include `intel_pasid_alloc_table()`, `intel_pasid_free_table()`, `intel_pasid_get_table()`, `intel_pasid_setup_first_level()`, `intel_pasid_setup_second_level()`, `intel_pasid_setup_dirty_tracking()`, `intel_pasid_setup_pass_through()`, `intel_pasid_setup_nested()`, `intel_pasid_tear_down_entry()`, `intel_pasid_setup_page_snoop_control()`, `intel_pasid_setup_sm_context()`, `intel_pasid_teardown_sm_context()`, and `intel_context_flush_no_pasid()`.

Control flow: allocation sizes the PASID directory from PCI PASID capability and `intel_pasid_max_id`, allocates IOMMU-accounted pages, and lazily allocates 4 KiB PASID entry tables with `try_cmpxchg64()` on PDEs. Setup paths validate hardware capability, lock `iommu->lock`, reject already-present entries, encode page-table pointers/domain IDs/address widths/PGTT/snoop/fault bits, release the lock, then flush caches using PASID-cache, PIOTLB/IOTLB, device-TLB, or write-buffer invalidations. Teardown clears present first, flushes PASID and TLB state based on PGTT, clears the entry or leaves FPD for fault-ignore SVA release, and drains PRQ when needed. Scalable-mode context setup installs the PASID directory into all matching PCI DMA aliases and handles copied kdump contexts with global invalidations.

State and persistence: `struct pasid_table` hangs from `device_domain_info`; PDE/PTE pages remain until table free. PASID entries persist hardware translation state. Context entries persist PASID-table base, RID2PASID, DTE/PASIDE/PRE bits, and present/fault-enable state.

Dependencies and integration: integrates VT-d queued invalidation, Intel domain ID allocation, second-stage page-table metadata, PCI ATS/devTLB invalidations, SVA/nested code, kdump copied contexts, and `iommu-pages` allocation.

Risks: invalidation ordering is spec-critical, especially present-bit clearing, A/D dirty tracking toggles, and context replacement after copied tables. Lazy PDE population must remain race-safe. Device-TLB flushes are skipped for absent PCI devices to avoid hangs. PASID zero has special RID2PASID invalidation semantics.

Test signals: PASID table allocation/free with different PCI PASID widths, concurrent PASID entry creation, first/second/nested/pass-through setup rejection paths, dirty tracking enable/disable, SVA teardown with PRQ drain, scalable context setup for PCI aliases, and kdump copied-context cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/pasid.c -->
