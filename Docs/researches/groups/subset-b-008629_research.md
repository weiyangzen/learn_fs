# Group Research: subset-b-008629

Work item `subset-b-008629` covers RocksDB write throttling/concurrency internals and the front portion of the `db_stress_tool` harness. Each source file has a wrapped section so reconciliation can split this grouped report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_controller_test.cc -->
# Research: sources/storage-engines/rocksdb/db/write_controller_test.cc

- **Purpose:** Unit tests for `WriteController` delayed-write and stop-token behavior. The file verifies the public token API, delay arithmetic, debt accumulation, and accumulated credit behavior using a controllable clock.
- **Important APIs/types/functions:** Defines `TimeSetClock`, a `SystemClockWrapper` test clock exposing `now_micros_`; defines `WriteControllerTest`; test cases are `BasicAPI`, `StartFilled`, `DebtAccumulation`, and `CreditAccumulation`; `main()` installs stack traces and runs GoogleTest.
- **Control flow:** Tests create a `WriteController`, acquire scoped delay/stop tokens, call `GetDelay()` with byte counts, then advance fake time to pay debt or accumulate credit. Token destructors are part of the exercised behavior because leaving scopes releases delay/stop pressure.
- **State and persistence behavior:** No durable state. Important transient state is fake time, scoped token lifetime, the controller's delayed write rate, stop count, and internally accumulated debt/credit.
- **Dependencies and integration points:** Depends on `db/write_controller.h`, `rocksdb/system_clock.h`, and `test_util/testharness.h`. It integrates with RocksDB's unit-test binary and guards behavior relied on by write stalls in DBImpl.
- **Risks:** The tests depend on exact microsecond arithmetic and constants like refill timing, so rate-controller implementation changes can break tests even when user-visible behavior is close. Floating-style literals cast to integers make boundary tolerance important.
- **Test signals:** GoogleTest assertions check delayed rate, stop/delay predicates, exact or bounded delay values, debt monotonicity, and debt/credit reset on token release.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_controller_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_stall_stats.cc -->
# Research: sources/storage-engines/rocksdb/db/write_stall_stats.cc

- **Purpose:** Implements conversion and metric-routing helpers for write-stall causes and conditions. It maps enum values to stable hyphenated names and to internal DB/column-family stats counters.
- **Important APIs/types/functions:** Implements `InvalidWriteStallHyphenString`, `WriteStallCauseToHyphenString`, `WriteStallConditionToHyphenString`, `InternalCFStat`, `InternalDBStat`, `isCFScopeWriteStallCause`, `isDBScopeWriteStallCause`, and `WriteStallStatsMapKeys::{TotalStops,TotalDelays,CFL0FileCountLimitDelaysWithOngoingCompaction,CFL0FileCountLimitStopsWithOngoingCompaction,CauseConditionCount}`.
- **Control flow:** Switches on `WriteStallCause` and `WriteStallCondition`; valid CF-scoped causes route to `InternalCFStatsType`, DB-scoped write-buffer-manager stops route to `InternalDBStatsType`, and invalid combinations return sentinel enum maxima or `"invalid"`.
- **State and persistence behavior:** No mutable persistent state. String-returning helpers use function-local static strings to provide stable references without repeated allocation.
- **Dependencies and integration points:** Includes `db/write_stall_stats.h`, which depends on `InternalStats` and public RocksDB enum types. Integrated with stats collection, property/map output, and write-stall diagnostics.
- **Risks:** New write-stall enum values must be added consistently here or they will surface as invalid strings/stat sentinels. `CauseConditionCount` asserts on non CF/DB-scope causes and returns empty under assertion-disabled builds.
- **Test signals:** Coverage should validate string keys, stat enum routing, invalid fallbacks, and map-key names consumed by monitoring/property APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_stall_stats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_stall_stats.h -->
# Research: sources/storage-engines/rocksdb/db/write_stall_stats.h

