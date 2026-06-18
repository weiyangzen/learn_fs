# Research: subset-b-006126

Work item `subset-b-006126` covers Linux memory-management helpers copied under `sources/distributed-fs/ceph-client/mm`. The files form a connected cluster around get-user-pages (GUP), debug coverage for GUP/pin behavior, highmem kernel mappings, and HMM page-table/DMA translation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/gup.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/gup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/gup_test.c -->
# sources/distributed-fs/ceph-client/mm/gup_test.c

## Purpose

`gup_test.c` provides a debugfs-backed test and benchmark interface for the GUP and PUP APIs implemented in `gup.c`. When `CONFIG_GUP_TEST` is enabled, late init creates `/sys/kernel/debug/gup_test` with ioctl commands defined in `gup_test.h`. User-space selftests and benchmark tools use this node to pin or get user pages in controlled batches, measure acquisition and release time, dump selected pages, and keep a long-term pin live across ioctl calls for COW and migration tests.

## Important APIs, Types, and Functions

The file registers `gup_test_fops` with `nonseekable_open`, `gup_test_ioctl`, `compat_ptr_ioctl`, and `gup_test_release`. The main dispatcher, `gup_test_ioctl()`, accepts benchmark/test commands (`GUP_FAST_BENCHMARK`, `PIN_FAST_BENCHMARK`, `PIN_LONGTERM_BENCHMARK`, `GUP_BASIC_TEST`, `PIN_BASIC_TEST`, `DUMP_USER_PAGES_TEST`) and long-term fixture commands (`PIN_LONGTERM_TEST_START`, `PIN_LONGTERM_TEST_STOP`, `PIN_LONGTERM_TEST_READ`).

`__gup_test_ioctl()` copies a `struct gup_test` from userspace, allocates a `struct page **` array, optionally takes `current->mm->mmap_lock`, loops over the requested address range in `nr_pages_per_call` chunks, invokes the requested GUP API, records elapsed microseconds for get/pin and release phases, optionally verifies DMA-pinned state, optionally dumps selected pages, and releases pages with either `put_page()` or `unpin_user_pages()`.

`put_back_pages()` mirrors the acquisition mode: ordinary GUP commands call `put_page()`, pin commands call `unpin_user_pages()`, and dump mode chooses according to `GUP_TEST_FLAG_DUMP_PAGES_USE_PIN`. `verify_dma_pinned()` checks `folio_maybe_dma_pinned()` for pin commands and `folio_is_longterm_pinnable()` for long-term pin benchmarks, warning and dumping a page on mismatch.

The stateful long-term fixture uses `pin_longterm_test_mutex`, `pin_longterm_test_pages`, and `pin_longterm_test_nr_pages`. `pin_longterm_test_start()` copies a `struct pin_longterm_test`, validates page alignment and flags, allocates an array, then calls `pin_user_pages()` or `pin_user_pages_fast()` with `FOLL_LONGTERM` and optional `FOLL_WRITE` until the full range is pinned or a failure occurs. `pin_longterm_test_read()` maps each pinned page with `kmap_local_page()`, copies one page at a time to a user-provided destination, and unmaps with `kunmap_local()`. `pin_longterm_test_stop()` unpins and frees the stored array, and `gup_test_release()` stops the fixture when the debugfs file is closed.

## Control Flow

The benchmark path is single-ioctl and mostly stateless. `gup_test_ioctl()` copies the input structure, `__gup_test_ioctl()` allocates storage, acquires `mmap_lock` for non-fast commands, walks the address interval, and stops early when a call returns fewer pages than requested or an error. It then updates the user-visible `get_delta_usec`, `put_delta_usec`, and adjusted `size` fields before copying the structure back to userspace. The actual return code remains `0` unless there was an ioctl, copy, allocation, or locking error; partial page acquisition is communicated through the adjusted structure.

The long-term fixture path is multi-ioctl. `PIN_LONGTERM_TEST_START` owns the global page array until `PIN_LONGTERM_TEST_STOP`, file release, or a failed start cleanup. The mutex serializes start/read/stop and prevents concurrent fixtures. `PIN_LONGTERM_TEST_READ` does not expose kernel addresses; it copies page contents through temporary local mappings.

