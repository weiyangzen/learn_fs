# subset-b-006131 Research

Grouped research for the listed Linux MM sanitizer files under the Ceph client source mirror. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmemleak.c -->
# sources/distributed-fs/ceph-client/mm/kmemleak.c

## Purpose
`kmemleak.c` implements the kernel memory leak detector runtime. It records allocator events as `struct kmemleak_object` metadata, scans kernel roots and tracked objects for pointer reachability, and reports old allocated objects that remain below their required reference count through `/sys/kernel/debug/kmemleak` and kernel logs.

## Important APIs, Types, And Functions
The central type is `struct kmemleak_object`, which stores object address, size, allocation stack handle, state flags, reference-count color state, checksum, scan areas, task attribution, RB-tree node, RCU list node, and object-local lock. `struct kmemleak_scan_area` restricts scanning to selected subranges. Public allocator-facing entry points include `kmemleak_alloc()`, `kmemleak_alloc_percpu()`, `kmemleak_vmalloc()`, `kmemleak_free()`, `kmemleak_free_part()`, `kmemleak_free_percpu()`, `kmemleak_alloc_phys()`, `kmemleak_free_part_phys()`, and `kmemleak_ignore_phys()`. False-positive and scan-control APIs include `kmemleak_not_leak()`, `kmemleak_transient_leak()`, `kmemleak_ignore()`, `kmemleak_ignore_percpu()`, `kmemleak_scan_area()`, `kmemleak_no_scan()`, and `kmemleak_update_trace()`.

Internal object management is split between `__alloc_object()`, `__link_object()`, `__create_object()`, `find_and_remove_object()`, `delete_object_full()`, `delete_object_part()`, `__delete_object()`, `get_object()`, and `put_object()`. Lookup uses three RB roots selected by `object_tree()`: normal virtual addresses, physical-address objects, and percpu objects. Reporting uses `print_unreferenced()`, `hex_dump_object()`, and seq-file callbacks exposed by `kmemleak_fops`.

## Control Flow
Allocation hooks call `create_object*()`, which allocate metadata from a slab cache or early emergency pool, capture task and stack-depot information, and insert the object into the proper RB tree and global `object_list`. Free hooks remove the object from the tree/list, clear `OBJECT_ALLOCATED`, and release the metadata through RCU once its use count reaches zero.

The scanner (`kmemleak_scan()`) first resets object reference counts, queues already gray roots, and paints unsuitable physical objects black. It then scans root regions: percpu sections, online `struct page` memory, and optionally task stacks. `scan_block()` reads pointer-sized words, filters by known address ranges, and uses `pointer_update_refs()` to locate tracked objects and turn them gray once they reach `min_count`. `scan_gray_list()` recursively scans newly reachable objects until the gray list drains. A checksum pass temporarily grays modified white objects to reduce false positives, then a final pass marks old still-white allocated objects as reported leaks.

Runtime control flows through the debugfs file. Reads iterate reported unreferenced objects under `scan_mutex`; writes accept commands such as `scan`, `clear`, `off`, `stack=on/off`, `scan=on/off`, `scan=<seconds>`, and `dump=<address>`. Auto-scanning is performed by `kmemleak_scan_thread()`, started at late init when configured or by debugfs command.

## State And Persistence
Persistent runtime state is in global lists, RB trees, address bounds, object caches, the early metadata pool, `scan_thread`, scan timing variables, and enable/error flags. Object state persists until corresponding free hooks remove it or kmemleak is disabled and cleanup runs. Allocation stacks are persisted as stack-depot handles. Report state is sticky through `OBJECT_REPORTED` until `clear` paints reported leaks gray. The debugfs file is created in `kmemleak_late_init()`, while static data and BSS objects are registered in `kmemleak_init()` as initial gray roots.

## Dependencies And Integration Points
The file integrates with kernel allocators, vmalloc, percpu allocation, bootmem/memblock partial frees, physical memory tracking, debugfs, kthreads, workqueues, stack depot, RCU, RB trees, KASAN tag stripping, KFENCE size discovery, KCSAN disable/enable around checksums, memory hotplug zone iteration, and task-stack access. It is controlled by `CONFIG_DEBUG_KMEMLEAK*`, `kmemleak=on/off`, and the `verbose` module parameter.

