# Group Research: group_887_linux_sources_os_linux_linux_mm_gup_c_sources_os_linux_linux_mm_gup__48b3904520a8

Scope: `Docs/research_subset_a.md`

Files researched:

- `sources/os/linux/linux/mm/gup.c`
- `sources/os/linux/linux/mm/gup_test.c`
- `sources/os/linux/linux/mm/gup_test.h`
- `sources/os/linux/linux/mm/highmem.c`
- `sources/os/linux/linux/mm/hmm.c`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/gup.c -->
# File Research: sources/os/linux/linux/mm/gup.c

## Purpose

`gup.c` is the Linux memory-management implementation of get-user-pages and pin-user-pages APIs. It translates user virtual address ranges into referenced `struct page` pointers, optionally faults pages into existence, and distinguishes ordinary references (`FOLL_GET`) from DMA-style pins (`FOLL_PIN`). It also contains the fast lockless page-table walker, slow faulting path, long-term pin migration checks, page/folio unpin helpers, prefault helpers, and memfd folio pinning support.

## Major Responsibilities

- Implement public GUP/PUP entry points: `get_user_pages*()`, `pin_user_pages*()`, fast-only variants, remote variants, and unlocked variants.
- Walk page tables through PTE/PMD/PUD levels and follow normal pages, huge PMDs/PUDs, zero pages, gate pages, and special PFN mappings.
- Fault missing or insufficiently permitted mappings with `handle_mm_fault()` when the caller allows the slow path.
- Enforce VMA access rules, architecture access permissions, `FOLL_FORCE`, write/COW semantics, secretmem rejection, and DAX/long-term restrictions.
- Track DMA pins separately from ordinary page references using folio pincounts or `GUP_PIN_COUNTING_BIAS`.
- Provide unpin APIs that optionally dirty pages and collapse repeated pages from the same folio for efficient refcount updates.
- Support long-term pins by rejecting or migrating movable/unpinnable folios before returning them pinned.
- Provide prefault helpers such as `fault_in_readable()`, `fault_in_writeable()`, `fault_in_safe_writeable()`, `populate_vma_page_range()`, `faultin_page_range()`, and `__mm_populate()`.
- Pin folios belonging to memfd-backed shmem or hugetlb files through `memfd_pin_folios()`.

## Reference and Pin Accounting

The central helpers are:

- `try_get_folio()`: safely raises a folio refcount after checking that the original page still belongs to the same folio.
- `try_grab_folio()`: implements `FOLL_GET` or `FOLL_PIN` behavior for slow paths.
- `try_grab_folio_fast()`: fast-path version used with interrupts disabled.
- `gup_put_folio()`: releases either ordinary references or DMA pins.

`FOLL_PIN` differs from `FOLL_GET`: zero folios are deliberately not pinned, large folios with a dedicated pincount update `_pincount`, and smaller folios encode pins by adding `GUP_PIN_COUNTING_BIAS` to the normal refcount. Pin acquisition and release update `NR_FOLL_PIN_ACQUIRED` and `NR_FOLL_PIN_RELEASED`.

Debug checks in `sanity_check_pinned_pages()` verify that anonymous pinned pages remain exclusive, because once a page is pinned the kernel cannot safely convert it into a shared anonymous mapping. The file also rejects PCI P2PDMA pages unless `FOLL_PCI_P2PDMA` is explicitly allowed.

## Unpin and Dirtying APIs

Exported release helpers include:

- `unpin_user_page()`
- `unpin_folio()`
- `unpin_user_pages()`
- `unpin_user_folio()`
- `unpin_folios()`
- `unpin_user_pages_dirty_lock()`
- `unpin_user_page_range_dirty_lock()`
- `folio_add_pin()`
- `folio_add_pins()`

Dirtying variants group adjacent pages that belong to the same folio, mark clean folios dirty under the folio lock when requested, and then release the corresponding number of pins. The non-dirty unpin path also groups repeated folios to avoid redundant accounting. `gup_fast_unpin_user_pages()` is a fast-path rollback helper and intentionally skips some debug checks because it can run after a fork race invalidated exclusivity assumptions.

## Slow GUP Path

