# sources/distributed-fs/ceph-client/drivers/iommu/amd/nested.c

Purpose: implements AMD nested translation domains for iommufd/vIOMMU. It validates userspace-provided guest DTE data, allocates nested domains, maps guest domain IDs to host domain IDs, and programs physical DTEs combining host stage-2 and guest state.

Important APIs, types, and functions: `amd_iommu_alloc_domain_nested()` is the allocation callback for `iommufd_viommu_ops`; `validate_gdte_nested()` enforces legal guest DTE fields; `gdom_info_load_or_alloc_locked()` manages xarray entries; `set_dte_nested()` synthesizes the hardware DTE; `nested_attach_device()` installs it; `nested_domain_free()` decrements mapping refs and frees hDomIDs. Key state includes `struct nested_domain`, `struct amd_iommu_viommu`, and `struct guest_domain_mapping_info`.

Control flow: allocation copies `IOMMU_HWPT_DATA_AMD_GUEST` from userspace, validates mode/GCR3/GPT/GLX constraints, extracts guest DomID, and looks up or allocates a `guest_domain_mapping_info` under `gdomid_array`. Existing mappings increment a refcount; new mappings allocate an AMD protection-domain ID as hDomID. Attach rejects PASID-enabled devices, builds a nested DTE from the parent v1 page table plus guest GCR3/GPT fields, and calls `amd_iommu_update_dte()`.

State and persistence: the gDomID-to-hDomID map persists in the vIOMMU xarray and is refcounted across nested domains. hDomIDs are allocated from the same global IDA as protection domains. The nested domain stores the copied guest DTE, chosen gDomID, pointer to mapping info, and parent vIOMMU pointer.

Dependencies and integration points: depends on AMD DTE bit definitions, `pt_iommu_amdv1_hw_info()`, `amd_iommu_set_dte_v1()`, `amd_iommu_make_clear_dte()`, `amd_iommu_update_dte()`, iommufd UAPI copy helpers, and the parent-domain/vIOMMU state initialized in `iommufd.c`.

Risks: incorrect gDomID-to-hDomID reuse can cause TLB tag aliasing across nested devices. Validation must reject reserved DTE encodings and unsupported 5-level guest tables. Free paths must erase xarray entries only after the final reference and must always free the hDomID. Nested attach bypasses normal domain device-list ownership, so it relies on group locking and DTE update serialization.

Test signals: iommufd nested-domain allocation with duplicate and unique guest DomIDs, invalid DTE field fuzzing, 4-level versus 5-level capability checks, attach to devices with PASID disabled/enabled, and parent-domain flushes that must also invalidate every mapped hDomID.
