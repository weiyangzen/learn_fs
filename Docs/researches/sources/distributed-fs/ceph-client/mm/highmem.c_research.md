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
