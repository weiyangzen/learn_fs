# sources/distributed-fs/ceph-client/arch/x86/pci/acpi.c

## Purpose
Integrates ACPI PCI root discovery with x86 PCI bus scanning, IRQ routing, NUMA node selection, host bridge resource windows, and MMCFG/ECAM setup. It decides whether to trust ACPI `_CRS`, whether to clip host bridge windows with E820 reservations, and how to treat removable/tunneled PCIe devices behind Thunderbolt/USB4 paths.

## Important APIs, types, and functions
- Local `struct pci_root_info` wraps `struct acpi_pci_root_info`, `struct pci_sysdata`, and optional MMCFG tracking fields.
- Global policy flags are `pci_use_e820`, `pci_use_crs`, and `pci_ignore_seg`.
- `pci_acpi_crs_quirks()` applies BIOS-year heuristics, DMI quirks, and `pci=` command-line overrides for `_CRS` and E820 clipping policy.
- `arch_pci_dev_is_removable()` classifies external/tunneled PCIe devices using root-port external-facing state, USB4 host-interface properties, and known Intel Thunderbolt root-port IDs.
- `setup_mcfg_map()` and `teardown_mcfg_map()` insert/delete ACPI root ECAM ranges when `CONFIG_PCI_MMCONFIG` is enabled.
- `pci_acpi_root_get_node()` resolves NUMA node from ACPI `_PXM`, with fallback to hardware-probed `x86_pci_root_bus_node()`.
- `pci_acpi_root_prepare_resources()` gathers ACPI root resources, filters config-space IO ports, or falls back to hardware-probed/default resources when `_CRS` is ignored.
- `pci_acpi_scan_root()` creates or updates root buses via `acpi_pci_root_create()`.
- `pcibios_root_bridge_prepare()` attaches ACPI companions to root bridges.
- `pci_acpi_init()` installs ACPI IRQ routing callbacks.

## Control flow
Early ACPI PCI setup first calls `pci_acpi_crs_quirks()` to set policy. Root scan enters `pci_acpi_scan_root()`, which handles ignored segments, rejects unsupported multiple domains, reuses an existing bus or allocates `pci_root_info`, and delegates bus creation to ACPI PCI root ops. Root ops call `setup_mcfg_map()` during init, `pci_acpi_root_prepare_resources()` before bus creation, and `teardown_mcfg_map()` on release. After scanning, child PCIe buses are configured. IRQ init later binds `pcibios_enable_irq`/`pcibios_disable_irq` to ACPI routing and optionally routes all existing devices for `pci=routeirq`.

## State and persistence
The file maintains global policy flags and per-root `pci_root_info` allocations owned by ACPI root lifecycle callbacks. MMCFG ranges inserted for an ACPI root are tracked by `mcfg_added`, `start_bus`, and `end_bus` so teardown can delete only ranges this root added. Bus `sysdata` persists domain, node, and ACPI companion pointers.

## Dependencies and integration points
Depends on ACPI PCI root APIs, DMI matching, x86 NUMA helpers, `bus_numa.c` fallback resources, MMCONFIG insertion/deletion, PCI core resource lists, firmware node properties, PCIe topology helpers, and ACPI IRQ routing. It integrates with `common.c` through `pci_root_ops`, global `pci_probe` command-line flags, `pci_routeirq`, and `pcibios_*` hooks.

## Risks and edge cases
Firmware defects dominate the risk surface: bad `_CRS`, bogus E820 reservations, missing `_PXM`, broken `_SEG`, and incomplete USB4 host-interface properties. Incorrect `_CRS` policy can either hide usable windows or allocate into reserved host-bridge space. MMCFG failures are tolerated for segment zero but fatal for nonzero segments because extended config access may be impossible. Removable-device classification has topology exceptions for discrete Thunderbolt/USB4 controllers directly under external-facing root ports.

## Test signals
Boot logs should show whether ACPI host bridge windows and E820 reservations are used or ignored. Validate root bus domains/nodes/resources, ECAM access, Thunderbolt/USB4 hotplug classification, ACPI IRQ routing, and `pci=use_crs`, `pci=nocrs`, `pci=use_e820`, `pci=no_e820`, and DMI quirk behavior. Regressions often appear as missing devices, failed BAR assignment, broken hotplug, or no extended config space.
