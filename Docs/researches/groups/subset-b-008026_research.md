# subset-b-008026 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBBatchOperation.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBBatchOperation.java

Purpose: JUnit coverage for `RDBBatchOperation`, both at the write-batch command assembly layer and against real `DBStore` instances backed by RocksDB.

Important APIs/types/functions: `RDBBatchOperation.newAtomicOperation`, `BatchOperation`, `DBStoreBuilder`, `Table.putWithBatch`, `Table.deleteWithBatch`, `DBStore.commitBatchOperation`, `StringCodec`, `CodecBufferCodec`, and the test-only `TrackingUtilManagedWriteBatchForTesting.Operation`.

Control flow: `testBatchOperation` mocks a column family and verifies that repeated operations on the same key are compacted so only the effective batch writes/deletes are emitted. `testRDBBatchOperationWithRDB` runs 30,000 random puts/deletes into one store through a batch and into a second store directly, commits the batch, then iterates both stores to prove equivalent persisted order and contents.

State and persistence behavior: Real tests create two temporary RocksDB stores and compare persisted key/value streams after commit. The mocked test inspects in-memory write batch state grouped by column family name.

Dependencies and integration points: Integrates with RocksDB native library loading, Ozone configuration, direct and persisted codec-buffer formats, `RocksDatabase.ColumnFamily`, Mockito, and Ratis `CheckedConsumer`.

Risks: Random operation generation can make failures non-reproducible. The large 30,000 operation loop is performance-sensitive. Correctness depends on byte-buffer lifetime and direct-buffer handling during batch deduplication.

Test signals: Strong signal for batch equivalence, direct/persisted codec path parity, and last-write-wins behavior for duplicate keys before commit.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBBatchOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStore.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStore.java

Purpose: Unit and integration tests for `RDBStore`, the RocksDB-backed database store abstraction used by HDDS/Ozone metadata components.

Important APIs/types/functions: `newManagedDBOptions`, `newRDBStore`, `RDBStore.getTable`, `listTables`, `flushDB`, `compactDB`, `compactTable`, `getCheckpoint`, `getUpdatesSince`, `getEstimatedKeyCount`, `RDBTable`, `DBCheckpoint`, `DBUpdatesWrapper`, and `TableConfig`.

Control flow: Setup builds a temporary RocksDB with default plus named column families and statistics enabled. Tests write random rows, flush and compact DB/table data, inspect table listing and missing-table errors, create checkpoints, reopen from checkpoints, request update batches by sequence number, simulate reopening with a removed configured family, and compare SST files between checkpoints.

State and persistence behavior: The tests exercise RocksDB column-family state, live file metadata, checkpoint directories, sequence numbers, WAL/update wrappers, persisted rows across reopen, and cleanup of checkpoint directories.

Dependencies and integration points: Depends on RocksDB `Statistics`, managed RocksDB option wrappers, Ozone constants for SST suffixes, temporary files, and byte-array tables.

Risks: Some estimates are checked with loose bounds and the assertions use `||` where an intended range may have been `&&`, reducing precision. `compareSstWithSameName` reads file lists from `checkpoint1` twice, so same-name comparison may miss files present only in the second checkpoint. Random data makes exact debugging harder.

Test signals: Covers store lifecycle, compaction, checkpoint generation/cleanup, update extraction limits, downgrade column-family behavior, table lookup/listing, and leak detection through `CodecBuffer`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStoreByteArrayIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStoreByteArrayIterator.java

Purpose: Specifies expected behavior for `RDBStoreByteArrayIterator`, the byte-array iterator wrapper around RocksDB iterators.

Important APIs/types/functions: `RDBStoreByteArrayIterator`, `ManagedRocksIterator`, `RDBTable`, `IteratorType` (`NEITHER`, `KEY_ONLY`, `VALUE_ONLY`, `KEY_AND_VALUE`), `seek`, `seekToFirst`, `seekToLast`, `removeFromDB`, `forEachRemaining`, `hasNext`, and `next`.

Control flow: Mockito stubs `RocksIterator` validity, keys, and values. Tests verify constructor seeking, forward iteration, `hasNext` invalidation behavior, ordered RocksDB calls during `next`, seek semantics, removal through the owning table, close propagation, prefix-specific seek behavior, and unsupported `seekToLast` for prefixed iterators.

State and persistence behavior: No real RocksDB persistence is used; state is simulated through mocked iterator sequences. `removeFromDB` is the only path that mutates a mocked table.

Dependencies and integration points: Integrates RocksDB iterator API with HDDS `Table.KeyValue` abstraction and table deletion. Uses Mockito in-order verification and log-level adjustment for managed object diagnostics.

Risks: Mocked iterator behavior can diverge from native RocksDB edge cases. Prefix tests only validate a key equal to the prefix, not keys that merely start with it.

Test signals: Strong call-order signal for iterator correctness, iterator type key/value read flags, table deletion delegation, and prefix iterator restrictions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStoreByteArrayIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStoreCodecBufferIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStoreCodecBufferIterator.java

Purpose: Mirrors byte-array iterator tests for `RDBStoreCodecBufferIterator`, validating the direct `CodecBuffer` path that avoids unnecessary array copies.

Important APIs/types/functions: `RDBStoreCodecBufferIterator`, `CodecBuffer`, `ManagedRocksIterator`, `RDBTable.delete(ByteBuffer)`, `IteratorType.KEY_AND_VALUE`, `seek(ByteBuffer)`, `key(ByteBuffer)`, and `value(ByteBuffer)`.

Control flow: Helper answers write bytes into supplied `ByteBuffer` instances to emulate RocksDB direct-buffer APIs. Tests cover foreach iteration, `hasNext`, constructor and explicit seeking, `next` call order, seek result materialization, key/value reads, removal from DB using a buffered key, unsupported removal without a table, close, null-prefix iteration, and prefixed iterator constraints.

