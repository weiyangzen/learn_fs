# subset-b-006130 Research

Grouped research report for the requested KASAN, KFENCE, and khugepaged memory-management sources. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/report.c -->
# sources/distributed-fs/ceph-client/mm/kasan/report.c

## Purpose

`report.c` is the common KASAN error reporting engine. It serializes reports, applies boot-time report policy, suppresses recursive KASAN checks while printing, gathers generic object context, and delegates mode-specific details to helpers implemented by the generic, software-tag, or hardware-tag report files.

## Important APIs, Types, and Functions

Key state includes `kasan_flags`, `KASAN_BIT_REPORTED`, `KASAN_BIT_MULTI_SHOT`, `enum kasan_arg_fault`, `kasan_arg_fault`, and `report_lock`. Boot interfaces are `early_kasan_fault()` for `kasan.fault=report|panic|panic_on_write` and `kasan_set_multi_shot()` for `kasan_multi_shot`. KUnit-only helpers `kasan_save_enable_multi_shot()`, `kasan_restore_multi_shot()`, `kasan_kunit_test_suite_start()`, and `kasan_kunit_test_suite_end()` adjust reporting behavior during sanitizer tests. The public report entry points are `kasan_report_invalid_free()`, `kasan_report()`, optional `kasan_report_async()`, and `kasan_non_canonical_hook()`.

## Control Flow

Normal memory-access reporting enters `kasan_report()`, saves/restores user access state, rejects reports if software-mode suppression or one-shot gating says no, calls `start_report()`, fills `struct kasan_report_info`, calls `complete_report_info()`, prints the report, then calls `end_report()`. Invalid frees use `kasan_report_invalid_free()` with a non-access report type and bypass the software suppression check because invalid free is an allocator event rather than a poisoned-memory load. `complete_report_info()` finds the first bad address, slab/cache/object, allocation size, and fixed bug type for invalid or double frees, then calls `kasan_complete_mode_report_info()` to classify mode-specific access bugs and fill stack tracks. `print_report()` emits the error header, tag metadata when available, address/object/page/stack descriptions, and surrounding metadata bytes. Hardware-tag async faults use `kasan_report_async()` and can only print a conservative invalid-access report with no address details.

## State and Persistence Behavior

Reporting state is runtime-only. `kasan_flags` persists across the booted kernel to enforce one-shot behavior unless `kasan_multi_shot` or KUnit enables repeated reports. `kasan_arg_fault` is set during early boot and becomes read-only after init. `report_lock` serializes console output; `current->kasan_depth` or hardware tag-check suppression prevents recursion while report code reads poisoned areas. Reports taint the kernel with `TAINT_BAD_PAGE`, can trigger `check_panic_on_warn()`, and may panic depending on `kasan.fault`.

## Dependencies and Integration Points

This file depends on slab metadata (`kasan_addr_to_slab()`, `nearest_obj()`), shadow/tag helpers (`kasan_find_first_bad_addr()`, `kasan_get_alloc_size()`, `kasan_metadata_fetch_row()`, `kasan_print_tags()`), stack depot, vmalloc and module address helpers, lockdep, ftrace warning handling, KUnit, and `trace_error_report_end(ERROR_DETECTOR_KASAN, ...)`. It is the central integration point between compiler/hardware KASAN checks and human-readable kernel diagnostics.

## Risks and Edge Cases

The highest risks are recursive faults during reporting, deadlocks while printk touches poisoned memory, misleading classification when tag-based stack-ring evidence is stale, and address decoding for non-canonical pointers. The code deliberately uses one-shot reporting by default to avoid flooding after memory corruption. `panic_on_write` treats invalid frees as writes because allocator metadata is being modified.

## Test Signals

Useful signals include KASAN KUnit tests with multi-shot enabled, boot tests for `kasan.fault` and `kasan_multi_shot`, invalid-free and double-free reports, software-mode suppressed sections around slab metadata, hardware-tag async fault reports, stack/object/page/vmalloc metadata in dmesg, and tracepoint emission for KASAN reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/report.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/report_generic.c -->
# sources/distributed-fs/ceph-client/mm/kasan/report_generic.c

## Purpose

`report_generic.c` supplies KASAN report helpers for the generic shadow-byte mode. It interprets shadow memory values, extracts slab allocation/free metadata, decodes stack-frame poisoning metadata, and exposes compiler-generated `__asan_report_*_noabort` entry points.

## Important APIs, Types, and Functions

Important functions are `kasan_find_first_bad_addr()`, `kasan_get_alloc_size()`, `kasan_complete_mode_report_info()`, `kasan_metadata_fetch_row()`, `kasan_print_aux_stacks()`, and, under `CONFIG_KASAN_STACK`, `kasan_print_address_stack_frame()`. Internal classifiers include `get_shadow_bug_type()`, `get_wild_bug_type()`, and `get_bug_type()`. The `DEFINE_ASAN_REPORT_LOAD/STORE` macros export fixed-size load/store report shims plus `__asan_report_load_n_noabort()` and `__asan_report_store_n_noabort()`.

