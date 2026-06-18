<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/pasid.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/pasid.h

Purpose: internal Intel PASID data layout and bitfield helper header. It defines PASID directory/table structures, translation-type constants, setup flags, inline PTE/PDE accessors, and prototypes consumed by Intel SVA, nested, DMA-domain, and context setup code.

Important APIs/types/functions: `struct pasid_dir_entry`, `struct pasid_entry`, and `struct pasid_table` represent hardware PASID structures. Inline helpers include `pasid_pde_is_present()`, `get_pasid_table_from_pde()`, `pasid_pte_is_present()`, `pasid_pte_get_pgtt()`, `pasid_clear_entry()`, `pasid_clear_entry_with_fpd()`, `pasid_set_domain_id()`, `pasid_set_slptr()`, `pasid_set_flptr()`, `pasid_set_translation_type()`, `pasid_set_present()`, `pasid_clear_present()`, `pasid_set_ssade()`, `pasid_set_page_snoop()`, `pasid_set_pgsnp()`, and nested/SRE/WPE/EAFE setters.

Control flow: implementation code composes entries by clearing all eight qwords, setting page-table pointers and translation fields, applying capability-driven flags, and finally calling `pasid_set_present()` with a DMA write barrier. Teardown clears present with a barrier before invalidation.

State and persistence: helpers directly encode persistent hardware-visible qwords. `PASID_PTE_FPD` supports non-present entries that suppress fault processing during fault-ignore teardown.

Dependencies and integration: depends on Linux bit macros, VT-d page masks, device and Intel IOMMU forward declarations, and the exported implementation in `pasid.c`.

Risks: bit positions must match VT-d scalable-mode PASID entry layout. `PASID_FLAG_NESTED` and `PASID_FLAG_FL5LP` both use `BIT(1)`, which is safe only because they are used in separate contexts. Barrier placement around present-bit changes is correctness-critical.

Test signals: compile coverage across all Intel IOMMU build options, unit-style validation of encoded qwords against VT-d spec tables, 4-level/5-level first-level setup, and teardown cases preserving or clearing FPD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/pasid.h -->