## State and Persistence Behavior

Most benchmark state is transient and freed before ioctl return. The long-term fixture intentionally persists pinned pages in static globals, holding DMA pins across ioctl calls so user-space tests can modify mappings, fork, or otherwise observe COW behavior while the kernel retains pins. The state is process-independent at the file implementation level because the globals are file-static, so only one long-term fixture can exist system-wide for this debugfs node.

The file mutates user-provided `struct gup_test` fields before copying back, emits kernel warnings and `dump_page()` diagnostics, and can keep pages pinned until stop or release. It relies on `gup.c` for all actual pin semantics and on `highmem.c` `kmap_local_page()` support when reading pinned pages.

## Dependencies and Integration Points

Dependencies include `linux/debugfs.h`, `linux/highmem.h`, `linux/uaccess.h`, `linux/ktime.h`, and `gup_test.h`. The command numbers and ABI structures are shared with in-tree selftests such as `tools/testing/selftests/mm/gup_test.c` and COW tests that include `mm/gup_test.h`. The debugfs creation is conditional on `CONFIG_GUP_TEST` via `mm/Makefile` and `mm/Kconfig`.

## Risks and Edge Cases

The test interface is privileged by debugfs mode `0600`, but it still pins arbitrary current-process user memory and can consume memory proportional to `size / PAGE_SIZE`. `nr_pages_per_call` must be sensible; a zero value would make progress impossible in the loop, so user-space tests must provide a nonzero batch size. The long-term fixture returns `-EINVAL` if already active, but because state is global, concurrent unrelated test processes can interfere. `pin_longterm_test_start()` advances the local `pages` pointer while preserving the original in `pin_longterm_test_pages`; cleanup must always use the global original pointer, which it does.

`pin_longterm_test_read()` copies full pages to a user address without independently validating the destination range up front; it relies on `copy_to_user()` failure handling. Benchmark commands that acquire zero pages still perform release timing over zero pages and report the shortened `size`.

## Test Signals

This file is itself a test hook. Strong signals are successful open/ioctl cycles on `/sys/kernel/debug/gup_test`, passing selftests under `tools/testing/selftests/mm`, absence of `verify_dma_pinned()` warnings, expected page dumps for `DUMP_USER_PAGES_TEST`, and correct cleanup on file release. Long-term tests should verify both slow and fast pin modes, optional write pins, COW behavior after fork, readback through `PIN_LONGTERM_TEST_READ`, and cleanup through both explicit stop and close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/gup_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/gup_test.h -->
# sources/distributed-fs/ceph-client/mm/gup_test.h

## Purpose

`gup_test.h` defines the user/kernel ABI for the debugfs GUP test driver in `gup_test.c`. It is shared with in-tree user-space selftests, so its ioctl numbers, structure layouts, and flag meanings must remain stable for compatible test binaries.

## Important APIs, Types, and Functions

The header defines ioctl commands with the `'g'` type: `GUP_FAST_BENCHMARK`, `PIN_FAST_BENCHMARK`, `PIN_LONGTERM_BENCHMARK`, `GUP_BASIC_TEST`, `PIN_BASIC_TEST`, `DUMP_USER_PAGES_TEST`, `PIN_LONGTERM_TEST_START`, `PIN_LONGTERM_TEST_STOP`, and `PIN_LONGTERM_TEST_READ`. The benchmark and dump commands use `struct gup_test`; long-term start uses `struct pin_longterm_test`; long-term read accepts a `__u64` user destination address.

`struct gup_test` contains timing outputs (`get_delta_usec`, `put_delta_usec`), input range (`addr`, `size`), batching (`nr_pages_per_call`), raw GUP flags (`gup_flags`), test-specific flags (`test_flags`), and up to `GUP_TEST_MAX_PAGES_TO_DUMP` one-based page indices in `which_pages`. `GUP_TEST_FLAG_DUMP_PAGES_USE_PIN` selects pin vs get behavior for dump mode.

