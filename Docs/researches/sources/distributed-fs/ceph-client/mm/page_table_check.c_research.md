# sources/distributed-fs/ceph-client/mm/page_table_check.c

## Purpose
`page_table_check.c` implements a debug hardening feature that tracks user-accessible page-table mappings per physical page. It catches illegal double writable anonymous mappings, anon/file mapping type conflicts, stale mappings on free, and userfaultfd write-protect flag inconsistencies.

## Important APIs, Types, And Functions
- `struct page_table_check` stores atomic anon and file map counters in page extensions.
- `page_table_check_ops` registers page extension storage and static-key initialization.
- `page_table_check_clear()` and `page_table_check_set()` decrement/increment per-page counters and BUG on invalid states.
- `__page_table_check_zero()` verifies counters are zero when pages are freed or allocated.
- `__page_table_check_pte_clear()`, `__page_table_check_pmd_clear()`, and `__page_table_check_pud_clear()` remove mapping counts.
- `__page_table_check_ptes_set()`, `__page_table_check_pmds_set()`, and `__page_table_check_puds_set()` clear old entries and add new mapping counts.
- `__page_table_check_pte_clear_range()` clears all PTEs under a PMD table.

## Control Flow
An early parameter or enforced Kconfig setting decides whether page extension storage is needed. Initialization disables the `page_table_check_disabled` static key when enabled. Page-table set hooks ignore `init_mm`, validate write-protect flag combinations, clear the previous entry or entries, and if the new entry is user-accessible, increment the anon or file counter for every base page covered. Clear hooks decrement the appropriate counter. Anonymous pages BUG if they acquire file mappings or more than one writable mapping; file pages BUG if they acquire anon mappings or counters underflow. Free/alloc zero checks BUG if any counter remains.

## State And Persistence Behavior
State is runtime-only per-page extension counters and the static branch. Counters are atomic because page-table operations can touch the same page concurrently. There is no persistence beyond the current boot, and failures intentionally crash via `BUG_ON()` to expose corruption.

## Dependencies And Integration Points
The file integrates with architecture/generic page-table update hooks, `page_ext`, swap/softleaf encodings for migration and device-private entries, userfaultfd write-protect helpers, `leafops`, and exported symbols used by low-level page-table code.

## Risks
- This is fatal-debug logic: false positives panic the system.
- Correctness depends on every relevant page-table modification calling the check hooks in the right order.
- Large PMD/PUD mappings must account for every base page, so incorrect `pgcnt` or stride calculations skew counters.
- UFFD-WP and softleaf cached-writable checks are subtle across migration/device-private entries.

## Test Signals
- Boot with `page_table_check=on` and run fork/COW, mprotect, THP, hugetlb-adjacent, migration, swap, and device-private memory tests.
- Intentionally create conflicting writable anonymous aliases in a debug test to verify the BUG path.
- Exercise page free paths with mapped pages to ensure `__page_table_check_zero()` detects leaks.
- Run userfaultfd write-protect tests involving present, swap, migration, and device-private entries.
