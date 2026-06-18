<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/string_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/string_kunit.c

## Purpose
KUnit coverage for generic kernel string and memory helpers in `linux/string.h`, including typed memset variants, string length/search/compare/copy/append helpers, fixed-size non-string conversions, suffix checks, and optional microbenchmarks.

## APIs, Types, and Functions
The suite registers as `string` through `kunit_test_suites()`. Test cases cover `memset16()`, `memset32()`, `memset64()`, `strlen()`, `strnlen()`, `strchr()`, `strrchr()`, `strnchr()`, `strspn()`, `strcspn()`, `strcmp()`, `strncmp()`, `strcasecmp()`, `strncasecmp()`, `strscpy()`, `strscpy_pad()`, `strcat()`, `strncat()`, `strlcat()`, `strtomem()`, `strtomem_pad()`, `memtostr()`, `memtostr_pad()`, and `strends()`. Helper macros such as `STRCMP_TEST_EXPECT_*` normalize compare-result expectations, while `strscpy_check()` verifies destination bytes, padding, terminators, and untouched poison bytes. Optional `CONFIG_STRING_KUNIT_BENCH` enables benchmark helpers `alloc_max_bench_buffer()`, `fill_random_string()`, and `STRING_BENCH_BUF()`.

## Control Flow, State, and Persistence
Most tests allocate per-test buffers with KUnit managed allocation or `vmalloc()`, iterate offsets and lengths near page-aligned buffer ends, invoke a target helper, and assert exact return values and memory contents. Large compare tests use two static 2048-byte buffers and mutate one byte at `STRCMP_CHANGE_POINT`. Append tests use a volatile global `unconst` to avoid constant folding. Benchmarks seed pseudo-random data deterministically, warm up calls, disable preemption while timing, then print throughput/latency with `kunit_info()`. There is no persistent runtime state outside static compare buffers and benchmark constants.

## Dependencies and Integration
Depends on KUnit, slab/vmalloc allocation, printk, random state helpers, timekeeping, math64, and standard kernel string APIs. It integrates with the kernel test framework as a module or built-in test suite and is sensitive to architecture-optimized string implementations.

## Risks and Test Signals
Risks include missing cases around overlapping buffers, very large counts beyond the small `strscpy_check()` buffer, non-ASCII case folding expectations, and benchmark noise if used as a performance signal. Strong test signals are exhaustive offset/length sweeps for length/search helpers, poison-byte overflow checks for copy helpers, long-string compare change points, and optional deterministic benchmarks gated by `CONFIG_STRING_KUNIT_BENCH`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/string_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_bits.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_bits.c

## Purpose
KUnit and compile-time checks for bit construction and mask macros from `linux/bits.h`, especially typed `BIT_*`, `GENMASK*`, and input validation behavior.

## APIs, Types, and Functions
The file uses `_Generic` through `assert_type()` and `static_assert()` to validate result types and values for `BIT_U8()`, `BIT_U16()`, `BIT_U32()`, `BIT_U64()`, `GENMASK()`, `GENMASK_ULL()`, and typed `GENMASK_U8/U16/U32/U64()`. Runtime KUnit cases exercise `__GENMASK()`, `__GENMASK_ULL()`, `GENMASK()`, `GENMASK_ULL()`, `GENMASK_U128()` under `CONFIG_ARCH_SUPPORTS_INT128`, and `GENMASK_INPUT_CHECK()`.

## Control Flow, State, and Persistence
Compile-time assertions fire during build if macro types or constants change. Runtime tests are direct expectation checks over known mask ranges and over unknown variable inputs for `GENMASK_INPUT_CHECK()`. The `TEST_GENMASK_FAILURES` block intentionally contains invalid macro invocations for opt-in compile-failure testing. There is no runtime state.

## Dependencies and Integration
Depends on KUnit, `linux/bits.h`, and integer type definitions. It integrates with the `bits-test` KUnit suite and complements build-time macro diagnostics.

## Risks and Test Signals
Risks include architecture differences in `unsigned long` width, compiler behavior around constant expressions, and limited coverage for assembly users noted by the FIXME. Test signals are compile-time type/value assertions, runtime boundary masks at high bits, optional expected compile failures, and 128-bit checks when the architecture supports them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_bits.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_fprobe.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_fprobe.c

## Purpose
KUnit sanity tests for the fprobe infrastructure, validating entry probes, return probes, symbol-list registration, per-entry data, skipped exits, and multiple fprobes on one target.

## APIs, Types, and Functions
The suite uses `struct fprobe`, `register_fprobe()`, `register_fprobe_syms()`, `unregister_fprobe()`, `ftrace_regs_get_return_value()`, `ftrace_location_range()`, and kallsyms lookup helpers. Target functions `fprobe_selftest_target()` and `fprobe_selftest_target2()` are `noinline` and called through function pointers. Handlers include `fp_entry_handler()`, `fp_exit_handler()`, `entry_only_handler()`, `fprobe_entry_multi_handler()`, and `fprobe_exit_multi_handler()`.

## Control Flow, State, and Persistence
`fprobe_test_init()` seeds `rand1`, installs indirect target pointers, and resolves ftrace locations. Each test sets `current_test`, registers probes for a symbol pattern or symbol list, calls target functions, asserts handler side effects, and unregisters probes. Entry handlers assert non-preemptible execution and correct instruction pointer; exit handlers assert return values and optional `entry_data_size` storage. `test_fprobe_skip()` makes the entry handler return nonzero to suppress the exit handler. Multi-probe tests register two probes in both orders and validate all handlers fire once.

## Dependencies and Integration
Depends on fprobe/ftrace, kallsyms, random number generation, KUnit, and architecture support for function tracing. It integrates with dynamic instrumentation internals and may be built only when fprobe support is available.

## Risks and Test Signals
Risks include target inlining despite safeguards, missing ftrace locations, architecture-specific return register handling, global state shared across tests, and cleanup sensitivity if registration fails partway. Test signals include handler call counts, return-value validation, `fp.nmissed` behavior, data handoff through entry storage, and multi-registration order coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_fprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_hash.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_hash.c

## Purpose
KUnit coverage for integer and string hashing helpers in `linux/hash.h` and `linux/stringhash.h`, checking equivalence between generic and architecture-specific implementations and sufficient bit coverage.