- **Purpose:** Declares write-stall stats helper functions and scope-count constants shared by write-stall reporting code.
- **Important APIs/types/functions:** Exposes string conversion helpers, `InternalCFStat`, `InternalDBStat`, `isCFScopeWriteStallCause`, `isDBScopeWriteStallCause`, and constexpr `kNumCFScopeWriteStallCauses`/`kNumDBScopeWriteStallCauses`.
- **Control flow:** Header only declares behavior; comments document preconditions that stat lookup callers must pass a scoped cause and a non-normal condition.
- **State and persistence behavior:** No state. Constants encode assumptions about contiguous enum ranges ending at `kCFScopeWriteStallCauseEnumMax` and `kDBScopeWriteStallCauseEnumMax`.
- **Dependencies and integration points:** Includes `db/internal_stats.h` and `rocksdb/types.h`; used by DB/CF internal stats and user-facing write-stall statistics map generation.
- **Risks:** The scope constants depend on enum layout. Reordering or inserting enum values outside the intended ranges can silently misclassify causes unless corresponding tests cover scope predicates.
- **Test signals:** Compile-time use catches signature drift; runtime tests should exercise all enum values and `kNormal` rejection paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_stall_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_thread.cc -->
# Research: sources/storage-engines/rocksdb/db/write_thread.cc

- **Purpose:** Implements RocksDB's single-writer batching, pipelined WAL/memtable handoff, parallel memtable writer launch, unbatched writer gating, adaptive waiting, and write-stall queue blocking.
- **Important APIs/types/functions:** Key methods are `JoinBatchGroup`, `EnterAsBatchGroupLeader`, `ExitAsBatchGroupLeader`, `EnterAsMemTableWriter`, `ExitAsMemTableWriter`, `LaunchParallelMemTableWriters`, `CompleteParallelMemTableWriter`, `EnterUnbatched`, `ExitUnbatched`, `BeginWriteStall`, `EndWriteStall`, and `WaitForMemTableWriters`. Internal helpers include `AwaitState`, `BlockingAwaitState`, `SetState`, `LinkOne`, `LinkGroup`, `CreateMissingNewerLinks`, `CompleteLeader`, and `CompleteFollower`.
- **Control flow:** Writers atomically push themselves onto a newest-writer list. The first writer becomes group leader; leaders materialize reverse `link_newer` links, select compatible followers under size/option constraints, perform WAL work externally, then complete followers or transfer remaining writers to the memtable queue when pipelined writes are enabled. Memtable leaders optionally group followers and either run sequentially or wake parallel workers. State transitions wake blocked threads through either atomic polling/yielding or lazily created condition variables.
- **State and persistence behavior:** Maintains atomic queue heads `newest_writer_` and `newest_memtable_writer_`, `last_sequence_`, per-writer status/sequence/link state, per-group status/running counters, and stall counters protected by DB/stall mutexes. No durable storage is written here, but it gates WAL/memtable persistence performed by higher write-path code.
- **Dependencies and integration points:** Uses `WriteBatchInternal`, `ImmutableDBOptions`, `InstrumentedMutex`, perf context wait timers, `SyncPoint`, `Random`, and port synchronization. DBImpl write code uses it to serialize WAL order, sequence assignment, memtable insertion, and write-stall handling.
- **Risks:** The implementation is race-sensitive: dummy writers, `link_older/link_newer` reconstruction, pipelined handoff ordering, and `STATE_LOCKED_WAITING` synchronization must remain exact. Compatibility checks in batch grouping affect correctness for sync, no-slowdown, WAL-disabled, protection, callback, and WBWI-ingest writes. Blocking/yield adaptation can hide liveness bugs if state transitions are missed.
- **Test signals:** Sync-point tests, stress tests, and write-path unit tests should target leader handoff, pipelined ordering, no-slowdown stall failure, unbatched waits, parallel memtable error propagation, and wait-stat behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_thread.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_thread.h -->
# Research: sources/storage-engines/rocksdb/db/write_thread.h

