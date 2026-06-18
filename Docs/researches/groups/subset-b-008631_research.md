# subset-b-008631 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_test_base.cc -->
## sources/storage-engines/rocksdb/db_stress_tool/db_stress_test_base.cc

### Purpose

`db_stress_test_base.cc` implements the non-abstract mechanics behind RocksDB's `db_stress` test harness. It owns the lifecycle of a stress-test database, option construction, DB open/reopen behavior, randomized operation dispatch, transaction helper paths, iterator verification, backup/checkpoint validation, fault-injection handling, and a large set of API probes. Concrete stress-test variants subclass the `StressTest` interface declared in the header and supply data-model-specific operations such as `TestPut`, `TestGet`, `VerifyDb`, and external-file ingestion.

The implementation is compiled only when `GFLAGS` is enabled and is driven almost entirely by global stress-test flags from `db_stress_common.h`. It is not a library component for normal application use; it is a dense integration test driver for exercising RocksDB combinations that are hard to cover with small unit tests.

### Important APIs, types, and helpers

The anonymous namespace provides local scaffolding:

- `StressReadScopedBlockBufferProvider` implements `ReadScopedBlockBufferProvider` with aligned buffers and strict allocation accounting. Its destructor aborts if any read-scoped lease was not cleaned up, making it a leak/lifetime detector for the read path.
- `CreateFilterPolicy()` chooses no filter, Bloom, or Ribbon policy from `FLAGS_bloom_bits` and `FLAGS_bloom_before_level`.
- `OpenFaultInjectionConfig`, `EnableThreadLocalOpenFault()`, `MaybeEnableOpenFaultInjection()`, and `NeedsFaultInjection()` translate open/runtime fault flags into `FaultInjectionTestFS` behavior.

The main `StressTest` implementation covers:

- Construction and cleanup: `StressTest::StressTest()`, `CleanUp()`, `CleanUpColumnFamilies()`, `InitializeListenersForOpen()`, and getters for paths/env/fs.
- Cache and options setup: `NewCache()`, `BuildOptionsTable()`, `InitializeOptionsFromFile()`, `InitializeOptionsFromFlags()`, `InitializeOptionsGeneral()`, `InitializeMergeOperator()`, `CheckAndSetOptionsForUserTimestamp()`, and `ShouldDisableAutoCompactionsBeforeVerifyDb()`.
- DB lifecycle: `InitDb()`, `FinishInitDb()`, `TrackExpectedState()`, `Open()`, `Reopen()`, `PreloadDbAndReopenAsReadOnly()`, `RecordManifestStateBeforeReopen()`, and `VerifyManifestNotRewritten()`.
- Transaction support: `NewTxn()`, `CommitTxn()`, `ExecuteTransaction()`, `ProcessRecoveredPreparedTxns()`, `ProcessRecoveredPreparedTxnsHelper()`, and `IsExpectedTxnError()`.
- Random operation driver: `OperateDb()`, which selects and executes reads, writes, deletes, range deletes, iteration, backup/checkpoint, flush/compaction, WAL, snapshot, property, metadata, and custom operations.
- Verification helpers: `AssertSame()`, `ProcessStatus()`, the `VerificationAbort()` overloads, `DebugString()`, iterator comparison via `TestIterate()`, `TestIterateAttributeGroups()`, `TestIterateImpl()`, `TestMultiScan()`, `VerifyIterator()`, `DumpIteratorDivergenceDiagnostics()`, `GetRangeHash()`, and snapshot release checks.
- API probes: `TestGetLiveFiles*`, `TestGetSortedWalFiles()`, `TestGetCurrentWalFile()`, `TestGetProperty()`, `TestGetPropertiesOfAllTables()`, `TestApproximateSize()`, `TestCompactFiles()`, `TestCompactRange()`, `TestPromoteL0()`, `TestFlush()`, `TestResetStats()`, `TestPauseBackground()`, `TestDisableFileDeletions()`, `TestDisableManualCompaction()`, `TestAbortAndResumeCompactions()`, `TestBackupRestore()`, and `TestCheckpoint()`.

### Control flow

Initialization starts in `InitDb()`: the test prints environment settings, opens the DB, and prepares a table of dynamic option mutations. `FinishInitDb()` then optionally preloads read-only DB contents, restores expected values from a persisted history trace, processes recovered prepared transactions, and wires the compaction filter factory to `SharedState`.