## APIs, Types, and Functions
Helper functions `xorshift()`, `mod255()`, and `fill_buf()` generate deterministic nonzero strings. `test_int_hash()` exercises `__hash_32()`, `hash_32()`, and `hash_64()` for output widths 1 through 32, optionally comparing to `__hash_32_generic()` and `hash_64_generic()` under architecture feature macros. `test_string_or()` checks `full_name_hash()` coverage. `test_hash_or()` compares `hashlen_string()` length/hash results to `full_name_hash()` across substrings and feeds hash outputs into integer hash tests.

## Control Flow, State, and Persistence
The test fills a 256-byte buffer with deterministic nonzero bytes, then loops over every substring endpoint. For each substring it temporarily NUL-terminates at `j`, computes hashes from `buf+i`, updates OR accumulators, and asserts lengths and bounded k-bit outputs. Final assertions require OR coverage of all expected result bits. State is local to each KUnit case.

## Dependencies and Integration
Depends on KUnit, kernel hash/stringhash headers, compiler attributes, and architecture feature macros such as `HAVE_ARCH__HASH_32` and `HAVE_ARCH_HASH_64`. It integrates as the `hash` KUnit suite.

## Risks and Test Signals
Risks include cubic runtime sensitivity to `SIZE`, probabilistic coverage assumptions, and conditional paths that only run on some architectures. Test signals are exhaustive substring comparisons, generic-vs-arch equality where required, k-bit upper-bound checks, and final OR masks covering all bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_kprobes.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_kprobes.c

## Purpose
KUnit sanity tests for kprobe and kretprobe registration, handler invocation, missed-recursion accounting, multi-probe registration, and optional stacktrace correctness on kretprobe trampolines.

## APIs, Types, and Functions
Uses `struct kprobe`, `struct kretprobe`, `register_kprobe()`, `register_kprobes()`, `unregister_kprobe()`, `register_kretprobe()`, `register_kretprobes()`, `regs_return_value()`, `stack_trace_save()`, and `stack_trace_save_regs()`. Target functions include `kprobe_target()`, `kprobe_target2()`, `kprobe_recursed_target()`, and stacktrace driver/target functions. `KP_CLEAR()` resets probe fields before reuse.

## Control Flow, State, and Persistence
`kprobes_test_init()` clears static probe structures, assigns function pointers to avoid inlining, and seeds `rand1`. Tests register probes by symbol name, call target functions, assert pre/post or return handler side effects, and unregister. The recursion test places a kprobe on `kprobe_recursed_target()` while handlers call that target and expects `nmissed == 2`. Kretprobe tests run only under `CONFIG_KRETPROBES`; stacktrace tests additionally require `CONFIG_ARCH_CORRECT_STACKTRACE_ON_KRETPROBE` and verify saved stack frames contain original return addresses.

## Dependencies and Integration
Depends on kprobes/kretprobes, random generation, KUnit, stacktrace support, architecture unwind behavior, and relevant config options. It integrates with the `kprobes_test` suite and exercises low-level dynamic instrumentation.

## Risks and Test Signals
Risks include architecture-specific unwinder behavior, module-vs-built-in differences for `stack_trace_save_regs()`, global static probe state, target inlining, and unregister cleanup after partial failures. Test signals include handler values, return-value checks, recursion miss count, batch register/unregister behavior, and nested kretprobe stacktrace validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_kprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_linear_ranges.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_linear_ranges.c

## Purpose
KUnit tests for `linear_range` helpers, using two simple selector-to-value ranges to verify value lookup, selector lookup, and total value counts.

## APIs, Types, and Functions
Defines two `struct linear_range` entries with `LINEAR_RANGE()`. Test cases call `linear_range_get_value_array()`, `linear_range_get_selector_high()`, `linear_range_values_in_range_array()`, and `linear_range_get_selector_low_array()`.

## Control Flow, State, and Persistence
Static arrays describe expected selectors and values for two ranges. Each test iterates expected entries and asserts exact return codes, selector/value mapping, and found flags. Boundary checks verify selectors outside the range and values below/above the range. State is static immutable test data only.

## Dependencies and Integration
Depends on KUnit and `linux/linear_range.h`. It registers as `linear-ranges-test` and targets helpers used by regulator, power, and driver tables.

## Risks and Test Signals
Risks include limited range complexity, no overlap or descending-range cases, and no large arithmetic overflow stress. Test signals cover both single-range and array-of-ranges lookup, below-minimum high selector behavior, above-maximum low selector behavior, and total count computation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_linear_ranges.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_list_sort.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_list_sort.c

## Purpose
KUnit test for `list_sort()`, checking sorting correctness, list integrity, element preservation, poison fields, and stability for equivalent keys.

## APIs, Types, and Functions
Defines `struct debug_el` around `struct list_head`, poison fields, sortable `value`, and original `serial`. `check()` validates element identity and poisons through `test->priv`. `cmp()` unwraps list nodes and compares values after validating both elements. `list_sort_test()` allocates elements, populates a linked list, calls `list_sort()`, and verifies the result.

## Control Flow, State, and Persistence
The test allocates an array of original element pointers and 642 list elements (`512+128+2`), fills values with random numbers below one third of the length to force duplicates, appends each element, sorts, then walks the list. During the walk it asserts bidirectional linkage, nondecreasing compare results, stable serial ordering for equal values, valid poisons, and unchanged list length. All memory is KUnit-managed.

## Dependencies and Integration
Depends on KUnit, `linux/list_sort.h`, list primitives, slab allocation, and random helpers. It integrates as the `list_sort` suite.

## Risks and Test Signals
Risks include random input not being reproducible unless the global random stream is controlled, a single chosen list length, and comparator subtraction overflow if value ranges changed. Test signals are structural integrity checks, stable-sort validation, poison preservation, and a length chosen to hit multiple internal list-sort carry cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_list_sort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_ratelimit.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_ratelimit.c

## Purpose
KUnit tests for `___ratelimit()` behavior, covering basic burst/interval semantics, disabled/unlimited modes, re-enabling, and concurrent stress accounting.

## APIs, Types, and Functions
Uses `DEFINE_RATELIMIT_STATE()`, `RATELIMIT_STATE_INIT_FLAGS()`, `___ratelimit()`, `ratelimit_state_reset_miss()`, `kthread_run()`, `kthread_stop()`, `schedule_timeout_idle()`, and CPU mask helpers. `struct stress_kthread` records attempts, allowed calls, limited calls, missed counts, and task pointer.

