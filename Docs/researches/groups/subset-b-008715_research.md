# subset-b-008715 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_locking_test.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_locking_test.cc

## Purpose
This non-Windows gtest file exercises RocksDB's range-lock manager through `TransactionDB` and the point-lock-manager compatibility test suite. It validates that range locks conflict with overlapping range and point locks, work under non-default comparators, expose lock-status data, count waits, support waiter access/retry, and trigger lock escalation when enabled.

## Important APIs, Types, And Functions
`RangeLockingTest` owns a temporary `TransactionDB`, `Options`, `TransactionDBOptions`, and a `RangeLockManagerHandle` created by `NewRangeLockManager(nullptr)`. `NewTxn()` wraps `BeginTransaction()` and casts to `PessimisticTransaction`.

The tests cover `Transaction::GetRangeLock()`, `GetForUpdate()`, `Put(..., assume_tracked=true)`, `Commit()`, `Rollback()`, `RangeLockManagerHandle::GetStatus()`, `SetMaxLockMemory()`, `SetEscalationBarrierFunc()`, and `GetRangeLockStatusData()`. `PointLockManagerTestExternalSetup()` adapts `AnyLockManagerTest` to use the range lock manager's point-lock facade.

## Control Flow
The fixture recreates a DB for each test, opens it with `txn_db_options.lock_mgr_handle`, then tests run conflicting transaction sequences. Comparator tests destroy and reopen the DB with reverse-bytewise or timestamp-aware comparators. The lock-wait tests use `SyncPoint` callbacks and a background `port::Thread` to hold a waiter inside range-lock code while another transaction releases locks.

## State And Persistence Behavior
The DB directory is per-thread temporary state and is destroyed in setup and teardown. Locks are in-memory transaction state; tests roll back or commit and delete transactions explicitly. No test asserts durable data beyond using puts to force lock paths.

## Dependencies
The file depends on RocksDB transaction APIs, DB options, `db_impl`, `testutil`, `AnyLockManagerTest`, `TransactionDBMutexFactoryImpl`, `SyncPoint`, and comparator test helpers. The whole file is skipped on Windows because the range-lock tree is not supported there.

## Integration Points
This is the main test signal for the range lock manager integrated with RocksDB's pessimistic transaction layer. It also instantiates the generic point lock manager behavior suite against `NewRangeLockManager(...)->getLockManager()`, making range-lock implementation changes visible to point-lock callers.

## Risks And Edge Cases
The escalation tests are skipped under ThreadSanitizer feature detection and by default on compilers without `__has_feature`, so escalation coverage may be absent in many builds. Lock timeout assertions can be timing-sensitive. Comparator regressions are high risk because range endpoints are raw DBTs without timestamps but must honor user comparator ordering.

## Test Signals
Direct signals include conflicts, reverse comparator length-disparity ordering, timestamp comparator `CompareWithoutTimestamp` behavior, snapshot validation busy status, status reporting for multiple transactions, wait counter increments, waiter wakeup/retry, and generic point-lock behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_locking_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/db.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/db.h

## Purpose
`db.h` is a compact BerkeleyDB/PerconaFT compatibility shim used by the vendored range-tree lock code. It defines the DBT key container, legacy engine-status row shape, and numeric error/flag constants expected by the locktree sources.

## Important APIs, Types, And Functions
`DBT` is forward-declared and then defined as `__toku_dbt { void *data; size_t size; size_t ulen; uint32_t flags; }`. `simple_dbt` is present but marked unused. `TOKU_ENGINE_STATUS_ROW_S` models status rows with `keyname`, `columnname`, `legend`, display/include enums, and a union of value forms.

Constants include `DB_LOCK_DEADLOCK`, `DB_LOCK_NOTGRANTED`, `DB_NOTFOUND`, `DB_KEYEXIST`, DBT allocation flags, and `TOKUDB_OUT_OF_LOCKS`. `lock_wait_callback` is a two-transaction callback typedef.

## Control Flow
There is no runtime control flow. This header supplies ABI-like names and status/error values consumed by locktree, OMT, DBT helpers, and status plumbing.

## State And Persistence Behavior
No state is owned here. The DBT struct is a borrowed or caller-owned buffer descriptor unless helper code clones or frees it. Status row values are filled elsewhere by `LTM_STATUS_S` and the manager.

## Dependencies
Only `<stdint.h>` and `<sys/types.h>` are included. Many downstream files assume this header's constants match the old PerconaFT convention and map them to RocksDB statuses at higher layers.

## Integration Points
`comparator.h`, `locktree.h`, `range_buffer`, wait-graph code, and OMT-backed containers use these types and constants. It is a narrow compatibility boundary between RocksDB transaction code and imported PerconaFT range-lock internals.

## Risks And Edge Cases
Changing numeric error codes can break callers that translate legacy return codes. `DBT::data` is mutable even in logically const use, so ownership and constness must be enforced by convention. `ulen` and `flags` are only partially meaningful in this port.

## Test Signals
Compilation of the range-tree subtree is the primary signal. Runtime coverage comes indirectly from range-lock tests that exercise `DB_LOCK_NOTGRANTED`, `DB_LOCK_DEADLOCK`, and DBT endpoint comparisons.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/ft/comparator.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/ft/comparator.h

## Purpose
`comparator.h` wraps a legacy Fractal Tree key comparison callback in `toku::comparator`, adding support for negative and positive infinity DBTs and carrying an optional memcmp magic byte.

## Important APIs, Types, And Functions
`ft_compare_func` is the callback signature `int(void*, const DBT*, const DBT*)`. Free declarations include `toku_keycompare()` and default-visible `toku_builtin_compare_fun()`.

`toku::comparator` exposes `create()`, `inherit()`, `create_from()`, `destroy()`, `get_compare_func()`, `get_memcmp_magic()`, `valid()`, and `operator()(const DBT*, const DBT*)`. `MEMCMP_MAGIC_NONE` disables the magic shortcut.

## Control Flow
`operator()` first routes any infinite endpoint through `toku_dbt_infinite_compare()`. If memcmp magic is configured and both DBTs carry it, the code asserts because this RocksDB port expects not to take that branch, but still contains the legacy built-in compare call. Otherwise it invokes `_cmp(_cmp_arg, a, b)`.