`Open()` is the central lifecycle function. It initializes or loads `Options`, layers the stress-test filesystem and optional fault-injection filesystem into `options_.env`, rebuilds an `SstFileManager` on that env when needed, configures compression managers, validates incompatible flag combinations, discovers or creates column-family descriptors, and opens one of several DB flavors: ordinary `DB`, read-only `DB`, stackable `BlobDB`, `OptimisticTransactionDB`, `TransactionDB`, `DBWithTTL`, and optionally a secondary instance. It also supports fault-injected open retries for non-transaction DBs and verifies that recovered sequence numbers are not behind `SharedState`.

`OperateDb()` is the hot loop. For each reopen epoch, all threads periodically vote for a synchronized `Reopen()`. Within each epoch it sets read/write options from flags, enables thread-local fault injection in debug builds, then repeatedly chooses operations by flag-controlled probabilities. Some maintenance probes are sampled independently before the main read/write/delete/iterate/custom dispatch. User writes may temporarily disable fault injection when unsynced-data-loss tracing cannot yet tolerate missing history entries. Reads branch into `Get`, `MultiGet`, `GetEntity`, or `MultiGetEntity`; iterates branch into `MultiScan`, expected-state iterator verification, normal iterators, or attribute-group iterators.

`Reopen()` cancels background work when needed, releases column-family handles, persists WAL contents before close, optionally calls `Close()`, resets DB owner pointers, records MANIFEST state, calls `Open(..., reopen=true)`, verifies MANIFEST/CURRENT reuse expectations, and restarts history tracing when data-loss-sensitive tracking is enabled.

### State and persistence behavior

The class stores DB identity and paths (`db_index_`, `db_label_`, `db_path_`, expected values path, secondary path), filesystem wrappers (`DbStressFSWrapper`, `FaultInjectionTestFS`, `CompositeEnvWrapper`), option and cache objects, DB owner/raw pointers, transaction DB pointers, column-family handles/names, dynamic option tables, secondary DB state, and MANIFEST verification state.

Persistent state is deliberately stressed rather than abstracted away. `TrackExpectedState()` and `FinishInitDb()` coordinate with `SharedState` history when WAL disabling, manual WAL flushing, or sync-fault injection could cause prefix recovery. `PreloadDbAndReopenAsReadOnly()` writes all keys, commits expected values, flushes, closes, and reopens in read-only mode. `ProcessRecoveredPreparedTxns()` handles prepared transactions left by a prior crash by marking affected expected keys as unknown/pending and randomly committing or rolling back recovered transactions. `TestBackupRestore()` and `TestCheckpoint()` create temporary persistent copies, reopen them with reconstructed options, validate sampled keys against the shared expected state, and clean up directories with fault injection disabled around cleanup.

MANIFEST persistence has explicit test logic. `RecordManifestStateBeforeReopen()` chooses a mode based on `reuse_manifest_on_open`, `optimize_manifest_for_recovery`, best-efforts recovery, fault-injection, DB ID writes, and recovery-flush flags, then records the MANIFEST number/size and `CURRENT` file contents. `VerifyManifestNotRewritten()` warns or exits depending on the strictness mode if the MANIFEST was recreated, grew unexpectedly, or `CURRENT` changed.

### Dependencies and integration points

This file integrates most of the db_stress subsystem: common flags and key/value generators, `SharedState`, `ThreadState`, stress listeners, compaction filters/services, table properties collectors, custom compression managers, filters, wide merge operators, and driver globals such as caches/rate limiters. It exercises public RocksDB APIs (`DB`, `TransactionDB`, `OptimisticTransactionDB`, `BackupEngine`, `Checkpoint`, `DBWithTTL`, `BlobDB`, `Options`, iterators, snapshots, WAL APIs, properties, metadata APIs), internal utilities (`DBImpl`, `InternalStats`, `ParseFileName`, `ReadFileToString`, CRC helpers), and test utilities (`FaultInjectionTestFS`, sync/kill-point support, bytewise timestamp comparator).

The subclass integration surface is important: concrete tests override logical operations and may customize column families, key generation, key-locking policy, additional listeners, transaction DB options, restored DB options, custom operations, and control column-family handles. This base class supplies concurrency, lifecycle, fault, and validation policy around those hooks.

### Risks and sharp edges

