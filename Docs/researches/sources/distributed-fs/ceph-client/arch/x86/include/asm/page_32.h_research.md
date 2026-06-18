# sources/distributed-fs/ceph-client/arch/x86/include/asm/page_32.h

## Purpose
Defines x86-32 physical address conversion and basic page clear/copy helpers.

## Important APIs, Types, And Functions
Includes `page_32_types.h`, defines `__phys_addr_nodebug(x)` as `x - PAGE_OFFSET`, optional debug `__phys_addr()`, `__phys_addr_symbol()`, `__phys_reloc_hide()`, and inline `clear_page()` and `copy_page()` using `memset()` and `memcpy()`.

## Control Flow
Address conversion subtracts the 32-bit kernel `PAGE_OFFSET`. Page clear/copy helpers operate directly on kernel virtual addresses without exception handling.

## State And Persistence
No state is declared. The helpers mutate page memory supplied by callers.

## Dependencies And Integration Points
Depends on 32-bit page type constants and Linux string routines. It is included by `page.h` for non-64-bit x86 builds and used throughout mm initialization and page management.

## Risks And Edge Cases
No exception handling means callers must pass valid mapped kernel addresses. Debug virtual builds replace `__phys_addr()` with a checked function. The direct subtraction model assumes classic 32-bit kernel mapping.

## Test Signals
x86-32 build and boot coverage, debug-virtual tests, page allocator tests, and memory copy/clear stress provide signal.
