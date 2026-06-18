# sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v4wb.S

## Purpose
Implements ARMv4 range TLB invalidation for SA110/SA1100/SA1110-style CPUs with split I/D TLBs, no I-TLB entry invalidation by MVA, and a write buffer.

## Important APIs, Types, And Functions
Exports `v4wb_flush_user_tlb_range` and `v4wb_flush_kern_tlb_range`. Uses VM executable flags to decide when to invalidate the whole I-TLB and always invalidates D-TLB entries by page.

## Control Flow
User flush skips inactive mms, drains the write buffer, checks `VM_EXEC`, invalidates the full I-TLB for executable mappings, then loops over aligned pages invalidating D-TLB entries. Kernel flush drains, aligns, invalidates the full I-TLB unconditionally, and loops over D-TLB entries.

## State, Dependencies, And Integration
State is write buffer plus split I/D TLB content. Dependencies are `asm/tlbflush.h`, VM flag helpers, and processor table selection through `v4wb_tlb_fns`.

## Risks And Test Signals
Risks are stale executable translations if `VM_EXEC` detection is wrong, excessive full I-TLB invalidation cost, and missing write-buffer drains before invalidation. Test signals include SA110-class boot, executable mmap permission transitions, fork/exec stress, and kernel text mapping changes.
