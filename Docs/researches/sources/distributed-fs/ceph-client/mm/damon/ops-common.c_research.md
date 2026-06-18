# sources/distributed-fs/ceph-client/mm/damon/ops-common.c

Purpose: Supplies shared low-level helpers for DAMON address-operation backends, especially page/folio lookup, access-bit aging, hot/cold scoring, folio filters, and NUMA migration support.

Important APIs, types, and functions: `damon_get_folio()` obtains an online LRU folio for a PFN. `damon_ptep_mkold()`, `damon_pmdp_mkold()`, `damon_folio_mkold()`, and `damon_folio_young()` implement access-bit/idle-state sampling via reverse mapping and MMU notifiers. `damon_hot_score()` and `damon_cold_score()` compute DAMOS score values. `damos_folio_filter_match()` evaluates anon, active, memcg, young, hugepage-size, and unmapped filters. `damon_migrate_pages()` migrates isolated folios to a target NUMA node.

Control flow: Access checks clear young bits and set folio idle state, later query young/idle/MMU notifier state to decide if accessed. Filters call into folio predicates and may mark young pages old after matching. Migration groups folios by source node, locks where possible, calls `migrate_pages()` with async DAMON reason, returns migrated folios, and puts back failed pages to LRU.

State and persistence: No global persistent state. It mutates PTE/PMD young bits, folio idle/young flags, LRU membership during migration, and memcg references while filtering.

Dependencies and integration: Uses rmap walking, page idle, mmu_notifier, memcg, migration, swap/softleaf handling, THP conditionals, and `../internal.h`. Called by paddr and vaddr DAMON ops.

Risks: Rmap walking and nonblocking folio locking can miss accesses or decline sampling under contention. Young filtering has side effects by aging folios. Migration ignores cpuset/mempolicy by design and must avoid reclaim recursion using `memalloc_noreclaim_save()`.

Test signals: Page idle and DAMON access sampling tests, THP and device-exclusive mapping coverage, memcg filter checks, NUMA migration success/failure counts, and KUnit or trace validation of hot/cold scores.