## Control Flow

When common reporting asks for generic details, `kasan_find_first_bad_addr()` walks shadow bytes from the access start until it finds poison. `kasan_get_alloc_size()` scans object shadow bytes, treating zero as a full valid granule, 1..7 as a partial final granule, and poison as the end or an uncomputable freed object. `kasan_complete_mode_report_info()` classifies the bug from shadow values and copies alloc/free stack tracks from slab-side KASAN metadata. Stack reports parse compiler frame descriptions by finding `KASAN_STACK_LEFT`, validating `KASAN_CURRENT_STACK_FRAME_MAGIC`, and printing object ranges inside the frame.

## State and Persistence Behavior

This file owns no long-lived storage. It reads persistent runtime state from KASAN shadow memory, slab alloc/free metadata, and stack depot handles. Stack-depot handles are retained by allocation metadata elsewhere; this file only copies or prints them.

## Dependencies and Integration Points

It integrates with `report.c` through the mode helper API and with compiler ASAN instrumentation through the exported report symbols. It depends on `kasan_mem_to_shadow()`, `addr_has_metadata()`, shadow poison constants such as `KASAN_SLAB_REDZONE`, `KASAN_SLAB_FREE_META`, stack depot, slab metadata, current task stack layout, and arch stack-growth assumptions.

## Risks and Edge Cases

Shadow bytes can be racy with buggy kernel writes, so some classifications are best-effort. Freed objects can return allocation size 0, causing common code to fall back to cache object size. Stack-frame decoding is only supported for the current task's own stack and assumes the compiler frame description format remains stable.

## Test Signals

Signals include generic KASAN KUnit coverage for OOB, UAF, invalid free, stack OOB, alloca OOB, global OOB, vmalloc OOB, auxiliary work stacks, ASAN compiler callbacks, and reports whose metadata rows match expected shadow poison bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/report_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/report_hw_tags.c -->
# sources/distributed-fs/ceph-client/mm/kasan/report_hw_tags.c

## Purpose

`report_hw_tags.c` provides the hardware tag-based KASAN implementation of the report helper API. It reads architectural memory tags rather than byte-addressable shadow memory and formats pointer-tag versus memory-tag diagnostics.

## Important APIs, Types, and Functions

The exported helper set is `kasan_find_first_bad_addr()`, `kasan_get_alloc_size()`, `kasan_metadata_fetch_row()`, and `kasan_print_tags()`. It uses `hw_get_mem_tag()`, `KASAN_TAG_INVALID`, `KASAN_GRANULE_SIZE`, and `META_BYTES_PER_ROW`.

## Control Flow

For normal hardware-tag faults, the faulting address is already the first bad granule, so `kasan_find_first_bad_addr()` simply strips the pointer tag and returns the address. Allocation-size recovery walks object granules with `hw_get_mem_tag()` until it sees `KASAN_TAG_INVALID` or reaches `cache->object_size`. Metadata-row fetching synthesizes report rows by reading each granule's hardware tag. `kasan_print_tags()` prints the pointer tag and the hardware memory tag for the bad address.

## State and Persistence Behavior

No storage is owned here. The effective state is in architectural memory tags associated with kernel memory and in slab cache object size metadata. Freed or invalid-tagged objects may cause allocation-size discovery to return 0.

## Dependencies and Integration Points

This file is selected for `CONFIG_KASAN_HW_TAGS` and is called by the common report engine. It depends on architecture support for memory tagging and on common KASAN tag helpers such as `get_tag()` and `kasan_reset_tag()` from the shared headers.

## Risks and Edge Cases

The implementation assumes common report code calls it only for normal memory-access reports where hardware already supplied the precise failing address. It cannot reconstruct fine-grained shadow poison classes like generic KASAN, so final bug type comes from tag-mode stack-ring evidence in `report_tags.c`.

## Test Signals

Signals include hardware tag fault reports with pointer and memory tags, correct object-size reporting before invalid tags, async report behavior from `report.c`, and architecture/MTE tests that verify tag suppression during report printing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/report_hw_tags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/report_sw_tags.c -->
# sources/distributed-fs/ceph-client/mm/kasan/report_sw_tags.c

## Purpose

`report_sw_tags.c` provides software tag-based KASAN report helpers. It uses shadow memory as a tag store, compares pointer tags against shadow tags, and exposes minimal stack-address description support for stack-tag reports.

## Important APIs, Types, and Functions

The helper API consists of `kasan_find_first_bad_addr()`, `kasan_get_alloc_size()`, `kasan_metadata_fetch_row()`, `kasan_print_tags()`, and optional `kasan_print_address_stack_frame()`. It relies on `get_tag()`, `kasan_reset_tag()`, `kasan_mem_to_shadow()`, `addr_has_metadata()`, and `KASAN_TAG_INVALID`.

