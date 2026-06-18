# subset-b-008685 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/two_level_iterator.cc -->
# sources/storage-engines/rocksdb/table/two_level_iterator.cc

Purpose: implements `NewTwoLevelIterator()` by defining `TwoLevelIndexIterator`, an `InternalIteratorBase<IndexValue>` that flattens a first-level partition index into the concatenated stream of second-level block/index entries. It is RocksDB's partitioned-index traversal helper: the first-level iterator yields `IndexValue` handles, and `TwoLevelIteratorState::NewSecondaryIterator()` materializes the iterator for the selected partition.

Important APIs and control flow: `Seek`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, `Next`, and `Prev` all position the first-level iterator, call `InitDataBlock()`, then position or advance the second-level iterator. `SkipEmptyDataBlocksForward()` and `SkipEmptyDataBlocksBackward()` loop across partitions whose secondary iterator is null or exhausted without error. `status()` prioritizes first-level errors, then second-level errors, then the iterator's saved corruption status.

State and ownership: the object owns `state_`, `first_level_iter_`, and the current `second_level_iter_`; destruction deletes all three through non-arena paths. `data_block_handle_` caches the handle used for the active secondary iterator so `InitDataBlock()` can avoid recreating it when the partition offset has not changed and the existing iterator is not incomplete. No persistent state is written.

Dependencies and integration: depends on RocksDB internal iterator wrappers, `BlockHandle`, `IndexValue`, and table/block format code. The state object is supplied by block-based table code and hides the details of reading partitioned index blocks.

Risks and test signals: the code assumes iterators are not arena-created, so ownership mismatches would cause invalid deletes. `InitDataBlock()` only compares handle offset, so callers must not present distinct partitions with the same offset but different semantics. A null secondary iterator becomes `Corruption("Missing block for partition ...")`. Boundary tests should cover empty first-level indexes, empty partitions, backward seeks before/after range ends, incomplete secondary iterators, and status precedence.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/two_level_iterator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/two_level_iterator.h -->
# sources/storage-engines/rocksdb/table/two_level_iterator.h

Purpose: declares the two-level iterator abstraction used for partitioned table/index traversal. A first-level iterator points at block handles, and the returned iterator exposes a single ordered stream from the corresponding second-level iterators.

Important APIs/types: `TwoLevelIteratorState` is the extension point with virtual `NewSecondaryIterator(const BlockHandle&)`. `NewTwoLevelIterator(TwoLevelIteratorState*, InternalIteratorBase<IndexValue>*)` constructs the flattening iterator and transfers ownership of both the state and first-level iterator to the implementation.

Control flow and integration: callers provide an index iterator whose values contain `IndexValue::handle`. On demand, the implementation asks the state object for a secondary iterator over the pointed-to block. This header intentionally keeps block loading policy out of the iterator interface.

State and persistence behavior: the header declares no durable state. Its ownership contract is important: first-level and secondary iterators are expected not to be arena allocated.

Dependencies: includes RocksDB env/iterator APIs and `table/iterator_wrapper.h`; forward declares `ReadOptions` and `InternalKeyComparator`.

Risks and test signals: any implementer of `TwoLevelIteratorState` must return heap-owned `InternalIteratorBase<IndexValue>` instances or null on failure. Tests should verify ownership, null secondary behavior, partition transitions, and ordering equivalence with a flat iterator.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/two_level_iterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/unique_id.cc -->
# sources/storage-engines/rocksdb/table/unique_id.cc

Purpose: implements stable SST unique-id generation, session-id encoding, external/public ID encoding, and debugging string formats. These functions derive IDs from table properties (`db_id`, `db_session_id`, original file number) and are explicitly long-term stable because SST IDs can be stored in manifests, caches, backups, or diagnostics.