## State And Persistence Behavior
The object stores only the callback pointer, callback argument, and magic byte. It does not own comparator argument memory; callers must ensure the underlying comparator context outlives the locktree.

## Dependencies
It includes DBT compatibility, memory/assert macros, and DBT helper functions from `util/dbt.h`. The actual RocksDB comparator adaptation lives outside this header.

## Integration Points
`keyrange`, `treenode`, `locktree`, and `locktree_manager::get_lt()` depend on this wrapper for every endpoint ordering decision. Range-lock comparator tests specifically protect reverse comparator and timestamp comparator behavior through the adapter using this surface.

## Risks And Edge Cases
Comparator lifetime is external and easy to violate. The memcmp magic branch asserts, so enabling it inadvertently would abort debug builds. Infinite DBTs must be distinguishable by pointer/helper predicates or range ordering breaks.

## Test Signals
`RangeLockWithReverseComparator` and `RangeLockWithTimestampComparator` are the strongest direct signals. Tree insertion, overlap, escalation, and release tests indirectly cover ordinary and infinite endpoint comparisons.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/ft/comparator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/ft/ft-status.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/ft/ft-status.h

## Purpose
`ft-status.h` declares the locktree-manager status table used to export memory, escalation, pending request, single-transaction optimization, and wait counters from the range-lock subsystem.

## Important APIs, Types, And Functions
`LTM_STATUS_S` enumerates rows from `LTM_SIZE_CURRENT` through `LTM_LONG_WAIT_ESCALATION_TIME`, with `LTM_STATUS_NUM_ROWS` as the bound. It stores `TOKU_ENGINE_STATUS_ROW_S status[...]`, has `init()` and `destroy()`, and tracks `m_initialized`.

`LTM_STATUS` is a pointer alias. `ltm_status` is an extern singleton, `LTM_STATUS_VAL(x)` indexes numeric status values, and `toku_status_init()` / `toku_status_destroy()` are thin lifecycle declarations.

## Control Flow
This header has no implementation control flow. `locktree_manager::get_status()` calls `ltm_status.init()`, fills `LTM_STATUS_VAL(...)` fields, and assigns the singleton to the caller's status pointer.

## State And Persistence Behavior
The status rows are process-local telemetry. They are recomputed from in-memory manager and locktree counters and are not persisted. `m_initialized` prevents repeated row metadata setup in the implementation.

## Dependencies
It depends on `db.h`, race-tool annotations, and the local status utility. The status row shape intentionally mirrors PerconaFT/TokuDB interfaces even though RocksDB exposes a smaller public status struct elsewhere.

## Integration Points
`manager.cc` writes these rows; `treenode.h` includes this header for substituted transaction/status types. Range-lock manager handle status methods ultimately surface subsets of these counters to RocksDB tests and callers.

## Risks And Edge Cases
The singleton makes status collection global, so callers should treat it as a snapshot buffer rather than independent per-manager storage. New counters need enum, row initialization, and manager fill logic kept in sync.

## Test Signals
`BasicLockEscalation`, `LockWaitCount`, and `MultipleTrxLockStatusData` exercise corresponding memory, escalation, and wait/status surfaces indirectly.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/ft/ft-status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/concurrent_tree.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/concurrent_tree.cc

## Purpose
`concurrent_tree.cc` implements the lockable range tree wrapper used by `locktree` to store non-overlapping row-lock ranges with per-subtree mutual exclusion.

## Important APIs, Types, And Functions
`concurrent_tree::create()` initializes an always-present root `treenode`; `destroy()`, `is_empty()`, and `get_insertion_memory_overhead()` provide lifecycle and memory accounting. `locked_keyrange::prepare()`, `acquire()`, `release()`, `insert()`, `remove()`, `remove_all()`, and `add_shared_owner()` are the mutable access primitives.

## Control Flow
`prepare()` locks the root and makes the current protected range infinite. `acquire()` narrows protection to the subtree that could contain or overlap the requested `keyrange`: empty root or root overlap stays at root, otherwise it descends with `find_node_with_overlapping_child()`. Inserts either populate an empty root or recurse through `treenode::insert()`. Removes delegate to `treenode::remove()` and handle the special empty-root result.

## State And Persistence Behavior
State is entirely in memory in `m_root` and allocated descendant nodes. The tree owns copied key ranges inside nodes, not persistent DB records. It assumes `destroy()` is called only after the tree is empty.

## Dependencies
It depends on `concurrent_tree.h`, `treenode`, `keyrange`, and comparator support. It is excluded under `OS_WIN`.

## Integration Points
`locktree` prepares/acquires locked keyranges for conflict checks, acquisition, release, dump, STO migration, and escalation. Memory accounting uses `sizeof(treenode)` via `get_insertion_memory_overhead()`.

## Risks And Edge Cases
The API relies on strict prepare/acquire/release sequencing; missing `release()` leaves tree mutexes held. `remove()` assumes the exact range exists. Subtree locking correctness depends on `treenode` preserving non-overlap and balanced child pointers.

## Test Signals
Range-lock conflict, release, escalation, and waiter tests indirectly exercise this file. Dedicated unit tests are referenced through friend declarations but are not in this work item.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/concurrent_tree.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/concurrent_tree.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/concurrent_tree.h

## Purpose
`concurrent_tree.h` declares a range-index abstraction whose nodes store non-overlapping lock ranges and whose `locked_keyrange` guard grants exclusive access to the subtree overlapping a requested range.

## Important APIs, Types, And Functions
`concurrent_tree` exposes `create(const comparator*)`, `destroy()`, `is_empty()`, and `get_insertion_memory_overhead()`. Nested `locked_keyrange` exposes `prepare()`, `acquire()`, `release()`, templated `iterate(F*)`, `add_shared_owner()`, `insert()`, `remove()`, and `remove_all()`.

## Control Flow
The access model is documented in the header: all users serialize at `prepare()`, then either acquire a narrower overlapping range or operate under the root-wide prepared state, then release. `iterate()` traverses the locked subtree and only visits ranges overlapping `m_range`.

## State And Persistence Behavior
The object embeds one root `treenode` so even an empty tree has a mutex. `locked_keyrange` stores pointers to the tree and currently locked subtree plus the represented `keyrange`. No durable storage is involved.

## Dependencies
It includes the comparator wrapper, `keyrange`, and `treenode`. Templates are intentionally expanded through inclusion in `locktree.cc`.

