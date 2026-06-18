# subset-b-008980 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/extern.h -->
## sources/storage-engines/wiredtiger/src/include/extern.h

Purpose: this is WiredTiger's generated internal prototype registry. It is marked as built by `prototypes.py` and gathers declarations for the engine-wide `__wt_*`, `__wti_*`, inline, and unit-test-only entry points so compilation units can share one consistent internal ABI. It is not business logic by itself, but it is a high-value integration map for the storage engine: transaction visibility, block management, cache accounting, schema, cursor, metadata, tiered/disaggregated storage, rollback-to-stable, logging, diagnostics, and OS/file helpers all surface here.

Important APIs/types/functions: the largest families are `__wt_txn_*` and `__wti_txn_*` for begin/commit/rollback/prepare, timestamps, snapshots, pinned timestamp maintenance, prepared discovery, transaction log integration, and visibility checks; `__wt_block_*`, `__wti_block_*`, `__wt_bm_*`, `__wt_blkcache_*`, and `__wti_blkcache_*` for block addresses, checkpoints, compaction, salvage, verification, allocation/free lists, object/block cache, and disaggregated block manager operations; `__wt_cache_*` inline accessors and mutators for cache bytes, dirty bytes, image bytes, page counts, and memory footprint; `__wt_page_*`, `__wti_page_*`, `__wt_ref_*`, `__wt_cell_*`, and `__wt_row_*` for page instantiation, eviction, cell packing/unpacking, row keys/values, and tree walking; `__wt_cursor_*`, `__wti_cursor_*`, `__wt_btcur_*`, and specialized cursor openers for file/table/index/stat/history-store/backup/config/metadata cursors; `__wt_schema_*` and `__wti_schema_*` for tables, column groups, indexes, tiered handles, create/alter/drop/rename/truncate, and metadata release; `__wt_metadata_*`, `__wt_meta_*`, and `__wt_turtle_*` for metadata table, checkpoint lists, meta tracking, turtle file bootstrap, and system information; `__wt_session_*`, `__wt_conn_*`, `__wti_conn_*`, and `__wti_connection_*` for connection/session lifecycle, data handles, worker threads, extension registration, load control, prefetch, page history, sweep, statlog, and close paths. The file also declares extension API shims (`__wt_ext_*`), JSON/packing helpers, random/time/verbose/error/debug functions, RW/spin lock helpers, hazard pointer helpers, generation helpers, hash map helpers, 4-bit integer packing inlines, and `HAVE_UNITTEST` declarations with `__ut_*` hooks for otherwise-internal block, disaggregation, layered-table, and transaction comparators.

Control flow: callers do not execute this header; they include it to bind to functions implemented across `src/*`. The declaration patterns still reveal control boundaries. Most mutating APIs take `WT_SESSION_IMPL *session` as the operational context and return `int` with `WT_GCC_FUNC_DECL_ATTRIBUTE((warn_unused_result))`, forcing error propagation through `WT_RET`-style call chains. Many routines take pointer out-parameters (`WT_CURSOR **cursorp`, `WT_BLOCK **blockp`, `WT_ITEM *buf`, `bool *existp`) and use explicit phase functions such as `*_start`, `*_finish`, `*_resolve`, `*_destroy`, `*_close`, and `*_release`. Inline declarations form fast-path control for memory barriers, visibility checks, cache accounting, filesystem wrappers, cursor state checks, and transaction read/write checks.

State and persistence behavior: although it stores no state itself, this header exposes the persistent-state surfaces of WiredTiger. Checkpoints, metadata, turtle file, history store, transaction logs, disaggregated checkpoint metadata, tiered object metadata, block addresses, cell time windows, and page images are all represented by declared entry points. In-memory state surfaces include sessions, data handles, hazard pointers, generations, cache usage counters, update vectors, cursor caches, thread groups, prefetch queues, prepared transaction artifacts, and extension-owned objects. Persistence risk is especially concentrated around APIs that encode/decode addresses or metadata (`__wt_block_addr_pack/unpack`, `__wti_block_disagg_ckpt_pack/unpack`, `__wt_meta_ckptlist_*`, `__wt_txn_printlog`, `__wt_turtle_update`) because a signature mismatch or unchecked return can corrupt durable files or recovery decisions.