The slow path begins in `__get_user_pages_locked()` and calls `__get_user_pages()`. It requires or acquires `mmap_lock`, optionally allows the fault handler to drop it, and loops over VMAs and page-table mappings until the requested range is processed or an error occurs.

Important slow-path helpers:

- `gup_vma_lookup()`: VMA lookup with diagnostics for historical stack-growth behavior.
- `check_vma_flags()`: rejects VM_IO, VM_PFNMAP, secretmem, incompatible anonymous/file mappings, shadow stacks, FSDAX long-term pins, and permission violations.
- `follow_page_mask()`: top-level page-table follower.
- `follow_p4d_mask()`, `follow_pud_mask()`, `follow_pmd_mask()`, `follow_page_pte()`: page-table level walkers.
- `follow_huge_pud()` and `follow_huge_pmd()`: huge leaf handlers.
- `faultin_page()`: converts GUP flags to `FAULT_FLAG_*` and invokes `handle_mm_fault()`.
- `get_gate_page()`: handles architecture gate/vDSO-like pages.

`__get_user_pages()` can return partial success. If a page is missing or a read-only mapping must be unshared for `FOLL_PIN`, it calls `faultin_page()` and retries. It handles `-EMLINK` as an unshare request, `-EEXIST` for PFN mappings without `struct page`, and copies subpages of large folios into the caller's page array while taking the extra references needed for the whole range.

## Write, COW, and Long-Term Safety

The file is careful about write access. `can_follow_write_common()`, `can_follow_write_pte()`, `can_follow_write_pmd()`, and `can_follow_write_pud()` allow `FOLL_FORCE` only for private COW-capable mappings where the anonymous page is exclusive and no soft-dirty or userfaultfd write-protect condition requires a real write fault.

`writable_file_mapping_allowed()` prevents the most problematic case: a long-term `FOLL_PIN | FOLL_WRITE` against a file-backed mapping that needs dirty tracking. That scenario can bypass filesystem write-notify semantics and silently dirty data through the direct kernel mapping.

Long-term pins are routed through `__gup_longterm_locked()`. When `FOLL_LONGTERM` is present, pages are first pinned, then `check_and_migrate_movable_pages()` verifies that the resulting folios are long-term pinnable. If not, `collect_longterm_unpinnable_folios()` isolates movable folios or identifies device-coherent folios, and `migrate_longterm_unpinnable_folios()` unpins and migrates them. Successful migration returns `-EAGAIN` internally so the full range is pinned again.

## Fast GUP Path

`gup_fast_fallback()` drives the fast path. It validates the user range, tries `gup_fast()`, and only falls back to slow GUP if the fast path did not pin all pages and the caller did not request `FOLL_FAST_ONLY`.

Fast GUP is compiled under `CONFIG_HAVE_GUP_FAST`. It disables interrupts while walking page tables so page-table pages cannot be freed underneath the walker. The hierarchy is:

- `gup_fast_pgd_range()`
- `gup_fast_p4d_range()`
- `gup_fast_pud_range()`
- `gup_fast_pmd_range()`
- `gup_fast_pte_range()`
- `gup_fast_pmd_leaf()`
- `gup_fast_pud_leaf()`

Fast PTE handling pins the folio first, then verifies that both the higher-level entry and the PTE still match. If anything changed, the pin is released and the caller falls back. Fast GUP rejects PROT_NONE, inaccessible entries, special PTEs, unsafe long-term writable file-backed folios, secretmem folios, and mappings requiring anonymous unsharing.

For `FOLL_PIN`, `gup_fast()` also samples `current->mm->write_protect_seq`; if fork write-protection races with a DMA pin, fast-pinned pages are unpinned and the slow path is used.

## Public APIs and Return Conventions

Public APIs validate external flags through `is_valid_gup_args()`, which blocks internal-only flags, enforces `FOLL_GET` and `FOLL_PIN` mutual exclusion, requires `pages` for get/pin operations, and rejects invalid `FOLL_LONGTERM` combinations.

Key exported entry points:

- `get_user_pages_remote()`
- `get_user_pages()`
- `get_user_pages_unlocked()`
- `get_user_pages_fast_only()`
- `get_user_pages_fast()`
- `pin_user_pages_remote()`
- `pin_user_pages()`
- `pin_user_pages_unlocked()`
- `pin_user_pages_fast()`
- `fixup_user_fault()`
- `get_dump_page()`