- **Purpose:** Declares the `WriteThread` concurrency coordinator and its per-writer/per-group state model for RocksDB writes.
- **Important APIs/types/functions:** Defines `State` bit flags, `Writer`, `WriteGroup`, `WriteGroup::Iterator`, and `AdaptationContext`. Public methods cover batch joining, batch/memtable leader entry/exit, parallel memtable launch/completion, unbatched entry/exit, stall begin/end/wait, and `UpdateLastSequence`.
- **Control flow:** The header documents the lifecycle: writers start in `STATE_INIT`, may become WAL group leaders, memtable leaders, parallel memtable workers/callers, or completed followers. `Writer` exposes callback checks, final-status folding, WAL/memtable eligibility, and lazy wait primitive construction.
- **State and persistence behavior:** `Writer` carries batch pointers, trace batch, write options, callbacks, WAL/log references, sequence number, status, write-group pointer, queue links, and optional mutex/CV storage. `WriteThread` owns queue heads, last allocated sequence, stall dummy/counters, and immutable option-derived wait/grouping settings.
- **Dependencies and integration points:** Includes write callbacks, pre/post memtable callbacks, RocksDB options/status/types/write batch, internal formatting, and instrumented mutex support. It is part of the DBImpl write-path contract and not tied to the DB mutex for most operations.
- **Risks:** Callers must respect documented locking and lifecycle constraints: `StateMutex` is last in lock order, writer stack lifetime must outlive waits, `batch == nullptr` identifies unbatched operations, and callback failures must prevent WAL/memtable writes. Header comments are part of the concurrency contract.
- **Test signals:** ABI/compile tests catch signature changes; behavioral tests should validate every state transition path and callback/status precedence in `Writer::FinalStatus`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/write_thread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/CMakeLists.txt -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/CMakeLists.txt

- **Purpose:** Defines the `db_stress` executable target for the CMake build.
- **Important APIs/types/functions:** Adds `db_stress${ARTIFACT_SUFFIX}` from stress source files and links it with `${ROCKSDB_LIB}` plus `${THIRDPARTY_LIBS}`; appends the target to `tool_deps`.
- **Control flow:** Build-system only: source list is compiled into one tool target when the enclosing build enables it.
- **State and persistence behavior:** Produces a build artifact, not runtime state.
- **Dependencies and integration points:** Integrates db_stress with the RocksDB CMake tool build, including gflags-dependent source files and RocksDB/third-party libraries.
- **Risks:** New stress-tool source files must be added here or they will be omitted from CMake builds. Conditional compilation around `GFLAGS` still requires link inputs to be consistent.
- **Test signals:** CMake configure/build of the `db_stress` target and downstream CI tool dependency builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/batched_ops_stress.cc -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/batched_ops_stress.cc

- **Purpose:** Implements the batched-ops stress variant where each logical key maps to ten physical keys (`0`-`9` prefixes) written/deleted atomically in one `WriteBatch`, then verified through point, multi-get, entity, and prefix-scan APIs.
- **Important APIs/types/functions:** Defines `BatchedOpsStressTest : StressTest`, overrides `IsStateTracked`, `TestPut`, `TestDelete`, unsupported `TestDeleteRange`/`TestIngestExternalFile`, `TestGet`, `TestMultiGet`, `TestGetEntity`, `TestMultiGetEntity`, `TestPrefixScan`, `VerifyDb`, `ContinuouslyVerifyDb`, and helper `CompareColumns`; factory `CreateBatchedOpsStressTest`.
- **Control flow:** `TestPut` generates one value body and writes ten suffixed values in one batch using `Put`, `Merge`, `TimedPut`, `PutEntity`, or attribute groups depending on flags. Read paths take snapshots where needed, fetch all ten variants, strip/check the digit suffix, and compare shared value/entity contents. Prefix scan constructs ten bounded iterators and advances them in lockstep.
- **State and persistence behavior:** Persists ten physical records per logical write in RocksDB; deletes them in one batch. The class does not use expected-state tracking and records only thread stats/errors. Snapshots are acquired/released for consistent multi-key verification.
- **Dependencies and integration points:** Depends on `db_stress_common.h`, `StressTest`, wide-column helpers, SQFC table filters, `ManagedSnapshot`, `WriteBatch`, and gflags. Selected by the db_stress tool factory for batched operation mode.
- **Risks:** Verification assumes all ten keys are atomically updated and values end with the expected digit. Assertions guard iterator validity and column-family indexing; release builds may continue after inconsistencies reported only to stderr. Unsupported range delete/ingest paths terminate if scheduled incorrectly.
- **Test signals:** Error counters and stderr messages for inconsistent values/entities/columns, wrong suffixes, iterator status failures, and API errors; stats count writes, deletes, gets, and prefixes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/batched_ops_stress.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/cf_consistency_stress.cc -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/cf_consistency_stress.cc

