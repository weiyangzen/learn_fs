<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/Makefile

## Purpose
This Makefile selects 64-bit Book3S MMU objects for hash, radix, hugepage, IOMMU, and memory protection-key support.

## Important APIs, types, and functions
Always-built objects are `mmu_context.o`, `pgtable.o`, and `trace.o`. Hash MMU builds add hash page table, utilities, TLB, SLB, slice, native/hash page-size helpers, hugepage, and subpage protection objects. Radix builds add radix page table/TLB/hugepage objects.

## Control flow
Kbuild conditionally adds objects based on `CONFIG_PPC_64S_HASH_MMU`, page size, transparent hugepage, radix MMU, hugetlb, SPAPR TCE IOMMU, and pkeys. It disables ftrace/KASAN/KCOV instrumentation for sensitive low-level paths.

## State and persistence behavior
No runtime state; controls build composition and instrumentation.

## Dependencies and integration points
Top-level integration for Book3S64 hash/radix MM subsystems.

## Risks and edge cases
Instrumentation exclusions protect real-mode/SLB paths; removing them can break low-level faults. Wrong page-size object selection can break hash insertion.

## Test signals
Build success across hash/radix, 4K/64K, THP, hugetlb, pkeys, and KASAN/KCOV combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/Makefile -->