Most APIs return the number of pages pinned/referenced, possibly less than requested, or a negative error if no pages were obtained. Some pin APIs return `0` on argument-validation failure paths where older API behavior expects that convention.

## Prefault and Population Helpers

The file also provides user-memory prefault helpers used by copy loops, mlock, MAP_POPULATE, and `MADV_POPULATE_*`.

- `fault_in_writeable()` and `fault_in_readable()` probe userspace with unsafe access helpers and return the number of bytes not faulted in.
- `fault_in_subpage_writeable()` adds sub-page permission probing for cases such as arm64 MTE.
- `fault_in_safe_writeable()` resolves write faults via `fixup_user_fault()` without writing to the target memory.
- `populate_vma_page_range()` faults in a single VMA range and respects `VM_LOCKONFAULT`, access permissions, and COW behavior.
- `faultin_page_range()` is the MADV_POPULATE-oriented helper with stricter error reporting.
- `__mm_populate()` walks VMAs without an initial `mmap_lock` and faults in eligible ranges.

## memfd Folio Pinning

`memfd_pin_folios()` pins folios from shmem or hugetlb-backed memfd files over a byte range. It looks up contiguous page-cache folios with `filemap_get_folios_contig()`, allocates missing folios through `memfd_alloc_folio()`, records the offset into the first folio, and then runs long-term migration checks using the folio-oriented migration wrapper. Callers must release the returned folios with `unpin_folios()` or `unpin_folio()`.

## Integration Points

This file sits at the boundary between the VM, filesystems, DMA, core dumping, futex-style fault fixups, memory migration, hugetlb, transparent huge pages, secretmem, shmem, memfd, and architecture page-table code. Its invariants are consumed broadly: DMA users rely on `FOLL_PIN` accounting, filesystems rely on long-term write restrictions, fork relies on write-protect sequence detection, and mmu/page-table code relies on the fast walker respecting TLB and page-table lifetime rules.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/gup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/gup_test.c -->
# File Research: sources/os/linux/linux/mm/gup_test.c

## Purpose

`gup_test.c` implements the kernel-side debugfs test and benchmark interface for GUP and PUP operations. It exposes `/sys/kernel/debug/gup_test` with ioctl commands that exercise fast GUP, slow GUP, fast pinning, slow pinning, long-term pinning, selected page dumping, and a stateful long-term pin/read/stop workflow.

## Major Responsibilities

- Dispatch `gup_test.h` ioctl commands through a debugfs file.
- Benchmark GUP/PUP acquisition and release times using `ktime_get()` and microsecond deltas.
- Allocate a temporary `struct page **` array for the requested user range.
- Take `mmap_read_lock()` for operations that require the slow path.
- Release returned pages correctly: `put_page()` for `FOLL_GET` style commands and `unpin_user_pages()` for `FOLL_PIN` commands.
- Verify that pin-oriented tests actually returned folios that appear DMA-pinned.
- Optionally dump selected pages for diagnostics.
- Maintain a global stateful long-term pin test buffer until explicit stop or file release.

## Main Ioctl Flow

`gup_test_ioctl()` accepts:

- `GUP_FAST_BENCHMARK`
- `PIN_FAST_BENCHMARK`
- `PIN_LONGTERM_BENCHMARK`
- `GUP_BASIC_TEST`
- `PIN_BASIC_TEST`
- `DUMP_USER_PAGES_TEST`
- `PIN_LONGTERM_TEST_START`
- `PIN_LONGTERM_TEST_STOP`
- `PIN_LONGTERM_TEST_READ`

The benchmark/basic/dump commands copy a `struct gup_test` from userspace, call `__gup_test_ioctl()`, and copy the updated timing and size data back. The long-term stateful commands are forwarded to `pin_longterm_test_ioctl()`.

`__gup_test_ioctl()` computes the number of pages from `.size`, allocates the page pointer array with `kvcalloc()`, optionally takes `mmap_read_lock_killable()`, and loops from `.addr` to `.addr + .size` in chunks of `.nr_pages_per_call`. Each iteration calls the selected GUP/PUP API and stops on short result or error. It records acquisition time in `.get_delta_usec`, updates `.size` to the processed byte count, performs optional verification/dumping, releases pages, and records release time in `.put_delta_usec`.

