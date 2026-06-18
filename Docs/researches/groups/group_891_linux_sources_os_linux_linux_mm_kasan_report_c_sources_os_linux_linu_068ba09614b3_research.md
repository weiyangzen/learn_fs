# Group Research: group_891_linux_sources_os_linux_linux_mm_kasan_report_c_sources_os_linux_linu_068ba09614b3

Scope: `Docs/research_subset_a.md` / Linux `mm/kasan`, `mm/kfence`, and `mm/khugepaged.c`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/report.c -->
# File Research: sources/os/linux/linux/mm/kasan/report.c

## Role

Common KASAN error-reporting implementation. It handles report throttling, KUnit integration, report suppression, report locking, error formatting, address/object/page descriptions, memory metadata dumps, and dispatch for access, invalid-free, and asynchronous hardware-tag reports.

## Key Behavior

- Parses `kasan.fault=report|panic|panic_on_write` and `kasan_multi_shot`.
- Enforces single-shot reporting unless multi-shot is enabled; KASAN KUnit tests can temporarily enable multi-shot.
- Suppresses reports during KASAN-disabled critical sections for software modes, while hardware tag mode suppresses CPU tag checks around report printing.
- `start_report()` disables trace-on-warning, disables lockdep, suppresses recursive KASAN checking, takes `report_lock`, and prints the report banner.
- `end_report()` emits trace end events, unlocks, honors `panic_on_warn` and `kasan.fault`, taints the kernel, restores lockdep, and re-enables checking.
- `complete_report_info()` identifies first bad address, slab/cache/object metadata, allocation size, invalid/double-free type, and calls the mode-specific completion hook.
- `print_report()` prints bug type, pointer/memory tags when available, stack trace, slab object allocation/free stacks, variable/global/stack/vmalloc/page descriptions, and surrounding metadata.
- `kasan_report()` wraps regular access reports with `user_access_save/restore`.
- `kasan_report_invalid_free()` reports invalid and double free without software-suppression checks.
- `kasan_report_async()` handles hardware tag asynchronous faults with no address details.
- `kasan_non_canonical_hook()` decodes shadow faults from bogus pointers into null/user/wild-memory-access hints.

## Dependencies

Uses KUnit, stack depot, stack trace, slab internals, vmalloc, module address checks, task stack helpers, KASAN mode hooks from `kasan.h`, and `trace/events/error_report.h`.

## Research Notes

