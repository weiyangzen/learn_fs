# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/subpage_prot.c

Purpose: provides the Book3S64 hash-MMU `subpage_prot` syscall, adding 4K subpage restrictions inside larger kernel page sizes for selected user ranges.

Important APIs and control flow: `SYSCALL_DEFINE3(subpage_prot)` rejects radix, validates page alignment and task bounds, rejects hugepage-only ranges, allocates the per-mm subpage protection table on demand, optionally marks/splits THP VMAs, demotes segments to 4K, copies user protection words, and flushes corresponding HPTEs. Passing a null map clears stored restrictions through `subpage_prot_clear()`. `subpage_prot_free()` releases low and high-level protection pages during mm teardown.

State and dependencies: state lives in `mm->context.hash_context->spt`, including low-memory pointers, high-level pointer pages, and `maxaddr`. It depends on `mmap_write_lock`, page-table walking, HPTE invalidation through `pte_update()`, THP split helpers, `demote_segment_4k()`, and user-copy APIs. Risks include partially updated maps if user copy faults after lock dropping, stale HPTEs if flushing misses ranges, THP interaction mistakes, and memory leaks in sparse high-range tables. Test signals are syscall ABI tests, clear/set cycles, THP split coverage, invalid alignment/range errors, and hash-vs-radix behavior.