- **Purpose:** Implements the column-family consistency stress variant, ensuring the same logical operations applied across all column families remain visible consistently through point, entity, multi-get, iterator, checksum, and recovery verification paths.
- **Important APIs/types/functions:** Defines `CfConsistencyStressTest : StressTest`, overrides write/delete/range-delete/read/entity/prefix/verification methods, `GenerateColumnFamilies`, and `GetControlCfh`. Private diagnostics include `DebugOpKind`, `DebugEvent`, `RecordDebugEvent`, sequence mapping helpers, `ReportInvalidWriteSequenceBounds`, `DumpRecentDebugEvents`, and `DumpGetEntityMismatchDebug`; factory `CreateCfConsistencyStressTest`.
- **Control flow:** Writes build one `WriteBatch` spanning all generated CFs and record latest-sequence bounds. Reads randomly either sample one CF or compare all CFs under a snapshot, temporarily disabling read fault injection during verification. Full verification walks all CF iterators in lockstep; continuous verification computes CRCs, optionally against a secondary DB after catch-up.
- **State and persistence behavior:** Persists identical logical key/value/entity operations across all CFs. Maintains `batch_id_` for value generation and a mutex-protected deque of recent debug events capped at 512. Verification failure state is written to `SharedState` to stop/fail fast.
- **Dependencies and integration points:** Depends on `db_stress_common.h`, wide-column helpers, file utilities, `GetAllKeyVersions`, secondary DB support, fault-injection FS controls, and `SharedState`. It is the stress mode behind `FLAGS_test_cf_consistency`.
- **Risks:** Cross-CF exactness can be affected by snapshots, WAL/secondary replay limits, retryable injected errors, and sequence interleaving. The `TestDeleteRange` loop indexes `rand_column_families[cf]` while iterating values, so malformed CF vectors would be dangerous. Diagnostics are best-effort and capped.
- **Test signals:** Failure signs include `SetVerificationFailure`, mismatched CF iterator output, entity mismatch dumps, invalid sequence bounds, CRC mismatches, and stderr/stdout diagnostic blocks with recent events and internal key versions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/cf_consistency_stress.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress.cc -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress.cc

- **Purpose:** Entry point for the `db_stress` executable.
- **Important APIs/types/functions:** If `GFLAGS` is unavailable, defines a small `main()` that prints an installation message and exits 1. With `GFLAGS`, includes stack tracing and `rocksdb/db_stress_tool.h`; `main(argc, argv)` installs the stack trace handler and calls `ROCKSDB_NAMESPACE::db_stress_tool`.
- **Control flow:** Compile-time branch selects either stub failure or real db_stress dispatch.
- **State and persistence behavior:** No direct persistent state; delegates all runtime state to `db_stress_tool`.
- **Dependencies and integration points:** Depends on gflags availability, `port/stack_trace.h`, and the public db_stress tool entry point.
- **Risks:** Builds without gflags produce an executable that always fails. Startup failures from flag parsing or tool initialization are delegated.
- **Test signals:** Process exit code and stderr message for no-gflags builds; normal stress-tool output for gflags builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_common.cc -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_common.cc

