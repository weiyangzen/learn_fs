# sources/distributed-fs/ceph-client/drivers/pci/setup-res.c

## Purpose
`setup-res.c` provides lower-level PCI resource operations for BAR and bridge-window assignment: programming config-space BARs, claiming resources in parent windows, falling back to firmware addresses, assigning and releasing resources, and enabling device decode bits.

## Important APIs, types, and functions
Important functions include `pci_update_resource()`, `pci_claim_resource()`, `pci_disable_bridge_window()`, weak `pcibios_retrieve_fw_addr()`, `pci_align_resource()`, weak `pcibios_align_resource()`, `pci_assign_resource()`, `pci_reassign_resource()`, `pci_release_resource()`, and `pci_enable_resources()`. Internal `pci_std_update_resource()` programs normal and ROM BARs, while `__pci_assign_resource()` and `_pci_assign_resource()` allocate from the device bus and transparent upstream bridges.

## Control flow and behavior
BAR update skips virtual-function BARs, unimplemented or unset resources, and fixed resources. It converts CPU resources to bus addresses, chooses the right BAR register, optionally disables memory decoding for non-atomic 64-bit BAR updates, writes low and high dwords, mirrors saved config space, verifies reads, and restores the command register.

Claiming finds a compatible parent resource, skips shadow ROMs, calls `request_resource_conflict()`, and marks conflicts or missing windows as `IORESOURCE_UNSET`. Assignment marks the resource unset, computes alignment, allocates from the best matching bridge window, falls back to the firmware address from `pcibios_retrieve_fw_addr()` if no space exists, clears unset/start-align flags, re-enables bridge windows, and updates config-space BARs for endpoint resources. Reassignment expands an already assigned resource; release detaches it from the resource tree and resets start/end to size form. Enabling validates requested required resources and sets `PCI_COMMAND_IO` or `PCI_COMMAND_MEMORY` only when claimed parents exist.

## State and persistence
The file mutates `struct resource` ranges, flags, and parent links, device command register decode bits, BAR registers, ROM enable bits, and `saved_config_space[]`. Firmware-address fallback depends on architecture-provided saved firmware BAR addresses.

## Dependencies and integration points
It is used heavily by `setup-bus.c`. It depends on resource-tree APIs, PCI config accessors, architecture `pcibios_*` hooks, SR-IOV update helpers, bridge-window helpers, and command-register semantics.

## Risks
Programming 64-bit BARs while decode remains enabled can briefly expose bad addresses, hence the decode-disable path. Misclassifying optional resources can allow devices to be enabled with missing required BARs. Firmware fallback on root buses assumes host bridges route all I/O or memory of the appropriate type.

## Test signals
Exercise 32-bit and 64-bit BARs, ROM BARs enabled and disabled, overlapping resources, missing parent bridge windows, transparent bridges, fixed resources, firmware fallback, SR-IOV VF BAR handling, and `pci_enable_resources()` failures for unset or unclaimed required BARs.
