# subset-b-008667 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/WriteBatchWithIndexTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/WriteBatchWithIndexTest.java

Purpose: JUnit coverage for RocksJava `WriteBatchWithIndex`, especially read-your-own-writes semantics, batch index iteration, column family overloads, savepoints, direct/heap `ByteBuffer` APIs, and lookup helpers.

Important APIs/types/functions: `WriteBatchWithIndex`, `WBWIRocksIterator`, `RocksIterator`, `ReadOptions`, `WriteOptions`, `ColumnFamilyHandle`, `DirectSlice`, `ByteBufferAllocator`, `getFromBatch`, `getFromBatchAndDB`, `newIteratorWithBase`, `setSavePoint`, `rollbackToSavePoint`, `popSavePoint`, `setMaxBytes`, `getWriteBatch`.

Control flow and state: tests open temporary RocksDB instances, populate base DB state, then layer a `WriteBatchWithIndex` over base iterators. The merged iterator is probed with `seek`, `seekForPrev`, forward iteration, and reverse iteration after puts, deletes, single deletes, and reinserts. Column family tests repeat the same state transitions through explicit CF handles. Savepoint tests mutate keys after nested savepoints, then roll back or pop and assert the visible batch view. `iterator()` builds expected `WriteEntry` objects and verifies seek/iteration behavior for array-backed and direct buffers. `getFromBatchAndDB` checks batch values shadow DB values and deletes hide DB data.

State and persistence behavior: batch mutations are in-memory until `db.write()` persists them. Base DB values remain durable across iterator construction, while the indexed batch overlays newer, deleted, or missing keys. `getWriteBatch()` returns a non-owning native wrapper, so lifetime is tied to the parent batch-with-index.

Dependencies and integration points: integrates RocksJava JNI, native library loading through `RocksNativeLibraryResource`, JUnit `TemporaryFolder`, AssertJ, column family open APIs, `ByteBuffer` direct and heap paths, and helper `ByteBufferAllocator`.

Risks: iterator validity is easy to misuse after deletes because nearest-key behavior must be checked against the requested key. The tests expose native-handle lifetimes and non-owning write batch handles. Direct `ByteBuffer` methods consume buffer positions, so callers must flip/reset as expected. Savepoint stack underflow intentionally throws `RocksDBException`.

Test signals: strong coverage for default and named CFs, direct/heap buffer seeking, overwrite true/false iterator constructors, max-batch-size enforcement, exact-match lookup, range delete half-open boundaries, and savepoint exception paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/WriteBatchWithIndexTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/WriteOptionsTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/WriteOptionsTest.java

Purpose: JUnit coverage for RocksJava `WriteOptions` option setters/getters and native copy-constructor behavior.

Important APIs/types/functions: `WriteOptions.setSync`, `sync`, `setDisableWAL`, `disableWAL`, `setIgnoreMissingColumnFamilies`, `setNoSlowdown`, `setLowPri`, `setMemtableInsertHintPerBatch`, and `new WriteOptions(origOpts)`.

Control flow and state: `writeOptions()` creates one native-backed options object and toggles each boolean true then false, asserting the Java getter mirrors the native value. `copyConstructor()` randomizes several booleans on the original, sets `memtableInsertHintPerBatch`, copies, and compares values.

State and persistence behavior: this is transient JNI option state only; no database is opened and no persisted write behavior is tested.

Dependencies and integration points: depends on RocksJava native library loading and `PlatformRandomHelper` for platform-specific randomness. These options feed DB write paths elsewhere.

Risks: coverage is limited to boolean round-trips; it does not prove `noSlowdown`, `lowPri`, WAL disabling, or sync change write behavior under load. `copyConstructor()` omits some toggled properties such as `noSlowdown` and `lowPri`.

Test signals: basic native handle construction, mutability, and copy propagation are covered.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/WriteOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/test/RemoveEmptyValueCompactionFilterFactory.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/test/RemoveEmptyValueCompactionFilterFactory.java

Purpose: Test fixture factory that produces `RemoveEmptyValueCompactionFilter` instances for RocksJava compaction-filter tests.

Important APIs/types/functions: extends `AbstractCompactionFilterFactory<RemoveEmptyValueCompactionFilter>`, implements `createCompactionFilter(AbstractCompactionFilter.Context)` and `name()`.

Control flow and state: `createCompactionFilter` ignores the supplied compaction context and returns a new `RemoveEmptyValueCompactionFilter` on each factory invocation. `name()` returns a stable descriptive name.

State and persistence behavior: no internal mutable state is stored. Persistence effects are delegated to the returned compaction filter, which removes entries with empty values during compaction in consuming tests.

Dependencies and integration points: integrates with RocksJava native compaction filter factory callbacks and is consumed by tests that set a compaction filter factory on options.

Risks: context is ignored, so it cannot vary behavior by full/manual compaction or column family. The factory allocates a new filter every call and relies on RocksJava/native ownership handling.

Test signals: this file is itself a helper, not a test; its correctness is signaled by downstream compaction filter tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/test/RemoveEmptyValueCompactionFilterFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/test/RocksJunitRunner.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/test/RocksJunitRunner.java

Purpose: Custom command-line JUnit runner for RocksJava that prints class-level progress and per-method status, then exits with distinct failure codes.

Important APIs/types/functions: `RocksJunitRunner.main`, nested `RocksJunitListener extends TextListener`, `testRunStarted`, `testStarted`, `testFailure`, `testIgnored`, `testFinished`, `testRunFinished`, `printTestsSummary`, and `Status` enum.

Control flow and state: `main` converts class-name arguments to `Class<?>`, registers the listener on `JUnitCore`, runs all classes, exits `-1` on test failure or `-2` on class lookup failure. The listener tracks current class/method, status, start time, and counters. On class changes it prints the previous class summary, then starts a new block. Failures are split into assertion failures and errors by exception type.

State and persistence behavior: all state is process-local counters and current-test metadata. No test results are persisted except stdout/stderr and process exit status.

Dependencies and integration points: uses JUnit internals (`RealSystem`, `TextListener`), `JUnitCore`, and imports `RocksDB` only to keep RocksJava context available. Intended for build/test scripts.

Risks: relies on JUnit internal classes and mutable listener state; parallel JUnit execution would make counters unsafe. `testIgnored` can set status without `testStarted` establishing method state for some JUnit flows.

Test signals: no dedicated tests here; behavior is observable when running RocksJava test suites.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/test/RocksJunitRunner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/test/TestableEventListener.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/test/TestableEventListener.java

Purpose: Test-only `AbstractEventListener` subclass that exposes a native hook to invoke all enabled event callbacks.

Important APIs/types/functions: constructors forwarding optional `EnabledEventCallback...`, `invokeAllCallbacks()`, and native `invokeAllCallbacks(long handle)`.