State and persistence behavior: Uses mocked RocksDB state with explicit leak detection and `CodecTestUtil.gc` to check buffer lifecycle after iterator use.

Dependencies and integration points: Depends on RocksDB direct buffer iterator methods, `CodecBuffer` lifetime management, table deletion by `ByteBuffer`, Mockito, and HDDS string/hex utilities for debug output.

Risks: Direct buffers require careful closing; tests assert no leaks but rely on GC-triggered cleanup. Debug `System.out` output is noisy. Prefix matching is only lightly sampled.

Test signals: Good coverage of direct-buffer iterator call order, resource closure, deletion delegation, and prefix iterator behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStoreCodecBufferIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStoreIteratorWithDBClose.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStoreIteratorWithDBClose.java

Purpose: Regression tests for safe iterator behavior while `RDBStore`/RocksDB is closed concurrently.

Important APIs/types/functions: `RDBStore.close`, `RDBTable.iterator`, `Table.KeyValueIterator`, `IteratorType.KEY_AND_VALUE`, `hasNext`, `forEachRemaining`, iterator `close`, and package-private `RDBTable.isClosed`.

Control flow: Setup creates a temporary store, table, and 100 entries. Tests launch scanner threads, close the DB mid-iteration, verify `hasNext` returns false without exceptions, prove physical DB close waits for open iterator references, validate end-to-end concurrent close/scan races, test `forEachRemaining` under close, and ensure iterator close after DB close does not throw.

State and persistence behavior: Real RocksDB data is written before concurrency tests. Main state under test is the DB closed flag and internal reference counter preventing physical close while iterators are open.

Dependencies and integration points: Uses Java executors, futures, latches, atomics, temporary RocksDB stores, and shared helpers from `TestRDBStore`.

Risks: Timing-based sleeps can be flaky on slow or overloaded hosts. Tests intentionally block close until iterator release, so leaked iterators would hang. Shutdown of executors is manual.

Test signals: High-value concurrency signal for volume-failure/background-scanner races and native crash prevention when RocksDB is closed during scans.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStoreIteratorWithDBClose.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBTableStore.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBTableStore.java

Purpose: Broad integration coverage for raw `RDBTable` operations and typed table access over RocksDB column families.

Important APIs/types/functions: `RDBTable`, `Table.put/get/delete/deleteRange`, `putWithBatch`, `deleteWithBatch`, `iterator`, `getRangeKVs`, `dumpToFileWithPrefix`, `loadFromFile`, `isExist`, `getIfExist`, `getEstimatedKeyCount`, `RDBMetrics`, and typed table creation with `StringCodec`, `ByteStringCodec`, and `CacheType`.

Control flow: Setup creates normal and fixed-prefix column families. Tests cover handle retrieval, put/get/empty state, deletes and range deletes, batch writes/deletes, cross-codec typed reads, iterator counts, `isExist` and `getIfExist` metrics, large-value `ByteBuffer` reads, estimated row counts, iterator removal at several positions, prefixed byte/string iteration, prefixed range fetches, and dump/load of prefix-specific SST data including empty dumps.

State and persistence behavior: Mutates real RocksDB tables, closes/reopens store in existence tests, inspects metrics counters, writes dump files, and tests prefix extractor behavior.

Dependencies and integration points: Uses managed RocksDB options, RocksDB prefix extractors, Ozone metadata filters, protobuf `ByteString`, random test data, and `TypedTable`.

Risks: Static `count` is not reset per test and may cross-contaminate if tests are reordered. Random strings and prefix ordering can complicate reproductions. Metrics assertions couple tests to exact implementation counters.

Test signals: Excellent API-surface signal for raw table CRUD, batching, iterators, prefix scans, range reads, metrics, dump/load, and typed-codec interoperability.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBTableStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestTypedRDBTableStore.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestTypedRDBTableStore.java

Purpose: Tests `TypedTable<String,String>` behavior over `RDBTable`, especially cache-overlay semantics and typed CRUD.

Important APIs/types/functions: `TypedTable`, `StringCodec`, `ByteArrayCodec`, `TableCache.CacheType.PARTIAL_CACHE`, `CacheKey`, `CacheValue`, `addCacheEntry`, `cleanupCache`, `iterator`, `putWithBatch`, `deleteWithBatch`, `isExist`, `getIfExist`, and `getEstimatedKeyCount`.

Control flow: Setup creates ten column families. Tests verify typed put/get/empty, delete, batch put/delete, iterator/foreach counts, exception translation from raw `RDBTable.iterator`, cache reads for synthetic entries, cache tombstone handling, cache cleanup by epoch, existence/get-if-exists with and without cache entries, estimated counts, and byte-array typed table copy semantics.

State and persistence behavior: Real RocksDB state backs typed tables, while `addCacheEntry` injects in-memory overlay values or tombstones. Cleanup removes cache epochs and waits for expected size changes.

Dependencies and integration points: Uses RocksDB managed options, HDDS cache classes, Mockito for exception translation, and `GenericTestUtils.waitFor`.

Risks: Static iterator `count` is shared across tests. A loop in `testTypedTableWithCache` always reads key `"1"` instead of the loop key, narrowing coverage. Cache tests are sensitive to epoch cleanup implementation details.

Test signals: Good signal for typed table CRUD, batch delegation, cache overlay precedence, tombstone behavior, cleanup, exception wrapping, and byte-array defensive-copy semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestTypedRDBTableStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestTypedTable.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestTypedTable.java

Purpose: Deep tests for `TypedTable` codec behavior, key ordering, empty keys/values, and iterator modes over typed metadata keys.

