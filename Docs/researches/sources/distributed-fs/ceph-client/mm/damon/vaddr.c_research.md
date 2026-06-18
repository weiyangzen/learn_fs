# sources/distributed-fs/ceph-client/mm/damon/vaddr.c

## Purpose
This file implements DAMON operations for process virtual address spaces. It registers `DAMON_OPS_VADDR` for adaptive virtual address monitoring and `DAMON_OPS_FVADDR` for fixed virtual address ranges. It derives initial monitored regions from a target process's VMAs, samples page-table accessed/idle state, and applies DAMOS actions such as `madvise()`, stat accounting, and NUMA migration.

## Important APIs, Types, And Functions
Target and mm helpers are `damon_get_task_struct()`, `damon_get_mm()`, and `damon_va_target_valid()`. Region initialization/update centers on `__damon_va_three_regions()`, `damon_va_three_regions()`, `__damon_va_init_regions()`, `damon_va_init()`, and `damon_va_update()`.

Access sampling uses page-table walkers:

- `damon_va_prepare_access_checks()` chooses a random sampling address per region and calls `damon_va_mkold()`.
- `damon_mkold_pmd_entry()` and `damon_mkold_hugetlb_entry()` clear young/accessed state and set folio idle state.
- `damon_va_check_accesses()` calls `damon_va_young()` through `damon_young_pmd_entry()` and `damon_young_hugetlb_entry()` and updates region access rates.

DAMOS action support includes `damos_va_filter_young_match()`, `damos_va_filter_out()`, migration helpers `damos_va_migrate_dests_add()`, `damos_va_migrate_pmd_entry()`, `damos_va_migrate()`, stat helpers `damos_va_stat_pmd_entry()` and `damos_va_stat()`, `damos_madvise()`, `damon_va_apply_scheme()`, and `damon_va_scheme_score()`.

`damon_va_initcall()` registers the operation table with DAMON core.

## Control Flow
At subsystem init, `damon_va_initcall()` registers vaddr ops with initialization/update callbacks and then registers fixed-vaddr ops by copying the same operation table but clearing `.init` and `.update`.

For adaptive vaddr monitoring, initialization walks each target. If the user did not provide regions, `__damon_va_init_regions()` obtains the target `mm_struct`, finds the two largest unmapped gaps among VMAs, constructs three ranges covering mapped regions outside those gaps, and installs them with `damon_set_regions()`. Periodic update recomputes the three ranges and resets target regions.

For sampling, the prepare phase randomly selects one address inside each region and clears accessed/young state for that address. The check phase later tests whether the same address became young or non-idle, caches the last checked folio result for adjacent regions in the same target, and updates `nr_accesses`/`nr_accesses_bp`.

For DAMOS actions, `damon_va_apply_scheme()` maps actions to `do_madvise()` behaviors, migration, or stat-only walks. Migration walks PTE/PMD entries in the region, filters folios, isolates eligible folios into weighted destination lists, and calls `damon_migrate_pages()`. Stat walks count bytes that pass filters without applying memory advice.

## State And Persistence
The operation stores no global runtime state except the registered ops. It relies on per-context targets, per-region `sampling_addr`, access counters, scheme fields, and target PID references. `damon_va_cleanup_target()` releases target PID references with `put_pid()`.

Sampling functions use static local cache variables in `__damon_va_check_access()` (`last_addr`, `last_folio_sz`, `last_accessed`) to reuse a page lookup for adjacent regions in the same target during a check pass.

## Dependencies And Integration Points
The file depends on Linux MM internals: VMA maple tree iteration, mmap locks, page-table walkers, PTE/PMD/hugetlb helpers, folio idle/young state, MMU notifiers, THP, HugeTLB, `do_madvise()`, LRU isolation, NUMA migration, and scheduler rescheduling.

It integrates with DAMON core via `struct damon_operations`: `.init`, `.update`, `.prepare_access_checks`, `.check_accesses`, `.target_valid`, `.cleanup_target`, `.apply_scheme`, and `.get_scheme_score`. It also uses common DAMON operations helpers for pte/pmd aging, hot/cold scoring, folio filters, and migration.

## Risks And Edge Cases
`__damon_va_three_regions()` requires at least two nonzero unmapped gaps. Processes with too few mappings or insufficient gaps fail initialization/update and are skipped or left unchanged.

Page-table walking races are mitigated with mmap read locks, page-table locks, and walker read locks, but sampling is inherently approximate. Young checks combine PTE/PMD young bits, folio idle state, and MMU notifier young state; architecture-specific behavior can affect accuracy.

The static last-folio cache in `__damon_va_check_access()` is scoped to the function and reused across calls; it is guarded only by the `same_target` boolean and assumes the calling flow is serial per context.

Migration destination selection uses weighted modulo based on VMA offset and folio order. If all destination weights are zero, migration is skipped. If no explicit destinations exist, all isolated folios go to `scheme->target_nid`.

Stat and migration walkers skip duplicate folios using `s->last_applied`; correctness relies on updating this field consistently across THP and PTE paths.

## Test Signals
`tests/vaddr-kunit.h` directly covers three-region derivation and `damon_set_regions()` update behavior. Core KUnit tests cover filter and scoring primitives. The file has no direct KUnit coverage for page-table young/mkold walkers, HugeTLB/THP paths, madvise application, migration isolation, or NUMA destination weighting.
