<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/pci.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/pci.c

Purpose: provides Xtensa PCI resource alignment, bus fixup, and IO BAR mmap support. Important functions are `pcibios_align_resource`, `pcibios_fixup_bus`, and `pci_iobar_pfn`.

Control flow aligns IO resources to avoid low-10-bit aliasing with ISA-like devices, delegates memory resource alignment to generic PCI logic, reads bridge bases for subordinate buses, and adjusts VMA page offset for `/proc/bus/pci` IO BAR mappings using controller IO space offsets. Persistent state affected includes PCI resource assignments, bridge windows, and mmap VMA offsets. Dependencies include `asm/pci-bridge.h`, PCI core, resource flags, and platform controller data. Integration points are PCI enumeration, resource allocation, procfs PCI mmap, and device drivers. Risks are IO resource overlarge warnings without hard failure, bad controller `sysdata`, offset arithmetic errors, and legacy IO mirroring assumptions. Test signals include PCI enumeration/resource logs, devices behind bridges, procfs BAR mmap, and resource alignment inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/pci.c -->