Important APIs/types/functions: `TypedTable`, `Codec`, `ByteArrayCodec`, `StringCodec`, `LongCodec`, `ContainerID.getCodec`, `TableIterator`, `Table.KeyValueIterator`, iterator modes `NEITHER`, `KEY_ONLY`, `VALUE_ONLY`, `KEY_AND_VALUE`, `keyIterator`, and `valueIterator`.

Control flow: Setup creates several RocksDB column families and tracks closeables. Tests exercise empty byte-array and string keys/values with both codec-buffer and byte-array codec paths, compare `ContainerID` and `Long` persisted key formats by reopening tables with alternate key codecs, populate thousands of generated boundary/random keys, and validate prefix and non-prefix iterators across all iterator read modes.

State and persistence behavior: Real RocksDB persistence is used to prove codec-stable key serialization across different logical key types. Iterator tests destructively remove entries from expected maps as they are observed.

Dependencies and integration points: Integrates HDDS codecs, SCM `ContainerID`, table cache type selection, RocksDB column families, and leak detection.

Risks: Heavy random key generation can lengthen runs and reduce determinism. Prefix tests rely on stringified container IDs and map ordering. The compatibility test assumes `ContainerID` and `Long` codecs intentionally share persisted representation.

Test signals: Strong signal for typed codec compatibility, empty value handling, iterator read-mode laziness, key/value iterator alignment, and prefix scan correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestTypedTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/cache/TestTableCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/cache/TestTableCache.java

Purpose: Parameterized unit tests for table cache implementations: full cache, partial cache, and no-cache behavior.

Important APIs/types/functions: `TableCache`, `FullTableCache`, `PartialTableCache`, `TableNoCache`, `CacheKey`, `CacheValue`, `CacheStats`, `evictCache`, `getEpochEntries`, `iterator`, `size`, and `TableCache.CacheType`.

Control flow: Tests create cache instances by type, populate epoch-indexed entries, evict selected epochs, verify full-cache no-op/retention rules versus partial-cache deletion rules, handle renamed keys and overrides, process delete tombstones, run asynchronous writes, validate nonconsecutive epoch lists, inspect stats counters, and assert no-cache ignores writes.

State and persistence behavior: All state is in-memory cache state. Epoch maps model cleanup state used by HA transaction application and cache compaction.

Dependencies and integration points: Uses JUnit parameterization, `CompletableFuture`, `GenericTestUtils` log-level changes, and cache internals exposed through stats and epoch accessors.

Risks: Tests rely on implementation-specific epoch-entry sizes. Parallel write coverage is limited to simple asynchronous insertion and not a full race detector.

Test signals: Strong cache semantics signal for eviction, overridden entries, tombstones, stats, full versus partial behavior, and no-cache null behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/cache/TestTableCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/cache/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/cache/package-info.java

Purpose: Package-level documentation for DB cache utility tests.

Important APIs/types/functions: Declares package `org.apache.hadoop.hdds.utils.db.cache` and documents that this package contains tests for DB cache utilities.

Control flow: No executable control flow.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Serves Javadoc/package metadata for the cache test package.

Risks: Minimal; stale package comments could become inaccurate if the package scope changes.

Test signals: No runtime test signal; supports source organization and generated Javadocs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/cache/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/package-info.java

Purpose: Package-level documentation for DB utility tests.

Important APIs/types/functions: Declares package `org.apache.hadoop.hdds.utils.db`.

Control flow: No executable control flow.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Provides Javadoc metadata for the RocksDB/table utility test package.

Risks: Minimal; package comment is broad and could drift from actual package contents.

Test signals: No runtime assertions; organizational metadata only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/package-info.java

Purpose: Package-level documentation for HDDS utility test helpers.

Important APIs/types/functions: Declares package `org.apache.hadoop.hdds.utils` with a short comment identifying DB test utilities.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Javadoc/package metadata for utility test code.

Risks: The comment is narrow relative to a general `utils` package and may not describe all package contents over time.

Test signals: No runtime signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/AuditLogTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/AuditLogTestUtils.java

Purpose: Static test helper for enabling, reading, verifying, truncating, and deleting Ozone audit logs.

Important APIs/types/functions: `enableAuditLog`, `verifyAuditLog`, `auditLogContains`, `truncateAuditLogFile`, `deleteAuditLogFile`, `AuditAction`, and `AuditEventStatus`.

Control flow: `enableAuditLog` sets the Log4j configuration system property. `verifyAuditLog` waits until `audit.log` contains an action/status pair. `auditLogContains` reads the whole file and checks all requested substrings, returning false on I/O failure. Truncate/delete helpers mutate the fixed audit log path.

State and persistence behavior: Operates on the process system property and a working-directory `audit.log` file.

Dependencies and integration points: Uses Apache Commons IO, Java NIO files, `GenericTestUtils.waitFor`, and the audit logging API.

Risks: Fixed relative file name can collide across tests running in the same directory. Whole-file reads are acceptable for tests but not scalable. Silent false on I/O errors can hide setup problems until timeout.

Test signals: Supports audit integration tests by polling asynchronous log writes and resetting audit log state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/AuditLogTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/DummyAction.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/DummyAction.java

Purpose: Test enum implementing `AuditAction` for representative audit operations.

Important APIs/types/functions: Enum constants for create/read/update/delete volume, bucket, key operations plus owner/quota changes; `getAction`.

Control flow: `getAction` returns the enum constant string.

State and persistence behavior: Stateless enum values.

Dependencies and integration points: Used by audit message tests to avoid binding to production-specific actions while exercising `AuditAction`.

Risks: Dummy action names may drift from real audit operation vocabulary, but they intentionally provide generic coverage.

Test signals: Supplies deterministic action strings for audit logger formatting and exclusion tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/DummyAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/DummyEntity.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/DummyEntity.java

Purpose: Simple test implementation of `Auditable` that exposes two mutable key/value fields as audit parameters.

Important APIs/types/functions: `DummyEntity`, getters/setters for `key1` and `key2`, and `toAuditMap`.

