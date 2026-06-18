# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/string.h

## Purpose

selects ABI-optimized string routine declarations or aliases for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 27 lines, 699 bytes. Key macros/defines: `__ABI_CSKY_STRING_H`,
`__HAVE_ARCH_MEMCMP`, `__HAVE_ARCH_MEMCPY`, `__HAVE_ARCH_MEMMOVE`, `__HAVE_ARCH_MEMSET`,
`__HAVE_ARCH_STRCMP`, `__HAVE_ARCH_STRCPY`, `__HAVE_ARCH_STRLEN`.

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
