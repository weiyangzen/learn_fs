# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/pgtable-bits.h

## Purpose

defines page-table bit assignments, cacheability encodings, swap encodings, and protection bits for
C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 53 lines, 1556 bytes. Key macros/defines: `__ASM_CSKY_PGTABLE_BITS_H`,
`_PAGE_ACCESSED`, `_PAGE_READ`, `_PAGE_WRITE`, `_PAGE_PRESENT`, `_PAGE_MODIFIED`,
`_PAGE_SWP_EXCLUSIVE`, `_PAGE_GLOBAL`, `_PAGE_VALID`, `_PAGE_DIRTY`, `_PAGE_SO`, `_PAGE_BUF`,
`_PAGE_CACHE`, `_CACHE_MASK`, `_CACHE_CACHED`, `_CACHE_UNCACHED`, `_PAGE_PROT_NONE`,
`__swp_type(x)`; plus 2 more.

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