## Page Release and Verification

`put_back_pages()` matches release API to acquisition API:

- `GUP_FAST_BENCHMARK` and `GUP_BASIC_TEST` use `put_page()`.
- `PIN_FAST_BENCHMARK`, `PIN_BASIC_TEST`, and `PIN_LONGTERM_BENCHMARK` use `unpin_user_pages()`.
- `DUMP_USER_PAGES_TEST` chooses `unpin_user_pages()` or `put_page()` based on `GUP_TEST_FLAG_DUMP_PAGES_USE_PIN`.

`verify_dma_pinned()` checks only pin-oriented commands. It tests `folio_maybe_dma_pinned()` and, for the long-term benchmark, `folio_is_longterm_pinnable()`, warning and dumping the first failing folio.

`dump_pages_test()` treats `.which_pages[]` as 1-based page numbers relative to `.addr`. Out-of-range selections are zeroed with a warning, and selected pages are printed via `dump_page()`.

## Stateful Long-Term Pin Test

The file maintains:

- `pin_longterm_test_mutex`
- `pin_longterm_test_pages`
- `pin_longterm_test_nr_pages`

`pin_longterm_test_start()` copies `struct pin_longterm_test`, validates flags and page alignment, allocates the page array, and pins the whole range with `FOLL_LONGTERM`, optionally `FOLL_WRITE`, and optionally the fast API. It can loop because pin calls may return partial progress. On failure it calls `pin_longterm_test_stop()`.

`pin_longterm_test_read()` copies each pinned page to a user-provided destination using `kmap_local_page()`, `copy_to_user()`, and `kunmap_local()`.

`pin_longterm_test_stop()` unpins all held pages and frees the array. It is called by explicit ioctl and by `gup_test_release()`, so held long-term pins are cleaned up when the debugfs file is closed.

## Integration Points

The test file depends directly on the APIs implemented in `gup.c`, on `kmap_local_page()` from highmem/local-kmap infrastructure, and on debugfs for exposure. It is a diagnostic and benchmark utility, not a production memory-management primitive.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/gup_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/gup_test.h -->
# File Research: sources/os/linux/linux/mm/gup_test.h

## Purpose

`gup_test.h` defines the userspace ABI for the debugfs GUP test driver implemented by `gup_test.c`. It contains ioctl numbers, flag constants, and the fixed-layout structures copied between userspace and the kernel.

## Ioctl Definitions

The header reserves ioctl command type `'g'` for:

- `GUP_FAST_BENCHMARK`
- `PIN_FAST_BENCHMARK`
- `PIN_LONGTERM_BENCHMARK`
- `GUP_BASIC_TEST`
- `PIN_BASIC_TEST`
- `DUMP_USER_PAGES_TEST`
- `PIN_LONGTERM_TEST_START`
- `PIN_LONGTERM_TEST_STOP`
- `PIN_LONGTERM_TEST_READ`

The benchmark and basic test ioctls use `_IOWR()` because the kernel both reads test parameters and writes timing/results back. `PIN_LONGTERM_TEST_START` and `PIN_LONGTERM_TEST_READ` use `_IOW()`, while `PIN_LONGTERM_TEST_STOP` carries no payload.

## Data Structures

`struct gup_test` contains:

- `get_delta_usec` and `put_delta_usec` result fields.
- `addr` and `size` describing the user virtual range.
- `nr_pages_per_call` controlling chunk size for repeated GUP/PUP calls.
- `gup_flags` passed through to the selected API after kernel validation in `gup.c`.
- `test_flags` for test-specific behavior.
- `which_pages[8]`, a 1-based list of page indices for dump tests.

`struct pin_longterm_test` contains:

- `addr`
- `size`
- `flags`

Supported long-term flags are `PIN_LONGTERM_TEST_FLAG_USE_WRITE` and `PIN_LONGTERM_TEST_FLAG_USE_FAST`.

## ABI Notes

All ABI-sized fields use fixed-width Linux integer types. `GUP_TEST_MAX_PAGES_TO_DUMP` is fixed at 8, and zero entries in `which_pages[]` mean "do nothing". The header is tightly coupled to `gup_test.c`; changing structure layout or ioctl numbers would affect userspace tests.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/gup_test.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/highmem.c -->
# File Research: sources/os/linux/linux/mm/highmem.c