Control flow and state: construction delegates enabled callback configuration to `AbstractEventListener`. `invokeAllCallbacks()` passes the listener native handle to JNI, which triggers callback dispatch for tests.

State and persistence behavior: listener state is native-handle backed; no persistence. Correctness depends on the listener remaining open while native callbacks execute.

Dependencies and integration points: integrates RocksJava event listener JNI and tests that need deterministic callback invocation without requiring real compaction/flush/table events.

Risks: native method availability and handle lifetime are critical; misuse after close can hit invalid native state. Callback coverage depends on JNI implementation, not visible in this Java file.

Test signals: helper for event listener tests; downstream assertions validate callback observability.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/test/TestableEventListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/ByteBufferAllocator.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/ByteBufferAllocator.java

Purpose: Small test utility interface abstracting heap versus direct `ByteBuffer` allocation.

Important APIs/types/functions: `ByteBufferAllocator.allocate(int capacity)`, constants `HEAP` and `DIRECT`.

Control flow and state: callers select one of two singleton allocator implementations. Each call returns a fresh `ByteBuffer` of the requested capacity.

State and persistence behavior: stateless; returned buffers are transient test objects.

Dependencies and integration points: used by RocksJava tests that must exercise both direct JNI buffer paths and ordinary heap buffers without duplicating test bodies.

Risks: no validation of capacity; direct buffer allocation can pressure off-heap memory in large tests.

Test signals: indirect coverage through `WriteBatchWithIndexTest` and comparator tests using direct/heap pathways.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/ByteBufferAllocator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/BytewiseComparatorIntTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/BytewiseComparatorIntTest.java

Purpose: Parameterized RocksJava test that verifies `BytewiseComparator` orders positive 4-byte integer keys consistently across default and named column families.

Important APIs/types/functions: `BytewiseComparator`, `ComparatorOptions.setUseDirectBuffer`, `setMaxReusedBufferSize`, `setReusedSynchronisationType`, `testRoundtrip`, `testRoundtripCf`, and parameter sets for direct/non-direct, reused buffer size, and synchronization type.

Control flow and state: `prepareKeys()` creates 500 unique positive integer keys as big-endian byte arrays. Each test builds comparator options from parameters, opens a DB with the comparator, writes all keys, reopens, iterates from first to last, decodes keys with `ByteBuffer`, and asserts strictly increasing integer order. The CF variant puts data into a named column family configured with the comparator and repeats the reopen/iterate check.

State and persistence behavior: temporary DB files persist across close/reopen inside each test to confirm comparator identity/order metadata works after reopening.

Dependencies and integration points: RocksJava comparator JNI, `RocksNativeLibraryResource`, column family descriptors/options, direct buffer callback paths, and comparator reused-buffer synchronization strategies.

Risks: random keys are non-deterministic because no seed is set. It only uses positive ints, avoiding signed-byte ordering pitfalls for negative values. CF option handles must be closed carefully.

Test signals: strong signal for comparator round-tripping, CF integration, and direct versus heap callback compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/BytewiseComparatorIntTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/BytewiseComparatorTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/BytewiseComparatorTest.java

Purpose: Port of comparator DB iteration tests comparing Java bytewise/reverse comparators to RocksDB C++ built-in comparators over randomized write/delete/iterator operations.

Important APIs/types/functions: `BytewiseComparator`, `ReverseBytewiseComparator`, `BuiltinComparator`, `doRandomIterationTest`, `openDatabase`, `toJavaComparator`, nested `KVIter implements RocksIteratorInterface`.

Control flow and state: each test opens a temporary DB with either C++ or Java comparator, builds an equivalent Java `TreeMap`, applies randomized puts/deletes with periodic flushes, then performs randomized iterator operations (`seekToFirst`, `seekToLast`, `seek`, `seekForPrev`, `next`, `prev`, `refresh`) and point gets. RocksDB iterator results are compared to `KVIter`, a reference iterator over the `TreeMap` using the same comparator.

State and persistence behavior: DB state lives on temporary files and may flush to SSTs during tests; the reference `TreeMap` tracks expected logical state. No long-term persistence.

Dependencies and integration points: JNI comparator callbacks, built-in C++ comparator names, Rocks iterator API, flush/write/read options, direct and non-direct comparator buffer modes.

Risks: `KVIter.status()` throws when invalid, whereas RocksDB iterator status can be valid even when positioned invalid; the test calls status before operations and avoids invalid value reads. Random seeds are fixed for reproducibility, but key universe is small.

Test signals: strong behavioral equivalence checks across Java/C++ comparator implementations, reverse ordering, flush boundaries, and iterator navigation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/BytewiseComparatorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/CapturingWriteBatchHandler.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/CapturingWriteBatchHandler.java

Purpose: Test `WriteBatch.Handler` implementation that records every write-batch callback as an `Event` for assertions.

Important APIs/types/functions: overrides `put`, `merge`, `delete`, `singleDelete`, `deleteRange`, `logData`, `putBlobIndex`, prepare/commit marker methods, `getEvents`, nested `Event`, and `Action` enum.

Control flow and state: each callback appends a new `Event` to an internal `ArrayList`. `getEvents()` returns a copy of the event list. `Event.equals` compares action, column family id, and byte-array contents with `Arrays.equals`; `hashCode` mirrors that state.

State and persistence behavior: entirely in-memory test capture. Events keep references to byte arrays rather than copies, so later mutation by tests can change captured content.

Dependencies and integration points: used by tests invoking `WriteBatch.iterate(handler)` to verify JNI callback order and payloads.

Risks: `putBlobIndex(int, key, value)` drops the supplied column family id and records default id through the two-argument constructor. Transaction marker callbacks ignore XIDs/timestamps, so the helper only asserts marker type presence, not payload.

Test signals: downstream write batch tests use this as an oracle for callback ordering and action classification.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/CapturingWriteBatchHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/DirectByteBufferAllocator.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/DirectByteBufferAllocator.java

Purpose: `ByteBufferAllocator` implementation returning direct off-heap buffers for JNI path testing.

Important APIs/types/functions: `allocate(int capacity)` delegates to `ByteBuffer.allocateDirect`.

Control flow and state: stateless allocation on demand.

State and persistence behavior: no persistence; allocated direct buffers are released by JVM cleaner/GC.

Dependencies and integration points: selected through `ByteBufferAllocator.DIRECT` in tests that verify RocksJava APIs accept and advance direct buffers correctly.

Risks: direct buffers consume off-heap memory and are not reclaimed immediately; excessive use in tests can expose memory pressure.

Test signals: coverage comes from tests parameterized over direct allocation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/DirectByteBufferAllocator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/EnvironmentTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/EnvironmentTest.java

Purpose: JUnit tests for RocksJava `Environment` platform detection and JNI/shared-library filename construction.

