<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-priv.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommu-priv.h

Purpose: private IOMMU core header shared inside `drivers/iommu`. It exposes internal helpers for device ops, fwspec, bus registration, mock devices, attach handles, iommufd MSI helpers, device PASID replacement, and debug pagealloc wrappers.

Important APIs/types/functions: `dev_iommu_ops()`, `dev_iommu_free()`, `iommu_ops_from_fwnode()`, `iommu_fwspec_ops()`, `iommu_fwspec_free()`, `iommu_device_register_bus()`, `iommu_device_unregister_bus()`, `iommu_mock_device_add()`, attach-handle helpers, `iommufd_sw_msi()`, `iommu_replace_device_pasid()`, and `iommu_debug_map/unmap_begin/unmap_end/init()` wrappers.

Control flow: internal code includes this header to access device-owned IOMMU ops after probe, manage firmware specs and attach handles, or call debug hooks without sprinkling config ifdefs. Debug wrappers branch on the static key only when `CONFIG_IOMMU_DEBUG_PAGEALLOC` is enabled; otherwise they compile away.

State and persistence: no state here except references to external static key/debug functions. It defines internal contracts for persistent core objects such as `dev_iommu`, `iommu_fwspec`, groups, domains, and attach handles.

Dependencies and integration: used by generic IOPF, SVA, debug pagealloc, and IOMMU core code. Depends on public `linux/iommu.h`, MSI types, and optional iommufd/IRQ MSI support.

Risks: `dev_iommu_ops()` trusts that probe installed valid ops, so misuse before probe would dereference invalid state. This is private API; external drivers should not depend on it. Conditional stubs must preserve semantics across config combinations.

Test signals: all IOMMU core build configs, attach-handle PASID routing, iommufd MSI enabled/disabled builds, debug pagealloc enabled/disabled runtime, and mock device tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-priv.h -->
