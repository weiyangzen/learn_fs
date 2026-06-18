<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmiowb.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmiowb.h

## Purpose
Defines RISC-V MMIO write barrier behavior.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_MMIOWB_H`, `mmiowb() RISCV_FENCE(o, w)`.

## Control Flow
Runtime flow is a wrapper sequence around MMIO or port-I/O reads and writes: optional fences bracket raw loads/stores, endian conversion is applied for CPU-visible values, and generic driver code calls the resulting accessors.

## State And Persistence
No durable state is stored by the header. Accessors mutate device-visible MMIO state and rely on fences to preserve ordering against CPUs, DMA, and devices.

## Dependencies And Integration Points
Direct includes are `linux/smp.h`, `asm-generic/mmiowb.h`. Integrates with driver MMIO APIs, PCI I/O space, generic `asm-generic/io.h`, DMA/noncoherent cache hooks, and RISC-V fence semantics.

## Risks And Edge Cases
Risks are missing fences, wrong endian conversion, noncoherent DMA cache omissions, and incorrect port/MMIO address translation, which can produce device data corruption or ordering bugs.

## Test Signals
Test signals include driver probe and DMA tests on coherent and noncoherent systems, PCI enumeration, MMIO ordering litmus tests, CBO cache-maintenance tests, and sparse/endian build checks.

Source read size: 15 lines, 365 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmiowb.h -->
