# subset-b-008716 Research

Grouped research report for RocksDB range-tree locking portability, utility, lock manager/tracker, and optimistic transaction sources. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_pthread.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_pthread.h

## Purpose
Provides PerconaFT-style pthread wrapper types and inline helpers used by the Toku locktree code embedded in RocksDB. It normalizes mutexes, condition variables, rwlocks, thread-local keys, joins, detaches, and thread exit behind `toku_*` names while preserving optional performance-schema instrumentation and debug ownership checks.

## Important APIs, Types, And Functions
The main public types are `toku_mutex_t`, `toku_cond_t`, `toku_pthread_rwlock_t`, `toku_mutex_aligned_t`, and aliases such as `toku_pthread_t`, `toku_pthread_key_t`, and `toku_timespec_t`. Important helpers include `toku_mutex_init`, `toku_mutex_destroy`, `toku_mutex_lock_with_source_location`, `toku_mutex_trylock_with_source_location`, `toku_mutex_unlock`, `toku_cond_init`, `toku_cond_wait_with_source_location`, `toku_cond_timedwait_with_source_location`, `toku_cond_signal`, `toku_cond_broadcast`, and thread-specific wrappers. Macros inject `__FILE__` and `__LINE__` into lock and wait calls.

## Control Flow
Mutex lock and condition wait operations start instrumentation, call the underlying pthread primitive, end instrumentation, assert success, then update debug fields when enabled. Condition waits temporarily clear debug ownership before the pthread wait releases the mutex and restore ownership after wake-up. Destructor and initializer wrappers maintain instrumentation handles alongside native pthread objects.

## State And Persistence Behavior
All state is in memory. `toku_mutex_t` and `toku_cond_t` store native pthread objects plus optional instrumentation and debug metadata. There is no durable persistence. Correct lifetime is manual: callers must initialize before use and destroy after no threads can access the object.

## Dependencies And Integration Points
Depends on `pthread.h`, `toku_portability.h`, assertion macros, and Toku instrumentation functions such as `toku_instr_mutex_*` and `toku_instr_cond_*`. It is used broadly by the range-tree lock library for locktree manager, lock requests, and wait queues.

## Risks And Edge Cases
`toku_mutex_trylock_with_source_location` calls `pthread_mutex_lock` rather than `pthread_mutex_trylock`, so its name is misleading and any caller expecting nonblocking behavior would block. Debug assertions depend on strict single-owner use and can fire if native pthread objects are manipulated outside these wrappers. Adaptive mutex initialization is platform-dependent, with musl and Apple falling back to default mutexes.

## Test Signals
Signals are indirect through range-locking tests and locktree unit coverage. Debug builds can catch invalid unlocks, destroyed locked mutexes, and condition waits without held mutexes. Sanitizer or deadlock tests should pay attention to the misleading trylock wrapper.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_pthread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_race_tools.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_race_tools.h

## Purpose
Defines optional Valgrind DRD/Helgrind annotations and unsafe access helpers for the imported Toku code. When Valgrind support is unavailable, all annotations compile to no-ops so the locktree code can build normally.

## Important APIs, Types, And Functions
Macros include `TOKU_ANNOTATE_NEW_MEMORY`, `TOKU_VALGRIND_HG_ENABLE_CHECKING`, `TOKU_VALGRIND_HG_DISABLE_CHECKING`, `TOKU_DRD_IGNORE_VAR`, ignore-read/write begin/end annotations, and `TOKU_VALGRIND_RESET_MUTEX_ORDERING_INFO`. Templates `toku_unsafe_fetch` and `toku_unsafe_set` perform intentionally racy reads/writes while bracketing them with DRD ignore annotations.

## Control Flow
On Linux with `USE_VALGRIND`, the header includes Valgrind DRD and Helgrind headers and maps macros directly. Otherwise it defines `NVALGRIND`, sets `RUNNING_ON_VALGRIND` to zero, and turns the annotations into empty operations. Unsafe fetch/set execute a plain load or store while annotations are active; Helgrind enable/disable calls are compiled under `if (0)` due known false-positive behavior.

## State And Persistence Behavior
No persistent state is kept. The only side effects are tool annotations and the memory load/store in unsafe helpers.

## Dependencies And Integration Points
Used by OMT mark/index bitfields and other locktree internals that intentionally allow benign races. Integrates with DRD/Helgrind only in instrumented builds and is otherwise transparent to RocksDB.

## Risks And Edge Cases
These helpers can hide real races if used around mutable data without a higher-level synchronization argument. Because no-op mode is the default on most builds, correctness cannot depend on annotations. The `if (0)` Helgrind disable/enable blocks document a historical limitation but also mean Helgrind may still report some intentional races.

