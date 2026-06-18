<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/tlb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/tlb.c

## Purpose
This file provides C TLB/hash flush wrappers for Book3S32 hash MMUs.

## Important APIs, types, and functions
Exported functions are `hash__flush_range`, `hash__flush_tlb_mm`, `hash__flush_tlb_page`, and `hash__flush_gather`.

## Control flow
Range flush aligns start/end to pages, walks PMD spans, and calls `flush_hash_pages` for present PMDs. Full-mm flush iterates VMAs. Page flush picks the VMA mm or `init_mm` for kernel addresses. Gather flush chooses full-mm/range based on `mmu_gather` flags.

## State and persistence behavior
It does not directly mutate PTEs; it delegates HPTE/TLB state mutation to `flush_hash_pages`.

## Dependencies and integration points
Integrated with Linux TLB gather/unmap paths, VMA iteration, PMD lookup, and `hash_low.S`.

## Risks and edge cases
Correct end-address rounding, VMA iteration locking assumptions, kernel versus user mm selection, and PMD count calculation are important.

## Test signals
No stale mappings after unmap/mprotect/exit, correct full-mm flush during dup/exit, and stable hash-table state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/tlb.c -->
