# sources/distributed-fs/ceph-client/drivers/eisa/pci_eisa.c

## Purpose
`pci_eisa.c` discovers generic PCI-to-EISA bridge devices and registers a real EISA root device backed by the bridge bus IO resource.

## Important APIs, types, and functions
The file centers on the static `pci_eisa_root` and two init helpers: `pci_eisa_init()` enables a found PCI bridge and populates the EISA root, while `pci_eisa_init_early()` walks PCI devices looking for `PCI_CLASS_BRIDGE_EISA`.

## Control flow
At `subsys_initcall_sync` time, after PCI subsystem setup but before PNP/ISA probing, the driver scans all PCI devices. For each EISA bridge, it enables the device, finds the first IO resource on the parent PCI bus, initializes `struct eisa_root_device` with that resource, maximum slots, base address, and DMA mask, stores it as driver data, and calls `eisa_root_register()`.

## State and persistence behavior
State is a single static root object plus driver data on the PCI device. It reserves IO resources indirectly through `eisa_root_register()`. There is no persistent state.

## Dependencies and integration points
It depends on PCI enumeration, PCI class codes, EISA root registration from `eisa-bus.c`, and early init ordering relative to x86 PCI and PNP/ISA code.

## Risks and edge cases
The code assumes one useful PCI/EISA bridge root and only passes one IO resource because the EISA core supports a single IO range. Missing bus IO resources or failed `pci_enable_device()` abort registration. Returning `-1` instead of a more specific errno limits diagnostics. Init ordering is critical to avoid PNP claiming resources first.

## Test signals
Validate on PCI/EISA bridge hardware or emulation, PCI resource absence, multiple bridges, early boot ordering with PNP enabled, and successful EISA slot enumeration through the registered root.
