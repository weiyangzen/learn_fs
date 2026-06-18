<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_rimt.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi_rimt.h

## Purpose
`acpi_rimt.h` declares RISC-V ACPI RIMT IOMMU registration and per-device IOMMU configuration helpers.

## Important APIs, types, and functions
With `CONFIG_ACPI_RIMT`, `rimt_iommu_register()` registers an IOMMU device described by RIMT. With both `CONFIG_IOMMU_API` and `CONFIG_ACPI_RIMT`, `rimt_iommu_configure_id()` configures a device for a given ID. Disabled stubs return `-ENODEV`.

## Control flow
ACPI enumeration registers RIMT IOMMU devices, then device setup calls configure-by-ID to bind devices to the right IOMMU translation path.

## State and persistence behavior
Firmware-derived IOMMU registration and device/IOMMU bindings persist in the IOMMU core; the header stores no state.

## Dependencies and integration points
It integrates ACPI RIMT parsing with Linux device and IOMMU APIs, primarily for RISC-V ACPI systems.

## Risks and test signals
Risks include missing support being surfaced only as `-ENODEV`, incorrect ID binding, and mismatches between RIMT parsing and IOMMU API availability. Test signals include RISC-V ACPI IOMMU boot, device DMA tests, and config-matrix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_rimt.h -->