Control flow: Constructor initializes default values. `toAuditMap` creates a new `HashMap` containing the two current field values.

State and persistence behavior: In-memory mutable fields only; no persistence.

Dependencies and integration points: Used by audit logger tests to provide message parameters through the production `Auditable` contract.

Risks: HashMap iteration order is not guaranteed, though audit tests generally check value presence rather than relying entirely on map order.

Test signals: Provides stable audit parameter data for formatted message assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/DummyEntity.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/TestOzoneAuditLogger.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/TestOzoneAuditLogger.java

Purpose: Tests formatting, severity routing, filtering, and exception logging for `AuditLogger`.

Important APIs/types/functions: `AuditLogger`, `AuditLoggerType.OMLOGGER`, `AuditMessage.Builder`, `logWriteSuccess`, `logWriteFailure`, `logReadSuccess`, `logReadFailure`, `logAuthFailure`, `refreshDebugCmdSet`, `AuditLogger.AUDIT_LOG_DEBUG_CMD_LIST_PREFIX`, and `AuditMessage.getFormattedMessage`.

Control flow: Static setup selects `auditlog.properties` and builds reusable audit messages. Each test logs a message, reads `audit.log`, retries for asynchronous delivery, and checks expected level/logger/class/message substrings. The exclusion test configures a debug command list to suppress `CREATE_VOLUME`. A multiline exception test asserts both formatted audit line and stack trace lines.

State and persistence behavior: Writes and clears a working-directory `audit.log`; deletes it after all tests. `AUDIT.refreshDebugCmdSet` updates logger filtering from configuration.

Dependencies and integration points: Integrates Log4j2 config, Ozone configuration, commons-io file reads/writes, dummy audit action/entity, and AssertJ.

Risks: File-based assertions can be flaky under parallel execution or if another test writes `audit.log`. Line-index assumptions in multiline exception checks couple to logger layout.

Test signals: Good signal for audit log level policy, message content, debug exclusion filtering, auth failure logging, and exception stack trace inclusion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/TestOzoneAuditLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/package-info.java

Purpose: Package-level documentation for Ozone audit logger unit tests.

Important APIs/types/functions: Declares package `org.apache.hadoop.ozone.audit` and notes that Log4j2 test configuration is loaded from `src/test/resources/auditlog.properties`.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Javadoc metadata for the audit test package.

Risks: The referenced config file path must remain valid for the comment to be accurate.

Test signals: No runtime signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/lease/TestLeaseManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/lease/TestLeaseManager.java

Purpose: Unit tests for `LeaseManager` acquisition, release, expiration, callbacks, reuse, and renewal.

Important APIs/types/functions: `LeaseManager`, `Lease`, `LeaseException`, `LeaseAlreadyExistException`, `LeaseNotFoundException`, `acquire`, `get`, `release`, `shutdown`, `start`, `hasExpired`, `getRemainingTime`, `getLeaseLifeTime`, and `renew`.

Control flow: Tests create a `LeaseManager<DummyResource>`, start it, acquire leases with default/custom timeouts and callbacks, assert duplicate acquisition and missing lease exceptions, release leases, sleep past expiration, verify callback execution or non-execution on release, reacquire resources after release/timeout, and renew a lease.

State and persistence behavior: All state is in-memory lease registry plus manager background expiration behavior. Callback tests mutate a map tracking lease status.

Dependencies and integration points: Uses a nested resource object with stable `equals`, `hashCode`, and `toString` to satisfy lease-map and error-message behavior.

Risks: Several tests sleep for lease duration plus one second, making the suite slow and timing-sensitive. Interrupted sleep retries full duration. Managers must be shut down to avoid lingering scheduler threads.

Test signals: Strong lifecycle signal for lease uniqueness, expiry removal, callback semantics, resource reuse, custom timeouts, and renewal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/lease/TestLeaseManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/lease/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/lease/package-info.java

Purpose: Package documentation for lease management unit tests.

Important APIs/types/functions: Declares package `org.apache.hadoop.ozone.lease`.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Javadoc metadata for lease tests.

Risks: Minimal.

Test signals: No runtime signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/lease/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/package-info.java

Purpose: Package documentation for Ozone-related test helper classes and common utility tests.

Important APIs/types/functions: Declares package `org.apache.hadoop.ozone`.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Javadoc metadata for the broader Ozone test package.

Risks: Broad description can become vague as package content changes.

Test signals: No runtime signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/InjectedUpgradeFinalizationExecutor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/InjectedUpgradeFinalizationExecutor.java

Purpose: Test executor that extends `DefaultUpgradeFinalizationExecutor` with injectable pause/abort points for upgrade finalization tests.

Important APIs/types/functions: `InjectedUpgradeFinalizationExecutor<T>`, enum `UpgradeTestInjectionPoints`, `UpgradeTestInjectionAbort`, `configureTestInjectionFunction`, `injectTestFunctionAtThisPoint`, and overridden `execute`.

Control flow: `execute` calls injected functions before pre-finalize, after pre-finalize, after feature finalization, and after post-finalize. If an injected function returns true, an internal exception aborts the flow. Any exception logs a warning and resets upgrade state to `FINALIZATION_REQUIRED` when finalization is still needed, then always calls `markFinalizationDone`.

State and persistence behavior: Holds a configured `Callable<Boolean>` and injection point. Mutates the finalizer version manager's upgrade state on failed/incomplete finalization.

Dependencies and integration points: Integrates with `BasicUpgradeFinalizer`, `DefaultUpgradeFinalizationExecutor`, `UpgradeFinalization.Status`, and SLF4J logging.

Risks: Catch-all exception handling suppresses injected errors by design, so tests must assert resulting state. Injection point numeric values skip 3, which is harmless but non-obvious.