- **Purpose:** Implements shared db_stress globals, key/value generation, wide-column verification, background helper threads, remote compaction worker plumbing, checksum factories, timestamp generation, and local filesystem cleanup helpers.
- **Important APIs/types/functions:** Defines global caches/rate-limiter/compression/checksum/rep settings, Zipfian hot-key helpers, `PoolSizeChangeThread`, `DbVerificationThread`, `CompressedCacheSetCapacityThread`, remote compaction helpers and `RemoteCompactionWorkerThread`, `GenerateOneKey`, `GenerateNKeys`, `GenerateValue`, `GetValueBase`, `GenerateWideColumns`, `GenerateExpectedWideColumns`, `VerifyWideColumns`, `VerifyIteratorAttributeGroups`, `GetNowNanos`, `GetWriteUnixTime`, `DbStressChecksumGenFactory`, `GetFileChecksumImpl`, `DeleteFilesInDirectory`, `SaveFilesInDirectory`, `InitUnverifiedSubdir`, `DestroyUnverifiedSubdir`, and `DbStressDestroyDb`.
- **Control flow:** Background threads loop until `SharedState` stop flags are set, mutate env/cache/verification/remotely compacted jobs, then signal completion. Remote compaction dequeues jobs, builds override options, optionally cancels/resumes, runs `DB::OpenAndCompact`, and publishes results. Key/value functions deterministically encode values and variable-width ordered keys from flags.
- **State and persistence behavior:** Maintains global shared objects and Zipfian CDF state; writes/checks DB files indirectly through RocksDB APIs; creates/removes `unverified` state directories with `Env::Default`; remote compaction creates output directories and serialized results; `DbStressDestroyDb` destroys DB/blob DB directories through raw env.
- **Dependencies and integration points:** Includes `db_stress_common.h`, `db_stress_test_base.h`, fault injection, secondary cache, file checksum helper, `xxhash`, compaction service APIs, and `SharedState`. Used by nearly every db_stress mode.
- **Risks:** Many helpers rely on global flags and shared globals initialized elsewhere. Detached cancellation threads depend on shared atomic lifetime. Cleanup intentionally uses raw/default env to avoid fault injection, which differs from DB I/O env. Assertions guard value sizes and checksum names.
- **Test signals:** Stress failures surface through stats/errors, asserts, checksum mismatch reports, remote compaction statuses, verification thread failures, and filesystem cleanup statuses.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_common.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_common.h -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_common.h

- **Purpose:** Central shared header for db_stress flags, globals, enum parsers, key encoding, helper declarations, and stress-test factory declarations.
- **Important APIs/types/functions:** Declares a large set of gflags; shared globals `raw_env`, caches, write-buffer manager, rate limiter, compression/checksum enum globals, and `FLAGS_rep_factory`; `StringToRepFactory`, `StringToCompressionType`, `StringToChecksumType`, `TemperatureToString`; `SplitString`, `GetNextPrefix`, `AppendIntToString`, `Key`, `GetIntVal`, prefix-count helpers, hex/wide-column formatting, and declarations for background threads, key/value/entity helpers, factories, checksum implementation, and DB cleanup.
- **Control flow:** Inline parsers translate flag strings to enum values with fallback/assert behavior. Inline key functions preserve sort order by big-endian fixed-width chunks and can reverse keys back to expected-state indexes.
- **State and persistence behavior:** Declares shared runtime objects and `KeyGenContext`. No direct persistence in the header, but its APIs define the key/value formats persisted by db_stress and the expected-values mapping used for verification.
- **Dependencies and integration points:** Pulls in DBImpl/version internals, stress env/listener/shared/test base, RocksDB public APIs, utilities, fault injection, merge operators, blob DB, gflags compatibility, and coding/compression helpers. This is the main include surface for stress variants.
- **Risks:** The broad include and flag surface makes this a high-coupling header. Key encoding assumes `key_gen_ctx` is initialized consistently; parser fallbacks can silently choose defaults after invalid input; many declarations exist only under `GFLAGS`.
- **Test signals:** Compile coverage for all stress modes, flag validator behavior, key round-trip tests, prefix-bound tests, and stress runs using variable key lengths/wide columns/checksums.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compaction_filter.h -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compaction_filter.h