## Test Signals
Valgrind DRD runs should suppress known benign races around OMT mark bits. Ordinary unit tests only validate that the no-op path compiles and that higher-level concurrent lock operations behave correctly.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_race_tools.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_time.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_time.h

## Purpose
Provides Toku-style timing primitives for the locktree code, especially cheap performance timestamps and wall-clock microsecond time.

## Important APIs, Types, And Functions
`tokutime_t` is a `uint64_t` performance timestamp. `toku_time_now()` reads an architecture-specific cycle or timebase register. `toku_current_time_microsec()` uses `gettimeofday` and returns microseconds since the Unix epoch.

## Control Flow
`toku_time_now()` is a compile-time architecture switch: x86 uses `rdtsc`, AArch64 reads `cntvct_el0`, PowerPC uses `__ppc_get_timebase`, s390x uses `stckf`, RISC-V uses `rdcycle`, and LoongArch uses `rdtime.d`. Unsupported architectures fail compilation. Wall-clock microseconds are fetched through `gettimeofday`.

## State And Persistence Behavior
No state is stored. Values are transient timing samples used by status counters and wait/escalation timing.

## Dependencies And Integration Points
Depends on system time headers and architecture intrinsics/assembly. Locktree status and lock wait paths use these values for elapsed-time statistics. Comments note RocksDB `Env::NowMicros()` and `NowNanos()` as possible substitutes.

## Risks And Edge Cases
Cycle counters are not portable wall-clock time and can vary by architecture, CPU frequency behavior, or virtualization. `gettimeofday` can move backward if system time changes. The hard `#error` on unsupported platforms makes this header a portability gate for range-tree locking.

## Test Signals
Compile coverage across supported architectures is important. Runtime tests should only compare elapsed differences, not absolute `tokutime_t` values. Lock wait and escalation counters are indirect behavioral signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/txn_subst.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/txn_subst.h

## Purpose
Supplies a small substitute for TokuDB transaction identifiers needed by the standalone locktree integration.

## Important APIs, Types, And Functions
Defines `TXNID` as `uint64_t`, sentinel constants `TXNID_NONE`, `TXNID_SHARED`, and `TXNID_ANY`, and `TxnidVector`, a `std::set<TXNID>` with a convenience `contains()` method.

## Control Flow
There is no dynamic control flow. The locktree code uses sentinels to distinguish no owner, multiple shared owners, and wildcard transaction matching.

## State And Persistence Behavior
`TxnidVector` owns an in-memory ordered set of transaction IDs. No durable transaction state is represented here.

## Dependencies And Integration Points
Includes `omt.h` and `<set>`. Range-tree status dumping uses `TXNID_SHARED` plus `TxnidVector` to enumerate owners. RocksDB casts `PessimisticTransaction*` values to `TXNID`, so this type bridges pointer identity into the imported locktree API.

## Risks And Edge Cases
Pointer-to-`uint64_t` transaction IDs are process-local and must never be persisted. The sentinel values reserve top unsigned values, so real IDs must avoid them. `contains()` is non-const, limiting use through const references.

## Test Signals
Signals are indirect through lock status and deadlock path reporting, especially shared-owner paths where `TXNID_SHARED` requires consulting the owner set.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/txn_subst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/standalone_port.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/standalone_port.cc

## Purpose
Implements standalone glue that lets the imported Toku locktree build inside RocksDB without the rest of PerconaFT/TokuDB.

## Important APIs, Types, And Functions
Defines allocation wrappers `toku_free`, `toku_xmalloc`, `toku_xrealloc`, `toku_xmemdup`, and `toku_xcalloc`; global instrumentation keys such as `lock_request_m_wait_cond_key` and `manager_mutex_key`; `toku_memory_footprint`; `LTM_STATUS_S::init` and `destroy`; and bytewise key comparators `toku_keycompare` and `toku_builtin_compare_fun`.

## Control Flow
Allocation wrappers directly call libc allocation functions. Status initialization populates each `ltm_status.status` row with `TOKUFT_STATUS_INIT`, including lock memory, escalation, wait, timeout, and STO metrics. Comparator functions compare common prefixes with `memcmp`, then break ties by key length.

## State And Persistence Behavior
The file owns process-global instrumentation key variables and the global `ltm_status` object. State is in-memory status metadata only. It does not persist lock state or allocator state.

## Dependencies And Integration Points
Includes Toku compatibility headers, `ft-status`, memory helpers, and `dbt.h`. `RangeTreeLockManager::GetStatus()` later reads locktree status rows initialized through this path. Toku locktree code depends on these symbols during linking.