## Control Flow

The first-bad-address helper strips the pointer tag, then walks shadow granules until the stored tag differs from the pointer tag. Allocation-size discovery walks the object's shadow tags until it sees `KASAN_TAG_INVALID`. Metadata rows are copied directly from shadow memory. Tag printing reports the pointer tag and current shadow tag. The stack-frame printer only identifies that the buggy address belongs to the current task stack and does not decode frame objects like generic KASAN.

## State and Persistence Behavior

The file owns no persistent state. It reads per-granule software tags stored in KASAN shadow memory and object/cache metadata supplied by slab code.

## Dependencies and Integration Points

It integrates with common reporting and the shared tag-mode classifier in `report_tags.c`. It also pairs with `sw_tags.c`, which performs runtime checks and writes software tags via `kasan_poison()`.

## Risks and Edge Cases

Like hardware tags, software tags are probabilistic and can miss bugs when an invalid access happens to carry a matching tag. Stale or overwritten shadow tags can make allocation-size and first-bad-address discovery imprecise. Stack reporting is less detailed than generic mode.

## Test Signals

Signals include SW_TAGS KASAN reports that show mismatched pointer and memory tags, first-bad-address movement across valid tagged granules, invalid-tag allocation-size fallback, and compiler HWASAN report callback coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/report_sw_tags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/report_tags.c -->
# sources/distributed-fs/ceph-client/mm/kasan/report_tags.c

## Purpose

`report_tags.c` contains shared report classification for tag-based KASAN modes. Because tag mismatch reports do not carry generic shadow poison classes, this file infers alloc/free history from the KASAN stack ring to classify slab out-of-bounds versus slab use-after-free.

## Important APIs, Types, and Functions

The important entry point is `kasan_complete_mode_report_info()`. Internal helper `get_common_bug_type()` detects wrapped access ranges and otherwise returns `invalid-access`. The file uses the external `stack_ring` with `struct kasan_stack_ring_entry`, `entry->ptr`, `entry->track`, `entry->is_free`, and `entry->size`.

## Control Flow

Common reporting calls `kasan_complete_mode_report_info()` after it has found the cache and object. If no object is available and no fixed bug type was set, the file assigns a common bug type. Otherwise it takes `stack_ring.lock`, reads the current ring position, and walks backward up to `stack_ring.size` entries. Matching requires the untagged object pointer, the pointer tag, and object size to match. The first matching free entry sets `free_track` and suggests `slab-use-after-free`; the first matching alloc entry sets `alloc_track` and suggests `slab-out-of-bounds`. Duplicate alloc or free entries stop the inference.

## State and Persistence Behavior

This file only reads the stack ring. The ring is a bounded in-memory history, so evidence can be overwritten, stale, or absent. It fills transient fields in `struct kasan_report_info`; it does not persist reports.

## Dependencies and Integration Points

It depends on `tags.c` for stack-ring allocation and writes, on common report handling in `report.c`, and on tag helpers for pointer reset/tag comparison. The lock pairing is important: `tags.c` uses the same ring lock to avoid seeing partially written entries.

## Risks and Edge Cases

The classification is explicitly best-effort. Another object with the same tag can reuse the address, entries can be overwritten, and a ring with disabled stack collection provides no alloc/free evidence. In such cases reports fall back to `invalid-access` or the fixed bug type supplied by common code.

## Test Signals

Signals include tag-mode KASAN reports that include alloc and free stack traces when stack collection is enabled, fallback classification when `kasan.stacktrace=off`, and ring-size stress tests that overwrite old evidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/report_tags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/shadow.c -->
# sources/distributed-fs/ceph-client/mm/kasan/shadow.c

## Purpose

`shadow.c` manages KASAN shadow memory for generic and software tag modes. It provides explicit read/write range checks, instrumented memory intrinsic wrappers, poison/unpoison primitives, memory-hotplug shadow handling, vmalloc/module shadow population, and vmalloc poisoning on allocation/free.

## Important APIs, Types, and Functions

Public entry points include `__kasan_check_read()`, `__kasan_check_write()`, `__asan_memset()`, `__asan_memmove()`, `__asan_memcpy()`, optional `__hwasan_mem*` aliases, `kasan_poison()`, `kasan_poison_last_granule()`, `kasan_unpoison()`, `__kasan_populate_vmalloc()`, `__kasan_release_vmalloc()`, `__kasan_unpoison_vmalloc()`, `__kasan_poison_vmalloc()`, `kasan_alloc_module_shadow()`, and `kasan_free_module_shadow()`. Internal vmalloc helpers include `kasan_populate_vmalloc_pte()`, `__kasan_populate_vmalloc_do()`, and `kasan_depopulate_vmalloc_pte()`.