Important APIs/types/functions: `Environment.isWindows`, `isUnix`, `isPowerPC`, `isAarch64`, `is64Bit`, `getJniLibraryExtension`, `getJniLibraryFileName`, `getFallbackJniLibraryFileName`, `getSharedLibraryFileName`, `getSharedLibraryName`, `getJniLibraryName`, `initIsMuslLibc`, reflection helpers for static fields.

Control flow and state: `saveState` records initial static `Environment` fields. Each test uses reflection to inject OS/arch/musl combinations, then asserts expected platform predicates and library names for macOS, Linux glibc/musl, Unix, AIX, Windows, ppc64le, and aarch64. `restoreState` restores all fields after the class.

State and persistence behavior: mutates global static process state in `Environment`; no file persistence. The restore method is essential to avoid leaking fake OS state into other tests.

Dependencies and integration points: tests the naming contract consumed by `NativeLibraryLoader` and packaging of RocksJava native artifacts.

Risks: reflection against private static fields is brittle and unsafe under parallel execution. JDK module/access changes can break reflective field writes. Musl detection is partially simulated and does not probe real libc here.

Test signals: good table-like coverage of supported platform filename mappings and unsupported AIX 32-bit behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/EnvironmentTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/HeapByteBufferAllocator.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/HeapByteBufferAllocator.java

Purpose: `ByteBufferAllocator` implementation returning array-backed heap buffers for non-direct JNI path testing.

Important APIs/types/functions: `allocate(int capacity)` delegates to `ByteBuffer.allocate`.

Control flow and state: stateless allocation on demand.

State and persistence behavior: heap buffers are ordinary GC-managed Java objects.

Dependencies and integration points: selected through `ByteBufferAllocator.HEAP` in tests that compare heap and direct buffer API behavior.

Risks: array-backed buffers can take different JNI paths from direct buffers, so this helper should be paired with direct tests rather than treated as complete coverage.

Test signals: indirect coverage through buffer-parameterized tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/HeapByteBufferAllocator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/IntComparatorTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/IntComparatorTest.java

Purpose: Parameterized test for RocksJava `IntComparator` and the JNI comparator callback path using random signed integer keys.

Important APIs/types/functions: `IntComparator`, `ComparatorOptions`, `ReusedSynchronisationType`, `testRoundtrip`, `testRoundtripCf`, RocksDB default and named column family opens.

Control flow and state: the class generates 500 unique 4-byte signed integer keys. For each buffer/synchronization parameter set, it opens a DB or named CF with `IntComparator`, writes all keys, reopens with the same comparator, iterates in order, decodes each key to `int`, and asserts strict ascending order with exactly `TOTAL_KEYS` entries.

State and persistence behavior: temporary DB files are reopened to validate persisted comparator metadata and ordering. CF handles/options are explicitly closed after use.

Dependencies and integration points: exercises Java comparator callbacks across direct and heap buffers, reused JNI buffer strategies, and column family comparator configuration.

Risks: random key generation is unseeded. Comparator compatibility depends on reopening with the same comparator object/configuration; opening with a mismatched comparator would be outside this test. Native direct buffer reuse synchronization is only indirectly stressed by single-thread iteration.

Test signals: strong signal for signed integer ordering, comparator callback correctness, and CF round-trip behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/IntComparatorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/JNIComparatorTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/JNIComparatorTest.java

Purpose: Parameterized test that compares full key iteration order from Java comparators against C++ built-in bytewise and reverse-bytewise comparators.

Important APIs/types/functions: `BuiltinComparator.BYTEWISE_COMPARATOR`, `REVERSE_BYTEWISE_COMPARATOR`, `BytewiseComparator`, `ReverseBytewiseComparator`, `storeWithJavaComparator`, `storeWithCppComparator`, `readAllWithJavaComparator`, `readAllWithCppComparator`.

Control flow and state: for each built-in/directness parameter, the test writes all integers from `Short.MIN_VALUE - 1` to `Short.MAX_VALUE + 1` as 4-byte keys into one DB using the Java comparator and another using the C++ comparator. It then reopens and iterates both DBs, decoding keys into arrays, and asserts identical order.

State and persistence behavior: uses temporary DB directories and close/reopen cycles to validate on-disk order. The declared `useDirectBuffer` parameter is not applied to `ComparatorOptions` in this file, so directness is represented in the parameter name but not in behavior.

Dependencies and integration points: RocksJava comparator JNI and built-in comparator configuration.

Risks: potential test gap: `useDirectBuffer` is unused, so direct comparator callback equivalence is not actually varied here. The key range is large enough for meaningful ordering but still bounded.

Test signals: strong Java-vs-C++ ordering equivalence for bytewise and reverse bytewise comparators, subject to the directness caveat.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/JNIComparatorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/ReverseBytewiseComparatorIntTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/ReverseBytewiseComparatorIntTest.java

Purpose: Parameterized test verifying `ReverseBytewiseComparator` produces descending integer order for positive 4-byte keys in default and named column families.

Important APIs/types/functions: `ReverseBytewiseComparator`, `ComparatorOptions`, `ReusedSynchronisationType`, `testRoundtrip`, `testRoundtripCf`.

Control flow and state: generates 500 unique positive integer keys, writes them under a reverse bytewise comparator, reopens the DB/CF, iterates from first to last, decodes keys to ints, and asserts each key is less than the previous key. The parameter matrix covers direct/non-direct buffers, reused-buffer sizes, and synchronization modes.

State and persistence behavior: temporary DB state is persisted across close/reopen to validate comparator configuration and ordering.

Dependencies and integration points: RocksJava comparator callbacks, column family APIs, direct buffer JNI paths, and comparator option reuse behavior.

Risks: random key generation is unseeded; only positive ints are used, reducing coverage of bytewise ordering for negative signed representations. Multi-thread reuse behavior is not directly stressed.

Test signals: good reverse-order signal for both default and named CFs under multiple comparator buffer configurations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/ReverseBytewiseComparatorIntTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/SizeUnitTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/SizeUnitTest.java

Purpose: Simple unit test for RocksJava `SizeUnit` constants.

Important APIs/types/functions: `SizeUnit.KB`, `MB`, `GB`, `TB`.

Control flow and state: asserts each larger unit equals the previous unit multiplied by 1024, starting from `COMPUTATION_UNIT`.

State and persistence behavior: none.

Dependencies and integration points: validates constants used by Java tests/configuration examples for byte sizes.

Risks: only checks relative values, not overflow boundaries or string parsing.

Test signals: basic regression coverage for binary size unit constants.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/SizeUnitTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/StdErrLoggerTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/StdErrLoggerTest.java

Purpose: Smoke tests that a native `StdErrLogger` can be constructed and attached to Java `Options` and `DBOptions`.

