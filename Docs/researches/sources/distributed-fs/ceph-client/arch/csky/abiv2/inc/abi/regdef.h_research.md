# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/regdef.h

## Purpose

names C-SKY architectural registers for assembly and inline assembly consumers for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 31 lines, 600 bytes. Key macros/defines: `__ASM_CSKY_REGDEF_H`, `syscallid`,
`regs_syscallid(regs)`, `regs_fp(regs)`, `DEFAULT_PSR_VALUE`, `SYSTRACE_SAVENUM`, `TRAP0_SIZE`.

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