## Control Flow, State, and Persistence
`test_ratelimit_smoke()` consumes a three-event burst, sleeps partial and full intervals, mutates `testrl.burst` and `testrl.interval`, and checks boolean decisions. `test_ratelimit_stress()` spawns one low-priority worker per online CPU for two seconds; each worker loops on `___ratelimit()`, counts results, and reads missed counts on exit. The final aggregate asserts allowed+limited equals attempts and limited equals missed. Static ratelimit state and `doneflag` persist across the module lifetime.

## Dependencies and Integration
Depends on KUnit, ratelimit internals, scheduler sleeps, kthreads, CPU masks, and memory allocation. Both test cases are marked `KUNIT_CASE_SLOW`.

## Risks and Test Signals
Risks include wall-clock duration, scheduler timing sensitivity, `doneflag` not reset if the stress test were rerun in the same module instance, high CPU-count fanout, and missed cleanup if thread creation partially fails. Test signals include interval boundary behavior, burst-zero disable semantics, interval-zero unlimited semantics, and concurrent accounting consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_ratelimit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_sort.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_sort.c

## Purpose
Simple KUnit regression test for the generic `sort()` helper on integer arrays.

## APIs, Types, and Functions
Defines `cmpint()` as the comparator and `test_sort()` as the sole test. It uses `sort(base, num, size, cmp, swap)` with a NULL custom swap function.

## Control Flow, State, and Persistence
The test allocates 1000 integers, fills them with a deterministic multiplicative-modulo sequence, sorts the full array, and verifies nondecreasing order. It then refills `TEST_LEN - 1` entries with a different seed, sorts that shorter range, and verifies order again. State is local KUnit-managed memory.

## Dependencies and Integration
Depends on KUnit, `linux/sort.h`, slab allocation, and module metadata. It registers as `lib_sort`.

## Risks and Test Signals
Risks include comparator subtraction overflow if values are expanded beyond the current small range, no stability check, and limited type coverage. Test signals are deterministic input, full-length and off-by-one-length sort coverage, and post-sort monotonic assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_sort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/usercopy_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/usercopy_kunit.c

## Purpose
KUnit tests for user access helpers: valid and invalid `copy_to_user()`/`copy_from_user()`, scalar `get_user()`/`put_user()`, `check_zeroed_user()`, and `copy_struct_from_user()` ABI-extension semantics.

## APIs, Types, and Functions
Uses `copy_to_user()`, `copy_from_user()`, `get_user()`, `put_user()`, `clear_user()`, `check_zeroed_user()`, `copy_struct_from_user()`, `kunit_vm_mmap()`, and `memchr_inv()`. `struct usercopy_test_priv` holds kernel memory, user memory, and buffer size. `TEST_U64` conditionally enables 64-bit scalar access tests on capable 32-bit architectures and all 64-bit architectures.

## Control Flow, State, and Persistence
`usercopy_test_init()` skips non-MMU systems, allocates two pages of kernel memory, maps two pages of user memory below `TASK_SIZE`, and stores both in `test->priv`. Valid tests copy a page both ways and exercise scalar get/put. Invalid tests skip alternate address-space or non-MMU systems, then confirm kernel addresses cast to `__user` are rejected and destination zeroing/preservation occurs. `check_zeroed_user()` is compared to `memchr_inv()` over every subrange of a 1024-byte page-boundary-spanning pattern. `copy_struct_from_user()` checks equal-size, old-userspace shorter input with zero-fill, too-large nonzero tail rejection, and too-large zero tail success.

## Dependencies and Integration
Depends on KUnit, MMU support, `uaccess`, mmap helpers, scheduler/task address limits, and architecture user access enforcement. It registers as `usercopy`.

## Risks and Test Signals
Risks include architecture-specific user address models, disabled explosive reversed-copy coverage, runtime cost of O(n^2) subrange zero checks, and user memory permissions using `PROT_EXEC` though execute is not central. Test signals include page-boundary scanning, valid scalar sizes, invalid kernel/user confusion rejection, copy-tail zeroing, and struct ABI compatibility behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/usercopy_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/util_macros_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/util_macros_kunit.c

## Purpose
KUnit tests for `find_closest()` and `find_closest_descending()` helpers from `linux/util_macros.h`, including driver-like lookup tables and arithmetic progressions.

## APIs, Types, and Functions
Uses `FIND_CLOSEST_RANGE_CHECK` and `FIND_CLOSEST_DESC_RANGE_CHECK` macros to loop integer input ranges and assert returned indexes. Test functions are `test_find_closest()` and `test_find_closest_descending()`.

## Control Flow, State, and Persistence
Each test defines several static sorted arrays: real-world style averaging/oversampling/watchdog tables, increasing or decreasing arithmetic arrays, unsigned arrays, and mixed negative-to-positive arrays. For each inclusive input range, it calls the target helper and asserts the expected nearest index. There is no persistent runtime state.

## Dependencies and Integration
Depends on KUnit and `linux/util_macros.h`. It registers as the `util_macros.h` suite and protects helper behavior used by drivers that select the nearest supported hardware setting.

## Risks and Test Signals
Risks include no explicit tie-breaking explanation outside expected ranges, no empty-array coverage, and compile-time macro behavior depending on array type. Test signals are broad contiguous input ranges, ascending and descending variants, signed/unsigned arrays, negative inputs, and regression coverage for the AD7616 oversampling table mentioned in comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/util_macros_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/uuid_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/uuid_kunit.c

## Purpose
KUnit tests for UUID/GUID parsing in `lib/uuid.c`, validating byte ordering for GUID and UUID forms and rejection of malformed strings.

## APIs, Types, and Functions
Defines `struct test_uuid_data` with a canonical UUID string, expected little-endian `guid_t`, and expected big-endian `uuid_t`. Tests call `guid_parse()`, `uuid_parse()`, `guid_equal()`, and `uuid_equal()`.

## Control Flow, State, and Persistence
Valid tests iterate `test_uuid_test_data`, parse each string into a local object, and compare against `GUID_INIT()` or `UUID_INIT()` constants. Invalid tests iterate strings missing hyphens, containing invalid hex, or containing insufficient data, expecting `-EINVAL`. There is no mutable state.

## Dependencies and Integration
Depends on KUnit and `linux/uuid.h`. It registers as the `uuid` suite and directly covers the parser used by kernel subsystems accepting textual UUIDs.