Important APIs/types/functions: `StdErrLogger(InfoLogLevel, prefix)`, `Options.setLogger`, `DBOptions.setLogger`.

Control flow and state: each test creates options plus a stderr logger in try-with-resources and sets the logger on the options object. It deliberately avoids emitting logs to keep test output clean.

State and persistence behavior: native logger/options state only; no database is opened and no log is persisted.

Dependencies and integration points: RocksJava native library, logger JNI, `InfoLogLevel`.

Risks: does not verify actual stderr output, prefixes, log-level filtering, or lifetime interaction with an open DB. It only catches construction and setter failures.

Test signals: smoke signal for logger object creation and option attachment.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/StdErrLoggerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/TestUtil.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/TestUtil.java

Purpose: Shared RocksJava test utilities for common options, random dummy data, and `ByteBuffer` extraction.

Important APIs/types/functions: `optionsForLogIterTest`, `defaultOptions`, `dummyString(int)`, `bufferBytes(ByteBuffer)`.

Control flow and state: options helpers create configured `Options` objects with create-if-missing, write buffer sizes, target file size, and WAL/log iteration settings. `dummyString` uses a static `Random` and an alphabet to build byte arrays. `bufferBytes` copies remaining bytes from a `ByteBuffer` using `mark`, `get`, and `reset` so the caller’s position is preserved.

State and persistence behavior: options influence DB files in consuming tests, but this helper persists nothing. The static `Random` is shared and unseeded.

Dependencies and integration points: used throughout RocksJava tests for consistent option defaults and byte buffer assertions.

Risks: callers own returned native `Options` and must close them. Shared random is not deterministic and not synchronized. `bufferBytes` requires mark/reset support, which standard heap/direct buffers have but custom buffers might not.

Test signals: helper only; correctness is exercised by dependent tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/TestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/WriteBatchGetter.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/WriteBatchGetter.java

Purpose: Test `WriteBatch.Handler` that tracks the latest value for a single target key while iterating a write batch.

Important APIs/types/functions: constructor `WriteBatchGetter(byte[] key)`, `getValue`, overrides for `put`, `merge`, `delete`, `singleDelete`, `putBlobIndex`, and unsupported callbacks.

Control flow and state: each relevant callback compares the event key with the target using `Arrays.equals`. Puts, merges, and blob indexes store the event value; deletes and single deletes set value to null. CF-aware overloads also update `columnFamilyId`, though no getter exposes it. Range deletes, log records, and transaction markers throw `UnsupportedOperationException`.

State and persistence behavior: in-memory reduction over a batch stream; no persistence. Stored `value` references are not copied.

Dependencies and integration points: useful for tests that need batch lookup semantics without opening a DB.

Risks: unsupported callbacks make it unsafe for arbitrary modern write batches containing ranges, logs, or transaction markers. Merge is treated as value replacement, not merge-operator semantics. CF id is private and unused.

Test signals: downstream tests can assert final target value/null after batch iteration.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/WriteBatchGetter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/auto_roll_logger.cc -->
# sources/storage-engines/rocksdb/logging/auto_roll_logger.cc

Purpose: Implementation of RocksDB `AutoRollLogger`, which wraps an underlying `Logger` and rotates LOG files by size and/or elapsed time, plus `CreateLoggerFromOptions`.

Important APIs/types/functions: constructor, `ResetLogger`, `RollLogFile`, `GetExistingFiles`, `TrimOldLogFiles`, `Logv`, `LogHeader`, `WriteHeaderInfo`, `LogExpired`, `CreateLoggerFromOptions`.

Control flow and state: construction resolves DB absolute path, computes active LOG path, renames an existing LOG, scans old info logs, opens a new logger, and trims old logs. `Logv` takes a mutex, checks time/size thresholds before writing, rolls and resets if needed, replays stored headers, trims excess files, pins the current logger in a shared pointer, releases the mutex, then writes concurrently. `RollLogFile` picks a unique old filename by timestamp, waits for pinned references, closes the old logger, renames active LOG, and enqueues it for trimming.

State and persistence behavior: persists active and rolled LOG files in DB/log directories. Keeps header strings and old-log queue in memory. Cached seconds reduce clock calls and drive time rotation.

Dependencies and integration points: `FileSystem`, `SystemClock`, filename helpers, `DBOptions`, `Env`, `Logger`, `ROCKS_LOG_WARN`, and sync points for concurrency tests.

Risks: busy-waits on `logger_.use_count() > 1`; rename errors inside `RollLogFile` are ignored. Header serialization truncates at 1024 bytes. Old-log deletion bypasses DB rate limiting and directory sync. `Logv` asserts status ok.

Test signals: covered by auto-roll logger tests for size/time rolling, trimming, headers, create failures, rename races, info log levels, and flush while rolling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/auto_roll_logger.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/auto_roll_logger.h -->
# sources/storage-engines/rocksdb/logging/auto_roll_logger.h

Purpose: Declaration of the rolling logger interface and factory used by DB option initialization.

Important APIs/types/functions: `AutoRollLogger`, overrides `Logv`, `LogHeader`, `Flush`, `GetLogFileSize`, `GetInfoLogLevel`, `SetInfoLogLevel`, `CloseImpl`, test accessors, and `CreateLoggerFromOptions`.

Control flow and state: the class owns a shared underlying logger, filesystem/clock references, active path, status, rotation thresholds, retained headers, old-file queue, clock cache, I/O options/context, and a mutex. Public methods generally lock, pin `logger_`, and then delegate.

State and persistence behavior: tracks active and historical LOG files while delegating actual bytes to the underlying logger. Destructor closes the inner logger if not already closed and permits unchecked status.

Dependencies and integration points: inherits `Logger`, uses RocksDB port mutexes and file naming utilities, and is selected when `DBOptions.max_log_file_size` or `log_file_time_to_roll` is nonzero.

Risks: exposes test-only internals that can become stale if implementation changes. The destructor accesses `logger_` without locking, assuming no concurrent use during destruction.

Test signals: interface behavior is exercised by `auto_roll_logger_test.cc`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/auto_roll_logger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/auto_roll_logger_test.cc -->
# sources/storage-engines/rocksdb/logging/auto_roll_logger_test.cc

Purpose: C++ test suite for `AutoRollLogger` and `CreateLoggerFromOptions`.

Important APIs/types/functions: helper `RollLogFileBySizeTest`, `RollLogFileByTimeTest`, `RollNTimesBySize`, `GetLogFiles`, `CleanupLogFiles`, tests for size/time rolling, option factory selection, auto-deleting, flush concurrency, log levels, close, header replay, file existence, create failures, and rename errors.

