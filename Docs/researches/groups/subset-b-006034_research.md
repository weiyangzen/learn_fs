# Research Group: subset-b-006034

Grouped research for the listed kernel sources under `sources/distributed-fs/ceph-client/kernel`. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/kernel/jump_label.c

## Purpose
Implements Linux jump-label/static-key runtime support: it sorts generated `__jump_table` entries, binds entries to `struct static_key`, patches branch/NOP sites through architecture hooks, and tracks module-provided jump-label sites. The file is performance critical because static branches are used across hot paths to turn feature checks into patched instructions.

## Important APIs, Types, and Functions
Exports `static_key_count`, `static_key_slow_inc`, `static_key_slow_dec`, `static_key_enable`, `static_key_disable`, deferred decrement helpers, `jump_label_rate_limit`, and `jump_label_text_reserved`. Initialization is in `jump_label_init`, `jump_label_init_ro`, and the module notifier registered by `jump_label_init_module`. Internally, `jump_label_cmp`, `jump_label_sort_entries`, `static_key_set_entries`, `jump_label_type`, `jump_label_can_update`, and `__jump_label_update` are the key mechanics. With modules enabled, `struct static_key_mod` links a key to jump entries in built-in and module tables.

## Control Flow
Boot initialization sorts `__start___jump_table` to `__stop___jump_table`, rewrites default NOPs, marks init-text entries, and stores each key's first entry pointer. Runtime enable paths transition `key->enabled` from 0 to -1 while patching and publish 1 with release ordering; disable/decrement paths only patch when the count reaches 0. `jump_label_update` resolves whether a key points directly at entries, is linked to module lists, or belongs to a module, then calls `__jump_label_update` to invoke `arch_jump_label_transform` or queued batch patching.

## State and Persistence
State is in each `static_key` (`enabled`, entry pointer/type bits, linked-list tag), in static module-list nodes allocated at module load, and in global `static_key_initialized`. `jump_label_mutex` and CPU read locks serialize table mutation and text patching against CPU/module hotplug. No disk persistence exists; state is reconstructed at boot and maintained across module load/unload.

## Dependencies and Integration Points
Depends on generated jump-table sections, architecture jump-label transform hooks, module notifier ordering, init section helpers, `kernel_text_address`, CPU hotplug locking, and static-key APIs from `linux/static_key.h`. Text patching clients use `jump_label_text_reserved` to avoid overwriting patch sites.

## Risks
Incorrect reference count transitions can patch live text in the wrong direction. Module add/remove must fold linked keys back to direct entries without leaving stale `static_key_mod` nodes. The relative-entry swap function must preserve self-relative offsets during sort. `jump_label_can_update` deliberately skips init/exit text outside legal patch windows; mistakes here can patch freed or non-text memory.

## Test Signals
`CONFIG_STATIC_KEYS_SELFTEST` runs `jump_label_test` as an early initcall, toggling true/false static branches and checking `static_key_enabled` and branch helpers. Runtime warnings cover underflow, concurrent enable/decrement ordering, missing module-list nodes, bad text addresses, and failed allocations during module notifier handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kallsyms.c -->
# sources/distributed-fs/ceph-client/kernel/kallsyms.c

## Purpose
Provides in-kernel symbol lookup, symbol formatting for stack traces/oopses, `/proc/kallsyms`, and BPF iterator exposure. It decodes the generated compressed kallsyms tables and combines vmlinux, module, ftrace, BPF, and kprobe symbol sources.

## Important APIs, Types, and Functions
Core lookup APIs are `kallsyms_lookup_name`, `kallsyms_on_each_symbol`, `kallsyms_on_each_match_symbol`, `kallsyms_lookup_size_offset`, `kallsyms_lookup`, `lookup_symbol_name`, and sprint helpers (`sprint_symbol`, `sprint_symbol_build_id`, `sprint_symbol_no_offset`, `sprint_backtrace`, `sprint_backtrace_build_id`). `struct kallsym_iter` drives `/proc/kallsyms` and BPF iteration. Compression helpers include `kallsyms_expand_symbol`, `kallsyms_get_symbol_type`, `get_symbol_offset`, `kallsyms_sym_address`, and `kallsyms_lookup_names`.