- **Purpose:** Provides a db_stress compaction filter that removes or purges keys known to be absent in `SharedState`, without mutating state during compaction.
- **Important APIs/types/functions:** Defines `DbStressCompactionFilter : CompactionFilter` with `FilterV2` and `Name`; defines `DbStressCompactionFilterFactory : CompactionFilterFactory` with `SetSharedState`, `CreateCompactionFilter`, and `Name`.
- **Control flow:** `FilterV2` keeps keys when no shared state is available, when keys look like batched-snapshot leftovers, or when the per-key mutex cannot be acquired. Otherwise it decodes the key number, checks expected existence/overwrite policy under the key mutex, and returns `kRemove`, `kPurge`, or `kKeep`.
- **State and persistence behavior:** Reads `SharedState` expected key state but does not mutate it. Compaction decisions affect persisted SST output by dropping keys/tombstones.
- **Dependencies and integration points:** Depends on `db_stress_common.h`, `db_stress_shared_state.h`, and `rocksdb/compaction_filter.h`; configured in db_stress options when compaction-filter stress is enabled.
- **Risks:** Key decoding assumes the db_stress key format and user timestamp suffix size. A failed `TryLock` conservatively keeps keys, reducing filter coverage. Current TODO notes lack of wide-column blob entity coverage for newer filter APIs.
- **Test signals:** Stress verification should remain consistent after compactions; assertions catch timestamp/key decoding issues; coverage should include overwrite and no-overwrite expected-state modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compaction_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compaction_service.cc -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compaction_service.cc

- **Purpose:** Implements waiting/result interpretation for the db_stress remote compaction service.
- **Important APIs/types/functions:** Implements `DbStressCompactionService::Wait`.
- **Control flow:** Polls `SharedState::GetRemoteCompactionResult` until a result appears or the service is aborted. Successful results return `kSuccess`; failures may fall back to local compaction when configured or retryable, otherwise serialize the failure into a `CompactionServiceResult` and return `kFailure`.
- **State and persistence behavior:** Reads remote compaction result state from `SharedState`; writes serialized failure details into the caller-provided result string when needed. Sleeps through `Env::Default`.
- **Dependencies and integration points:** Includes the service header, `db_stress_test_base.h`, and `rocksdb/env.h`; used by RocksDB compaction service callbacks configured during stress tests.
- **Risks:** Wait is polling-based and depends on worker threads publishing results. Empty result strings on failure need successful serialization to propagate status. Abort returns before late results are installed.
- **Test signals:** Compaction service status (`kSuccess`, `kUseLocal`, `kFailure`, `kAborted`), fallback behavior under injected retryable errors, and primary DB compaction completion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compaction_service.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compaction_service.h -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compaction_service.h

- **Purpose:** Declares and mostly implements a simulated remote `CompactionService` for db_stress.
- **Important APIs/types/functions:** Defines `DbStressCompactionService`, `kClassName`, `Name`, `kWaitIntervalInMicros`, `kTempOutputDirectoryPrefix`, `Schedule`, `Wait`, `OnInstallation`, and `CancelAwaitingJobs`.
- **Control flow:** `Schedule` builds a job ID and temp output path, enqueues work in `SharedState`, and returns success unless aborted. `OnInstallation` reads the serialized result, deletes output files/directories, and removes the result from shared state. `CancelAwaitingJobs` sets the abort flag.
- **State and persistence behavior:** Holds `SharedState*`, atomic abort state, and fallback policy. Creates temp output directory names and cleans output directories through `Env::Default`; actual compaction output is produced by worker threads.
- **Dependencies and integration points:** Depends on compaction job/service APIs, `SharedState`, options, and fault-injection headers. Paired with `RemoteCompactionWorkerThread` in `db_stress_common.cc`.
- **Risks:** Cleanup is best-effort and TODO-marked on failure. Job IDs combine DB identity/session/job values and must stay unique. Aborted service sends new jobs to local compaction and waiting jobs to aborted.
- **Test signals:** Remote compaction queue/result counts, cleanup of temp output dirs, fallback status under abort/failure, and stress verification after compaction installation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compaction_service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compression_manager.cc -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compression_manager.cc