## Purpose

`highmem.c` implements common Linux high-memory mapping support. It provides permanent highmem mappings through the pkmap area, local per-task/per-CPU kmap mappings through fixmap slots, highmem page zeroing helpers, and optional hashed `page_address()` tracking for architectures that cannot store direct virtual addresses in `struct page`.

## Major Responsibilities

- Count free and total highmem pages.
- Implement `kmap_high()`, `kmap_high_get()`, and `kunmap_high()` for schedulable highmem mappings.
- Maintain `pkmap_count[]`, `pkmap_page_table`, `kmap_lock`, wait queues, and TLB flush handling for pkmap slots.
- Translate kmap virtual addresses back to pages in `__kmap_to_page()`.
- Implement `kmap_local_page()` internals using fixmap PTE slots, migration disable, and per-task `kmap_ctrl`.
- Save and restore local kmap mappings across context switches.
- Provide `zero_user_segments()` for zeroing one or two ranges inside a possibly compound page.
- Optionally implement hashed `page_address()` and `set_page_address()` mappings.

## Permanent Highmem Mapping Path

The `CONFIG_HIGHMEM` section manages the pkmap area. `pkmap_count[]` is intentionally not a simple reference count:

- `0` means the slot is usable and has not been mapped since the last TLB flush.
- `1` means no active users, but the stale mapping still requires a TLB flush before reuse.
- Values above `1` mean active users, with `count - 1` users.

`map_new_virtual()` searches for a usable pkmap slot, flushing zero-count-stale slots with `flush_all_zero_pkmaps()` when the colored index wraps. If no slot is available, it sleeps on the color-specific wait queue until another task unmaps a slot. Once a slot is selected, it installs a PTE in `pkmap_page_table`, sets `pkmap_count` to `1`, and records the virtual address with `set_page_address()`.

`kmap_high()` locks `kmap_lock`, reuses an existing mapping from `page_address()` when present, otherwise calls `map_new_virtual()`, then increments the slot count. `kunmap_high()` decrements the count and wakes waiters when the slot becomes inactive but still pending TLB flush.

Architectures can override color selection and wait queues with `get_pkmap_color()`, `get_next_pkmap_nr()`, `no_more_pkmaps()`, `get_pkmap_entries_count()`, and `get_pkmap_wait_queue_head()`.

## Address Translation and Zeroing

`__kmap_to_page()` recognizes:

- pkmap addresses and translates them through `pkmap_page_table`.
- local kmap fixmap addresses and compares against the current task's saved `kmap_ctrl.pteval[]`.
- ordinary lowmem direct-map addresses via `virt_to_page()`.

`zero_user_segments()` zeroes up to two byte ranges across a page or compound page. It maps individual subpages with `kmap_local_page()` only when a segment overlaps that subpage, unmaps with `kunmap_local()`, and flushes the dcache for changed subpages.

## Local Kmap Implementation

Under `CONFIG_KMAP_LOCAL`, local mappings are built from fixmap slots. `kmap_local_idx_push()` and `kmap_local_idx_pop()` maintain a per-task nesting index, with `CONFIG_DEBUG_KMAP_LOCAL` optionally leaving guard slots.

`__kmap_local_pfn_prot()`:

1. Disables migration so the local virtual address remains CPU-stable.
2. Disables preemption while selecting and installing a fixmap PTE.
3. Computes the architecture-specific slot index.
4. Installs the PTE with `arch_kmap_local_set_pte()`.
5. Stores the PTE in `current->kmap_ctrl.pteval[]`.
6. Re-enables preemption and returns the fixmap virtual address.

`__kmap_local_page_prot()` avoids creating a mapping for lowmem pages unless debug force-map mode requires one. It can also reuse `arch_kmap_local_high_get()` before installing a new local PTE.

`kunmap_local_indexed()` validates that the unmap address matches the current nesting slot, clears the PTE, clears the saved PTE value, pops the index, re-enables preemption, and re-enables migration. It also handles mappings obtained from `kmap_high_get()` and warns on unexpected user-range addresses.

## Context Switch Handling