Dependencies and integration points: it depends on the full WiredTiger internal type universe (`WT_SESSION_IMPL`, `WT_CONNECTION_IMPL`, `WT_BTREE`, `WT_CURSOR`, `WT_REF`, `WT_PAGE`, `WT_BLOCK`, `WT_BM`, `WT_TXN`, `WT_TIME_WINDOW`, `WT_CONFIG_ITEM`, `WT_ITEM`, and many feature structs), compiler attribute macros from `gcc.h` or platform equivalents, and configuration macros such as `HAVE_DIAGNOSTIC`, `HAVE_UNITTEST`, and visibility attributes. It is generated from source definitions and inline headers, so `dist/s_prototypes` or `prototypes.py` is an integration dependency: manual edits are overwritten and stale declarations would break builds or hide ABI drift.

Risks: the main risk is contract drift between implementation definitions, inline headers, and this generated declaration file. Because almost every internal subsystem appears here, stale prototypes can produce compile failures, wrong attributes, or subtler ABI mismatches when varargs, visibility, constness, or diagnostic-only parameters change. The broad use of `warn_unused_result` is a guard, but only if consumers respect compile warnings. The `HAVE_DIAGNOSTIC` conditional parameters in functions such as hazard/page APIs require macros and callers to stay synchronized across diagnostic and non-diagnostic builds. Unit-test-only declarations expose internals deliberately but must remain behind `HAVE_UNITTEST` to avoid growing production linkage.

Test signals: strong signals are generated-prototype checks, full multi-platform builds, diagnostic and non-diagnostic builds, unit-test builds, and link tests that touch extensions. Runtime signals come from recovery/checkpoint/rollback-to-stable tests, transaction timestamp visibility tests, block salvage/verify/compact tests, disaggregated and tiered storage suites, cursor API tests, metadata/turtle corruption tests, cache eviction stress, and sanitizer builds that exercise inline atomics and lock-free helpers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/extern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/extern_darwin.h -->
## sources/storage-engines/wiredtiger/src/include/extern_darwin.h

Purpose: this generated platform prototype header declares the Darwin-specific synchronization functions used by WiredTiger. It keeps macOS semaphore and futex-like APIs separate from the general POSIX and core `extern.h` surface.

Important APIs/types/functions: `__wt_futex_wait` waits on a `volatile WT_FUTEX_WORD *` while it equals an expected value, accepts a microsecond timeout, and can return the observed wake value through `wake_valp`. `__wt_futex_wake` wakes either one or all waiters according to `WT_FUTEX_WAKE` and publishes a wake value. `__wt_semaphore_init`, `__wt_semaphore_destroy`, `__wt_semaphore_post`, and `__wt_semaphore_wait` wrap `WT_SEMAPHORE` lifecycle and counting behavior for Darwin. All return `int` and are marked `warn_unused_result`.

Control flow: higher-level lock, condition, and thread coordination code calls these declarations through WiredTiger's internal synchronization abstractions. Wait paths typically validate the current futex word, sleep with a bounded timeout or until woken, then re-check shared state in the caller. Semaphore paths follow explicit init/post/wait/destroy lifecycle.

State and persistence behavior: no durable state is managed. The state is process-local synchronization state in `WT_FUTEX_WORD` and `WT_SEMAPHORE`; mistakes affect liveness, wakeup ordering, and shutdown rather than on-disk data directly. Because these primitives guard cache, eviction, checkpoint, and connection state, synchronization bugs can indirectly cause inconsistent in-memory decisions before persistence.

Dependencies and integration points: it depends on `futex.h` for `WT_FUTEX_WORD` and `WT_FUTEX_WAKE`, `WT_SESSION_IMPL`, `WT_SEMAPHORE`, `time_t`, and the Darwin implementation files selected by the build. It integrates with thread groups, condition variables, eviction/checkpoint workers, and any subsystem using WiredTiger semaphores.

Risks: Darwin does not expose Linux futex semantics directly, so implementation details must faithfully emulate the expected compare/sleep/wake behavior and timeout units. Lost wakeups, mishandled wake values, or unchecked return values can deadlock worker threads. Semaphore destroy during active waiters and timeout granularity differences are important edge cases.

Test signals: macOS builds, concurrency stress tests, eviction/checkpoint worker lifecycle tests, forced shutdown tests with waiting threads, timeout behavior tests, and sanitizer/thread-sanitizer runs are the best signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/extern_darwin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/extern_linux.h -->
## sources/storage-engines/wiredtiger/src/include/extern_linux.h

Purpose: this generated platform prototype header declares the Linux-specific futex and semaphore entry points used by WiredTiger synchronization code.