- **Purpose:** Registers the db_stress custom compression manager with RocksDB's object registry.
- **Important APIs/types/functions:** Implements `DbStressCustomCompressionManager::Register`.
- **Control flow:** Uses `std::call_once` to allow unsupported format versions for tests and add a `CompressionManager` factory under the custom compatibility name.
- **State and persistence behavior:** Mutates the process-global object registry once. This enables later DB opens to read SSTs written with the custom compatibility name.
- **Dependencies and integration points:** Includes `db_stress_compression_manager.h` and `rocksdb/utilities/object_registry.h`; used by stress setup when custom compression manager mode is enabled.
- **Risks:** Registration must happen before reading files that require the custom compatibility name. `TEST_AllowUnsupportedFormatVersion()` affects test process behavior globally.
- **Test signals:** Successful DB reopen/read of SST files requiring `DbStressCustom1`; object-registry factory lookup.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compression_manager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compression_manager.h -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compression_manager.h

- **Purpose:** Defines a custom `CompressionManager` used by db_stress to exercise custom compression/decompression paths and compatibility-name persistence.
- **Important APIs/types/functions:** Defines `DbStressCustomCompressionManager` with `Name`, `CompatibilityName`, `SupportsCompressionType`, `GetCompressor`, `GetDecompressor`, `GetDecompressorForTypes`, and static `Register`.
- **Control flow:** Supports built-in compression plus custom AA/AB/AC types. `GetCompressor` randomly chooses among the requested type and custom test algorithms; decompressor instances can restrict allowed types.
- **State and persistence behavior:** Holds a shared built-in default compression manager. Compression choices affect SST block contents and stored compression metadata.
- **Dependencies and integration points:** Uses test utility custom compressor/decompressor implementations and built-in v2 compression manager. Registration is implemented in the `.cc` file.
- **Risks:** Random compressor selection increases coverage but can complicate reproducibility if seed/thread-local random state changes. Compatibility name must remain stable for old SST readability.
- **Test signals:** Stress runs with custom compression should verify writes, reads, compactions, and reopen across files compressed with multiple custom algorithms.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_compression_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_driver.cc -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_driver.cc

- **Purpose:** Runs a configured `StressTest` instance: initializes DBs, launches worker/background threads, coordinates operation and verification phases, reports stats, and shuts down helper threads.
- **Important APIs/types/functions:** Implements `ThreadBody`, `RunStressTestImpl`, and `RunStressTest`.
- **Control flow:** Worker threads optionally verify crash-recovery state, signal initialization, wait for start, run `OperateDb`, wait for verification start, verify DB, and signal done. The driver initializes DB/options, starts background verification, remote compaction, pool-size, and compressed-cache threads as needed, coordinates condition-variable barriers, reports results, and stops background threads.
- **State and persistence behavior:** Mutates `SharedState` phase counters/flags. Initializes and destroys `unverified` subdirs when preserving unverified changes. Configures fault injection before operations and prints statistics after completion.
- **Dependencies and integration points:** Depends on `db_stress_shared_state.h`, `db_stress_common.h`, fault injection, raw env threading, and `StressTest` virtual methods. Called by the top-level db_stress tool after flags/options are set.
- **Risks:** Barrier correctness depends on all worker/background threads updating `SharedState` counters. Some background thread state objects are stack-allocated and must outlive their threads; shutdown waits enforce that. `std::call_once` means some global background threads are tied to the first DB's shared state.
- **Test signals:** Initialization/operation/verification phase log lines, merged stats, verification failure flag, crash-recovery pass/fail messages, and background-thread-finished message.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_driver.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_driver.h -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_driver.h

- **Purpose:** Declares the db_stress driver entry points used to run a `SharedState`/`StressTest` configuration.
- **Important APIs/types/functions:** Declares `ThreadBody(void*)` and `RunStressTest(SharedState*)` under `GFLAGS`.
- **Control flow:** Header only; implementation in `.cc` owns thread body and stress run orchestration.
- **State and persistence behavior:** No direct state; functions operate on `SharedState`.
- **Dependencies and integration points:** Includes `db_stress_shared_state.h` and `db_stress_test_base.h`; used by the db_stress top-level tool.
- **Risks:** The header has an include before `#ifdef GFLAGS`, so non-gflags consumers still parse `db_stress_shared_state.h`. API is intentionally narrow, so driver changes require updating only these declarations.
- **Test signals:** Compile/link coverage of db_stress driver and execution through `RunStressTest`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_env_wrapper.h -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_env_wrapper.h