Control flow and state: tests initialize per-thread DB/log directories, write predictable messages until thresholds are crossed, use `EmulatedSystemClock` for time rolling, and inspect file sizes/counts/contents. Factory tests vary `DBOptions` to choose `EnvLogger` or `AutoRollLogger`. SyncPoint orchestration pins an old logger during flush while another path rolls. Rename tests use `SpecialEnv` counters/errors.

State and persistence behavior: creates and deletes real LOG files under test directories; validates rolled file retention and active LOG creation. Uses shell `rm -rf`/Windows commands in setup.

Dependencies and integration points: DB open path, Env/FileSystem, `EnvLogger`, emulated clocks, sync points, test utilities.

Risks: filesystem timing and shell cleanup can be platform-sensitive. Some factory tests are disabled on Windows. Size-rolling checks depend on formatted log message sizes.

Test signals: comprehensive coverage of rolling thresholds, retention, header replay, log-level filtering, failure paths, and concurrency pinning.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/auto_roll_logger_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/env_logger.h -->
# sources/storage-engines/rocksdb/logging/env_logger.h

Purpose: Logger implementation that writes formatted log records through a RocksDB `Env`/`FSWritableFile`.

Important APIs/types/functions: `EnvLogger`, `FileOpGuard`, `Logv`, `Flush`, `FlushLocked`, `CloseImpl`, `CloseHelper`, `GetLogFileSize`.

Control flow and state: `Logv` builds a timestamp/thread-id prefix, formats into a stack buffer and retries with a 64KB heap buffer if needed, appends a newline, then under `FileOpGuard` appends to `WritableFileWriter`, marks flush pending, and flushes if five seconds have elapsed. `FileOpGuard` disables perf/iostats pollution and locks the mutex for file operations. Close and flush also use the guard.

State and persistence behavior: appends to a log file and tracks pending flush plus last flush time. Close flushes/finishes the underlying writer. Reopening through factory can overwrite existing files depending on caller behavior.

Dependencies and integration points: `WritableFileWriter`, `Env`, `SystemClock`, perf/iostats context, port time functions, sync points used by auto-roll tests.

Risks: append errors are ignored and writer seen-error state is reset. `flush_pending_` and `last_flush_micros_` are atomic but most meaningful changes are mutex-guarded. Long messages beyond 64KB are truncated.

Test signals: `env_logger_test.cc` covers empty files, multiple lines, overwrite, close, and concurrent logging.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/env_logger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/env_logger_test.cc -->
# sources/storage-engines/rocksdb/logging/env_logger_test.cc

Purpose: C++ tests for `EnvLogger` file writing behavior.

Important APIs/types/functions: `CreateLogger`, `WriteLogs`, `LogMessage`, tests `EmptyLogFile`, `LogMultipleLines`, `Overwrite`, `Close`, `ConcurrentLogging`.

Control flow and state: creates a logger with `NewEnvLogger`, sets INFO level, writes messages through generic logging helpers, flushes/closes, then counts matching lines in the log file. The concurrent test starts five threads, each writing and flushing twenty messages, then verifies total line count.

State and persistence behavior: creates a per-thread log file, deletes it after each test, and verifies persisted log content.

Dependencies and integration points: default `Env`, logger factory, thread abstraction, test utilities for line counting.

Risks: line-count checks depend on complete flush/close behavior. Concurrent test verifies count, not interleaving format or atomicity of each line beyond what the logger provides.

Test signals: good coverage for basic persistence, overwrite/truncate behavior, close flushing, and multi-thread append safety.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/env_logger_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/event_logger.cc -->
# sources/storage-engines/rocksdb/logging/event_logger.cc

Purpose: Implementation of structured event logging to info logs or deferred log buffers.

Important APIs/types/functions: `EventLoggerStream` constructors/destructor, `EventLogger::Log`, static `Log`, and `LogToBuffer`.

Control flow and state: an `EventLoggerStream` lazily creates a `JSONWriter` on first insertion and adds `time_micros`. On destruction it closes the JSON object and either writes prefixed JSON to a `Logger`, writes to `LogBuffer`, or prints to stdout under compile-time flag. Static helpers prepend `EVENT_LOG_v1`.

State and persistence behavior: stream owns its `JSONWriter` until destructor. Output persists only through the target logger or buffered log flush.

Dependencies and integration points: generic `Log`, `LogToBuffer`, `LogBuffer`, chrono system clock, and optional `ROCKSDB_PRINT_EVENTS_TO_STDOUT`.

Risks: destructor-driven emission means partially constructed streams still log at scope exit. JSON escaping is minimal because `JSONWriter` writes raw strings in quotes. The stream manually owns `JSONWriter` via raw pointer.

Test signals: `event_logger_test.cc` verifies key fields in emitted output.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/event_logger.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/event_logger.h -->
# sources/storage-engines/rocksdb/logging/event_logger.h

Purpose: Header for RocksDB structured event logging and lightweight JSON assembly.

Important APIs/types/functions: `JSONWriter`, `EventLoggerStream`, `EventLogger`, `Prefix`, `Log`, `LogToBuffer`, array/object methods and stream insertion operators.

Control flow and state: `JSONWriter` is a small state machine alternating between key and value states, with special handling for arrays and arrayed objects. `EventLoggerStream` forwards insertions to the writer and emits on destruction. `EventLogger` binds either direct logger output or log-buffer output.

State and persistence behavior: no persistence by itself; generated JSON strings flow to info logs or buffers.

Dependencies and integration points: used by RocksDB subsystems that emit machine-readable operational events to LOG.

Risks: JSON string values are not escaped for quotes/backslashes, so unsafe values can produce invalid JSON. State assertions are debug-time only. Nested object/array support is limited.

Test signals: simple field-presence test exists; complex JSON state transitions are not heavily tested in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/event_logger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/event_logger_test.cc -->
# sources/storage-engines/rocksdb/logging/event_logger_test.cc

Purpose: Minimal test for `EventLogger` structured output.

Important APIs/types/functions: `StringLogger`, `EventLogger`, `event_logger.Log() << key << value`.

Control flow and state: `StringLogger` captures the most recent formatted log line in a fixed buffer. The test writes an event with `id` and `event`, then asserts the captured output contains those fields and `time_micros`.

State and persistence behavior: all output is in memory; no files.

Dependencies and integration points: tests the generic `Logger` interface and event stream destructor emission.

Risks: only substring checks are performed; JSON validity, prefix presence, escaping, arrays, and buffer logging are not covered.

Test signals: smoke signal that stream insertion emits fields on destruction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/event_logger_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/log_buffer.cc -->
# sources/storage-engines/rocksdb/logging/log_buffer.cc

Purpose: Implementation of deferred info-log buffering for code paths that cannot log immediately, often while holding mutexes.

Important APIs/types/functions: `LogBuffer::AddLogToBuffer`, `FlushBufferToLog`, free functions `LogToBuffer`.