Important APIs/types/functions: the futex declarations mirror the Darwin surface: `__wt_futex_wait` blocks on a 32-bit `WT_FUTEX_WORD` if the observed value matches `expected`, with timeout and optional wake-value reporting, while `__wt_futex_wake` wakes one or all waiters and writes a wake value. The semaphore declarations provide `WT_SEMAPHORE` init, destroy, post, and wait. All functions return status and carry `warn_unused_result`.

Control flow: low-level Linux synchronization implementations back higher-level condition variables, semaphores, and thread coordination. Callers are expected to update shared words atomically, use futex wait as a blocking slow path, and wake waiters after publishing the state change they should observe.

State and persistence behavior: the only state is in-memory synchronization state. Linux futex operations are tied to the 32-bit word documented in `futex.h`; no file or metadata state is persisted. Correctness still affects persistence indirectly because these primitives coordinate threads that flush, checkpoint, evict, and close data handles.

Dependencies and integration points: it depends on Linux system futex support through implementation files, `WT_FUTEX_WORD`, `WT_FUTEX_WAKE`, `WT_SEMAPHORE`, `WT_SESSION_IMPL`, and `time_t`. It integrates with the same engine-wide synchronization paths as Darwin and Windows but can use native futex semantics.

Risks: futex correctness requires exact word sizing, expected-value comparison, timeout conversion, EINTR/retry behavior, and memory ordering around wait/wake. Returning wake values through `wake_valp` means stale or racy publication would confuse higher layers. Callers must not ignore errors from these functions.

Test signals: Linux concurrency stress, thread sanitizer builds where available, futex timeout and wake-one/wake-all tests, worker shutdown tests, and long-running eviction/checkpoint/backup workloads are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/extern_linux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/extern_posix.h -->
## sources/storage-engines/wiredtiger/src/include/extern_posix.h

Purpose: this generated POSIX prototype header declares the OS abstraction layer used on Unix-like platforms: path handling, privilege checks, dynamic loading, condition variables, filesystem hooks, memory mapping, time, process/thread utilities, and stream buffering.

Important APIs/types/functions: path and process helpers include `__wt_absolute_path`, `__wt_path_separator`, `__wt_has_priv`, `__wt_process_id`, and `__wt_thread_id`. Dynamic library APIs are `__wt_dlopen`, `__wt_dlsym`, and `__wt_dlclose`. Condition and once primitives are `__wt_cond_alloc`, `__wt_cond_destroy`, `__wt_cond_signal`, `__wt_cond_wait_signal`, and `__wt_once`. Thread wrappers are `__wt_thread_create`, `__wt_thread_join`, and `__wt_thread_str`. Time and sleep APIs include `__wt_epoch_raw`, `__wt_localtime`, `__wt_sleep`, and `__wt_yield`. Filesystem integration is anchored by `__wt_os_posix` plus `__wti_posix_directory_list*`, `__wti_posix_file_extend`, `__wti_posix_map`, `__wti_posix_map_preload`, `__wti_posix_map_discard`, `__wti_posix_unmap`, and remap/resize helpers.

Control flow: startup calls `__wt_os_posix` to install a `WT_FILE_SYSTEM`. Runtime code flows through wrapper functions rather than calling libc/syscalls directly, allowing error mapping, session diagnostics, and durable file semantics to stay consistent. Memory mapping flows through map/preload/discard/unmap, while remap-aware resize uses prepare/remap/release helpers around file growth.

State and persistence behavior: this layer does not own database metadata, but it directly manipulates durable files and mapped views. Directory listing and file-size/extend/map operations influence table files, log files, checkpoint files, and backup/copy workflows. Condition variables and threads are in-memory process state; dynamic library handles hold extension-loading state.

Dependencies and integration points: it depends on POSIX APIs (`dlopen`, pthreads, time functions, file/mmap primitives, process IDs, stdio buffering) behind WiredTiger types such as `WT_SESSION_IMPL`, `WT_FILE_SYSTEM`, `WT_FILE_HANDLE`, and `WT_DLH`. It integrates with extension loading, storage source/file-system abstraction, live restore/remap handling, logging, checkpoint, backup, and diagnostic output.

Risks: OS wrappers are portability choke points. Path rules, privilege detection, mmap lifetime, remap during resize, durable extend semantics, and directory-list filtering can differ across POSIX variants. `__wt_getenv`, `__wt_localtime`, thread, snprintf, and sleep functions with default visibility may be consumed outside the core library, so signature or visibility drift is risky. Memory-mapped file length/cookie mismatches can lead to stale reads or unmap errors.