Important APIs/functions: `EncodeSessionId()` packs entropy into a 20-character base-36 string, preserving all 64 lower bits and part of the upper bits. `DecodeSessionId()` accepts 13-24 base-36 characters and returns `NotSupported` for missing, short, long, or malformed input. `GetSstInternalUniqueId()` builds a 128-bit or 192-bit internal ID: word 0 preserves session lower bits, word 1 hashes DB identity and xors file number, and optional word 2 stores a second DB hash. `InternalUniqueIdToExternal()` and `ExternalUniqueIdToInternal()` apply a bijective hash with offsets so all-zero internal IDs map to all-zero external IDs. `EncodeUniqueIdBytes()`/`DecodeUniqueIdBytes()` convert numerical words to 16- or 24-byte fixed64 strings. `GetUniqueIdFromTableProperties()` and `GetExtendedUniqueIdFromTableProperties()` are public helpers over `TableProperties`.

State and persistence: no local persistent state is mutated, but the byte encodings and hash transformations are durable compatibility contracts. `force=true` allows fallback hashing of malformed session IDs for temporary/test IDs.

Dependencies and integration: uses `util/coding_lean.h`, `util/hash.h`, `util/string_util.h`, `rocksdb/unique_id.h`, and table properties. Integrates with SST metadata, cache key identity, manifest validation, and human-readable diagnostics through `UniqueIdToHumanString()`.

Risks and test signals: compatibility regressions are the main risk. Tests should pin known session encodings, decode error statuses, 16/24-byte length checks, zero mapping, bijective round trips, malformed forced generation, and file-number uniqueness for a fixed DB/session.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/unique_id.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/unique_id_impl.h -->
# sources/storage-engines/rocksdb/table/unique_id_impl.h

Purpose: declares internal unique-id representations and helper functions behind RocksDB's SST unique-id public API.

Important APIs/types: `UniqueId64x2` is the standard two-word ID; `UniqueId64x3` is the extended three-word variant. `kNullUniqueId64x2` and `kNullUniqueId64x3` reserve all-zero values as null sentinels. `UniqueIdPtr` is an implicit wrapper around either array type and exposes `ptr` plus `extended` so shared code can operate on both lengths.

Control flow and integration: callers compute an internal ID with `GetSstInternalUniqueId()`, optionally transform it with `InternalUniqueIdToExternal()`, then encode bytes for public surfaces. Reverse helpers exist mostly for tests. Session ID helpers bridge process/session randomness to compact filename-friendly IDs.

State and persistence: declarations emphasize long-term stability. Any change in binary layout, session encoding, or bijective transform can break stable SST identity, cache keys, and metadata verification.

Dependencies: includes `<array>` and `rocksdb/unique_id.h` for status/table-property-facing contracts.

Risks and test signals: `UniqueIdPtr` has no runtime size checks beyond the selected constructor, so callers must not pass insufficient storage. Tests should exercise both standard and extended forms, null sentinel invariants, external/internal round trips, and session ID entropy preservation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/unique_id_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/mock_time_env.cc -->
# sources/storage-engines/rocksdb/test_util/mock_time_env.cc

Purpose: implements the platform-specific part of `MockSystemClock`, currently `InstallTimedWaitFixCallback()`, a debug-build workaround for timed wait behavior differences.

Important API/control flow: in non-release builds it disables sync-point processing, clears callbacks, and on macOS registers a callback at `InstrumentedCondVar::TimedWaitInternal`. The callback rewrites an already-expired deadline to a real-clock deadline one millisecond in the future, then sync-point processing is re-enabled.

State and dependencies: mutates global `SyncPoint` callback state. It depends on `test_util/sync_point.h` and `MockSystemClock::RealNowMicros()`. No durable state is written.

Integration points: used by tests that run against mock time but still pass deadlines to platform condition variables interpreted against real time.

Risks and test signals: this helper globally clears callbacks, so callers must install it before adding test-specific sync points or accept that existing callbacks are removed. It is disabled in release builds and only changes macOS behavior. Tests should verify no deadlock when a mocked deadline is already elapsed and that non-macOS builds leave deadlines unchanged.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/mock_time_env.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/mock_time_env.h -->
# sources/storage-engines/rocksdb/test_util/mock_time_env.h

