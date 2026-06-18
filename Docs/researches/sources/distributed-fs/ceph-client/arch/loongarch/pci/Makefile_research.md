<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/pci/Makefile -->
## sources/distributed-fs/ceph-client/arch/loongarch/pci/Makefile

### Purpose
This Makefile selects LoongArch PCI architecture support objects.

### Important APIs, Types, And Functions
Rules are `obj-y += pci.o` and `obj-$(CONFIG_ACPI) += acpi.o`.

### Control Flow
`pci.o` is always built for this directory; ACPI PCI root scanning support is conditional on `CONFIG_ACPI`.

### State, Persistence, And Dependencies
No runtime state exists. Dependencies are Kbuild and `CONFIG_ACPI`.

### Integration Points
Controls inclusion of generic PCI hooks and ACPI ECAM/root-bridge support.

### Risks
Wrong object selection can break PCI enumeration or introduce ACPI dependencies into non-ACPI builds.

### Test Signals
Cross-build LoongArch PCI configs with and without ACPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/pci/Makefile -->