- The file is flag-dense; many behaviors rely on global flags being mutually compatible. Several incompatibilities are checked with `exit(1)`, while others rely on assertions.
- DB pointer ownership is delicate. `db_owner_`, `db_`, `txn_db_`, `optimistic_txn_db_`, `db_aptr_`, secondary DB handles, and raw column-family handles must be updated in the right order across open/reopen/cleanup.
- Fault injection is intentionally disabled around some validation and cleanup paths. Missing a disable/reenable region can cause false positives, while over-disabling can hide bugs.
- `Open()` only supports open fault injection on the non-transaction path. Transaction DB paths assert successful open.
- Snapshot and column-family interactions have acknowledged unsafe areas when column families can be dropped concurrently. Some APIs assert `FLAGS_clear_column_family_one_in == 0`.
- Iterator verification must skip undefined combinations involving prefix extractors, bounds, timestamps, and unsupported reverse scans. Incorrect skip logic can either hide a real iterator bug or report a false divergence.
- Backup/checkpoint validation samples limited keys, so it is a signal rather than a full equivalence proof.
- Manifest verification uses the default env to list/read DB files while the DB itself uses `GetDbEnv()`; this is intentional for local DB paths but is a coupling to filesystem assumptions.

### Test signals

The strongest signals are verification failures recorded in `SharedState`, error counters in thread stats, fatal exits/assertions, and stderr diagnostics. Specific test signals include snapshot stability via `AssertSame()`, iterator/control-iterator equivalence, value/wide-column consistency checks, range CRC stability across compaction, restored/checkpoint sampled-key checks, property API availability checks, WAL lock invariants, MANIFEST/CURRENT rewrite warnings or fatal failures, and status processing that treats only injected retryable errors as ignorable. Successful execution with broad flag coverage is itself the intended integration signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_test_base.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_test_base.h -->
## sources/storage-engines/rocksdb/db_stress_tool/db_stress_test_base.h

### Purpose

`db_stress_test_base.h` declares the `StressTest` base class and option-initialization helpers used by RocksDB's `db_stress` tool. It defines the shared interface between the generic stress harness and concrete stress-test implementations. The base class owns database lifecycle, common randomized API exercises, transactions, snapshots, backup/checkpoint tests, iterator validation, fault-injection utilities, option mutation, and verification reporting, while subclasses provide the data-model-specific operations.

The header is guarded by `GFLAGS`, matching the flag-driven stress binary. It also includes `rocksdb/io_status.h` before the `GFLAGS` block, then exposes the rest of the declarations only when the stress tool is buildable.

### Important APIs, types, and functions

The public API is intentionally small:

- `StressTest::StressTest()` and virtual destructor construct the test for one DB index/path set.
- Path/env accessors expose DB label/path, expected-values directory, secondaries directory, optional `FaultInjectionTestFS`, and DB env.
- `NewCache()` and `GetBlobCompressionTags()` provide static setup helpers.
- `BuildOptionsTable()`, `InitDb()`, `FinishInitDb()`, `TrackExpectedState()`, `OperateDb()`, `VerifyDb()`, `ContinuouslyVerifyDb()`, `PrintStatistics()`, `EnableAutoCompaction()`, `GetOptions()`, and `CleanUp()` form the main lifecycle and execution surface.
- `MightHaveUnsyncedDataLoss()` centralizes whether expected-state history must account for possible prefix recovery.
- `IsErrorInjectedAndRetryable()` and `IsExpectedTxnError()` classify statuses that should not be treated as ordinary correctness failures.

The protected API is the subclass contract and common operation library:

- Required subclass hooks include `VerifyDb()`, `ContinuouslyVerifyDb()`, `IsStateTracked()`, `TestGet()`, `TestMultiGet()`, `TestGetEntity()`, `TestMultiGetEntity()`, `TestPrefixScan()`, `TestPut()`, `TestDelete()`, `TestDeleteRange()`, and `TestIngestExternalFile()`.
- Optional hooks include `MaybeClearOneColumnFamily()`, `ShouldAcquireMutexOnKey()`, `GenerateColumnFamilies()`, `GenerateKeys()`, `TestKeyMayExist()`, `TestCompactRange()`, `TestPromoteL0()`, `GetControlCfh()`, `TestIterate()`, `TestIterateAttributeGroups()`, `TestIterateAgainstExpected()`, `TestBackupRestore()`, `PrepareOptionsForRestoredDB()`, `TestCheckpoint()`, `TestApproximateSize()`, `TestCustomOperations()`, `RegisterAdditionalListeners()`, and `PrepareTxnDbOptions()`.
- Transaction helpers include `NewTxn()`, `CommitTxn()`, `ExecuteTransaction()`, `ProcessRecoveredPreparedTxns()`, and `ProcessRecoveredPreparedTxnsHelper()`.
- Verification helpers include `AssertSame()`, `GetRangeHash()`, `GetWhiteBoxKeys()`, `VerifyIterator()`, `DumpIteratorDivergenceDiagnostics()`, `ProcessStatus()`, the `VerificationAbort()` overloads, and `DebugString()`.
- Snapshot, property, compaction, WAL/live-file metadata, background-work, and option helpers are declared for use inside the base implementation and subclasses.