## Risks
Correctness depends on strict lock ordering among `scan_mutex`, `kmemleak_lock`, and object locks. Missed allocator hooks, stale address bounds, overbroad `OBJECT_NO_SCAN`, or incorrect `min_count` choices can hide leaks. RB-tree overlap handling disables kmemleak because corrupt object ranges invalidate lookup safety. Scanning arbitrary memory requires careful KASAN/KCSAN suppression and chunking to avoid faulting, recursion, and latency. Debugfs `off` is irreversible, and cleanup preserves metadata if leaks were found until users explicitly clear it.

## Test Signals
Operational signals are kernel boot/init logs, warnings from overlap or pool exhaustion paths, `/sys/kernel/debug/kmemleak` scan output, `echo scan`, `echo clear`, and `echo dump=<addr>` behavior. Build coverage is gated by `CONFIG_DEBUG_KMEMLEAK`. Runtime validation should exercise kmalloc/vmalloc/percpu/physical allocation hooks, partial frees, false-positive annotations, auto-scan thread start/stop, and verbose leak reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmemleak.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/Makefile -->
# sources/distributed-fs/ceph-client/mm/kmsan/Makefile

## Purpose
This Makefile defines how the KernelMemorySanitizer runtime is built. It collects the always-built KMSAN runtime objects and applies compile flags that prevent the sanitizer runtime from recursively instrumenting itself or being wrapped by other tracing/sanitizer mechanisms.

## Important APIs, Types, And Functions
The build API is Kbuild metadata rather than C symbols. `obj-y` includes `core.o`, `instrumentation.o`, `init.o`, `hooks.o`, `report.o`, and `shadow.o`. `obj-$(CONFIG_KMSAN_KUNIT_TEST)` conditionally adds `kmsan_test.o`. File-specific variables set `KMSAN_SANITIZE := n`, `KCOV_INSTRUMENT := n`, `UBSAN_SANITIZE := n`, remove `$(CC_FLAGS_FTRACE)`, and assign `CC_FLAGS_KMSAN_RUNTIME` to every runtime object.

## Control Flow
During kernel build, Kbuild compiles the runtime with KMSAN, KCOV, UBSAN, branch profiling, ftrace, stack protector, and conserve-stack effects disabled where configured. The KUnit test is the exception: `KMSAN_SANITIZE_kmsan_test.o := y` intentionally instruments the tests so they can trigger KMSAN reports.

## State And Persistence
There is no runtime state. The file persists build policy: which objects are linked into `mm/kmsan/` and which compiler instrumentation is allowed for each object.

## Dependencies And Integration Points
It depends on Kbuild variables, compiler support for `cc-option` and `cc-disable-warning`, and Kconfig symbols `CONFIG_KMSAN_KUNIT_TEST` plus the global KMSAN build mode. It directly affects every C file in this directory by controlling recursion-prone instrumentation.

## Risks
If runtime objects become instrumented by KMSAN, ftrace, branch profiling, KCOV, or UBSAN, the sanitizer may recurse into itself, miss metadata updates, or deadlock. If the KUnit test is not instrumented, many tests stop exercising the compiler-inserted hooks. The disabled uninitialized warning on the test object is intentional because tests deliberately create uninitialized values.

## Test Signals
Build success with KMSAN enabled is the first signal. The stronger signal is `CONFIG_KMSAN_KUNIT_TEST`, where reports are expected from `kmsan_test.o` while the runtime remains non-recursive and stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/core.c -->
# sources/distributed-fs/ceph-client/mm/kmsan/core.c

## Purpose
`core.c` implements the central KMSAN metadata operations: task context initialization, memory poisoning and unpoisoning, metadata copy/move semantics, origin-chain creation, contiguous metadata validation, and range checking that converts poisoned shadow bytes into user-visible reports.

## Important APIs, Types, And Functions
Global `kmsan_enabled` gates runtime behavior, and `DEFINE_PER_CPU(struct kmsan_ctx, kmsan_percpu_ctx)` provides interrupt-context metadata state. `kmsan_internal_task_create()` initializes a task's KMSAN context and unpoisons thread info. `kmsan_internal_poison_memory()` and `kmsan_internal_unpoison_memory()` set shadow/origin state. `kmsan_save_stack_with_flags()` stores origin stacks in stack depot with extra bits for depth and UAF status. `kmsan_internal_memmove_metadata()` copies shadow/origin metadata using memmove ordering. `kmsan_internal_chain_origin()` creates chain-origin stack-depot records. `kmsan_internal_check_memory()` scans a range for poisoned bytes and reports contiguous same-origin regions. `kmsan_metadata_is_contiguous()` validates that a logical range maps to one contiguous metadata range or is entirely untracked.