This file is the shared presentation and policy layer for KASAN reports. It deliberately disables instrumentation and lockdep while reporting to avoid recursive faults or deadlocks, then delegates mode-specific classification and metadata decoding to `report_generic.c`, `report_tags.c`, `report_sw_tags.c`, or `report_hw_tags.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/report.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/report_generic.c -->
# File Research: sources/os/linux/linux/mm/kasan/report_generic.c

## Role

Generic shadow-memory KASAN report support. It classifies bugs from shadow byte values, derives allocation sizes from generic shadow metadata, prints decoded stack-frame object information, and exports compiler ASan report entry points.

## Key Functions

- `kasan_find_first_bad_addr()` walks generic shadow bytes from the accessed address until it finds the first poisoned granule.
- `kasan_get_alloc_size()` derives the real allocation size from slab object shadow bytes, including partial last granules.
- `get_shadow_bug_type()` maps generic poison values to bug classes such as slab/global/stack out-of-bounds, use-after-free, alloca out-of-bounds, and vmalloc out-of-bounds.
- `get_wild_bug_type()` classifies addresses without KASAN metadata as null pointer, user memory, or wild memory access.
- `kasan_complete_mode_report_info()` fills the bug type and, for slab objects, copies alloc/free tracks from KASAN object metadata.
- `kasan_metadata_fetch_row()` copies shadow bytes for the common metadata dump.
- `kasan_print_aux_stacks()` prints stored auxiliary work-creation stacks.
- Under `CONFIG_KASAN_STACK`, stack-frame descriptor parsing locates and prints the poisoned stack frame and local-object ranges.
- Exports `__asan_report_load{1,2,4,8,16}_noabort`, `__asan_report_store{1,2,4,8,16}_noabort`, and variable-size load/store report functions.

## Dependencies

Uses generic KASAN shadow mapping helpers, slab KASAN metadata, stack depot, task stack helpers, exported compiler instrumentation ABI, and slab internals.

## Research Notes

This is the most precise KASAN reporting mode because poison byte values encode the memory region state. It can distinguish many concrete failure modes directly from shadow memory and can decode compiler-generated stack metadata when stack instrumentation is enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/report_generic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/report_hw_tags.c -->
# File Research: sources/os/linux/linux/mm/kasan/report_hw_tags.c

## Role

Hardware tag-based KASAN report helpers. It adapts common reporting to memory tags read from hardware rather than software shadow bytes.

## Key Functions

- `kasan_find_first_bad_addr()` returns the untagged access address directly because hardware tag faults identify the failing address.
- `kasan_get_alloc_size()` scans granules with `hw_get_mem_tag()` until `KASAN_TAG_INVALID` or cache object size.
- `kasan_metadata_fetch_row()` fills a metadata row by reading hardware memory tags for each granule.
- `kasan_print_tags()` prints the pointer tag and hardware memory tag at the failing address.

## Dependencies

Uses hardware tag helpers from `kasan.h`, KASAN tag constants, memory-management headers, and slab cache object sizes.

## Research Notes

Unlike generic KASAN, hardware tag mode does not infer the first bad address by shadow walking. It trusts the hardware fault address and provides tag mismatch context for the common report printer.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/report_hw_tags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/report_sw_tags.c -->
# File Research: sources/os/linux/linux/mm/kasan/report_sw_tags.c

## Role

Software tag-based KASAN report helpers. It bridges common report printing to tag values stored in software shadow memory.

## Key Functions

- `kasan_find_first_bad_addr()` compares the pointer tag with shadow tag bytes and returns the first granule whose memory tag differs.
- `kasan_get_alloc_size()` scans software shadow tags until `KASAN_TAG_INVALID`.
- `kasan_metadata_fetch_row()` copies software tag shadow bytes for the metadata dump.
- `kasan_print_tags()` prints pointer tag and shadow memory tag.
- Under `CONFIG_KASAN_STACK`, `kasan_print_address_stack_frame()` prints basic current-task stack ownership.

## Dependencies

Uses KASAN tag helpers, shadow mapping, stack/task helpers, slab internals, and common KASAN report structures.

## Research Notes

Software tag reporting is less semantically rich than generic shadow reporting: tag mismatch establishes invalid access, while allocation/free classification comes from the shared tag-mode stack ring in `report_tags.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/report_sw_tags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/report_tags.c -->
# File Research: sources/os/linux/linux/mm/kasan/report_tags.c

## Role

Shared tag-based KASAN report classification for software and hardware tag modes. It searches the tag-mode allocation/free stack ring to infer bug type and recover allocation/free tracks.

## Key Functions

- `get_common_bug_type()` classifies wrapped/negative-size accesses as out-of-bounds and otherwise returns `invalid-access`.
- `kasan_complete_mode_report_info()` scans `stack_ring` backwards under its write lock.
- It matches entries by untagged object address, pointer tag, and cache object size.
- First matching free entry tends to classify the bug as `slab-use-after-free`.
- First matching allocation entry tends to classify the bug as `slab-out-of-bounds`.
- It copies matching alloc/free `kasan_track` records into the report and falls back to common classification if no entry is found.

## Dependencies

Uses the global `kasan_stack_ring` from `tags.c`, atomic ring position, tag helpers, slab cache metadata, and KASAN report structures.

## Research Notes

Tag-based bug classification is best-effort because ring entries can be overwritten and a later allocation with the same tag can reuse the address. The report is probabilistic but still gives useful recent allocation/free context.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/report_tags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/shadow.c -->
# File Research: sources/os/linux/linux/mm/kasan/shadow.c

## Role

Runtime shadow-memory management for generic and software tag-based KASAN. It provides instrumented memory access wrappers, poisoning/unpoisoning primitives, memory hotplug shadow allocation, vmalloc/module shadow population, and vmalloc shadow release.

## Key Functions

