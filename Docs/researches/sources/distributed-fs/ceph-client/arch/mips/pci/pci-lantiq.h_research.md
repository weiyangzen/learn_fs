## sources/distributed-fs/ceph-client/arch/mips/pci/pci-lantiq.h

### Purpose
This header defines the shared contract between the Lantiq PCI platform driver and its config-space access implementation.

### Important APIs, Types, And Functions
It declares the global config mapping `ltq_pci_mapped_cfg` and the config access callbacks `ltq_pci_read_config_dword()` and `ltq_pci_write_config_dword()`.

### Control Flow
No control flow exists here. The declarations allow `pci-lantiq.c` to build a `struct pci_ops` before the functions are linked from the low-level operations file.

### State, Persistence, And Dependencies
`ltq_pci_mapped_cfg` must be initialized by `ltq_pci_probe()` before any config operations are used. The header depends on Linux PCI type declarations through including translation units.

### Integration Points
It connects Lantiq device-tree probing and generic PCI enumeration with config-space read/write routines.

### Risks
If config ops run before probe maps `ltq_pci_mapped_cfg`, config cycles will dereference an invalid mapping. The function names imply dword access even though PCI core may request byte and word sizes.

### Test Signals
A successful boot should show config reads after resource mapping, and build tests should catch missing ops definitions.