Control flow and state: `AddLogToBuffer` skips messages below the logger’s current level, allocates a fixed-size record from an `Arena`, stores current time, formats the message with truncation, NUL-terminates it, and appends the record pointer. `FlushBufferToLog` iterates buffered records, formats original timestamp metadata, logs each message at the buffer’s level, and clears the vector.

State and persistence behavior: messages live in the buffer’s arena until the buffer is destroyed; flushing writes them to the target logger. Clearing drops pointers but arena memory remains allocated for the buffer lifetime.

Dependencies and integration points: `Arena`, `autovector`, port time functions, generic `Log`.

Risks: max log size truncates messages; arena memory is not reclaimed on flush. If local time conversion fails, a buffered entry is skipped. Thread safety is not provided.

Test signals: indirectly covered through event logging and subsystems using buffered logs; no dedicated test in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/log_buffer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/log_buffer.h -->
# sources/storage-engines/rocksdb/logging/log_buffer.h

Purpose: Declaration of `LogBuffer`, a temporary buffer of timestamped log entries for delayed flushing.

Important APIs/types/functions: `LogBuffer`, `AddLogToBuffer`, `IsEmpty`, `FlushBufferToLog`, `kDefaultMaxLogSize`, `BufferedLog`, free `LogToBuffer` overloads.

Control flow and state: stores log level, target logger, arena allocator, and vector of `BufferedLog*`. Callers append formatted records and later flush them to the logger.

State and persistence behavior: in-memory until `FlushBufferToLog`; persisted only after target logger writes.

Dependencies and integration points: used by logging macros and event logger buffering to avoid immediate logging inside sensitive sections.

Risks: no ownership of `info_log_`; caller must keep logger alive. `IsEmpty` returns `size_t` rather than `bool`, despite semantic name. Buffer memory grows until object destruction.

Test signals: behavior is exercised indirectly by log-buffer users.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/log_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/logging.h -->
# sources/storage-engines/rocksdb/logging/logging.h

Purpose: Macro layer for RocksDB logging with file/line prefixes and log levels.

Important APIs/types/functions: `ROCKS_LOG_PREPEND_FILE_LINE`, `RocksLogShorterFileName`, `ROCKS_LOG_HEADER`, `ROCKS_LOG_AT_LEVEL`, level macros, buffer macros, `ROCKS_LOG_DETAILS`.

Control flow and state: macros expand to generic `Log`/`LogToBuffer` calls, adding shortened file name and source line for non-header logs. Header logs intentionally omit file/line metadata. Details logging is compiled as an empty statement by default.

State and persistence behavior: no state; persistence depends on target logger/buffer.

Dependencies and integration points: included by `.cc` files only to avoid namespace pollution; used broadly across RocksDB internals.

Risks: macro formatting can evaluate arguments according to varargs rules and lacks type safety. `RocksLogShorterFileName` depends on this header’s path length constant. Empty details macro can hide side effects if arguments are ever added there.

Test signals: indirectly covered by logger tests that count output lines and header behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/logging/logging.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/allocator.h -->
# sources/storage-engines/rocksdb/memory/allocator.h

Purpose: Internal memory allocation interfaces for arena-backed allocations and write-buffer accounting.

Important APIs/types/functions: abstract `Allocator`, `Allocate`, `AllocateAligned`, `BlockSize`, and `AllocTracker` with `Allocate`, `DoneAllocating`, `FreeMem`, `is_freed`.

Control flow and state: `Allocator` defines the allocation contract used by arenas/memtable structures. `AllocTracker` records bytes reserved through a `WriteBufferManager`; implementation in `memtable/alloc_tracker.cc` reserves on allocate, schedules free when allocation phase is done, and frees once.

State and persistence behavior: tracks memory accounting only; no persistence. Allocated memory is freed by allocator lifetime or underlying memory manager.

Dependencies and integration points: `WriteBufferManager`, `Arena`, `ConcurrentArena`, and memtable allocation paths.

Risks: `AllocTracker` is non-copyable and expects precise lifecycle calls. Incorrect `DoneAllocating`/destruction ordering can skew write-buffer pressure accounting.

Test signals: arena tests indirectly exercise allocation; write-buffer manager tests cover tracker implementation outside this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/allocator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/arena.cc -->
# sources/storage-engines/rocksdb/memory/arena.cc

Purpose: Implementation of RocksDB’s arena allocator for fast lifetime-based allocation with inline storage, regular blocks, irregular large blocks, and optional huge-page support.

Important APIs/types/functions: `OptimizeBlockSize`, constructor/destructor, `AllocateFallback`, `AllocateFromHugePage`, `AllocateAligned`, `AllocateNewBlock`.

Control flow and state: construction clamps block size, initializes inline block allocation pointers, records inline memory with tracker, and configures huge-page size. Small unaligned allocations use the inline/current block from the high end. Aligned allocations account for alignment slop from the low end. Fallback allocates large requests separately when above one quarter block size; otherwise it allocates a new regular or huge-page block and sets current pointers.

State and persistence behavior: memory lives until arena destruction; no individual frees. `blocks_memory_`, `alloc_bytes_remaining_`, and irregular count expose accounting.

Dependencies and integration points: memtables, log buffers, `MemMapping`, `AllocTracker`, malloc usable size, sync points, logger warnings for huge-page fallback.

Risks: zero-byte allocations are asserted invalid. Huge-page allocation can fail and fall back. Accounting can exceed requested sizes because of allocator usable size and block granularity. Tracker destructor asserts memory was freed/scheduled correctly.

Test signals: `arena_test.cc` validates memory accounting, approximate usage, alignment, lazy mappings, and unmapped large allocation behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/arena.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/arena.h -->
# sources/storage-engines/rocksdb/memory/arena.h

Purpose: Public declaration for the internal `Arena` allocator.

Important APIs/types/functions: `Arena`, constants `kInlineSize`, `kMinBlockSize`, `kMaxBlockSize`, `kAlignUnit`, `Allocate`, `AllocateAligned`, `ApproximateMemoryUsage`, `MemoryAllocatedBytes`, `AllocatedAndUnused`, `IrregularBlockNum`, `OptimizeBlockSize`, `ScopedArenaPtr`.

Control flow and state: the header documents the two-ended current block strategy: unaligned chunks allocate from one end, aligned chunks from the other. It stores inline memory, regular blocks, huge mappings, current allocation pointers, block accounting, and optional non-owned tracker.

State and persistence behavior: all allocations have arena lifetime. Inline block avoids heap allocation for initial small allocations.

Dependencies and integration points: implements `Allocator` and is used by memtables, skip lists, log buffers, and other short-lifetime internal structures.

Risks: not thread-safe by itself. `ApproximateMemoryUsage` excludes unused current-block space and is an estimate. Objects constructed in arena memory need explicit destruction, supported by `ScopedArenaPtr`.