## Integration Points
This is the low-level concurrency primitive below `locktree`. Higher layers use it to make acquisition/release/escalation appear atomic with respect to overlapping ranges while allowing disjoint subtree operations.

## Risks And Edge Cases
The class does not enforce RAII, so exceptions or early returns can leak locks if callers do not release. The contract requires callers to avoid inserting overlapping ranges and to remove only existing exact ranges. Shared-owner updates require an exact keyrange match.

## Test Signals
All range-lock manager tests that acquire conflicting or non-conflicting ranges are integration signals. Structural behavior is also exercised by lock escalation, which iterates and rebuilds the whole tree.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/concurrent_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/keyrange.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/keyrange.cc

## Purpose
`keyrange.cc` implements the `toku::keyrange` endpoint pair used as the ordering key and interval payload in the range-lock tree.

## Important APIs, Types, And Functions
Implemented methods include borrowed creation, deep-copy creation, destruction, `extend()`, `get_memory_size()`, `compare()`, `overlaps()`, `get_infinite_range()`, endpoint accessors, and private copy-management helpers.

## Control Flow
`create()` borrows endpoint DBTs. `create_copy()` deep-copies endpoints, optimizing point ranges by storing one payload and making the right DBT reference the left copy. `compare()` returns `LESS_THAN`, `GREATER_THAN`, `EQUALS`, or `OVERLAPS` by comparing right-vs-left, left-vs-right, then both endpoints. `extend()` replaces left/right copies if the incoming range expands the current bounds.

## State And Persistence Behavior
A keyrange may either borrow endpoint pointers or own DBT copies in `m_left_key_copy` and `m_right_key_copy`. `destroy()` frees owned copies only. Infinite endpoints are represented by shared helper DBTs and are not copied. No disk state is written.

## Dependencies
It depends on the comparator wrapper and DBT helper functions such as `toku_clone_dbt`, `toku_destroy_dbt`, `toku_dbt_equals`, `toku_dbt_is_infinite`, and infinite endpoint factories.

## Integration Points
`treenode` copies keyranges into tree nodes, `locktree` constructs temporary requested/release ranges, and `range_buffer` serializes equivalent endpoints for transaction-owned lock lists and escalation callbacks.

## Risks And Edge Cases
Ownership is subtle: replacing one side of a point range must move the shared copy correctly. `get_memory_size()` ignores the point optimization and malloc overhead by design, so accounting is approximate. Callers must ensure borrowed DBTs outlive temporary operations.

## Test Signals
Comparator-specific range-lock tests cover key ordering. Conflict, consolidation, release, and escalation paths indirectly validate equality, overlap, and extend semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/keyrange.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/keyrange.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/keyrange.h

## Purpose
`keyrange.h` declares a cheap borrowed-or-owned inclusive range abstraction over two DBT endpoints, including support for infinite endpoints and point-range copy optimization.

## Important APIs, Types, And Functions
Public methods are `create()`, `create_copy()`, `destroy()`, `extend()`, `get_memory_size()`, `get_left_key()`, `get_right_key()`, `compare()`, `overlaps()`, and static `get_infinite_range()`. `comparison` describes positional relationship as `EQUALS`, `LESS_THAN`, `GREATER_THAN`, or `OVERLAPS`.

## Control Flow
The header's contract distinguishes borrowed temporary ranges from copied persistent ranges. Tree nodes use copies, while request/release paths often build borrowed ranges around stack or caller-owned DBTs.

## State And Persistence Behavior
The object stores two DBT copies, two optional endpoint pointers, and `m_point_range`. If endpoint pointers are non-null, accessors return borrowed pointers; otherwise they return the owned DBT copies.

## Dependencies
It depends only on `ft/comparator.h`, which brings DBT and helper declarations. Implementation depends on DBT clone/destroy utilities.

## Integration Points
Every tree operation and lock conflict computation relies on this range relationship contract. Lock escalation uses `extend()` to merge adjacent owned ranges and uses accessors when writing callback buffers.

## Risks And Edge Cases
The enum naming is from the perspective of this range relative to the argument and can be easy to misuse. The type has manual lifecycle functions rather than constructors/destructors, so forgetting `destroy()` leaks copied DBTs.

## Test Signals
Range lock acquisition, release, and escalation provide indirect coverage. Unit tests for overlapping/equal ranges would be valuable because errors here corrupt all higher-level conflict decisions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/keyrange.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/lock_request.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/lock_request.cc

## Purpose
`lock_request.cc` implements pending lock acquisition, timed waits, retry/wakeup, deadlock detection, wait reporting, and waiter cancellation for range-lock requests.

## Important APIs, Types, And Functions
Key methods are `create()`, `destroy()`, `set()`, `start()`, `wait()`, `retry()`, `retry_all_lock_requests()`, `retry_all_lock_requests_info()`, `kill_waiter()`, and pending-list helpers. It uses `txnid_set` for conflict sets and `wfg` for deadlock detection.

## Control Flow
`start()` tries `locktree::acquire_write_lock()` or `acquire_read_lock()`. On `DB_LOCK_NOTGRANTED`, it copies endpoint DBTs before sleeping, marks itself pending, inserts into the locktree's sorted pending request list under `m_info->mutex`, and checks for deadlock. `wait()` retries once under the pending mutex, reports waits, then sleeps on an external condition until grant, timeout, or kill callback. Releases call `retry_all_lock_requests()` to coalesce retry work and broadcast successful waiters.

## State And Persistence Behavior
A request transitions through `UNINITIALIZED`, `INITIALIZED`, `PENDING`, `COMPLETE`, and `DESTROYED`. Pending requests own DBT endpoint copies if endpoints are finite. Counters for waits, timeouts, long waits, and wait time accumulate in `lt_lock_request_info`; no persistent state exists.

## Dependencies
It uses RocksDB-provided external mutex/condition wrappers, locktree APIs, transaction IDs, DBT helpers, current-time helpers, wait graph, and OMT sorted arrays.

## Integration Points
Higher-level range-lock manager code constructs these requests when immediate lock acquisition fails. `locktree_manager::iterate_pending_lock_requests()` and `kill_waiter()` inspect or manipulate the same pending request lists.

## Risks And Edge Cases
Pending-list operations assume unique txnid requests per locktree. Deadlock detection only includes transactions that currently have pending lock requests. `toku_external_mutex_trylock()` always locks in this port, so status collection may block despite trylock naming.