Test signals: POSIX filesystem tests, extension load/unload tests, mmap and remap resize tests, backup/copy-and-sync tests, file durability tests, thread lifecycle tests, and builds on Linux, macOS, and other Unix platforms validate this header's contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/extern_posix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/extern_win.h -->
## sources/storage-engines/wiredtiger/src/include/extern_win.h

Purpose: this generated Windows platform prototype header declares WiredTiger's Windows OS abstraction surface. It covers Windows error translation, path handling, dynamic loading, futex/semaphore equivalents, condition variables, threads, time, UTF conversion, directory listing, file size, and memory mapping.

Important APIs/types/functions: Windows error APIs include `__wt_getlasterror`, `__wt_formatmessage`, and `__wt_map_windows_error`; extension-facing error mapping is exposed through the main extern surface. Path/privilege/process helpers include `__wt_absolute_path`, `__wt_has_priv`, `__wt_path_separator`, `__wt_process_id`, and `__wt_thread_id`. Synchronization APIs include `__wt_cond_*`, `__wt_futex_wait`, `__wt_futex_wake`, and `__wt_semaphore_*`. Runtime wrappers include `__wt_once`, `__wt_os_win`, `__wt_thread_create`, `__wt_thread_join`, `__wt_thread_str`, `__wt_epoch_raw`, `__wt_sleep`, and `__wt_yield`. Windows-specific conversion and filesystem APIs include `__wti_to_utf16_string`, `__wti_to_utf8_string`, `__wti_win_directory_list*`, `__wti_win_fs_size`, `__wti_win_map`, and `__wti_win_unmap`.

Control flow: connection startup initializes Windows OS services through `__wt_os_win`. File and directory operations route through Windows-specific implementations to handle UTF-16 paths and Windows error codes before returning WiredTiger-style `int` statuses. Dynamic loading and symbol resolution wrap Windows library APIs. Synchronization and thread wrappers provide the same internal shape used by POSIX builds.

State and persistence behavior: durable effects occur through Windows filesystem size, mapping, directory, and dynamic-library operations. UTF conversion buffers are transient `WT_ITEM` allocations but are critical for correct path access. Futex/semaphore/condition/thread state is process-local and coordinates workers that can affect persistence.

Dependencies and integration points: it depends on Windows types such as `DWORD` and wide-character APIs, plus WiredTiger session, file-system, file-handle, semaphore, futex, condition, thread, and dynamic-library types. It integrates with extension loading, storage files, backup/directory traversal, memory-mapped reads, and all worker-thread subsystems.

Risks: Windows path and encoding behavior is the major portability risk. UTF-8/UTF-16 conversion errors, path separator assumptions, and Windows error-code mapping can produce misleading diagnostics or inaccessible files. Memory mapping and unmapping must keep cookies and lengths aligned with Windows handles. Futex emulation and semaphore behavior must match expectations from the shared synchronization code. Visibility attributes are absent compared with POSIX, so exports are governed by the Windows build/link configuration.

Test signals: Windows CI builds, path tests with non-ASCII names, directory listing and backup tests, mmap tests, extension DLL load/unload tests, Windows error mapping tests, and concurrency shutdown tests are the best validation signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/extern_win.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/futex.h -->
## sources/storage-engines/wiredtiger/src/include/futex.h

Purpose: this header defines the tiny shared type contract for WiredTiger's futex-style synchronization API. The comment explicitly says the futex API is for building other synchronization mechanisms and is not intended for general use.

Important APIs/types/functions: `WT_FUTEX_WORD` is a `uint32_t`, matching Linux's futex word-size limit even on 64-bit architectures. `WT_FUTEX_WAKE` is an enum with `WT_FUTEX_WAKE_ONE` and `WT_FUTEX_WAKE_ALL`, controlling whether wake operations release one waiter or all waiters.

Control flow: this header does not implement waiting or waking; platform prototype headers declare `__wt_futex_wait` and `__wt_futex_wake`, and platform source files implement them. Higher-level synchronization code stores state in a `WT_FUTEX_WORD`, waits while the word has an expected value, and wakes waiters after changing the word.

State and persistence behavior: futex words are in-memory synchronization state only. They do not persist to disk, but they gate access to shared engine state and can affect the timing of checkpoint, eviction, and shutdown activity.

Dependencies and integration points: it depends only on fixed-width integer definitions and is consumed by Linux, Darwin, Windows, and any common synchronization abstraction that needs `WT_FUTEX_WORD` or `WT_FUTEX_WAKE`.

Risks: the hard 32-bit word contract must remain consistent across all platform implementations. Extending the enum or changing word size would break native futex assumptions and possibly ABI/layout assumptions in synchronization structs. The "not suitable for general use" warning matters because direct use can bypass required memory-ordering and loop/recheck patterns.