Test signals: dedicated arena tests cover the major public accounting and allocation contracts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/arena.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/arena_test.cc -->
# sources/storage-engines/rocksdb/memory/arena_test.cc

Purpose: C++ test suite for `Arena` and memory mapping behavior.

Important APIs/types/functions: `MemoryAllocatedBytesTest`, `ApproximateMemoryUsageTest`, `SimpleTest`, `PopMinorPageFaultCount`, tests `Empty`, `MemoryAllocatedBytes`, `ApproximateMemoryUsage`, `Simple`, `MmapTest.AllocateLazyZeroed`, `UnmappedAllocation`.

Control flow and state: tests allocate large, small, aligned, and random-sized chunks, checking memory accounting within tolerance and verifying written byte patterns remain intact. Huge-page variants run when requested. Mapping tests allocate lazy-zeroed memory, count page faults while touching halves of the mapping, and verify data. Unmapped allocation repeatedly allocates a 1MB block until page-fault behavior indicates fresh unmapped pages.

State and persistence behavior: memory-only tests; no persistent files.

Dependencies and integration points: `Arena`, `MemMapping`, port page size, rusage page fault counters, jemalloc config checks.

Risks: page-fault assertions are platform-sensitive and include conservative bypass/fallback behavior. Memory accounting tolerances accommodate allocator overhead.

Test signals: strong coverage for arena allocation correctness, accounting, huge-page fallback tolerance, and OS lazy allocation assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/arena_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/concurrent_arena.cc -->
# sources/storage-engines/rocksdb/memory/concurrent_arena.cc

Purpose: Implementation details for `ConcurrentArena` construction and shard selection.

Important APIs/types/functions: thread-local `tls_cpuid`, constructor, `Repick`, constant `kMaxShardBlockSize`.

Control flow and state: constructor chooses shard block size as `min(128KB, block_size / 8)`, initializes the underlying `Arena`, and snapshots accounting via `Fixup`. `Repick` obtains a core-local shard and index, stores a nonzero encoded shard id in TLS, and returns the shard.

State and persistence behavior: in-memory thread-local shard selection and arena memory only.

Dependencies and integration points: `CoreLocalArray`, `Random` include, port threading support, `Arena`.

Risks: shard sizing trades contention reduction against fragmentation; very small block sizes can reduce shard utility. TLS cpu id can become stale after thread migration but design tolerates approximate sharding.

Test signals: no dedicated test in this subset; exercised indirectly by memtable/concurrent allocation users.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/concurrent_arena.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/concurrent_arena.h -->
# sources/storage-engines/rocksdb/memory/concurrent_arena.h

Purpose: Thread-safe allocator wrapper around `Arena` using fast arena locking and lazily used per-core shards for small allocations.

Important APIs/types/functions: `ConcurrentArena`, `Allocate`, `AllocateAligned`, `ApproximateMemoryUsage`, `MemoryAllocatedBytes`, `AllocatedAndUnused`, `IrregularBlockNum`, `AllocateImpl`, `Shard`, `Fixup`, `ShardAllocatedAndUnused`.

Control flow and state: large allocations, forced huge-page aligned allocations, and early uncontended allocations go directly to the arena under `arena_mutex_`. Otherwise a shard is selected via TLS/core-local state; if the shard lacks space, it reloads from the main arena with a shard block sized to minimize waste. Aligned requests are rounded to pointer alignment before sharding.

State and persistence behavior: allocations share arena lifetime. Atomic counters mirror arena accounting plus shard unused space.

Dependencies and integration points: used in concurrent memtable allocation paths where many writer threads allocate small nodes.

Risks: accounting is approximate under relaxed atomics. Fragmentation can occur in per-core shards. `AllocateAligned` uses `(bytes - 1)` and therefore assumes `bytes > 0`.

Test signals: not directly tested here; behavior is covered through broader memtable/concurrency tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/concurrent_arena.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/jemalloc_nodump_allocator.cc -->
# sources/storage-engines/rocksdb/memory/jemalloc_nodump_allocator.cc

Purpose: Specialized `MemoryAllocator` using jemalloc arenas whose extents are marked `MADV_DONTDUMP`, reducing core-dump footprint.

Important APIs/types/functions: `IsSupported`, constructor/destructor, `PrepareOptions`, `InitializeArenas`, `Allocate`, `Deallocate`, `UsableSize`, `GetArenaIndex`, `GetThreadSpecificCache`, static extent hook `Alloc`, `DestroyArena`, `DestroyThreadSpecificCache`, `NewJemallocNodumpAllocator`.

Control flow and state: support checks compile-time jemalloc/POSIX/MADV availability. `PrepareOptions` validates tcache bounds and arena count, then initializes arenas once. Arena initialization creates jemalloc arenas, copies extent hooks, records original alloc hook, replaces alloc hook with one that calls `madvise(..., MADV_DONTDUMP)`, and stores hook ownership. Allocations choose an arena randomly per thread and optionally create/use a thread-specific tcache. Destruction scrapes/destroys tcaches and arenas.

State and persistence behavior: process memory allocator state only; no persistence. Static original alloc hook is process-wide.

Dependencies and integration points: jemalloc mallctl/mallocx/dallocx, `MemoryAllocator` factory registry, configurable options, thread local pointer utility.

Risks: assumes new jemalloc arenas share the same original alloc hook. Some mallctl failures become `Incomplete`; tcache creation failure silently disables tcache. `madvise` failure asserts and prints stderr. Only available for specific build/platform combinations.

Test signals: memory allocator tests validate factory creation, option parsing, invalid bounds, direct constructor helper, and allocation when supported.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/jemalloc_nodump_allocator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/jemalloc_nodump_allocator.h -->
# sources/storage-engines/rocksdb/memory/jemalloc_nodump_allocator.h

Purpose: Declaration and build gating for `JemallocNodumpAllocator`.

Important APIs/types/functions: class `JemallocNodumpAllocator`, `kClassName`, `Name`, `IsSupported`, `IsMutable`, `PrepareOptions`, allocation overrides, jemalloc hook helpers, `original_alloc_`, `per_arena_hooks_`, `tcache_`, `arena_indexes_`.

Control flow and state: compile-time macros enable implementation only when RocksDB is built with jemalloc on POSIX with jemalloc major version >= 5 and `MADV_DONTDUMP`. The allocator is mutable until prepared, then holds arena and hook state.

State and persistence behavior: manages process heap arenas and thread-local tcaches; no persisted state.

Dependencies and integration points: `BaseMemoryAllocator`, `JemallocAllocatorOptions`, object registry/factory path, jemalloc helper headers.

Risks: conditional compilation means methods only exist under support macros; callers must check support. Static hook storage is shared across allocator instances.

