# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/ckmmu.h

## Purpose

defines C-SKY MMU/TLB register constants and helper macros for ABI-specific page-table and TLB
management for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 139 lines, 2157 bytes. Includes: `abi/reg_ops.h`, `asm/barrier.h`. Functions:
`read_mmu_index`, `write_mmu_index`, `read_mmu_entrylo0`, `read_mmu_entrylo1`, `write_mmu_pagemask`,
`read_mmu_entryhi`, `write_mmu_entryhi`, `read_mmu_msa0`, `write_mmu_msa0`, `read_mmu_msa1`,
`write_mmu_msa1`, `tlb_probe`, `tlb_read`, `tlb_invalid_all`, `local_tlb_invalid_all`,
`tlb_invalid_indexed`, `setup_pgd`. Key macros/defines: `__ASM_CSKY_CKMMUV2_H`, `NOP32`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