## Risks And Edge Cases
The `toku_x*` functions do not abort on allocation failure despite Toku naming convention comments, so callers assuming non-null allocation can crash later. `LTM_STATUS_S::destroy()` leaves partitioned counter destruction as a TODO. This file is excluded on Windows, matching the range-tree lock manager's `OS_WIN` guard.

## Test Signals
Link success for range-tree builds is the primary signal. Runtime signals include populated lock manager counters and correct bytewise comparator behavior for internal DBTs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/standalone_port.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/dbt.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/dbt.cc

## Purpose
Implements helper functions for Berkeley DB-style `DBT` objects used as the locktree's key/range carrier.

## Important APIs, Types, And Functions
Functions include `toku_init_dbt`, `toku_empty_dbt`, `toku_init_dbt_flags`, `toku_destroy_dbt`, `toku_fill_dbt`, `toku_memdup_dbt`, `toku_copyref_dbt`, `toku_clone_dbt`, `toku_sdbt_cleanup`, infinity sentinel accessors, `toku_dbt_is_infinite`, `toku_dbt_is_empty`, `toku_dbt_infinite_compare`, and `toku_dbt_equals`.

## Control Flow
Initialization zeroes the struct. Fill/copyref create non-owning DBTs over caller memory. Memdup/clone allocate owned storage and set `DB_DBT_MALLOC`. Destroy frees only DBTs marked `DB_DBT_MALLOC` or `DB_DBT_REALLOC`. Infinity values are represented by the addresses of static DBT objects, not by payload bytes.

## State And Persistence Behavior
DBTs are transient memory views or owned buffers. Static positive/negative infinity sentinels live for the process. No durable data is written.

## Dependencies And Integration Points
Depends on `db.h`, `memory.h`, and Toku allocation wrappers. Range-tree lock manager serializes endpoints into strings, wraps them in DBTs with `toku_fill_dbt`, and passes them into locktree requests and range buffers.

## Risks And Edge Cases
Non-owning DBTs require the referenced string or buffer to outlive the locktree call that consumes it. Equality checks pointer and size, not byte content, for non-infinite DBTs. Infinity is identity-based; copying the sentinel content into another DBT does not create an infinite DBT.

## Test Signals
Indirect tests come from range locking and lock status dumping. Focused tests should cover ownership flags, sentinel comparisons, and cleanup of allocated DBTs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/dbt.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/dbt.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/dbt.h

## Purpose
Declares the DBT helper API used by the standalone Toku locktree code.

## Important APIs, Types, And Functions
The header declares initialization, fill, duplication, clone, destroy, simple DBT cleanup, positive/negative infinity sentinels, infinity/empty checks, infinity comparison, and pointer equality helpers.

## Control Flow
As a declaration header, it has no runtime flow. Its comments document ownership expectations: some helpers only reference caller memory while others allocate and require `toku_destroy_dbt`.

## State And Persistence Behavior
The declared API manipulates in-memory `DBT` and `simple_dbt` structures only.

## Dependencies And Integration Points
Includes the local `db.h` compatibility header. It is included by `standalone_port.cc`, locktree code, range buffers, and RocksDB's range-tree manager/tracker bridge.

## Risks And Edge Cases
The API is easy to misuse because ownership is encoded in flags and several helpers return DBTs pointing at external memory. Infinite DBTs are pointer sentinels, so callers must preserve sentinel identity.

## Test Signals
Compile coverage plus range lock acquisition/release tests validate the header contract. Dedicated tests should assert ownership and sentinel behavior across declarations and implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/dbt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/growable_array.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/growable_array.h

## Purpose
Defines a minimal constructor-free dynamic array used by imported Toku structures, especially temporary index lists in OMT mark deletion.

## Important APIs, Types, And Functions
`toku::GrowableArray<T>` exposes `init`, `deinit`, `fetch_unchecked`, `store_unchecked`, `push`, `get_size`, and `memory_size`.

## Control Flow
`init` zeroes the pointer and sizes. `push` doubles capacity when full, using `XREALLOC_N`, then stores the new value. `deinit` frees the backing array. Fetch/store are unchecked except for a paranoid invariant in store.

## State And Persistence Behavior
State is a heap buffer, element count, and capacity. Nothing persists. Elements are copied by assignment and no element destructors are run explicitly.

## Dependencies And Integration Points
Uses Toku allocation wrappers and invariant macros from portability headers. OMT uses it to collect marked indexes before deleting them.

## Risks And Edge Cases
The class is only safe for trivially managed values; it does not construct or destroy elements like `std::vector`. `fetch_unchecked` has no bounds check. Callers must remember `init` and `deinit`.

## Test Signals
Indirect OMT mark deletion tests exercise growth and cleanup. Memory instrumentation can detect forgotten `deinit` calls or unsafe element types.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/growable_array.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/memarena.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/memarena.cc