Purpose: defines `MockSystemClock`, a test `SystemClockWrapper` that advances logical time without sleeping. The file notes that `SpecialEnv` is preferred for DB tests because it adds DB-safe mock-time hooks.

Important APIs: `GetCurrentTime()`, `NowSeconds()`, `NowMicros()`, and `NowNanos()` read `current_time_us_`. `SetCurrentTime()`, `SleepForMicroseconds()`, and `MockSleepForSeconds()` advance time monotonically with overflow assertions. `RealNowMicros()` delegates to the wrapped clock. `TimedWait()` synthetically unlocks the condition-variable mutex, yields, randomly chooses timeout vs wakeup, and if timing out advances mock time to the deadline.

State behavior: `current_time_us_` is atomic, but comments state fake sleep is not thread-safe as a test-time abstraction. `TimedWait()` temporarily releases and reacquires the caller's mutex, and emits sync points around the synthetic sleep.

Dependencies/integration: uses RocksDB `SystemClock`, `port::CondVar`, TLS `Random`, and debug `SyncPoint`. Tests use it for deterministic or accelerated time behavior.

Risks and test signals: nondeterministic `TimedWait()` can expose races but makes exact wakeup assertions fragile. Overflow and monotonicity are assert-only. Tests should cover fake sleep increments, seconds/micros/nanos conversions, mutex release behavior, sync-point hooks, and callers that depend on timeout vs wakeup.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/mock_time_env.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/secondary_cache_test_util.cc -->
# sources/storage-engines/rocksdb/test_util/secondary_cache_test_util.cc

Purpose: implements cache item helpers used by secondary-cache tests, including serialization, creation, size accounting, and failure injection.

Important APIs/functions: `WithCacheType::GetHelper()` returns a static `Cache::CacheItemHelper` for a cache-entry role with optional secondary-cache compatibility and optional save failure. `GetHelperFail()` is a convenience for failing save-to-secondary paths. Internal callbacks delete `TestItem`, compute size, serialize the entire buffer from offset zero, fail serialization, or reconstruct a `TestItem` from secondary-cache bytes.

State and ownership: helper arrays are static and indexed by `CacheEntryRole`. `CreateCallback()` allocates `TestItem` with `new`; `DeletionCallback()` owns deletion. `TestCreateContext::fail_create_` can force creation failure.

Dependencies/integration: uses advanced cache APIs and gtest expectations. It supports LRU and HyperClock cache test coverage through the declarations in the header.

Risks and test signals: `SaveToCallback()` expects full-object serialization from offset zero, so tests using partial offsets will fail. Role indexing assumes `kNumCacheEntryRoles` matches enum ordinals. Tests should cover all roles, successful secondary round trip, save failure, create failure, and helper chaining through the `without_secondary` fallback pointer.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/secondary_cache_test_util.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/secondary_cache_test_util.h -->
# sources/storage-engines/rocksdb/test_util/secondary_cache_test_util.h

Purpose: declares parameterized cache-test utilities for running the same tests against LRU, fixed HyperClock, and auto HyperClock cache implementations, with optional secondary-cache support.

Important APIs/types: `TestCreateContext` carries a `fail_create_` flag. `WithCacheType::TestItem` is a heap-backed byte buffer with `Buf()`, `Size()`, and `ToString()`. `WithCacheType::NewCache()` builds a cache based on virtual `Type()` and optional `ShardedCacheOptions` modification. Overloads set shard bits, strict capacity, metadata charge policy, or secondary cache. `WithCacheTypeParam` plugs into gtest parameterized tests. `GetTestingCacheTypes()` returns all supported type strings.

State behavior: `estimated_value_size_` influences HyperClock construction. Cache hash seeds are forced to zero for deterministic tests. No persistent state is written.