## Control Flow

Range-check APIs call `kasan_check_range()` with read/write intent. Instrumented memory wrappers validate source and destination before forwarding to `__mem*`. Poisoning strips pointer tags, validates granule alignment, converts memory addresses to shadow addresses, and writes poison/tag bytes. Generic mode additionally records partial-granule accessibility in the last shadow byte. Vmalloc population maps shadow pages for vmalloc/module regions, initializes them to `KASAN_VMALLOC_INVALID`, flushes caches, and relies on vmalloc publication barriers to prevent other CPUs from seeing stale poison after allocation. Release logic frees only shadow pages fully covered by a free vmalloc region, with careful alignment to avoid freeing shadow shared by neighboring allocations.

## State and Persistence Behavior

The persistent runtime state is shadow memory mappings and their poison/tag bytes. Memory-hotplug and vmalloc code allocate or release backing pages for portions of the shadow address space. Module shadow is marked via `VM_KASAN` on the owning `vm_struct` so it can be released when modules unload.

## Dependencies and Integration Points

The file integrates with compiler instrumentation, vmalloc, module allocation, memory hotplug notifiers, memblock/vmalloc page table manipulation, kmemleak, cache/TLB flushing, and architecture address translation helpers. It is disabled or simplified in some UML paths where all shadow is pre-mapped.

## Risks and Edge Cases

Risks are mostly mapping and ordering bugs: freeing a shadow page still shared by another vmalloc allocation, publishing vmalloc memory before shadow is unpoisoned, failing page-table allocations under constrained GFP masks, and recursive checking through instrumented memory functions. The code uses uninstrumented `__mem*` and page-table locks/barriers to reduce those risks.

## Test Signals

Signals include KASAN reports for vmalloc/module OOB, memory hotplug online/offline with KASAN enabled, module load/unload with shadow allocation, compiler intrinsic tests, partial-granule generic poisoning checks, and stress tests for concurrent vmalloc allocate/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/shadow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/sw_tags.c -->
# sources/distributed-fs/ceph-client/mm/kasan/sw_tags.c

## Purpose

`sw_tags.c` is the software tag-based KASAN runtime. It initializes per-CPU tag pseudo-random state, checks instrumented memory accesses by comparing pointer tags against shadow tags, exposes HWASAN compiler callbacks, and forwards mismatches to common KASAN reporting.

## Important APIs, Types, and Functions

Important state is per-CPU `prng_state`. Main functions are `kasan_init_sw_tags()`, `kasan_random_tag()`, `kasan_check_range()`, `kasan_byte_accessible()`, fixed-size `__hwasan_load/store*_noabort` callbacks, `__hwasan_loadN_noabort()`, `__hwasan_storeN_noabort()`, `__hwasan_tag_memory()`, and `kasan_tag_mismatch()`.

## Control Flow

Initialization seeds each CPU PRNG from cycles, initializes shared tag state through `kasan_init_tags()`, enables KASAN, and logs stacktrace status. Access checking ignores zero-size ranges, detects range wraparound, bypasses native kernel tag `KASAN_TAG_KERNEL`, strips tags, validates metadata coverage, then walks every shadow granule touched by the access. Any tag mismatch calls `kasan_report()` and returns the inverse of whether a report was emitted. HWASAN callbacks are thin wrappers around `kasan_check_range()` or `kasan_poison()`.

## State and Persistence Behavior

Only PRNG state is owned here, and it is per-CPU runtime state. Memory tags persist in shadow memory via `kasan_poison()` and `kasan_unpoison()` from `shadow.c`. The random generator intentionally trades cryptographic strength for low overhead and probabilistic coverage.

## Dependencies and Integration Points

This file integrates with compiler HWASAN instrumentation, the shared tag stack-ring code in `tags.c`, common reporting in `report.c`, and shadow memory operations in `shadow.c`. It also includes kernel highmem/kmap compatibility handling through the special native kernel tag.

## Risks and Edge Cases

Tag checking is probabilistic and can miss accesses when tags match by chance. Range wraparound is treated as a reportable OOB. Preemption during PRNG update may duplicate tags across contexts, which is accepted by design. Native kernel-tag bypass suppresses false positives but can hide tag mismatches from paths that lose pointer tags.

## Test Signals

Signals include HWASAN load/store callback tests, tag mismatch reports, random-tag distribution smoke tests, native-kernel-tag bypass cases around kmap/page_address style pointers, and `kasan_byte_accessible()` checks for tagged and untagged addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/sw_tags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/tags.c -->
# sources/distributed-fs/ceph-client/mm/kasan/tags.c

## Purpose

`tags.c` implements shared tag-based KASAN stack tracking. It parses boot parameters for stack collection and stack-ring size, allocates the bounded stack ring, and records allocation/free stack information used later by tag-mode report classification.

## Important APIs, Types, and Functions