The header also declares two enums:

- `LastIterateOp` records the most recent iterator positioning operation so verifier logic can distinguish seek, seek-for-prev, seek-to-first/last, and next/prev behavior.
- `ManifestVerifyMode` records whether reopen should skip MANIFEST checks, warn about reuse/no-write expectations, or enforce strict no-rewrite behavior.

Free functions at the end initialize options from an OPTIONS file or flags, fill general stress defaults, configure user-defined timestamps, and decide whether compaction should be disabled before verification.

### Control flow defined by the interface

The intended flow is: create `StressTest`, call `InitDb()` to open and configure, call `FinishInitDb()` for post-open shared-state work, optionally call `TrackExpectedState()` for history tracing, run worker threads through `OperateDb()`, use `VerifyDb()` or `ContinuouslyVerifyDb()` for correctness checks, print statistics, then `CleanUp()`.

During operation the base class calls subclass hooks at randomized points. Key and column-family generators allow subclasses to expand one random choice into multi-key or multi-CF operations. The base class wraps those hooks with shared read/write options, fault-injection policy, expected-status handling, key locks for range deletes or backup/checkpoint validation, and thread stats.

The transaction helpers are intended to hide pessimistic versus optimistic transaction setup from subclasses. `ExecuteTransaction()` creates a transaction, runs a callback, commits, and retries optimistic `TryAgain` failures within a fixed bound.

### State and persistence behavior

`StressTest` stores both persistent DB-facing state and in-memory test state. Persistent-facing members include paths, env/filesystem wrappers, cache/filter/index factories, `Options`, DB owner/raw pointers, transaction DB pointers, secondary DB handles, column-family handles/names, and MANIFEST file-number/size/current-file state. In-memory test state includes dynamic option mutation tables, reopen counters, preload completion, stopped-state tracking, atomic DB pointer publication, and generated column-family naming.

The header makes persistence expectations visible through helpers such as `MightHaveUnsyncedDataLoss()`, `TrackExpectedState()`, `PreloadDbAndReopenAsReadOnly()`, recovered prepared transaction processing, backup/checkpoint hooks, snapshot acquisition/release checks, and MANIFEST reopen verification methods. It also exposes timestamp helpers that can set older read timestamps for point lookups and range scans when user-defined timestamps are enabled and persisted.

### Dependencies and integration points

The declaration depends on RocksDB core types (`DB`, `Options`, `Status`, `ReadOptions`, `WriteOptions`, `Cache`, `ColumnFamilyHandle`, `Snapshot`, `Transaction`, `TransactionDB`, `OptimisticTransactionDB`, `TransactionDBOptions`), experimental query-filter configuration, user-defined index factories, fault-injection filesystems, and db_stress support types (`SharedState`, `ThreadState`, common flags/helpers, and `CompositeEnvWrapper`). The class is the central bridge between the db_stress driver and concrete test modes such as batched, no-batch, CF-consistency, transaction, wide-column/entity, and custom operation stress tests.

### Risks and sharp edges

- The base class has many virtual hooks with assumptions enforced only by comments, assertions, or surrounding flag logic. Subclasses must update expected state consistently and respect key-locking requirements when they opt into state tracking.
- Several helpers expose raw pointers and manual handle ownership. Column-family and secondary handles are deleted by `CleanUpColumnFamilies()`, so subclasses must not outlive or double-delete them.
- The transaction and timestamp APIs have explicit incompatibilities. For example, user timestamps reject TransactionDB, batched modes, and external ingestion in the implementation.
- Iterator verification is templated and depends on a caller-provided `verify_func`; incorrect hook behavior can make verifier failures hard to diagnose.
- `GetControlCfh()` defaults to the tested column family, but subclasses that use a mirrored/control CF must override it correctly or iterator comparisons will be invalid.
- Fault-injection status classification is strict: injected retryable errors can be ignored in many paths, but data-loss statuses and unexpected transaction errors should surface as failures.

### Test signals

The header exposes the test signals that concrete implementations should use: `ProcessStatus()` for status-to-verification-failure handling, `VerificationAbort()` overloads for detailed failures, `AssertSame()` for snapshot stability, iterator verification and divergence diagnostics, `GetRangeHash()` for compaction non-mutation checks, live-file/property/WAL metadata API probes, backup/checkpoint sampled validation, and `PrintStatistics()`. Subclasses should treat a `SharedState` verification failure or stop request as authoritative and avoid continuing destructive work after it is set.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db_stress_tool/db_stress_test_base.h -->