## Control Flow
Poisoning saves a stack with optional UAF metadata and writes shadow bytes to `0xff` plus matching origin slots. Unpoisoning writes zero shadow bytes and clears origin slots only when the corresponding shadow group is fully zero. Metadata memmove first looks up destination metadata; if the source is untracked it unpoisons the destination, otherwise it copies shadow byte-by-byte in forward or backward order and chains origins for poisoned bytes. Memory checking walks page-sized chunks, groups consecutive poisoned bytes by origin, and calls `kmsan_report()` whenever the origin changes or an untracked/unpoisoned gap ends a group.

## State And Persistence
The file persists global enable state and per-CPU contexts. Memory initialization state is encoded outside this file in shadow and origin pages, while origin stack traces persist in stack depot. Origin chains carry extra bits for maximum chain depth and whether the origin represents use-after-free.

## Dependencies And Integration Points
It depends on `kmsan_get_metadata()` and `kmsan_get_shadow_origin_ptr()` from `shadow.c`, reporting from `report.c`, context definitions from `linux/kmsan_types.h`, stack depot/stacktrace APIs, vmalloc address translation, and page metadata maintained by KMSAN initialization and hooks. It is called by compiler instrumentation, allocator hooks, page hooks, and explicit checks in `hooks.c`.

## Risks
The implementation assumes metadata contiguity for bulk operations; violating that assumption triggers diagnostic output and can make reports unreliable. Origin slot alignment is delicate because one origin covers `KMSAN_ORIGIN_SIZE` bytes. Origin chaining can allocate, so entry points must avoid recursion with runtime guards. A failed stack-depot save can return zero, which intentionally suppresses reports for that origin.

## Test Signals
KUnit tests cover uninitialized kmalloc/page/stack data, UAF origins, function-parameter propagation, `kmsan_check_memory()`, memcpy alignment and origin-gap handling, long origin chains, stackdepot roundtrips, and unpoisoning behavior. Runtime warning paths in `kmsan_metadata_is_contiguous()` are important negative signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/hooks.c -->
# sources/distributed-fs/ceph-client/mm/kmsan/hooks.c

## Purpose
`hooks.c` connects KMSAN to kernel subsystems that allocate, free, map, copy, or hand memory to devices/userspace. It turns allocator and I/O lifecycle events into shadow/origin updates and explicit checks for information leaks.

## Important APIs, Types, And Functions
Task hooks are `kmsan_task_create()` and `kmsan_task_exit()`. Slab and large allocation hooks are `kmsan_slab_alloc()`, `kmsan_slab_free()`, `kmsan_kmalloc_large()`, and `kmsan_kfree_large()`. Vmalloc/ioremap metadata mapping is handled by `kmsan_vunmap_range_noflush()`, `kmsan_ioremap_page_range()`, and `kmsan_iounmap_page_range()`. Transfer hooks include `kmsan_copy_to_user()`, `kmsan_memmove()`, `kmsan_handle_urb()`, `kmsan_handle_dma()`, and `kmsan_handle_dma_sg()`. Public explicit APIs include `kmsan_poison_memory()`, `kmsan_unpoison_memory()`, `kmsan_unpoison_entry_regs()`, `kmsan_check_memory()`, `kmsan_enable_current()`, and `kmsan_disable_current()`.

## Control Flow
Allocation paths poison newly allocated memory unless `__GFP_ZERO` initializes it; free paths poison memory with the UAF bit set, except RCU-safe or constructor-backed slabs where reuse semantics make that unsafe. I/O mappings allocate and map shadow/origin pages in the vmalloc metadata ranges and unwind partial failures. `copy_to_user` checks only bytes actually copied, reporting `REASON_COPY_TO_USER`; if an architecture allows kernel addresses through this path, metadata is copied instead. DMA and USB hooks check outgoing buffers, unpoison incoming buffers, and do both for bidirectional transfers. Runtime guards prevent most hooks from recursing into instrumented code.

## State And Persistence
The hooks update persistent shadow/origin metadata owned by pages, slabs, vmalloc areas, and DMA-visible buffers. `kmsan_disable_current()` and `kmsan_enable_current()` manipulate the current task context depth to suppress or re-enable reporting in selected regions.