Key state includes `kasan_arg_stacktrace`, static key `kasan_flag_stacktrace`, `STACK_RING_BUSY_PTR`, and global `struct kasan_stack_ring stack_ring`. Boot parsers are `early_kasan_flag_stacktrace()` for `kasan.stacktrace=off|on` and `early_kasan_flag_stack_ring_size()` for `kasan.stack_ring_size=...`. Main functions are `kasan_init_tags()`, `save_stack_info()`, `kasan_save_alloc_info()`, and `kasan_save_free_info()`.

## Control Flow

Initialization applies the stacktrace boot policy, chooses the default ring size when needed, and allocates the ring from memblock. Allocation/free tracking saves a stack depot handle, takes the ring read lock, atomically advances `stack_ring.pos`, skips busy slots, claims a slot by changing `entry->ptr` to `STACK_RING_BUSY_PTR`, fills object size, track, free/alloc flag, and pointer, then releases the lock. If the slot previously referenced a stack depot handle, the old handle is dropped after publishing the new entry.

## State and Persistence Behavior

The stack ring is fixed-size runtime memory allocated at boot. It is a lossy circular history; old entries are overwritten as allocations and frees occur. The static key persists the stack-collection policy for the running kernel.

## Dependencies and Integration Points

This file integrates with slab allocation/free hooks for tag-based KASAN, stack depot, memblock, static keys, and `report_tags.c`, which walks the same ring to infer bug types and copy stack tracks. The ring lock prevents report readers from seeing partially written entries.

## Risks and Edge Cases

The busy-slot loop must avoid corrupting entries under concurrent writers. Ring size too small reduces report quality; allocation failure disables stack collection. Stack depot reference management is important because overwritten stack handles are explicitly released.

## Test Signals

Signals include boot coverage for `kasan.stacktrace` and `kasan.stack_ring_size`, tag-mode reports with alloc/free stacks, disabled-stacktrace fallback reports, and stress tests with concurrent slab allocations and frees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kasan/tags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kfence/Makefile -->
# sources/distributed-fs/ceph-client/mm/kfence/Makefile

## Purpose

The KFENCE `Makefile` selects the KFENCE object files and compiler flags. It builds the guarded allocator core and reporting code into the kernel, and conditionally builds the KUnit test module when KFENCE tests are enabled.

## Important APIs, Types, and Functions

Build rules set `CONTEXT_ANALYSIS := y`, `obj-y := core.o report.o`, `CFLAGS_kfence_test.o := -fno-omit-frame-pointer -fno-optimize-sibling-calls`, and `obj-$(CONFIG_KFENCE_KUNIT_TEST) += kfence_test.o`.

## Control Flow

There is no runtime control flow. The build system always compiles `core.o` and `report.o` when the KFENCE directory is active, while `kfence_test.o` depends on `CONFIG_KFENCE_KUNIT_TEST`.

## State and Persistence Behavior

No runtime state is owned here. The test-specific compiler flags persist in the build output and improve stack-trace determinism for report-matching tests.

## Dependencies and Integration Points

This file integrates with Kbuild, KFENCE Kconfig selection, obj-y linking, and KUnit test builds. The frame-pointer and sibling-call flags support `kfence_test.c`, which validates function names in console reports.

## Risks and Edge Cases

Removing or changing the test flags can make report stack matching flaky. Omitting `report.o` or `core.o` would break public KFENCE symbols expected by slab, fault handling, and debugfs code.

## Test Signals

Signals are successful kernel builds with KFENCE enabled, successful KUnit builds with `CONFIG_KFENCE_KUNIT_TEST`, and stable KFENCE report stack frames in tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kfence/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kfence/core.c -->
# sources/distributed-fs/ceph-client/mm/kfence/core.c

## Purpose

`core.c` implements KFENCE's guarded-object allocator, sampling gate, metadata lifecycle, guard-page protection, canary checking, debugfs views, initialization, shutdown handling, and page-fault classification. It is the allocator-side half of KFENCE.

## Important APIs, Types, and Functions

Important global state includes `kfence_enabled`, `disabled_by_warn`, `kfence_sample_interval`, `__kfence_pool`, `kfence_metadata`, `kfence_metadata_init`, `kfence_freelist_lock`, `kfence_freelist`, `kfence_allocation_key`, `kfence_allocation_gate`, `alloc_covered[]`, `stack_hash_seed`, and `counters[]`. Key public functions are `kfence_alloc_pool_and_metadata()`, `kfence_init()`, `kfence_shutdown_cache()`, `__kfence_alloc()`, `kfence_ksize()`, `kfence_object_start()`, `__kfence_free()`, and `kfence_handle_page_fault()`. Core internal functions include `kfence_init_pool()`, `kfence_guarded_alloc()`, `kfence_guarded_free()`, `metadata_update_state()`, `set_canary()`, `check_canary()`, `toggle_allocation_gate()`, and `kfence_init_late()`.