- `__kasan_check_read()` and `__kasan_check_write()` call `kasan_check_range()` for compiler/runtime checks.
- Optional `memset`, `memmove`, and `memcpy` overrides validate source/destination ranges before calling raw implementations.
- `__asan_memset`, `__asan_memmove`, and `__asan_memcpy` are exported compiler instrumentation entry points; software tag mode aliases HWASan memintrinsics to them.
- `kasan_poison()` writes a poison/tag value over shadow bytes for granule-aligned ranges.
- `kasan_poison_last_granule()` records partial-granule accessibility for generic mode.
- `kasan_unpoison()` unpoisons a rounded-up range with the pointer tag, then applies generic partial-granule poisoning.
- Memory hotplug support maps or frees shadow memory for online/offline memory ranges, leaking boot-time shadow that cannot currently be released.
- `__kasan_populate_vmalloc()` allocates and maps vmalloc/module shadow pages, initializes them to invalid, handles UML’s pre-mapped shadow case, and relies on vmalloc/page-table ordering for visibility.
- `__kasan_release_vmalloc()` frees only shadow pages fully covered by the vmalloc free region, with optional page-table removal and TLB flush.
- `__kasan_unpoison_vmalloc()` assigns a random tag unless told to keep the existing tag, skips executable mappings for software tag mode, and unpoisons the vmalloc range.
- `__kasan_poison_vmalloc()` poisons freed vmalloc shadow as invalid.
- Without `CONFIG_KASAN_VMALLOC`, module shadow allocation/free uses `__vmalloc_node_range()` and tracks `VM_KASAN`.

## Dependencies

Uses KASAN mapping helpers, vmalloc internals, page-table walkers, memory hotplug notifiers, memblock/vmalloc allocation, cache/TLB flush helpers, kmemleak, KFENCE include visibility, and architecture hooks.

## Research Notes

This file owns the actual shadow state that common and mode-specific reporting later interprets. The vmalloc release logic is especially careful: because vmalloc regions and shadow pages are not aligned the same way, it frees only pages proven unused by the surrounding free region and documents the concurrency assumptions around `free_vmap_area_lock`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/shadow.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/sw_tags.c -->
# File Research: sources/os/linux/linux/mm/kasan/sw_tags.c

## Role

Core runtime for software tag-based KASAN. It initializes tag mode, generates pointer tags, checks access ranges against software shadow tags, exports HWASan compiler ABI hooks, and handles tag mismatch callbacks.

## Key Functions

- `kasan_init_sw_tags()` seeds per-CPU PRNG state, initializes shared tag infrastructure, enables KASAN, and logs stacktrace state.
- `kasan_random_tag()` uses a per-CPU LCG seeded from cycle counters to generate probabilistic allocation tags.
- `kasan_check_range()` validates a memory range:
  - accepts zero-length access;
  - reports wrapped ranges;
  - ignores native kernel tag `0xff` to avoid false positives from kmap/page-address paths;
  - rejects addresses without metadata;
  - compares all covered shadow tag bytes against the pointer tag.
- `kasan_byte_accessible()` checks whether one tagged byte is accessible.
- Exports `__hwasan_load{1,2,4,8,16}_noabort`, `__hwasan_store{1,2,4,8,16}_noabort`, and variable-size load/store hooks.
- `__hwasan_tag_memory()` poisons a range with the supplied tag.
- `kasan_tag_mismatch()` decodes compiler access info into access size and write/read state, then reports.

## Dependencies

Uses software shadow mapping, tag helpers, exported compiler HWASan ABI, per-CPU state, random/cycle data, slab/KASAN internals, and stack collection controls.

## Research Notes

The PRNG is intentionally lightweight and non-atomic because software tag KASAN is a probabilistic debugging detector. Correctness depends on matching pointer tags to shadow tags, while security-grade unpredictability is explicitly traded off for runtime cost.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/sw_tags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kasan/tags.c -->
# File Research: sources/os/linux/linux/mm/kasan/tags.c

## Role

Shared initialization and allocation/free stack tracking for tag-based KASAN modes.

## Key Functions

- Parses `kasan.stacktrace=off|on` and `kasan.stack_ring_size=<entries>`.
- Defines `kasan_flag_stacktrace` as a static key controlling alloc/free stack collection.
- `kasan_init_tags()` applies boot-time stacktrace policy and allocates the stack ring from memblock, defaulting to `32K` entries.
- `save_stack_info()` saves an allocation or free stack to stack depot and records it in the global ring.
- Ring updates use a busy sentinel plus compare-exchange to avoid readers observing partially written entries.
- Old stack depot handles are dropped after replacement.
- `kasan_save_alloc_info()` and `kasan_save_free_info()` record alloc/free events for later tag-mode report reconstruction.

## Dependencies

Uses memblock allocation, stack depot, static keys, atomic ring position, scheduler clock/task state through KASAN track helpers, and slab cache object sizes.