## Purpose
Implements a simple arena allocator for objects that are allocated many times, never moved, and freed together.

## Important APIs, Types, And Functions
Implements `memarena::create`, `destroy`, `malloc_from_arena`, `move_memory`, `total_memory_size`, `total_size_in_use`, `total_footprint`, and `chunk_iterator` operations. Internal helpers include `round_to_page` and the `MEMARENA_MAX_CHUNK_SIZE` cap.

## Control Flow
Allocations come from the current chunk until it lacks space. The old current chunk is moved into `_other_chunks`, cumulative size/footprint counters are updated, and a new page-rounded chunk is allocated with exponential growth capped at 64 MiB and at least the requested size. `move_memory` appends all source chunks to the destination and clears the source.

## State And Persistence Behavior
The arena stores heap chunks, used byte counts, allocated sizes, and cumulative accounting. It is transient and freed by `destroy` or transferred by `move_memory`.

## Dependencies And Integration Points
Uses Toku memory wrappers and `toku_memory_footprint`. Locktree structures use memarena-style allocation for grouped transient records and buffers.

## Risks And Edge Cases
There is no per-allocation free, no alignment adjustment beyond whatever chunk base provides, and no constructor/destructor handling. `round_to_page` assumes nonzero sizes. `move_memory` transfers ownership completely, so using source allocations after destination destruction is unsafe.

## Test Signals
Arena unit tests should cover growth, chunk iteration, move ownership, size accounting, and large allocation page rounding. Higher-level leak tests catch missing `destroy`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/memarena.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/memarena.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/memarena.h

## Purpose
Declares the `memarena` arena allocator and its chunk iterator.

## Important APIs, Types, And Functions
Public methods are `create`, `destroy`, `malloc_from_arena`, `move_memory`, `total_memory_size`, `total_size_in_use`, `total_footprint`, and nested `chunk_iterator::{current,next,more}`. Internal `arena_chunk` stores `buf`, `used`, and `size`.

## Control Flow
The header defines construction defaults and the iterator's conceptual order: `_current_chunk` is represented by index `-1`, followed by `_other_chunks`.

## State And Persistence Behavior
The object owns all chunk memory until destroyed or moved. State is in memory only.

## Dependencies And Integration Points
Included by locktree utility code needing stable addresses and bulk-free behavior. `standalone_port.cc` provides the memory footprint helper used by the implementation.

## Risks And Edge Cases
Manual `create`/`destroy` lifetime is required despite a C++ constructor. The iterator exposes raw memory plus used byte counts and depends on the arena remaining alive and unchanged. It is not thread-safe.

## Test Signals
Header contract is validated by implementation tests and by any locktree path that copies or iterates arena chunks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/memarena.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/omt.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/omt.h

## Purpose
Declares Toku's Order Maintenance Tree, a mutable ordered sequence with index-based operations, Heaviside-function searches, optional mark bits, and split/merge support.

## Important APIs, Types, And Functions
`toku::omt<omtdata_t, omtdataout_t, supports_marks>` exposes creation from empty or sorted arrays, split, merge, clone, clear, destroy, `size`, `insert`, `insert_at`, `set_at`, `delete_at`, range iteration, pointer iteration, fetch, `find_zero`, directional `find`, `memory_size`, and mark-specific `iterate_and_mark_range`, `iterate_over_marked`, `delete_all_marked`, `verify_marks_consistent`, and `has_marks`. Internal templates define subtree handles and nodes, stealing high bits for mark state when enabled.

## Control Flow
The public API presents a sequence abstraction. Searches rely on caller-provided monotonic sign functions, supporting exact, predecessor, and successor lookup. Mark-enabled trees force tree representation and use node/subtree bits to mark visited ranges and later delete marked nodes.

## State And Persistence Behavior
OMT state is in memory and alternates between array and tree representations. Array state tracks `start_idx`, `num_values`, and `values`; tree state tracks root, next free node index, and node array. No values pointed to by stored pointers are freed by `destroy`.

## Dependencies And Integration Points
Depends on Toku portability macros, race annotations, and `GrowableArray`. Locktree internals use OMTs for ordered collections such as transaction IDs, range records, and tree bookkeeping.

## Risks And Edge Cases
The API requires POD-like values and manual lifetime management. Search correctness depends on the supplied Heaviside function being monotonic. Mark bits are intentionally racy in limited cases and require exclusive access for verification and most mutation. The maximum node index is constrained by bit stealing when marks are enabled.

## Test Signals
Useful tests cover sorted creation, insert/delete/fetch by index, predecessor/successor searches, split/merge, conversion between array and tree forms, mark iteration/deletion, and memory-size accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/omt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/omt_impl.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/omt_impl.h

