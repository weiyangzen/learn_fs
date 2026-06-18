# sources/distributed-fs/ceph-client/drivers/iommu/intel/iommu.h

## Purpose

`iommu.h` is the shared Intel VT-d driver contract for the files in this directory. It defines hardware register offsets, capability decoders, command/status bit encodings, queued-invalidation descriptor formats, core data structures for IOMMUs/domains/devices/PASIDs/cache tags, inline context/PTE/descriptor helpers, and cross-file function declarations. It is the schema binding `dmar.c`, `iommu.c`, debugfs, PASID, PRQ, SVM, nested translation, cache tag, and perf code together.

## Important APIs, Types, And Functions

- VT-d page constants: `VTD_PAGE_SHIFT`, `VTD_PAGE_SIZE`, `VTD_PAGE_MASK`, `VTD_PAGE_ALIGN()`, `VTD_STRIDE_SHIFT`, and address-width constants.
- Register offsets: `DMAR_VER_REG`, `DMAR_CAP_REG`, `DMAR_ECAP_REG`, global command/status registers, fault registers, invalidation queue registers, interrupt-remapping registers, PRQ registers, PerfMon registers, and enhanced command registers.
- Capability decoders: `cap_*()` and `ecap_*()` macros expose hardware features such as scalable mode, PASID, PRS, nested translation, snoop control, queued invalidation, interrupt remapping, superpages, fault register count, and address widths.
- `IOMMU_WAIT_OP()` is the common MMIO polling macro used by hardware command paths and panics on timeout.
- Queued invalidation structures and encodings include `struct qi_desc`, `struct q_inval`, `QI_*` descriptor types, status values, queue length, PRQ sizing, and descriptor-building helpers.
- Translation structures include `struct root_entry`, `struct context_entry`, `struct dma_pte`, and helpers such as `context_present()`, `context_set_present()`, `context_clear_present()`, `context_set_translation_type()`, `context_set_address_root()`, `context_set_domain_id()`, `dma_pte_addr()`, `dma_pte_present()`, and `dma_pte_superpage()`.
- Core state structs include `struct intel_iommu`, `struct dmar_domain`, `struct iommu_domain_info`, `struct device_domain_info`, `struct dev_pasid_info`, `struct iommu_pmu`, and `struct cache_tag`.
- Domain helpers include `to_dmar_domain()`, `domain_id_iommu()`, `iommu_domain_did()`, `intel_domain_is_fs_paging()`, and `intel_domain_is_ss_paging()`.
- Cross-file declarations expose DMAR/QI functions, domain attach/detach, PASID setup helpers, cache tag operations, PRQ/IOPF functions, SVM allocation, debugfs hooks, sysfs attribute groups, IOMMU ops, and enhanced command submission.

## Control Flow

This header does not execute a runtime flow by itself, but its inline helpers define the ordering and encodings used by runtime flows. Context entry setup generally clears or initializes fields, sets domain ID/address/translation type, performs a DMA write memory barrier, and then sets the present bit. Teardown clears the present bit with `context_clear_present()`, which includes a write barrier and documents the caller's obligation to perform the VT-d invalidation handshake.

Queued invalidation flow is encoded by helpers such as `qi_desc_iotlb()`, `qi_desc_dev_iotlb()`, `qi_desc_piotlb_all()`, `qi_desc_piotlb()`, and `qi_desc_dev_iotlb_pasid()`. `dmar.c` builds descriptors with these helpers, submits them with `qi_submit_sync()`, and interprets the `QI_FREE`, `QI_IN_USE`, `QI_DONE`, and `QI_ABORT` status array.

Domain/device flows use header-defined structs as shared state. `iommu.c` allocates and mutates `dmar_domain`, `device_domain_info`, and `dev_pasid_info`; `dmar.c` uses `intel_iommu` and QI fields for hardware control; debugfs reads the same structures for observability.

## State And Persistence

The header describes persistent state rather than owning it. `struct intel_iommu` persists per hardware remapping unit and contains MMIO addresses, capability registers, command shadow, locks, domain ID allocator, root table pointer, invalidation queue, PRQ/IOPF state, device rbtree, IRQ-remapping state, IOMMU core device, NUMA node, flags, DRHD backpointer, perf state, and PMU state. `struct dmar_domain` persists per IOMMU domain and tracks page-table implementation, attached IOMMUs, devices, PASIDs, cache tags, dirty tracking, force snooping, nested parent/child relationships, and SVA notifier state. `struct device_domain_info` persists per probed device and records BDF/segment, ATS/PASID/PRI state, IOPF reference count, IOMMU/domain pointers, PASID table, debugfs dentry, and RID rbtree node.

## Dependencies And Integration Points

The header includes Linux IOVA, IOMMU, IDR/IDA, MMU notifier, xarray, perf, PCI, bitfield, IO, generic page-table IOMMU, x86 IOMMU, and iommufd UAPI definitions. Conditional sections adapt to `CONFIG_IRQ_REMAP`, `CONFIG_INTEL_IOMMU`, `CONFIG_INTEL_IOMMU_SVM`, and `CONFIG_INTEL_IOMMU_DEBUGFS`. It imports PASID-related types by forward declaration and exposes hooks to PASID, SVM, nested, PRQ, debugfs, cache tag, and perf modules.

## Risks And Edge Cases

- Register and descriptor encodings are hardware ABI. Any incorrect bit definition can corrupt translation, fail invalidations, or mis-handle interrupts.
- `IOMMU_WAIT_OP()` panics on hardware timeout. Callers must use it only for operations where panic is the intended fail-stop behavior.
- Context field setters mostly OR fields into existing values. Callers are expected to clear entries first when reprogramming, or stale bits can remain.
- `context_set_present()` and `context_clear_present()` encode memory-order assumptions. Reordering these relative to cache flushes and invalidations is unsafe.
- `qi_desc_dev_iotlb_pasid()` warns on non-aligned invalidation addresses and encodes size by manipulating low address bits; off-by-one errors here directly affect TLB invalidation coverage.
- `device_rbtree_find()` declaration returns a device pointer without lifetime protection; callers must synchronize if release can race.
- Conditional stubs for disabled configs must preserve call-site semantics, especially for debugfs and SVM paths.

## Test Signals

Validation should include compile coverage across combinations of `CONFIG_INTEL_IOMMU`, `CONFIG_IRQ_REMAP`, `CONFIG_INTEL_IOMMU_SVM`, and `CONFIG_INTEL_IOMMU_DEBUGFS`; static assertions from `PT_IOMMU_CHECK_DOMAIN`; sparse/lockdep checks around inline synchronization assumptions; descriptor encoding tests or trace validation for IOTLB, DevTLB, PASID cache, page group response, and PRQ paths; and boot/runtime tests that read capability fields and confirm the driver programs expected register bits in legacy and scalable modes.
