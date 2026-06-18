<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_viot.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi_viot.h

## Purpose
`acpi_viot.h` declares ACPI VIOT initialization and virtio-IOMMU configuration helpers.

## Important APIs, types, and functions
With `CONFIG_ACPI_VIOT`, it exposes `acpi_viot_early_init()`, `acpi_viot_init()`, and `viot_iommu_configure()`. Disabled builds provide no-op init functions and `viot_iommu_configure()` returning `-ENODEV`.

## Control flow
Boot code performs early and normal VIOT parsing. Device setup calls `viot_iommu_configure()` to attach devices to virtio-IOMMU topology described by ACPI.

## State and persistence behavior
Parsed VIOT topology and IOMMU mappings persist in ACPI/IOMMU core state. This header only declares the interface.

## Dependencies and integration points
It depends on `linux/acpi.h` and device declarations. Integration points are ACPI boot, virtio-IOMMU setup, and device DMA configuration.

## Risks and test signals
Risks include early/late init ordering problems, `-ENODEV` paths in generic callers, and incorrect device-to-IOMMU mapping. Test signals include ACPI VIOT boot, virtio-IOMMU DMA tests, and builds without VIOT support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_viot.h -->