## Control Flow

Boot allocates pool and metadata unless sampling is disabled or KASAN hardware tags are active. Pool initialization marks object pages as slab pages, protects guard pages, initializes metadata, randomizes the freelist, and publishes `kfence_metadata` only after success. Sampling uses a delayed work item to periodically open the allocation gate and optionally enable a static key. `__kfence_alloc()` filters incompatible sizes/zones/caches, advances the gate, records a stack hash, skips covered sources when the pool is mostly full, and calls `kfence_guarded_alloc()`. Guarded allocation removes metadata from the freelist, chooses left or right placement in the object page, stores metadata and stack state, sets canaries, initializes memory/constructors, and updates counters. Free validates the exact object address, reports invalid/double frees, checks and restores canaries/guard-page protection, handles init-on-free, and either returns metadata to the freelist or marks zombie allocations during cache shutdown. Page faults inside the KFENCE pool are classified as redzone OOB, object-page UAF, or invalid, reported through `kfence_report_error()`, then unprotected so execution can proceed or the selected fault policy can trigger.

## State and Persistence Behavior

KFENCE keeps a fixed pool and metadata array for the lifetime of the kernel once initialized. Object metadata tracks state, address, size, cache pointer, one temporarily unprotected page, stack tracks, allocation coverage hash, and optional memcg object extensions. Counters and debugfs output persist until reboot. Runtime module parameters can disable or re-enable sampling if initialization resources remain available.

## Dependencies and Integration Points

The file integrates with slab allocation/free hooks, architecture page-protection helpers from `asm/kfence.h`, KASAN enablement checks, KCSAN scoped-access assertions, stack tracing, RCU for `SLAB_TYPESAFE_BY_RCU`, memcg object extensions, panic/reboot notifiers, debugfs, static keys, irq work, and report handling in `report.c`.

## Risks and Edge Cases

Important risks include recursive allocation while reporting, page-protection failures, races with cache destruction, RCU delayed frees, debugfs iteration over changing metadata, use-after-free faults racing with reallocation, and late enablement allocation failures. `KFENCE_WARN_ON()` disables KFENCE after internal invariants fail. Coverage skipping is probabilistic because it uses a counting Bloom filter over stack hashes.

## Test Signals

Signals include KFENCE KUnit tests, debugfs `kfence/stats` and `kfence/objects`, OOB/UAF/invalid-free/corruption reports, sampling interval changes through module parameters, cache shutdown zombie accounting, panic-time canary checks when enabled, and boot/late-enable logs showing pool address and object count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kfence/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kfence/kfence.h -->
# sources/distributed-fs/ceph-client/mm/kfence/kfence.h

## Purpose

`kfence.h` is the internal KFENCE contract shared by core allocation, reporting, and tests. It defines object states, metadata layout, canary patterns, stack tracking, error/fault enums, metadata lookup, and report/debug helpers.

## Important APIs, Types, and Functions

Important definitions include `KFENCE_CANARY_PATTERN_U8()`, `KFENCE_CANARY_PATTERN_U64`, `KFENCE_STACK_DEPTH`, `enum kfence_object_state`, `struct kfence_track`, `struct kfence_metadata`, `KFENCE_METADATA_SIZE`, `addr_to_metadata()`, `enum kfence_error_type`, and `enum kfence_fault`. Declared functions are `kfence_report_error()`, `kfence_handle_fault()`, and `kfence_print_object()`. Shared variables include `kfence_enabled`, `kfence_freelist_lock`, and `kfence_metadata`.

## Control Flow

The header has no standalone runtime flow, but `addr_to_metadata()` maps an address inside `__kfence_pool` to its metadata by calculating the object index from the alternating guard/object page layout. Report and core code use the enums to drive allocation state transitions and report behavior.

## State and Persistence Behavior

The header defines persistent metadata fields: freelist node, RCU head, per-object lock, state, object address/size/cache, unprotected fault page, allocation/free tracks, allocation coverage hash, and optional memcg object extensions. The actual storage lives in `core.c`.

## Dependencies and Integration Points

It depends on `linux/mm.h`, `linux/slab.h`, spinlocks, RCU types, and `../slab.h`. It is included by `core.c`, `report.c`, and `kfence_test.c`, forming the internal ABI for KFENCE object state and diagnostics.

## Risks and Edge Cases

Because metadata layout is shared across core/report/test code, field changes can break locking assumptions or diagnostics. `addr_to_metadata()` can return NULL for guard-edge addresses or invalid pool offsets, and callers must handle that when reporting invalid accesses.

## Test Signals

Signals include compile coverage of all KFENCE translation units, tests for metadata lookup around object and guard-page boundaries, canary corruption reports, and debugfs object printing under the metadata lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kfence/kfence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kfence/kfence_test.c -->
# sources/distributed-fs/ceph-client/mm/kfence/kfence_test.c