## Risks and Test Signals
Risks include limited invalid formats, no uppercase-string coverage, and no direct test for `uuid_is_valid()` or random generation. Test signals are explicit GUID-vs-UUID endian expectations and common parse-failure cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/uuid_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/textsearch.c -->
# sources/distributed-fs/ceph-client/lib/textsearch.c

## Purpose
Core generic text-search framework for linear and non-linear data. It provides algorithm registration, algorithm lookup/autoload, configuration lifecycle, and a convenience wrapper for contiguous buffers.

## APIs, Types, and Functions
Exports `textsearch_register()`, `textsearch_unregister()`, `textsearch_prepare()`, `textsearch_destroy()`, and `textsearch_find_continuous()`. Internal state includes the RCU-protected `ts_ops` list and `ts_mod_lock`. `lookup_ts_algo()` resolves registered algorithms and takes a module reference. `struct ts_linear_state` and `get_linear_data()` adapt contiguous memory to the block-fetch callback model.

## Control Flow, State, and Persistence
Algorithms register a populated `struct ts_ops` with a unique name. Registration validates required callbacks, checks for duplicate names under a spinlock, and appends via `list_add_tail_rcu()`. Lookup walks the list under RCU and uses `try_module_get()` to pin the provider. `textsearch_prepare()` rejects zero-length patterns, optionally requests `ts_<algo>` modules under `TS_AUTOLOAD`, calls the algorithm `init()`, stores `ops` in the returned config, and drops the module reference on error. `textsearch_destroy()` calls an optional algorithm destructor, releases the module, and frees the config. Linear searches install `get_linear_data` into `conf->get_next_block` and stash buffer metadata in `state->cb`.

## Dependencies and Integration
Depends on module loading, RCU lists, spinlocks, error pointers, slab allocation, and `linux/textsearch.h`. Algorithms in `ts_bm.c`, `ts_kmp.c`, and `ts_fsm.c` integrate by registering `struct ts_ops`; users include networking, filtering, and other subsystems that need pattern search over fragmented data.

## Risks and Test Signals
Risks include unregister lifetime requiring RCU-safe users, mutation of `conf->get_next_block` by the linear helper making shared configs caller-sensitive, autoload deadlock avoidance when `TS_AUTOLOAD` is omitted, and algorithm-specific pattern compatibility. Test signals should include duplicate registration, missing callback validation, module autoload success/failure, concurrent search with separate `ts_state`, destroy reference release, and continuous versus block-backed searches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/textsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/timerqueue.c -->
# sources/distributed-fs/ceph-client/lib/timerqueue.c

## Purpose
Generic timer queue implementation using cached rbtrees to maintain timers ordered by expiration time.

## APIs, Types, and Functions
Exports `timerqueue_add()`, `timerqueue_del()`, `timerqueue_iterate_next()`, and `timerqueue_linked_add()`. Helpers `__timerqueue_less()` and `__tq_linked_less()` compare `expires` values for ordinary and linked timerqueue node wrappers.

## Control Flow, State, and Persistence
`timerqueue_add()` warns if the node is already linked, then calls `rb_add_cached()` and returns whether the inserted node is the leftmost/earliest timer. `timerqueue_del()` warns if the node is empty, erases it with `rb_erase_cached()`, clears the node, and returns whether the queue remains non-empty. `timerqueue_iterate_next()` wraps `rb_next()` to move forward without mutation. `timerqueue_linked_add()` inserts a linked-node variant. All queue state is caller-owned; this file performs no locking.

## Dependencies and Integration
Depends on `linux/timerqueue.h`, rbtree helpers, warnings, and GPL exports. It integrates with timer users that need ordered expiration queues and must provide external serialization.

## Risks and Test Signals
Risks include caller failure to serialize operations, adding an already-linked node, deleting an unlinked node, duplicate expiration ordering not being stable beyond rbtree behavior, and misuse of the linked-node container layout. Test signals include earliest-node return values, delete-last behavior, iteration order, duplicate expiration cases, and lockdep or race tests in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/timerqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/trace_readwrite.c -->
# sources/distributed-fs/ceph-client/lib/trace_readwrite.c

## Purpose
Defines and exports MMIO read/write tracepoint helpers when `CONFIG_TRACE_MMIO_ACCESS` is enabled.

## APIs, Types, and Functions
With `CREATE_TRACE_POINTS`, includes `trace/events/rwmmio.h` to instantiate tracepoints. Under `CONFIG_TRACE_MMIO_ACCESS`, exports `log_write_mmio()`, `log_post_write_mmio()`, `log_read_mmio()`, and `log_post_read_mmio()`, plus tracepoint symbols `rwmmio_write`, `rwmmio_post_write`, `rwmmio_read`, and `rwmmio_post_read`.

## Control Flow, State, and Persistence
Each helper is a thin wrapper that forwards caller addresses, width, value where applicable, and `__iomem` address to the generated tracepoint. There is no local state or persistence.

## Dependencies and Integration
Depends on ftrace, module exports, `linux/io.h`, and the generated rwmmio trace events. It integrates with instrumented MMIO accessors or architecture code that calls these logging hooks.

## Risks and Test Signals
Risks include trace overhead on hot MMIO paths, incorrect caller-address plumbing by callers, and no compiled helpers when the config is off. Test signals include tracepoint visibility, correct pre/post event ordering, width/value/address encoding, and build coverage for both config states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/trace_readwrite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ts_bm.c -->
# sources/distributed-fs/ceph-client/lib/ts_bm.c

## Purpose
Boyer-Moore implementation for the textsearch framework, optimized for performance on blocks where matches do not need to span block boundaries.

## APIs, Types, and Functions
Defines private `struct ts_bm` with uppercase or raw pattern bytes, pattern length, bad-character shift table, and flexible good-suffix shift table. Core functions are `bm_init()`, `bm_find()`, `bm_get_pattern()`, `bm_get_pattern_len()`, `compute_prefix_tbl()`, `subpattern()`, and `matchpat()`. `bm_ops` registers the algorithm name `"bm"`.

## Control Flow, State, and Persistence
`bm_init()` rejects zero length and allocation-size overflow, allocates one `ts_config` private area containing shift tables and pattern bytes, stores flags, uppercases the pattern for `TS_IGNORECASE`, and precomputes bad/good shifts. `bm_find()` starts from `state->offset`, fetches blocks through `conf->get_next_block()`, scans each block right-to-left within candidate windows, and returns the absolute match offset. It advances to the next block when no match is found within the current block and returns `UINT_MAX` at end. Module init/exit register/unregister with the core textsearch registry.