Test signals: Enables deterministic tests for concurrent, paused, and terminated upgrade finalization paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/InjectedUpgradeFinalizationExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestAbstractLayoutVersionManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestAbstractLayoutVersionManager.java

Purpose: Tests generic `AbstractLayoutVersionManager` initialization, feature finalization, feature allowance, and JMX exposure.

Important APIs/types/functions: `AbstractLayoutVersionManager`, `LayoutFeature`, `init`, `finalized`, `needsFinalization`, `unfinalizedFeatures`, `isAllowed`, metadata/software layout version getters, and MBean attributes.

Control flow: Tests initialize with metadata behind or equal to software layout version, assert failure when metadata version exceeds available features, finalize the next feature, reject out-of-order finalization, verify idempotent already-finalized calls, check feature allowed/disallowed status before and after finalization, and read JMX attributes from the platform MBean server.

State and persistence behavior: Uses in-memory layout feature lists and metadata layout version; registers/closes manager JMX state.

Dependencies and integration points: Uses Mockito spy initialization, JMX `MBeanServer`, and anonymous `LayoutFeature` implementations.

Risks: JMX object names can conflict if managers are not closed or tests run in parallel. The test features return null descriptions, so description handling is not covered.

Test signals: Strong signal for layout version invariants, ordered finalization, allowed-feature gates, and management visibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestAbstractLayoutVersionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestBasicUpgradeFinalizer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestBasicUpgradeFinalizer.java

Purpose: Tests `BasicUpgradeFinalizer` phase ordering, already-finalized short-circuiting, and concurrent finalization status behavior.

Important APIs/types/functions: `BasicUpgradeFinalizer`, `UpgradeFinalizer`, `UpgradeFinalization.StatusAndMessages`, `finalize`, `reportStatus`, `getStatus`, `isFinalizationDone`, `preFinalizeUpgrade`, `finalizeLayoutFeature`, `postFinalizeUpgrade`, and `UpgradeTestUtils.newPausingFinalizationExecutor`.

Control flow: One test spies a simple finalizer and verifies pre-finalize, feature finalization, and post-finalize occur in order and persist storage layout versions. Another confirms no phases run when metadata is already final. The concurrency test pauses finalization at an injected point, checks simultaneous finalize/status calls report in-progress, resumes, and verifies subsequent status calls report done.

State and persistence behavior: Mock layout version managers hold version state. Mock `Storage` receives layout version and `persistCurrentState` calls during feature finalization.

Dependencies and integration points: Uses injected executor, mock layout features from `TestUpgradeFinalizerActions`, Java futures/latches/executors, Mockito in-order verification, and SLF4J.

Risks: Executors are created per submitted task and not explicitly shut down, which can leave transient threads. Concurrency behavior depends on latch placement.

Test signals: High-value signal for upgrade finalizer state machine, phase ordering, finalization idempotence, and client-visible concurrent statuses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestBasicUpgradeFinalizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestDefaultUpgradeFinalizationExecutor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestDefaultUpgradeFinalizationExecutor.java

Purpose: Tests exception propagation policy in `DefaultUpgradeFinalizationExecutor`.

Important APIs/types/functions: `DefaultUpgradeFinalizationExecutor.execute`, anonymous `BasicUpgradeFinalizer`, `preFinalizeUpgrade`, `postFinalizeUpgrade`, `finalizeLayoutFeature`, and `AbstractLayoutVersionManager.needsFinalization`.

Control flow: The first test creates a finalizer whose pre-finalize step throws and asserts `execute` propagates the `IOException`. The second creates a finalizer whose post-finalize step throws while finalization is no longer needed and asserts the executor completes without throwing.

State and persistence behavior: State is mocked through `needsFinalization`; no persisted layout files are used.

Dependencies and integration points: Uses Mockito to mock the layout version manager and JUnit exception assertions.

Risks: Raw generic usage hides type-safety issues. Tests do not cover exceptions during individual feature finalization.

Test signals: Focused signal for pre-finalize hard failure versus post-finalize soft failure behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestDefaultUpgradeFinalizationExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestUpgradeFinalizerActions.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestUpgradeFinalizerActions.java

Purpose: Test scaffolding for upgrade finalizer action behavior.

Important APIs/types/functions: `MockUpgradeFinalizer`, `MockLayoutVersionManager`, enum `MockLayoutFeature`, `MockLayoutFeature.addAction`, `MockLayoutFeature.action`, and `MockFailingUpgradeAction`.

Control flow: Mock finalizer overrides pre/post/finalize methods as no-ops. Mock layout manager initializes with the enum feature set. Mock layout features expose layout versions and optional attached actions. Failing action throws an `IllegalStateException` when executed.

State and persistence behavior: In-memory mock layout version state and per-enum optional action field; no persistence.

Dependencies and integration points: Integrates with `BasicUpgradeFinalizer`, `AbstractLayoutVersionManager`, `LayoutFeature`, `HDDSUpgradeAction`, and `MockComponent`.

Risks: Enum action field is mutable and shared across tests, so tests using it must reset state to avoid contamination.

Test signals: Provides reusable fixtures for action success/failure and feature version ordering in upgrade tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestUpgradeFinalizerActions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/UpgradeTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/UpgradeTestUtils.java

Purpose: Shared utilities for upgrade tests, including VERSION file creation and injected finalization executors.

Important APIs/types/functions: `createVersionFile`, `newPausingFinalizationExecutor`, `newTerminatingFinalizationExecutor`, `StorageInfo`, `HddsProtos.NodeType`, `InjectedUpgradeFinalizationExecutor`, and `UpgradeTestInjectionPoints`.

Control flow: `createVersionFile` builds `StorageInfo` with node type, random cluster ID, current time, metadata layout version, optional properties, then writes a `VERSION` file. Executor helpers configure injection callbacks that either pause on latches and resume or terminate by returning true.

