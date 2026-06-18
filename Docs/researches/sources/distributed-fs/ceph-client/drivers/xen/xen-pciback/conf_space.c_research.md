# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space.c

## Purpose
`conf_space.c` implements Xen pciback's virtual PCI configuration space dispatcher. It intercepts guest config reads/writes, overlays selected fields, and blocks unsafe changes to real PCI resources unless explicitly allowed.

## Important APIs, types, and functions
Public functions are generated real-config accessors, `xen_pcibk_config_read`, `xen_pcibk_config_write`, `xen_pcibk_get_interrupt_type`, `xen_pcibk_config_free_dyn_fields`, `xen_pcibk_config_reset_dev`, `xen_pcibk_config_free_dev`, `xen_pcibk_config_add_field_offset`, `xen_pcibk_config_init_dev`, and `xen_pcibk_config_init`. `xen_pcibk_permissive` is a module parameter. It operates on `struct config_field` and `struct config_field_entry` lists stored in `struct xen_pcibk_dev_data`.

## Control flow
Device initialization creates a config-field list, adds header fields, capability fields, and quirk entries. Reads first read the real PCI config value, then merge any overlapping virtual fields into the returned value. Writes walk overlapping fields, read the virtual field value, merge the guest write, and call field-specific write callbacks. Unhandled writes are ignored with a warning unless device or module permissive mode allows direct writes. Reset/free paths call field callbacks and release list entries.

## State and persistence
Per-device state is the config field list and callback data owned by `xen_pcibk_dev_data`. The global permissive flag affects all devices at runtime. PCI config writes change hardware state when allowed, but the overlay itself is in memory only.

## Dependencies and integration points
It depends on Linux PCI config accessors, `pciback.h`, `conf_space.h`, and quirks/header/capability providers. It integrates with pciback operation handling that services frontend PCI config-space requests.

## Risks and test signals
Risks include incorrect overlap merging for partial reads/writes, duplicate field handling, permissive-mode safety, interrupt type detection when qemu bypasses MSI helpers, callback data lifetime, and mapping PCIBIOS errors to Xen ABI values. Test signals include guest config reads/writes of BARs, command register, MSI/MSI-X, unaligned invalid requests, permissive toggles, reset/free cycles, and frontend PCI passthrough boot tests.