## Test Signals
Lock timeout tests, wait counter tests, waiter-access tests, deadlock-oriented point-lock tests through `AnyLockManagerTest`, and kill/wait callback paths are the important signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/lock_request.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/lock_request.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/lock_request.h

## Purpose
`lock_request.h` declares the object that represents one potentially blocking range-lock acquisition and the wait-reporting structures used by callbacks.

## Important APIs, Types, And Functions
`lock_wait_info` records the locktree, waiting transaction, opaque extra pointer, and waited-on transaction IDs; `lock_wait_infos` is a vector of these. `lock_request::type` distinguishes `READ` and `WRITE`. Public APIs cover lifecycle, request reset, `start()`, timed `wait()`, endpoint/txnid accessors, static retry functions, test callbacks, extra access, and waiter killing.

## Control Flow
The documented flow is initialize, set request parameters, start immediate acquisition, optionally do other work, wait on a timed condition if pending, and destroy when no longer pending. Static retry functions are called after lock release to wake newly grantable requests.

## State And Persistence Behavior
Private fields store txnid, conflict txnid, start time, borrowed or copied endpoints, request type, owning `locktree`, completion code, state enum, external condition variable, big-transaction flag, locktree request-info pointer, extra pointer, and optional deadlock callback.

## Dependencies
It includes DBT/status definitions, comparator declarations, external pthread wrappers, `locktree`, `txnid_set`, and `wfg`. It uses `std::vector` and `std::function` via included headers.

## Integration Points
`locktree_manager` exposes pending requests and can kill waiters. RocksDB transaction lock manager code maps lock timeouts and deadlocks from this class into `Status` values.

## Risks And Edge Cases
The class is manually stateful and reusable, so callers must not destroy while pending or reuse without `set()`. Endpoint copies are made only when entering pending state; immediate acquisitions borrow caller DBTs. Test callback hooks can alter timing-sensitive behavior.

## Test Signals
Tests should cover immediate grant, timeout, deadlock, retry-after-release, killed waiter, wait callback contents, and request reuse after completion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/lock_request.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/locktree.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/locktree.cc

## Purpose
`locktree.cc` implements the core range-lock table for one dictionary/column family: immediate lock acquisition, conflict detection, shared read-lock coalescing, transaction lock release, lock dumping, single-transaction optimization, and escalation.

## Important APIs, Types, And Functions
Implemented public methods include `create()`, `destroy()`, reference counting, `acquire_read_lock()`, `acquire_write_lock()`, `get_conflicts()`, `release_locks()`, `escalate()`, userdata accessors, comparator/barrier setters, `dump_locks()`, and dictionary comparison.

Internal helpers include `row_lock`, overlap iteration, `determine_conflicting_txnids()`, memory accounting helpers, `sto_*` single-transaction optimization methods, `acquire_lock_consolidated()`, `remove_overlapping_locks_for_txnid()`, and escalation extraction/rebuild logic.

## Control Flow
Acquisition prepares the rangetree root, attempts STO fast path, then acquires the overlapping subtree. If an identical shared lock is the only overlap, the new owner is added. If overlaps all belong to the same txnid, ranges are merged into one dominating range. Otherwise conflict txnids are returned. Release iterates a transaction's range buffer and removes owned overlapping locks, exiting STO first for partial releases. Escalation locks the full tree, removes locks in batches, merges adjacent compatible locks unless a barrier is present, rebuilds the tree, and calls callbacks per txnid.

## State And Persistence Behavior
State is in-memory: comparator copy, reference count, concurrent tree pointer, userdata, pending request info, STO txnid/buffer/score, escalation barrier, and STO timing counters. Lock state is not persisted; higher layers track transaction-owned ranges separately.

## Dependencies
It depends on `concurrent_tree`, `range_buffer`, `growable_array`, memory macros, time helpers, OMT, transaction IDs, and the manager for memory accounting and callbacks.

## Integration Points
`lock_request` calls acquisition and conflict methods. `locktree_manager` creates, references, destroys, escalates, and reads status from locktrees. RocksDB range-lock manager wraps this object per column family/dictionary.

## Risks And Edge Cases
Memory accounting is approximate and must be balanced on every insert/remove/STO transition. Shared locks are supported only for identical ranges and are not merged during escalation. STO migration can create latency spikes, bounded by buffer size. Barriers must follow comparator ordering.

## Test Signals
Range conflict tests, shared-lock upgrade timeout, lock status dumping, wait counters, basic escalation, escalation barriers, and point-lock compatibility are key signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/locktree.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/locktree.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/locktree.h

## Purpose
`locktree.h` declares the central range-lock abstractions: a manager for all dictionary locktrees, a per-dictionary `locktree`, pending request metadata, status counters, and callback contracts for create/destroy/escalation.

## Important APIs, Types, And Functions
Key types include `DICTIONARY_ID`, `lt_counters`, `lt_lock_request_info`, callback typedefs, `locktree_manager`, and `locktree`. Manager APIs cover lifecycle, memory limit, get/release/reference, status, pending iteration, memory accounting, escalation, and waiter killing. `locktree` APIs cover lifecycle, acquisition, conflict discovery, release, escalation, comparator/barrier setup, status dump, and userdata.

## Control Flow
The header documents manager ownership: callers get a referenced locktree by dictionary ID and later release it; the manager destroys it on final release. Lock acquisition returns immediately with success, `DB_LOCK_NOTGRANTED`, or out-of-locks, while `lock_request` handles waits.

## State And Persistence Behavior
Manager state includes global lock-memory limit/current usage, cumulative counters, callbacks, OMT map, mutexes, and escalator state. `locktree` state includes dictionary ID, comparator, concurrent range tree, pending request info, STO buffer/score, and escalation barrier. All state is process-local.

## Dependencies
It includes atomic support, DBT/status definitions, comparator, external/internal pthread wrappers, time helpers, OMT, `range_buffer`, `txnid_set`, and wait graph declarations.

## Integration Points
This is the imported locktree interface wrapped by RocksDB's `RangeTreeLockManager`. Status and escalation functions feed public range-lock manager handle methods tested in `range_locking_test.cc`.

## Risks And Edge Cases
Reference counting is external and not RAII. Comparator lifetime is guaranteed by higher layers. STO and normal tree lock lists duplicate transaction-owned lock tracking, and comments flag this as a layering issue. `set_max_lock_memory()` rejects lowering below current usage.