## Control Flow
Name lookup binary-searches `kallsyms_seqs_of_names`, expands candidate names from `kallsyms_names`, then scans adjacent duplicates. Address lookup binary-searches sorted addresses, backs up to the first alias, calculates symbol end from the next non-aliased symbol or section boundaries, and then expands the symbol name. `/proc/kallsyms` uses seq-file callbacks to walk core symbols first, then modules, ftrace module pages, BPF symbols, and kprobe symbols.

## State and Persistence
The main state is generated read-only arrays declared in `kallsyms_internal.h`: offsets, compressed names, token tables, markers, and name-order sequences. Iterator instances keep transient position and section-end caches. The proc entry is created at `device_initcall`.

## Dependencies and Integration Points
Integrates with modules, BPF JIT symbol lookup and BPF iterators, ftrace, kprobes, `/proc`, seq_file, KDB, build IDs, and address visibility policy through `kallsyms_show_value`. Many other kernel diagnostics rely on the sprint and lookup APIs.

## Risks
Compressed-name decoding and marker seeking must remain synchronized with `scripts/kallsyms.c` output. Symbol value visibility must not leak addresses when policy hides them. Iteration may reschedule, so module and name lifetime guarantees rely on RCU or caller discipline. Duplicate symbol names and aliases require careful ordering.

## Test Signals
`kallsyms_selftest.c` exercises lookup correctness, duplicate handling, compression ratio, and lookup performance. Runtime failures appear as missing `/proc/kallsyms` entries, incorrect stack traces, unresolved module/BPF symbols, or warnings around missing module build IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kallsyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kallsyms_internal.h -->
# sources/distributed-fs/ceph-client/kernel/kallsyms_internal.h

## Purpose
Declares the generated kallsyms data arrays consumed by `kallsyms.c` and selftests. It is a private contract between the build-time kallsyms generator and kernel lookup code.

## Important APIs, Types, and Functions
The header exports no functions. It declares `kallsyms_offsets`, `kallsyms_names`, `kallsyms_num_syms`, `kallsyms_token_table`, `kallsyms_token_index`, `kallsyms_markers`, and `kallsyms_seqs_of_names`.

## Control Flow
No runtime control flow exists in the header. Consumers use `kallsyms_markers` to jump into compressed names, `kallsyms_token_*` to expand names, `kallsyms_offsets` to compute addresses, and `kallsyms_seqs_of_names` for name-sorted binary search.

## State and Persistence
State is generated at build time and linked into the kernel image as constant data. It persists only for the lifetime of the running kernel.

## Dependencies and Integration Points
Depends on `linux/types.h` and on generated symbols emitted by the build system. `kallsyms.c` and `kallsyms_selftest.c` must agree on array encoding.

## Risks
Any generator/layout mismatch corrupts symbol lookup globally. The arrays have implicit size and encoding relationships not captured by C types, so changes must be coordinated with kallsyms generation scripts.

## Test Signals
The kallsyms selftest indirectly validates this header by traversing all symbols, calculating compression ratios, and matching lookups against expected addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kallsyms_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kallsyms_selftest.c -->
# sources/distributed-fs/ceph-client/kernel/kallsyms_selftest.c

## Purpose
Implements boot-time functional and performance tests for kallsyms lookup and traversal. It validates exact lookup of known function/data symbols, duplicate-name traversal, address-to-name consistency, compression ratio, and relative performance of lookup APIs.

## Important APIs, Types, and Functions
Defines test symbols and variables (`kallsyms_test_func*`, `kallsyms_test_var*`) and uses `struct test_stat` plus `struct test_item`. Main routines are `test_kallsyms_basic_function`, `test_kallsyms_compression_ratio`, `test_perf_kallsyms_lookup_name`, `test_perf_kallsyms_on_each_symbol`, `test_perf_kallsyms_on_each_match_symbol`, and `kallsyms_test_init`.