State and persistence behavior: Writes VERSION files under caller-provided directories. Executor callbacks synchronize on provided latches and log state transitions.

Dependencies and integration points: Uses Ozone storage metadata, protobuf node types, Java properties, UUIDs, latches, and SLF4J.

Risks: Version file content includes current time and UUID, so exact file bytes are nondeterministic. Pausing executor must be unpaused or tests can hang.

Test signals: Enables deterministic upgrade storage setup and controlled finalization concurrency/failure tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/UpgradeTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/util/TestBackgroundService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/util/TestBackgroundService.java

Purpose: Tests `BackgroundService` task execution semantics, especially waiting for all submitted tasks and single-worker sequencing.

Important APIs/types/functions: `BackgroundService`, `BackgroundTaskQueue`, `BackgroundTask`, `BackgroundTaskResult.EmptyTaskResult`, `getTasks`, `execTaskCompletion`, `shutdown`, and `start`.

Control flow: A nested `TestTask` increments a per-index map entry under a lock. One test queues ten tasks, pre-locks even-index tasks, starts a service with ten workers, verifies odd tasks complete while even tasks block and completion callback is not called, unlocks, and waits for completion. Another runs five tasks with one worker and verifies all complete.

State and persistence behavior: State is in-memory task queue, maps, locks, and `runCount`; no persistence.

Dependencies and integration points: Uses Java locks, atomics, streams, `GenericTestUtils.waitFor`, JUnit timeout, and HDDS background service utilities.

Risks: Timing-sensitive sleeps and lock coordination can be flaky on slow hosts. The test intentionally blocks worker threads until locks are released.

Test signals: Strong signal that `BackgroundService` waits for the whole batch before invoking completion and respects configured worker thread count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/util/TestBackgroundService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/enforce-error.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/enforce-error.xml

Purpose: XML topology fixture for prefix-enforcement validation failure.

Important APIs/types/functions: Defines `configuration`, `layoutversion`, four `layer` entries, and a `topology` path with `enforceprefix>true</enforceprefix>`.

Control flow: Parser input only. The path `/datacenter/rack/nodegroup/node` references layers where `rack` has prefix `rack` but `nodegroup`/`node` have empty prefixes while enforcement is true.

State and persistence behavior: Static resource file; no runtime state except parser-derived topology model.

Dependencies and integration points: Consumed by network topology parser tests for XML schema and prefix checks.

Risks: Type casing varies (`ROOT`, `InnerNode`, `Leaf`), so parser case-sensitivity is part of the fixture assumptions.

Test signals: Negative signal for enforced prefix validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/enforce-error.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/external-entity.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/external-entity.xml

Purpose: XML security fixture containing an external entity declaration to test XXE hardening.

Important APIs/types/functions: Defines a `DOCTYPE` with entity `xxe` pointing to `file:///etc/passwd`, then uses `&xxe;` as a layer type.

Control flow: Parser input only. A secure parser should reject or ignore external entity expansion and fail validation rather than reading local files.

State and persistence behavior: Static resource; attempts to reference external file system content only if XML parser is insecure.

Dependencies and integration points: Consumed by network topology XML parser/security tests.

Risks: If parser features are misconfigured, this fixture could expose local file content during tests. It must remain in test resources only.

Test signals: Security regression signal for disabling external entity expansion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/external-entity.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/good.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/good.xml

Purpose: Valid XML network topology fixture.

Important APIs/types/functions: Defines layout version 1, layers for datacenter/root, rack, nodegroup, and node/leaf, default locations for inner layers, and topology path `/datacenter/rack/nodegroup/node` with prefix enforcement enabled.

Control flow: Parser input only; expected to build a valid ordered topology hierarchy.

State and persistence behavior: Static resource file.

Dependencies and integration points: Positive fixture for network topology XML parsing and validation tests.

Risks: Prefixes and defaults encode expected parser conventions; changing network topology schema requires updating this fixture.

Test signals: Baseline positive signal for XML topology parsing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/good.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/good.yaml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/good.yaml

Purpose: Valid YAML network topology fixture.

Important APIs/types/functions: Root object with `cost`, `prefix`, `type`, `defaultName`, and nested `sublayer` arrays down to a leaf node.

Control flow: Parser input only; expected to produce root -> datacenter -> rack -> nodegroup -> node.

State and persistence behavior: Static YAML resource.

Dependencies and integration points: Positive fixture for YAML topology parser tests.

Risks: YAML comments document schema expectations such as explicit prefixes for inner nodes; parser/schema changes may require coordinated fixture updates.

Test signals: Baseline positive signal for YAML topology parsing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/good.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/invalid-cost.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/invalid-cost.xml

Purpose: Negative XML topology fixture for invalid layer cost.

Important APIs/types/functions: Layer `rack` has `<cost>-1</cost>` while costs are expected to be nonnegative.

Control flow: Parser input only; validation should reject the configuration.

State and persistence behavior: Static resource.

Dependencies and integration points: Used by topology parser validation tests.

Risks: Also includes mixed type casing and defaults; tests should ensure the intended failure is cost, not another validation branch.

Test signals: Negative signal for cost validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/invalid-cost.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/invalid-version.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/invalid-version.xml

Purpose: Negative XML topology fixture for nonnumeric layout version.

Important APIs/types/functions: `<layoutversion>a</layoutversion>` with otherwise similar layer/topology structure.

Control flow: Parser input only; version parsing should fail before accepting topology.

State and persistence behavior: Static resource.

Dependencies and integration points: Used by topology parser version validation tests.

Risks: The fixture also contains a negative rack cost, so tests expecting a specific error must account for parser validation order.

Test signals: Negative signal for layout version parsing and validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/invalid-version.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/middle-leaf.yaml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/middle-leaf.yaml

Purpose: Negative YAML topology fixture where a middle layer is marked as a leaf but still has children.