Dependencies/integration: integrates with `rocksdb/advanced_cache.h` and gtest `WithParamInterface`. Tests inherit this class to obtain cache factories and helpers.

Risks and test signals: unknown type values assert and return null. HyperClock options depend on `estimated_value_size_` and min charge calculations. Tests should exercise each cache type, option modification callback propagation, secondary-cache configuration, and helper retrieval for representative roles.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/secondary_cache_test_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/sync_point.cc -->
# sources/storage-engines/rocksdb/test_util/sync_point.cc

Purpose: provides the public `SyncPoint` singleton wrappers, direct-I/O mocking hooks, global kill-point exclusion storage, and debug-only testable assertion state.

Important APIs/control flow: in non-release builds `SyncPoint::GetInstance()` returns a static singleton whose methods delegate to `SyncPoint::Data`: loading dependencies/markers, registering callbacks, clearing state, enabling/disabling, and processing points. `SetupSyncPointsToMockDirectIO()` registers callbacks that clear `O_DIRECT` from writable, random-access, and sequential file creation flags on supported platforms.

State behavior: owns the singleton `Data` through a raw pointer and deletes it in the destructor. `rocksdb_kill_exclude_prefixes` is a global vector outside the RocksDB namespace. `g_throw_on_testable_assertion_failure` is a debug-only atomic counter used by `testable_assert`.

Dependencies/integration: depends on `sync_point_impl.h`, platform `fcntl.h`, and RocksDB tests that compile `TEST_SYNC_POINT` macros. Direct-I/O mocking integrates with Env file creation sync points.

Risks and test signals: all substantive behavior disappears under `NDEBUG` except direct-I/O setup's outer symbol. Global sync-point state can leak between tests if not cleared. Tests should validate callback delegation, cleanup behavior, direct-I/O flag mutation, and release-build no-op compilation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/sync_point.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/sync_point.h -->
# sources/storage-engines/rocksdb/test_util/sync_point.h

Purpose: declares debug-only sync-point and kill-point test instrumentation macros used to force deterministic thread interleavings and randomized crash testing.

Important APIs/types: `KillPoint` stores crash odds and exclusion prefixes and exposes `TestKillRandom()`. `SyncPoint` declares dependency pairs, dependency/marker loading, callback registration and clearing, processing control, trace clearing, and overloaded `Process()` for string literals. Macros include `TEST_SYNC_POINT`, `TEST_IDX_SYNC_POINT`, `TEST_SYNC_POINT_CALLBACK`, `TEST_KILL_RANDOM`, `IGNORE_STATUS_IF_ERROR`, `testable_assert`, and `ASSERT_TESTABLE_FAILURE`.

Control flow: in debug builds, sync-point macros call the singleton's `Process()`, potentially blocking until dependencies clear and running callbacks. In release builds, most macros compile away to no-ops.

State and dependencies: exposes global testable assertion counter and `TestableAssertionFailure` in debug builds. Depends on RocksDB namespace/slice plus gtest for assertion helpers.

Risks and test signals: tests that depend on sync points must not run under release builds expecting behavior. `ASSERT_TESTABLE_FAILURE` increments/decrements a global counter, so exception paths must not bypass cleanup. Tests should cover macro no-op behavior, indexed point naming, callback arguments, and marker/dependency interaction via the implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/sync_point.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/sync_point_impl.cc -->
# sources/storage-engines/rocksdb/test_util/sync_point_impl.cc

Purpose: implements debug-only kill-point random crashes and the core sync-point dependency engine.

Important APIs/control flow: `KillPoint::TestKillRandom()` returns if odds are disabled or the point has an excluded prefix, adjusts odds divisible by seven to avoid weak random coverage, then calls `port::Crash()` with source location when selected. `SyncPoint::Data::LoadDependency()` and `LoadDependencyAndMarkers()` rebuild predecessor/successor maps, marker maps, cleared trace, and bloom filter entries. `Process()` quickly skips disabled or unregistered points, records marker thread IDs, waits until all predecessors are cleared, runs callbacks outside the mutex, records the point as cleared, and notifies waiters.

