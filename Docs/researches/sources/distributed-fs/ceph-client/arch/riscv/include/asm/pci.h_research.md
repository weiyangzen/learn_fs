<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/pci.h

## Purpose
Defines RISC-V PCI I/O and memory minimums, bus-to-node lookup, and generic PCI integration.

## Important APIs, Types, And Functions
types `pci_bus`; functions/prototypes `pcibus_to_node`; macros/constants `_ASM_RISCV_PCI_H`, `PCIBIOS_MIN_IO`, `PCIBIOS_MIN_MEM`, `cpumask_of_pcibus(bus) (pcibus_to_node(bus)`.

## Control Flow
Runtime flow is a wrapper sequence around MMIO or port-I/O reads and writes: optional fences bracket raw loads/stores, endian conversion is applied for CPU-visible values, and generic driver code calls the resulting accessors. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
No durable state is stored by the header. Accessors mutate device-visible MMIO state and rely on fences to preserve ordering against CPUs, DMA, and devices.

## Dependencies And Integration Points
Direct includes are `linux/types.h`, `linux/slab.h`, `linux/dma-mapping.h`, `asm/io.h`, `asm-generic/pci.h`. Integrates with driver MMIO APIs, PCI I/O space, generic `asm-generic/io.h`, DMA/noncoherent cache hooks, and RISC-V fence semantics.

## Risks And Edge Cases
Risks are missing fences, wrong endian conversion, noncoherent DMA cache omissions, and incorrect port/MMIO address translation, which can produce device data corruption or ordering bugs.

## Test Signals
Test signals include driver probe and DMA tests on coherent and noncoherent systems, PCI enumeration, MMIO ordering litmus tests, CBO cache-maintenance tests, and sparse/endian build checks.

Source read size: 33 lines, 728 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pci.h -->
