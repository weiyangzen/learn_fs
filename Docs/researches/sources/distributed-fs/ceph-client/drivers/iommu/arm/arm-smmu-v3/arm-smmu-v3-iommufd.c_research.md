# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3-iommufd.c

Purpose: Arm SMMU v3 iommufd support for hardware info, vSMMU creation, nested domains, virtual invalidation forwarding, and virtual event reporting.

Important APIs, types, and functions: `arm_smmu_hw_info()` reports IDR/IIDR/AIDR data; `arm_vsmmu_alloc_domain_nested()` creates `IOMMU_DOMAIN_NESTED`; `arm_smmu_attach_dev_nested()` installs nested STEs; `arm_vsmmu_cache_invalidate()` copies and converts userspace invalidation commands; `arm_smmu_get_viommu_size()` gates vIOMMU support; `arm_vsmmu_init()` initializes vSMMU state; `arm_vmaster_report_event()` rewrites event SID to vSID. Local helpers validate vSTEs and convert vSID to host SID.

Control flow: nested allocation copies `IOMMU_HWPT_DATA_ARM_SMMUV3`, validates allowed STE bits/configs, extracts ATS intent, and stores sanitized STE words. Nested attach ensures same SMMU, no active SSIDs, prepares attach state under the ASID lock, derives ATS disable policy from virtual EATS, builds a physical STE that combines S2 parent and virtual S1/CD-table/bypass/abort state, installs it, and commits attach state. Invalidation copies an array from userspace, converts each command to CPU-endian internal format, overwrites VMID/SID with host values, batches into the command queue, and reports progress by shrinking `entry_num`.

State and persistence: `struct arm_vsmmu` stores the host SMMU, S2 parent, and VMID. `struct arm_smmu_nested_domain` stores sanitized virtual STE data, ATS enable flag, and vSMMU pointer. `struct arm_smmu_vmaster` stores per-attached-device vSID state for invalidations and event reporting.

Dependencies and integration points: depends on core SMMU v3 stream-table/CD/cmdq helpers, iommufd vIOMMU/vDEVICE APIs, UAPI structures for Arm SMMUv3, S2 parent domains, implementation-specific hooks, and event queue reporting. Imports the `IOMMUFD` namespace.

Risks: command conversion must not trust userspace VMID/SID fields; failures return `-EIO` for invalid virtual commands. ATS coherency depends on the VM generating ATC invalidations when EATS says ATS is enabled. vIOMMU support is withheld unless hardware has nesting, no forced sync defect, and either full writeback snoop or S2FWB.

Test signals: iommufd create vSMMU, nested attach with abort/bypass/S1 translate STEs, invalid vSTE bit fuzzing, vDEVICE mapping for invalidation/event paths, TLBI/ATC/CFGI command conversion, command queue batching, and event SID rewriting.