State behavior: guarded maps track dependencies, callbacks, markers, marked thread IDs, and cleared points. `num_callbacks_running_` prevents callback clearing while callbacks execute. No durable state exists.

Dependencies/integration: uses TLS `Random`, `port::Crash`, condition variables, and `DynamicBloom` from the implementation struct. Called only through `SyncPoint` wrappers/macros.

Risks and test signals: dependency cycles can deadlock until processing is disabled. Callbacks run without the mutex, so they can race with test teardown unless cleared carefully. Tests should cover predecessor ordering, disable wakeups, marker same-thread filtering, callback clear waiting, and kill exclusion prefixes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/sync_point_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/sync_point_impl.h -->
# sources/storage-engines/rocksdb/test_util/sync_point_impl.h

Purpose: defines the debug-only internal state container for `SyncPoint`, plus a small allocator used to avoid circular dependencies with RocksDB arenas.

Important APIs/types: `SingleAllocator` implements only `AllocateAligned()` by resizing an internal string buffer, enough for `DynamicBloom`; other allocation methods assert. `SyncPoint::Data` stores dependency maps, callbacks, markers, mutex/condition variable, cleared point trace, bloom filter, enabled flag, and callback-running count. It provides loading, callback, processing, enable/disable, trace clearing, and marker filtering methods.

State behavior: `enabled_` is atomic for cheap checks. `DisableProcessing()` wakes all waiters so threads blocked in `Process()` can exit. `point_filter_` avoids locking for points that have no dependency/callback/marker interest.

Dependencies/integration: includes `memory/concurrent_arena.h`, `port/port.h`, `util/dynamic_bloom.h`, `util/random.h`, and public sync-point declarations. It is included by implementation files rather than being a public test API.

Risks and test signals: `SingleAllocator` is intentionally single-use and incomplete; expanding bloom usage could expose its assert-only methods. Tests should stress disable during wait, callback clearing while a callback runs, and marker filtering for different thread IDs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/sync_point_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/testharness.cc -->
# sources/storage-engines/rocksdb/test_util/testharness.cc

Purpose: implements common gtest harness helpers for RocksDB tests: process/thread-specific paths, random seed selection, memory gating, status assertions, regex assertions, and debug sync-point cleanup.

Important APIs/control flow: a debug-only `SyncPointCleanupListener` is statically registered with gtest and clears sync-point processing, callbacks, traces, and dependencies after every test. `GetPidStr()` abstracts process ID across Windows/POSIX. `TmpDir()`, `PerThreadDBPath()`, `RandomSeed()`, and `HasBigMem()` provide environment-sensitive test setup. `AssertStatus()` and `AssertMatchesRegex()` produce gtest assertion results. `TestRegex` wraps `std::regex` behind a shared implementation.

State behavior: static listener registration mutates gtest global listener state. `RandomSeed()` reads `TEST_RANDOM_SEED`, and `HasBigMem()` reads `ROCKSDB_BIGMEM_TESTS` and physical memory via `sysconf` when available.

Dependencies/integration: integrates with gtest, Env test directories, stack trace/test utilities, and sync-point debug infrastructure.

Risks and test signals: static listener ordering matters, but it prevents stale callbacks from sharded test processes. `PerThreadDBPath()` hashes thread IDs, so it is unique enough for tests but not a persistent naming scheme. Tests should cover regex assertion messages, invalid seeds defaulting to 301, big-memory gating, and sync-point cleanup between tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/testharness.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/testharness.h -->
# sources/storage-engines/rocksdb/test_util/testharness.h

Purpose: declares RocksDB's gtest convenience layer: skip/bypass macros, status assertions, temporary path helpers, random seed and memory gates, and regex matching assertions.

