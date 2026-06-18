# subset-b-008664 research

Grouped research for RocksDB Java tests under `sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb`. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BytewiseComparatorRegressionTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BytewiseComparatorRegressionTest.java

## Purpose

Regression coverage for Java bytewise comparator behavior after historical ordering bugs. It verifies that Java `BytewiseComparator`, the default comparator, and `BuiltinComparator.BYTEWISE_COMPARATOR` order bytes as unsigned bytewise keys, then checks `SstFileWriter` can write SST keys that previously exposed the same comparator issue.

## Important APIs, control flow, and dependencies

The tests use `Options.setComparator`, `RocksDB.open`, `RocksIterator`, `SstFileWriter`, `EnvOptions`, `Slice`, and helper hex parsing. `performTest` writes three byte-array keys, iterates from the first key, and asserts the exact order. `testSST` writes two hex-decoded binary keys to an external SST with a Java comparator.

## State, persistence, risks, and test signals

Temporary DB and SST folders isolate persisted state. The key risk is signed-byte comparison in Java or inconsistent Java/C++ comparator naming causing sorted iteration or SST construction failures. Signals are exact array-order assertions and successful `SstFileWriter.finish()` for non-text binary keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BytewiseComparatorRegressionTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CheckPointTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CheckPointTest.java

## Purpose

Tests Java checkpoint binding behavior for creating physical DB snapshots and exporting a column family for later import workflows.

## Important APIs, control flow, and dependencies

The suite uses `Checkpoint.create`, `createCheckpoint`, `exportColumnFamily`, `ExportImportFilesMetaData`, `RocksDB.open`, and `Options`. The main checkpoint test writes `key`, creates `snapshot1`, writes `key2`, creates `snapshot2`, then reopens both snapshot directories to confirm snapshot isolation. `exportColumnFamily` exports metadata twice around a second write.

## State, persistence, risks, and test signals

This is persistence-heavy: checkpoint directories must contain enough SST/MANIFEST/WAL state to reopen independently. Exported metadata must reflect the column-family files at export time. Risks include invalid DB handles, invalid paths, and binding lifetime issues; negative tests cover null DB, closed DB, and illegal checkpoint paths. Signals are reopened DB reads and expected exception types.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CheckPointTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ClockCacheTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ClockCacheTest.java

## Purpose

Smoke-tests construction and native ownership of the Java `ClockCache` wrapper.

## Important APIs, control flow, and dependencies

The test creates a `ClockCache` with capacity, shard bits, and strict capacity limit in a try-with-resources block. It depends on `RocksNativeLibraryResource` and the `Cache` base type.

## State, persistence, risks, and test signals

No DB state is persisted. The important state is native cache allocation and release through `close()`. The risk is JNI constructor mismatch or leaking native cache handles. Passing construction and disposal without exception is the test signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ClockCacheTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ColumnFamilyOptionsTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ColumnFamilyOptionsTest.java

## Purpose

Comprehensive JNI contract coverage for `ColumnFamilyOptions`: copy construction, property parsing, scalar option getters/setters, enum round-trips, nested option objects, compaction filters, memtable/prefix helpers, defaults helpers, and path lists.

## Important APIs, control flow, and dependencies

The test exercises `ColumnFamilyOptions`, `ConfigOptions`, `CompressionOptions`, `CompactionOptionsUniversal`, `CompactionOptionsFIFO`, `DbPath`, `Cache`, `ConcurrentTaskLimiterImpl`, memtable configs, comparator selection, compression and compaction enums, prefix extractor helpers, and `RemoveEmptyValueCompactionFilterFactory`. Most tests create one options object, set a randomly generated or fixed value, and assert the getter returns the same value. Property parsing tests verify valid props, ignored unknown options under `ConfigOptions.setIgnoreUnknownOptions(true)`, and null/empty/unknown failure cases.

## State, persistence, risks, and test signals

