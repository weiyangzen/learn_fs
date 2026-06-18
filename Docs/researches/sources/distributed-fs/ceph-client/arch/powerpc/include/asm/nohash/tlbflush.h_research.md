<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/tlbflush.h

## Purpose
This header declares and, for 8xx, implements nohash TLB flush operations for mm, page, range, kernel range, and page-size-specific invalidation.

## Important APIs, Types, And Functions
It defines `MMU_NO_CONTEXT`, declares `flush_tlb_range()`, `flush_tlb_kernel_range()`, `local_flush_tlb_mm()`, `local_flush_tlb_page()`, `local_flush_tlb_page_psize()`, `__local_flush_tlb_page()`, and SMP `flush_tlb_mm()`, `flush_tlb_page()`, `__flush_tlb_page()`. On UP, global names alias local helpers.

## Control Flow
On 8xx, `local_flush_tlb_mm()` checks the mm context id before issuing `tlbia`; page flushes issue `tlbie`; kernel-range flush chooses single-page `tlbie` or full `tlbia` based on range size. Other nohash CPUs use out-of-line implementations.

## State And Persistence Behavior
The affected state is hardware TLB contents. The header does not store state, but it depends on `mm->context.id` to avoid unnecessary 8xx full invalidation for inactive contexts.

## Dependencies And Integration Points
It integrates with generic MM invalidation, nohash PTE update helpers, SMP shootdown code, and architecture TLB assembly.

## Risks And Edge Cases
Missing `sync`/`isync` ordering can expose stale translations. The 8xx full-flush fallback is coarse. SMP builds must route global flushes through shootdown implementations rather than local aliases.

## Test Signals
Run mmap/unmap, mprotect, fork/exit, TLB shootdown, hugepage invalidation, and 8xx kernel-range flush tests under SMP and UP builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/tlbflush.h -->
