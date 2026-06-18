# sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/reg_ops.h

## Purpose

provides inline helpers or macros for reading and writing C-SKY control registers for C-SKY ABI v1

## Important APIs, Types, and Functions

Source read size: 26 lines, 489 bytes. Includes: `asm/reg_ops.h`. Functions: `mfcr_hint`,
`mfcr_ccr2`. Key macros/defines: `__ABI_REG_OPS_H`, `cprcr(reg)`, `cpwcr(reg, val)`.

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