## Dependencies And Integration Points
This file integrates with slab internals, page allocation, vmalloc/vmap/ioremap internals, USB URBs, DMA directions and scatterlists, copy-to-user paths, user access save/restore, and KMSAN core metadata functions. It relies on the runtime being compiled without instrumentation because hooks may run in allocator and fault-sensitive paths.

## Risks
Incorrect hook gating can miss initialization events or recurse into KMSAN. Constructor and `SLAB_TYPESAFE_BY_RCU` handling trades UAF detection for valid kernel reuse patterns. Ioremap cleanup must avoid leaking metadata pages or leaving stale vmalloc mappings. DMA handling ignores highmem physical addresses, which avoids unsafe direct mapping assumptions but can reduce coverage. Copy-to-user checks happen after copying because the actual copied byte count is only known afterward.

## Test Signals
KUnit cases exercise kmalloc/kzalloc, large page UAF, vmalloc/vmap initialization, percpu propagation, explicit poison/unpoison/check calls, and copy-from-kernel nofault behavior. Integration signals also come from USB and DMA paths producing `kernel-infoleak`-style KMSAN reports when uninitialized data is submitted outward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/hooks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/init.c -->
# sources/distributed-fs/ceph-client/mm/kmsan/init.c

## Purpose
`init.c` prepares KMSAN metadata during early boot and enables the runtime once enough memory infrastructure exists. It records boot-time ranges needing metadata, allocates shadow/origin pages for reserved and kernel data ranges, and coordinates metadata allocation while memblock pages are released to the buddy allocator.

## Important APIs, Types, And Functions
`struct start_end_pair` and `start_end_pairs[]` store future metadata ranges. `kmsan_record_future_shadow_range()` normalizes and merges those ranges. `kmsan_init_shadow()` records reserved memory, `.data`, and `NODE_DATA()` ranges, then calls `kmsan_init_alloc_meta_for_range()`. `struct metadata_page_pair held_back[]` stores held shadow/origin page blocks per order for eager metadata assignment. `kmsan_memblock_free_pages()` consumes every third memblock-free block as real memory and assigns the previous two blocks as metadata. `kmsan_memblock_discard()` and helper `smallstack` logic split leftovers and free usable thirds. `kmsan_init_runtime()` initializes the initial task, discards leftovers, logs warnings, and sets `kmsan_enabled`.

## Control Flow
Early boot records ranges before the page allocator is fully online. As memblock frees pages, KMSAN holds back two blocks for each order and uses them as shadow and origin for the third block via `kmsan_setup_meta()`. When memblock is about to disappear, leftover held blocks are collected from high to low order, repeatedly grouping triples into page/shadow/origin sets and splitting leftovers to smaller orders. Runtime starts only after this metadata bootstrap is complete.

## State And Persistence
Boot-only state uses `__initdata` arrays and stacks, which are discarded after initialization. Persistent state is page-to-shadow/origin associations installed by `kmsan_setup_meta()` and `kmsan_init_alloc_meta_for_range()`, plus the global `kmsan_enabled` flag set at runtime start.

## Dependencies And Integration Points
The file depends on memblock, reserved memory enumeration, NUMA node data, kernel section symbols, page allocator internals, and `shadow.c` metadata setup helpers. It is part of the architecture-specific KMSAN boot contract because every normal page needs corresponding shadow and origin storage before instrumentation can safely trust metadata.

## Risks
The eager 2/3 metadata allocation scheme is memory-expensive and boot-order-sensitive. `NUM_FUTURE_RANGES` bounds range tracking; overflow is a warning condition. Range merging is intentionally simple and assumes a small number of ranges. Incorrect held-back bookkeeping can either leak memory to metadata or release pages without metadata, causing later false reports or metadata faults.

## Test Signals
Boot logs `Starting KernelMemorySanitizer` and the production-use warning indicate runtime activation. Early boot warnings from KMSAN assertions, page metadata faults, or later metadata contiguity failures indicate initialization problems. KUnit page, vmalloc, and vmap tests indirectly validate this setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/instrumentation.c -->
# sources/distributed-fs/ceph-client/mm/kmsan/instrumentation.c

## Purpose
`instrumentation.c` implements the `__msan_*` ABI expected by Clang's `-fsanitize=kernel-memory` instrumentation. It translates compiler-inserted metadata queries, memory intrinsic wrappers, stack-variable poisoning, origin chaining, and uninitialized-use warnings into KMSAN runtime operations.