Important APIs/macros: `ROCKSDB_GTEST_SKIP()` uses `GTEST_SKIP_` when available and otherwise records success while printing to stderr. `ROCKSDB_GTEST_BYPASS()` marks intentionally omitted parameterizations. `ASSERT_OK`, `EXPECT_OK`, `ASSERT_NOK`, and `EXPECT_NOK` wrap `Status`. `EXPECT_NEAR2` avoids integer precision warnings. `TestRegex`, `ASSERT_MATCHES_REGEX`, and `EXPECT_MATCHES_REGEX` provide whole-string regex checks.

State and integration: no persistent state. Declarations integrate with `Env`, gtest, and `port/stack_trace.h`. `using test::TestRegex` exposes the helper in the RocksDB namespace.

Risks and test signals: skip macros do not themselves return from tests, so callers must return after invoking them. Regex constructors can throw on bad patterns. Tests should verify status failure output, skip behavior on gtest versions with and without real skip support, and regex whole-match semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/testharness.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/testutil.cc -->
# sources/storage-engines/rocksdb/test_util/testutil.cc

Purpose: implements broad RocksDB test utilities: random data/options factories, comparator wrappers, file corruption/truncation helpers, direct-I/O and prefetch probes, mock object registration, and a special memtable factory for flush-triggering tests.

Important APIs/functions: `RandomKey()`, `CompressibleString()`, and `RandomName()` generate test inputs. UDT helpers expose timestamp test modes. `Uint64Comparator()` and timestamp comparator wrappers create comparators. `CorruptKeyType()` and `KeyStr()` build internal-key strings. `SleepingBackgroundTask` timed waits are implemented here. Random option functions populate `DBOptions`, `ColumnFamilyOptions`, block table options, table factories, merge operators, compaction filters, compression vectors, and slice transforms. `IsDirectIOSupported()` and `IsPrefetchSupported()` probe filesystem behavior by creating temporary files. `CorruptFile()` flips bits and can verify SST checksum failure; `TruncateFile()` rewrites file content to a new length. `GetFileType()` and `GetFileNumber()` parse RocksDB filenames. `CreateEnvFromSystem()` uses `TEST_ENV_URI` and `TEST_FS_URI`. `RegisterTestObjects()` and `RegisterTestLibrary()` add test factories to `ObjectRegistry`.

State behavior: static constants define default format-version coverage and no-I/O read options. `RegisterTestLibrary()` has a function-local static guard. `SpecialMemTableRep` wraps another memtable and reports huge memory usage after a threshold to force flush. No production durable state is written, but helpers deliberately create/delete temp files.

Dependencies/integration: touches many RocksDB subsystems: DB/memtable internals, file readers/writers, Env/FileSystem APIs, table factories, object registry, mock clock, compression manager, and sync points.

Risks and test signals: random option generation can produce invalid or expensive combinations, so callers must constrain tests. `CorruptFile()` loads whole files into memory. file-name parsing uses `substr(found)` including the slash when a slash exists, so tests should confirm expected parser behavior. Registration is one-shot and argument-sensitive only on first call. Test signals include option round trips, object factory lookup, direct I/O/prefetch probes, corruption checksum failures, and forced memtable flush after configured inserts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/testutil.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/testutil.h -->
# sources/storage-engines/rocksdb/test_util/testutil.h

Purpose: declares and defines a large set of inline test doubles and helpers for RocksDB unit tests, spanning in-memory file abstractions, comparators, background-task synchronization, compaction/merge test objects, custom compression wrappers, random option factories, filesystem probes, and object registration.

Important APIs/types: `RandomKeyType`, `UserDefinedTimestampTestMode`, `PlainInternalKeyComparator`, `SimpleSuffixReverseComparator`, `StringSink`, `RandomRWStringSink`, `OverwritingStringSink`, `StringSource`, `SeqStringSource`, `StringFS`, `NullLogger`, `SleepingBackgroundTask`, `FilterNumber`, `CompressorCustomAlg`, and `DecompressorCustomAlg` are the major reusable test types. Function declarations cover randomization, key building, file corruption/truncation, env creation, file type/number parsing, and registration.