## Test Signals
Manager lifecycle, memory limit/escalation, lock acquire/release, pending request iteration, status reporting, and reference-count races are the intended test surfaces.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/locktree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/manager.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/manager.cc

## Purpose
`manager.cc` implements `locktree_manager`, which owns the map of active dictionary locktrees, global lock-memory accounting, coordinated lock escalation, status collection, pending request iteration, and waiter cancellation.

## Important APIs, Types, And Functions
Implemented methods include `create()`, `destroy()`, `get_lt()`, `reference_lt()`, `release_lt()`, memory limit/accounting methods, `check_current_lock_constraints()`, `run_escalation()`, `escalate_all_locktrees()`, `escalate_locktrees()`, `get_status()`, `iterate_pending_lock_requests()`, and `kill_waiter()`. Nested `locktree_escalator` serializes concurrent escalation attempts.

## Control Flow
`get_lt()` locks the manager map, finds or creates a locktree, invokes create callback, and inserts it. `release_lt()` decrements refs, removes the map entry under the mutex if the count reaches zero, accumulates counters, and destroys outside the mutex. Constraint checks run escalation when big transactions exceed half the memory limit or all transactions exceed the limit. Escalation snapshots referenced locktrees, escalates them one by one, releases refs, and records timing/result counters.

## State And Persistence Behavior
All state is in-memory: OMT map, max/current memory, callbacks, mutexes, cumulative counters, and escalation stats. Status collection writes into the global `ltm_status` singleton.

## Dependencies
It uses internal pthread wrappers, OMT, status helpers, `lock_request`, `locktree`, memory macros, and time helpers.

## Integration Points
RocksDB's range lock manager owns one manager and calls into it for per-column-family locktrees, lock memory configuration, status, and waiter cancellation. `locktree` reports memory deltas back to this manager.

## Risks And Edge Cases
Reference-count cleanup is race-sensitive and relies on dictionary IDs never being reused. `get_status()` uses a trylock wrapper that always locks in this port, so status calls may block. Escalation may fail to reduce memory enough, yielding `TOKUDB_OUT_OF_LOCKS`.

## Test Signals
Escalation memory-limit tests, lock wait count/status tests, multiple locktree status reporting, and concurrent open/close stress are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/manager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/range_buffer.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/range_buffer.cc

## Purpose
`range_buffer.cc` implements a compact arena-backed serialization format for transaction-owned key ranges, including exclusive/shared flag storage and point-range compaction.

## Important APIs, Types, And Functions
It implements `record_header` infinity helpers and initialization, iterator record accessors/deserialization, iterator traversal, `create()`, `append()`, `is_empty()`, `total_memory_size()`, `get_num_ranges()`, `destroy()`, `append_range()`, and `append_point()`.

## Control Flow
`append()` stores one copy if endpoints are equal, otherwise stores left and right payloads after a header. `record_header::init()` records infinity flags and key sizes. Iteration uses `memarena::chunk_iterator`; `current()` deserializes the record at the current chunk offset, and `next()` advances by the last record size, moving chunks as needed.

## State And Persistence Behavior
The buffer owns all serialized range bytes in a `memarena` and resets wholesale on `destroy()`. DBT records returned by an iterator point into the current serialized record and are valid only while that record object remains in scope.

## Dependencies
It depends on DBT helpers, memory/assert macros, `memarena`, and fixed-width integer types. It assumes key payload sizes fit in 16-bit header fields.

## Integration Points
Transactions and STO mode use range buffers as lock ownership lists. `locktree::release_locks()` iterates them to release locks, and escalation callbacks receive per-transaction buffers describing replacement ranges.

## Risks And Edge Cases
`MAX_KEY_SIZE` is enforced with invariants, not recoverable errors. Header layout is implicitly serialized in memory and has a commented-out size assertion. Infinite point ranges and right-key-size-zero point records require careful deserialization.

## Test Signals
Range acquisition/release, STO migration, dump/status, and escalation all consume range buffers. Focused tests should cover finite range, finite point, infinite endpoints, chunk transitions, exclusive flag preservation, and maximum key size.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/range_buffer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/range_buffer.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/range_buffer.h

## Purpose
`range_buffer.h` declares an append-only key-range buffer used to store a transaction's lock ranges cheaply and iterate them later for release, STO migration, and escalation callbacks.

## Important APIs, Types, And Functions
`range_buffer` exposes `create()`, `append()`, `is_empty()`, `total_memory_size()`, `get_num_ranges()`, and `destroy()`. Nested `iterator` exposes constructors, `current()`, and `next()`. Nested `iterator::record` exposes left/right DBT accessors, serialized `size()`, `deserialize()`, and `get_exclusive_flag()`.

## Control Flow
The header defines a record format: fixed header followed by left and optional right key payloads. Equal endpoints are point records with a single key payload; full ranges store two payloads. Iteration walks variable-length records across memarena chunks.

## State And Persistence Behavior
State is one `memarena` plus an integer range count. It is transient and destroyed as a unit, not individually freed per range.

## Dependencies
It includes integer headers, DBT helpers, and `memarena`. The implementation also uses memory macros and string copy functions.

## Integration Points
`locktree` uses this for transaction-owned lock records, STO buffer, release lists, and per-transaction escalation output. Higher RocksDB layers may receive buffers through escalation callbacks to update tracked locks.

## Risks And Edge Cases
There is no random deletion or ownership transfer; misuse requires rebuilding. Iteration records expose DBTs pointing into arena memory, so consumers must copy if they outlive iteration. The 64 KiB key size limit is a hard invariant.

## Test Signals
Tests should validate round-trip append/iterate for point and range locks, shared/exclusive flags, infinite endpoints, empty buffers, and memory-size changes used by lock memory accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/range_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/treenode.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/treenode.cc

## Purpose
`treenode.cc` implements the mutex-protected binary search tree node used by `concurrent_tree` to store one non-overlapping range lock plus optional child subtrees.

## Important APIs, Types, And Functions
Implemented methods include mutex wrappers, root lifecycle, `set_range_and_txnid()`, `range_overlaps()`, allocation/free, in-place swap, shared-owner add/remove, search, insert, remove, recursive removal, depth estimate, imbalance checks, rotations, child locking, and child pointer maintenance.