`struct pin_longterm_test` contains an address, size, and flags. `PIN_LONGTERM_TEST_FLAG_USE_WRITE` adds `FOLL_WRITE`; `PIN_LONGTERM_TEST_FLAG_USE_FAST` selects `pin_user_pages_fast()` instead of slow `pin_user_pages()`.

## Control Flow

The header has no runtime control flow, but it shapes ioctl dispatch in `gup_test.c`. `_IOWR` commands copy a structure in and back out, allowing the kernel to return timing and adjusted-size fields. `_IOW` commands copy input only. `PIN_LONGTERM_TEST_STOP` carries no payload and triggers cleanup of the persistent fixture.

## State and Persistence Behavior

The structures are ABI state exchanged with user space. `struct gup_test` is both input and output; the kernel overwrites timing fields and adjusts `size` to the processed range. The header itself stores no state, but changes to field order, type width, command numbers, or flag values would break compiled selftests and external diagnostic tools.

## Dependencies and Integration Points

The only include is `linux/types.h` for fixed-width kernel ABI types. The header is included by `mm/gup_test.c` and by selftests under `tools/testing/selftests/mm`, including COW and GUP benchmark tests. It also appears in documentation for pin-user-pages testing.

## Risks and Edge Cases

The ABI uses `__u64` for user addresses so 32-bit compatibility depends on `compat_ptr_ioctl` and explicit casting in `gup_test.c`. `which_pages` uses one-based indexing where zero means "do nothing"; tests must not treat entries as zero-based. `gup_flags` passes raw kernel `FOLL_*` values from user test code to the debugfs helper, so test binaries must be built against matching kernel headers.

## Test Signals

The primary signal is that in-tree selftests compile against this header and can drive `/sys/kernel/debug/gup_test`. ABI regressions usually show up as ioctl failures, incorrect timing/size copyback, wrong page dump selection, or long-term fixture commands being rejected unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/gup_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/highmem.c -->
# sources/distributed-fs/ceph-client/mm/highmem.c

## Purpose

`highmem.c` implements common high-memory mapping support and local kmap infrastructure. On systems where not all physical memory is permanently mapped into the kernel virtual address space, it manages persistent highmem mappings (`kmap_high()`/`kunmap_high()`), temporary per-task/per-CPU local mappings (`kmap_local_page()` implementation helpers), page-address lookup for highmem pages, and helper routines such as `zero_user_segments()`.

The code is used by MM, block, filesystem, and test code that needs a kernel virtual address for a `struct page`. In this work item, `gup_test.c` uses `kmap_local_page()` and `kunmap_local()` to read long-term pinned pages.

## Important APIs, Types, and Functions

For `CONFIG_HIGHMEM`, the exported APIs are `__nr_free_highpages()`, `__totalhigh_pages()`, `__kmap_to_page()`, `kmap_high()`, optional `kmap_high_get()`, `kunmap_high()`, `__kmap_flush_unused()`, and `zero_user_segments()`. The central persistent mapping state is `pkmap_count[LAST_PKMAP]`, `pkmap_page_table`, and `kmap_lock`. The count has three states: `0` means reusable and flushed, `1` means unused but still needs a TLB flush, and `>1` means active users plus the reserved count.

`map_new_virtual()` finds or waits for a free PKMAP slot, handles architecture cache-color callbacks (`get_pkmap_color()`, `get_next_pkmap_nr()`, `no_more_pkmaps()`), installs a PTE with `set_pte_at()`, initializes `pkmap_count`, and records the reverse mapping with `set_page_address()`. `flush_all_zero_pkmaps()` clears slots with count `1`, removes page-address associations, and flushes the kernel TLB range.

For `CONFIG_KMAP_LOCAL`, exported helpers include `__kmap_local_pfn_prot()`, `__kmap_local_page_prot()`, and `kunmap_local_indexed()`, while scheduler hooks `__kmap_local_sched_out()`, `__kmap_local_sched_in()`, and `kmap_local_fork()` preserve/clear local mappings across context switch and fork. Local mapping state lives in `current->kmap_ctrl.idx` and `current->kmap_ctrl.pteval[]`; the slot index is adjusted for CPU and architecture-specific mapping functions.

