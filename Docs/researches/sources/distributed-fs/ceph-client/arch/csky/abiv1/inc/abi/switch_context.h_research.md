# sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/switch_context.h

## Purpose

defines ABI-specific context switch save/restore contracts for C-SKY ABI v1

## Important APIs, Types, and Functions

Source read size: 16 lines, 313 bytes. Key macros/defines: `__ABI_CSKY_PTRACE_H`. Local structs:
`switch_stack`.

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
