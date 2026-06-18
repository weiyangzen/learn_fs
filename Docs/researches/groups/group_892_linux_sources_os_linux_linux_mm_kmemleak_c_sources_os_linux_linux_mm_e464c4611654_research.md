# Group Research: group_892_linux_sources_os_linux_linux_mm_kmemleak_c_sources_os_linux_linux_mm_e464c4611654

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux/mm/kmemleak.c` and `sources/os/linux/linux/mm/kmsan/*`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kmemleak.c -->
# File Research: sources/os/linux/linux/mm/kmemleak.c

## Role

Implements the Linux kernel memory leak detector. `kmemleak` tracks allocations reported by kernel allocators, stores per-allocation metadata in rbtrees and lists, periodically scans kernel memory for pointer references, and reports allocated objects that appear unreachable through `/sys/kernel/debug/kmemleak`.

## Core Model

- `struct kmemleak_object` is the metadata record for each tracked allocation. It stores allocation address, size, flags, minimum reference count, current reference count, checksum, stack-depot allocation trace, optional scan subareas, creation time, pid, and comm.
- Tracked objects live in `object_list` and in one of three rbtrees:
  - `object_tree_root` for normal virtual addresses.
  - `object_phys_tree_root` for physical-address tracked objects.
  - `object_percpu_tree_root` for percpu allocations.
- Object colors are encoded through `count` and `min_count`:
  - white: not enough references, leak candidate.
  - gray: referenced or explicitly marked false positive.
  - black: ignored and not scanned.
- Object deletion uses `use_count` plus RCU freeing so scans and debugfs iteration can safely traverse metadata while frees occur.

## Locking and Lifetime

- `kmemleak_lock` protects `object_list`, deletion state, and all object rbtrees.
- Each object has `object->lock` protecting mutable metadata and preventing the underlying allocation from being freed while scanned.
- `scan_mutex` serializes memory scans, debugfs control operations, scan-thread state, and gray-list use.
- Required nesting is documented as `scan_mutex -> object->lock -> kmemleak_lock -> other_object->lock`.
- `DELSTATE_NO_DELETE` lets long RCU traversals temporarily reschedule without losing a current object from `object_list`.

## Allocation Tracking

- Public callbacks include:
  - `kmemleak_alloc()`, `kmemleak_free()`, `kmemleak_free_part()`.
  - `kmemleak_alloc_percpu()`, `kmemleak_free_percpu()`.
  - `kmemleak_vmalloc()`.
  - `kmemleak_alloc_phys()`, `kmemleak_free_part_phys()`.
- `__alloc_object()` allocates metadata from a slab cache when available, otherwise from the static emergency pool.
- `__link_object()` inserts metadata into the right rbtree and global list, updates address bounds used to reject impossible pointer values quickly, and rejects overlapping tracked ranges.
- Partial frees split an existing tracked object into left and right remainder objects around the freed range.
- Allocation traces are captured through stack depot after `object_cache` exists.

## Annotation API

- `kmemleak_not_leak()` paints an object gray so it remains scanned but is not reported.
- `kmemleak_ignore()` and `kmemleak_ignore_percpu()` paint objects black so they are not scanned or reported.
- `kmemleak_transient_leak()` resets an object checksum to delay reporting until a later scan.
- `kmemleak_scan_area()` limits scanning to selected subranges inside an object, falling back to full scan if scan-area metadata cannot be allocated.
- `kmemleak_no_scan()` marks an object as not containing references while still allowing references to the object to be found.
- `kmemleak_update_trace()` replaces an object allocation stack trace when the original allocation site is not useful.
- `kmemleak_vmalloc()` handles the `vm_struct` reference by requiring `min_count = 2` and forwarding surplus references via `excess_ref`.

## Scan Algorithm

`kmemleak_scan()` performs a mark-and-sweep style pass:

1. Set `jiffies_last_scan`.
2. Iterate all objects, reset `count` to white, preserve already-gray roots, and blacken physical objects outside lowmem.
3. Scan percpu sections on SMP systems.
4. Scan in-use `struct page` objects for each populated zone under memory-hotplug protection.
5. Optionally scan every task stack.
6. Drain `gray_list`, scanning each referenced object and discovering further references.
7. For still-white objects, compute CRC checksums and temporarily gray recently modified candidates to avoid reporting unstable objects.
8. Drain the gray list again.
9. Report old, still-white, allocated objects as suspected leaks.

Pointers are read word-aligned from scanned memory. Each candidate is KASAN-tag-reset, checked against known address bounds, looked up by alias in the normal and percpu rbtrees, and then used to increment the target object's reference count. Self-references and simple circular `excess_ref` cases are ignored.

## Scanning Details

- Large blocks are scanned in `MAX_SCAN_SIZE` chunks to reduce scheduling latency.
- KASAN and KCSAN are disabled around direct memory reads and checksum generation.
- Per-cpu objects are scanned on every possible CPU.
- Physical objects are scanned through `__va()` only when considered valid lowmem.
- Objects with scan areas scan only those areas unless `OBJECT_FULL_SCAN` is set.
- Checksums use `crc32()` over object contents, with percpu checksums XORed across CPUs.

## Reporting and Debugfs

- `print_unreferenced()` emits address, type, size, task info, a short hex dump, checksum, and allocation backtrace.
- Hex dumps are capped to two rows to avoid seq-file/log spam.
- `kmemleak_seq_*` implements debugfs iteration over reported unreferenced objects.
- `/sys/kernel/debug/kmemleak` write commands support:
  - `off`
  - `stack=on` / `stack=off`
  - `scan=on` / `scan=off`
  - `scan=<seconds>`
  - `scan`
  - `clear`
  - `dump=<address>`
- `clear` either marks currently reported leaks gray or, after disable, frees internal metadata.

## Initialization and Shutdown

- `kmemleak_boot_config()` handles `kmemleak=off` and `kmemleak=on`.
- `kmemleak_init()` initializes timing, metadata caches, and root scan objects for `.data`, `.bss`, and possibly `.data..ro_after_init`.
- `kmemleak_late_init()` creates the debugfs file, starts automatic scanning when configured, and reports remaining emergency-pool capacity.
- `kmemleak_disable()` irreversibly stops allocation/free tracing and schedules cleanup when late init has run.
- Cleanup stops the scan thread, disables free tracing, and frees metadata if no leaks were preserved for later debugfs inspection.

## Dependencies

Uses allocator hooks, debugfs, seq_file, kthreads, rbtrees, stack depot, RCU, memblock, memory-hotplug zone iteration, KASAN/KFENCE/KCSAN integration, percpu APIs, CRC32, and kernel task-stack helpers.

## Research Notes

This file is the full implementation of kmemleak’s runtime: metadata management, leak detection, reporting, debugfs control, and lifecycle. Correctness depends heavily on the documented lock ordering, RCU object lifetime, pointer alias handling, and conservative scan roots. False positives are reduced through minimum age, object annotations, checksums for recently modified objects, task-stack scanning, and explicit gray/black controls.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kmemleak.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kmsan/Makefile -->
# File Research: sources/os/linux/linux/mm/kmsan/Makefile

## Role

Build rules for KernelMemorySanitizer runtime objects and KMSAN KUnit tests.

## Contents

- Builds KMSAN runtime objects into `obj-y`:
  - `core.o`
  - `instrumentation.o`
  - `init.o`
  - `hooks.o`
  - `report.o`
  - `shadow.o`
- Disables sanitizers and coverage for the runtime:
  - `KMSAN_SANITIZE := n`
  - `KCOV_INSTRUMENT := n`
  - `UBSAN_SANITIZE := n`
- Adds runtime C flags:
  - `-fno-stack-protector`
  - optional `-fno-conserve-stack`
  - `-DDISABLE_BRANCH_PROFILING`
- Removes ftrace flags from every runtime object to avoid recursion.
- Applies the runtime flags uniformly to all KMSAN runtime objects.
- Builds `kmsan_test.o` only under `CONFIG_KMSAN_KUNIT_TEST`.
- Enables KMSAN instrumentation for `kmsan_test.o` and disables the compiler `uninitialized` warning there.

## Research Notes

The Makefile is safety-critical because the sanitizer runtime must not recursively instrument itself with KMSAN, ftrace, KCOV, UBSAN, stack protector, or branch profiling. The test object is intentionally different: it is instrumented so it can validate KMSAN behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kmsan/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kmsan/core.c -->
# File Research: sources/os/linux/linux/mm/kmsan/core.c

## Role

Core KMSAN runtime library. It manages task contexts, poisoning and unpoisoning memory metadata, origin stack creation and chaining, metadata copying, range checks, and metadata-contiguity validation.

## Key State

- `kmsan_enabled` gates runtime behavior globally.
- `DEFINE_PER_CPU(struct kmsan_ctx, kmsan_percpu_ctx)` provides interrupt/NMI-safe context storage when `current->kmsan_ctx` is unavailable.
- Task creation clears the task KMSAN context and unpoisons `thread_info`.

## Poisoning and Origins

- `kmsan_internal_poison_memory()` saves an origin stack with optional use-after-free extra bits and fills shadow/origin metadata.
- `kmsan_internal_unpoison_memory()` clears shadow and origin metadata.
- `kmsan_save_stack_with_flags()` captures a bounded stack trace and stores it in stack depot with KMSAN extra bits.
- `kmsan_internal_chain_origin()` creates a chained origin record for stores of uninitialized values, preserving use-after-free state and bounding chain depth to `KMSAN_MAX_ORIGIN_DEPTH`.

## Metadata Mutation

- `kmsan_internal_set_shadow_origin()` fills shadow bytes and updates origin slots at `KMSAN_ORIGIN_SIZE` granularity.
- Origin updates preserve nonzero origins unless all corresponding shadow bytes are clear.
- Missing metadata is tolerated for untracked ranges, but checked operations warn if metadata was expected.

## Metadata Copying

- `kmsan_internal_memmove_metadata()` copies shadow/origin metadata with `memmove()` semantics.
- It handles overlapping ranges by choosing forward or backward iteration.
- If source metadata is unavailable, destination memory is treated as initialized.
- Nonzero source shadow bytes trigger origin chaining so reports can show store propagation history.
- It avoids repeatedly chaining identical adjacent origins by caching the previous old/new origin pair.

## Memory Checking

- `kmsan_internal_check_memory()` scans a range for poisoned shadow bytes.
- It groups consecutive poisoned bytes with the same origin and calls `kmsan_report()` for each group.
- It handles untracked pages by flushing any pending report and skipping the untracked chunk.
- `kmsan_metadata_is_contiguous()` verifies that metadata for a cross-page range is either entirely untracked or linearly contiguous in shadow and origin memory.

## Vmalloc Helper

- `kmsan_vmalloc_to_page_or_null()` accepts only vmalloc/module metadata addresses, maps them to pages, and rejects invalid PFNs.

## Dependencies

Uses stack trace/depot, preemption/interrupt helpers, vmalloc, highmem, page and zone helpers, slab internals, and KMSAN shadow APIs.

## Research Notes

This file contains KMSAN’s central metadata invariants. Most exported hooks eventually delegate here. The most important correctness properties are contiguous metadata, correct origin-slot handling for unaligned copies, bounded origin chains, and avoiding allocation/instrumentation recursion while creating stack-depot origins.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kmsan/core.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kmsan/hooks.c -->
# File Research: sources/os/linux/linux/mm/kmsan/hooks.c

## Role

KMSAN hooks for kernel subsystems. These functions connect KMSAN metadata updates to allocation/free paths, vmalloc/ioremap mapping, user copies, USB URBs, DMA transfers, and public KMSAN check/poison APIs.

## Allocation Hooks

- `kmsan_task_create()` initializes a task KMSAN context inside a runtime guard.
- `kmsan_task_exit()` disables KMSAN for the current task when exiting.
- `kmsan_slab_alloc()` poisons slab object memory unless the allocation is zeroed, constructed, RCU-typesafe, untracked, or inside KMSAN runtime.
- `kmsan_slab_free()` poisons freed slab objects as use-after-free origins unless constructor or RCU semantics prevent that.
- `kmsan_kmalloc_large()` and `kmsan_kfree_large()` mirror slab handling for large page-backed allocations.
- Free poisoning avoids reclaim allocations by using `GFP_KERNEL & ~__GFP_RECLAIM`.

## Vmalloc and I/O Mapping

- `vmalloc_shadow()` and `vmalloc_origin()` derive vmalloc/module metadata addresses with `kmsan_get_metadata()`.
- `kmsan_vunmap_range_noflush()` unmaps shadow and origin vmalloc metadata and flushes caches.
- `kmsan_ioremap_page_range()` allocates zeroed shadow/origin pages for ioremap mappings, maps them into metadata virtual ranges, handles partial failure cleanup, and flushes metadata ranges.
- `kmsan_iounmap_page_range()` unmaps and frees metadata pages for ioremap ranges.

## Usercopy and Memory Movement

- `kmsan_copy_to_user()` checks copied kernel bytes for uninitialized data after copy completion.
- If the target address is actually kernel memory on architectures without overlapping user/kernel address space, it copies metadata instead of reporting a user leak.
- `kmsan_memmove()` exports metadata movement for ordinary memmove-like operations.

## USB and DMA

- `kmsan_handle_urb()` checks outbound URB transfer buffers and unpoisons inbound buffers.
- `kmsan_handle_dma_page()` applies direction-specific checking/unpoisoning:
  - `DMA_TO_DEVICE`: check initialized.
  - `DMA_FROM_DEVICE`: unpoison after device writes.
  - `DMA_BIDIRECTIONAL`: check then unpoison.
  - `DMA_NONE`: no action.
- `kmsan_handle_dma()` ignores highmem physical addresses, converts lowmem to virtual addresses, and processes page-by-page to avoid crossing unrelated allocations.
- `kmsan_handle_dma_sg()` applies DMA handling over scatterlists.

## Public KMSAN API

- `kmsan_poison_memory()` can poison arbitrary memory but exits inside runtime to avoid stack-depot allocation deadlocks.
- `kmsan_unpoison_memory()` can run even from runtime because it does not allocate or call instrumented code.
- `kmsan_unpoison_entry_regs()` unpoisons interrupt/syscall entry registers.
- `kmsan_check_memory()` reports uninitialized bytes in a range.
- `kmsan_enable_current()` and `kmsan_disable_current()` manipulate the per-task disable depth.

## Dependencies

Uses slab internals, vmalloc mapping internals, user access state save/restore, USB, DMA direction, scatterlist APIs, and KMSAN core metadata routines.

## Research Notes

This file is the integration boundary between KMSAN and the rest of the kernel. It is deliberately careful about runtime recursion, constructor/RCU allocator semantics, device direction semantics, and user/kernel address-space ambiguity during copy-to-user handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kmsan/hooks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kmsan/init.c -->
# File Research: sources/os/linux/linux/mm/kmsan/init.c

## Role

Boot-time initialization for KMSAN metadata. It records early memory ranges requiring metadata, allocates metadata before normal allocation is fully available, and completes runtime startup.

## Future Metadata Ranges

- `kmsan_record_future_shadow_range()` records virtual ranges for later metadata allocation.
- Ranges are page-aligned and merged with overlapping existing entries.
- The static table holds up to `NUM_FUTURE_RANGES` entries and warns on overflow or invalid ranges.

## Early Shadow Initialization

`kmsan_init_shadow()` records and allocates metadata for:

- Reserved memblock ranges.
- Kernel `.data`.
- `NODE_DATA()` structures for each online node.

It calls `kmsan_init_alloc_meta_for_range()` for every merged recorded range.

## Memblock Page Recycling Scheme

- `kmsan_memblock_free_pages()` implements eager metadata allocation while memblock frees pages to the page allocator.
- For each order, the first freed block is held as shadow, the second as origin, and the third becomes the real page block receiving those metadata blocks.
- Metadata association is installed with `kmsan_setup_meta()`.
- This effectively uses two thirds of incoming early pages as metadata for the remaining third until normal setup completes.

## Leftover Metadata Recovery

- `held_back[]` stores unmatched shadow/origin blocks by page order.
- `smallstack` and `collect` provide a small temporary stack for splitting leftover higher-order blocks.
- `kmsan_memblock_discard()` walks orders high-to-low, collects leftovers, groups blocks in triples, assigns two as metadata for the third, frees usable pages, and splits remainders to lower order.

## Runtime Enable

- `kmsan_init_runtime()` initializes the `init_task` KMSAN context, discards/reclaims leftover memblock metadata blocks, logs startup warnings, and sets `kmsan_enabled = true`.

## Dependencies

Uses memblock, reserved memory iteration, node data, section symbols, page allocator core free path, and KMSAN shadow setup.

## Research Notes

This file solves the bootstrap problem that KMSAN needs shadow/origin memory before the ordinary allocator can safely run under KMSAN. The held-back triple scheme is central: two page blocks become metadata for the third, with leftovers split and recovered at the end.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kmsan/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kmsan/instrumentation.c -->
# File Research: sources/os/linux/linux/mm/kmsan/instrumentation.c

## Role

Implements the compiler-facing `__msan_*` API emitted by Clang for `-fsanitize=kernel-memory`. It returns metadata pointers for instrumented loads/stores, handles compiler-rewritten memory intrinsics, creates stack-local origins, and emits KMSAN warnings.

## Metadata Pointer Hooks

- `__msan_metadata_ptr_for_load_n()` and `__msan_metadata_ptr_for_store_n()` handle non-standard access sizes.
- Macro-generated hooks handle fixed-size loads and stores for 1, 2, 4, and 8 bytes.
- All metadata pointer retrieval uses `user_access_save()` / `user_access_restore()` around `kmsan_get_shadow_origin_ptr()`.
- Bad asm/user/untracked addresses are redirected away from real metadata by lower-level dummy metadata behavior.

## Inline Assembly

- `__msan_instrument_asm_store()` unpoisons memory written by inline assembly on a best-effort basis.
- It intentionally omits the runtime-recursion check so entry/exit assembly stores can be marked initialized.
- Stores larger than 4096 bytes warn once and are clamped to 8 bytes.

## Memory Intrinsics

- `__msan_memmove()` calls `__memmove()`, copies metadata with memmove semantics, and restores return-value metadata from destination parameter metadata.
- `__msan_memcpy()` calls `__memcpy()` and then uses memmove-style metadata copying for correctness.
- `__msan_memset()` calls `__memset()` and unpoisons the destination, because Clang does not pass metadata for the fill byte.
- Zero-length memmove/memcpy calls return without metadata work.

## Origin and Stack Local Handling

- `__msan_chain_origin()` wraps `kmsan_internal_chain_origin()` under runtime and user-access guards.
- `__msan_poison_alloca()` creates an alloca-origin stack-depot record containing a magic value, local variable description, and caller return addresses, then poisons the stack variable.
- `__msan_unpoison_alloca()` clears metadata for stack locals.
- `__msan_warning()` reports undefined use of an uninitialized value.
- `__msan_get_context_state()` returns the current context state holding parameter and return-value TLS metadata.

## Dependencies

Uses KMSAN context state, stack depot, user access helpers, KMSAN string/intrinsic wrappers, and compiler-generated calling conventions.

## Research Notes

This file is the required ABI between compiler instrumentation and the kernel runtime. Its correctness depends on preserving parameter/return metadata through rewritten intrinsics, avoiding recursive runtime instrumentation, and creating meaningful origins for uninitialized stack locals.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kmsan/instrumentation.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kmsan/kmsan.h -->
# File Research: sources/os/linux/linux/mm/kmsan/kmsan.h

## Role

Private KMSAN runtime header. It defines runtime constants, metadata pointer structures, bug reasons, context helpers, recursion guards, origin extra-bit encoding, internal function prototypes, and address classification helpers.

## Key Definitions

- Magic origin markers:
  - `KMSAN_ALLOCA_MAGIC_ORIGIN`
  - `KMSAN_CHAIN_MAGIC_ORIGIN`
- Poison flags:
  - `KMSAN_POISON_NOCHECK`
  - `KMSAN_POISON_CHECK`
  - `KMSAN_POISON_FREE`
- Metadata constants:
  - `KMSAN_ORIGIN_SIZE` is 4 bytes.
  - `KMSAN_MAX_ORIGIN_DEPTH` is 7.
  - `KMSAN_STACK_DEPTH` is 64.
  - `KMSAN_META_SHADOW` and `KMSAN_META_ORIGIN` select metadata type.
- `struct shadow_origin_ptr` packages shadow and origin pointers for compiler hooks.
- `enum kmsan_bug_reason` distinguishes generic uninitialized use, copy-to-user leaks, and USB submit leaks.

## Runtime Context

- Declares per-CPU KMSAN context for interrupt contexts.
- `kmsan_get_context()` returns `current->kmsan_ctx` in task context or the raw per-CPU context otherwise.
- `kmsan_in_runtime()` suppresses recursive runtime entry and conservatively treats nested hard IRQs and NMIs as runtime.
- `kmsan_enter_runtime()` and `kmsan_leave_runtime()` increment/decrement per-context runtime nesting with warnings on unexpected nesting.

## Origin Extra Bits

- `kmsan_extra_bits()` packs origin chain depth and use-after-free state into stack-depot extra bits.
- `kmsan_uaf_from_eb()` and `kmsan_depth_from_eb()` unpack those fields.

## Internal API

Declares internal routines for:

- Metadata copying, poisoning, unpoisoning, and setting shadow/origin.
- Origin chaining and stack saving.
- Task-context creation.
- Memory checking and reporting.
- Metadata contiguity checks.
- Vmalloc metadata page lookup.
- Page metadata setup.
- Early range metadata allocation.

## Address Helpers

- `kmsan_internal_is_module_addr()` checks module virtual address range.
- `kmsan_internal_is_vmalloc_addr()` checks vmalloc virtual address range.
- These are simple non-instrumented replacements for helpers that might recurse inside KMSAN runtime.

## Research Notes

This header is the coupling point for KMSAN runtime files. The inline runtime guard and context selection logic are particularly important because nearly every KMSAN hook depends on avoiding recursive sanitizer execution.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kmsan/kmsan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kmsan/kmsan_test.c -->
# File Research: sources/os/linux/linux/mm/kmsan/kmsan_test.c

## Role

KUnit test suite for KMSAN. It triggers expected uninitialized-memory, use-after-free, and no-report cases, captures console reports through the printk console tracepoint, and verifies report type and symbol matching.

## Report Capture Harness

- `observed` stores a spinlock-protected captured report header and flags.
- `probe_console()` watches console output for `BUG: KMSAN: `, copies the first matching line, and stops capture for the current test.
- `report_available()`, `report_reset()`, and `report_matches()` provide test assertions.
- `struct expect_report` records expected bug type and symbol.
- Matching strips exact offsets and module suffixes to avoid brittle comparisons.

## Helpers

- `check_true()`, `check_false()`, and `USE(x)` force conditional use of values so KMSAN reports undefined use.
- Expectation macros define no-report, uninitialized-value, and use-after-free expectations.
- `memcpy_noinline()` prevents compiler inlining when testing metadata propagation through `memcpy()`.
- `do_uninit_local_array()` deliberately writes uninitialized bytes into a selected array range.
- `fibonacci()` creates long origin chains.

## Covered Test Cases

- Heap allocation:
  - uninitialized `kmalloc()`.
  - initialized `memset()` after `kmalloc()`.
  - initialized `kzalloc()`.
- Stack and calls:
  - uninitialized stack variables.
  - initialized stack variables.
  - uninitialized function parameters.
  - multiple parameter propagation.
- Explicit checking:
  - `kmsan_check_memory()` on uninitialized local arrays.
- Virtual memory:
  - initialized pages mapped by `vmap()`.
  - `vmalloc()` buffers initialized by `memset()`.
  - guard-page edge safety for `memset()`.
- Use-after-free:
  - freed `kmalloc()` object.
  - freed single page.
  - freed high-order page tail.
- Per-CPU and printk:
  - uninitialized values through per-CPU storage.
  - uninitialized values passed to `pr_info()`.
- Copy and memset behavior:
  - initialized `memcpy()`.
  - uninitialized aligned-to-aligned copy.
  - uninitialized aligned-to-unaligned copy.
  - preservation of nonzero origins across initialized gaps.
  - `memset16()`, `memset32()`, `memset64()`.
- Origin and stack depot:
  - long origin-chain depth behavior.
  - stackdepot save/fetch/print round trip.
- Public API and nofault copy:
  - `kmsan_unpoison_memory()` equivalence with instrumentation.
  - `copy_from_kernel_nofault()` with uninitialized source.

## Suite Lifecycle

- `test_init()` resets captured report state before each test.
- `kmsan_suite_init()` registers the console tracepoint and disables `panic_on_kmsan`.
- `kmsan_suite_exit()` unregisters the tracepoint, synchronizes tracepoint removal, and restores `panic_on_kmsan`.
- The suite is registered as `kmsan` and carries GPL module metadata.

## Research Notes

The tests validate both positive and negative behavior across allocator hooks, compiler instrumentation, metadata propagation, origin handling, and reporting. The suite intentionally relies on instrumenting `kmsan_test.o`, unlike the runtime itself.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kmsan/kmsan_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kmsan/report.c -->
# File Research: sources/os/linux/linux/mm/kmsan/report.c

## Role

KMSAN reporting implementation. It formats bug reports, decodes origin chains from stack depot, serializes report output, and optionally panics on reports.

## Global State

- `kmsan_report_lock` serializes report formatting.
- `report_local_descr` is a fixed buffer for local variable descriptions.
- `panic_on_kmsan` is exported and exposed as module parameter `kmsan.panic`.

## Stack Filtering

- `get_stack_skipnr()` skips internal `__msan_*` and `kmsan_*` frames so reports point at user/kernel code of interest.
- It formats symbols into a small buffer and stops at the first non-runtime frame.

## Origin Formatting

- `pretty_descr()` converts Clang local descriptions like `----local@function` into a cleaner local variable name.
- `kmsan_print_origin()` decodes stack-depot records:
  - alloca origins identify a local variable and creation PCs.
  - chain origins show where uninitialized data was stored, then continue to the previous origin.
  - ordinary origins print the creation stack.
- Chained origins at maximum depth print a truncation notice.
- Fetched chained stack entries are unpoisoned before printing.

## Report Emission

`kmsan_report()`:

- Returns early when KMSAN is disabled, already in runtime, disabled for the current task, or missing an origin.
- Enters runtime, saves user-access state, and takes the report lock.
- Determines bug type from reason and origin UAF bit:
  - `uninit-value`
  - `use-after-free`
  - `kernel-infoleak`
  - `kernel-infoleak-after-free`
  - `kernel-usb-infoleak`
  - `kernel-usb-infoleak-after-free`
- Captures and prints the current stack after skipping runtime frames.
- Prints the origin chain.
- Prints byte-range, access address, and user-copy destination details when available.
- Adds `TAINT_BAD_PAGE` with unreliable lockdep state.
- Panics when `panic_on_kmsan` is set.

## Dependencies

Uses console/module parameters, stack depot, stack trace printing, user access save/restore, raw spinlocks, and KMSAN core helpers.

## Research Notes

This file is focused on producing useful and non-recursive reports. The raw spinlock plus runtime guard prevents report interleaving and sanitizer recursion, while stack filtering and origin-chain decoding make reports actionable.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kmsan/report.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/kmsan/shadow.c -->
# File Research: sources/os/linux/linux/mm/kmsan/shadow.c

## Role

KMSAN shadow/origin metadata address implementation. It maps kernel addresses to metadata, provides dummy metadata for untracked accesses, copies page metadata, handles page allocation/free metadata, maps vmalloc metadata, and installs early page metadata.

## Metadata Storage

- Direct-map pages store metadata page pointers in `struct page` fields:
  - `page->kmsan_shadow`
  - `page->kmsan_origin`
- `shadow_ptr_for()` and `origin_ptr_for()` return page-addressed metadata.
- `page_has_metadata()` requires both shadow and origin pages.
- Metadata pages themselves are marked with no metadata to avoid recursive tracking.
- `dummy_load_page` returns zero metadata for untracked loads.
- `dummy_store_page` absorbs stores to untracked metadata without affecting later loads.

## Address Translation

- `vmalloc_meta()` maps vmalloc and module addresses into parallel shadow/origin virtual ranges:
  - `KMSAN_VMALLOC_SHADOW_START`
  - `KMSAN_VMALLOC_ORIGIN_START`
  - `KMSAN_MODULES_SHADOW_START`
  - `KMSAN_MODULES_ORIGIN_START`
- Origin addresses are aligned down to `KMSAN_ORIGIN_SIZE`.
- `kmsan_get_metadata()` handles vmalloc/module metadata, architecture-specific metadata, and direct-map page metadata.
- Invalid or metadata-less addresses return `NULL`.

## Compiler Metadata Pointer API

- `kmsan_get_shadow_origin_ptr()` returns shadow/origin pointers for instrumented loads/stores.
- If KMSAN is disabled or metadata is absent, it returns dummy metadata:
  - stores go to dummy store page.
  - loads read zero shadow/origin from dummy load page.
- It warns on access sizes larger than a page and verifies metadata contiguity.

## Page Metadata Operations

- `kmsan_copy_page_meta()` copies shadow and origin metadata from one page to another, or unpoisons destination if source lacks metadata.
- `kmsan_alloc_page()` initializes metadata for newly allocated pages:
  - zeroed allocations or disabled KMSAN get clear metadata.
  - nonzero allocations get shadow set to poisoned and origin filled with a saved stack handle.
  - runtime allocations are left alone to avoid recursion.
- `kmsan_free_page()` poisons freed pages with use-after-free origins.
- `kmsan_setup_meta()` assigns contiguous shadow/origin page arrays to a page block.

## Vmap and Early Allocation

- `kmsan_vmap_pages_range_noflush()` maps metadata pages corresponding to physical pages into vmalloc/module metadata ranges and flushes TLB/cache state.
- It builds arrays of source shadow/origin pages, maps both ranges with `PAGE_KERNEL`, and frees temporary arrays.
- `kmsan_init_alloc_meta_for_range()` allocates shadow and origin memory with memblock for boot-time ranges and assigns metadata pages to every covered real page.

## Dependencies

Uses architecture KMSAN hooks, vmalloc/module metadata layout constants, memblock, TLB/cache flushing, slab helpers, page allocator hooks, and KMSAN core origin/poison routines.

## Research Notes

This file defines where KMSAN metadata lives. The fallback dummy pages are essential for tolerating untracked memory, while direct-map page metadata and vmalloc/module parallel ranges provide the main metadata mapping mechanisms.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/kmsan/shadow.c -->