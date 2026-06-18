<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig-shared.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig-shared.c

## Purpose
`mmconfig-shared.c` is the common x86 ECAM/MMCONFIG discovery, validation, resource, and hotplug-management layer. It builds the global list of PCI ECAM regions from known hostbridge probes, ACPI MCFG, and hotplug `_CBA` inputs, validates reservation ownership, and invokes architecture-specific map/unmap backends.

## Important APIs, types, and functions
Primary APIs are `pci_mmconfig_add()`, `pci_mmconfig_lookup()`, `pci_mmcfg_early_init()`, `pci_mmcfg_late_init()`, `pci_mmconfig_insert()`, and `pci_mmconfig_delete()`. Internal helpers allocate sorted `struct pci_mmcfg_region` entries, probe Intel E7520/945, AMD Fam10h, NVIDIA MCP55, parse ACPI MCFG, validate E820/ACPI/EFI reservations, reject broken ECAM regions, insert resources at late init, and optionally provide an APEI address filter.

## Control flow
Early init runs if `PCI_PROBE_MMCONF` is enabled. It prefers known hostbridge probes, otherwise parses ACPI MCFG, rejects unreserved/broken regions, sets `pcibios_last_bus` if needed, and calls `pci_mmcfg_arch_init()`. Late init retries ACPI parsing after more infrastructure is available when early config access did not fully select ECAM. `late_initcall()` inserts ECAM resources into `iomem_resource`. Hostbridge hotplug calls `pci_mmconfig_insert()` to validate, map, insert, and publish new regions under lock; deletion removes them with RCU synchronization.

## State and persistence behavior
Global state includes `pci_mmcfg_list`, `pci_mmcfg_lock`, `pci_mmcfg_running_state`, `pci_mmcfg_arch_init_failed`, and `known_bridge`. Region entries persist resource names, physical ranges, segment/bus ranges, and architecture-private mappings. Lookup uses RCU-compatible list traversal.

## Dependencies and integration points
It depends on ACPI table/resource parsing, EFI memory descriptors, E820 reservation checks, raw PCI config access for hostbridge probes, resource insertion, APEI filtering, and arch-specific files `mmconfig_32.c`/`mmconfig_64.c`/platform overrides.

## Risks and edge cases
Firmware MCFG ranges are often malformed, overlapping, too large, above 4GB on old systems, or not reserved in ACPI resources. Early validation cannot use the ACPI interpreter, so it relies on DMI age and E820 only for older systems. Hotplug insertion must avoid duplicates, invalid bus ranges, conflicting resources, failed mappings, and concurrent readers.

## Test signals
Boot with `pci=nommconf`, ACPI MCFG-only systems, known Intel/AMD/NVIDIA hostbridges, EFI MMIO-backed ECAM, hot-added host bridges, APEI error injection, and resource conflict scenarios. Logs should show ECAM ranges, reservation source, size reductions, and map failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig-shared.c -->
