# sources/distributed-fs/ceph-client/arch/powerpc/kernel/iomap.c

## Purpose
Provides the PowerPC implementation of simple I/O port mapping and PCI I/O unmap behavior.

## Important APIs, Types, And Functions
Exports `ioport_map` and, with PCI, `pci_iounmap`.

## Control Flow
`ioport_map` converts an I/O port number to an `__iomem` virtual address by adding `_IO_BASE`. `pci_iounmap` ignores addresses recognized as ISA or PCI I/O port windows and calls `iounmap` only for true MMIO mappings.

## State And Persistence
No owned state. The functions interpret existing global I/O mapping state such as `_IO_BASE`, ISA bridge mappings, and PCI host bridge I/O windows.

## Dependencies And Integration Points
Depends on `asm/io.h`, PCI bridge helpers, ISA bridge helpers, and generic PCI resource mapping code. It prevents generic PCI unmap from tearing down permanently mapped I/O port windows.

## Risks And Edge Cases
Incorrect classification of an address as I/O port versus MMIO can leak an ioremap or unmap a fixed I/O window. The simple `_IO_BASE` arithmetic assumes platform setup already established the I/O space mapping.

## Test Signals
Signals include PCI driver probe/remove paths using `pci_iomap`/`pci_iounmap`, legacy I/O port access, ISA bridge systems, and resource leak checks during repeated driver bind/unbind.
