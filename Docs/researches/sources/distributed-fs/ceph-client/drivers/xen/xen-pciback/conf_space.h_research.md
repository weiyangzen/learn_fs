# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space.h

## Purpose
`conf_space.h` defines the virtual PCI configuration-space field abstraction used by Xen pciback.

## Important APIs, types, and functions
It defines callback typedefs for field init/reset/free/read/write operations, `struct config_field`, `struct config_field_entry`, interrupt-type constants, `xen_pcibk_permissive`, and the `OFFSET` macro. Inline helpers add one field, an array of fields, or offset-adjusted fields. It declares real config accessors, capability/header initialization, and interrupt-type detection.

## Control flow
The header's inline add helpers iterate sentinel-terminated field arrays and call `xen_pcibk_config_add_field_offset`. Actual control flow is implemented in the C files.

## State and persistence
The structures describe runtime per-device field list entries and per-field private data. No state is stored in the header itself.

## Dependencies and integration points
It depends on Linux lists and errno helpers and is shared by `conf_space.c`, header/capability/quirk modules, and pciback code.

## Risks and test signals
Risks include field array sentinel mistakes, callback signature drift, size/read/write union misuse, and offset arithmetic errors. Test signals are compile coverage, config-field registration tests, and pciback config-space operations crossing field boundaries.