Test signals: compile tests across platforms, futex wait/wake behavior tests, and higher-level semaphore/condition stress tests validate this contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/gcc.h -->
## sources/storage-engines/wiredtiger/src/include/gcc.h

Purpose: this header centralizes GCC/Clang-oriented compiler attributes, packed-struct syntax, CPU pause and memory-barrier primitives, and generated atomic helper functions for WiredTiger. It is the compiler and hardware memory-model adapter for the rest of the engine.

Important APIs/types/functions: format macros include `WT_PTRDIFFT_FMT` and `WT_SIZET_FMT`; packed structs use `WT_PACKED_STRUCT_BEGIN/END`. Function attributes are split between `WT_GCC_FUNC_ATTRIBUTE`, which marks definitions for prototype generation, and `WT_GCC_FUNC_DECL_ATTRIBUTE`, which emits declaration attributes such as `warn_unused_result`, `visibility`, `format`, or `cold`. Barrier macros include `WT_COMPILER_BARRIER`, architecture-specific `WT_PAUSE`, `WT_FULL_BARRIER`, `WT_ACQUIRE_BARRIER`, and `WT_RELEASE_BARRIER`. Atomic helpers are generated by `WT_ATOMIC_FUNC`, `WT_ATOMIC_CAS_FUNC`, and `WT_ATOMIC_FUNC_STORE_LOAD` for integer sizes, signed/unsigned variants, `size_t`, `bool`, and `uintmax_t`. Specialized helpers cover relaxed double load/store, enum and pointer acquire/release access, pointer CAS, and generic relaxed and/or/load/store.

Control flow: architecture selection happens at preprocess time. x86 uses `pause` and `mfence` with compiler barriers for acquire/release because of TSO; MIPS, PPC64, AArch64, s390x, SPARC, RISC-V, and LoongArch each map to their native barrier instructions. If no supported architecture is detected, compilation fails with "No barrier implementation for this hardware". On AArch64 with `HAVE_RCPC` and without TSAN, `ACQUIRE_READ` and `RELEASE_WRITE` use LDAPR/STLR assembly variants; otherwise they fall back to GCC `__atomic` builtins. Atomic helpers provide relaxed, acquire/release, seq-cst, volatile, add/sub/fetch-add, and CAS variants.

State and persistence behavior: no durable state is stored. The state affected is every shared in-memory variable updated through these helpers: cache counters, flags, transaction IDs, generation counters, hazard slots, worker-state flags, and lock-free coordination fields. Memory-ordering bugs here can make persistent subsystems observe stale or reordered state before writing checkpoints, metadata, or logs.

Dependencies and integration points: it depends on GCC/Clang-compatible inline assembly and `__atomic` builtins, `assert.h`, fixed-width integer types, architecture predefines, build flags such as `HAVE_RCPC` and `TSAN_BUILD`, and C static assertions. It is included by low-level headers such as `hardware.h`, inline cache/transaction/page helpers, spin locks, and generated prototypes that attach attributes.

Risks: this file is architecture-sensitive. An incorrect barrier mapping can create rare corruption, visibility, or deadlock bugs. The AArch64 RCPC path uses inline assembly constraints and size dispatch, so type-size mismatches or unsupported compiler behavior would be dangerous; the `if (0)` assignment and `static_assert` are safeguards. TSAN builds intentionally use `__atomic` because standalone barriers are not tracked. New architectures must not silently compile without an explicit barrier implementation.

Test signals: cross-architecture CI, sanitizer/TSAN builds, stress tests for eviction/checkpoint/transaction concurrency, spin-lock benchmarks, and targeted tests for atomic flag/counter behavior are the key signals. Compile failures on unsupported hardware are intentional and should be treated as a porting task, not a test failure in supported matrices.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/generation.h -->
## sources/storage-engines/wiredtiger/src/include/generation.h

Purpose: this header defines callback cookie structs for WiredTiger's generation tracking logic. Generations are used to coordinate resource lifetime and determine whether sessions are still active in a generation before reclaiming or advancing shared resources.

Important APIs/types/functions: `WT_GENERATION_COOKIE` carries `ret_active`, `ret_oldest_gen`, `which`, and `target_generation` while walking sessions to ask whether a target generation is still active and what the oldest seen generation is. `WT_GENERATION_DRAIN_COOKIE` embeds the base cookie and adds `start`, `minutes`, `pause_cnt`, and `verbose_timeout_flags` for drain operations that may wait and report progress/timeouts.