## Research Notes

This file is the source of allocation/free context used by `report_tags.c`. Because tag modes do not encode rich object state in poison bytes, recent ring history is essential for classifying tag mismatches into use-after-free or out-of-bounds reports.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kasan/tags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kfence/Makefile -->
# File Research: sources/os/linux/linux/mm/kfence/Makefile

## Role

Build rules for the KFENCE subsystem.

## Contents

- Enables `CONTEXT_ANALYSIS := y`.
- Always builds `core.o` and `report.o` into the KFENCE object set.
- Builds `kfence_test.o` when `CONFIG_KFENCE_KUNIT_TEST` is enabled.
- Applies `-fno-omit-frame-pointer` and `-fno-optimize-sibling-calls` to `kfence_test.o` for reliable test stack traces.

## Research Notes

The Makefile keeps production KFENCE split between allocation/fault core logic and reporting, with KUnit tests compiled only under the test config.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kfence/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kfence/core.c -->
# File Research: sources/os/linux/linux/mm/kfence/core.c

## Role

KFENCE guarded object allocator and page-fault handler. It allocates and initializes the guarded pool, samples slab allocations, places objects next to guard pages, checks canaries, detects invalid frees/use-after-free/out-of-bounds accesses, manages debugfs and timers, and integrates with slab cache shutdown.

## Key Data

- `kfence_enabled`, `kfence_sample_interval`, `kfence_burst`, `kfence_deferrable`, and `kfence_check_on_panic` control runtime behavior.
- `__kfence_pool` is the guarded memory pool.
- `kfence_metadata` is the visible metadata array; `kfence_metadata_init` is kept private until pool initialization succeeds.
- `kfence_freelist` holds available guarded objects under `kfence_freelist_lock`.
- `kfence_allocation_key` and `kfence_allocation_gate` implement sampled allocation gating.
- `alloc_covered[]` is a counting Bloom filter used to avoid over-covering the same allocation stack when the pool is mostly occupied.
- Debug counters track allocations, frees, active objects, zombie allocations, bugs, and skipped allocation reasons.

## Allocation and Free Flow

- `__kfence_alloc()` rejects objects larger than a page, incompatible GFP zones, DMA caches, `SLAB_SKIP_KFENCE`, disabled state, and covered allocation stacks.
- `kfence_guarded_alloc()` removes metadata from the freelist, trylocks it to avoid printk recursion deadlocks, chooses left/right placement randomly, records allocation state/stack/cache/size/hash, sets slab fields, installs canaries, runs optional init/ctor, optionally stress-protects the object, and updates counters.
- `__kfence_free()` finds metadata and defers freeing through RCU for `SLAB_TYPESAFE_BY_RCU`; otherwise it calls `kfence_guarded_free()`.
- `kfence_guarded_free()` validates the pointer/state, reports invalid free or double free, checks race exclusivity with KCSAN scoped access, restores guard protection after prior reports, marks freed, updates allocation coverage, checks canaries, zeroes if init-on-free is required, protects the object page to catch UAF, and returns metadata to the freelist unless it is a zombie.
- `kfence_shutdown_cache()` turns live objects from a destroying cache into zombie allocations, then clears cache pointers for freed objects from that cache.

## Pool Initialization

- `kfence_alloc_pool_and_metadata()` reserves pool and metadata memory during boot, unless sample interval is zero or KASAN hardware tags are enabled.
- `kfence_init_pool()` calls the architecture pool setup, marks object pages as slab pages, initializes metadata and guard pages, randomizes the freelist, and publishes `kfence_metadata` only after success.
- `kfence_init_pool_early()` finalizes boot-time memblock allocation and avoids kmemleak overlap.
- `kfence_init_late()` supports runtime enablement by allocating contiguous or exact pages after boot.
- `kfence_init_enable()` enables static-key gating, initializes delayed work, registers panic/reboot notifiers, marks KFENCE enabled, and queues the timer.

## Fault Handling

- `kfence_handle_page_fault()` handles faults inside the KFENCE pool.
- Faults on odd pages are guard-page accesses and are reported as out-of-bounds against the closest allocated neighbor.
- Faults on object pages are reported as use-after-free.
- Unknown pool faults are reported as invalid accesses.
- The faulting page is unprotected after reporting so execution can proceed according to the configured report/oops/panic policy.
- If KFENCE is runtime-disabled, faults simply unprotect the page.