Control flow and state: in-memory file types store contents in strings or maps and implement selected RocksDB file interfaces. `SleepingBackgroundTask` coordinates a background sleeper with mutex/condvar state. Custom compression prepends a five-byte header containing the custom type and dictionary hash, then delegates to LZ4; decompression strips/checks the header and delegates. `ReadOptionsNoIo` sets block-cache-only reads.

Dependencies/integration: includes Env, FileSystem, table, iterator, merge, compaction, compression, and mutex utilities. It is a central include for tests needing lightweight RocksDB-compatible objects.

Risks and test signals: many test doubles intentionally implement only part of their interface and return `NotSupported` elsewhere. `StringSource` can return direct slices in mmap mode or scratch-backed slices otherwise. Custom decompression has an `allowed_types_` field that must be enforced by users/tests. Tests should cover in-memory read/write semantics, compression header round trips, background wakeup paths, and no-I/O read options.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/testutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/testutil_test.cc -->
# sources/storage-engines/rocksdb/test_util/testutil_test.cc

Purpose: provides a focused gtest for recursive directory destruction through the file utility layer.

Important APIs/control flow: helper `CreateFile()` opens a writable file with `Env::NewWritableFile()` and closes it. `TEST(TestUtil, DestroyDirRecursively)` creates a per-thread test directory with a file and nested directory/file, calls `DestroyDir(env, test_dir)`, then asserts the directory no longer exists. `main()` installs the stack-trace handler, initializes gtest, and runs all tests.

State behavior: creates and deletes files under the Env test directory. It expects a clean per-thread path and leaves no durable state on success.

Dependencies/integration: uses `testutil.h`, `file/file_util.h`, RocksDB Env APIs, gtest harness macros, and stack-trace installation.

Risks and test signals: the test is a smoke test for recursive deletion, not exhaustive coverage of permission errors, symlink behavior, or concurrent deletion. It assumes `CreateDir()` succeeds on a fresh path. Failure signals are direct `ASSERT_OK` or final `IsNotFound()` assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/testutil_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/transaction_test_util.cc -->
# sources/storage-engines/rocksdb/test_util/transaction_test_util.cc

Purpose: implements `RandomTransactionInserter`, a transaction stress helper that repeatedly increments one random key in each key set and verifies that all sets retain equal totals.

Important APIs/control flow: `TransactionDBInsert()` begins/reuses a transaction, assigns a unique thread/id-derived name, sometimes sets a snapshot, and calls `DoInsert()`. `OptimisticTransactionDBInsert()` does the same for optimistic transactions. `DBInsert()` writes through a plain `WriteBatch`. `DBGet()` formats keys as four-digit set prefix plus random key number, reads through transaction or DB, parses numeric values, and treats not found as zero. `DoInsert()` shuffles set order, chooses an increment, gets/deletes/puts per set, optionally prepares, maybe writes commit-time batch data, commits or rolls back, and records success/failure/bytes/status. `Verify()` sums each set through point lookups or iterators and reports corruption when totals differ.

State behavior: the inserter owns reusable `Transaction*` and `optimistic_txn_` pointers, counters, last status, mutable read options, and transaction IDs. It uses snapshots only within a call and releases verification snapshots.

Dependencies/integration: integrates with `DB`, `TransactionDB`, `OptimisticTransactionDB`, transaction options, snapshots, logging, thread IDs, and RocksDB random utilities.

Risks and test signals: the helper assumes the DB starts empty and values are decimal integers. `DoInsert()` logs/asserts around transaction expectations and treats some conflict statuses as expected. `RollbackDeletionTypeCallback()` mirrors the delete-vs-single-delete rule based on set index. Tests should cover concurrent transaction stress, optimistic conflict handling, prepared commit paths, rollback paths, snapshot verification delays, and invariant failure detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/transaction_test_util.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/transaction_test_util.h -->
# sources/storage-engines/rocksdb/test_util/transaction_test_util.h