## Control Flow
`late_initcall(kallsyms_test_init)` starts a CPU-pinned kthread. The thread waits until `SYSTEM_RUNNING`, runs correctness tests first, aborts on failure, then prints compression/performance statistics. Correctness tests compare direct lookup results for fixed symbols, scan all symbols, randomly sample full traversal, and verify `kallsyms_on_each_match_symbol` matches `kallsyms_on_each_symbol`.

## State and Persistence
Temporary state is allocated with `kmalloc_objs`, and fixed test symbols are linked into the kernel image. Results are emitted to the kernel log; no persistent state is stored.

## Dependencies and Integration Points
Depends on `kallsyms.c` public APIs, generated kallsyms internals, random bytes, scheduler clock, kthreads, and exported test declarations in `kallsyms_selftest.h`.

## Risks
Tests are timing-sensitive for performance output but correctness failures should be deterministic. Random sampling reduces cost but may not cover every full traversal path every boot. Data-symbol checks only run with `CONFIG_KALLSYMS_ALL`.

## Test Signals
Kernel log lines include `start`, `abort`, compression table output, per-symbol timing, traversal timing, and `finish`. Failures log symbol name, expected address, observed address/count, or traversal mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kallsyms_selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kallsyms_selftest.h -->
# sources/distributed-fs/ceph-client/kernel/kallsyms_selftest.h

## Purpose
Provides external declarations for kallsyms selftest symbols so generated kallsyms and test code can reference stable function/data names.

## Important APIs, Types, and Functions
Declares `kallsyms_test_var_bss`, `kallsyms_test_var_data`, `kallsyms_test_func`, and `kallsyms_test_func_weak`.

## Control Flow
No control flow; it is a declaration-only header.

## State and Persistence
The declared variables/functions are defined in `kallsyms_selftest.c` and linked into the kernel when the selftest is enabled.

## Dependencies and Integration Points
Includes `linux/types.h` and is consumed by `kallsyms_selftest.c`.

## Risks
If declarations diverge from definitions, selftest build or lookup validation breaks. Weak function semantics are part of the tested symbol set.

## Test Signals
Build success and selftest address comparisons validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kallsyms_selftest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcmp.c -->
# sources/distributed-fs/ceph-client/kernel/kcmp.c

## Purpose
Implements the `kcmp` syscall, allowing authorized userspace to compare whether two tasks share kernel resources such as files, VM, fs, sighand, IO context, SysV semaphore undo lists, or epoll targets.

## Important APIs, Types, and Functions
Main entry is `SYSCALL_DEFINE5(kcmp)`. Helpers are `kptr_obfuscate`, `kcmp_ptr`, `get_file_raw_ptr`, `kcmp_lock`, `kcmp_unlock`, optional `kcmp_epoll_target`, and `kcmp_cookies_init`. `cookies[KCMP_TYPES][2]` obfuscates pointer ordering.

## Control Flow
The syscall finds both tasks in the caller's PID namespace under RCU, pins them, takes their `exec_update_lock` semaphores in address order, checks `ptrace_may_access`, then dispatches by `type`. File comparisons acquire file references transiently; epoll mode copies a userspace slot and compares the target file stored in an epoll instance.

## State and Persistence
Only boot-initialized random cookies persist. Comparisons return equality/order over obfuscated pointer values; real pointers are never exposed. No per-call state persists after task refs and locks are released.

## Dependencies and Integration Points
Integrates with ptrace permissions, PID namespaces, file tables, epoll, task signal locks, SysV IPC when enabled, and `arch_initcall` random cookie setup.

## Risks
Permission checks are central because resource sharing is sensitive. Lock ordering must prevent deadlocks when comparing a task with itself or another task. `get_file_raw_ptr` intentionally returns a raw pointer after dropping a ref for comparison only; callers must not dereference it later.

## Test Signals
Expected syscall errors include `-ESRCH`, `-EPERM`, `-EBADF`, `-EINVAL`, and `-EOPNOTSUPP`. KCMP behavior is typically validated by userspace tests that compare known shared and non-shared resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcov.c -->
# sources/distributed-fs/ceph-client/kernel/kcov.c

