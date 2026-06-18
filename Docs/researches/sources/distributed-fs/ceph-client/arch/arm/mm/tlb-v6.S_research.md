# sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v6.S

## Purpose
Provides ARMv6 range TLB invalidation for Harvard-style split I/D TLBs, including ASID-aware user invalidation and kernel-range invalidation.

## Important APIs, Types, And Functions
Exports `v6wbi_flush_user_tlb_range` and `v6wbi_flush_kern_tlb_range`. Uses `mmid`, `asid`, `vma_vm_flags`, CP15 write-buffer drains, and CP15 c8 MVA invalidation operations.

## Control Flow
User flush extracts `vma->vm_mm->context.id`, drains the write buffer, aligns start/end to pages, combines ASID with MVA, reads VM flags, then loops invalidating D-TLB entries and I-TLB entries for executable mappings. Kernel flush aligns addresses, loops invalidating both D and I TLBs, drains, and prefetch flushes.

## State, Dependencies, And Integration
State is local TLB and write-buffer contents. Dependencies include ARMv6 architecture mode, ASID layout, `asm/tlbflush.h`, and `v6wbi_tlb_flags`. Integration is through `v6wbi_tlb_fns` in `tlb.c`.

## Risks And Test Signals
Risks include ASID composition mistakes, executable flag handling bugs, missing final synchronization, and unsupported assumptions if non-Harvard builds are introduced. Test signals are ARMv6 boot, ASID wrap tests, mmap/mprotect stress, and executable page coherence tests.