No DB is opened, but native option state is allocated and freed repeatedly. Nested Java wrappers such as compression options, compaction options, cache, limiter, filters, and path lists must preserve references correctly across JNI. Risks include stale native field names, signed/unsigned numeric truncation, enum byte mapping drift, and lifetime bugs when options hold native children. Assertions cover every exposed option family plus old-default values and fluent method identity.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ColumnFamilyOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ColumnFamilyTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ColumnFamilyTest.java

## Purpose

Integration coverage for Java column-family lifecycle and API variants: descriptors, listing, default family handles, opening DBs with multiple families, aliases for the default CF across DB flavors, fixed-buffer reads, write batches, iterators, multi-get, properties, dropped handles, binary names, Unicode names, and explicit handle destruction.

## Important APIs, control flow, and dependencies

The file uses `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `RocksDB.open`, `openReadOnly`, `OptimisticTransactionDB`, `TransactionDB`, `TtlDB`, `WriteBatch`, `WriteOptions`, `ReadOptions`, `RocksIterator`, `multiGetAsList`, `getProperty`, `getAggregatedLongProperty`, `dropColumnFamily`, `dropColumnFamilies`, and `destroyColumnFamilyHandle`. Tests open temporary DBs, create or list column families, perform per-CF writes/deletes/gets, then validate isolation and metadata. The default-CF synonym tests reopen DBs with `RocksDB.DEFAULT_COLUMN_FAMILY` in different descriptor positions and across transaction/TTL variants.

## State, persistence, risks, and test signals

Column-family metadata is persisted in the DB manifest and is verified through reopen/list operations. The suite also checks Java handle state after drops and explicit destruction. Risks include requiring the default CF in the descriptor list, using disposed handles, off-by-one errors in offset/length buffer reads, multi-get CF/key count mismatches, incorrect binary name handling, and missing cleanup of returned handles. Signals are value isolation by CF, exact returned byte arrays, exception expectations, property availability, iterator contents, and ownership flags.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ColumnFamilyTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactRangeOptionsTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactRangeOptionsTest.java

## Purpose

Validates Java accessors for manual compaction options and cancellation state.

## Important APIs, control flow, and dependencies

The test uses `CompactRangeOptions`, `BottommostLevelCompaction`, and `Slice`. It round-trips `exclusiveManualCompaction`, `bottommostLevelCompaction`, `changeLevel`, `targetLevel`, `targetPathId`, `allowWriteStall`, `maxSubcompactions`, `fullHistoryTSLow`, and `canceled`. Cancellation is toggled by repeated `setCanceled` calls.

## State, persistence, risks, and test signals

No DB state is created. The important state is native option storage, including nullable timestamp slices and the sticky cancellation flag. Risks are enum drift, null slice handling, and incorrect boolean defaults. Signals are default assertions, round-trip equality, and cancellation behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactRangeOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionFilterFactoryTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionFilterFactoryTest.java

## Purpose

Tests that a Java compaction filter factory attached to `ColumnFamilyOptions` is invoked through native compaction for a column family.

## Important APIs, control flow, and dependencies

The test uses `RemoveEmptyValueCompactionFilterFactory`, `ColumnFamilyOptions.setCompactionFilterFactory`, `ColumnFamilyDescriptor`, `DBOptions`, `RocksDB.open`, `flush`, `compactRange`, and `keyMayExist`. It opens default plus `new_cf`, writes a normal value and an empty value to the filtered CF, flushes, compacts, and verifies the normal value remains while the empty value may not exist.

## State, persistence, risks, and test signals

Data moves from memtable to SST and through compaction, so this validates native callback plumbing and CF-specific option persistence into the opened DB. Risks include Java callback lifetime, filter factory ownership, and compaction not being triggered deterministically. Signals are retained value readback and false `keyMayExist` for the filtered empty value.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionFilterFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionJobInfoTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionJobInfoTest.java

## Purpose

Checks default Java wrapper values for `CompactionJobInfo`, the metadata object delivered to compaction event listeners.

## Important APIs, control flow, and dependencies

Each test creates an empty `CompactionJobInfo` and reads a single field: column family name, `Status`, thread/job ids, input/output levels, input/output file lists, table properties, compaction reason, compression type, and nested `CompactionJobStats`.

## State, persistence, risks, and test signals

No compaction is run. The state under test is the default native object. Risks are null object returns, wrong default enum values, and list/map conversion failures. Signals are empty collections, `Status.Code.Ok`, zero numeric fields, `kUnknown` reason, `NO_COMPRESSION`, and non-null stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionJobInfoTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionJobStatsTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionJobStatsTest.java

## Purpose

Verifies default and reset behavior for the Java `CompactionJobStats` wrapper.

## Important APIs, control flow, and dependencies

The file constructs `CompactionJobStats`, calls `reset` and `add`, and reads all exposed counters: elapsed time, input/output record and file counts, manual-compaction flag, byte totals, replaced/deletion/corrupt counts, file IO timing counters, output key prefixes, and single-delete stats.

## State, persistence, risks, and test signals

No DB state is involved. The important state is the native stats object and Java conversion of integral counters and byte-prefix arrays. Risks include newly added native fields not being exposed consistently, nonzero uninitialized memory, and incorrect reset/add JNI binding. Signals are zero/false/empty defaults and no exception from adding another stats object.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionJobStatsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionOptionsFIFOTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionOptionsFIFOTest.java

## Purpose

Accessor coverage for FIFO compaction-specific options.

## Important APIs, control flow, and dependencies

The tests create `CompactionOptionsFIFO`, set `maxTableFilesSize` and `allowCompaction`, and assert getter values.

## State, persistence, risks, and test signals

Only native option state is allocated. Risks are unsigned size conversion and default/native field drift. Signals are exact getter equality after setter calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionOptionsFIFOTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionOptionsTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionOptionsTest.java

## Purpose

Tests the generic manual `CompactionOptions` Java wrapper.

## Important APIs, control flow, and dependencies

The file round-trips `compression`, `outputFileSizeLimit`, and `maxSubcompactions` on `CompactionOptions`. It also verifies the default compression sentinel `DISABLE_COMPRESSION_OPTION`.

## State, persistence, risks, and test signals

No DB state is used. Native wrapper state must preserve enum and numeric values. Risks are enum byte mapping drift and long/int truncation. Signals are default assertions and exact getter values after setters.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionOptionsUniversalTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionOptionsUniversalTest.java

## Purpose

Accessor coverage for universal compaction configuration.

## Important APIs, control flow, and dependencies

The tests create `CompactionOptionsUniversal` and round-trip `sizeRatio`, `minMergeWidth`, `maxMergeWidth`, `maxSizeAmplificationPercent`, `compressionSizePercent`, `stopStyle`, and `allowTrivialMove`.

## State, persistence, risks, and test signals

Only native option storage is involved. Risks include enum mapping for `CompactionStopStyle`, integer conversion, and boolean default drift. Signals are exact getter equality after each setter.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionOptionsUniversalTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionPriorityTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionPriorityTest.java

## Purpose

Validates Java enum mapping for `CompactionPriority`.

## Important APIs, control flow, and dependencies

The test calls `CompactionPriority.getCompactionPriority` with a valid enum byte and `valueOf` with a symbolic name, plus an invalid byte negative case.

## State, persistence, risks, and test signals

No native DB state is touched. The risk is byte-value drift between Java and C++ enum definitions. Signals are correct enum identity for valid inputs and `IllegalArgumentException` for invalid byte values.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionPriorityTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionStopStyleTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionStopStyleTest.java

## Purpose

Validates Java enum mapping for universal compaction stop style.

## Important APIs, control flow, and dependencies

The test covers `CompactionStopStyle.getCompactionStopStyle`, `valueOf`, and invalid byte handling.

## State, persistence, risks, and test signals

No DB state is persisted. The risk is Java/C++ enum byte mismatch. Signals are expected enum identity for valid mappings and `IllegalArgumentException` for invalid values.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionStopStyleTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ComparatorOptionsTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ComparatorOptionsTest.java

## Purpose

Tests Java comparator option settings that affect Java comparator callback buffering.

## Important APIs, control flow, and dependencies

The suite uses `ComparatorOptions`, `ReusedSynchronisationType`, `setUseDirectBuffer`, and `setMaxReusedBufferSize`. It verifies reused synchronization mode transitions, direct-buffer toggling, and positive/negative buffer-size values.

## State, persistence, risks, and test signals

No DB is opened. The key state is native comparator option storage used later by `AbstractComparator` implementations. Risks include incorrect enum storage and buffer option defaults affecting comparator correctness or callback performance. Signals are getter equality and known defaults.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ComparatorOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompressionOptionsTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompressionOptionsTest.java

## Purpose

Accessor coverage for `CompressionOptions`.

## Important APIs, control flow, and dependencies

The tests set and read `windowBits`, `level`, `strategy`, `maxDictBytes`, `zstdMaxTrainBytes`, and `enabled`.

## State, persistence, risks, and test signals

Only native options memory is used. Risks are numeric conversion errors and default `enabled` drift. Signals are exact getter values and false-to-true `enabled` transition.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompressionOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompressionTypesTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompressionTypesTest.java

## Purpose

Validates string-to-enum lookup for compression library names.

## Important APIs, control flow, and dependencies

The test iterates all `CompressionType` values, calls `getLibraryName`, then resolves it through `CompressionType.getCompressionType`. The sentinel `DISABLE_COMPRESSION_OPTION` is expected to resolve to `NO_COMPRESSION`.

## State, persistence, risks, and test signals

No native DB state is involved. The risk is lookup drift for names used in option parsing or metadata. Signals are exact enum equality for each library name and the special sentinel behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompressionTypesTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ConcurrentTaskLimiterTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ConcurrentTaskLimiterTest.java

## Purpose

Tests basic Java wrapper behavior for a native `ConcurrentTaskLimiter`.

## Important APIs, control flow, and dependencies

`beforeTest` creates `ConcurrentTaskLimiterImpl` with a name and max outstanding task count. Tests read `name`, `outstandingTask`, `setMaxOutstandingTask`, and `resetMaxOutstandingTask`; `afterTest` closes the limiter.

## State, persistence, risks, and test signals

No DB state is persisted. The native limiter tracks outstanding task state, but no tasks are scheduled, so the expected count remains zero. Risks include ownership/lifetime bugs and broken fluent return identity. Signals are name equality, zero outstanding tasks, and setter methods returning the same wrapper.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ConcurrentTaskLimiterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/DBOptionsTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/DBOptionsTest.java

## Purpose

Broad JNI contract coverage for `DBOptions`, including copy construction, properties parsing, environment and IO controls, WAL/log/manifest settings, write scheduling, caches, WAL filters, rate limiting, stats, recovery toggles, DB ID persistence, listeners, and nested native object ownership.

## Important APIs, control flow, and dependencies

The file exercises `DBOptions`, `ConfigOptions`, `Env`, `RocksEnv`, `DbPath`, `WriteBufferManager`, `Cache`, `AbstractWalFilter`, `RateLimiter`, `SstFileManager`, `Statistics`, and `AbstractEventListener`. Most tests set one field and assert the getter. Property tests cover valid props and null/empty/unknown failures. Nested-resource tests attach envs, row caches, write buffer managers, WAL filters, rate limiters, SST file managers, statistics, and listener lists.

## State, persistence, risks, and test signals

No DB is generally opened, but these options control persistent behavior such as WAL recovery, manifest DB ID writing, log directories, WAL directories, atomic flush, two write queues, and best-effort recovery. The listener test is notable: it verifies list replacement does not invalidate previously returned Java listener references. Risks include stale option names, long/int truncation, enum drift, child-wrapper lifetime bugs, and listener list ownership mistakes. Signals are exact defaults, fluent return identity, getter equality, and expected exceptions for invalid properties.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/DBOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/DefaultEnvTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/DefaultEnvTest.java

## Purpose

Integration and accessor coverage for the default RocksDB environment wrapper.

## Important APIs, control flow, and dependencies

The tests use `RocksEnv.getDefault`, `Env.setBackgroundThreads`, `getBackgroundThreads`, `getThreadPoolQueueLen`, `incBackgroundThreadsIfNeeded`, `lowerThreadPoolIOPriority`, `lowerThreadPoolCPUPriority`, `getThreadList`, `Priority`, `ThreadStatus`, and `Options.setEnv`. One test opens a DB to ensure thread status is populated, then queries the default env. Another opens a DB with an explicitly attached env.

## State, persistence, risks, and test signals

The environment is process-global native state, so thread count mutations persist beyond a single method unless native code isolates defaults. No data persistence is the focus, but a temporary DB is opened to create observable background threads. Risks include platform-specific thread-status availability and global side effects between tests. Signals are expected thread counts, zero initial queue lengths, no exception from priority lowering, and non-empty thread lists.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/DefaultEnvTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/DirectSliceTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/DirectSliceTest.java

## Purpose

Tests `DirectSlice`, a Java wrapper for native slices backed by direct buffers or strings.

## Important APIs, control flow, and dependencies

The suite constructs `DirectSlice` from strings, direct `ByteBuffer`s, and direct buffers with explicit length. It calls `toString`, `get`, `removePrefix`, and `clear`, and verifies heap `ByteBuffer` inputs are rejected.

## State, persistence, risks, and test signals

No DB state is involved. The state is native/direct memory ownership and slice view offsets. Risks include accepting non-direct buffers, double free on repeated `clear`, incorrect null-termination handling, and prefix offset errors. Signals are expected strings/bytes and `IllegalArgumentException` for heap buffers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/DirectSliceTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/EnvOptionsTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/EnvOptionsTest.java

## Purpose

Accessor coverage for `EnvOptions`, the per-file IO option object used by file writers and DB file operations.

## Important APIs, control flow, and dependencies

The tests construct `EnvOptions` directly and from `DBOptions`, then round-trip mmap/direct IO flags, fallocate behavior, close-on-exec flag, bytes-per-sync, compaction readahead size, writable file max buffer size, and `RateLimiter` references.

## State, persistence, risks, and test signals

No DB files are created here. The native option state controls lower-level persistence IO behavior in other APIs such as SST writing. Risks include inconsistent transfer from `DBOptions`, boolean default drift, and child rate-limiter lifetime. Signals are exact getter equality and successful replacement of one rate limiter with another.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/EnvOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/EventListenerTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/EventListenerTest.java

## Purpose

Tests Java `AbstractEventListener` callback delivery, callback metadata conversion, enabled-callback filtering, and real DB operations that trigger flush, compaction, file deletion, handle deletion, and external ingestion events.

## Important APIs, control flow, and dependencies

The helper flows open temporary DBs with listeners. `flushDb` writes and flushes to trigger `onFlushBegin`, `onFlushCompleted`, table creation, and memtable events. `deleteTableFile` writes enough data, flushes, compacts, then `deleteFilesInRanges` to trigger table deletion. `compactRange` triggers compaction begin/completed. `deleteColumnFamilyHandle` closes a handle to trigger deletion-started. `ingestExternalFile` writes an SST via `SstFileWriter` and calls `ingestExternalFile`.

The synthetic callback test builds `TableProperties`, `FlushJobInfo`, `Status`, table/file/memtable/write-stall/external-ingestion info objects, and a `CapturingTestableEventListener` to invoke every callback and assert payload equality.

## State, persistence, risks, and test signals

Real tests persist memtables to SSTs, compact files, delete ranges, and ingest external files. Callback state may be written from native background threads, so `ListenerEvents` fields are volatile. Risks include listener lifetime, callback thread visibility, platform-specific file IO events, stale metadata conversion, and callback filtering errors. Signals are atomic booleans from real callbacks, full event coverage from synthetic invocation, enabled-event filtering, and captured assertion propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/EventListenerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/FilterTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/FilterTest.java

## Purpose

Smoke-tests Java filter policy construction and attachment to options.

## Important APIs, control flow, and dependencies

The test creates an `Options` object, then creates `BloomFilter` instances with default arguments, bits-per-key, and bits-per-key plus block-based mode, setting each through options where applicable.

## State, persistence, risks, and test signals

No DB is opened. The important state is native filter allocation and option ownership. Risks are JNI constructor drift and premature filter disposal while options hold references. Successful construction and try-with-resources cleanup are the signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/FilterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/FlushOptionsTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/FlushOptionsTest.java

## Purpose

Accessor coverage for `FlushOptions`.

## Important APIs, control flow, and dependencies

The tests round-trip `waitForFlush` and `allowWriteStall` on a native `FlushOptions` object.

## State, persistence, risks, and test signals

No DB state is created. These options affect memtable persistence in flush operations elsewhere. Risks are default drift and boolean setter binding errors. Signals are expected defaults and changed getter values.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/FlushOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/FlushTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/FlushTest.java

## Purpose

Integration test for explicit flush through the Java API.

## Important APIs, control flow, and dependencies

The test opens a DB with create-if-missing and high write-buffer thresholds, writes four keys with `WriteOptions.setDisableWAL(true)`, asserts active memtable entry count is `4`, calls `db.flush(new FlushOptions().setWaitForFlush(true))`, then asserts the active memtable entry count is `0`.

## State, persistence, risks, and test signals

The test moves data from mutable memtable to persisted SST without relying on WAL. Risks include property-name changes, asynchronous flush races if wait is not honored, and write-buffer option interactions. Signals are the `rocksdb.num-entries-active-mem-table` property before and after flush.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/FlushTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/HyperClockCacheTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/HyperClockCacheTest.java

## Purpose

Smoke-tests `HyperClockCache` creation and integration as a block cache.

## Important APIs, control flow, and dependencies

The test creates a `HyperClockCache`, installs it in `BlockBasedTableConfig.setBlockCache`, opens a DB with `Options`, writes one key/value pair, and reads cache usage and pinned usage.

## State, persistence, risks, and test signals

A temporary DB is opened but persistence semantics are not deeply inspected. The state under test is cache allocation, table config ownership, and ability to query native usage counters. Risks include constructor parameter mismatch and cache/table-config lifetime bugs. Signals are nonnegative usage counters after DB use.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/HyperClockCacheTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ImportColumnFamilyTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ImportColumnFamilyTest.java

## Purpose

Integration coverage for importing one or more exported column-family file sets into a new column family.

## Important APIs, control flow, and dependencies

The tests use `Checkpoint.exportColumnFamily`, `ExportImportFilesMetaData`, `ImportColumnFamilyOptions`, `createColumnFamilyWithImport`, `ColumnFamilyDescriptor`, and `RocksDB`. The first test exports the default CF from one DB and imports it into `new_cf` in the same DB. The second exports default CF metadata from two DBs, combines the metadata list, and imports both into a new CF in the first DB.

## State, persistence, risks, and test signals

This directly validates persisted SST metadata handoff. Exported metadata must describe files that can be linked or copied into a new CF without losing key/value data. Risks include metadata lifetime, duplicate/range overlap handling, import option defaults, and file path correctness. Signals are reads from the imported column family for all source keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ImportColumnFamilyTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/InfoLogLevelTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/InfoLogLevelTest.java

## Purpose

Tests info log level behavior for Java options and enum mapping.

## Important APIs, control flow, and dependencies

The tests open DBs with default logging and with `InfoLogLevel.FATAL_LEVEL` through `Options` and `DBOptions`, flush data, and inspect the RocksDB `LOG` file after stripping headers. It also verifies invalid byte mapping and `valueOf`.

## State, persistence, risks, and test signals

The persisted artifact is the DB log file in the temporary DB directory. Risks include platform-specific path separators, log header filtering, default logging changes, and enum byte drift. Signals are nonempty log body at default level, empty log body at fatal level, and expected enum/exception behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/InfoLogLevelTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/IngestExternalFileOptionsTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/IngestExternalFileOptionsTest.java

## Purpose

Accessor and constructor coverage for `IngestExternalFileOptions`.

## Important APIs, control flow, and dependencies

The tests construct options with no arguments and with constructor booleans, then round-trip `moveFiles`, `snapshotConsistency`, `allowGlobalSeqNo`, `allowBlockingFlush`, `ingestBehind`, and `writeGlobalSeqno`.

## State, persistence, risks, and test signals

No external files are ingested here. These options affect later persisted SST ingestion semantics. Risks include constructor parameter order drift, default value changes, and boolean JNI binding errors. Signals are exact getter equality and known false defaults for `ingestBehind` and `writeGlobalSeqno`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/IngestExternalFileOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/KeyExistsTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/KeyExistsTest.java

## Purpose

Integration coverage for exact key-existence APIs across default CF, explicit column families, `ReadOptions`, byte-array slices, and direct `ByteBuffer` keys.

## Important APIs, control flow, and dependencies

`before` opens a DB with default plus `new_cf`; `after` closes handles and DB. Tests use `put`, `delete`, `keyExists` overloads, `ReadOptions`, direct buffers, offset/length key slices, and `ExpectedException`. They verify that each key exists only in its own CF, deletes change existence to false, and out-of-range byte-array offsets throw.

## State, persistence, risks, and test signals

State lives in memtables/SSTs of a temporary DB; no reopen is required. The direct-buffer tests validate JNI reads of `ByteBuffer` position/limit without copying through arrays. Risks include CF-handle routing mistakes, stale existence after delete, direct-buffer address handling, and Java bounds validation. Signals are true/false existence assertions and `IndexOutOfBoundsException` for invalid slices.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/KeyExistsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/KeyMayExistTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/KeyMayExistTest.java

## Purpose

Integration coverage for probabilistic `keyMayExist` overloads, including optional value retrieval, column-family routing, sliced byte arrays, direct and heap `ByteBuffer` inputs, and non-UTF8 values.

## Important APIs, control flow, and dependencies

Setup opens a DB with two column families and builds a sliced key embedded inside prefix/suffix bytes. Tests call byte-array overloads with `Holder<byte[]>`, null holders, `ReadOptions`, CF handles, and direct `ByteBuffer` value buffers. ByteBuffer tests assert returned `KeyMayExist` enum, value length, and value-buffer position/limit behavior when the destination buffer has an offset or insufficient remaining capacity.

## State, persistence, risks, and test signals

Temporary DB state is written through puts; no reopen is needed. `keyMayExist` may be conservative, but with freshly inserted keys it should return true and often the value. Risks include holder not being nulled on miss, incorrect offset/length validation, direct-buffer position corruption, null value-buffer misuse, CF mismatch, and non-Unicode byte handling. Signals are value equality, false results for wrong CF or partial wrong keys, `BufferUnderflowException` in expected read paths, and `AssertionError` for null value buffers in ByteBuffer overloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/KeyMayExistTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/LRUCacheTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/LRUCacheTest.java

## Purpose

Smoke-tests `LRUCache` construction and usage counters.

## Important APIs, control flow, and dependencies

The test constructs `LRUCache` with capacity, shard bits, strict capacity limit, high-priority pool ratio, and memory allocator, then reads `getUsage` and `getPinnedUsage`.

## State, persistence, risks, and test signals

No DB is opened. Native cache state is allocated and released through try-with-resources. Risks include constructor signature drift and usage counter JNI issues. Signals are nonnegative usage and pinned usage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/LRUCacheTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/LoggerTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/LoggerTest.java

## Purpose

Tests Java custom logger callbacks, log-level filtering, `Options` and `DBOptions` logger attachment, and runtime log-level changes.

## Important APIs, control flow, and dependencies

Each test creates an anonymous `Logger` overriding `log(InfoLogLevel, String)` and counting messages. It attaches the logger to `Options` or `DBOptions`, opens a DB, and asserts message counts under `DEBUG`, `WARN`, or `FATAL`. Runtime tests change `logger.setInfoLogLevel` after opening, then write and flush to cause messages.

## State, persistence, risks, and test signals

Temporary DB opens trigger native log messages. The state under test is Java callback lifetime, logger log-level state, and option ownership. Risks include callbacks after logger close, missing callback filtering, and DBOptions/Options divergence. Signals are message count greater than zero at debug, zero at warn/fatal for open paths, getter equality for log levels, and nonzero messages after runtime switch to debug.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/LoggerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MemTableTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MemTableTest.java

## Purpose

Accessor coverage for memtable representation configuration classes.

## Important APIs, control flow, and dependencies

The tests use `HashSkipListMemTableConfig`, `SkipListMemTableConfig`, `HashLinkedListMemTableConfig`, and `VectorMemTableConfig`, round-tripping bucket counts, height, branching factor, lookahead, huge page TLB size, bucket-entry logging settings, threshold/use-huge-page booleans, and reserved size.

## State, persistence, risks, and test signals

No DB is opened, but these config objects are later consumed by `ColumnFamilyOptions`. Risks include stale factory names, numeric conversion errors, and option default drift. Signals are expected defaults and exact getter equality after setters.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MemTableTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MemoryUtilTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MemoryUtilTest.java

## Purpose

Integration coverage for `MemoryUtil.getApproximateMemoryUsageByType` over DBs and caches.

## Important APIs, control flow, and dependencies

The tests open one or two DBs using `BlockBasedTableConfig` with `LRUCache`, write/flush/get a key to create memtable, table reader, and cache usage, then call `MemoryUtil.getApproximateMemoryUsageByType`. Results are compared to DB aggregate properties `rocksdb.size-all-mem-tables`, `rocksdb.cur-size-all-mem-tables`, and `rocksdb.estimate-table-readers-mem`. A null-input test expects absent map values.

## State, persistence, risks, and test signals

State spans memtables, flushed SST table readers, block cache contents, and multiple DB handles. Risks include approximate counter instability, property-name drift, cache stats changes, and aggregation mistakes across DBs/caches. Signals are equality with DB properties for memtable/table-reader counts, cache usage increasing after reads, and null results for null input sets.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MemoryUtilTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MergeCFVariantsTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MergeCFVariantsTest.java

## Purpose

Parameterized integration coverage for column-family merge overloads using `UInt64AddOperator`.

## Important APIs, control flow, and dependencies

The parameter list covers `RocksDB.merge` overloads with raw byte arrays, `WriteOptions`, array offsets/lengths, direct `ByteBuffer`, and heap `ByteBuffer`. The test opens a DB with default and `new_cf` using merge-operator CF options, puts an initial 64-bit value, applies the selected merge variant, reads and decodes the result, then creates another CF and verifies a normal merge there.

## State, persistence, risks, and test signals

Merge operands are stored in the DB and resolved through the configured CF merge operator. Risks include overload-specific JNI bugs, ByteBuffer position handling, offset/length mistakes, merge operator not attached to dynamically created CFs, and handle cleanup. Signals are exact numeric sums: `100 + 1 = 101` and `200 + 50 = 250`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MergeCFVariantsTest.java -->
