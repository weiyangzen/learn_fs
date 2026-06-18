# sources/distributed-fs/ceph-client/arch/arm/mm/tlb-fa.S

## Purpose
Implements Faraday FA520/FA526/FA626 range TLB invalidation for unified TLBs with write buffer and BTB behavior.

## Important APIs, Types, And Functions
Exports `fa_flush_user_tlb_range(start, end, vma)` and `fa_flush_kern_tlb_range(start, end)`. Uses `vma_vm_mm`, `act_mm`, `PAGE_SZ`, CP15 write-buffer drain, and unified TLB invalidate-by-MVA operations.

## Control Flow
User flush first compares the VMA's mm with `current->active_mm`; if it is not active, it returns without flushing. Active ranges drain the write buffer, align the start address to a page boundary, loop by page invalidating UTLB entries, then drain again. Kernel range follows the same loop and also performs a prefetch flush.

## State, Dependencies, And Integration
State is CPU TLB and write buffer state only. Dependencies are `asm/tlbflush.h`, `proc-macros.S`, VM flag/mm access macros, and Faraday proc-info entries that select `fa_tlb_fns` from `tlb.c`.

## Risks And Test Signals
Risks are active-mm comparison mistakes, address alignment errors, missing BTB/prefetch ordering for executable kernel mappings, and stale entries on context switches. Test with mmap/munmap/mprotect stress, kernel module text mapping changes, and Faraday-specific boot tests.