## Purpose
Implements the OMT template declared in `omt.h`, including representation switching, balanced tree rebuilds, index arithmetic, binary searches, and mark cleanup.

## Important APIs, Types, And Functions
Implements all public `omt` methods plus internal helpers such as `create_internal`, `maybe_resize_array`, `convert_to_array`, `convert_to_tree`, `rebuild_from_sorted_array`, `insert_internal`, `delete_internal`, `iterate_internal`, `rebalance`, `find_internal_zero`, `find_internal_plus`, and `find_internal_minus`.

## Control Flow
Small append/prepend-like operations can stay in array form; middle insert/delete or mark support converts to tree form. Tree nodes store subtree weights, so index operations descend by comparing the target index with left weight. Rebalancing flattens a subtree to an index array and rebuilds it around median nodes. Root rebalance can convert through array form. Search in array mode uses binary search; tree mode recursively follows monotonic sign transitions.

## State And Persistence Behavior
State remains entirely in heap arrays owned by the OMT. `clear` resets counts without freeing capacity, while `destroy` frees the active representation. Tree `node_free` does not reuse nodes immediately; capacity pressure can force conversion/rebuild.

## Dependencies And Integration Points
Uses DB error constants such as `DB_KEYEXIST` and `DB_NOTFOUND`, Toku allocation wrappers, and invariant macros. OMT behavior directly affects locktree range ordering, owner lists, and escalation structures.

## Risks And Edge Cases
Mutation while marks exist is guarded by `barf_if_marked`, so callers must delete or clear marks before structural changes. `iterate_ptr` asserts callback success rather than propagating errors. Value memory is shallow-copied; pointer payload ownership is external. Recursive tree operations can be sensitive to corrupted weights.

## Test Signals
High-value tests include randomized comparison against `std::vector`, exact index validation after every mutation, mark consistency checks, rebuild/rebalance coverage, and binary search behavior for all sign-pattern cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/omt_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/partitioned_counter.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/partitioned_counter.h

## Purpose
Declares a high-throughput counter abstraction designed for frequent increments and infrequent reads by partitioning counts per thread.

## Important APIs, Types, And Functions
The C API defines opaque `PARTITIONED_COUNTER` and functions `create_partitioned_counter`, `destroy_partitioned_counter`, `increment_partitioned_counter`, `read_partitioned_counter`, `partitioned_counters_init`, and `partitioned_counters_destroy`.

## Control Flow
This header only declares behavior. Comments describe the intended flow: increments update thread-local state without a shared lock or atomic operation; reads sum live thread-local counters and a dead-thread aggregate populated by pthread-key destructors.

## State And Persistence Behavior
Counters are in-memory, monotonic 64-bit values. No persistence is involved.

## Dependencies And Integration Points
`status.h` can allocate partitioned counters for `STATUS_PARCOUNT` rows. Locktree status counters are exposed through RocksDB lock manager status APIs.

## Risks And Edge Cases
Reads may be slightly stale by design. Overflow is caller-prohibited. Because this file only declares the API, link-time availability of the implementation is required when status rows actually allocate partitioned counters.

## Test Signals
Expected tests include increment/read correctness, thread teardown aggregation, performance comparisons, and init/destroy ordering around static objects.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/partitioned_counter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/status.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/status.h

## Purpose
Defines `TOKUFT_STATUS_INIT`, a macro for initializing Toku engine status rows used by locktree status reporting.

## Important APIs, Types, And Functions
The macro sets row key name, column name, type, legend, include policy, and creates a partitioned counter when the status type is `STATUS_PARCOUNT`.

## Control Flow
The macro writes metadata into `array.status[k]`, applies compile-time assertions to catch invalid column-name use, sets the include mask, and conditionally calls `create_partitioned_counter`.

## State And Persistence Behavior
It initializes in-memory status row metadata and optional counter objects. There is no persistence.

## Dependencies And Integration Points
Includes `partitioned_counter.h` and is used by `LTM_STATUS_S::init()` in `standalone_port.cc`. RocksDB's range-tree manager reads initialized rows for escalation count, wait count, and current lock memory.

## Risks And Edge Cases
Macro arguments are evaluated in-place and depend on surrounding type definitions from Toku status headers. Partitioned counters allocated here must eventually be destroyed, but the standalone destroy path currently has a TODO.

## Test Signals
Status initialization tests should verify row names and counter allocation. Range lock status APIs provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/range_tree_lock_manager.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/range_tree_lock_manager.cc

## Purpose
Implements RocksDB's `RangeTreeLockManager`, a non-Windows range lock manager backed by the imported Toku locktree library.