## Purpose
Implements KCOV coverage collection for fuzzing through a debugfs device. It records instrumented PCs or comparison operands for the current task, and supports remote coverage sections for background threads and softirqs.

## Important APIs, Types, and Functions
`struct kcov` tracks device state, buffer, owner task, remote mode, refcount, and sequence. Remote state uses `struct kcov_remote`, `struct kcov_remote_area`, and per-CPU `struct kcov_percpu_data`. Instrumentation entry points include `__sanitizer_cov_trace_pc`, comparison callbacks, and switch tracing. User API is through `kcov_open`, `kcov_mmap`, `kcov_ioctl`, `kcov_close`; remote kernel API exports `kcov_remote_start`, `kcov_remote_stop`, and `kcov_common_handle`.

## Control Flow
Users open `/sys/kernel/debug/kcov`, call `KCOV_INIT_TRACE`, mmap the buffer, then enable PC or CMP mode. Instrumented callbacks check task mode and append records into the shared buffer. Disable resets task state and drops the active reference. Remote enable registers handles in a hash table; `kcov_remote_start` looks up a handle, installs a temporary per-task/per-CPU coverage area, and `kcov_remote_stop` merges records into the owning buffer if the sequence still matches.

## State and Persistence
State persists while the debugfs fd, enabled task, or remote section holds a refcount. Coverage buffers are vmalloc-backed and user-mapped. Remote area caches are kept in a global list, and per-CPU IRQ areas are allocated at init. No data survives close or reboot.

## Dependencies and Integration Points
Depends on compiler sanitizer coverage hooks, debugfs, vmalloc mmap insertion, task_struct KCOV fields, KMSAN unpoisoning, local locks, softirq context checks, and subsystem handle definitions from `linux/kcov.h`.

## Risks
Mode transitions must prevent multiple tasks from using one kcov object. Ordering barriers protect callback readers from partially installed task state. Remote start cannot take `kcov->lock` under `kcov_remote_lock`, so sequence checks defend against disable races. Buffer count updates need write barriers before userspace observes new records.

## Test Signals
`CONFIG_KCOV_SELFTEST` checks interrupt filtering by enabling tracing without a buffer and waiting for timer interrupts. Runtime validation is mostly userspace fuzzing tests exercising debugfs ioctls, mmap sizing, remote handles, and record formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/Makefile -->
# sources/distributed-fs/ceph-client/kernel/kcsan/Makefile

## Purpose
Builds the KCSAN runtime, debugfs interface, reporting code, boot selftest, and optional KUnit suite with the instrumentation exclusions required for sanitizer runtime code.

## Important APIs, Types, and Functions
This is Kbuild metadata rather than C API. It sets `KCSAN_SANITIZE := n`, `KCOV_INSTRUMENT := n`, `UBSAN_SANITIZE := n`, removes ftrace flags from runtime objects, sets special `CFLAGS_core.o`, builds `core.o debugfs.o report.o`, and conditionally builds `selftest.o` and `kcsan_test.o`.

## Control Flow
Kbuild uses the file to prevent recursive sanitizer/ftrace instrumentation of the sanitizer runtime. `KCSAN_INSTRUMENT_BARRIERS_selftest.o := y` forces barrier instrumentation in boot selftests, while `CFLAGS_kcsan_test.o := $(CFLAGS_KCSAN)` intentionally instruments the KUnit tests.

## State and Persistence
No runtime state. Build-time flags determine which objects exist and how they are instrumented.

## Dependencies and Integration Points
Integrates with Kbuild sanitizer variables, ftrace flags, structleak plugin disabling, and `CONFIG_KCSAN_SELFTEST` / `CONFIG_KCSAN_KUNIT_TEST`.

## Risks
Accidentally instrumenting runtime objects can recurse into KCSAN from KCSAN itself. Removing required instrumentation from tests would make selftests meaningless. Architecture-specific atomics require `-mno-outline-atomics` when supported.

## Test Signals
Build output and enabled config options determine whether boot selftests and KUnit tests are available. Recursive instrumentation failures usually appear as early boot crashes or noisy sanitizer recursion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/core.c -->
# sources/distributed-fs/ceph-client/kernel/kcsan/core.c

