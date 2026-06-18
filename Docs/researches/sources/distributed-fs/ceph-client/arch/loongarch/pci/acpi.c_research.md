<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/pci/acpi.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/pci/acpi.c

### Purpose
`acpi.c` implements LoongArch ACPI PCI root scanning, ECAM config-window setup, resource preparation, NUMA node assignment, and root-info cleanup.

### Important APIs, Types, And Functions
It defines `struct pci_root_info` and functions `pcibios_add_bus()`, `pcibios_root_bridge_prepare()`, `acpi_pci_bus_find_domain_nr()`, `pci_acpi_scan_root()`, plus helpers `acpi_release_root_info()`, `acpi_prepare_root_resources()`, `arch_pci_ecam_create()`, and `pci_acpi_setup_ecam_mapping()`.

### Control Flow
Root scan allocates `pci_root_info` and ops, maps ECAM from MCFG or Loongson defaults, assigns release/resource/pci ops, reuses an existing bus if found or creates one through `acpi_pci_root_create()`, claims/preserves resources when requested, assigns unassigned resources, and configures child bus settings. Resource prep probes ACPI windows and, when the `PCIH` method is absent, extends memory resources with high address bits from `mcfg_addr`. Custom ECAM creation reserves iomem, maps config space, calls ops init, and cleans up on conflicts/errors.

### State, Persistence, And Dependencies
State includes allocated root info, ECAM mappings, iomem resource reservations, PCI bus `sysdata`, ACPI companions, NUMA node assignment, and resource lists. Dependencies include ACPI PCI root support, PCI ECAM ops, Loongson default ECAM ops/addressing, NUMA `pa_to_nid()`, and generic PCI resource assignment.

### Integration Points
Generic ACPI PCI calls `pci_acpi_scan_root()`. `pci.c` supplies `mcfg_addr_init()` and default Loongson PCI behavior. Device drivers rely on resulting PCI buses, resources, IRQ/MSI domains, and config-space ops.

### Risks
MCFG fallback address construction and nonstandard `bus_shift` handling are platform-sensitive. Resource high-bit adjustment can produce wrong host windows if ACPI firmware methods are misread. Cleanup must free ops and ECAM mappings on all failure paths.

### Test Signals
Boot ACPI LoongArch systems with standard/nonstandard MCFG, enumerate PCIe devices, inspect `/proc/iomem`, run hotplug/resource reassignment tests, and validate NUMA node placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/pci/acpi.c -->
