# sources/distributed-fs/ceph-client/mm/page_vma_mapped.c

## Purpose
`page_vma_mapped.c` implements `page_vma_mapped_walk()`, the reverse-map helper that finds all page-table entries in one VMA mapping a target page or folio range. It supports normal PTEs, PMD-mapped THP, hugetlb, migration entries, and device-private/exclusive softleaf entries.

## Important APIs, Types, And Functions
- `page_vma_mapped_walk()` is the exported iterator over matching mappings.
- `page_vma_mapped_walk_done()` is called through `not_found()` or by callers to release held locks and mappings.
- `map_pte()` maps and optionally locks a PTE page, handling strict sync mode and PMD-change retry.
- `check_pte()` verifies that a PTE or softleaf entry overlaps the requested PFN range.
- `check_pmd()` verifies PMD-sized PFN range overlap.
- `page_mapped_in_vma()` is a memory-failure helper that returns the mapped address for a single page in a VMA.

## Control Flow
The walker first finishes any prior PMD-only mapping, then handles hugetlb VMAs through `hugetlb_walk()` and `huge_pte_lock()`. For normal VMAs it computes the range of addresses where the page could appear, descends PGD/P4D/PUD/PMD levels, skips absent upper entries by stepping to the next boundary, and treats PMD THP or PMD migration entries as direct matches if PFN ranges overlap. Non-present PMDs can also trigger PMD zap synchronization in `PVMW_SYNC` mode. Otherwise it maps a PTE page, validates the PTE against the requested PFN range, and iterates forward through PTEs until the VMA end or PMD boundary, returning each match with the page-table lock held.

## State And Persistence Behavior
The persistent state is in caller-provided `struct page_vma_mapped_walk`: current address, PFN range, VMA, flags, PTE/PMD pointers, PTL, and page-table-crossed flag. The file mutates no long-lived global state. It temporarily locks PTE, PMD, or hugepage page-table locks and maps PTE pages.

## Dependencies And Integration Points
It is tightly integrated with rmap, page migration, memory failure, hugetlb, THP splitting, HMM/device-private memory, softleaf swap encodings, MMU synchronization, and VMA address calculation helpers. Page idle, reclaim, migration, and memory-failure code rely on this walker to find exact mappings.

## Risks
- Page tables can change concurrently; PMD lockless reads and retry checks must be exact to avoid stale PTE access.
- Callers must release locks with `page_vma_mapped_walk_done()` when stopping early.
- Migration and device-private entries are non-present but still count as mappings for some rmap operations.
- THP range overlap must account for subpages without overflowing PFN arithmetic.
- Hugetlb locking differs from normal PTE/PMD locking and assumes callers hold the mapping semaphore documented by rmap users.

## Test Signals
- Rmap operations over PTE-mapped THP, PMD THP, split THP races, hugetlb, migration entries, and device-private/exclusive entries.
- Memory-failure `page_mapped_in_vma()` on mapped and unmapped pages.
- Lockdep/KCSAN while unmapping or splitting PMDs concurrently with rmap walks.