Control flow: session-walk code passes these cookies to callbacks. The callback reads each session's generation for the selected resource (`which`), updates whether the target is active, and records the oldest generation. Drain control uses the extended cookie to pause, track elapsed time, and decide whether to emit verbose timeout diagnostics.

State and persistence behavior: the cookies are stack/transient control state, not persistent state. They coordinate safe reclamation of in-memory resources that may protect persistent structures indirectly, such as data handles, hazard-protected pages, metadata views, or checkpoint-related resources.

Dependencies and integration points: it depends on `struct timespec`, `uint64_t`, `bool`, and generation constants/arrays defined elsewhere in the WiredTiger connection and session structures. It integrates with `generation_inline.h` and functions declared in `extern.h` such as `__wt_gen_active`, `__wt_gen_init`, `__wt_gen_next_drain`, `__wt_session_gen_enter`, and `__wt_session_gen_leave`.

Risks: incorrect cookie updates can free resources while a session still references them or can stall drains forever. Timeout reporting fields must not change behavior in a way that hides a stuck generation. The embedded-base layout is simple but assumes callbacks know when they can treat the drain cookie as a base generation cookie.

Test signals: generation drain tests, handle sweep tests, cache/session close tests, long-running cursor plus schema operation tests, diagnostic timeout tests, and sanitizer runs that catch use-after-free are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/generation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/generation_inline.h -->
## sources/storage-engines/wiredtiger/src/include/generation_inline.h

Purpose: this inline header provides the fast-path accessors for WiredTiger generation counters. The comment notes a future cleanup goal to move all generation functions into one file.

Important APIs/types/functions: `__wt_gen(session, which)` returns the connection-wide generation for a resource by relaxed volatile atomic load from `S2C(session)->generations[which]`. `__wt_gen_next(session, which, genp)` atomically increments the connection generation and optionally returns the new value. `__wt_session_gen(session, which)` returns the current session's generation for the selected resource by relaxed volatile atomic load from `session->generations[which]`.

Control flow: resource managers call `__wt_gen_next` when moving a resource class to a new generation. Sessions enter and leave generations through non-inline functions declared in `extern.h`; checks compare per-session generation values with connection generation values to decide whether old resources remain active. The inline functions keep reads and increments cheap because they are used in frequent synchronization paths.

State and persistence behavior: the state is in-memory generation counters on the connection and sessions. Generations are not durable, but they protect lifecycle decisions for resources that can back durable data, including data handles, metadata, page references, and cache structures.

Dependencies and integration points: it depends on `WT_SESSION_IMPL`, `S2C(session)`, the `generations` arrays, and atomic helpers from `gcc.h`. It integrates with `generation.h` cookies, session generation enter/leave functions, handle sweep, hazard-pointer style lifetime control, and shutdown/drain logic.

Risks: relaxed loads are intentional but require callers to provide the necessary synchronization and comparison discipline. Using the wrong `which` index or forgetting to publish session generation entry/exit can cause premature reclamation or leaks. `__wt_gen_next` uses a seq-cst add helper, so changing it to a weaker operation would need careful review.

Test signals: handle lifecycle stress, session close while resources are active, generation drain timeout tests, schema/drop/rename concurrent with cursors, and sanitizer use-after-free detection validate this area.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/generation_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/hardware.h -->
## sources/storage-engines/wiredtiger/src/include/hardware.h

Purpose: this header layers shared-memory annotations, one-shot read/write macros, atomic flag manipulation, and cache-line padding helpers over the compiler/CPU primitives from `gcc.h`. It documents and implements common lock-free communication idioms used throughout WiredTiger.

Important APIs/types/functions: `wt_shared` is an annotation-only macro for variables used in lock-free inter-thread communication. `WT_RELEASE_WRITE_WITH_BARRIER` and `WT_ACQUIRE_READ_WITH_BARRIER` are deprecated wrappers that either use TSAN-visible `__atomic` operations or explicit barriers plus relaxed accesses. `WT_READ_ONCE` and `WT_WRITE_ONCE` force a single source-level memory access to compile into a single load/store using volatile typed access under GCC/Clang, falling back to barrier wrappers elsewhere. Atomic flag helpers include `FLD_ISSET_ATOMIC_8/16/32`, `FLD_SET_ATOMIC_8/16/32`, `FLD_CLR_ATOMIC_8/16/32`, and object-oriented `F_ISSET_ATOMIC_*`, `F_SET_ATOMIC_*`, `F_CLR_ATOMIC_*` variants for `flags_atomic`. Cache-line support includes `WT_CACHE_LINE_ALIGNMENT` with architecture-specific sizes and `WT_CACHE_LINE_PAD_BEGIN/END`.