## Dependencies and Integration
Depends on `linux/textsearch.h`, ctype helpers, module infrastructure, overflow-check helpers, and the core registry in `textsearch.c`. Users select it via `textsearch_prepare("bm", ...)`.

## Risks and Test Signals
Risks include the documented inability to find matches spanning multiple blocks, correctness of shift-table arithmetic, case-folding limited to byte-wise `toupper()`, and allocation overflow handling. Test signals should compare against KMP on linear data, exercise fragmented data with boundary-spanning matches that BM should miss, test ignore-case bad-shift entries, zero-length rejection, and very large length overflow rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ts_bm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ts_fsm.c -->
# sources/distributed-fs/ceph-client/lib/ts_fsm.c

## Purpose
Finite-state-machine textsearch algorithm that matches tokenized patterns over streamed byte blocks, supporting specific bytes, ctype-like token classes, wildcards, optional/multiple recurrence, and an optional head-ignore mode.

## APIs, Types, and Functions
Defines private `struct ts_fsm` with token count and copied `struct ts_fsm_token` array. `token_map` translates public token type IDs into ctype bitmasks, and `token_lookup_tbl[256]` classifies bytes. Core functions are `match_token()`, `fsm_find()`, `fsm_init()`, `fsm_get_pattern()`, and `fsm_get_pattern_len()`. `fsm_ops` registers algorithm name `"fsm"`.

## Control Flow, State, and Persistence
`fsm_init()` validates that pattern length is an integral nonzero token array, rejects `TS_IGNORECASE`, validates token type and recurrence limits, permits `TS_FSM_HEAD_IGNORE` only as a non-final first token, allocates config storage, copies tokens, and maps token types to bitmasks. `fsm_find()` reads blocks via `get_next_block()`, maintains consumed byte count and block index, determines strict mode from the first token, and walks tokens applying recurrence rules. Mismatches either fail in strict mode or advance and restart in non-strict mode. On a match, it updates `state->offset` to the end and returns the match start.

## Dependencies and Integration
Depends on textsearch core, `linux/textsearch_fsm.h`, module registration, and ctype constants. It integrates as an algorithm selectable by `textsearch_prepare("fsm", ...)`.

## Risks and Test Signals
Risks include complex block-boundary control flow, unsupported ignore-case mode, potential allocation-size overflow because `sizeof(*fsm) + len` is not explicitly checked, and assumptions encoded in the manual 256-entry classification table. Test signals should include strict and non-strict matches, every recurrence type, token classes near ASCII/non-ASCII boundaries, block splits at every token boundary, invalid token validation, and final-token multi/any behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ts_fsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ts_kmp.c -->
# sources/distributed-fs/ceph-client/lib/ts_kmp.c

## Purpose
Knuth-Morris-Pratt implementation for the textsearch framework, providing linear-time matching that can carry partial matches across data blocks.

## APIs, Types, and Functions
Defines private `struct ts_kmp` with pattern pointer, pattern length, and flexible prefix table. Core functions are `kmp_init()`, `kmp_find()`, `compute_prefix_tbl()`, `kmp_get_pattern()`, and `kmp_get_pattern_len()`. `kmp_ops` registers algorithm name `"kmp"`.

## Control Flow, State, and Persistence
`kmp_init()` rejects zero-length patterns and allocation overflow, allocates a config private area containing prefix table and pattern bytes, computes the prefix table using optional case folding, and stores an uppercase pattern for `TS_IGNORECASE`. `kmp_find()` initializes `q` from zero for each call, starts reading at `state->offset`, fetches blocks, advances through bytes while falling back through the prefix table on mismatch, and returns the absolute start offset once `q == pattern_len`. It updates `state->offset` to the end of the match so `textsearch_next()` can continue.

## Dependencies and Integration
Depends on textsearch core, ctype helpers, module registration, overflow-check helpers, and algorithm selection through `textsearch_prepare("kmp", ...)`.

## Risks and Test Signals
Risks include case folding being byte-oriented, prefix table correctness for repeated prefixes, and callers needing to preserve `ts_state` between successive calls. Test signals include matches spanning block boundaries, repeated-pattern fallback cases, ignore-case matching, zero-length and overflow rejection, and comparison against naive search on randomized data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ts_kmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ubsan.c -->
# sources/distributed-fs/ceph-client/lib/ubsan.c

## Purpose
Kernel UBSAN runtime reporting implementation. It maps compiler-emitted sanitizer handlers to kernel warnings, KUnit failures, stack dumps, optional panic-on-warn, and trap-mode failure strings.

## APIs, Types, and Functions
When trap support is enabled, `report_ubsan_failure()` maps Clang sanitizer handler codes to short reason strings based on enabled `CONFIG_UBSAN_*` checks. Without `CONFIG_UBSAN_TRAP`, the file exports compiler ABI handlers such as `__ubsan_handle_add_overflow()`, `__ubsan_handle_sub_overflow()`, `__ubsan_handle_mul_overflow()`, `__ubsan_handle_negate_overflow()`, `__ubsan_handle_implicit_conversion()`, `__ubsan_handle_divrem_overflow()`, `__ubsan_handle_type_mismatch()`, `__ubsan_handle_type_mismatch_v1()`, `__ubsan_handle_out_of_bounds()`, `__ubsan_handle_shift_out_of_bounds()`, `__ubsan_handle_builtin_unreachable()`, `__ubsan_handle_load_invalid_value()`, and `__ubsan_handle_alignment_assumption()`. Helpers decode type descriptors, values, source locations, and suppression state.

## Control Flow, State, and Persistence
Reports are suppressed when the current task is already in UBSAN or when the `source_location` has its `REPORTED_BIT` set via `test_and_set_bit()`. `ubsan_prologue()` increments `current->in_ubsan`, prints a cut marker and source location, and fails the current KUnit test. Handlers format type/value-specific diagnostics, then `ubsan_epilogue()` dumps the stack, decrements `in_ubsan`, and honors panic-on-warn. Type mismatch and shift/invalid-value paths wrap reporting with `user_access_save()`/`user_access_restore()` to avoid user access state issues. `__ubsan_handle_builtin_unreachable()` panics after reporting because it cannot return safely.

## Dependencies and Integration
Depends on compiler-emitted UBSAN metadata structures from `ubsan.h`, task state, printk/warn infrastructure, stack dumps, KUnit bug integration, bitops, user access controls, and sanitizer config options. It exports ABI symbols expected by instrumented kernel code.

