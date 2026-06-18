<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/nested.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/nested.c

Purpose: Intel VT-d nested-domain support for iommufd/user-managed stage-1 page tables nested on a stage-2 DMA domain. It allocates nested domains, attaches devices or PASIDs, installs nested PASID entries, and exposes user invalidation for guest stage-1 changes.

Important APIs/types/functions: `intel_iommu_domain_alloc_nested()` consumes `IOMMU_HWPT_DATA_VTD_S1`; `intel_nested_attach_dev()` attaches a RID to a nested domain; `intel_nested_set_dev_pasid()` attaches a PASID; `intel_nested_cache_invalidate_user()` handles `IOMMU_HWPT_INVALIDATE_DATA_VTD_S1`; `intel_nested_domain_free()` removes the nested domain from its parent stage-2 list.

Control flow: allocation validates `nested_supported()`, requested flags, user data type, parent stage-2 paging compatibility, and `nested_parent`. It copies the user VT-d stage-1 config, initializes domain lists/locks/xarray, and links into `s2_domain->s1_domains`. Attach blocks translation, verifies parent stage-2 compatibility, attaches the domain to the IOMMU, assigns cache tags, enables IOPF routing, programs PASID `IOMMU_NO_PASID`, then records the device on the domain list. PASID attach performs similar compatibility checks, registers `dev_pasid_info`, replaces IOPF routing, programs the PASID entry, and removes the old PASID association.

State and persistence: nested domains persist `s1_cfg`, `s2_domain`, cache tags, `dev_pasids`, and parent `s1_domains` links. Device attachment updates `device_domain_info` and PASID tables; user invalidations do not persist, they flush cache-tag ranges.

Dependencies and integration: depends on Intel scalable-mode PASID programming in `pasid.c`, core IOMMU domain/PASID attach handles, PCI ATS/PRI compatibility, iommufd user data copy helpers, and cache-tag invalidation helpers.

Risks: nested attach is only valid when the stage-2 domain is compatible with the current IOMMU and marked nested-parent. PASID replacement must unwind IOPF and dev-pasid bookkeeping in the right order. User invalidation accepts only aligned ranges and supported flags; incorrect processed counts can affect userspace retry logic.

Test signals: iommufd nested HWPT allocation, invalid parent rejection, PASID attach/replace/unwind, device attach with IOPF, userspace cache invalidation arrays with partial failures, and teardown while parent tracks child stage-1 domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/nested.c -->