For `HASHED_PAGE_VIRTUAL`, the file defines `struct page_address_map`, `struct page_address_slot`, `page_address()`, `set_page_address()`, and `page_address_init()` to map highmem pages to their persistent virtual addresses through a hash table.

## Control Flow

Persistent highmem mapping starts in `kmap_high()`: take `kmap_lock`, check whether `page_address(page)` already exists, allocate a new virtual slot if necessary, increment `pkmap_count`, then unlock. If no slot is immediately available, `map_new_virtual()` flushes stale slots and eventually sleeps on a color-specific wait queue until another task calls `kunmap_high()`. Unmapping decrements `pkmap_count`; when it reaches `1`, the slot cannot be reused until `flush_all_zero_pkmaps()` clears the PTE and performs the required TLB flush.

Local mapping starts in `__kmap_local_page_prot()`. Lowmem pages can return `page_address(page)` directly unless debug-forced mapping is enabled. Highmem pages try an architecture-provided existing mapping, otherwise `__kmap_local_pfn_prot()` disables migration and preemption, pushes a per-task kmap index, computes the fixmap virtual address, verifies the PTE is clear, installs a PTE, records the PTE value in task state, and re-enables preemption. `kunmap_local_indexed()` validates stack-like unmap order, clears the PTE, pops the index, and re-enables migration.

During scheduling, `__kmap_local_sched_out()` clears all active local mapping PTEs for the outgoing task without changing the nesting index; `__kmap_local_sched_in()` restores them for the incoming task. This preserves the guarantee that a local kmap virtual address remains valid for the task even across preemption, while still preventing stale mappings from being active on the wrong CPU.

`zero_user_segments()` iterates over base pages in a possibly compound page, maps each page locally only if needed, zeroes up to two byte ranges, unmaps, flushes dcache, and validates that requested ranges were fully consumed.

## State and Persistence Behavior

Persistent kmap state is global: PKMAP PTEs, counts, wait queues, and page-address associations remain until unmapped and flushed. Local kmap state is per task and per CPU-derived slot; migration is disabled while local mappings are live so the computed fixmap address remains stable. `kmap_local_fork()` warns and clears inherited kmap state in a forked task.

`page_address()` state may be direct lowmem mapping or hash-table state for highmem persistent mappings. `zero_user_segments()` mutates page contents and dcache state but does not retain mappings.

## Dependencies and Integration Points

The file depends on architecture fixmap and PTE helpers, TLB/cache flushing, highmem configuration, task `kmap_ctrl`, page flags, wait queues, spinlocks, and optional architecture hooks for color-sensitive caches or non-linear local kmap PTE arrays. Its exported APIs are used broadly by filesystems, block code, networking, memory tests, and GUP tests needing temporary page access.

## Risks and Edge Cases

The persistent PKMAP count protocol is fragile: a slot at count `1` cannot be reused before TLB flushing, and waking waiters before the count reaches a reusable state would race. `kmap_high()` can sleep and must not be used in interrupt context. `kmap_high_get()` has architecture-specific locking because some architectures need it from any context.

Local kmap is stack-like. Unmapping out of order, migrating while a mapping is live, or losing scheduler save/restore state can leave wrong PTEs visible or trigger debug warnings. Debug modes intentionally reserve guard slots and force lowmem pages through the mapping path, which broadens test coverage but changes performance.

`__kmap_to_page()` has warning paths for addresses in PKMAP or fixmap ranges and falls back to `virt_to_page()` otherwise. Incorrect virtual-address classification could return the wrong page for debugging or address translation users.

## Test Signals

Useful signals include highmem boot tests, `CONFIG_DEBUG_KMAP_LOCAL` warnings, scheduler preemption tests with nested `kmap_local_page()` mappings, `zero_user_segments()` coverage for compound pages and split ranges, and GUP long-term readback through `gup_test.c`. On highmem architectures, stress tests should exercise PKMAP exhaustion, wait/wakeup behavior, TLB flush reuse, and hashed `page_address()` add/remove behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/highmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hmm.c -->
# sources/distributed-fs/ceph-client/mm/hmm.c

