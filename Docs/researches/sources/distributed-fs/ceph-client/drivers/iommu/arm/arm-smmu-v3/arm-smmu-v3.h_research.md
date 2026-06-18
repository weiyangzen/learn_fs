<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3.h

## Purpose

`arm-smmu-v3.h` is the private hardware ABI and shared driver-state header for the Arm SMMUv3 driver family. It defines MMIO register offsets, register bitfields, stream table and context descriptor layouts, command/event/PRI queue encodings, in-memory queue and domain structures, implementation hook contracts, feature and option masks, SVA/iommufd/Tegra extension entry points, and helper inlines used by the main driver and companion implementation files.

## Important APIs, Types, and Functions

The register macro blocks cover ID registers, CR0/CR1/CR2, GBPA, IRQ control, global errors, MSI config registers, stream table base/config registers, command/event/PRI queue base/prod/cons registers, common memory attributes, and queue index/wrap helpers. The header also defines natural queue sizing through `Q_MAX_SZ_SHIFT` and per-queue maximum shifts.

Hardware table types include `struct arm_smmu_ste`, `struct arm_smmu_strtab_l1`, `struct arm_smmu_strtab_l2`, `struct arm_smmu_cd`, `struct arm_smmu_cdtab_l1`, and `struct arm_smmu_cdtab_l2`. Helpers such as `arm_smmu_strtab_l1_idx`, `arm_smmu_strtab_l2_idx`, `arm_smmu_cdtab_l1_idx`, and `arm_smmu_cdtab_l2_idx` encode the split between L1 and L2 tables.

Command-related definitions include `struct arm_smmu_cmdq_ent`, command opcodes, TLBI range fields, ATC invalidation fields, PRI response fields, CMD_SYNC fields, `struct arm_smmu_ll_queue`, `struct arm_smmu_queue`, `struct arm_smmu_cmdq`, `struct arm_smmu_cmdq_batch`, and `arm_smmu_cmdq_supports_cmd`.

Driver state types include `struct arm_smmu_device`, `struct arm_smmu_master`, `struct arm_smmu_domain`, `struct arm_smmu_nested_domain`, `struct arm_smmu_master_domain`, `struct arm_smmu_invs`, `struct arm_smmu_inv`, `struct arm_smmu_inv_state`, `struct arm_smmu_attach_state`, `struct arm_smmu_event`, `struct arm_smmu_vmaster`, and `struct arm_vsmmu`. `struct arm_smmu_impl_ops` is the extension point for vendor-specific SMMUv3 implementations.

Extern and prototype declarations expose cross-file functions such as `arm_smmu_domain_alloc`, `arm_smmu_clear_cd`, `arm_smmu_get_cd_ptr`, `arm_smmu_make_s1_cd`, `arm_smmu_write_cd_entry`, `arm_smmu_set_pasid`, `arm_smmu_domain_inv_range`, `__arm_smmu_cmdq_skip_err`, `arm_smmu_init_one_queue`, `arm_smmu_cmdq_init`, `arm_smmu_attach_prepare`, `arm_smmu_attach_commit`, `arm_smmu_install_ste_for_dev`, and `arm_smmu_cmdq_issue_cmdlist`. KUnit-only declarations expose STE/CD and invalidation-array internals for direct tests.

## Control Flow

The header itself has no runtime control flow, but it shapes the driver flow. Probe code reads `IDR*` fields into `ARM_SMMU_FEAT_*` flags, configures queues using `Q_*` and queue-size macros, and programs hardware tables using the STRTAB and CTXDESC definitions. Command construction fills an `arm_smmu_cmdq_ent` union and the main driver encodes it into the CMDQ bitfields declared here.

Attach and invalidation sequencing are modeled in the structures declared here. `arm_smmu_attach_state` carries old domain, master, SSID, ATS policy, vmaster state, and two invalidation states across prepare and commit. `arm_smmu_invs` describes the RCU-protected per-domain invalidation array that fast-path invalidation readers consume. The enum ordering of `arm_smmu_inv_type` is intentionally used for command issue ordering, with TLBI before ATC invalidation.