## Important APIs, Types, And Functions
Defines `NewRangeLockManager`, endpoint serialization/deserialization, `TryLock`, two `UnLock` overloads, `CompareDbtEndpoints`, deadlock buffer accessors, escalation callbacks, column-family add/remove, locktree lookup caching, status reporting, and lock status dumping.

## Control Flow
`TryLock` serializes start/end endpoints into DBTs, obtains the column-family locktree, configures a `toku::lock_request`, installs a deadlock path callback, starts the request, waits with the transaction lock timeout converted to milliseconds, clears waiting state, destroys the request, and maps Toku return codes to RocksDB `Status`. Waiting callbacks push waitee IDs into `PessimisticTransaction::SetWaitingTxn`. Unlock by key releases a single point-like range; unlock by tracker delegates to `RangeTreeLockTracker`.

## State And Persistence Behavior
Lock state lives in Toku locktrees owned by `locktree_manager`. Per-CF locktrees are stored in `ltree_map_` and cached per thread with `ThreadLocalPtr`. Deadlock paths are retained in an in-memory ring buffer. No lock state is durable.

## Dependencies And Integration Points
Integrates `RangeLockManagerBase`, `RangeLockManagerHandle`, `PessimisticTransaction`, `TransactionDBMutexFactory`, `ThreadLocalPtr`, RocksDB comparators, sync points, and Toku `locktree`, `lock_request`, and `range_buffer`. `AddColumnFamily` supplies the comparator context used by locktree ordering.

## Risks And Edge Cases
`GetLockTreeForCF` may return null for removed or missing column families; callers assume it is valid in lock/unlock paths. Dropping a column family while transactions still hold locks is explicitly unresolved. Reverse comparator handling only flips suffix/tie cases, while non-tie compare returns raw comparator results. Non-exclusive lock requests are passed as reads, despite header comments saying only exclusive locks are currently supported.

## Test Signals
`range_locking_test.cc` sync points cover waiting/deadlock flows. Useful signals include timeout status, deadlock buffer contents, wait metadata, lock status dumps, escalation counter increments, CF cache invalidation, and endpoint ordering with timestamp-aware comparators.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/range_tree_lock_manager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/range_tree_lock_manager.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/range_tree_lock_manager.h

## Purpose
Declares the RocksDB range lock manager implementation that adapts Toku locktree to the `LockManager` and `RangeLockManagerHandle` interfaces.

## Important APIs, Types, And Functions
`RangeTreeLockManager` exposes column-family registration, deadlock buffer APIs, `TryLock`, unlock overloads, lock memory limits, status getters, point/range support flags, lock tracker factory access, `GetLockTreeForCF`, and escalation barrier configuration. It also declares endpoint serialization and wait callback helpers.

## Control Flow
The header defines the ownership model: locktrees are stored as `shared_ptr` values with a custom deleter that calls `locktree_manager::release_lt`; map access is guarded by `ltree_map_mutex_`; thread-local caches accelerate lookups.

## State And Persistence Behavior
Persistent storage is not involved. In-memory state includes the locktree manager, CF map, TLS cache, deadlock buffer, mutex factory, and escalation barrier function.

## Dependencies And Integration Points
Depends on RocksDB transaction lock manager interfaces and Toku locktree headers. The `RangeTreeLockTrackerFactory` returned here ensures transactions use range buffers that Toku can consume during release.

## Risks And Edge Cases
The class is compiled out on Windows. The no-op range-specific unlock overload means range release depends on tracker-based transaction cleanup. Users must call `AddColumnFamily` before locking a CF.

## Test Signals
Compile coverage verifies interface conformance. Runtime tests should verify factory creation, CF add/remove, memory-limit plumbing, deadlock buffer resizing, and tracker factory compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/range_tree_lock_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/range_tree_lock_tracker.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/range_tree_lock_tracker.cc

## Purpose
Implements transaction-side tracking of range-tree locks so a transaction can release all Toku locktree ranges it owns.

## Important APIs, Types, And Functions
Implements `RangeTreeLockTracker::Track` for point and range requests, `GetPointLockStatus`, `Clear`, `RangeLockList::Append`, `ReleaseLocks`, and `ReplaceLocks`.

## Control Flow
Track methods serialize RocksDB point/range endpoints into DBTs and append them to a per-CF `toku::range_buffer`. `ReleaseLocks` sets `releasing_locks_` under mutex, then releases each non-empty buffer through the matching locktree, resets the buffer, retries pending lock requests, clears all buffers, and clears the releasing flag. `ReplaceLocks` is called from escalation; it skips updates during release, otherwise replaces the buffer for the escalated locktree with the locktree's new range list.

## State And Persistence Behavior
State is a map from column-family ID to `shared_ptr<toku::range_buffer>`, plus a mutex and atomic release flag. It is entirely in-memory and owned by the transaction lock tracker.