`__kmap_local_sched_out()` clears all active local kmap PTEs for the outgoing task without changing the saved nesting index. This is safe with interrupts because nested interrupt kmaps use unused slots and restore their own index.

`__kmap_local_sched_in()` reinstalls saved PTEs for the incoming task. `kmap_local_fork()` warns and clears inherited kmap state if a task is forked while local mappings are active.

## Hashed Page Address Support

When `HASHED_PAGE_VIRTUAL` is defined, highmem virtual-address tracking uses a small hash table:

- `struct page_address_map page_address_maps[LAST_PKMAP]`
- `struct page_address_slot page_address_htable[1 << PA_HASH_ORDER]`

`page_address()` returns direct lowmem addresses for lowmem pages and otherwise searches the hashed list for a highmem page. `set_page_address()` inserts or removes page-to-virtual mappings under the bucket lock. `page_address_init()` initializes all hash buckets.

## Integration Points

This file supports many subsystems that need temporary kernel access to highmem pages, including the GUP test long-term read path, block I/O helpers, page-cache operations, and architecture code. Correctness depends on strict nesting, migration/preemption handling, TLB flushing before pkmap reuse, and architecture hooks for aliasing caches or non-linear kmap PTE layouts.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/highmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/hmm.c -->
# File Research: sources/os/linux/linux/mm/hmm.c

## Purpose

`hmm.c` implements core Heterogeneous Memory Management range-fault and DMA-map helpers. It lets device drivers inspect a process address range as PFN entries, optionally fault CPU page tables to satisfy requested access, represent device-private and migration entries, and map valid PFNs for DMA including PCI P2PDMA handling.

## Major Responsibilities

- Walk process page tables for an `hmm_range`.
- Fill `range->hmm_pfns[]` with PFNs plus HMM flags such as valid, writable, order, error, DMA mapped, and P2PDMA state.
- Decide when a missing or insufficient mapping must be faulted in based on default range flags and per-PFN request flags.
- Handle PTE holes, non-present PTEs, migration entries, device-private entries, transparent huge PMDs, huge PUDs, and hugetlb mappings.
- Reject unsupported VMAs or mark them as `HMM_PFN_ERROR`.
- Coordinate with mmu interval notifiers so callers retry if invalidation raced with the walk.
- Allocate, free, map, and unmap HMM DMA mapping state.

## Range Fault State and Flags

`struct hmm_vma_walk` stores the active `hmm_range` and `last`, the next address that still needs processing after a retryable fault or migration wait.

Internal fault flags are:

- `HMM_NEED_FAULT`
- `HMM_NEED_WRITE_FAULT`
- `HMM_NEED_ALL_BITS`

`HMM_PFN_INOUT_FLAGS` preserves selected caller-owned output/input bits across PFN replacement: `HMM_PFN_DMA_MAPPED`, `HMM_PFN_P2PDMA`, and `HMM_PFN_P2PDMA_BUS`.

`hmm_pte_need_fault()` combines per-PFN request flags masked by `range->pfn_flags_mask` with `range->default_flags`. It requests a normal fault if the CPU mapping is not valid, and a write fault if write access was requested but the CPU mapping is not writable.

`hmm_range_need_fault()` applies that decision over a contiguous set of PFN entries and stops once both read and write fault requirements are known.

## Page Table Walking

The walker is registered through `hmm_walk_ops`:

- `.pud_entry = hmm_vma_walk_pud`
- `.pmd_entry = hmm_vma_walk_pmd`
- `.pte_hole = hmm_vma_walk_hole`
- `.hugetlb_entry = hmm_vma_walk_hugetlb_entry`
- `.test_walk = hmm_vma_walk_test`
- `.walk_lock = PGWALK_RDLOCK`

`hmm_range_fault()` requires the caller to hold `mmap_lock`, checks `mmu_interval_check_retry()` before each walk, and repeats on `-EBUSY`. A retry means some part of the range was faulted or waited on; entries before `last` are already output entries and entries at or after `last` still contain input request flags.

## Holes, PTEs, and Non-Present Entries

`hmm_vma_walk_hole()` handles missing page-table levels or PTE holes. If the range requested faults and a VMA exists, it calls `hmm_vma_fault()`. Without a VMA, requested faults fail with `-EFAULT`; otherwise the PFN array is filled with `HMM_PFN_ERROR`. Non-faulting holes inside a VMA are filled with zero flags.

