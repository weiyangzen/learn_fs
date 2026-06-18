<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_iommu.h -->
# sources/distributed-fs/ceph-client/include/linux/of_iommu.h

## Purpose
This header declares OF helpers for configuring IOMMU mappings and reserved regions for devices described by Devicetree.

## Important APIs, types, and functions
With `CONFIG_OF_IOMMU`, it exports `of_iommu_configure()` and `of_iommu_get_resv_regions()`. Disabled builds return `-ENODEV` or no-op. Forward declarations cover `struct device`, `struct device_node`, and `struct iommu_ops`.

## Control flow
Device setup calls `of_iommu_configure()` with the master node and optional requester ID, allowing OF IOMMU specifiers to attach the device to an IOMMU domain. Later, reserved regions are appended to a list with `of_iommu_get_resv_regions()`.

## State and persistence
The header holds no state. IOMMU domain attachment, device links, and reserved-region lists are maintained by IOMMU core/provider code.

## Dependencies and integration points
It integrates OF phandle specifiers with the IOMMU core, DMA configuration, bus setup, and reserved-memory/identity-mapping policy.

## Risks and test signals
Risks include interpreting requester IDs incorrectly, missing reserved regions, failing open in disabled builds, and probe deferral loops when IOMMU providers are unavailable. Test devices with `iommus` properties, multi-ID masters, reserved region enumeration, DMA configuration interaction, provider deferral, and `!CONFIG_OF_IOMMU` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_iommu.h -->