## Control Flow
Search compares the target range with the current range, locks/rebalances the relevant child, and descends until a parent of the overlapping or insertion subtree is found. Insert recurses left/right for non-overlap or adds a shared owner for exact shared-lock equality. Remove either removes this subtree root or recurses to the matching child. `maybe_rebalance()` performs AVL-style single/double rotations when depth estimates exceed thresholds.

## State And Persistence Behavior
Each node owns a copied `keyrange`, transaction owner state, optional shared-owner vector, child pointers with depth estimates, comparator pointer, mutex, root/empty flags, and lock-mode flag. State is in-memory only.

## Dependencies
It uses comparator, keyrange, transaction ID substitution, memory macros, internal pthread wrappers, race-tool annotations, and `TxnidVector`.

## Integration Points
`concurrent_tree::locked_keyrange` delegates all actual tree mutation and traversal to this class. `locktree` depends on correct owner preservation during removal, shared-owner update, and rotations.

## Risks And Edge Cases
Manual lock ordering is delicate; rotations unlock all but the new root and reset valgrind ordering metadata. `swap_in_place()` must move range, txnid, shared flag, and owners together. Shared-owner removal can leave `m_txnid == TXNID_SHARED` with a null owners pointer if invariants are broken.

## Test Signals
Insertion/removal order stress, shared lock duplicate ownership, release of one shared owner, escalation extraction after rotations, and concurrent non-overlapping acquisitions are key tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/treenode.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/treenode.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/treenode.h

## Purpose
`treenode.h` declares the low-level mutable node type backing `concurrent_tree`, including traversal, insertion, removal, shared ownership, per-node locking, and approximate balancing.

## Important APIs, Types, And Functions
Public APIs include root lifecycle, range/txnid setup, state queries, mutex lock/unlock, subtree search, templated `traverse_overlaps()`, `insert()`, `remove()`, and `recursive_remove()`. Private helpers define `child_ptr`, shared-owner operations, extreme-child search, root removal, rebalance operations, allocation/free, and range/owner swapping.

## Control Flow
`traverse_overlaps()` performs in-order traversal while locking each child before recursing and unlocking after. The tree assumes callers hold the current node lock and children are initially unlocked for most operations.

## State And Persistence Behavior
The node contains a `toku_mutex_t`, copied `keyrange`, `TXNID` or `TXNID_SHARED`, shared-lock flag, optional owner vector, left/right children and depth estimates, comparator pointer, and root/empty flags.

## Dependencies
It includes comparator, memory helpers, pthread wrappers, status header, transaction ID substitution, and `keyrange`.

## Integration Points
`concurrent_tree` is the only intended caller; `locktree` observes node data through traversal callbacks. Friend unit-test classes can inspect internals.

## Risks And Edge Cases
This is not a general container: callers must enforce non-overlap and exact-match removal. The templated traversal passes references to internal ranges that must not be used after node deletion. Balance estimates are approximate and updated through child pointers.

## Test Signals
Tree unit tests should cover overlap traversal pruning, exact removal, root emptying, rotations, shared owners, and recursive removal. Range-lock integration tests cover it indirectly.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/treenode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/txnid_set.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/txnid_set.cc

## Purpose
`txnid_set.cc` implements a small sorted transaction-ID set on top of the local OMT container.

## Important APIs, Types, And Functions
`find_by_txnid()` compares transaction IDs. Methods implement `create()`, `destroy()`, `contains()`, `add()`, `remove()`, `size()`, and indexed `get()`.

## Control Flow
`create()` initializes the OMT without allocating an array. Lookup operations use `find_zero` with the comparator. `add()` inserts and accepts duplicate `DB_KEYEXIST`. `remove()` deletes only if found. `get()` fetches by sorted index and returns `TXNID_NONE` only for impossible `EINVAL` fallback.

## State And Persistence Behavior
State is the OMT-held set of TXNIDs. It is transient and must be destroyed manually. Ordering is sorted by numeric transaction ID.

## Dependencies
It includes `txnid_set.h` and `db.h` for return codes. It relies on OMT and invariant macros.

## Integration Points
Conflict collection, wait graph edges, shared-lock owner conflict expansion, and deadlock detection all use `txnid_set`.

## Risks And Edge Cases
The type is POD-style and manual lifecycle must be respected. `get(0)` is assumed valid by callers after conflicts are reported; conflict-producing paths must not leave the set empty.

## Test Signals
Set unit tests should cover duplicate insert, ordered fetch, removal of absent IDs, and empty lazy allocation. Lock timeout/deadlock paths indirectly exercise it.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/txnid_set.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/txnid_set.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/txnid_set.h

## Purpose
`txnid_set.h` declares a POD-compatible set abstraction for transaction IDs used by conflict, owner, and wait-for-graph code.

## Important APIs, Types, And Functions
The class exposes `create()`, `destroy()`, `contains()`, `add()`, `remove()`, `size()`, and `get(i)`. It stores `toku::omt<TXNID> m_txnids` and is guarded by `ENSURE_POD`.

## Control Flow
The API is intentionally simple: callers create the set, add/remove IDs, iterate by index, and destroy the internal OMT. Sorting is provided by implementation comparator functions.

## State And Persistence Behavior
All state is in-memory OMT storage. The set does not own transaction objects, only numeric IDs.

## Dependencies
It includes transaction ID substitution and OMT. `ENSURE_POD` comes through portability/assert infrastructure.

## Integration Points
`locktree::get_conflicts()`, `lock_request::deadlock_exists()`, `wfg::node::edges`, and shared-owner conflict expansion all depend on this type.

## Risks And Edge Cases
Because it is POD-style, constructors are not used; missing `create()` or `destroy()` causes invalid access or leaks. Index iteration assumes stable ordering while no mutation occurs.

## Test Signals
Conflict collection in range-lock tests and deadlock tests are integration coverage. Direct unit tests should validate POD lifecycle and duplicate handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/txnid_set.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/wfg.cc -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/wfg.cc

## Purpose
`wfg.cc` implements a wait-for graph used by `lock_request` to detect transaction deadlocks among pending lock requests.

## Important APIs, Types, And Functions
Implemented methods include `create()`, `destroy()`, `add_edge()`, `node_exists()`, `cycle_exists_from_txnid()`, `apply_nodes()`, `apply_edges()`, node lookup/creation helpers, comparator, and `node::alloc/free`.