## Important APIs, Types, And Functions
Metadata getters include `__msan_metadata_ptr_for_load_n()`, `__msan_metadata_ptr_for_store_n()`, and fixed-size generated getters for 1, 2, 4, and 8 byte loads/stores. `__msan_instrument_asm_store()` handles inline assembly stores. Intrinsic wrappers are `__msan_memmove()`, `__msan_memcpy()`, and `__msan_memset()`. Origin and stack hooks include `__msan_chain_origin()`, `__msan_poison_alloca()`, `__msan_unpoison_alloca()`, `__msan_warning()`, and `__msan_get_context_state()`.

## Control Flow
Load/store metadata getters call `kmsan_get_shadow_origin_ptr()` under `user_access_save()`. Memory intrinsic wrappers preserve parameter-0 metadata for return values, execute the raw memory operation, update destination metadata, and restore return metadata. `__msan_poison_alloca()` creates a special stack-depot origin containing local-variable description and caller PCs, then poisons the stack range. `__msan_warning()` directly reports an uninitialized value use when compiler checks detect undefined behavior. Inline assembly stores best-effort unpoison output memory to avoid false positives from stores the compiler cannot model.

## State And Persistence
The file updates shadow/origin metadata and per-task/per-CPU context-state TLS fields. Stack variable origins persist through stack depot records using `KMSAN_ALLOCA_MAGIC_ORIGIN`, while chained stores use `KMSAN_CHAIN_MAGIC_ORIGIN`.

## Dependencies And Integration Points
It is tightly coupled to Clang's KMSAN ABI, `struct kmsan_context_state`, shadow/origin address mapping from `shadow.c`, core metadata routines, user access helpers, raw `__memcpy`/`__memmove`/`__memset`, and exported symbols needed by instrumented kernel objects.

## Risks
ABI drift with the compiler would break instrumentation silently or at link time. `memset()` cannot propagate metadata from the fill byte because Clang does not pass that parameter metadata here, so the destination is treated as initialized. Assembly-store size is capped to avoid extreme metadata writes, which can lose precision for unusual asm outputs. Runtime guards are required because origin creation can allocate.

## Test Signals
The KUnit suite validates compiler instrumentation through stack variables, function parameter propagation, printk argument checking, memory intrinsic behavior, memset16/32/64, long origin chains, and local-origin report formatting. Link-time availability of all exported `__msan_*` symbols is a build signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/instrumentation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/kmsan.h -->
# sources/distributed-fs/ceph-client/mm/kmsan/kmsan.h

## Purpose
`kmsan.h` is the private runtime header shared by the KMSAN implementation files. It defines metadata constants, origin encoding helpers, bug-reason types, runtime recursion guards, and internal function prototypes.

## Important APIs, Types, And Functions
`struct shadow_origin_ptr` returns paired shadow and origin metadata pointers to instrumentation. Constants include origin magic values, poison flags, origin slot size, maximum origin-chain depth, stack depth, and metadata-kind booleans. `enum kmsan_bug_reason` distinguishes generic uninitialized uses, copy-to-user leaks, and USB submission leaks. Inline helpers `kmsan_get_context()`, `kmsan_in_runtime()`, `kmsan_enter_runtime()`, and `kmsan_leave_runtime()` manage the current runtime context. `kmsan_extra_bits()`, `kmsan_uaf_from_eb()`, and `kmsan_depth_from_eb()` encode stack-depot extra bits. The header declares internal poisoning, checking, metadata, reporting, page, vmalloc, and task functions.

## Control Flow
Runtime code calls `kmsan_enter_runtime()` before operations that may call instrumented code or allocate, then `kmsan_leave_runtime()` afterward. `kmsan_in_runtime()` suppresses recursive KMSAN work and conservatively bails out in nested hard IRQ or NMI contexts. Origin extra-bit helpers are used when saving or interpreting stack-depot handles.

## State And Persistence
The header itself stores no state, but its inline functions access `current->kmsan_ctx` or the per-CPU `kmsan_percpu_ctx`. It defines the encoding that persists in stack-depot handles for UAF status and origin-chain depth.

## Dependencies And Integration Points
It includes scheduler, IRQ, NMI, printk, stackdepot, stacktrace, mm, pgtable, and public `linux/kmsan.h` definitions. It hides implementation details from public KMSAN users while providing shared contracts among `core.c`, `hooks.c`, `instrumentation.c`, `report.c`, `shadow.c`, and `init.c`.

