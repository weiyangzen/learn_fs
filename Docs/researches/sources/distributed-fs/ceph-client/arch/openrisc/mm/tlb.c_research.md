<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/tlb.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/mm/tlb.c

## Purpose
Implements local OpenRISC TLB invalidation, mm context switching, and dummy mm context lifecycle.

## Important APIs, Types, And Functions
`local_flush_tlb_all()`, `local_flush_tlb_page()`, `local_flush_tlb_range()`, `local_flush_tlb_mm()`, `switch_mm()`, `init_new_context()`, and `destroy_context()` are central. The code uses `SPR_DTLBEIR`/`SPR_ITLBEIR` when available and falls back to clearing match registers.

## Control Flow
Full flush loops over IMMU set count and clears DTLB/ITLB match registers. Page/range flushes either write invalidate-by-effective-address SPRs or clear computed set entries. `switch_mm()` updates mm CPU masks, stores `current_pgd[cpu]`, and flushes all previous mappings because context IDs are not implemented.

## State And Persistence
Invalidates hardware TLBs, updates `current_pgd`, and sets `mm->context` to `NO_CONTEXT`.

## Dependencies And Integration Points
Depends on SPR MMU config bits, `current_pgd` from fault handling, generic scheduler `switch_mm`, and TLB flush declarations.

## Risks
`NUM_DTLB_SETS` appears to read `SPR_IMMUCFGR` instead of `SPR_DMMUCFGR`, a potential geometry bug. No ASID/context support means frequent full flushes. No-EIR fallback assumes single-way behavior.

## Test Signals
Context-switch memory isolation, TLB range/page invalidation, hardware with/without TLBEIR, SMP shootdowns, and page-table permission changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/mm/tlb.c -->