Control flow: atomic flag set/clear first do a quick load to avoid unnecessary CAS, then loop loading the original value and using compare-and-swap until the masked update succeeds. `WT_READ_ONCE` and `WT_WRITE_ONCE` are used at individual access sites to prevent compiler load fusion, invented loads, or store duplication in algorithms that intentionally allow concurrent unsynchronized access. Padding macros wrap struct fields in an anonymous union so array elements can occupy separate cache lines without requiring aligned allocation.

State and persistence behavior: this header only affects in-memory state, especially flags and counters read by multiple threads. It can indirectly affect durable behavior because shared flags coordinate checkpoint, eviction, block cache, background compact, shutdown, and transaction state.

Dependencies and integration points: it depends on `gcc.h` atomic and barrier helpers, GCC/Clang `__typeof__` when available, TSAN build flags, `WT_CACHE_LINE_ALIGNMENT`, and structures with `flags_atomic` members. It is consumed by many engine structs and lock-free algorithms.

Risks: the macros evaluate fields in low-level contexts and must be used with correctly sized integer fields. CAS loops are safe for simple bit masks but are not a substitute for higher-level locking when compound invariants exist. `WT_READ_ONCE`/`WT_WRITE_ONCE` provide compiler-access control, not full synchronization; callers still need acquire/release or stronger ordering when publishing data. Padding through anonymous unions is portable for supported compilers but affects struct layout and memory footprint.

Test signals: TSAN builds, stress tests around atomic flags, shutdown and worker coordination tests, cache-line sensitive performance tests, and compile tests on PPC64/s390x/default architectures validate this header.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/hardware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/hash_map.h -->
## sources/storage-engines/wiredtiger/src/include/hash_map.h

Purpose: this header defines WiredTiger's simple generic hash map container. The comments explicitly position it for low-performance use cases and prototyping rather than highly optimized hot paths.

Important APIs/types/functions: `WT_HASH_MAP_ITEM` stores a `TAILQ_ENTRY`, owned `key` and `data` pointers, and their sizes. `WT_HASH_MAP` stores an array of bucket heads (`TAILQ_HEAD(__wt_hash_map_hash, __wt_hash_map_item) *hash`), a parallel array of `WT_SPINLOCK` bucket locks, the bucket count `hash_size`, and optional fixed `value_size`. Functions are declared in `extern.h`: `__wt_hash_map_init`, `__wt_hash_map_get`, `__wt_hash_map_destroy`, and `__wt_hash_map_unlock`.

Control flow: callers initialize a map with a chosen bucket count, then call `__wt_hash_map_get` with key bytes and options to insert if missing and optionally keep the bucket lock held. Items are stored on per-bucket tail queues. If a caller keeps the lock, it must later call `__wt_hash_map_unlock` with the same key information. Destroy releases the map, locks, and owned item memory.

State and persistence behavior: all map state is in memory. The map owns key and value allocations, so callers must treat returned data as map-owned and should not free it directly. No durable state is written.

Dependencies and integration points: it depends on queue macros (`TAILQ_ENTRY`, `TAILQ_HEAD`), `WT_SPINLOCK`, memory allocation helpers, and declarations in `extern.h`. It can be used by subsystems needing modest keyed lookup without adding a specialized data structure.

Risks: bucket count selection affects performance and collision behavior. The keep-locked option creates an obligation that is easy to violate, leading to deadlock. Because the map owns memory, storing pointers to external lifetime-managed data as values would be risky unless copied as intended. It is not optimized for high-contention hot paths.

Test signals: unit tests for insert/find/missing-key behavior, duplicate key handling, fixed and variable value sizes, collision-heavy workloads, keep-locked/unlock pairing, and destroy-time leak checks are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/hash_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/hazard.h -->
## sources/storage-engines/wiredtiger/src/include/hazard.h

Purpose: this header defines the callback cookie used when walking sessions to find active hazard pointers. Hazard pointers protect pages or references from being reclaimed while a session may still use them.

Important APIs/types/functions: `WT_HAZARD_COOKIE` carries `search_ref`, an optional returned owning session pointer `ret_session`, an optional returned hazard slot `ret_hp`, and walk counters `walk_cnt` and `max`. Related functions are declared in `extern.h`, including `__wt_hazard_check`, `__wt_hazard_check_assert`, `__wt_hazard_set_func`, `__wt_hazard_clear`, and `__wt_hazard_close`.

