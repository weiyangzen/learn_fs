# sources/distributed-fs/ceph-client/mm/gup.c

## Purpose

`gup.c` implements the core get-user-pages and pin-user-pages machinery. It resolves user virtual addresses to `struct page` or `struct folio` references, handles slow faulting page-table walks and lockless GUP-fast walks, tracks the semantic difference between ordinary page references (`FOLL_GET`) and DMA pins (`FOLL_PIN`), and supplies the exported unpin APIs that callers must use after `pin_user_pages*()`. It also contains prefault helpers (`fault_in_*`, `__mm_populate()`, `populate_vma_page_range()`), coredump page lookup, long-term pin migration handling, and `memfd_pin_folios()`.

This code is central to kernel subsystems that need access to user memory without copying immediately: direct I/O, RDMA/ODP, GPU SVM, ptrace-like access, coredumps, `mlock()`/`MAP_POPULATE`, and memfd-backed sharing. The file is deliberately conservative because wrong pinning semantics can corrupt file-backed data, leak pages, or race with COW, fork, migration, and page-table teardown.

## Important APIs, Types, and Functions

The exported release APIs are `unpin_user_page()`, `unpin_user_pages()`, `unpin_user_pages_dirty_lock()`, `unpin_user_page_range_dirty_lock()`, `unpin_user_folio()`, `unpin_folio()`, and `unpin_folios()`. They funnel through `gup_put_folio()`, which reverses either exact large-folio pincount accounting or `GUP_PIN_COUNTING_BIAS` refcount accounting for small folios. `folio_add_pin()` and `folio_add_pins()` add extra logical pins to an already pinned folio.

The main exported acquisition APIs are `get_user_pages()`, `get_user_pages_remote()`, `get_user_pages_unlocked()`, `get_user_pages_fast()`, `get_user_pages_fast_only()`, `pin_user_pages()`, `pin_user_pages_remote()`, `pin_user_pages_unlocked()`, and `pin_user_pages_fast()`. The distinction is important: `get_*` APIs add ordinary references that are released with `put_page()`, while `pin_*` APIs set `FOLL_PIN` and require unpin routines. `is_valid_gup_args()` validates external flags, applies internal flags such as `FOLL_TOUCH`, `FOLL_REMOTE`, `FOLL_PIN`, `FOLL_GET`, `FOLL_UNLOCKABLE`, or `FOLL_FAST_ONLY`, and rejects invalid combinations such as simultaneous `FOLL_GET` and `FOLL_PIN`.

The slow path is built around `__get_user_pages_locked()` and `__get_user_pages()`. `__get_user_pages_locked()` owns or respects `mmap_lock` according to `locked`, handles retryable faults that can drop the lock, and sets `MMF_HAS_PINNED` for pin requests. `__get_user_pages()` iterates VMAs and pages, checks permissions via `check_vma_flags()`, resolves existing mappings through `follow_page_mask()`, faults missing or unsuitable mappings through `faultin_page()`, and fills the `pages[]` array with subpages from huge mappings when appropriate.

Page-table resolution is split by level: `follow_page_mask()` calls `follow_p4d_mask()`, `follow_pud_mask()`, `follow_pmd_mask()`, `follow_huge_pud()`, `follow_huge_pmd()`, and `follow_page_pte()`. These helpers enforce write permissions through `can_follow_write_pte()`, `can_follow_write_pmd()`, `can_follow_write_pud()`, and `can_follow_write_common()`, reject special pages for dumps, handle `PROT_NONE`, and return `-EMLINK` when an anonymous page must be unshared before a non-write pin can proceed.

The fast path is built around `gup_fast_fallback()`, `gup_fast()`, `gup_fast_pgd_range()`, `gup_fast_p4d_range()`, `gup_fast_pud_range()`, `gup_fast_pmd_range()`, `gup_fast_pud_leaf()`, `gup_fast_pmd_leaf()`, and `gup_fast_pte_range()`. It disables interrupts to stabilize page-table freeing, reads page-table entries locklessly, pins first via `try_grab_folio_fast()`, then verifies the page-table entry did not change. If fast walking cannot prove safety, it returns the pages pinned so far or falls back to the slow path unless `FOLL_FAST_ONLY` was requested.

Long-term pin handling is guarded by `__gup_longterm_locked()`, `check_and_migrate_movable_pages()`, `check_and_migrate_movable_folios()`, `collect_longterm_unpinnable_folios()`, and `migrate_longterm_unpinnable_folios()`. These functions ensure `FOLL_LONGTERM` pins do not indefinitely pin movable or otherwise unsuitable memory. The helper uses `pages_or_folios` to share logic between page arrays and folio arrays.

Other exported helper families include `fixup_user_fault()`, `fault_in_writeable()`, `fault_in_subpage_writeable()`, `fault_in_safe_writeable()`, `fault_in_readable()`, `get_dump_page()`, `populate_vma_page_range()`, `faultin_page_range()`, `__mm_populate()`, and `memfd_pin_folios()`.

## Control Flow