## Risks and Test Signals
Risks include ABI drift with Clang sanitizer handler metadata, endian-specific packing of `source_location.reported`, recursive reporting suppression hiding secondary issues, formatting 128-bit values only when supported, and panic behavior for unreachable reports. Test signals include KUnit tests that intentionally trigger each handler, trap-mode code-to-string mapping for enabled configs, duplicate-location suppression, user-access-state restoration, signed/unsigned value formatting, and panic-on-warn behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ubsan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ubsan.h -->
# sources/distributed-fs/ceph-client/lib/ubsan.h

## Purpose
Private UBSAN runtime ABI header defining Clang sanitizer check IDs, metadata layouts, max integer types, calling convention adjustments, and handler prototypes used by `ubsan.c`.

## APIs, Types, and Functions
Defines `enum ubsan_checks`, type-kind constants, `struct type_descriptor`, `struct source_location`, and per-check metadata structures: `overflow_data`, `implicit_conversion_data`, `type_mismatch_data`, `type_mismatch_data_v1`, `type_mismatch_data_common`, `nonnull_arg_data`, `out_of_bounds_data`, `shift_out_of_bounds_data`, `unreachable_data`, `invalid_value_data`, and `alignment_assumption_data`. Typedefs `s_max` and `u_max` use `__int128` when available. `ubsan_linkage` handles old Clang i386 calling convention quirks. Prototypes cover all exported handlers.

## Control Flow, State, and Persistence
This header has no executable control flow. Its key state contract is the `source_location` union that overlays an atomic-like reported bit with line/column fields, and the exact field order expected by compiler-emitted metadata.

## Dependencies and Integration
Depends on kernel integer types, config macros for architecture int128 support, x86/Clang version checks, and the Clang CodeGen sanitizer ABI. It is included by `ubsan.c` and must match compiler output.

## Risks and Test Signals
Risks include sanitizer enum ordering drift, calling convention mismatch on older Clang/i386, source-location bit overlay bugs on endian/word-size combinations, and unused metadata structs becoming stale. Test signals include building UBSAN-instrumented kernels with supported Clang versions, 32-bit x86 builds with old Clang, big-endian 64-bit builds, and handler invocation tests validating field decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ubsan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ucmpdi2.c -->
# sources/distributed-fs/ceph-client/lib/ucmpdi2.c

## Purpose
Provides the libgcc-style `__ucmpdi2()` helper for comparing two unsigned 64-bit integers on architectures/toolchains that need an out-of-line runtime routine.

## APIs, Types, and Functions
Exports `word_type notrace __ucmpdi2(unsigned long long a, unsigned long long b)`. It uses `DWunion` from `linux/libgcc.h` to access high and low 32-bit halves.

## Control Flow, State, and Persistence
The function compares unsigned high halves first, returning 0 if `a < b` and 2 if `a > b`. If high halves match, it compares low halves with the same return codes. Equal values return 1. There is no state.

## Dependencies and Integration
Depends on module exports and kernel libgcc compatibility types. It integrates with compiler-generated calls that expect GCC's comparison return convention for doubleword unsigned comparisons.