Purpose: declares `RandomTransactionInserter`, a reusable class for transaction stress tests that validate an equal-sum invariant across sets of keys.

Important APIs: constructor accepts randomness, write/read options, number of keys, number of sets, commit delay, and first transaction ID. Public insert methods target `TransactionDB`, `OptimisticTransactionDB`, or plain `DB`. Static `DBGet()` reads one formatted key. Static `Verify()` checks the invariant. Accessors expose last status, success/failure counts, and inserted byte totals. `RollbackDeletionTypeCallback()` returns whether a key's set uses `SingleDelete` during rollback testing.

State behavior: stores input options, mutable `ReadOptions` snapshot pointer during transaction inserts, counters, last status, reusable transaction pointers, and commit delay.

Dependencies/integration: includes RocksDB transaction DB public APIs and port utilities; forward declares `DB` and `Random64`.

Risks and test signals: not a general-purpose data generator; it assumes an initially empty DB and set prefixes from 0001 to 9999. Tests should check key formatting, deletion callback consistency with implementation, counter updates, and verification under both transactional and non-transactional writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/test_util/transaction_test_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/third-party/gcc/ppc-asm.h -->
# sources/storage-engines/rocksdb/third-party/gcc/ppc-asm.h

Purpose: vendored GCC runtime header providing PowerPC assembler register aliases and function-definition macros for multiple PowerPC ABIs. RocksDB carries it under third-party code for architecture-specific assembly compatibility.

Important APIs/macros: defines numeric aliases for general registers `r0`-`r31`, condition registers `cr0`-`cr7`, floating registers `f0`-`f31`, optional VSX `f32`-`f63` and `vs0`-`vs63`, and optional AltiVec `v0`-`v31`. `XGLUE`/`GLUE` concatenate tokens. ABI-specific macros include `FUNC_NAME`, `JUMP_TARGET`, `FUNC_START`, `HIDDEN_FUNC`, and `FUNC_END` for ELFv2, 64-bit descriptor ABIs, AIX descriptors, and generic ELF/PIC cases. Under `IN_GCC`, CFI macros map to gas directives when available. On 32-bit Linux it emits a `.note.GNU-stack` section.

State and persistence: no runtime state. It controls assembler symbol layout and unwind metadata at compile time.

Dependencies/integration: used by assembly sources that need portable PowerPC function prologues across GNU toolchains. It may include `auto-host.h` when compiled inside GCC.

Risks and test signals: macro definitions are ABI-sensitive; changing them can break symbol names, TOC setup, hidden visibility, or executable-stack markings. Vendored license terms are GPL with GCC Runtime Library Exception. Test signals are architecture build/link tests on ppc32, ppc64 ELFv1, ppc64 ELFv2, PIC, PC-relative, VSX, and AltiVec configurations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/third-party/gcc/ppc-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/CMakeLists.txt -->
# sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/CMakeLists.txt

Purpose: minimal CMake build file for the vendored fused GoogleTest source.

Important APIs/control flow: `add_library(gtest gtest-all.cc)` builds a `gtest` library target from the fused source. `target_link_libraries(gtest ${CMAKE_THREAD_LIBS_INIT})` links the thread library selected by the parent CMake configuration.

State and persistence: no runtime state and no generated configuration beyond the build target.

Dependencies/integration: assumes `gtest-all.cc` is present in the same fused source directory and that `${CMAKE_THREAD_LIBS_INIT}` has been set by a parent `find_package(Threads)` or equivalent.

Risks and test signals: this file does not set include directories, compile options, or thread discovery itself, so it relies on surrounding RocksDB CMake configuration. Build tests should verify vendored gtest target creation and successful link on platforms requiring explicit pthread/thread libraries.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/CMakeLists.txt -->