## Purpose
Implements the KCSAN runtime: probabilistic watchpoint setup, conflict detection, value-change inference, scoped/weak-memory checks, and TSAN-compatible compiler instrumentation callbacks.

## Important APIs, Types, and Functions
Global knobs include `kcsan_enabled`, `kcsan_udelay_task`, `kcsan_udelay_interrupt`, skip/watch parameters, and weak-memory mode. Core mechanics are `find_watchpoint`, `insert_watchpoint`, `try_consume_watchpoint`, `check_access`, `kcsan_found_watchpoint`, and `kcsan_setup_watchpoint`. Exported APIs include enable/disable, atomic-region helpers, access masks, scoped accesses, `__kcsan_check_access`, barrier hooks, TSAN read/write/range/volatile/atomic callbacks, function entry/exit, and instrumented memset/memmove/memcpy wrappers.

## Control Flow
Every instrumented access calls `check_access`. The fast path first scans matching encoded watchpoints; if one is found, it attempts to consume it and publish report info. If none is found, a per-CPU skip counter decides whether to set a new watchpoint. Setup encodes the access, inserts it into adjacent slots, samples the old value, delays, samples the new value, consumes/removes the watchpoint, and reports known-origin or unknown-origin races depending on whether another access consumed it.

## State and Persistence
KCSAN state lives in global atomic `watchpoints`, per-CPU skip and random state, per-task/per-CPU `kcsan_ctx`, module parameters, and counters defined in debugfs. State is runtime-only and reset on boot. Scoped access lists are lazily initialized per context.

## Dependencies and Integration Points
Uses `encoding.h` for watchpoint encoding, `report.c` for diagnostics, `permissive.h` for ignore rules, task context fields, user access save/restore, lockdep/IRQ trace preservation, compiler TSAN ABI, and kernel barrier instrumentation.

## Risks
This is extremely hot code; extra branches or dereferences impact the whole kernel under KCSAN. Watchpoint encoding can produce false positives that report code must filter. IRQ and scoped-access interactions share contexts and require careful disabling. Value-change inference can miss races or report unknown-origin races depending on config. Unbalanced KCSAN disable/atomic helpers intentionally warn.

## Test Signals
Boot selftest validates encoding and barrier instrumentation. KUnit tests exercise race reports, atomics, scoped assertions, weak-memory barriers, permissive mode, `data_race`, `__data_racy`, and zero-size access behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/debugfs.c -->
# sources/distributed-fs/ceph-client/kernel/kcsan/debugfs.c

## Purpose
Provides `/sys/kernel/debug/kcsan` for enabling/disabling KCSAN, displaying counters, maintaining report filter lists, and running a microbenchmark of runtime overhead.

## Important APIs, Types, and Functions
Defines `kcsan_counters` and counter names. Filter state is `report_filterlist`, protected by `report_filterlist_lock`. Main functions are `kcsan_skip_report_debugfs`, `insert_report_filterlist`, `set_report_filterlist_whitelist`, `show_info`, `debugfs_write`, `microbenchmark`, and `kcsan_debugfs_init`.

## Control Flow
Reads print enabled state, counters, filter type, and function list. Writes accept `on`, `off`, `microbench=<iters>`, `whitelist`, `blacklist`, or `!function_name`. Filter insertion resolves a function through kallsyms, grows the address array outside the raw spinlock, then appends under lock. Report filtering sorts lazily and uses bsearch on function starts.

## State and Persistence
Counters are atomic longs kept for the current boot. Filterlist memory persists until reboot and is not exposed as durable configuration. `kcsan_enabled` is toggled live with `WRITE_ONCE`.

## Dependencies and Integration Points
Depends on debugfs, seq_file, kallsyms, sort/bsearch, KCSAN core/reporting APIs, and raw spinlocks usable from report paths.

## Risks
Report filtering runs from diagnostic paths and must not allocate under raw locks. Duplicate entries are not deduplicated in kernel. Microbenchmark temporarily disables KCSAN globally and rewrites the current context, so it is a diagnostic tool rather than production state.