- **Purpose:** Provides filesystem wrappers used by db_stress to assert IO activity metadata, validate SST checksum propagation, wrap file objects, and optionally preserve MANIFEST history.
- **Important APIs/types/functions:** Defines `CheckIOActivity`, `DbStressRandomAccessFileWrapper`, `DbStressWritableFileWrapper`, and `DbStressFSWrapper`. Overrides random read, multi-read, prefetch, async read, append/positioned append, truncate, close, flush, sync/fsync, allocate, range sync, `NewRandomAccessFile`, `NewWritableFile`, and `DeleteFile`.
- **Control flow:** File wrappers assert expected `IOOptions::io_activity` in debug builds then delegate to target files. `NewRandomAccessFile` additionally checks SST file checksum function/value invariants. `DeleteFile` either delegates or renames MANIFEST files to `_renamed_` unless exempted.
- **State and persistence behavior:** Wraps filesystem I/O and can persist renamed MANIFEST files instead of deleting them. `if_preserve_all_manifests` controls manifest retention.
- **Dependencies and integration points:** Depends on `db_stress_common.h`, filename parsing, thread status utilities, and file checksum constants. Used when stress config wraps the base filesystem for DB I/O.
- **Risks:** Debug-only IO activity assertions can expose incorrect call-site metadata. Manifest rename preservation requires cleanup through raw env paths elsewhere. The filename substring check can theoretically false-positive on paths containing `MANIFEST-`.
- **Test signals:** Assertions on IO activity/checksum metadata, presence of renamed MANIFEST files for debugging, and successful reads/writes through wrapper delegation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_env_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_filters.cc -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_filters.cc

- **Purpose:** Builds db_stress SST query filter configuration fixtures for range-query filter testing.
- **Important APIs/types/functions:** Defines anonymous `VariableWidthExtractor` and `FixedWidthExtractor`, shared min/max filters for key segments 0-3, configuration sets `fooConfigs1`, `fooConfigs2`, `barConfigs2`, static manager data, and `DbStressSqfcManager()`.
- **Control flow:** Extractors split keys into segment endpoints either by variable zero-byte delimiters or fixed 8-byte chunks. `DbStressSqfcManager` constructs a shared `SstQueryFilterConfigsManager` once with two versions of named configs and returns it.
- **State and persistence behavior:** Maintains a process-static shared manager after first call. Filter configs affect SST/table query filtering metadata and range-query read behavior, not external files directly.
- **Dependencies and integration points:** Uses `rocksdb/experimental.h` SQFC APIs through `db_stress_filters.h`; consumed when stress flags enable SQFC for range queries.
- **Risks:** The `std::once_flag` is local non-static in the function while `mgr` is static; this means `call_once` does not actually provide persistent once semantics and initialization is attempted each call. Assertions catch manager creation failure only in debug builds.
- **Test signals:** Range queries using SQFC table filters, manager creation status, and correctness of prefix/range scan results under configured filter versions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_filters.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_filters.h -->
# Research: sources/storage-engines/rocksdb/db_stress_tool/db_stress_filters.h

- **Purpose:** Declares the db_stress SST query filter configuration manager accessor.
- **Important APIs/types/functions:** Declares `experimental::SstQueryFilterConfigsManager& DbStressSqfcManager()` under `GFLAGS`.
- **Control flow:** Header only; implementation constructs and returns the manager in `.cc`.
- **State and persistence behavior:** No header state. The returned manager governs in-process SQFC configuration used by stress reads.
- **Dependencies and integration points:** Includes `rocksdb/experimental.h`; used by stress setup and range-query code that needs SQFC filters.
- **Risks:** API availability is gated on `GFLAGS`; callers must link `db_stress_filters.cc`.
- **Test signals:** Compile/link coverage and stress runs with `FLAGS_use_sqfc_for_range_queries`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_filters.h -->
