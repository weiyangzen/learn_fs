# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/ops-dreamcast.c



Source read size: 79 lines, 2501 bytes.



Purpose: PCI config-space operations for the Dreamcast GAPSPCI bridge and Broadband Adapter.

Important APIs/types/functions: `gapspci_pci_ops`, `gapspci_read()`, `gapspci_write()`, and `gapspci_config_access()`.

Control flow: accepts only bus 0/devfn 0, reads or writes byte/word/dword config values directly through GAPSPCI BBA config I/O offsets, and returns device-not-found for all other targets.

State and persistence: no local state; all effects are GAPSPCI config-space I/O.

Dependencies and integration points: used by `pci-dreamcast.c` host controller registration and Dreamcast PCI fixups.

Risks and test signals: assumes a single device and no type-1 config cycles; accidental extra devfn access is hidden as not found. Test BBA enumeration and config read/write sizes.
