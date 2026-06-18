# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_quirks.h

## Purpose
`conf_space_quirks.h` declares pciback's dynamic configuration-space quirk interface.

## Important APIs, types, and functions
It defines `struct xen_pcibk_config_quirk`, containing list linkage, PCI device ID match data, and the associated `struct pci_dev`. It declares functions to add quirk fields, initialize quirks, free dynamic config fields, release a quirk, and test whether a field offset is already present.

## Control flow
The header itself has no runtime flow. Callers initialize per-device quirk records and add fields through the declared functions.

## State and persistence
The structure describes runtime quirk list entries. No state is stored by the header.

## Dependencies and integration points
It depends on Linux PCI and list definitions plus `struct config_field` from `conf_space.h` via users that include both. It is shared by quirk implementation and config-space setup code.

## Risks and test signals
Risks are declaration drift, missing include ordering for `struct config_field`, and mismatched quirk lifecycle assumptions. Test signals are pciback builds and dynamic quirk add/remove paths.
