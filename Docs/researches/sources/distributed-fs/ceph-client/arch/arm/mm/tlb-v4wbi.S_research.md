# sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v4wbi.S

## Purpose
Implements ARMv4/v5 write-buffered split I/D TLB invalidation with per-entry invalidation for both instruction and data TLBs. Used by ARM920/922/925/926 and XScale-class processors.

## Important APIs, Types, And Functions
Exports `v4wbi_flush_user_tlb_range` and `v4wbi_flush_kern_tlb_range`. Uses CP15 c8 I-TLB and D-TLB invalidate-by-MVA operations and a write-buffer drain.

## Control Flow
User flush verifies the VMA mm is active, drains the write buffer, reads `vm_flags`, aligns start, and loops over pages. For executable VMAs it invalidates the I-TLB entry; it always invalidates the D-TLB entry. Kernel flush drains and invalidates both I and D entries for every page in the range.

## State, Dependencies, And Integration
State changed is local CPU TLB and write buffer state. Dependencies are `proc-macros.S`, VM helpers, and `v4wbi_tlb_flags`. Integration is through `v4wbi_tlb_fns`, also used for some Feroceon configurations.

## Risks And Test Signals
Risks are stale instruction translations, missed inactive-mm handling assumptions, and excessive cost for large ranges. Test signals include ARM9/XScale boot, memory protection changes, executable page remapping, and context switch TLB behavior.
