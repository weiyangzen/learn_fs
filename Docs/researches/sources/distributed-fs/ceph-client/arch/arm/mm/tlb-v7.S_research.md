# sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v7.S

## Purpose
Implements ARMv7 range TLB invalidation with SMP-aware shareable operations, UP alternatives, ASID-aware user invalidation, and erratum 720789 handling.

## Important APIs, Types, And Functions
Exports `v7wbi_flush_user_tlb_range` and `v7wbi_flush_kern_tlb_range`. Uses `dsb ish`, `isb`, alternative SMP/UP instruction patching, `mmid`, `asid`, and CP15 c8 TLB invalidate by MVA operations.

## Control Flow
User flush obtains the VMA mm context ID, issues `dsb ish`, aligns addresses, masks ASID, optionally zeros ASID for erratum 720789 on SMP, combines ASID with MVA, and loops issuing SMP shareable or UP local invalidates. Kernel flush performs the same page loop without ASID and finishes with `dsb ish; isb`.

## State, Dependencies, And Integration
State changed is local or broadcast TLB content. Dependencies are ARMv7-A CP15 semantics, alternative patching, `CONFIG_SMP`, `CONFIG_ARM_ERRATA_720789`, and `v7wbi_tlb_flags_smp/up`. Integration is through `v7wbi_tlb_fns` and processor tables in `proc-v7.S`.

## Risks And Test Signals
Risks are stale remote TLBs if SMP alternatives or flags mismatch, too-broad invalidation under erratum handling, missing barriers, and branch-range issues for large loops. Test with SMP ARMv7 boot, mprotect/unmap stress across CPUs, ASID reuse, erratum-configured builds, and kernel text mapping changes.