## Dependencies And Integration Points
Depends on `RangeTreeLockManager` for locktree lookup and wait callback retry, `serialize_endpoint` for DBT-compatible keys, `PessimisticTransaction`, and Toku `range_buffer` iteration.

## Risks And Edge Cases
`ReplaceLocks` assumes a buffer entry already exists for the CF and dereferences it without checking. The release path intentionally drops the mutex while walking locktrees to avoid lock-order deadlocks, relying on `releasing_locks_` to make escalation callbacks no-op. If `GetLockTreeForCF` returns null during release, the code would dereference null.

## Test Signals
Tests should observe that tracked point/range locks are released, waiting requests are retried, escalation replaces tracked ranges, and concurrent release/escalation avoids deadlock.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/range_tree_lock_tracker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/range_tree_lock_tracker.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/range_tree_lock_tracker.h

## Purpose
Declares the `LockTracker` implementation paired with `RangeTreeLockManager`.

## Important APIs, Types, And Functions
`RangeLockList` owns per-CF `toku::range_buffer`s and declares `Append`, `ReleaseLocks`, and `ReplaceLocks`. `RangeTreeLockTracker` implements `Track` for point and range requests, lock support flags, unsupported untrack/merge/subtract/savepoint methods, `Clear`, point status, release and replacement forwarding. `RangeTreeLockTrackerFactory` creates tracker instances.

## Control Flow
The header documents the concurrency model: append and release are transaction-owner operations, while replace can be called from other threads during lock escalation and is synchronized.

## State And Persistence Behavior
Tracker state is transient transaction memory. It may differ briefly from locktree contents because acquisition, release, and escalation are concurrent; the comments state this is harmless for current behavior.

## Dependencies And Integration Points
Depends on RocksDB lock tracker interfaces, pessimistic transaction types, mutex utilities, and Toku locktree/range_buffer. The range lock manager advertises this factory through `GetLockTrackerFactory`.

## Risks And Edge Cases
Savepoints, untracking, merging, and subtraction are unsupported, so partial unlock semantics are limited. `IsPointLockSupported()` returns false for the tracker even though the manager can reduce point locks to ranges.

## Test Signals
Factory tests should verify a range-capable tracker is created. Transaction tests should cover full clear/release behavior and unsupported operations returning no-op or not-tracked statuses.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/range_tree_lock_tracker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction.cc

## Purpose
Implements RocksDB optimistic transactions, which track read/write keys and validate conflicts only at commit time instead of taking pessimistic locks during operations.

## Important APIs, Types, And Functions
Implements constructor, `Initialize`, `Reinitialize`, destructor, `Prepare`, `Commit`, `CommitWithSerialValidate`, `CommitWithParallelValidate`, `Rollback`, `TryLock`, `CheckTransactionForConflicts`, and `SetName`. `OptimisticTransactionCallback` invokes validation from the writer callback path.

## Control Flow
`TryLock` does not acquire a real lock. It sets a snapshot if needed, chooses the snapshot sequence or latest sequence, and records the key in the point lock tracker. `Commit` dispatches by validation policy. Serial validation uses `DBImpl::WriteWithCallback`, causing conflict checks on the writer thread before applying the write batch. Parallel validation locks deterministic OCC hash buckets for all tracked keys, checks conflicts cache-only, writes the batch, and unlocks with `Defer`.

## State And Persistence Behavior
Transaction state is inherited from `TransactionBaseImpl`: write batch, tracked locks, snapshot, and options. Successful commit writes the batch to RocksDB and clears transaction state. Rollback only clears local state. No prepared or named optimistic transaction state exists.

## Dependencies And Integration Points
Uses `OptimisticTransactionDBImpl`, `DBImpl`, `TransactionUtil::CheckKeysForConflicts`, `PointLockTrackerFactory`, `WriteCallback`, and OCC lock buckets. Conflict detection depends on memtable history retained by the DB options.

## Risks And Edge Cases
Two-phase commit and transaction names are unsupported. Cache-only validation can return retry-like failures if history is insufficient. Parallel validation locks raw mutex pointers and notes exception safety concerns. `exclusive` is tracked but not used for immediate locking.

## Test Signals
`optimistic_transaction_test.cc` should cover write-write and read-write conflicts, serial vs parallel validation, old transaction reuse, rollback clearing, unsupported prepare/name, and insufficient history behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction.h -->
# sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction.h

## Purpose
Declares the `OptimisticTransaction` class and its commit-time validation callback.