## Risks
The recursion guard is central to avoiding deadlocks and false recursion; incorrect depth accounting triggers `KMSAN_WARN_ON`. The hard IRQ/NMI shortcut can reduce coverage but protects against unsafe locking/allocation. Extra-bit packing must remain compatible with `STACK_DEPOT_EXTRA_BITS` and `KMSAN_MAX_ORIGIN_DEPTH`.

## Test Signals
Compile-time users across all KMSAN runtime files validate declarations. Runtime test signals include lack of recursive reports, correct UAF vs uninitialized bug-type selection, and origin-chain depth handling in KUnit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/kmsan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/kmsan_test.c -->
# sources/distributed-fs/ceph-client/mm/kmsan/kmsan_test.c

## Purpose
`kmsan_test.c` is the KUnit test suite for KMSAN. It intentionally creates initialized, uninitialized, copied, freed, vmapped, percpu, and stack-origin data flows, then verifies whether KMSAN reports or suppresses reports as expected.

## Important APIs, Types, And Functions
The suite uses a console tracepoint probe (`probe_console()`) to capture `BUG: KMSAN:` report headers into the `observed` state. `struct expect_report` describes expected error type and symbol. Helpers `report_available()`, `report_reset()`, and `report_matches()` compare captured output against expected report headers. Test cases cover kmalloc/kzalloc, stack variables, parameters, `kmsan_check_memory()`, vmap/vmalloc, UAF for slab and pages, percpu propagation, printk, memcpy alignment, origin gaps, memset variants, guarded buffers, long origin chains, stack depot, explicit unpoisoning, and `copy_from_kernel_nofault()`.

## Control Flow
Suite init registers the console tracepoint and disables `panic_on_kmsan`. Each test resets observed report state, performs operations intended to create or avoid poisoned metadata, and asserts `report_matches()`. Tests that expect multiple reports call `report_reset()` between checks. Suite exit unregisters the tracepoint, synchronizes tracepoint removal, and restores the original panic setting.

## State And Persistence
Persistent test state is the static `observed` capture buffer protected by a spinlock, plus saved `orig_panic_on_kmsan`. Individual tests allocate transient slab, page, vmalloc, vmap, and stack objects and free/unmap them where needed. The suite mutates global `panic_on_kmsan` for the duration of the tests to keep expected reports from panicking the kernel.

## Dependencies And Integration Points
It depends on KUnit, KMSAN public and private APIs, printk tracepoints, stack depot, slab/page/vmalloc/vmap allocation, percpu variables, `copy_from_kernel_nofault()`, and compiler KMSAN instrumentation enabled specifically for this object by the Makefile.

## Risks
Report matching is string/symbol based and strips offsets, so symbol naming or report formatting changes can break tests. The console tracepoint captures the first matching report and then ignores further output until reset, which keeps tests deterministic but can hide extra unexpected reports within a single test. Tests deliberately use uninitialized variables, so build flags must suppress compiler diagnostics without optimizing away the flows.

## Test Signals
This file is itself the primary test signal for KMSAN. Passing cases indicate correct poisoning/unpoisoning, origin propagation, UAF tagging, report formatting, metadata mapping for vmalloc/vmap/pages, and behavior of compiler-inserted hooks. Failures identify specific runtime contracts because each case has a narrow expected report/no-report outcome.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/kmsan_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/report.c -->
# sources/distributed-fs/ceph-client/mm/kmsan/report.c

## Purpose
`report.c` formats and emits KMSAN bug reports. It converts origins and bug reasons into human-readable stacks, local-variable descriptions, copy-to-user/USB leak types, tainting, and optional panic behavior.

## Important APIs, Types, And Functions
`panic_on_kmsan` is an exported module parameter under `kmsan.panic`. `kmsan_report_lock` serializes reports and protects `report_local_descr`. `get_stack_skipnr()` removes internal `__msan_*` and `kmsan_*` frames from displayed stacks. `pretty_descr()` extracts readable local variable names from Clang-provided descriptions. `kmsan_print_origin()` prints alloca origins, chained store origins, and generic creation stacks. `kmsan_report()` emits the full report.