Control flow: a caller that wants to know whether a `WT_REF` is protected populates `search_ref` and walks sessions. The callback increments `walk_cnt`, scans hazard slots up to `max`, and records the matching session and hazard pointer when found. Diagnostic/assert paths can wait for hazards or fail if an expected hazard state is violated.

State and persistence behavior: the cookie is transient. The protected state is in-memory page/reference ownership. Hazard correctness indirectly protects persistent correctness by preventing eviction, split, discard, or reconciliation code from freeing or reusing page structures while readers still depend on them.

Dependencies and integration points: it depends on `WT_REF`, `WT_SESSION_IMPL`, `WT_HAZARD`, and session-walk infrastructure. It integrates with page eviction, tree walk, cursor positioning, page release, and diagnostic verification.

Risks: incomplete scanning or stale returned pointers can cause use-after-free, eviction stalls, or false-positive busy results. `walk_cnt`/`max` must reflect the configured hazard slot capacity. Hazard operations are concurrency-sensitive and must be paired correctly with page acquire/release paths.

Test signals: eviction stress under concurrent readers, cursor traversal during page splits, diagnostic hazard assertions, sanitizer use-after-free detection, and workloads that force hazard table growth or saturation are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/hazard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/int4bitpack_inline.h -->
## sources/storage-engines/wiredtiger/src/include/int4bitpack_inline.h

Purpose: this inline header implements a compact Golomb-like variable-length encoding for small integers using 4-bit chunks. It is intended for efficient internal packing of positive integers, with helper conversion for signed integers through a zigzag-like transform.

Important APIs/types/functions: internal contexts `WT_4B_PACK_CONTEXT` and `WT_4B_UNPACK_CONTEXT` track the caller pointer, buffer end, start pointer, and whether the next operation targets the low or high nibble. Internal helpers initialize/finalize contexts, put/get 4-bit chunks, encode/decode one positive integer, and compute the number of nibbles required. Public inline APIs include `__wt_4b_pack_posint1`, `__wt_4b_pack_posint2`, `__wt_4b_pack_array`, `__wt_4b_unpack_posint1`, `__wt_4b_unpack_posint2`, `__wt_4b_unpack_array`, `__wt_4b_size_posint1`, `__wt_4b_size_posint2`, `__wt_4b_size_array`, `__wt_encode_signed_as_positive`, and `__wt_decode_positive_as_signed`.

Control flow: packing initializes a context at `*pp`, writes low nibble first, then high nibble in the same byte, and finalizes by advancing the pointer if only the low nibble was written. Each chunk uses bit 3 as a continuation flag and bits 0-2 as payload. Encoding consumes three low bits at a time; after the first continued chunk it subtracts one from the shifted remainder so decode can add one for later chunks. Unpacking mirrors this by reading low nibble then high nibble, advancing the pointer after the high nibble, accumulating payload shifted by multiples of three, and adding one to non-first chunks. Array functions repeat the scalar codec in one context so adjacent values can share bytes.

State and persistence behavior: state is caller-provided byte buffers and pointer advancement. The encoded byte stream may become persistent if used inside on-disk metadata or page images, so the nibble order, continuation bit, and plus-one rule are compatibility-sensitive. Size functions must match pack output exactly for callers that preallocate buffers.

Dependencies and integration points: it depends on `uint8_t`, `uint64_t`, `int64_t`, `size_t`, `WT_INLINE`, `WT_RET`, and error constants `ENOMEM` and `EINVAL`. Its prototypes are included in `extern.h` as `static WT_INLINE` declarations. It can integrate with page/block metadata or compact value encodings that need dense unsigned integer storage.

Risks: boundary handling is subtle. `__4b_pack_put_chunk` checks `end` before writing a fresh byte but can advance one past `end` after filling a high nibble, which is acceptable only because no write occurs after that advance. Unpack returns `EINVAL` when the current byte pointer reaches `end`, but malformed streams with endless continuation bits rely on `end` to terminate. The format currently only packs positive integers; signed support requires explicit encode/decode transforms by callers. Any format change would break existing encoded data.

Test signals: round-trip tests for boundary values 0 through multi-chunk values, arrays with odd/even nibble counts, exact size-function agreement, end-of-buffer `ENOMEM`, truncated input `EINVAL`, malformed continuation streams, signed encode/decode around zero and `INT64_MIN/INT64_MAX`, and fuzzing of random byte streams are the key signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/int4bitpack_inline.h -->