Important APIs/types/functions: Nested `sublayer` tree with a `rack` node declared `type: LEAF_NODE` while it contains nodegroup and node sublayers.

Control flow: Parser input only; validation should reject a leaf node with children or a leaf in the middle of the hierarchy.

State and persistence behavior: Static YAML resource.

Dependencies and integration points: Used by YAML topology validation tests.

Risks: If parser ignores children under leaf nodes, this fixture could be incorrectly accepted.

Test signals: Negative signal for structural leaf placement validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/middle-leaf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-leaf.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-leaf.xml

Purpose: Negative XML fixture with multiple leaf layers in one path.

Important APIs/types/functions: Both `rack` and `node` layers are declared `Leaf`.

Control flow: Parser input only; validation should reject a hierarchy where an intermediate layer is a leaf.

State and persistence behavior: Static resource.

Dependencies and integration points: Network topology XML validation tests.

Risks: The fixture relies on topology path ordering to expose the intermediate leaf error.

Test signals: Negative signal for exactly one terminal leaf requirement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-leaf.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-root.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-root.xml

Purpose: Negative XML fixture with multiple root layers.

Important APIs/types/functions: Both `datacenter` and `rack` layers are declared `ROOT`.

Control flow: Parser input only; validation should reject more than one root in the topology hierarchy.

State and persistence behavior: Static resource.

Dependencies and integration points: Network topology XML validation tests.

Risks: Type casing and default path syntax must align with parser expectations to isolate the root-count failure.

Test signals: Negative signal for single-root topology invariant.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-root.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-root.yaml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-root.yaml

Purpose: Negative YAML fixture with a root nested under another root.

Important APIs/types/functions: Top-level node has `type: ROOT`; its first child also has `type: ROOT`.

Control flow: Parser input only; validation should reject multiple root nodes.

State and persistence behavior: Static YAML resource.

Dependencies and integration points: YAML topology parser validation tests.

Risks: If validation only checks the top-level node, nested root misuse may be missed.

Test signals: Negative signal for root uniqueness in YAML topology.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-root.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-topology.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-topology.xml

Purpose: Negative XML fixture with duplicate `topology` sections.

Important APIs/types/functions: Contains one `layers` section and two identical `topology` elements.

Control flow: Parser input only; validation should reject ambiguous multiple topology definitions.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology parser validation tests.

Risks: If parser accepts the first or last topology silently, configuration ambiguity would go undetected.

Test signals: Negative signal for exactly one topology block requirement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/multiple-topology.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/no-leaf.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/no-leaf.xml

Purpose: Negative XML fixture with no leaf layer.

Important APIs/types/functions: All path layers are root or inner nodes; terminal `node` is `InnerNode`.

Control flow: Parser input only; validation should require a terminal leaf.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology validation tests.

Risks: If parser infers terminal path elements as leaves regardless of explicit type, this fixture may be accepted incorrectly.

Test signals: Negative signal for required leaf layer.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/no-leaf.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/no-root.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/no-root.xml

Purpose: Negative XML fixture with no root layer.

Important APIs/types/functions: Top path layer `datacenter` is declared `InnerNode` instead of `Root`.

Control flow: Parser input only; validation should reject topology without a root.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology validation tests.

Risks: If parser assumes the first layer is root regardless of type, this fixture can catch that bug.

Test signals: Negative signal for explicit root requirement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/no-root.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/no-topology.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/no-topology.xml

Purpose: Negative XML fixture missing the `topology` section.

Important APIs/types/functions: Defines valid-looking `layers` but no `topology` path/enforcement block.

Control flow: Parser input only; validation should reject incomplete configuration.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology parser validation tests.

Risks: Parser defaults could mask the missing topology if not explicitly checked.

Test signals: Negative signal for required topology block.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/no-topology.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/path-layers-size-mismatch.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/path-layers-size-mismatch.xml

Purpose: Negative XML fixture where topology path depth does not match declared layer ordering.

Important APIs/types/functions: Declares layers `datacenter`, `rack`, `node`, but topology path is `/datacenter/node`, omitting `rack`.

Control flow: Parser input only; validation should reject path/layer mismatch.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology parser path validation tests.

Risks: If parser validates only referenced layer existence, it may miss the omitted middle layer.

Test signals: Negative signal for path-to-layer depth consistency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/path-layers-size-mismatch.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/path-with-id-reference-failure.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/path-with-id-reference-failure.xml

Purpose: Negative XML fixture where topology path references an undeclared layer id.

Important APIs/types/functions: Declares `datacenter`, `rack`, `node`; topology path uses `/datacenter/room/node`.

Control flow: Parser input only; validation should fail resolving `room`.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology parser ID reference validation tests.

Risks: Error reporting should identify the missing path segment rather than a generic path mismatch.

Test signals: Negative signal for path layer ID reference validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/path-with-id-reference-failure.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/unknown-layer-type.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/unknown-layer-type.xml

Purpose: Negative XML fixture with an unsupported layer type.

Important APIs/types/functions: Terminal `node` layer has `<type>leaves</type>` rather than a supported root/inner/leaf value.

Control flow: Parser input only; validation should reject unknown type values.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology parser type validation tests.

Risks: Parser should not normalize arbitrary plural or typo values into leaf.

Test signals: Negative signal for strict layer type parsing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/unknown-layer-type.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/wrong-path-order-1.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/wrong-path-order-1.xml

Purpose: Negative XML fixture with topology path order starting at the wrong layer.

Important APIs/types/functions: Declared layers are root `datacenter`, inner `rack`, leaf `node`, but topology path is `/rack/datacenter/node`.

Control flow: Parser input only; validation should reject layer order inconsistent with declared hierarchy.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology path-order validation tests.

Risks: If parser builds hierarchy solely from the path order, it may miss type-order violations.

