# sources/distributed-fs/ceph-client/arch/x86/pci/common.c

## Purpose
Provides common x86 PCI glue: global probing flags, raw config access dispatch, root bus ops, config-space locking, DMI boot quirks, command-line `pci=` parsing, root scanning without ACPI, cacheline setup, resource fixups, MSI domain initialization, device enable/disable hooks, and VMD DMA-device resolution.

## Important APIs, variables, and functions
- Globals include `pci_probe`, `pci_routeirq`, `noioapicquirk`, `noioapicreroute`, `pcibios_last_bus`, `pirq_table_addr`, `raw_pci_ops`, `raw_pci_ext_ops`, and `pci_config_lock`.
- `raw_pci_read()` and `raw_pci_write()` dispatch to base or extended raw config ops.
- `pci_root_ops` exposes PCI core config access callbacks.
- `dmi_check_skip_isa_align()` and `dmi_check_pciprobe()` apply DMI quirks for ISA alignment skipping, breadth-first sorting, bus renumbering, and scanning all PCIe devices.
- `pcibios_fixup_bus()` reads bridge bases and applies BAR/ROM assignment policy.
- `pcibios_scan_root()` creates a non-ACPI root bus using `x86_pci_root_bus_node()` and `x86_pci_root_bus_resources()`.
- `pcibios_set_cache_line_size()` sets default PCI cacheline size from CPU data.
- `pcibios_init()` surveys resources and optionally sorts devices breadth-first.
- `pcibios_setup()` parses many `pci=` options and updates global flags.
- `pcibios_device_add()` attaches setup ROM info and initializes MSI domain.
- `pcibios_enable_device()`, `pcibios_disable_device()`, `pcibios_release_device()`, `pci_ext_cfg_avail()`, and `pci_real_dma_dev()` provide arch hooks.

## Control flow
Raw config requests from the PCI core enter `pci_root_ops`, which call `raw_pci_read/write()`. During boot, DMI checks and command-line parsing shape `pci_probe`. PCI root scanning either occurs through ACPI or `pcibios_scan_root()`, which allocates `pci_sysdata`, retrieves fallback resources, scans the bus, and adds devices. `pcibios_init()` runs after raw config backends are selected and performs cacheline/resource setup. Device add/enable hooks run during enumeration and driver binding.

## State and persistence
Most state is global and boot-lifetime: probe bitmasks, raw ops pointers, IRQ policy flags, last bus, PIRQ table address, and config lock. Per-root `pci_sysdata` allocations persist with root buses. Device-specific ROM metadata and MSI domain pointers are stored on `struct pci_dev`/device objects.

## Dependencies and integration points
Depends on the PCI core, ACPI PCI bus hooks, DMI, setup_data boot parameters, x86 IRQ domains, VMD helpers, raw backends from `direct.c`, MMCONFIG/BIOS backends, and resource survey code from other x86 PCI files. It is the central junction for many files in this directory.

## Risks and edge cases
Command-line flags can disable or force probing modes, so interactions between BIOS, direct, MMCONFIG, ACPI, ROM/BAR assignment, and IRQ routing must remain coherent. Raw config dispatch only uses `raw_pci_ops` for domain 0 and registers below 256; extended/nonzero-domain access requires `raw_pci_ext_ops`. Setup ROM scanning maps boot memory and must unmap every record. MSI domain selection must preserve special domains such as VMD.

## Test signals
Boot matrix testing with `pci=off`, `conf1`, `conf2`, `nommconf`, `assign-busses`, `routeirq`, `nobar`, `norom`, CRS/E820 flags, and DMI-quirked systems is useful. Check root resources, cacheline size logs, raw config availability, MSI domain assignment, ROM setup data attachment, and device enable/disable IRQ behavior.