## Control Flow
`add_edge(a,b)` creates both nodes if missing and inserts `b` into `a`'s edge set. Cycle detection starts from a target node, depth-first traverses outgoing edges, marks visited nodes to avoid repeated recursion, and reports nodes on the discovered cycle through an optional callback while unwinding.

## State And Persistence Behavior
The graph is transient per deadlock check. It owns OMT nodes; each node owns a `txnid_set` of outgoing edges and a temporary `visited` flag. `destroy()` frees every node and edge set.

## Dependencies
It uses `db.h` error codes, memory macros, OMT, transaction ID sets, and invariants.

## Integration Points
`lock_request::build_wait_graph()` recursively adds edges from the current blocked request and other pending blockers, then calls `cycle_exists_from_txnid()`.

## Risks And Edge Cases
The graph only includes blockers that themselves have pending requests, so it detects wait cycles rather than all conflict relationships. Recursive DFS depth grows with wait-chain length. Reporter callbacks run during traversal and must tolerate partial cycle ordering.

## Test Signals
Deadlock tests should cover simple two-node cycles, longer cycles, acyclic chains, duplicate edges, and reporter callback contents. Range-lock timeout tests exercise the no-cycle path.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/wfg.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/wfg.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/wfg.h

## Purpose
`wfg.h` declares the wait-for graph abstraction used to model "transaction A waits for transaction B" relationships for deadlock detection.

## Important APIs, Types, And Functions
Public APIs are `create()`, `destroy()`, `add_edge()`, `node_exists()`, `cycle_exists_from_txnid()`, `apply_nodes()`, and `apply_edges()`. Private `node` stores a `TXNID`, `txnid_set edges`, and `visited` flag, with allocation/free helpers.

## Control Flow
The graph API is mutable during construction, then traversed for cycle checks or diagnostic iteration. `cycle_exists_from_txnid()` accepts a `std::function<void(TXNID)>` reporter for deadlock detail collection.

## State And Persistence Behavior
State is one OMT of node pointers, each with an edge set. It is manual-lifecycle, POD-enforced, and transient.

## Dependencies
It includes `<functional>`, OMT, and `txnid_set`. Transaction ID definitions arrive through `txnid_set.h`.

## Integration Points
Only lock request deadlock logic should need this class. It is independent of key ranges and relies solely on transaction IDs supplied by conflict discovery.

## Risks And Edge Cases
Manual allocation and POD constraints limit modernization. Any caller that mutates the graph while traversing would violate assumptions. Large wait graphs could recurse deeply.

## Test Signals
Cycle/no-cycle unit tests and lock-request deadlock integration tests are expected. Reporter callback coverage is useful because RocksDB deadlock diagnostics depend on it.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/wfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/memory.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/memory.h

## Purpose
`memory.h` declares PerconaFT-style allocation wrappers, typed allocation macros, memory status reporting, and hooks for replacing allocator functions in tests.

## Important APIs, Types, And Functions
Functions include startup/shutdown, `toku_malloc`, `toku_calloc`, `toku_xmalloc`, `toku_xcalloc`, aligned variants, realloc variants, `toku_free`, usable-size, dup/string helpers, cleanup/check functions, allocator hook setters, status getter, and footprint helpers. Macros such as `XMALLOC`, `XCALLOC`, `XMALLOC_N`, `XCALLOC_N`, `ZERO_STRUCT`, and `CAST_FROM_VOIDP` make typed allocation concise.

## Control Flow
This header only declares behavior and macros. `x*` functions abort or assert on allocation failure, while plain functions return null and set status in the implementation.

## State And Persistence Behavior
The memory subsystem can keep process-local counters in `memory_status`, including counts, requested/used/freed bytes, max usage, failure sizes, allocator version, and mmap threshold. No DB persistence is involved.

## Dependencies
It includes `<stdlib.h>` and `toku_portability.h` for casts, attributes, and portability macros.

## Integration Points
The locktree code uses `XCALLOC`, `XMALLOC`, `XMALLOC_N`, and `toku_free` for nodes, managers, range buffers, and wait graph nodes. OMT and DBT helpers also rely on this allocation layer.

## Risks And Edge Cases
Allocation macros infer type from the destination variable; misuse is compile-time safer than raw malloc but still manual. Replacing allocator hooks can affect all users globally. Status counters may be approximate under concurrency.

## Test Signals
Memory accounting and leak tests, allocation-failure injection, and range-lock create/destroy stress exercise this layer indirectly.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_assert_subst.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_assert_subst.h

## Purpose
`toku_assert_subst.h` replaces PerconaFT's assertion macros with standard C/C++ assertions for the RocksDB port.

## Important APIs, Types, And Functions
It defines `assert_zero`, `invariant`, `invariant_notnull`, `invariant_zero`, lazy/paranoid variants, `ENSURE_POD(type)`, and `get_error_errno()`. In `NDEBUG`, core invariants compile to `(void)(a)`; paranoid variants still assert.

## Control Flow
The macros either evaluate to `assert(...)` checks or no-op casts depending on build mode. `get_error_errno()` asserts `errno` is nonzero and returns it.

## State And Persistence Behavior
There is no state. It only affects debug/release validation behavior.

## Dependencies
It includes `<assert.h>` and `<errno.h>`. `ENSURE_POD` assumes `<type_traits>` is available before use in C++ translation units.

## Integration Points
Nearly every range-tree file uses `invariant*` macros to enforce internal tree, OMT, locking, and memory assumptions.

## Risks And Edge Cases
Important safety checks vanish in release builds for non-paranoid invariants, so callers cannot rely on them for input validation. `ENSURE_POD` can fail compilation when classes gain constructors or non-trivial fields.

## Test Signals
Debug builds are important for catching tree and lock-request invariant violations. Release tests still need behavior checks because many defensive assertions are compiled out.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_assert_subst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_atomic.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_atomic.h

## Purpose
`toku_atomic.h` provides typed wrappers around GCC `__sync_*` atomic builtins with cache-line boundary assertions and poisons direct builtin use after wrapper definitions.

## Important APIs, Types, And Functions
Helpers include `which_cache_line()`, `crosses_boundary()`, `toku_sync_fetch_and_add()`, `toku_sync_add_and_fetch()`, `toku_sync_fetch_and_sub()`, `toku_sync_sub_and_fetch()`, `toku_sync_val_compare_and_swap()`, and `toku_sync_bool_compare_and_swap()`.