## Timer and Interfaces

- `toggle_allocation_gate()` periodically opens the allocation gate, enables static-key sampling when configured, waits for an allocation or shutdown, disables the key, and requeues itself.
- Reboot notifier disables KFENCE and cancels timer work to avoid late static-key IPIs.
- Debugfs exposes `kfence/stats` and `kfence/objects`.
- Panic notifier optionally checks all active canaries.
- Public helpers include `kfence_ksize()`, `kfence_object_start()`, `current_is_khugepaged()` is not here, and KFENCE allocation/free/fault entry points.

## Dependencies

Uses slab internals, page protection architecture hooks, static keys, delayed work, irq work, debugfs, stack traces, random/jhash, memblock/contiguous allocation, panic/reboot notifiers, KASAN hardware-tag detection, KCSAN scoped access, memcg object extensions, and KFENCE reporting.

## Research Notes

KFENCE trades coverage for low overhead. The implementation is defensive about recursion and partially initialized state: page-protection failures disable KFENCE, metadata is published only after full initialization, allocation uses trylock in a rare printk recursion case, and cache destruction intentionally leaks still-live guarded objects as zombies to preserve kernel semantics while improving later diagnostics.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kfence/core.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kfence/kfence.h -->
# File Research: sources/os/linux/linux/mm/kfence/kfence.h

## Role

Internal KFENCE header shared by core allocation/fault logic and report generation.

## Key Definitions

- `KFENCE_CANARY_PATTERN_U8(addr)` and `KFENCE_CANARY_PATTERN_U64` define address-varied canary patterns.
- `KFENCE_STACK_DEPTH` sets report stack depth to 64.
- `enum kfence_object_state` tracks unused, allocated, RCU-freeing, and freed objects.
- `struct kfence_track` stores pid, CPU, timestamp, stack depth, and stack entries.
- `struct kfence_metadata` records freelist/RCU nodes, state lock, object address, size, cache, one unprotected page, alloc/free tracks, allocation stack hash, and optional memcg object extension data.
- `KFENCE_METADATA_SIZE` rounds the metadata array to pages.
- `addr_to_metadata()` maps a pool address to its guarded-object metadata and rejects non-KFENCE or edge addresses.
- `enum kfence_error_type` enumerates out-of-bounds, use-after-free, canary corruption, invalid access, and invalid free.
- `enum kfence_fault` defines report/oops/panic handling policy.

## API Surface

Declares shared globals and functions:

- `kfence_enabled`
- `kfence_freelist_lock`
- `kfence_metadata`
- `kfence_report_error()`
- `kfence_handle_fault()`
- `kfence_print_object()`

## Dependencies

Includes Linux `mm`, `slab`, `spinlock`, and slab internals for `struct kmem_cache`.

## Research Notes

The metadata lock annotation is central: allocation, free, and page-fault reporting can race on the same metadata. `addr_to_metadata()` encodes the pool layout assumption that object pages and guard pages alternate.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kfence/kfence.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kfence/kfence_test.c -->
# File Research: sources/os/linux/linux/mm/kfence/kfence_test.c

## Role

KUnit test suite for KFENCE. It exercises pool allocation, object placement, canary corruption, out-of-bounds detection, use-after-free, invalid free handling, cache behavior, and stack-reporting assumptions.

## Key Test Infrastructure

- Uses KUnit expectations and KFENCE test-only exported symbols.
- Test build flags preserve frame pointers and disable sibling-call optimization to make stack traces stable.
- Allocates through slab/KFENCE paths and validates whether returned objects are KFENCE objects.
- Uses controlled invalid accesses and frees to trigger KFENCE reports.
- Tests validate counters, object metadata, allocation/free stack capture, and page-protection behavior where possible.

## Coverage Themes

- Basic guarded allocation and freeing.
- Object size and `ksize` behavior.
- Left/right object placement with canary redzones.
- Canary corruption detection on free.
- Out-of-bounds accesses into guard pages.
- Use-after-free detection after object page protection.
- Invalid free/double free reporting.
- Interaction with slab caches and constructor/initialization semantics.
- Behavior around disabled or skipped KFENCE allocation cases.
- Debug/report stack fidelity.

## Dependencies

Uses KUnit, slab allocation APIs, KFENCE public/test hooks, page-fault/report behavior, and compiler stack-frame preservation from the Makefile.

