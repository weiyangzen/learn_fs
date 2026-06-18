<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/io.h

## Purpose
Defines RISC-V I/O-space limits, ioremap wrappers, and ordered string I/O accessors.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_IO_H`, `IO_SPACE_LIMIT`, `PCI_IOBASE`, `ioremap_wc(addr, size)`, `__io_pbr() RISCV_FENCE(io, i)`, `__io_par(v) RISCV_FENCE(i, ior)`, `__io_pbw() RISCV_FENCE(iow, o)`, `__io_paw() RISCV_FENCE(o, io)`, `__io_reads_ins(port, ctype, len, bfence, afence)`, `__io_writes_outs(port, ctype, len, bfence, afence)`, `readsb(addr, buffer, count) __readsb(addr, buffer, count)`, `readsw(addr, buffer, count) __readsw(addr, buffer, count)`, `readsl(addr, buffer, count) __readsl(addr, buffer, count)`, `insb(addr, buffer, count) __insb(PCI_IOBASE + (addr), buffer, count)`, plus 13 more.

## Control Flow
Runtime flow is a wrapper sequence around MMIO or port-I/O reads and writes: optional fences bracket raw loads/stores, endian conversion is applied for CPU-visible values, and generic driver code calls the resulting accessors. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
No durable state is stored by the header. Accessors mutate device-visible MMIO state and rely on fences to preserve ordering against CPUs, DMA, and devices.

## Dependencies And Integration Points
Direct includes are `linux/types.h`, `linux/pgtable.h`, `asm/mmiowb.h`, `asm/early_ioremap.h`, `asm/mmio.h`, `asm-generic/io.h`. Integrates with driver MMIO APIs, PCI I/O space, generic `asm-generic/io.h`, DMA/noncoherent cache hooks, and RISC-V fence semantics.

## Risks And Edge Cases
Risks are missing fences, wrong endian conversion, noncoherent DMA cache omissions, and incorrect port/MMIO address translation, which can produce device data corruption or ordering bugs.

## Test Signals
Test signals include driver probe and DMA tests on coherent and noncoherent systems, PCI enumeration, MMIO ordering litmus tests, CBO cache-maintenance tests, and sparse/endian build checks.

Source read size: 147 lines, 5424 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/io.h -->
