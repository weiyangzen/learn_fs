<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_iort.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi_iort.h

## Purpose
`acpi_iort.h` declares ACPI IORT helpers for MSI mapping, ITS translation, IOMMU configuration, reserved memory regions, PMCG metadata, and domain-token lookup.

## Important APIs, types, and functions
Macros extract IORT IRQ number/trigger fields and define SMMUv3 PMCG model IDs. Token APIs include `iort_register_domain_token()`, deregister/find, and `iort_iwb_handle()`. With `CONFIG_ACPI_IORT`, it declares MSI ID mapping/translation, ITS physical address translation, device IRQ domain lookup, PMSI info, PMSI domain configuration, RMR SID list handling, DMA range lookup, IOMMU configure-by-ID, reserved-region enumeration, and max CPU address lookup. Disabled stubs preserve identity IDs or return no support.

## Control flow
During ACPI enumeration, IORT tables map requester IDs to interrupt controllers and IOMMUs. Device setup calls into these helpers to configure MSI domains, IOMMU fwnodes, DMA limits, and reserved memory regions.

## State and persistence behavior
Domain tokens and parsed IORT relationships are firmware-derived kernel state. RMR SID lists are caller-managed list state populated from table data.

## Dependencies and integration points
The header depends on ACPI, fwnode, irqdomain, IOMMU, MSI, and device core concepts. It is central for arm64 ACPI PCI/platform device DMA and interrupt routing.

## Risks and test signals
Risks include identity fallback masking missing IORT support, incorrect requester-ID translation, broken reserved-region propagation, and DMA limit errors. Test signals include ACPI IORT boot on SMMU systems, MSI delivery, IOMMU group setup, reserved memory tests, PMCG driver probe, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_iort.h -->