## Research Notes

The test file is intentionally coupled to KFENCE internals and report behavior. It is not a generic allocator test; it verifies that the sampled guarded allocator preserves slab-facing semantics while reliably detecting the specific memory safety classes KFENCE is designed for.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kfence/kfence_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kfence/report.c -->
# File Research: sources/os/linux/linux/mm/kfence/report.c

## Role

KFENCE report generation and object-info formatting. It prints console reports, object allocation/free histories, canary corruption details, fault handling outcomes, and printk object metadata integration.

## Key Functions

- Parses `kfence.fault=report|oops|panic`.
- `seq_con_printf()` writes to either a `seq_file` or the console.
- `get_stack_skipnr()` skips KFENCE/slab allocator internals to show the relevant caller frame.
- `kfence_print_stack()` prints allocation/free/RCU-freeing task, CPU, timestamp, elapsed time, and filtered stack entries.
- `kfence_print_object()` prints guarded object index, address range, size, cache name, and alloc/free stacks.
- `print_diff_canary()` shows changed canary bytes while avoiding object contents and pointer leaks unless `no_hash_pointers` permits raw values.
- `kfence_report_error()` captures a stack trace, disables lockdep for printing, emits a typed report header, prints stack and object metadata, emits error trace event, checks `panic_on_warn`, taints the kernel, and returns the configured fault action.
- `kfence_handle_fault()` implements report/no-op, `BUG()`, or panic behavior; panic disables KFENCE first to avoid recursion.
- Under `CONFIG_PRINTK`, `__kfence_obj_info()` fills `kmem_obj_info` for printk object diagnostics.

## Error Types

Reports distinguish:

- out-of-bounds read/write;
- use-after-free read/write;
- canary memory corruption;
- invalid read/write;
- invalid free.

## Dependencies

Uses stack trace helpers, scheduler clock, printk, panic/oops paths, lockdep, seq files, KFENCE metadata, architecture function-prefix support, and `trace/events/error_report.h`.

## Research Notes

KFENCE reporting intentionally accepts printk risk in difficult contexts to surface memory-safety failures. It narrows report stacks to user-relevant call sites and prints both allocation and deallocation history when metadata state allows.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kfence/report.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/khugepaged.c -->
# File Research: sources/os/linux/linux/mm/khugepaged.c

## Role

Transparent Huge Page background collapse daemon and forced-collapse implementation. It scans eligible VMAs, collapses anonymous, shmem, and read-only file-backed ranges into PMD-sized folios, retracts PTE page tables for already-present THPs, exposes khugepaged sysfs controls, and starts/stops the khugepaged kthread based on THP policy.

## Key Data and Controls

- `enum scan_result` records detailed scan/collapse outcomes for tracepoints and `MADV_COLLAPSE` errno mapping.
- Sysfs attributes under the khugepaged group control:
  - `scan_sleep_millisecs`
  - `alloc_sleep_millisecs`
  - `pages_to_scan`
  - `pages_collapsed`
  - `full_scans`
  - `defrag`
  - `max_ptes_none`
  - `max_ptes_swap`
  - `max_ptes_shared`
- `khugepaged_scan` holds the global mm-slot cursor and next address.
- `mm_slots_hash` and `khugepaged_scan.mm_head` track address spaces registered for background scanning.
- `collapse_control` distinguishes khugepaged from forced collapse and tracks per-node source-page load plus allocation fallback mask.

## Registration and Thread Lifecycle

- `hugepage_madvise()` handles `MADV_HUGEPAGE` and `MADV_NOHUGEPAGE`; positive advice registers the VMA’s `mm` for scanning if eligible.
- `khugepaged_init()` creates the `mm_slot` cache and initializes defaults.
- `__khugepaged_enter()` allocates an `mm_slot`, inserts it behind the scan cursor, grabs an mm reference, and wakes the daemon if needed.
- `khugepaged_enter_vma()` registers only if PMD-sized THP is enabled and VMA policy allows khugepaged.
- `__khugepaged_exit()` removes or serializes with the active slot when an mm exits.
- `start_stop_khugepaged()` starts or stops the kthread as PMD THP policy changes and updates min-free-kbytes recommendations.
- `khugepaged()` loops through scans and sleeps, is freezable, runs at `MAX_NICE`, and cleans the current slot on stop.

## Anonymous Collapse