## Purpose

`kfence_test.c` is the KUnit suite for KFENCE. It forces or waits for guarded allocations, triggers representative memory-safety bugs, captures console report output via the printk tracepoint, and verifies both reports and allocator integration behavior.

## Important APIs, Types, and Functions

Important test infrastructure includes `observed`, `probe_console()`, `report_available()`, `struct expect_report`, `report_matches()`, `setup_test_cache()`, `test_cache_destroy()`, `test_alloc()`, and `test_free()`. Test cases cover OOB read/write, UAF, nofault UAF, double free, invalid free address, canary corruption, aligned kmalloc gaps, cache shrink/destroy, bulk free, init-on-free, constructors, `__GFP_ZERO`, invalid pool access, `SLAB_TYPESAFE_BY_RCU`, `krealloc()`, and bulk allocation.

## Control Flow

Suite initialization registers a console tracepoint probe. Each test clears observed report state and optionally selects a private kmem_cache variant by checking for the `-memcache` suffix. `test_alloc()` loops until it obtains a KFENCE allocation matching the requested placement policy or returns a non-KFENCE allocation for negative cases, yielding so the sampling gate can open. Faulting tests perform a bad read/write/free and then call `report_matches()` to compare the report title and address line. Test exit destroys any custom cache; suite exit unregisters the tracepoint and synchronizes.

## State and Persistence Behavior

Test state is transient: `observed` stores the two report lines of interest, `test_cache` owns an optional kmem_cache for the current case, and `test->priv` selects cache-backed variants. The suite intentionally reads live KFENCE global state, pool address, and sampling interval.

## Dependencies and Integration Points

The suite depends on KUnit, printk trace events, KFENCE internals, slab/kmalloc APIs, RCU, copy-from-kernel-nofault behavior, `kmalloc_caches`, and arch-specific address translation via optional `arch_kfence_test_address()`. The Makefile disables frame-pointer omission and sibling-call optimization to keep stack matching stable.

## Risks and Edge Cases

Tests are timing-sensitive because they wait for sampled allocations. Console matching is intentionally partial because symbol offsets and module suffixes vary. Some tests skip or soften expectations for slow sample intervals, init-on-free config, and difficulty reacquiring the same guarded object.

## Test Signals

