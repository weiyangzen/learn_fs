# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/entry.h

## Purpose

defines low-level ABI entry/exit, register save, restore, and trap frame assembly macros for C-SKY
ABI v2

## Important APIs, Types, and Functions

Source read size: 314 lines, 4885 bytes. Includes: `asm/setup.h`, `abi/regdef.h`. Key
macros/defines: `__ASM_CSKY_ENTRY_H`, `LSAVE_PC`, `LSAVE_PSR`, `LSAVE_A0`, `LSAVE_A1`, `LSAVE_A2`,
`LSAVE_A3`, `LSAVE_A4`, `LSAVE_A5`, `KSPTOUSP`, `USPTOKSP`, `usp`, `MSA_SET`, `MSA_CLR`.

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
