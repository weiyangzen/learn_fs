# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/elf.h

## Purpose

defines ABI-specific ELF flags, register constants, and process personality details for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 43 lines, 1321 bytes. Key macros/defines: `__ABI_CSKY_ELF_H`,
`ELF_CORE_COPY_REGS(pr_reg, regs)`.

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
