# sources/distributed-fs/ceph-client/mm/userfaultfd.c

## Purpose

`userfaultfd.c` implements kernel-side helpers for userfaultfd operations over ordinary VMAs: atomic missing-page fill, zero-page fill, continue, poison, write-protect changes, zero-copy anonymous page moves, registration, clear, and release. It coordinates VMA lookup/locking, page-table installation, mmu notifier invalidation, rmap updates, hugetlb special cases, and VMA flag/context mutation.

## Important APIs, Types, and Functions

- `struct mfill_state` carries one atomic fill operation: userfaultfd context, source/destination ranges, mode flags, current VMA, current source/destination page addresses, and destination PMD.
- `vma_uffd_ops()` selects anonymous UFFD operations or filesystem-provided `vm_ops->uffd_ops`.
- `validate_dst_vma()` ensures a destination range stays inside a single registered VMA.
- `mfill_atomic_copy()`, `mfill_atomic_zeropage()`, `mfill_atomic_continue()`, and `mfill_atomic_poison()` are exported operation helpers that select a mode and call `mfill_atomic()`.
- `mwriteprotect_range()` and `uffd_wp_range()` apply or resolve userfaultfd write protection over VMA ranges.
- `move_pages()` implements `UFFDIO_MOVE` for anonymous, compatible VMAs, returning either bytes moved or a negative error.
- `vma_can_userfault()`, `userfaultfd_register_range()`, `userfaultfd_clear_vma()`, `userfaultfd_release_new()`, and `userfaultfd_release_all()` manage VMA eligibility and context/flag lifecycle.
- `double_pt_lock()` and `double_pt_unlock()` impose deterministic page-table-lock ordering for source/destination PTE operations.

## Control Flow

Atomic fill starts in `mfill_atomic()`, which validates page alignment/wrap conditions, locks a destination VMA with either per-VMA locking or `mmap_read_lock()`, takes `ctx->map_changing_lock`, checks `ctx->mmap_changing`, rejects unsupported modes, and dispatches hugetlb ranges to `mfill_atomic_hugetlb()`. For normal PTEs it establishes a PMD, selects the page-level handler, and advances page by page, returning a partial byte count if progress was made before an error or fatal signal.

Copy/zero fill allocates or obtains a folio through `vm_uffd_ops`, copies from userspace with a retry path that temporarily drops mapping locks to avoid mmap-lock deadlocks, marks the folio uptodate, optionally inserts it into file cache, and installs the PTE with `mfill_atomic_install_pte()`. PTE installation constructs dirty/writable/UFFD-WP PTEs, rejects non-empty destinations except allowed UFFD markers, updates rmap/mm counters, unlocks file-cache folios after successful install, and updates the MMU cache. Continue looks up an existing file-cache folio without allocation. Poison installs a poisoned PTE marker and refuses to overwrite any existing PTE.

`mwriteprotect_range()` walks VMAs under `mmap_read_lock()` and `map_changing_lock`, verifies each VMA is UFFD-WP capable, handles hugetlb alignment, and calls `uffd_wp_range()`, which wraps `change_protection()` in an `mmu_gather`.

`move_pages()` locks source and destination VMAs, validates that ranges are single-VMA, anonymous, writable, non-shared, compatible, and registered with the same context. It then walks PMD/PTE ranges. Huge PMDs may be moved whole if naturally aligned and destination-empty; otherwise they are split. PTE moves handle present anonymous folios, zero pages, swap entries, migration entries, holes, and destination-exists conditions. `move_pages_ptes()` uses mmu notifier invalidation and carefully rechecks PTE and PMD stability after taking locks.

Registration walks the target range with the mmap write lock held, validates `vma_can_userfault()`, uses `vma_modify_flags_uffd()` to split or merge as needed, assigns `vm_userfaultfd_ctx`, sets UFFD flags, and disables hugetlb PMD sharing when necessary. Release paths reset matching VMA contexts and clear UFFD flags, using `userfaultfd_clear_vma()` to resolve outstanding write-protect PTEs before flag removal.

## State and Persistence

The durable state is embedded in VMAs and page tables: `vma->vm_userfaultfd_ctx`, `VM_UFFD_*` flags, UFFD-WP PTE bits/markers, poison markers, and moved/installed PTE mappings. Transient state includes `mfill_state`, `ctx->map_changing_lock`, `ctx->mmap_changing`, PMD/PTE locks, folio locks/references, mmu notifier ranges, and hugetlb fault mutexes. Successful registration persists until explicit release, VMA modification, or process teardown.

## Dependencies and Integration Points

This file integrates with core mm locking (`mmap_lock`, per-VMA locks, page-table locks), VMA mutation from `vma.c`, folio allocation/rmap/LRU/memcg, shmem/filesystem `vm_uffd_ops`, hugetlb helpers, transparent huge page split/move helpers, swap and migration entries, mmu notifiers, TLB/cache flushing, soft-dirty support, and the userfaultfd context in `linux/userfaultfd_k.h`.

## Risks

- Many paths intentionally return `-EAGAIN` when mappings change, PMDs collapse/split, PTEs race, or per-VMA locking cannot stabilize the range. User space must be prepared to retry.
- `move_pages()` is conservative: shared, file-backed, PFNMAP/IO/MIXEDMAP/hugetlb/shadow-stack, non-writable, mlocked-mismatch, and protection-mismatch cases are rejected.
- Atomic fill can return partial progress; callers must not treat a short positive result as full success.
- Correctness depends on exact lock ordering between mmap locks, VMA locks, hugetlb locks, folio locks, and page-table locks.
- File-size checks prevent filling beyond EOF only while PTE locks are held; filesystem size and page-cache behavior are central to correctness.
- UFFD-WP on shared mappings changes write-notify/page-protection behavior, so interactions with dirty tracking and filesystem writeback need coverage.

## Test Signals

Signals include selftests for `UFFDIO_COPY`, `ZEROPAGE`, `CONTINUE`, `POISON`, `WRITEPROTECT`, and `MOVE`; hugetlb and THP variants; concurrent `mremap()`/`munmap()`/fork retry behavior; partial-progress/fatal-signal behavior; EOF fill rejection; WP marker support disabled/enabled cases; and mmu notifier/rmap validation under KASAN, lockdep, and debug VM configs.
