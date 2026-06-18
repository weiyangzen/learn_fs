<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_mcfg.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pci_mcfg.c

## Purpose
`pci_mcfg.c` parses the ACPI MCFG table and provides ECAM configuration-space resources for ACPI PCI roots. It also applies platform-specific quirks that replace generic ECAM operations or fabricate corrected config-space resource ranges for hardware whose MCFG description is incomplete or nonstandard.

## Important APIs, Types, and Functions
`struct mcfg_entry` stores parsed base address, segment, and bus range. With `CONFIG_PCI_QUIRKS`, `struct mcfg_fixup` matches OEM ID/table/revision, segment, and bus range to a `pci_ecam_ops` implementation and optional resource override. Public entry points are `pci_mcfg_lookup()` and `pci_mmcfg_late_init()`. Internal helpers include `pci_mcfg_parse()`, `pci_mcfg_apply_quirks()`, and `pci_mcfg_quirk_matches()`.

## Control Flow and State
Late init calls `acpi_table_parse()` for `MCFG`. The parser validates table length, allocates an array of entries, copies each allocation's segment/address/start/end bus values into `pci_mcfg_list`, and stores OEM identifiers for quirk matching. `pci_mcfg_lookup()` first honors root `_CBA` if present, otherwise searches parsed MCFG entries that cover the root's segment and bus resource. It builds a memory resource from base plus bus offset, applies quirks, rejects missing starts, and returns the final resource and ECAM ops.

## State and Persistence
The parsed `pci_mcfg_list` and saved OEM fields remain for the lifetime of the kernel. Per-root lookup may cache `root->mcfg_addr`. No userspace persistence exists; the state is boot firmware table interpretation.

## Dependencies and Integration Points
The file depends on ACPI table parsing, `struct acpi_pci_root`, PCI ECAM APIs, architecture-specific ECAM ops, resource helpers, and config-specific quirk tables for ARM64 and LoongArch. It feeds host-bridge creation paths that need a config-space resource.

## Risks and Test Signals
Risks include memory retained intentionally after init, quirks matching exact padded OEM strings/revisions, bus-range containment rejecting partial coverage, and incorrect fabricated resources causing config-space access faults. Test signals are MCFG detection logs, successful PCI config reads on quirked platforms such as ThunderX, X-Gene, Altra, Tegra194, Graviton, QDF2432, Loongson, and clean failure with `-ENXIO` when no valid ECAM base exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_mcfg.c -->