`hmm_vma_handle_pte()` handles individual PTEs:

- Empty PTEs and UFFD-WP markers fault if requested, otherwise report no CPU mapping.
- Device-private entries owned by `range->dev_private_owner` are reported directly as valid PFNs without faulting.
- Swap, device-private, and device-exclusive entries fault if the caller requested a valid mapping.
- Migration entries wait with `migration_entry_wait()` and return `-EBUSY`.
- Unsupported non-present entries fail with `-EFAULT`.
- Present normal pages produce `pte_pfn(pte) | HMM_PFN_VALID` and optionally `HMM_PFN_WRITE`.
- Present mappings without a normal page, except zero PFNs, become `HMM_PFN_ERROR` unless the caller requested a fault.

When `hmm_vma_handle_pte()` faults or waits, it unmaps the PTE before returning.

## Huge and Migration Handling

For transparent huge PMDs, `hmm_vma_handle_pmd()` computes a PMD-sized order flag, verifies requested access, and fills every base-page PFN entry with the huge mapping's PFN plus valid/write/order flags. It does not split THPs merely to inspect them.

`hmm_vma_walk_pmd()` handles PMD holes, PMD migration entries, absent PMDs, transparent huge PMDs, bad PMDs, and normal PTE tables. If THP migration is supported, `hmm_vma_handle_absent_pmd()` can report device-private PMD entries owned by the caller; otherwise absent unsupported PMDs are errors unless no valid mapping was requested.

When architecture huge PUD support is enabled, `hmm_vma_walk_pud()` locks a huge PUD, reports PUD-sized mappings similarly to PMDs, or asks the generic walker to descend into the subtree.

For hugetlb VMAs, `hmm_vma_walk_hugetlb_entry()` locks the huge PTE, checks requested access, and fills PFNs with the huge-page order. If a fault is needed, it drops both the huge PTE lock and hugetlb VMA read lock before calling `hmm_vma_fault()` to avoid deadlock, then reacquires the VMA lock before returning.

## VMA Filtering

`hmm_vma_walk_test()` permits readable VMAs that are not `VM_IO` and not `VM_PFNMAP`. Unsupported VMAs cannot be represented safely by HMM. If the caller requested faults, unsupported ranges fail with `-EFAULT`; otherwise their PFNs are filled with `HMM_PFN_ERROR` and the walker skips to the next VMA.

## DMA Map Helpers

`hmm_dma_map_alloc()` allocates `map->pfn_list`, optionally allocates a DMA address list, and tries to allocate an IOVA state. It rejects devices that require DMA sync or have limited DMA addressing because HMM cannot follow the usual DMA buffer ownership transfer model and cannot tolerate SWIOTLB-style bounce buffering.

`hmm_dma_map_free()` frees IOVA state, PFN storage, and DMA-address storage.

`hmm_dma_map_pfn()` maps one HMM PFN entry:

- Reuses existing DMA mappings when possible.
- Handles PCI P2PDMA states: no P2P, P2P through host bridge with `DMA_ATTR_MMIO`, or direct bus-address mapping.
- Uses `dma_iova_link()` and `dma_iova_sync()` when IOVA state is active.
- Otherwise uses `dma_map_phys()` and stores the DMA address if the device needs explicit unmap.
- Marks the PFN entry with `HMM_PFN_DMA_MAPPED` and any P2PDMA flags.

`hmm_dma_unmap_pfn()` reverses the mapping if the PFN is both valid and DMA mapped. Bus-address P2PDMA mappings do not require unmap; IOVA and explicit DMA mappings are unlinked or unmapped as appropriate. It clears DMA/P2PDMA bits from the PFN entry.

## Integration Points

HMM bridges process page tables, device-private memory, migration, mmu interval notifiers, DMA mapping, PCI P2PDMA, hugetlb, transparent huge pages, and driver-owned PFN arrays. Its main contract is retry-oriented: drivers must tolerate `-EBUSY`, revalidate against mmu notifier sequences, and treat PFN-array entries as a snapshot that can be invalidated by concurrent CPU memory-management activity.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/hmm.c -->