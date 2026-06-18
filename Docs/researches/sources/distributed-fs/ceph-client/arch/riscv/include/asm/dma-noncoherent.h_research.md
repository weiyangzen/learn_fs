<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/dma-noncoherent.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/dma-noncoherent.h

## Purpose
Declares non-coherent DMA cache-operation registration hooks for RISC-V platforms.

## Important APIs, Types, And Functions
types `riscv_nonstd_cache_ops`; functions/prototypes `riscv_noncoherent_register_cache_ops`, `noncoherent_cache_ops`; macros/constants `__ASM_DMA_NONCOHERENT_H`.

## Control Flow
Runtime flow is a wrapper sequence around MMIO or port-I/O reads and writes: optional fences bracket raw loads/stores, endian conversion is applied for CPU-visible values, and generic driver code calls the resulting accessors.

## State And Persistence
No durable state is stored by the header. Accessors mutate device-visible MMIO state and rely on fences to preserve ordering against CPUs, DMA, and devices.

## Dependencies And Integration Points
Direct includes are `linux/dma-direct.h`. Integrates with driver MMIO APIs, PCI I/O space, generic `asm-generic/io.h`, DMA/noncoherent cache hooks, and RISC-V fence semantics.

## Risks And Edge Cases
Risks are missing fences, wrong endian conversion, noncoherent DMA cache omissions, and incorrect port/MMIO address translation, which can produce device data corruption or ordering bugs.

## Test Signals
Test signals include driver probe and DMA tests on coherent and noncoherent systems, PCI enumeration, MMIO ordering litmus tests, CBO cache-maintenance tests, and sparse/endian build checks.

Source read size: 28 lines, 835 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/dma-noncoherent.h -->
