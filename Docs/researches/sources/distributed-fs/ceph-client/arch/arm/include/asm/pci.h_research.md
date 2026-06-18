# sources/distributed-fs/ceph-client/arch/arm/include/asm/pci.h

## Purpose
Declares ARM PCI host-bridge integration constants and helpers for resource mapping and optional I/O remapping.

## Important APIs, Types, And Functions
Key declarations include extern unsigned long pcibios_min_io;; extern unsigned long pcibios_min_mem;; static inline int pci_proc_domain(struct pci_bus *bus); extern void pcibios_report_status(unsigned int status_mask, int warn);. Important macros/constants include ASMARM_PCI_H, PCIBIOS_MIN_IO, PCIBIOS_MIN_MEM, pcibios_assign_all_busses(), HAVE_PCI_MMAP, ARCH_GENERIC_PCI_MMAP_RESOURCE. It depends directly on #include <asm/mach/pci.h> /* for pci_sys_data */.

## Control Flow
PCI core code uses the arch hooks during bus scan, resource setup, and mmap of PCI memory to userspace.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/mach/pci.h> /* for pci_sys_data */.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
