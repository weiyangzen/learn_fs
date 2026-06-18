<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-iommu.h -->
# sources/distributed-fs/ceph-client/include/linux/omap-iommu.h

## Purpose
This header declares OMAP IOMMU context save/restore and domain activation controls for the OMAP virtual address-space management driver.

## Important APIs, types, and functions
With `CONFIG_OMAP_IOMMU`, it exports `omap_iommu_save_ctx()`, `omap_iommu_restore_ctx()`, `omap_iommu_domain_deactivate()`, and `omap_iommu_domain_activate()`. Disabled stubs no-op or return `-ENODEV`.

## Control flow
Power-management paths save and restore IOMMU hardware context around suspend or clock gating. Domain users can deactivate and reactivate an OMAP IOMMU domain around runtime changes.

## State and persistence
Persistent state is IOMMU hardware registers and domain mappings maintained by the OMAP IOMMU implementation. Header stubs intentionally preserve builds when hardware support is absent.

## Dependencies and integration points
It depends on `struct device`, `struct iommu_domain`, OMAP IOMMU driver code, PM flows, and generic IOMMU domain management.

## Risks and test signals
Risks include lost context across suspend, activating domains with stale mappings, callers ignoring `-ENODEV`, and ordering bugs with clocks/resets. Test OMAP IOMMU suspend/resume, domain deactivate/activate cycles, remote processor/media users, and disabled config compile paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-iommu.h -->