- `collapse_scan_pmd()` examines one PMD range:
  - skips unsuitable PMDs;
  - counts none/zero PTEs, swap PTEs, shared pages, and referenced pages;
  - rejects userfaultfd write-protected entries;
  - rejects non-anon, zone-device, lazyfree, pinned, locked, non-LRU, or badly NUMA-distributed pages;
  - requires enough referenced pages for khugepaged;
  - can allow limited missing/swap/shared PTEs based on sysfs thresholds.
- `__collapse_huge_page_swapin()` optionally swaps pages back in before collapse.
- `alloc_charge_folio()` allocates a PMD-sized folio on the selected node and charges memcg.
- `collapse_huge_page()` releases the read lock for allocation, revalidates the VMA, optionally swaps in pages, takes mmap write lock, invalidates MMU notifiers, clears the PMD, isolates source pages, copies into the new folio, deposits the old page table, maps the huge PMD, and traces success/failure.
- Copy failure due to machine-check-safe copy restores the original PMD and releases isolated pages.

## File/Shmem Collapse

- `collapse_scan_file()` scans the page cache range, counts present and swap entries, rejects unsuitable folios, builds node-load data, and calls `collapse_file()` if enough pages are present.
- `collapse_file()` allocates a new PMD-sized folio, locks old folios, handles shmem holes/swap/fallocate pages, performs file readahead for missing read-only file pages, rejects dirty/writeback file folios, isolates old folios, releases private data, unmaps mappings, validates refcounts, copies data, fills holes with zeroes, installs retry entries for shmem holes, checks userfaultfd missing-mode constraints, replaces xarray entries with one multi-index folio, updates LRU/accounting stats, retracts PTE tables, and frees or rolls back old folios.
- Read-only file THP handling increments/decrements mapping THP counts and uses barriers against writable opens.

## PTE-Mapped THP Retraction

- `try_collapse_pte_mapped_thp()` detects a PMD-sized folio already in the page cache but mapped through PTEs.
- It verifies all mapped PTEs point to the correct huge folio, invalidates MMU notifiers, clears PTEs, removes rmap and counters, collapses the empty PTE table, frees it deferred, and optionally installs a huge PMD.
- `collapse_pte_mapped_thp()` is the public wrapper.
- `file_backed_vma_is_retractable()` rejects MAP_PRIVATE VMAs with anon data, userfaultfd-wp ranges, and possible guard-marker VMAs.
- `retract_page_tables()` walks file mappings and removes empty retractable PTE tables after file/shmem collapse.

## Scanning Loop

- `collapse_single_pmd()` dispatches anonymous versus file-backed collapse and retries file writeback once for forced `MADV_COLLAPSE`.
- `collapse_scan_mm_slot()` walks VMAs in the current mm slot under a trylock mmap read lock, advances by PMD-sized ranges, handles dropped locks, removes dead/disabled slots, and traces progress.
- `khugepaged_do_scan()` drains LRU caches, scans up to `pages_to_scan`, sleeps after first hugepage allocation failure, and stops when no work remains.
- `khugepaged_wait_work()` sleeps according to scan interval or waits for new work/stop.

## Forced Collapse

- `madvise_collapse()` implements `MADV_COLLAPSE` over a VMA range.
- It uses a non-khugepaged `collapse_control`, drains LRU caches, collapses each PMD-aligned subrange, reacquires mmap lock after dropped-lock paths, and returns actionable errno values through `madvise_collapse_errno()`.
- Forced collapse is less restricted by khugepaged reference thresholds but still respects VMA suitability and hard safety checks.

## Dependencies

Uses THP policy, VMA iteration, mmap locks, anon-vma locking, MMU notifiers, rmap, swap fault handling, shmem, xarray page cache, DAX/file writeback checks, userfaultfd, KSM zero-page handling, LRU isolation, memcg charging, page-table allocation/freeing, tracepoints from `trace/events/huge_memory.h`, and `mm_slot` infrastructure.

## Research Notes

This file is the central PMD-sized THP collapse engine. Its main invariants are repeated VMA/PMD revalidation after dropped locks, strict exclusion of pinned or unstable pages, MMU notifier coverage around page-table removal, and rollback paths for copy or page-cache replacement failures. Background khugepaged and synchronous `MADV_COLLAPSE` share most machinery but differ in thresholds, retry behavior, and returned failure semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/khugepaged.c -->