For ordinary slow GUP, exported wrappers validate flags, acquire or assert `mmap_lock`, and call `__get_user_pages_locked()`. That function calls `__get_user_pages()` in a loop. `__get_user_pages()` validates the current VMA, attempts `follow_page_mask()`, and either records a page, handles special error pointers, or calls `faultin_page()` to invoke `handle_mm_fault()`. If the fault can retry and releases the lock, the locked wrapper reacquires the lock, sets `FOLL_TRIED`, and resumes at the faulting address. Large folio and hugepage mappings are counted with `page_mask`, so one page-table hit can satisfy multiple pages and batch refcount or pincount increments.

For GUP-fast, `gup_fast_fallback()` normalizes the range, rejects overflow and kernel addresses, and calls `gup_fast()`. `gup_fast()` optionally samples `current->mm->write_protect_seq` for `FOLL_PIN`, disables interrupts, walks page tables without taking `mmap_lock`, and then rejects all fast pins if the write-protect sequence changed during the walk. Leaf handlers pin the folio before rechecking the page-table entry; if the entry changed, the pin is immediately dropped and the fast path aborts. If the fast path pins fewer pages than requested, the fallback slow path continues from the first missing page.

For long-term pins, `__gup_longterm_locked()` first pins with `FOLL_PIN`, then checks whether each pinned folio is long-term pinnable. If not, it unpins, isolates, and migrates the folios when possible, then retries the original pin. Device coherent folios are treated specially by converting the pin to an ordinary reference before device migration.

For memfd folio pinning, `memfd_pin_folios()` validates that the file is shmem or hugetlb, translates byte offsets into folio/page-cache indices, gathers contiguous folios from the file mapping, allocates missing folios via `memfd_alloc_folio()`, pins each folio with `FOLL_PIN`, records the offset into the first folio, and applies the same movable-folio migration loop as long-term GUP.

## State and Persistence Behavior

The file mutates page and folio reference state, folio `_pincount`, node stats (`NR_FOLL_PIN_ACQUIRED`, `NR_FOLL_PIN_RELEASED`), VMA/page-table accessed and dirty state, and the per-`mm_struct` `MMF_HAS_PINNED` flag. `FOLL_PIN` has persistent MM-level consequences because once an mm has seen pins, the flag remains for the mm lifetime. Pinning zero pages is special-cased to avoid useless refcount/pincount churn.

Dirtying helpers persist page-cache state by marking folios dirty before release. Prefault helpers intentionally do not retain pages, but they can instantiate page tables, allocate pages, set access/dirty state, and drain LRU batches. Long-term pin migration can move physical backing pages before returning to the caller, so callers must rely on returned pages rather than earlier PFNs. `memfd_pin_folios()` can allocate file-cache folios as a side effect.

## Dependencies and Integration Points

The file depends on core MM headers and subsystems: VMA lookup and permissions, page-table accessors, `handle_mm_fault()`, rmap anonymous exclusivity, hugetlb, THP, migration, memremap, shmem, memfd, secretmem, PCI P2PDMA, architecture cache/TLB/access helpers, and scheduler signal handling. Architecture integration is visible in `arch_make_folio_accessible()`, `arch_vma_access_permitted()`, `gup_fast_permitted()`, `pte_access_permitted()`, and TLB/page-table atomicity assumptions.

External users include drivers and filesystems that call `get_user_pages*()` or `pin_user_pages*()`, RDMA and GPU code that request `FOLL_LONGTERM`, coredump code via `get_dump_page()`, futex-like code via `fixup_user_fault()`, and VM code for `mlock()`/`MAP_POPULATE`. The local test files `gup_test.c` and `gup_test.h` expose direct debugfs/ioctl exercise points for these APIs.

## Risks and Edge Cases

The highest-risk area is COW and write-protect interaction. GUP-fast must not pin a shared anonymous page during fork write-protection; sequence checking and `PageAnonExclusive()` assertions are the primary safety signals. `gup_must_unshare()` returning `-EMLINK` ensures non-write pins break COW when required.

Long-term pins on file-backed or movable memory are dangerous. `writable_file_mapping_allowed()` rejects long-term writable pins on mappings that need dirty tracking, and migration checks prevent indefinite pins of movable memory. Bugs here can surface as filesystem writeback corruption, failed memory hot-unplug/migration, or pinned pages that never become reclaimable.

The fast path is intentionally incomplete. It must fall back for secretmem, ambiguous file-backed mappings, PTE-special entries, protnone entries, P2PDMA without permission, unsupported architecture conditions, and page-table races. Any future change that expands fast-path acceptance must preserve the pin-before-recheck ordering and barriers paired with COW/rmap code.

Return semantics are subtle: partial success returns a positive count even when a later page fails; callers must release exactly that many pages. `pin_user_pages_remote()` and `pin_user_pages()` return `0` rather than `-EINVAL` for invalid arguments in some wrapper cases, which is an API quirk worth preserving unless all callers are audited.

## Test Signals

Direct test signals come from `CONFIG_GUP_TEST`, `/sys/kernel/debug/gup_test`, and selftests under `tools/testing/selftests/mm` that include `mm/gup_test.h`. Relevant scenarios include GUP-fast vs slow GUP, `FOLL_PIN` vs `FOLL_GET`, long-term pin rejection/migration, COW behavior under fork, dump-page operation, and subpage/MTE write probing. Runtime debug signals include `CONFIG_DEBUG_VM` warnings in `sanity_check_pinned_pages()`, `VM_WARN_ON_ONCE_PAGE()` for anonymous pin exclusivity, folio refcount warnings, and page dumps emitted by `gup_test.c`.
