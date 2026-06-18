<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pci.h

## Purpose
Defines Xtensa PCI architecture constants and mmap capabilities.

## Important APIs, Types, And Functions
Defines `pcibios_assign_all_busses`, `PCIBIOS_MIN_IO`, `PCIBIOS_MIN_MEM`, `HAVE_PCI_MMAP`, `ARCH_GENERIC_PCI_MMAP_RESOURCE`, and `arch_can_pci_mmap_io`.

## Control Flow
No runtime flow. Generic PCI code uses these constants to allocate resources and allow user mappings.

## State And Persistence
No owned state; PCI core owns resources and mappings.

## Dependencies And Integration Points
Depends on generic PCI, scatterlist, slab/string helpers, and Xtensa I/O mapping.

## Risks And Edge Cases
Minimum IO/MEM resource assumptions may be wrong for unusual boards. PCI memory is assumed to equal physical memory address space for bounce-buffer decisions.

## Test Signals
Build PCI-enabled Xtensa, enumerate devices, mmap PCI resources from userspace, and validate IO/MEM BAR allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/pci.h -->