## Control Flow
`kmsan_report()` exits if KMSAN is disabled, already in runtime, suppressed for the current task, or given a zero origin. Otherwise it enters runtime, saves user-access state, locks report output, chooses a bug type from reason plus the origin UAF bit, prints the current access stack, prints origin details, prints byte-range and user-address context when available, taints the kernel, optionally panics, then restores state and leaves runtime. `kmsan_print_origin()` follows origin-chain records until it reaches an alloca or generic origin.

## State And Persistence
The file persists the panic setting and report serialization buffer. It also taints the kernel with `TAINT_BAD_PAGE` for each report. Origin data itself remains in stack depot and is only read here.

## Dependencies And Integration Points
It depends on stack depot, stacktrace, printk, module parameters, console output, user access helpers, KMSAN origin encodings from `kmsan.h`, and report callers in `core.c`, `hooks.c`, and `instrumentation.c`. KUnit tests observe its output through the printk console tracepoint.

## Risks
Report code runs in sensitive contexts and must avoid recursion. Holding a raw spinlock while printing serializes output but increases latency. Local description parsing depends on Clang's current string shape. `panic_on_kmsan` is intentionally dangerous and must be controlled for tests.

## Test Signals
KUnit report matching validates bug-type strings such as `uninit-value`, `use-after-free`, `kernel-infoleak`, and USB leak variants indirectly through expected headers. Long origin-chain and stackdepot tests validate origin printing does not create new KMSAN reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/report.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/shadow.c -->
# sources/distributed-fs/ceph-client/mm/kmsan/shadow.c

## Purpose
`shadow.c` implements KMSAN shadow/origin address translation and page metadata setup. It maps kernel, module, vmalloc, vmap, and page-backed addresses to metadata storage, provides dummy metadata for untracked accesses, and maintains per-page shadow/origin associations.

## Important APIs, Types, And Functions
Page helpers include `shadow_ptr_for()`, `origin_ptr_for()`, `page_has_metadata()`, and `set_no_shadow_origin_page()`. `vmalloc_meta()` computes metadata virtual addresses for vmalloc and module regions. `kmsan_get_shadow_origin_ptr()` returns metadata pairs for compiler instrumentation, falling back to dummy load/store pages. `kmsan_get_metadata()` resolves one shadow or origin pointer for an address. Page operations include `kmsan_copy_page_meta()`, `kmsan_alloc_page()`, `kmsan_free_page()`, `kmsan_vmap_pages_range_noflush()`, `kmsan_init_alloc_meta_for_range()`, and `kmsan_setup_meta()`.

## Control Flow
Instrumentation asks for metadata through `kmsan_get_shadow_origin_ptr()`. If KMSAN is disabled or metadata is unavailable, loads use a zero-filled dummy page and stores use a separate dummy page. For direct-mapped memory, `kmsan_get_metadata()` checks architecture metadata first, then resolves the backing `struct page` and its shadow/origin pages. For vmalloc/module addresses, metadata addresses are computed from fixed KMSAN metadata ranges. Page allocation poisons or clears metadata according to `__GFP_ZERO` and runtime state; freeing poisons memory with the UAF flag. Vmap maps metadata pages for each mapped data page into the vmalloc metadata ranges.

## State And Persistence
Per-page `kmsan_shadow` and `kmsan_origin` fields hold persistent metadata associations. `dummy_load_page` and `dummy_store_page` provide stable fallback metadata. Boot-time `kmsan_init_alloc_meta_for_range()` allocates and assigns metadata for existing ranges, while `kmsan_setup_meta()` assigns metadata for pages entering the allocator.

## Dependencies And Integration Points
The file depends on architecture KMSAN helpers, TLB/cache flush APIs, memblock, vmalloc metadata address constants, page allocator internals, and core poisoning/origin functions. It is the backing layer for `core.c`, `instrumentation.c`, `hooks.c`, and `init.c`.

## Risks
Returning dummy metadata avoids crashes but can hide real initialization state for untracked regions. Origin addresses require `KMSAN_ORIGIN_SIZE` alignment. Vmap metadata mapping must flush TLB/cache ranges and clean up allocations on errors. Page allocation assumes shadow/origin pages are contiguous for the order being initialized.

## Test Signals
KUnit cases covering uninitialized pages, page UAF, vmalloc initialization, vmap/vunmap, guarded vmalloc buffers, and metadata copy behavior indirectly validate this file. Metadata contiguity warnings from `core.c` are strong signals of bad shadow mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/kmsan/shadow.c -->