## Test Signals
Manual debugfs reads/writes validate command parsing. KCSAN reports should disappear or appear according to whitelist/blacklist mode. Counter changes provide runtime evidence of watchpoints, races, capacity pressure, and encoding false positives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/encoding.h -->
# sources/distributed-fs/ceph-client/kernel/kcsan/encoding.h

## Purpose
Defines how KCSAN encodes a watched access into one atomic long and maps addresses to watchpoint slots.

## Important APIs, Types, and Functions
Key constants are `SLOT_RANGE`, `INVALID_WATCHPOINT`, `CONSUMED_WATCHPOINT`, `MAX_ENCODABLE_SIZE`, address/size/write bit masks, and `WATCHPOINT_ADDR_BITS`. Inline helpers are `check_encodable`, `encode_watchpoint`, `decode_watchpoint`, `watchpoint_slot`, and `matching_access`.

## Control Flow
`core.c` calls `check_encodable` before installing a watchpoint, stores the encoded address/size/write bit with `encode_watchpoint`, later decodes candidate slots, and uses `matching_access` to check overlap. `report.c` also uses `matching_access` to reject encoding false positives.

## State and Persistence
No state is stored in the header. It defines the bit layout used by atomic watchpoint slots in `core.c`.

## Dependencies and Integration Points
Depends on page size, bit helpers, log2 helpers, and `NUM_SLOTS` from `kcsan.h`. The layout assumes enough unused virtual-address bits on common architectures and deliberately masks high address bits.

## Risks
Encoding truncates addresses, so two different addresses can map to the same encoded address and slot. The reporting path must filter actual address mismatches. `MAX_ENCODABLE_SIZE` bounds what KCSAN can watch precisely.

## Test Signals
`kcsan/selftest.c` repeatedly randomizes addresses, sizes, and write bits to ensure encode/decode round-trips and that invalid/consumed sentinels are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/encoding.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/kcsan.h -->
# sources/distributed-fs/ceph-client/kernel/kcsan/kcsan.h

## Purpose
Private KCSAN runtime header shared by core, debugfs, reporting, and tests. It centralizes runtime constants, counters, global knobs, and reporting interfaces.

## Important APIs, Types, and Functions
Defines `KCSAN_CHECK_ADJACENT`, `NUM_SLOTS`, `enum kcsan_counter_id`, and `enum kcsan_value_change`. Declares `kcsan_enabled`, delay knobs, `kcsan_counters`, IRQ trace helpers, debugfs report filter hook, and report producer/consumer functions.

## Control Flow
No direct control flow. It describes the communication contract: core records counters and calls report APIs; report code consults debugfs filters and value-change states; debugfs displays counters and can suppress reports.

## State and Persistence
Declares global state owned elsewhere. Counters and enable state persist for the boot only.

## Dependencies and Integration Points
Depends on `linux/kcsan.h` public definitions and task structures. It binds together `core.c`, `debugfs.c`, `report.c`, `encoding.h`, and tests.

## Risks
Counter or enum reordering must stay synchronized with `debugfs.c` names. Value-change semantics are used by report filtering and cannot be changed casually without altering user-visible report behavior.

## Test Signals
Debugfs counter output and KUnit report expectations validate the enum/API contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/kcsan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/kcsan_test.c -->
# sources/distributed-fs/ceph-client/kernel/kcsan/kcsan_test.c

## Purpose
KUnit suite for KCSAN runtime behavior. It creates controlled races, captures KCSAN console reports, and verifies expected reports or non-reports across normal races, atomics, scoped assertions, weak-memory barriers, permissive filtering, and compiler atomic builtins.

## Important APIs, Types, and Functions
Uses `struct expect_report`, `begin_test_checks`, `end_test_checks`, `probe_console`, `report_matches`, many `test_kernel_*` access kernels, parameter generator `nthreads_gen_params`, torture worker `access_thread`, and KUnit lifecycle hooks `test_init`, `test_exit`, `kcsan_suite_init`, `kcsan_suite_exit`.

## Control Flow
Suite init registers the console tracepoint. Each threaded test starts torture kthreads and timers that repeatedly run two access kernels. The test body sets `access_kernels`, loops until a timeout or expected report, and matches captured report title/access lines against expected function, address, size, and access type. Exit stops workers and clears access kernels.