## Risks and Test Signals
Risks include ABI return convention mismatch, endian/union layout assumptions delegated to `DWunion`, and accidental tracing recursion if `notrace` were removed. Test signals include compiler runtime tests for less/equal/greater high and low half combinations and architecture builds that emit `__ucmpdi2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ucmpdi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ucs2_string.c -->
# sources/distributed-fs/ceph-client/lib/ucs2_string.c

## Purpose
UCS-2 string helper implementation for length, bounded copy, comparison, UTF-8 size calculation, and UCS-2 to UTF-8 conversion.

## APIs, Types, and Functions
Exports `ucs2_strnlen()`, `ucs2_strlen()`, `ucs2_strsize()`, `ucs2_strscpy()`, `ucs2_strncmp()`, `ucs2_utf8size()`, and `ucs2_as_utf8()`. Operates on `ucs2_char_t` and emits UTF-8 bytes into `u8` buffers.

## Control Flow, State, and Persistence
Length helpers walk until NUL or maximum character count. `ucs2_strsize()` converts bounded character length to bytes. `ucs2_strscpy()` rejects zero size or count overflow, copies up to `count` UCS-2 code units, returns copied characters when a terminator is found, or NUL-terminates the last destination slot and returns `-E2BIG` on truncation. `ucs2_strncmp()` performs lexicographic comparison up to `len` or NUL. UTF-8 helpers count or emit one-, two-, or three-byte sequences for BMP code units and NUL-terminate only if space remains.

## Dependencies and Integration
Depends on `linux/ucs2_string.h` and module exports. It is used by firmware/EFI and other subsystems that expose UCS-2 strings.

## Risks and Test Signals
Risks include no surrogate-pair handling because UCS-2 is not full UTF-16, caller confusion between byte and character counts, partial UTF-8 output without NUL when buffer is full, and undefined overlap behavior for `ucs2_strscpy()`. Test signals include boundary counts, truncation return values, maximum count overflow warning, lexicographic NUL handling, UTF-8 exact sizing, and conversion buffers ending one or two bytes before a multibyte character.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ucs2_string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/union_find.c -->
# sources/distributed-fs/ceph-client/lib/union_find.c

## Purpose
Disjoint-set union-find helpers implementing path compression and union by rank.

## APIs, Types, and Functions
Exports in-source functions `uf_find(struct uf_node *node)` and `uf_union(struct uf_node *node1, struct uf_node *node2)` as declared by `linux/union_find.h`.

## Control Flow, State, and Persistence
`uf_find()` follows parent pointers until a root whose parent is itself, compressing the path by making each visited node point to its grandparent. `uf_union()` finds both roots, returns if already equal, otherwise attaches the lower-rank root under the higher-rank root or increments rank when ranks are equal. Persistent state lives in caller-owned `struct uf_node` parent and rank fields.

## Dependencies and Integration
Depends on `linux/union_find.h`. It integrates with callers that initialize each node's parent to itself and maintain any required locking.

## Risks and Test Signals
Risks include no NULL checks, no internal synchronization, incorrect behavior if nodes are not initialized as singleton sets, and rank overflow only in extreme constructed cases. Test signals include singleton find, repeated union idempotence, rank tie behavior, path compression effects, and concurrent caller locking tests where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/union_find.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/usercopy.c -->
# sources/distributed-fs/ceph-client/lib/usercopy.c

## Purpose
Out-of-line usercopy wrappers and a userspace zero-check helper for generic uaccess infrastructure.

## APIs, Types, and Functions
Conditionally exports `_copy_from_user()` and `_copy_to_user()` when inline variants are not used, forwarding to `_inline_copy_from_user()` and `_inline_copy_to_user()`. Exports `check_zeroed_user(const void __user *from, size_t size)`.

## Control Flow, State, and Persistence
`check_zeroed_user()` treats zero size as zeroed, aligns the starting user pointer down to an `unsigned long` boundary, expands size by the alignment offset, and starts a user read access window. It reads word-sized chunks with `unsafe_get_user()`, masks leading bytes before the original pointer and trailing bytes after the requested size, exits early if a nonzero word appears, and closes user access before returning 1 for all zero, 0 for nonzero, or `-EFAULT` on access failure. No state is retained.

## Dependencies and Integration
Depends on uaccess primitives, nospec/instrumentation headers, wordpart byte masks, fault-injection usercopy headers, and symbol exports. It is used by syscall helpers such as `copy_struct_from_user()` and validated by `usercopy_kunit.c`.

## Risks and Test Signals
Risks include subtle alignment and tail-mask mistakes, user fault cleanup paths, architecture-specific user access window semantics, and pointer arithmetic on `__user` addresses. Test signals include zero-size return, unaligned starts, sizes shorter than a word, page-boundary reads, injected faults, and comparison against `memchr_inv()` on copied user data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/usercopy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/uuid.c -->
# sources/distributed-fs/ceph-client/lib/uuid.c

## Purpose
Unified UUID/GUID helpers for null constants, random version-4 generation, string validation, and parsing with UUID big-endian and GUID little-endian byte ordering.

## APIs, Types, and Functions
Exports `guid_null`, `uuid_null`, `generate_random_uuid()`, `generate_random_guid()`, `guid_gen()`, `uuid_gen()`, `uuid_is_valid()`, `guid_parse()`, and `uuid_parse()`. Internal `guid_index` and `uuid_index` tables define byte placement; `__uuid_gen_common()` sets the DCE variant; `__uuid_parse()` handles canonical string parsing.

## Control Flow, State, and Persistence
Generation fills 16 bytes from `get_random_bytes()`, sets variant bits in byte 8, and sets version bits at UUID byte 6 or GUID byte 7 according to storage order. Validation checks exactly `UUID_STRING_LEN` positions for hyphens at 8/13/18/23 and hex digits elsewhere. Parsing validates first, then uses source indexes for pairs of hex digits and destination endian indexes to populate the 16-byte object. Null constants are static exported zero objects.

## Dependencies and Integration
Depends on random bytes, hex conversion, ctype, errno, UUID type definitions, and symbol exports. It integrates with filesystem IDs, boot IDs, firmware GUIDs, and drivers parsing UUID strings.

## Risks and Test Signals
Risks include validation not checking for a trailing NUL beyond the fixed length, case-insensitive hex acceptance via `isxdigit()`/`hex_to_bin()`, byte-order confusion between GUID and UUID APIs, and random generation depending on RNG readiness semantics. Test signals include version/variant bit checks, GUID/UUID parse byte order, malformed strings, uppercase hex, trailing characters, and null constant equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/uuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/Kconfig -->
# sources/distributed-fs/ceph-client/lib/vdso/Kconfig

## Purpose
Kconfig options that gate the generic vDSO support library, generic gettimeofday implementation, optional overflow protection, and vDSO getrandom support.

## APIs, Types, and Functions
Defines `HAVE_GENERIC_VDSO`, `GENERIC_GETTIMEOFDAY`, `GENERIC_VDSO_OVERFLOW_PROTECT`, and `VDSO_GETRANDOM`. The latter three are visible only inside `if HAVE_GENERIC_VDSO`.

## Control Flow, State, and Persistence
This is declarative configuration. Architectures select `HAVE_GENERIC_VDSO` and then select the relevant feature bools. Help text documents that generic gettimeofday requires architecture fallback implementations, overflow protection adds a hot-path conditional, and getrandom is selected by supporting architectures.

## Dependencies and Integration
Integrates with architecture Kconfig files, `lib/vdso/Makefile`, generic vDSO time code, and random vDSO code. These symbols control compilation and code paths in `datastore.c`, `gettimeofday.c`, and `getrandom.c`.

## Risks and Test Signals
Risks include selecting generic gettimeofday without required arch fallback hooks, enabling overflow protection with measurable hot-path cost, or selecting getrandom without architecture support glue. Test signals are architecture allmodconfig/build coverage, vDSO ABI tests, syscall fallback tests, and config matrix builds for each bool combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/Makefile -->
# sources/distributed-fs/ceph-client/lib/vdso/Makefile

## Purpose
Build glue for the generic vDSO library directory.

## APIs, Types, and Functions
Adds `datastore.o` to `obj-y` when `CONFIG_HAVE_GENERIC_VDSO` is enabled.

## Control Flow, State, and Persistence
Declarative kbuild only. It does not build `gettimeofday.c` or `getrandom.c` directly here because those are included or built through architecture vDSO build rules.

## Dependencies and Integration
Depends on kbuild and `CONFIG_HAVE_GENERIC_VDSO`. Integrates with architecture-specific vDSO makefiles that pull generic sources as needed.

## Risks and Test Signals
Risks include assuming all generic vDSO files are built from this makefile, or missing `datastore.o` when an architecture selects generic vDSO. Test signals are per-architecture build logs and symbol presence for generic vvar datastore support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/datastore.c -->
# sources/distributed-fs/ceph-client/lib/vdso/datastore.c

## Purpose
Kernel-side storage and VVAR mapping support for generic vDSO data pages, including time data, RNG data, optional architecture data, dynamic page allocation, and page-fault mapping.

## APIs, Types, and Functions
Defines `vdso_k_time_data`, `vdso_k_rng_data`, and `vdso_k_arch_data` conditionally. Provides `vdso_setup_data_pages()`, `vvar_fault()`, `vdso_vvar_mapping`, and `vdso_install_vvar_mapping()`. Uses VDSO page offsets such as `VDSO_TIME_PAGE_OFFSET`, `VDSO_TIMENS_PAGE_OFFSET`, `VDSO_RNG_PAGE_OFFSET`, and architecture page ranges.

## Control Flow, State, and Persistence
Boot-time `vdso_initdata` holds initial page contents. `vdso_setup_data_pages()` allocates enough pages for `VDSO_NR_PAGES`, splits the allocation into individually refcounted pages, copies init data, and repoints exported kernel data pointers to the dynamic pages. `vvar_fault()` maps the requested VVAR page based on `vmf->pgoff`, handling time namespace special mapping by inserting the real time page at the namespace companion offset and returning the namespace page for the requested offset. Unsupported offsets or disabled features return `VM_FAULT_SIGBUS`. `vdso_install_vvar_mapping()` installs a sealed, read-only, IO, mixedmap special mapping.

## Dependencies and Integration
Depends on memory management, special mappings, time namespaces, `vdso/datapage.h`, and `linux/vdso_datastore.h`. It integrates with architecture vDSO setup and userspace VVAR fault handling.

## Risks and Test Signals
Risks include page-offset mismatches, time namespace double mapping mistakes, refcounting errors, panic on allocation failure, and assumptions about not using folios for namespace remapping. Test signals include VVAR fault tests for every offset, time namespace clock reads, mlockall behavior, unsupported config SIGBUS paths, and architecture data page ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/datastore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/getrandom.c -->
# sources/distributed-fs/ceph-client/lib/vdso/getrandom.c

## Purpose
Generic userspace vDSO implementation of `getrandom()`, using per-thread opaque state, ChaCha20 fast key erasure, kernel RNG generation tracking, and syscall fallback for unsupported or unsafe cases.

## APIs, Types, and Functions
Core implementation is `__cvdso_getrandom_data()`, wrapped by `__cvdso_getrandom()`. It uses `struct vdso_rng_data`, `struct vgetrandom_state`, `struct vgetrandom_opaque_params`, `getrandom_syscall()`, `__arch_get_vdso_u_rng_data()`, and `__arch_chacha20_blocks_nostack()`. Helper `memcpy_and_zero_src()` copies batch bytes while zeroing the source using unaligned access helpers.

## Control Flow, State, and Persistence
A special parameter query call (`buffer == NULL`, `len == 0`, `flags == 0`, `opaque_len == ~0UL`) fills mmap parameters and state size. Normal calls validate that the opaque state does not straddle a page, flags are known, opaque length matches, and the kernel RNG is ready. If validation fails, or the state is already `in_use`, it calls the syscall. On generation mismatch, it writes the current generation before reseeding to detect forks correctly, pairs with kernel release ordering via `smp_rmb()`, fetches a fresh key from the syscall, and invalidates state on failure. It serves bytes from a cached batch, zeroing consumed bytes, generates full ChaCha blocks directly into the buffer, then refills a combined batch/key region to preserve forward secrecy. Before returning, it rereads state and kernel generations to detect fork/reseed/zeroed droppable memory; it retries once then falls back.

## Dependencies and Integration
Depends on vDSO datapage definitions, random uapi flags, memory mapping flags including `MAP_DROPPABLE`, architecture ChaCha and syscall hooks, barriers, page size config, and unaligned access helpers. It integrates into architecture vDSO symbol wrappers.

## Risks and Test Signals
Risks include per-state concurrency misuse across threads, signal reentrancy limitations, page-straddling state faults, generation ordering bugs, low-memory zeroing of droppable state, unsupported flags, and exact syscall fallback compatibility before RNG readiness. Test signals include parameter query ABI, flag matrix, zero-length behavior before and after readiness, fork detection, signal handler reentrancy, state page-boundary rejection, generation reseed races, and byte-for-byte length returns capped by `MAX_RW_COUNT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/getrandom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/gettimeofday.c -->
# sources/distributed-fs/ceph-client/lib/vdso/gettimeofday.c

