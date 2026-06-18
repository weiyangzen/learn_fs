<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-masks.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-masks.h

## Purpose
This header supplies common Linux protection-mask combinations for PowerPC page tables when the platform-specific PTE header has not overridden them.

## Important APIs, Types, And Functions
It conditionally defines `_PAGE_NA`, `_PAGE_NAX`, `_PAGE_RO`, `_PAGE_ROX`, `_PAGE_RW`, `_PAGE_RWX`, kernel permission masks `_PAGE_KERNEL_RO/ROX/RW/RWX`, and user protection macros `PAGE_NONE`, `PAGE_EXECONLY_X`, `PAGE_SHARED`, `PAGE_SHARED_X`, `PAGE_COPY`, `PAGE_COPY_X`, `PAGE_READONLY`, and `PAGE_READONLY_X`.

## Control Flow
No runtime flow is present. The macros are consumed at compile time by pgprot construction and generic mmap permission tables.

## State And Persistence Behavior
The resulting `pgprot_t` values persist in VMAs and PTEs created from those protections.

## Dependencies And Integration Points
It depends on platform `_PAGE_BASE`, `_PAGE_READ`, `_PAGE_WRITE`, `_PAGE_EXEC`, and `_PAGE_DIRTY` definitions. It is included by PTE layout headers.

## Risks And Edge Cases
Some backends override permission semantics, so these defaults must remain guarded. Incorrect combinations can grant execute/write permissions or break COW protections.

## Test Signals
Run mmap protection matrix tests, mprotect, COW, execute-only/read-only mapping checks, and backend cross-builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-masks.h -->