Configuration conditionals define build-time flow. When `CONFIG_ARM_SMMU_V3_SVA` is disabled, SVA helpers become stubs or NULL function pointers. When `CONFIG_TEGRA241_CMDQV` is disabled, `tegra241_cmdqv_probe` returns `-ENODEV`. When `CONFIG_ARM_SMMU_V3_IOMMUFD` is disabled, iommufd hardware-info, viommu, nested-domain, and vmaster hooks are NULL or no-op fallbacks.

## State and Persistence Behavior

The types in this header define all important persistent in-kernel state for the SMMUv3 driver. `arm_smmu_device` persists for the platform device lifetime and owns MMIO mappings, feature masks, command/event/PRI queues, stream tables, ID allocators, IOMMU core handle, stream tree, and stream mutex. `arm_smmu_master` persists while an endpoint is attached to the IOMMU core and owns stream IDs, CD table storage, ATS/stall flags, PASID width, and IOPF refcount. `arm_smmu_domain` persists for a paging/SVA domain and owns io-pgtable ops, ASID/VMID state, domain geometry, invalidation arrays, and attached device list.

Hardware-visible state is represented with little-endian entry arrays (`__le64`) and DMA addresses. Stream table entries and context descriptors are fixed at eight dwords in the main driver, and the header layout must stay aligned with the architecture. Queue state combines software producer/consumer shadow fields, hardware MMIO registers, coherent queue memory, and DMA base register encodings.

The header also encodes reference/lifetime expectations. `arm_smmu_invs` is RCU-freed. `arm_smmu_domain_free` assumes no invalidation concurrency remains. `arm_smmu_master_canwbs` derives write-back-safe coherency from firmware spec flags at runtime rather than storing a duplicate property.

## Dependencies and Integration Points

The header depends on kernel bitfield, IOMMU, iommufd, kernel utility, memory-zone, and size definitions. It is consumed by the main SMMUv3 driver, Tegra241 CMDQV, SVA support, iommufd support, and KUnit tests. Its public surface bridges Linux IOMMU core concepts (`struct iommu_domain`, `iommufd_viommu`, user data arrays, `enum iommu_hw_info_type`, `enum iommu_viommu_type`) with architecture-specific SMMUv3 state.

`struct arm_smmu_impl_ops` is a key integration point for implementation extensions. A vendor implementation can add reset/remove hooks, allocate extra structures, route commands to a secondary command queue, expose vendor-specific hardware info, and initialize virtual SMMU state. The main driver checks that `get_viommu_size` and `vsmmu_init` are paired.

## Risks and Edge Cases

This header is tightly coupled to hardware layout. Wrong bit masks, endian conversions, table sizes, or queue sizing constants can corrupt hardware-visible descriptors. Queue index and wrap macros depend on `max_n_shift`; callers must preserve natural alignment and power-of-two sizes.

Feature and option flags are bit positions in a shared `u32`, so additions need care to avoid overlap. The enum ordering of `arm_smmu_inv_type` is semantically significant for invalidation command order. `struct arm_smmu_cmdq_ent` is a union; command builders must only read fields valid for the selected opcode.

Conditional stubs are intentionally NULL/no-op in some configurations. Callers must be prepared for unsupported SVA, iommufd, and CMDQV paths. The iommufd fallback definitions make compile-time integration simple, but runtime behavior depends on the main driver checking capabilities before advertising user-facing features.

## Test Signals

Build tests should cover all relevant config combinations: SVA on/off, iommufd on/off, Tegra241 CMDQV on/off, KUnit on/off, PCI PRI/ATS on/off, and CMA alignment variants. KUnit tests should validate descriptor used-bit masks, hitless entry update helpers, invalidation-array helpers, queue macro wrap behavior, table index helpers, and command support filtering. Static analysis should watch flexible-array bounds, `__counted_by(max_invs)`, endian conversions, and struct-size assumptions shared with vendor files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3.h -->