The file itself is the primary signal: `kunit.py run kfence` or kernel KUnit execution should pass both kmalloc and memcache variants, with no stray reports in negative cases. Stable report matching validates report formatting and stack trimming in `report.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kfence/kfence_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kfence/report.c -->
# sources/distributed-fs/ceph-client/mm/kfence/report.c

## Purpose

`report.c` is KFENCE's diagnostics and fault-policy implementation. It formats memory-safety reports, prints stack and object metadata, handles the `kfence.fault` boot policy, taints or panics the kernel when configured, and exposes object information to printk slab diagnostics.

## Important APIs, Types, and Functions

Important state is `kfence_fault`, set by `early_kfence_fault()` from `kfence.fault=report|oops|panic`. Core functions are `seq_con_printf()`, `get_stack_skipnr()`, `kfence_print_stack()`, `kfence_print_object()`, `print_diff_canary()`, `kfence_report_error()`, `kfence_handle_fault()`, and optional `__kfence_obj_info()`.

## Control Flow

KFENCE core calls `kfence_report_error()` with the bad address, access type, registers if available, metadata when known, and error type. The function saves or reconstructs a stack trace, disables lockdep around printk, prints a type-specific header for OOB, UAF, corruption, invalid access, or invalid free, prints the current stack, prints object allocation/free details under the metadata lock, emits footer information and tracepoint, taints the kernel, and returns the configured fault action. `kfence_handle_fault()` then ignores, BUGs, or panics according to that action. `kfence_print_object()` also serves debugfs by writing to a `seq_file`.

## State and Persistence Behavior

The report file owns only the boot-time `kfence_fault` policy. It reads persistent metadata and stack tracks from `struct kfence_metadata`. Reports call `trace_error_report_end(ERROR_DETECTOR_KFENCE, address)` and add `TAINT_BAD_PAGE`.

## Dependencies and Integration Points

It integrates with KFENCE core fault/free paths, debugfs object listing, printk and seq_file output, stacktrace helpers, lockdep, panic handling, trace events, slab object info (`struct kmem_obj_info`), and optional arch symbol prefixes.

## Risks and Edge Cases

Reporting can occur in printk-unfriendly contexts, so the code knowingly accepts printk risk while suppressing lockdep noise. Stack trimming depends on symbol-prefix heuristics and can be affected by compiler optimization. Canary bytes are redacted unless pointer hashing is disabled to avoid leaking memory.

## Test Signals

Signals include KUnit report matching for all error types, `kfence.fault=oops|panic` boot behavior, debugfs object output, slab object diagnostic integration through `__kfence_obj_info()`, tracepoint emission, and canary corruption output with and without `no_hash_pointers`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kfence/report.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/khugepaged.c -->
# sources/distributed-fs/ceph-client/mm/khugepaged.c

## Purpose

`khugepaged.c` implements the background Transparent Huge Page collapse daemon and the forced `MADV_COLLAPSE` path. It tracks eligible address spaces, scans VMAs for PMD-sized ranges, collapses anonymous PTE pages into PMD-mapped anonymous folios, collapses file/shmem page-cache ranges into order-PMD folios, retracts PTE page tables for pte-mapped THPs, exposes sysfs tuning, and starts/stops the daemon according to THP policy.

## Important APIs, Types, and Functions

Important state includes `khugepaged_thread`, `khugepaged_mutex`, scan and allocation sleep tunables, `khugepaged_pages_to_scan`, `khugepaged_pages_collapsed`, `khugepaged_full_scans`, `khugepaged_mm_lock`, `khugepaged_wait`, PTE threshold tunables, `mm_slots_hash`, `mm_slot_cache`, and global `khugepaged_scan`. Main public functions are `hugepage_madvise()`, `khugepaged_init()`, `khugepaged_destroy()`, `__khugepaged_enter()`, `khugepaged_enter_vma()`, `__khugepaged_exit()`, `collapse_pte_mapped_thp()`, `start_stop_khugepaged()`, `khugepaged_min_free_kbytes_update()`, `current_is_khugepaged()`, and `madvise_collapse()`. Core collapse helpers include `collapse_scan_pmd()`, `collapse_huge_page()`, `__collapse_huge_page_isolate()`, `__collapse_huge_page_copy()`, `collapse_scan_file()`, `collapse_file()`, `try_collapse_pte_mapped_thp()`, `retract_page_tables()`, and `collapse_scan_mm_slot()`.

## Control Flow

Eligible VMAs enter through `khugepaged_enter_vma()` or `MADV_HUGEPAGE`, which allocate an `mm_slot`, insert it into the scan list/hash, grab an mm reference, and wake the daemon. The daemon drains LRU additions, scans up to `pages_to_scan`, iterates VMAs under trylocked `mmap_lock`, aligns ranges to PMD boundaries, and calls `collapse_single_pmd()`. Anonymous collapse first scans PTEs for present/young/anon/LRU/refcount/userfaultfd/swap constraints, optionally swaps in missing pages, allocates and charges a huge folio, invalidates notifiers, unlinks the PMD, isolates and copies source pages, installs a huge PMD, then frees old PTE pages. File/shmem collapse scans the page cache, locks and isolates folios, handles holes and swap entries, copies into a new huge folio, stores it as a multi-index xarray entry, retracts PTE tables from mappings, and frees old folios. Existing pte-mapped THPs can be collapsed by verifying all PTEs point at the same huge folio, removing the PTE page table, and optionally installing a huge PMD. `MADV_COLLAPSE` reuses this machinery with forced-collapse policy and returns actionable errno values mapped from `enum scan_result`.

## State and Persistence Behavior

The daemon persists mm scan state through `mm_slot` objects and the global scan cursor. Sysfs tunables persist until changed or rebooted. Page-cache and page-table transformations are persistent kernel memory state changes: successful collapse replaces many base pages or PTE mappings with a PMD-sized folio/mapping and increments counters. Failed scans leave page tables/page cache restored or unchanged.

## Dependencies and Integration Points

This file integrates with THP policy, sysfs attributes under `khugepaged`, mm slot helpers, VMA iteration, rmap, LRU isolation, memcg charging, page table locks, mmu notifiers, swap fault handling, userfaultfd, KSM zero-page handling, shmem, filemap/xarray, DAX exclusion, writeback, tracepoints in `trace/events/huge_memory.h`, kthreads/freezer, NUMA allocation policy, and min-free-kbytes watermarks.

## Risks and Edge Cases

The code is concurrency-heavy. Important risks include racing with mm exit, VMA changes while dropping `mmap_lock` for allocation/writeback, userfaultfd markers, GUP pins and elevated refcounts, dirty/writeback file pages, memory poison during copy, NUMA locality under node reclaim distance, page-table retraction without mmap lock for file mappings, and preserving lazyfree or droppable semantics. Many paths return precise `scan_result` values to avoid corrupting memory and to guide retries.

## Test Signals

Signals include THP/khugepaged tracepoints, sysfs counters (`pages_collapsed`, `full_scans`), vmstat THP scan/allocation events, `MADV_COLLAPSE` errno behavior, anon and shmem collapse tests, read-only file THP tests, userfaultfd exclusion tests, swap-in collapse, dirty/writeback retry behavior, pte-mapped THP retraction, mm exit races, and stress tests with GUP pins, KSM, memcg limits, NUMA, and concurrent truncate/hole-punch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/khugepaged.c -->
