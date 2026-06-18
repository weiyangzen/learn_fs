# Research: sources/distributed-fs/ceph-client/include/linux/pci-ecam.h

Purpose: `pci-ecam.h` defines Enhanced Configuration Access Mechanism address calculations, config-window data structures, generic ECAM operations, and platform quirk operation declarations.

Important APIs/types/functions: macros define ECAM bus, devfn, and register shifts/masks plus `PCIE_ECAM_OFFSET()`. `struct pci_ecam_ops` embeds `pci_ops` and optional init/enable/disable hooks. `struct pci_config_window` stores config resource, bus resource, mapping(s), ops, private data, and parent device. APIs include `pci_ecam_create()`, `pci_ecam_free()`, `pci_ecam_map_bus()`, and `pci_generic_ecam_ops`; ACPI quirk ops are declared for 32-bit access and known controllers.

Control flow and state: host bridge setup creates a config window from resources and ops, maps config-space memory, and uses `pci_ecam_map_bus()` to compute per-device config addresses. State persists as host bridge sysdata until bridge teardown.

Dependencies and integration points: depends on PCI core, kernel resources, platform devices, ACPI MCFG lookup, and architecture I/O memory mapping.

Risks and test signals: risks include incorrect bus shift, out-of-range register offsets, wrong 32-bit/per-bus mapping choice, and missing controller quirks. Tests should cover config reads/writes across bus/devfn/register ranges, ACPI MCFG quirk selection, resource teardown, and invalid bus resources.