## Purpose
Generic userspace vDSO implementations for `clock_gettime()`, `gettimeofday()`, optional `time()`, and optional `clock_getres()`, with high-resolution, coarse, raw, auxiliary clock, and time namespace support.

## APIs, Types, and Functions
Provides inline helpers and exported-by-inclusion functions such as `__cvdso_clock_gettime_data()`, `__cvdso_clock_gettime()`, `__cvdso_gettimeofday_data()`, `__cvdso_gettimeofday()`, optional `__cvdso_time_data()`, optional `__cvdso_clock_getres_data()`, and 32-bit variants under `BUILD_VDSO32`. Important helpers include `vdso_calc_ns()`, `vdso_delta_ok()`, `vdso_get_timestamp()`, `do_hres()`, `do_hres_timens()`, `do_coarse()`, `do_coarse_timens()`, `do_aux()`, and `vdso_set_timespec()`.

## Control Flow, State, and Persistence
The code reads architecture time data via `__arch_get_vdso_u_time_data()`, validates clock IDs, selects a clocksource data slot by bitmask (`VDSO_HRES`, `VDSO_COARSE`, `VDSO_RAW`, `VDSO_AUX`), and attempts a lockless sequence-count read. High-resolution paths read hardware cycles, validate clocksource/cycles, compute nanoseconds from cycle deltas, and normalize seconds/nanoseconds outside the seqcount loop. Coarse paths copy stored basetime directly. Time namespace paths detect namespace sequence state, switch to the real VVAR page at `PAGE_SIZE`, and add namespace offsets. Fallback syscalls are used when a clock is invalid, unsupported, disabled, or the architecture cannot provide a valid counter. `gettimeofday()` also copies timezone fields, and `clock_getres()` returns hrtimer, low-res, or auxiliary clock resolution.

## Dependencies and Integration
Depends on architecture-provided `asm/vdso/gettimeofday.h` hooks, vDSO datapage structures, clocksource modes, seqcount helpers, time namespace layout, auxiliary clock support, math64 helpers, and syscall fallback functions. It is included by architecture vDSO builds rather than built as a normal kernel object.

## Risks and Test Signals
Risks include seqcount loop placement around expensive normalization, overflow in cycle-to-ns math without optional protection, time namespace page offset assumptions, invalid clock bit shifts if clock validation changes, timezone indexing oddities, and architecture-specific counter validity. Test signals include vDSO versus syscall comparisons for realtime/monotonic/raw/coarse clocks, time namespace offset tests, 32-bit time ABI tests, clock_getres null/non-null output, auxiliary clock disabled paths, overflow-protection configs, and forced fallback modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/gettimeofday.c -->
