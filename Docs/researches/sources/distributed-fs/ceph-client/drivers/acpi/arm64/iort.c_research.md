# sources/distributed-fs/ceph-client/drivers/acpi/arm64/iort.c

## Purpose
Implements ARM64 ACPI I/O Remapping Table parsing. It creates SMMU/PMCG platform devices, maps device IDs through IORT topology, configures MSI and IOMMU domains, exposes RMR reserved regions, and provides DMA address limits.

## Important APIs, Types, And Functions
Important exports include `iort_register_domain_token()`, `iort_deregister_domain_token()`, `iort_find_domain_token()`, `iort_msi_map_id()`, `iort_msi_xlate()`, `iort_its_translate_pa()`, `iort_pmsi_get_msi_info()`, `iort_get_device_domain()`, `iort_iwb_handle()`, `acpi_configure_pmsi_domain()`, `iort_iommu_get_resv_regions()`, `iort_get_rmr_sids()`, `iort_put_rmr_sids()`, `iort_iommu_configure_id()`, `iort_dma_get_ranges()`, `acpi_iort_init()`, and optionally `acpi_iort_dma_get_max_cpu_address()`.

## Control Flow
Initialization obtains IORT and walks nodes. SMMU, SMMUv3, and PMCG nodes receive static fwnodes, platform resources, platform data, optional DMA setup, MSI domains, and platform device registration. Runtime lookup maps ACPI named components, IWB devices, or PCI root complexes to IORT nodes, walks ID mappings with overlap workarounds, locates ITS/SMMU parents, and configures MSI or IOMMU fwspecs. RMR code scans RMR nodes for matching SIDs and builds IOMMU reserved regions.

## State And Persistence
State includes the permanent IORT table pointer, spinlock-protected IORT-node-to-fwnode list, spinlock-protected ITS MSI chip token list, and platform devices. Device IOMMU fwspecs, MSI domains, software node properties, DMA masks, and reserved-region lists are persistent device-model state.

## Dependencies And Integration Points
Integrates ACPI IORT, PCI, IRQ domains/ITS, IOMMU API, ARM SMMU and PMCG drivers, platform devices, ACPI fwnodes, DMA ops, NUMA proximity, and PCI ACS.

## Risks
Risks include malformed node lengths/references, ID mapping off-by-one firmware ambiguity, NULL output references, duplicate/conflicting mappings, missing fwnodes, unavailable SMMU drivers causing probe defer, RMR overlap/alignment issues, PCI firmware configuration not preserved for RMR SIDs, and partial platform-device setup leaks.

## Test Signals
Test node scanning bounds, PCI and named-component matching, MSI ID translation and ITS token lookup, platform MSI domain assignment, IOMMU fwspec setup for aliases, ATS/CANWBS flags, RMR reserved-region generation, SMMU/PMCG resource creation, ACS request, DMA limit extraction, and bad firmware warnings.