Test signals: support-dependent tests instantiate and validate options/allocation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/jemalloc_nodump_allocator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/memkind_kmem_allocator.cc -->
# sources/storage-engines/rocksdb/memory/memkind_kmem_allocator.cc

Purpose: Implementation of a `MemoryAllocator` backed by memkind DAX KMEM when RocksDB is built with `MEMKIND`.

Important APIs/types/functions: `PrepareOptions`, `Allocate`, `Deallocate`, `UsableSize`.

Control flow and state: `PrepareOptions` checks compile-time support, then delegates to base allocator preparation. Under `MEMKIND`, `Allocate` calls `memkind_malloc(MEMKIND_DAX_KMEM, size)` and throws `std::bad_alloc` on null. `Deallocate` frees through `memkind_free`; usable size delegates to memkind when available.

State and persistence behavior: no internal state; allocations are process memory from the configured memkind.

Dependencies and integration points: memkind library, `BaseMemoryAllocator`, memory allocator factory registration.

Risks: unavailable unless compiled with memkind. Allocation failure throws rather than returning null. Behavior depends on DAX KMEM availability/configuration.

Test signals: memory allocator tests instantiate it conditionally and use it in block cache when supported.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/memkind_kmem_allocator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/memkind_kmem_allocator.h -->
# sources/storage-engines/rocksdb/memory/memkind_kmem_allocator.h

Purpose: Declaration of the memkind DAX KMEM memory allocator.

Important APIs/types/functions: `MemkindKmemAllocator`, `kClassName`, `Name`, `IsSupported`, `PrepareOptions`, conditional allocation overrides.

Control flow and state: support is a compile-time check on `MEMKIND`; unsupported builds return a reason string. Allocation methods are compiled only when support exists.

State and persistence behavior: stateless wrapper over memkind allocation APIs.

Dependencies and integration points: `MemoryAllocator::CreateFromString` registry and block cache allocator configuration.

Risks: build-dependent API surface. Runtime availability of desired memory kind is not deeply validated here beyond memkind allocation behavior.

Test signals: conditional parameterized allocator tests cover support and cache integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/memkind_kmem_allocator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/memory_allocator.cc -->
# sources/storage-engines/rocksdb/memory/memory_allocator.cc

Purpose: Registers built-in `MemoryAllocator` implementations and implements string-based allocator creation.

Important APIs/types/functions: `MemoryAllocatorWrapper`, `MemoryAllocator::CreateFromString`, `RegisterBuiltinAllocators`, factories for `DefaultMemoryAllocator`, `CountedMemoryAllocator`, `JemallocNodumpAllocator`, `MemkindKmemAllocator`.

Control flow and state: a static `once_flag` ensures built-in factories are registered once in the default object library. `CreateFromString` copies config options, enables prepare-options invocation, and calls `LoadManagedObject`. Wrapper type info allows nested `target` allocator configuration.

State and persistence behavior: process-global object registry state; no persistent files.

Dependencies and integration points: RocksDB customizable options/object registry, utility memory allocators, jemalloc/memkind allocator classes, cache/table options.

Risks: unsupported optional allocators return null from factories with an error message. String parsing depends on the customizable object framework. Registry is global and long-lived.

Test signals: `memory_allocator_test.cc` validates creation, string round-trip, unsupported behavior, and block cache integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/memory_allocator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/memory_allocator_impl.h -->
# sources/storage-engines/rocksdb/memory/memory_allocator_impl.h

Purpose: Small helper layer for cache/block allocations that may use a configured `MemoryAllocator`.

Important APIs/types/functions: `CacheAllocationDeleter`, `CacheAllocationPtr`, `AllocateBlock`, `AllocateAndCopyBlock`.

Control flow and state: `AllocateBlock` calls allocator `Allocate` when present and returns a `unique_ptr` with a deleter that calls `Deallocate`; otherwise it allocates `new char[size]`. `AllocateAndCopyBlock` allocates the target size and copies `Slice` bytes into the block.

State and persistence behavior: allocation ownership is held by `CacheAllocationPtr`; no persistence.

Dependencies and integration points: block cache/table code needing allocator-aware memory ownership, `Slice`, `MemoryAllocator`.

Risks: deleter stores a raw allocator pointer, so the allocator must outlive returned pointers. `AllocateAndCopyBlock` assumes allocation succeeds and data size is appropriate.

Test signals: indirectly covered by memory allocator block cache test and cache code.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/memory_allocator_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/memory_allocator_test.cc -->
# sources/storage-engines/rocksdb/memory/memory_allocator_test.cc

Purpose: C++ tests for `MemoryAllocator` factories, allocation, option parsing, and block-cache integration.

Important APIs/types/functions: parameterized `MemoryAllocatorTest`, tests `Allocate`, `CreateAllocator`, `DatabaseBlockCache`, `CreateMemoryAllocatorTest.JemallocOptionsTest`, `NewJemallocNodumpAllocator`.

Control flow and state: each parameter attempts `MemoryAllocator::CreateFromString` and records expected support. Supported allocators allocate/deallocate 1024 bytes and report usable size. String creation tests serialize via `ToString` and recreate. Database test configures an LRU block cache with the allocator, writes/flushes 200 keys, reads them back, and asserts cache usage grew. Jemalloc tests validate default options, invalid tcache bounds when limiting is enabled, accepted bounds when limiting disabled, and helper construction.

State and persistence behavior: creates a temporary DB for cache integration and destroys it. Allocator state is process-local.

Dependencies and integration points: `NewLRUCache`, block-based table factory, DB open/put/flush/get, optional jemalloc and memkind builds.

Risks: unsupported optional allocators are bypassed. Cache usage threshold is coarse and may depend on block/cache metadata. TODO notes lite mode incompatibility because tests rely on object creation by string.

Test signals: solid coverage for default allocator and conditional specialized allocators in factory and cache paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/memory_allocator_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/memory_usage.h -->
# sources/storage-engines/rocksdb/memory/memory_usage.h

Purpose: Template helpers for approximate memory usage of hash-map containers.

Important APIs/types/functions: `ApproximateMemoryUsage(std::unordered_map<...>)` and optional `ApproximateMemoryUsage(folly::F14FastMap<...>)`.

Control flow and state: unordered-map estimate adds object size, per-entry value plus next pointer, and bucket array size. Folly implementation delegates to `getAllocatedMemorySize` plus object size.

State and persistence behavior: pure calculation over container state; no mutation or persistence.

Dependencies and integration points: RocksDB memory accounting code for in-memory metadata maps; optional Folly support.

Risks: estimates are approximate and allocator/container-implementation dependent. The unordered-map formula may drift with STL implementation details.

Test signals: no direct tests in this subset; correctness is approximate by design.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/memory/memory_usage.h -->
