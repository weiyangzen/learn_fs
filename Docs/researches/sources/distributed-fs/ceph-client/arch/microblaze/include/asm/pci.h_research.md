# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pci.h

## Purpose

defines PCI DMA, resource, and pcibios policy hooks

## Important APIs, Types, and Functions

Source read size: 44 lines, 1025 bytes. Includes: `linux/types.h`, `linux/slab.h`, `linux/string.h`,
`linux/dma-mapping.h`, `linux/pci.h`, `linux/scatterlist.h`, `asm/io.h`, `asm/pci-bridge.h`. Defined
functions: `xilinx_pci_init`. Declared functions: `numbers`. Key macros/defines:
`__ASM_MICROBLAZE_PCI_H`, `PCIBIOS_MIN_IO`, `PCIBIOS_MIN_MEM`, `pcibios_assign_all_busses()`,
`HAVE_PCI_MMAP`, `ARCH_GENERIC_PCI_MMAP_RESOURCE`. Types visible in this file: `file`. External
symbols referenced/declared: `pci_domain_nr`, `pci_proc_domain`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