Test signals: Negative signal for root-first path ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/wrong-path-order-1.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/wrong-path-order-2.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/wrong-path-order-2.xml

Purpose: Negative XML fixture with leaf and inner layer order swapped.

Important APIs/types/functions: Declared layers are `datacenter` root, `rack` inner, `node` leaf, but topology path is `/datacenter/node/rack`.

Control flow: Parser input only; validation should reject a leaf before an inner layer.

State and persistence behavior: Static resource.

Dependencies and integration points: XML topology path-order validation tests.

Risks: Parser must validate both ID existence and semantic ordering to catch this.

Test signals: Negative signal for terminal leaf ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/networkTopologyTestFiles/wrong-path-order-2.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/ozone-site.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/ozone-site.xml

Purpose: Empty test `ozone-site.xml` configuration placeholder.

Important APIs/types/functions: Hadoop/Ozone XML `configuration` root with no `property` entries.

Control flow: Read by configuration loading paths during tests to provide site-specific overrides, currently none.

State and persistence behavior: Static resource; no properties persisted.

Dependencies and integration points: Integrates with Hadoop `Configuration`/Ozone configuration resource discovery and the standard `configuration.xsl` stylesheet reference.

Risks: Empty file intentionally means tests run with defaults; adding properties here would affect broad test behavior.

Test signals: Baseline signal that resource loading tolerates an empty Ozone site configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/ozone-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/test.db.ini -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/test.db.ini

Purpose: RocksDB options file with fake test-only DB, column-family, and block-table settings.

Important APIs/types/functions: `[DBOptions]`, `[CFOptions "default"]`, `[TableOptions/BlockBasedTable "default"]`, options such as `create_if_missing`, `create_missing_column_families`, compaction, write buffer, compression, table factory, filter policy, and block sizing.

Control flow: Parsed by RocksDB option-loading tests/configuration code; no executable code in the file itself.

State and persistence behavior: Static configuration that influences RocksDB open/create behavior, compaction, WAL, flush, block cache, and table format during tests.

Dependencies and integration points: Consumed by RocksDB Java option loaders and HDDS DB profile/configuration tests.

Risks: Header warns values are fake and not production safe. Invalid or outdated option names can break RocksDB parser compatibility across RocksDB upgrades.

Test signals: Provides broad coverage of RocksDB options file parsing, section handling, list values, comments, and option mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/resources/test.db.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/hadoop-dependency-client/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/hadoop-dependency-client/pom.xml

Purpose: Maven BOM-style module defining the pruned Hadoop client dependency surface for HDDS/Ozone clients.

Important APIs/types/functions: Maven `project`, parent `org.apache.ozone:hdds:2.3.0-SNAPSHOT`, artifact `hdds-hadoop-dependency-client`, packaging `pom`, and `dependencyManagement` entry for `org.apache.hadoop:hadoop-common`.

Control flow: During Maven dependency resolution, this POM manages `hadoop-common` at `${hadoop.version}` while excluding many transitive dependencies such as logging stacks, Jackson databind, Jersey, Guava, Curator, ZooKeeper, Jetty, Netty native epoll, servlet APIs, Avro, and Snappy.

State and persistence behavior: Build metadata only; no runtime state. It affects generated dependency graphs and downstream client classpaths.

Dependencies and integration points: Integrates with the parent HDDS build, Maven dependency management, Hadoop client libraries, and downstream modules importing this dependency POM.

Risks: The exclusion list is large and includes a duplicate Curator wildcard. Excluding broad artifacts can cause runtime `ClassNotFoundException` if downstream code implicitly needs them. Dependency drift in Hadoop can require updating exclusions.

Test signals: Build-level signal rather than unit tests; verifies intended classpath minimization when Maven resolves the module.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/hadoop-dependency-client/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-admin/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-admin/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs exclusion filter for generated admin interface protocol classes.

Important APIs/types/functions: `<FindBugsFilter>` with a single `<Match>` excluding package `org.apache.hadoop.hdds.protocol.proto`.

Control flow: Build tooling reads this filter to suppress static-analysis findings for generated protobuf code.

State and persistence behavior: Static build configuration; no runtime state.

Dependencies and integration points: Integrated with SpotBugs/FindBugs configuration in the Maven module or parent build.

Risks: Broad package exclusion can hide real issues if handwritten code is later placed in the same package. The module POM also sets `spotbugs.skip`, so this filter may be defensive or historical.

Test signals: Static-analysis configuration signal only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-admin/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-admin/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/interface-admin/pom.xml

Purpose: Maven module definition for the HDDS admin interface jar, primarily generated protobuf code.

Important APIs/types/functions: Parent `org.apache.ozone:hdds`, artifact `hdds-interface-admin`, packaging `jar`, properties `maven.test.skip` and `spotbugs.skip`, dependencies `protobuf-java` and `hdds-interface-client`, and build plugins for proto backward compatibility, compiler `proc=none`, and protobuf compilation.

Control flow: Maven builds the module by compiling protobuf sources with `protobuf-maven-plugin`, retaining output directories, skipping tests and SpotBugs because the module has generated code only, and disabling annotation processing in Java compilation.

State and persistence behavior: Build output is generated Java/classes from proto definitions; no runtime state in the POM itself.

Dependencies and integration points: Integrates with common HDDS proto definitions via `hdds-interface-client`, protobuf compiler artifact resolved by `${protobuf.version}` and `${os.detected.classifier}`, and Salesforce proto backwards compatibility plugin.

Risks: Skipping tests and SpotBugs reduces local quality gates. `clearOutputDirectory=false` can preserve stale generated files if proto generation changes unexpectedly. Protobuf plugin depends on OS classifier detection.

Test signals: Build-level signal for generated admin API compatibility and protobuf compilation rather than unit test behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/interface-admin/pom.xml -->