## Control Flow
Each wrapper asserts the target object does not cross an assumed 64-byte cache line, then calls the matching `__sync_*` builtin. The final `#pragma GCC poison` list prevents accidental direct builtin calls in files that include this header.

## State And Persistence Behavior
The wrappers mutate caller-owned scalar fields atomically; no persistent state exists. `locktree` uses them for reference counts, memory counters, and STO score updates.

## Dependencies
It includes boolean, size, integer headers and `toku_assert_subst.h`.

## Integration Points
`toku_portability.h` includes this header, so many locktree files receive these wrappers transitively. Manager memory accounting and locktree reference counting are the main users.

## Risks And Edge Cases
The old `__sync_*` builtins are full-barrier primitives and less expressive than modern `std::atomic`. The cache-line assertion is approximate and assumes 64-byte lines. Poisoning can surprise code that includes this header before third-party headers using builtins.

## Test Signals
Concurrent reference-count and memory-accounting stress tests are the best signals. Compilation also verifies no forbidden direct builtins appear after inclusion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_external_pthread.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_external_pthread.h

## Purpose
`toku_external_pthread.h` adapts RocksDB `TransactionDBMutexFactory` mutexes and condition variables to the TokuDB-style external mutex/cond API used for interruptible lock waits.

## Important APIs, Types, And Functions
Aliases define `toku_external_mutex_factory_t`, `toku_external_mutex_t`, and `toku_external_cond_t` as shared pointers to RocksDB mutex/cond types. Inline functions create/destroy, lock/unlock, signal/broadcast, timed wait, and trylock external mutexes/conditions.

## Control Flow
Initialization allocates a RocksDB mutex or condvar from the factory. Timed wait calls `TransactionDBCondVar::WaitFor()` and maps OK to `0`, anything else to `ETIMEDOUT`. `trylock` currently calls blocking `Lock()` and returns `0`.

## State And Persistence Behavior
State is shared-pointer ownership of RocksDB synchronization objects. No persistent state is involved.

## Dependencies
It includes pthread/time headers, RocksDB transaction DB mutex interfaces, and portability macros.

## Integration Points
`lock_request` uses external conditions for potentially long waits so RocksDB can provide custom wait primitives. `lt_lock_request_info` uses external mutexes around pending waiter lists.

## Risks And Edge Cases
`toku_external_mutex_trylock()` is not a true trylock in this port; callers expecting non-blocking behavior may block. The factory pointer must be valid and able to allocate both mutexes and condition variables. Timed-wait error mapping loses error detail.

## Test Signals
Wait timeout, waiter wakeup, killed waiter, and custom `TransactionDBMutexFactoryImpl` tests exercise this wrapper.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_external_pthread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_instrumentation.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_instrumentation.h

## Purpose
`toku_instrumentation.h` supplies no-op or MySQL-backed instrumentation abstractions for mutexes, condition variables, threads, files, and IO used by the imported TokuDB portability layer.

## Important APIs, Types, And Functions
It defines `pfs_key_t`, `toku_instr_object_type`, `TOKU_FILE`, forward declarations for PSI objects and Toku synchronization structs, `toku_instr_key`, `toku_instr_probe_empty`, probe macros, file operation enum, no-op instrumentation structs/functions, and extern instrumentation keys for locktree mutexes and conditions.

## Control Flow
Without `MYSQL_TOKUDB_ENGINE`, constructors and instrumentation begin/end functions are no-ops, and `toku_pthread_create()` delegates directly to `pthread_create()`. With MySQL integration, it includes `toku_instr_mysql.h`.

## State And Persistence Behavior
In the RocksDB build path, instrumentation stores no runtime state beyond placeholder objects. Extern keys are defined elsewhere and identify locktree synchronization objects.

## Dependencies
It includes `<stdio.h>` and, for the non-MySQL path, `<pthread.h>`. It relies on `UU` from portability headers to silence unused parameter warnings.

## Integration Points
Internal pthread wrappers use these hooks to name manager, treenode, request-info, retry, and escalator mutexes/conditions. RocksDB generally receives no performance-schema data from the no-op path.

## Risks And Edge Cases
Most functions are intentionally empty, so performance diagnostics may be absent. `TOKU_PROBE_STOP(p)` expands to `p->stop` rather than a call in this header, which matches legacy expectations but is easy to misuse.

## Test Signals
Compilation is the main direct signal. Synchronization tests indirectly verify that no-op instrumentation does not alter locking behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_instrumentation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_portability.h -->
# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_portability.h

## Purpose
`toku_portability.h` is the central portability include for the range-tree lock code, collecting standard system headers, atomic wrappers, type traits, casting helpers, unused-parameter annotations, and instrumentation declarations.

## Important APIs, Types, And Functions
It defines `constexpr_static_assert`, includes integer/time/stat headers, includes `toku_atomic.h`, conditionally includes `<type_traits>`, defines `CAST_FROM_VOIDP(name,value)`, and defines `UU(x)` as an unused-annotated parameter helper. It then includes `toku_instrumentation.h`.

## Control Flow
There is no runtime control flow. Preprocessor branches adjust `constexpr_static_assert` for clang and choose C++ vs C cast behavior.

## State And Persistence Behavior
No state is stored here. It shapes compilation of the imported locktree sources.

## Dependencies
It includes `<inttypes.h>`, `<stdint.h>`, `<stdio.h>`, `<sys/stat.h>`, `<sys/time.h>`, `<sys/types.h>`, `<unistd.h>`, `toku_atomic.h`, and instrumentation.

## Integration Points
Memory macros use `CAST_FROM_VOIDP`; instrumentation wrappers use `UU`; atomic functions propagate into manager and locktree code. This header is included broadly through `memory.h` and synchronization wrappers.

## Risks And Edge Cases
The `CAST_FROM_VOIDP` macro relies on GNU `__typeof__` in C++ mode. Include order matters because `toku_atomic.h` poisons raw `__sync_*` builtins after defining wrappers. Platform assumptions are POSIX-oriented, matching the non-Windows range-lock support.

## Test Signals
Cross-platform compilation and non-Windows range-lock test builds are the main signals. Windows is explicitly excluded by surrounding source files.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/toku_portability.h -->