## State and Persistence
Static test variables (`test_var`, `test_array`, `test_struct`, locks, seqlock) provide race targets. `observed` stores the current captured report under spinlock. Worker thread arrays and test end time exist per test run only.

## Dependencies and Integration Points
Depends on KUnit, torture kthreads, timers, console tracepoint, KCSAN public checks/assertions, lock primitives, seqlocks, jiffies, and compiler TSAN/KCSAN instrumentation.

## Risks
Tests are timing and configuration dependent; many expectations branch on config options such as weak memory, value-change-only, permissive mode, ignored atomics, and compiler compound-read support. Console parsing is intentionally narrow and could break if report formatting changes.

## Test Signals
The suite registers as `kcsan`. Cases cover basic data races, concurrent races, no-value-change filtering, unknown-origin races, write-write assumptions, atomic/plain races, zero-size accesses, `data_race`, `__data_racy`, exclusive assertions, jiffies/seqlock non-reports, atomic builtins, one-bit permissive filtering, and missing/correct barriers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/kcsan_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/permissive.h -->
# sources/distributed-fs/ceph-client/kernel/kcsan/permissive.h

## Purpose
Contains optional permissive-mode rules that suppress selected noisy KCSAN reports without embedding those policy decisions in the core runtime.

## Important APIs, Types, and Functions
Defines `kcsan_ignore_address` and `kcsan_ignore_data_race`.

## Control Flow
If `CONFIG_KCSAN_PERMISSIVE` is disabled, helpers return false. If enabled, `kcsan_ignore_address` suppresses races on `current->flags`. `kcsan_ignore_data_race` suppresses plain read races on word-sized or smaller values when the observed change affects only one bit, except boolean-looking 0/1 changes.

## State and Persistence
No state; all decisions are derived from access parameters and config.

## Dependencies and Integration Points
Called from `core.c` during found-watchpoint and setup/value-change paths. Uses bit counting, current task state, and KCSAN access type flags.

## Risks
This intentionally creates false negatives to reduce noise. The comments emphasize that ignored races are not generally safe, and future bug patterns may be hidden by broad rules.

## Test Signals
`kcsan_test.c` includes a one-bit value-change test that expects no report only when permissive mode is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/permissive.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/report.c -->
# sources/distributed-fs/ceph-client/kernel/kcsan/report.c

## Purpose
Builds and prints KCSAN race reports. It coordinates the thread that consumes a watchpoint with the thread that originally installed it, filters and rate-limits reports, formats stack traces/access descriptions, and handles unknown-origin races.

## Important APIs, Types, and Functions
Uses `struct access_info`, `struct other_info`, `struct report_time`, global `other_infos`, `report_times`, and `report_lock`. Main helpers are `rate_limit_report`, `skip_report`, `get_access_type`, `sanitize_stack_entries`, `print_report`, `prepare_report_producer`, `prepare_report_consumer`, and exported `kcsan_report_set_info`, `kcsan_report_known_origin`, `kcsan_report_unknown_origin`.

## Control Flow
The racing access that consumes a watchpoint calls `kcsan_report_set_info`, fills the per-watchpoint `other_info`, and optionally stalls for verbose task data. The original watchpoint owner calls `kcsan_report_known_origin`, waits for that info, verifies encoded and real address overlap, filters by value-change/config/debugfs/rate limit, prints the report, and releases the slot. Unknown-origin reporting bypasses `other_info` and prints a single-sided report.

## State and Persistence
Per-watchpoint `other_infos` are reused and marked valid by nonzero size. `report_times` stores recent report frame pairs for boot-time rate limiting. No reports are persisted beyond the kernel log.

## Dependencies and Integration Points
Depends on stacktrace, kallsyms for frame/function lookup, debugfs filters, lockdep/IRQ trace helpers, printk, panic-on-warn, and watchpoint matching from `encoding.h`.

## Risks
Report generation runs in sensitive contexts, so it disables KCSAN and lockdep around printk paths. Producer/consumer waiting must avoid deadlocks while still keeping task data valid. Formatting is consumed by tests and users, so wording changes can break expectations.