## Important APIs, Types, And Functions
`OptimisticTransaction` derives from `TransactionBaseImpl` and declares construction, `Reinitialize`, `Prepare`, `Commit`, `Rollback`, `SetName`, protected `TryLock`, private `Initialize`, `CheckTransactionForConflicts`, `Clear`, `UnlockGetForUpdate`, and commit helpers for serial and parallel validation. `OptimisticTransactionCallback` derives from `WriteCallback`.

## Control Flow
The declaration establishes that get-for-update unlock is a no-op because no real locks are acquired. Commit logic is split into policy-specific helpers, and validation can be injected into the write path through `OptimisticTransactionCallback`.

## State And Persistence Behavior
The class stores a pointer to its owning `OptimisticTransactionDB` and inherits all mutable transaction state from `TransactionBaseImpl`. No extra durable fields are introduced.

## Dependencies And Integration Points
Includes RocksDB DB, snapshot, transaction, write batch, and utility transaction headers. It is instantiated by `OptimisticTransactionDBImpl::BeginTransaction`.

## Risks And Edge Cases
The `txn_db_` pointer is const and marked unused in the field macro but is required for commit policy dispatch. Copying is disabled. External callers should not expect pessimistic lock release or prepare/name support.

## Test Signals
Compile and API tests validate override conformance. Behavioral tests should focus on commit policy dispatch and no-lock semantics for get-for-update.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction_db_impl.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction_db_impl.cc

## Purpose
Implements construction and opening of `OptimisticTransactionDBImpl` and creation/reuse of optimistic transaction objects.

## Important APIs, Types, And Functions
Defines `MakeSharedOccLockBuckets`, `OptimisticTransactionDBImpl::BeginTransaction`, three `OptimisticTransactionDB::Open` overloads, and `ReinitializeTransaction`.

## Control Flow
`MakeSharedOccLockBuckets` selects cache-aligned or regular bucket mutex storage. `BeginTransaction` either reinitializes an old transaction or allocates a new `OptimisticTransaction`. The main `Open` overload copies column-family descriptors, enables memtable history by setting `max_write_buffer_size_to_maintain = -1` where unset, opens a base `DB`, and wraps it in `OptimisticTransactionDBImpl`.

## State And Persistence Behavior
Opening persists normal RocksDB DB state through `DB::Open`; the wrapper adds in-memory OCC validation policy and bucket locks. Reusing a transaction clears/reinitializes local transaction state rather than creating durable metadata.

## Dependencies And Integration Points
Uses `DB::Open`, `DBOptions`, `ColumnFamilyDescriptor`, public optimistic transaction DB APIs, and `OptimisticTransaction`. Memtable history configuration is crucial for later conflict validation.

## Risks And Edge Cases
The open path mutates copied options, not caller objects, which is correct but can surprise tests inspecting original options. Existing nonzero history settings are preserved even if too small for workloads. `old_txn` reuse asserts the dynamic type in `ReinitializeTransaction`.

## Test Signals
Tests should verify default-CF open, multi-CF open, history option adjustment, old transaction reuse, and shared/cache-aligned bucket creation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction_db_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction_db_impl.h -->
# sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction_db_impl.h

## Purpose
Declares the concrete optimistic transaction DB wrapper and OCC lock bucket implementations used for parallel validation.

## Important APIs, Types, And Functions
`OccLockBucketsImplBase` extends public `OccLockBuckets` with `GetLockBucket`. `OccLockBucketsImpl<cache_aligned>` stores striped mutexes and reports memory usage. `OptimisticTransactionDBImpl` declares `BeginTransaction`, `DeleteRange`, `Write`, `GetValidatePolicy`, `GetLockBucket`, and private `ReinitializeTransaction`.

## Control Flow
The constructor records the validation policy and, for parallel validation, adopts shared lock buckets from options or creates default buckets with at least 16 stripes. `Write` rejects batches containing range deletes before delegating. `DeleteRange` is always unsupported.

## State And Persistence Behavior
The wrapper owns a base DB through `OptimisticTransactionDB`, a shared pointer to bucket locks when needed, and an immutable validation policy. Bucket locks are in-memory synchronization only.

## Dependencies And Integration Points
Depends on public optimistic transaction DB options, `Striped`, `CacheAlignedWrapper`, mutex utilities, and cast helpers. `OptimisticTransaction::CommitWithParallelValidate` calls `GetLockBucket` for every tracked key.

## Risks And Edge Cases
For serial validation, `bucketed_locks_` remains null and must not be used. Range deletion is rejected because optimistic conflict tracking is point-key based. Shared lock buckets allow cross-DB coordination only when users intentionally provide the same bucket object.

## Test Signals
Tests should cover memory usage reporting, shared bucket reuse, cache-aligned and regular bucket modes, parallel validation bucket locking, and range-delete rejection in both direct and batch writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction_db_impl.h -->
