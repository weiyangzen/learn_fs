# sources/distributed-fs/ceph-client/drivers/edac/edac_pci.h

## Purpose
This header defines the EDAC PCI controller data model and public API used by EDAC PCI core code and chipset drivers that want PCI parity/error reporting.

## Important APIs and Types
`struct edac_pci_counter` stores parity and non-parity atomic counters. `struct edac_pci_ctl_info` holds list linkage, numeric index, op state, delayed work, optional polling callback, owning device, module/controller/device names, private data, start time, sysfs name, counters, and kobject. Inline helpers `pci_write_bits8()`, `pci_write_bits16()`, and `pci_write_bits32()` read-modify-write PCI config registers with a mask. Exported constructor/destructor and registration APIs are declared at the bottom.

## Control Flow
The header defines how low-level users interact with the implementation: allocate control info, fill fields, optionally provide `edac_check`, add it to EDAC, later delete and release it. The `to_edac_pci_ctl_work()` macro maps delayed work back to the owning controller.

## State and Persistence
No state is created here, but the struct layout defines all persistent in-kernel controller state for EDAC PCI instances. Counters persist while the kobject-backed controller exists and are exposed through sysfs by `edac_pci_sysfs.c`.

## Dependencies and Integration
The header depends on kernel device, kobject, list, PCI, type, and workqueue headers plus `linux/edac.h`. It is compiled only partly under `CONFIG_PCI`; PCI-specific data structures and write helpers are excluded for non-PCI builds.

## Risks
The masked write helpers do not check return values from PCI config reads or writes, matching common low-level kernel style but hiding transient config access failures. Callers must initialize all naming and device fields before registration because sysfs and logs use them immediately.

## Test Signals
Build tests should cover PCI and non-PCI configurations. Runtime validation should verify masked PCI writes preserve unmasked bits and that controller fields appear correctly in sysfs/log output after registration.