## Purpose

`hmm.c` implements the core heterogeneous memory management range-fault walker and HMM DMA mapping helpers. HMM lets device drivers mirror CPU page-table state into device page tables or DMA mappings while coordinating with MMU interval notifiers. The file converts CPU PTE/PMD/PUD/hugetlb entries into `HMM_PFN_*` encoded PFNs, optionally faults pages in, handles device-private/exclusive/migration entries, and provides helper functions to allocate, map, and unmap DMA addresses for HMM PFN arrays.

Primary users in this tree include GPU SVM code and RDMA ODP code. The grep results show integration in DRM GPU SVM (`drivers/gpu/drm/drm_gpusvm.c`, Nouveau, AMDGPU/KFD), RDMA ODP (`drivers/infiniband/core/umem_odp.c`, mlx5, rxe), Hyper-V memory regions, and accelerator code.

## Important APIs, Types, and Functions

The main exported page-table API is `hmm_range_fault(struct hmm_range *range)`. The caller supplies a range with `start`, `end`, `notifier`, `notifier_seq`, `hmm_pfns`, `default_flags`, `pfn_flags_mask`, and optional `dev_private_owner`. The output array stores encoded PFNs plus flags such as `HMM_PFN_VALID`, `HMM_PFN_WRITE`, `HMM_PFN_ERROR`, order bits, and preserved DMA/P2P flags.

Internal walker state is `struct hmm_vma_walk`, which stores the range and the last unprocessed address. `hmm_walk_ops` hooks into generic pagewalk with `hmm_vma_walk_pud()`, `hmm_vma_walk_pmd()`, `hmm_vma_walk_hole()`, `hmm_vma_walk_hugetlb_entry()`, and `hmm_vma_walk_test()`.

Fault-decision helpers are `hmm_pte_need_fault()` and `hmm_range_need_fault()`. They combine per-PFN request bits with range defaults to decide whether a missing, read-only, or nonpresent entry requires a read or write fault. `hmm_vma_fault()` invokes `handle_mm_fault()` with `FAULT_FLAG_REMOTE` and optional `FAULT_FLAG_WRITE`, returning `-EBUSY` after a fault so `hmm_range_fault()` restarts safely from the recorded address.

Entry conversion helpers include `pte_to_hmm_pfn_flags()`, `pmd_to_hmm_pfn_flags()`, `pud_to_hmm_pfn_flags()`, `hmm_vma_handle_pte()`, `hmm_vma_handle_pmd()`, and `hmm_vma_handle_absent_pmd()`. They preserve input/output DMA flags through `HMM_PFN_INOUT_FLAGS`, report unsupported mappings as `HMM_PFN_ERROR`, and handle device-private pages owned by the caller without forcing migration back to system memory.

The exported DMA helpers are `hmm_dma_map_alloc()`, `hmm_dma_map_free()`, `hmm_dma_map_pfn()`, and `hmm_dma_unmap_pfn()`. They maintain `struct hmm_dma_map` arrays for PFNs and optional DMA addresses, support DMA IOVA state where possible, reject devices that require sync or limited addressing, and handle PCI P2PDMA states.

## Control Flow

`hmm_range_fault()` requires the caller to hold the mm mmap lock. It initializes `last` to `range->start`, checks `mmu_interval_check_retry()` against `range->notifier_seq`, and calls `walk_page_range()` from the last unprocessed address to the end. If a handler returns `-EBUSY` after faulting or waiting on migration, the loop retries; entries before `last` have already been stored, while later entries retain their input request flags.

For holes and unsupported VMAs, the walker either faults if requested or fills output entries with zero/no-valid or `HMM_PFN_ERROR`. For PTEs, `hmm_vma_handle_pte()` distinguishes empty/UFFD-WP markers, nonpresent softleaf entries, device-private pages owned by the caller, swap/device/migration entries, special mappings without normal pages, and normal present PTEs. Migration entries wait and return `-EBUSY`; swap or device entries fault when requested; unknown nonpresent entries fail.

