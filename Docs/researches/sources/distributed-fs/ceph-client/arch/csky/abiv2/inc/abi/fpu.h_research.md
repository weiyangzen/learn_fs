# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/fpu.h

## Purpose

defines ABI v2 floating-point state structures and FPU status/control bit masks for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 66 lines, 1585 bytes. Includes: `asm/sigcontext.h`, `asm/ptrace.h`. Functions:
`init_fpu`. Key macros/defines: `__ASM_CSKY_FPU_H`, `FPE_ILLE`, `FPE_FEC`, `FPE_IDC`, `FPE_IXC`,
`FPE_UFC`, `FPE_OFC`, `FPE_DZC`, `FPE_IOC`, `FPE_REGULAR_EXCEPTION`, `IDE_STAT`, `IXE_STAT`,
`UFE_STAT`, `OFE_STAT`, `DZE_STAT`, `IOE_STAT`.

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