## Test Signals
KUnit captures console output and matches report title plus access lines. Counters in debugfs track data races, assert failures, report races, unknown-origin races, and encoding false positives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/report.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/selftest.c -->
# sources/distributed-fs/ceph-client/kernel/kcsan/selftest.c

## Purpose
Boot-time KCSAN sanity tests for watchpoint encoding, access overlap logic, and memory barrier instrumentation.

## Important APIs, Types, and Functions
Tests are `test_encode_decode`, `test_matching_access`, `test_barrier`, and `kcsan_selftest`. Barrier checks are generated by `KCSAN_CHECK_READ_BARRIER`, `KCSAN_CHECK_WRITE_BARRIER`, and `KCSAN_CHECK_RW_BARRIER`.

## Control Flow
`postcore_initcall(kcsan_selftest)` runs three tests. Encoding tests random address/size/write combinations and validate decode results plus sentinel rejection. Matching tests check overlapping and non-overlapping ranges. Barrier tests, when weak memory and SMP are enabled, seed `current->kcsan_ctx.reorder_access`, execute many kernel barriers/atomics/unlocks, and verify the scoped access is cleared as expected.

## State and Persistence
Uses current task KCSAN context, a local spinlock, dummy atomics, and stack locals. It logs pass counts and panics if any test fails.

## Dependencies and Integration Points
Depends on `encoding.h`, KCSAN barrier instrumentation, random helpers, spinlocks, atomics, bitops, and postcore init ordering.

## Risks
Barrier expectations must track architecture and instrumentation semantics. The tests intentionally run early and panic on failure, so false failures block boot in selftest builds.

## Test Signals
Logs `selftest: passed/total tests passed`; individual failures use WARN/pr_err with details, and final failure calls `panic("selftests failed")`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kcsan/selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kexec.c -->
# sources/distributed-fs/ceph-client/kernel/kexec.c

## Purpose
Implements the legacy `kexec_load` syscall path. It loads a replacement kernel image or crash kernel from userspace segments, prepares architecture-specific state, installs it as the active kexec image, or unloads an existing image.

## Important APIs, Types, and Functions
Main functions are `kimage_alloc_init`, `do_kexec_load`, `kexec_load_check`, `SYSCALL_DEFINE4(kexec_load)`, and the compat syscall. It manipulates global `kexec_image` and `kexec_crash_image`, calls `machine_kexec_prepare`, `machine_kexec_post_load`, `kimage_load_segment`, `kimage_terminate`, and crash-memory helpers.

## Control Flow
Syscall entry checks permissions, LSM/IMA/lockdown policy, flag validity, segment count, and architecture bits. It copies userspace segment descriptors, serializes with `kexec_trylock`, handles unload when `nr_segments == 0`, frees any old crash image if needed, allocates and validates a `kimage`, allocates control/swap pages, prepares the machine, copies vmcoreinfo, loads segments, terminates the image, runs post-load hooks, and atomically exchanges the installed image pointer.

## State and Persistence
Loaded images persist in memory through global pointers until replaced, unloaded, executed, or freed. Crash kernels may occupy protected reserved crash memory. No disk state is written; userspace must handle filesystem sync/unmount before rebooting into kexec.

## Dependencies and Integration Points
Depends on capabilities, `kexec_load_permitted`, LSM `security_kernel_load_data`, lockdown, usercopy helpers, crash dump/hotplug support, architecture kexec hooks, vmcoreinfo, and internal kimage allocation/loading routines.

## Risks
This is a high-impact syscall: it can replace the running kernel. Segment validation, architecture matching, crash reserved-memory bounds, and lockdown checks must be correct. Error paths must free partially allocated control pages/images and re-protect crash memory when needed.

## Test Signals
Expected errors include `-EPERM`, `-EINVAL`, `-ENOMEM`, `-EBUSY`, `-EADDRNOTAVAIL`, and architecture hook failures. Functional validation comes from kexec/kdump tests that load, unload, crash-load, and boot into prepared images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/kexec.c -->