For huge mappings, PMD/PUD/hugetlb handlers compute a base PFN plus page offset, attach valid/write/order flags, and populate each page-sized slot in `hmm_pfns[]`. The code generally avoids splitting huge mappings and relies on MMU notifier invalidation to handle concurrent splits. Hugetlb write faults drop the hugetlb VMA lock before calling `hmm_vma_fault()` to avoid deadlock.

DMA mapping starts with `hmm_dma_map_alloc()`, which allocates PFN storage, optional DMA storage, and possibly an IOVA range. `hmm_dma_map_pfn()` converts the encoded HMM PFN to `struct page`/physical address, handles already-mapped entries, consults PCI P2PDMA state, then either links an IOVA, maps a physical address, or returns a P2P bus address. `hmm_dma_unmap_pfn()` reverses the operation if the PFN has both valid and DMA-mapped bits, clearing DMA/P2P flags afterward.

## State and Persistence Behavior

`hmm_range_fault()` mutates the caller-provided `hmm_pfns[]` array in place. It preserves `HMM_PFN_DMA_MAPPED`, `HMM_PFN_P2PDMA`, and `HMM_PFN_P2PDMA_BUS` bits from input to output so callers can reuse DMA state across faults or permission upgrades. It does not pin pages; validity is tied to the caller's MMU interval notifier sequence, and callers must retry if invalidation races are detected.

DMA helpers persist allocations in `struct hmm_dma_map`: PFN arrays, optional DMA address arrays, and IOVA state. `hmm_dma_map_pfn()` sets mapping flags in `pfn_list[idx]`; `hmm_dma_unmap_pfn()` clears them. P2P bus mappings set `HMM_PFN_P2PDMA_BUS` and do not require normal DMA unmap.

## Dependencies and Integration Points

The file depends on generic pagewalk, MMU interval notifiers, `handle_mm_fault()`, softleaf swap/device/migration entry helpers, THP and hugetlb support, device-private memory, memory hotplug, DMA mapping APIs, DMA IOVA helpers, and PCI P2PDMA. It exports symbols for device drivers rather than core user APIs.

Callers must coordinate with `mmu_interval_read_begin()`/retry and usually hold driver-specific locks that protect mirrored device page tables. RDMA ODP uses the DMA helpers to back hardware page tables; GPU SVM uses `hmm_range_fault()` to resolve CPU mappings for device faults and migrations.

## Risks and Edge Cases

The API is race-sensitive. `hmm_range_fault()` reads CPU page tables without pinning pages, so the notifier sequence is the validity contract. Callers that ignore `-EBUSY` or fail to retry on interval invalidation can program stale device mappings. Permission upgrades must preserve and resync DMA state correctly when an already mapped PFN gains write permission.

Fault policy is subtle because request bits can come from range defaults or individual PFN entries. Unsupported VMAs return `HMM_PFN_ERROR` only when no fault was requested; if a valid PFN was requested, they return hard failure. Device-private entries owned by the caller are reported directly, while other device/private/exclusive/swap entries usually require faulting or fail.

DMA helper restrictions are important. Devices requiring DMA sync or limited addressing are rejected because HMM cannot transfer buffer ownership under normal streaming DMA rules. P2PDMA path selection must match the target device; clearing only some mapping bits on errors would leak stale state, so the error paths and unmap paths deserve careful testing.

## Test Signals

Test signals come from driver selftests and runtime paths that exercise device faults: RDMA ODP page fault tests, GPU SVM fault/migration tests, P2PDMA mapping coverage, hugetlb/THP ranges, migration-entry waits, and MMU notifier invalidation retries. In-tree users contain assertions such as RDMA ODP checks that faulted ranges have `HMM_PFN_VALID` and not `HMM_PFN_ERROR`. DMA tests should verify map/unmap idempotence, IOVA and non-IOVA backends, P2PDMA bus mappings, and permission-upgrade remapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/hmm.c -->
