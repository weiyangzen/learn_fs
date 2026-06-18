# sources/distributed-fs/ceph-client/mm/mlock.c

## Purpose
Implements memory locking and unlocking for process VMAs and System V/shared memory accounting. It provides `mlock(2)`, `mlock2(2)`, `munlock(2)`, `mlockall(2)`, `munlockall(2)`, folio-level unevictable LRU transitions, per-CPU batching for mlock/munlock operations, RLIMIT/CAP checks, and user accounting for `SHM_LOCK`.

## Important APIs, Types, and Functions
User-facing syscall entry points are `mlock`, `mlock2`, `munlock`, `mlockall`, and `munlockall`. Exported or externally used helpers include `can_do_mlock()`, `mlock_drain_local()`, `mlock_drain_remote()`, `need_mlock_drain()`, `mlock_folio()`, `mlock_new_folio()`, `munlock_folio()`, `user_shm_lock()`, and `user_shm_unlock()`. The file-local `struct mlock_fbatch` stores a local lock and `folio_batch`; low pointer bits `LRU_FOLIO` and `NEW_FOLIO` encode which batch action to apply.

## Control Flow
Folio-level locking is deferred through per-CPU batches. `mlock_folio()` sets `PG_mlocked`, charges `NR_MLOCK`, takes a reference, and queues the folio as an LRU mlock operation. `mlock_new_folio()` does the same for newly allocated folios not yet on LRU. `munlock_folio()` queues the folio for unlock without clearing `PG_mlocked`; `__munlock_folio()` handles `mlock_count`, stats, and unevictable rescue decisions under the lruvec lock. `mlock_folio_batch()` decodes queued pointer flags, relocks the correct lruvec, calls `__mlock_folio()`, `__mlock_new_folio()`, or `__munlock_folio()`, unlocks the final lruvec, and releases folio refs.

Range operations operate on VMAs under the mmap write lock. `do_mlock()` normalizes and page-aligns the requested range, checks `RLIMIT_MEMLOCK` and `CAP_IPC_LOCK`, subtracts already-locked pages when needed, applies `VM_LOCKED` or `VM_LOCKONFAULT` through `apply_vma_lock_flags()`, then populates the range with `__mm_populate()` for non-on-fault mlock semantics. `munlock()` clears lock flags through the same VMA path. `mlockall()` updates `mm->def_flags` for future mappings and optionally applies current VMA flags, then populates all current address space when `MCL_CURRENT` is used.

`mlock_fixup()` filters secretmem and unsupported/special VMAs, splits or merges VMAs via `vma_modify_flags()`, updates `mm->locked_vm`, and invokes `mlock_vma_pages_range()` when actual page state must change. The page walker `mlock_pte_range()` handles PMD THPs and PTE ranges, skips zone-device pages and zero PMDs, batches large-folio PTE runs, and uses `allow_mlock_munlock()` to avoid incorrectly mlocking partially mapped large folios.

## State and Persistence Behavior
Persistent state includes VMA `VM_LOCKED` and `VM_LOCKONFAULT` flags, `mm->def_flags`, `mm->locked_vm`, folio `PG_mlocked`, folio `PG_unevictable`, folio `mlock_count`, LRU list placement, `NR_MLOCK`, unevictable VM events, and per-user `UCOUNT_RLIMIT_MEMLOCK` references for shared memory locks. Per-CPU folio batches are transient but must be drained on local CPU, CPU offline, LRU cache disable, or when callers need mlock side effects visible.

## Dependencies and Integration Points
The file integrates with VMA modification/iteration, pagewalk, rmap-visible VMA flags, LRU and lruvec locking, memcg/lruvec accounting, hugetlb and THP helpers, secretmem, resource limits, capabilities, shared memory user accounting, and population/fault-in helpers. It also cooperates with migration and reclaim: mlocked folios become unevictable, and migration restoration drains local mlock state when restoring mappings into locked VMAs.

## Risks and Edge Cases
Risk centers on mismatches between VMA lock flags and folio unevictable state, double mlock counting during concurrent migration/reclaim, partially mapped large folios, `mlock_count` undercount/overcount, and correct RLIMIT accounting when requests overlap already locked ranges. The temporary use of `VM_IO` inside `mlock_vma_pages_range()` is a concurrency signal to rmap walkers and must not leak as a visible VMA state. Secretmem is intentionally not unlocked. Error translation for population follows POSIX expectations, converting some `get_user_pages()` errors.

## Test Signals
Useful tests include `mlock`, `mlock2(MLOCK_ONFAULT)`, `munlock`, `mlockall` with current/future/onfault combinations, `munlockall`, RLIMIT and `CAP_IPC_LOCK` boundary cases, overlapping locked ranges, secretmem handling, THP and large-folio partial mappings, CPU hotplug drain paths, LRU unevictable statistics, shared memory `SHM_LOCK` accounting, and migration/reclaim interactions where mlocked folios must remain unevictable after PTE restoration.
