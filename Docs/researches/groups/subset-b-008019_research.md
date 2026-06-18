# subset-b-008019 Research

Grouped source research for Apache Ozone HDDS framework RocksDB table utilities, table caches, audit logging, common storage/block helpers, gRPC metrics, lease management, upgrade finalization, and checksum serialization contracts. Each section is marker-delimited for deterministic reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStoreCodecBufferIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStoreCodecBufferIterator.java

## Purpose

`RDBStoreCodecBufferIterator` is the `CodecBuffer`-based RocksDB iterator implementation used by `RDBTable` and `TypedTable` when both key and value codecs support direct buffers. It avoids byte-array materialization for iteration-heavy metadata paths and plugs into the shared `RDBStoreAbstractIterator` prefix/seek/remove framework. The complete 100-line source was read for this report.

## Important APIs, Types, and Functions

The package-private class extends `RDBStoreAbstractIterator<CodecBuffer>`. It owns two reusable `Buffer` helpers, one for keys and one for values, plus an `AtomicBoolean closed`. Key methods are `key()`, `getKeyValue()`, `seek0(CodecBuffer)`, `delete(CodecBuffer)`, `startsWithPrefix(CodecBuffer)`, and `close()`.

## Control Flow

Construction wires RocksDB iterator accessors based on `IteratorType`: keys are read when the caller asks for keys or when prefix matching requires them, values are read only for value-capable iterator types. The constructor immediately seeks to the first valid element. `getKeyValue()` returns null keys for value-only iteration and uses the reusable buffers to fetch RocksDB key/value bytes. Seeking delegates to `ManagedRocksIterator.seek(ByteBuffer)`, and removal deletes through the owning `RDBTable`.

## State and Persistence Behavior

The iterator does not persist state itself; it holds native RocksDB iterator state and direct buffers that must be released. `close()` is idempotent, closes the superclass iterator, releases the optional prefix buffer, and releases key/value buffers. A leaked iterator keeps the parent `RocksDatabase` acquire counter open.

## Dependencies and Integration Points

It depends on `CodecBuffer`, `CodecBuffer.Capacity`, `ManagedRocksIterator`, `RDBTable`, `IteratorType`, and Ratis `Preconditions`. It is selected by `TypedTable.newCodecBufferTableIterator` and raw `RDBTable.iterator(CodecBuffer, IteratorType)`.

## Risks and Edge Cases

Closed iterators fail through `assertOpen()`. Prefix matching must read keys even for value-only output. The caller must not retain returned `CodecBuffer` instances beyond the iterator lifecycle unless ownership is clear. Failure to close can block `RocksDatabase.close()` because managed iterators carry the DB acquire reference.

## Test Signals

Useful tests include prefix iteration with all `IteratorType` modes, seek/delete behavior with direct-buffer codecs, close idempotence, use-after-close assertions, and leak-sensitive DB close tests that ensure iterators release native references.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStoreCodecBufferIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBTable.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBTable.java

## Purpose

`RDBTable` is the byte-array table implementation over a single RocksDB column family. It is marked private and is intended to sit under `TypedTable`, which handles object codecs and cache semantics. The complete 331-line source was read for this report.

## Important APIs, Types, and Functions

The class implements `Table<byte[], byte[]>` and wraps a `RocksDatabase`, `RocksDatabase.ColumnFamily`, and `RDBMetrics`. It exposes `put`, `putWithBatch`, `isEmpty`, `isExist`, `get`, `getIfExist`, `delete`, `deleteRange`, `iterator`, `getEstimatedKeyCount`, `deleteBatchWithPrefix`, `dumpToFileWithPrefix`, `loadFromFile`, and `getRangeKVs`. Package-private overloads handle `ByteBuffer` and `CodecBuffer` fast paths.

## Control Flow

Most operations delegate directly to `RocksDatabase` with the table's column family. Existence checks use RocksDB `keyMayExist` first, record metrics, and fall back to `get` only when the result is inconclusive. Iteration creates byte-array or codec-buffer iterators with optional prefix and `IteratorType`. Range listing seeks either to the first key or a validated start key, filters keys, optionally stops at the first mismatch after results have begun when sequential listing is requested, and logs debug timing/filter counters.

## State and Persistence Behavior

Persistent data lives in RocksDB. Batched writes are recorded into `RDBBatchOperation` and persist only when the owning batch is committed. `dumpToFileWithPrefix` writes matching entries to an external SST file through `RDBSstFileWriter`; `loadFromFile` ingests it back into the column family. `deleteRange` and prefix batch deletion modify persistent key ranges.

## Dependencies and Integration Points

It depends on RocksDB wrapper classes (`RocksDatabase`, `RDBBatchOperation`, `RDBStoreByteArrayIterator`, `RDBStoreCodecBufferIterator`, `RDBSstFileWriter`, `RDBSstFileLoader`), `MetadataKeyFilters.KeyPrefixFilter`, `CodecBufferCodec`, and `RDBMetrics`. `TypedTable` is its main consumer.

## Risks and Edge Cases

Batch methods require `RDBBatchOperation` and throw on unexpected implementations. `keyMayExist` may be inconclusive, so tests must cover both definite and fallback paths. `getRangeKVs` rejects negative counts but permits zero-count empty results. Prefix buffers in `dumpToFileWithPrefix` must be closed on iterator creation failure. Start keys that do not exist return an empty range unless the key is compatible with a prefix edge case.

## Test Signals

Tests should cover metrics increments for get/existence paths, batch type validation, range scans with missing start keys, prefix filters, sequential stop behavior, SST dump/load round trips, direct-buffer get/delete paths, and iterator closure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDBCheckpoint.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDBCheckpoint.java

## Purpose

`RocksDBCheckpoint` is a small `DBCheckpoint` value object for a RocksDB checkpoint directory plus snapshot metadata. The complete 81-line source was read for this report.

## Important APIs, Types, and Functions

Constructors accept a checkpoint `Path`, or `Path`, timestamp, latest RocksDB sequence number, and creation duration. Implemented APIs are `getCheckpointLocation`, `getCheckpointTimestamp`, `getLatestSequenceNumber`, `checkpointCreationTimeTaken`, and `cleanupCheckpoint`.

## Control Flow

There is no complex control flow. Construction captures metadata; getters return the stored values; cleanup logs and recursively deletes the checkpoint directory.

## State and Persistence Behavior

The object represents an on-disk RocksDB checkpoint directory. `cleanupCheckpoint()` permanently deletes that directory with Apache Commons `FileUtils.deleteDirectory`. It does not create checkpoints itself; creation is handled by `RocksDatabase.RocksCheckpoint` and higher-level DB store code.

## Dependencies and Integration Points

It implements `DBCheckpoint`, uses `Path`, `FileUtils`, `jakarta.annotation.Nonnull`, and SLF4J. It is returned to consumers that need snapshot location, sequence number, and cleanup responsibility.

## Risks and Edge Cases

Cleanup is destructive and assumes the path is a checkpoint directory. The one-argument constructor leaves latest sequence number at `-1` and creation duration at `0`, so callers must tolerate unknown metadata. IO failures propagate from delete.

## Test Signals

Tests should verify getter values, default metadata values, cleanup of a temporary directory, and propagation when deletion fails or the path is invalid.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDBCheckpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDBConfiguration.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDBConfiguration.java

## Purpose

`RocksDBConfiguration` is an HDDS configuration bean for RocksDB logging, WAL, and write sync settings under `hadoop.hdds.db`. The complete 142-line source was read for this report.

## Important APIs, Types, and Functions

The class is annotated with `@ConfigGroup(prefix = "hadoop.hdds.db")`. Configured fields include RocksDB log enablement, log level, max log file size, number of kept log files, write option sync, WAL TTL, and WAL size limit. It exposes simple getters and setters for each field.

## Control Flow

There is no runtime control flow beyond property access. The HDDS config injection system reads `@Config` metadata and sets values before DB option builders consume the bean.

## State and Persistence Behavior

State is in-memory configuration derived from Ozone configuration files. It influences RocksDB behavior such as synchronous writes, logging, and WAL retention but does not persist anything directly.

## Dependencies and Integration Points

It depends on HDDS config annotations (`Config`, `ConfigGroup`, `ConfigType`) and config tags for OM, SCM, and DATANODE. DB store builders and RocksDB option factories are the expected consumers.

## Risks and Edge Cases

Defaults matter operationally: sync writes default false, RocksDB logging default false, WAL TTL defaults to 1200 seconds, and WAL size limit defaults to zero. Misconfigured sizes can affect disk usage or recovery windows. The log level is a free string and validation likely occurs elsewhere.

## Test Signals

Tests should exercise config binding from `OzoneConfiguration`, default values, setter/getter behavior, and downstream option generation for WAL/log/sync settings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDBConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDatabase.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDatabase.java

## Purpose

`RocksDatabase` is the central managed wrapper around `org.rocksdb.RocksDB`. It opens DBs with column families, wraps native resources in managed classes, tracks concurrent operations, closes on severe RocksDB errors, and exposes lower-level operations used by `RDBTable`, checkpointing, compaction, WAL update streaming, and SST maintenance. The complete 916-line source was read for this report.

## Important APIs, Types, and Functions

Important public/package APIs include `open`, `listColumnFamiliesEmptyOptions`, `getColumnFamily`, `dropColumnFamily`, `put`, `get`, `keyMayExist`, `delete`, `deleteRange`, `batchWrite`, `newIterator`, `flush`, `flushWal`, `compactRange`, `compactDB`, `createCheckpoint`, `getUpdatesSince`, `getLatestSequenceNumber`, `estimateNumKeys`, `getProperty`, `ingestExternalFile`, `deleteFilesNotMatchingPrefix`, `getManagedRocksDb`, and `close`. Nested types are `RocksCheckpoint` and `ColumnFamily`.

## Control Flow

`open` discovers extra existing column families not present in the requested family set, builds descriptors, opens read-only or read-write RocksDB, and wraps returned handles. Every operation first calls `acquire()`, incrementing a shared counter unless close has begun. Iterators receive an acquire token that is released when the managed iterator closes. On `RocksDBException`, `closeOnError` asynchronously closes the DB for corruption and IO errors. `close()` marks the DB closed, cancels background work, closes listeners, waits for the active-operation counter to drain, then closes handles, DB, descriptors, write options, and DB options.

## State and Persistence Behavior

The class owns persistent RocksDB state at the DB path and native resources for DB options, write options, descriptors, column family handles, and the DB instance. Data mutation methods persist to RocksDB or WAL according to configured write options. `RocksCheckpoint.createCheckpoint` materializes a filesystem checkpoint. `dropColumnFamily` removes a column family from RocksDB and local maps. `deleteFilesNotMatchingPrefix` deletes eligible last-level SST files whose key ranges do not match a configured prefix.

## Dependencies and Integration Points

It integrates RocksJava through HDDS managed wrappers (`ManagedRocksDB`, `ManagedReadOptions`, `ManagedWriteBatch`, `ManagedCheckpoint`, and related option classes), `TableConfig`, `RDBTable`, external file ingestion, `RocksDiffUtils`, and Ratis `MemoizedSupplier`/`UncheckedAutoCloseable`. It is the foundation for all RocksDB-backed metadata tables.

## Risks and Edge Cases

The acquire counter is critical: leaked iterators or long operations can delay close indefinitely. Column families discovered from old or future versions are opened as extras, which supports compatibility but can hide schema drift. `deleteFilesNotMatchingPrefix` assumes SST level constraints and prefix range logic are correct before deleting files. `getLastLevel()` assumes there is at least one live file. `finalize()` only warns on leaks and should not be relied on. ByteBuffer logging uses decoded keys and can be expensive or lossy for non-string keys.

## Test Signals

High-value tests include open with declared and extra column families, read-only open, corruption/IO close-on-error behavior, iterator-held close blocking and release, batch writes, ByteBuffer get sizing, keyMayExist enum handling, checkpoint creation, flush/compact paths, drop column family cleanup, and prefix-based SST deletion with synthetic metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDatabase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/SequenceNumberNotFoundException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/SequenceNumberNotFoundException.java

## Purpose

`SequenceNumberNotFoundException` signals that requested RocksDB WAL/update data cannot be found for a sequence number. The complete 35-line source was read for this report.

## Important APIs, Types, and Functions

It extends `IOException` and provides a no-argument constructor and a message constructor.

## Control Flow

There is no internal control flow. Higher-level WAL delta or checkpoint code throws/catches it as an I/O condition.

## State and Persistence Behavior

The class owns no state beyond inherited exception message/cause fields. It reflects WAL retention or sequence availability in persistent RocksDB state.

## Dependencies and Integration Points

It depends only on `java.io.IOException`. It integrates conceptually with `RocksDatabase.getUpdatesSince` and DB checkpoint/delta replication paths.

## Risks and Edge Cases

It has no cause-taking constructor, so callers that need to preserve an underlying cause must wrap differently or use `initCause`.

## Test Signals

Tests are usually indirect through update-since/checkpoint code; direct tests can verify checked-exception typing and message propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/SequenceNumberNotFoundException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/Table.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/Table.java

## Purpose

`Table` defines the evolving metadata key-value table contract used by Ozone DB stores. It abstracts typed keys and values, basic CRUD, iteration, cache hooks, range scans, and SST import/export. The complete 395-line source was read for this report.

## Important APIs, Types, and Functions

Core methods are `put`, `putWithBatch`, `isEmpty`, `isExist`, `get`, `getSkipCache`, `getReadCopy`, `getIfExist`, `delete`, `deleteWithBatch`, `deleteRange`, `iterator`, `keyIterator`, `valueIterator`, `getName`, `getEstimatedKeyCount`, cache methods, `getRangeKVs`, `deleteBatchWithPrefix`, `dumpToFileWithPrefix`, and `loadFromFile`. Nested types are immutable `KeyValue<K,V>` and `KeyValueIterator<KEY,VALUE>`.

## Control Flow

Default iterator helpers wrap the main key-value iterator and project keys or values through `TableIterator.convert`. Many cache-related default methods throw `NotImplementedException`, making cache support explicit in implementations such as `TypedTable`.

## State and Persistence Behavior

The interface does not own state. Implementations persist mutations to a metadata backend, commonly RocksDB. Cache methods describe in-memory state that may contain recently committed or pending entries depending on implementation.

## Dependencies and Integration Points

It uses `BatchOperation`, `CodecException`, `RocksDatabaseException`, `MetadataKeyFilters.KeyPrefixFilter`, `TableCacheMetrics`, and cache key/value wrappers. `RDBTable` and `TypedTable` are direct implementers in this subset.

## Risks and Edge Cases

Default methods that throw can surprise callers when used against minimal implementations. `getReadCopy` intentionally has implementation-specific reference semantics. `getRangeKVs` documentation states snapshot-like listing, but concrete implementations must provide that behavior. `TableIterator.convert.seek` applies the converter to a possibly null seek result, which depends on caller/implementation behavior.

## Test Signals

Contract tests should cover CRUD, batch writes/deletes, range listing semantics, iterator projections, cache hook support/unsupported behavior, and equality/hash behavior for `KeyValue`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/Table.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/TableConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/TableConfig.java

## Purpose

`TableConfig` describes a RocksDB column family/table name and its managed column family options. The complete 123-line source was read for this report.

## Important APIs, Types, and Functions

Important methods are `toName(byte[])`, `newTableConfig(Path,String)`, `getName`, `getDescriptor`, `getColumnFamilyOptions`, `equals`, `hashCode`, `toString`, and `close`.

## Control Flow

`newTableConfig` attempts to read per-column-family options from DB config files, falls back to the HDDS default DB profile if unavailable, then creates a config. `getDescriptor` clones managed options into a new `ColumnFamilyDescriptor`. Equality is based only on table name.

## State and Persistence Behavior

The object owns a `ManagedColumnFamilyOptions` instance that must be closed unless it is marked reused. It does not persist data but can load RocksDB options from files and supply descriptors for persistent column families.

## Dependencies and Integration Points

It depends on `DBConfigFromFile`, `DBStoreBuilder.HDDS_DEFAULT_DB_PROFILE`, `ManagedColumnFamilyOptions`, `ColumnFamilyDescriptor`, and HDDS `StringUtils`. `RocksDatabase.open` consumes sets of `TableConfig`.

## Risks and Edge Cases

The catch in `newTableConfig` ignores `RocksDBException`, so option-file failures silently use defaults. Equality ignores options, so two configs with the same name but different options collapse in sets. Ownership of managed options must be clear to prevent native leaks or double close.

## Test Signals

Tests should verify descriptor names/options, fallback on missing option files, equality by name, and close behavior for reused versus non-reused options.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/TableConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/TableIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/TableIterator.java

## Purpose

`TableIterator` is the closeable iterator contract for metadata table scans, adding RocksDB-style seek/remove operations to Java `Iterator`. The complete 105-line source was read for this report.

## Important APIs, Types, and Functions

The interface extends `Iterator<T>` and `Closeable`, with `close`, `seekToFirst`, `seekToLast`, `seek(KEY)`, and `removeFromDB`. Static `convert` adapts a `Table.KeyValueIterator` into another iterator shape.

## Control Flow

Concrete iterators implement navigation and removal. `convert` delegates all operations to the wrapped iterator and maps `next()`/`seek()` results through a provided function.

## State and Persistence Behavior

The interface owns no state. Implementations may hold native RocksDB iterators and remove persistent entries via `removeFromDB`.

## Dependencies and Integration Points

It depends on `Table.KeyValueIterator`, `RocksDatabaseException`, and `CodecException`. It is used by `Table.keyIterator`, `Table.valueIterator`, `RDBTable`, and `TypedTable`.

## Risks and Edge Cases

`close()` throws `RocksDatabaseException`, so callers should use compatible try-with-resources handling. `removeFromDB` mutates storage and should be used carefully while iterating. `convert.seek` does not guard null before applying the converter.

## Test Signals

Tests should cover adapter delegation, close propagation, seek conversion, remove propagation, and behavior when wrapped seek returns null.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/TableIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/TypedTable.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/TypedTable.java

## Purpose

`TypedTable<KEY,VALUE>` is the public typed metadata table implementation over `RDBTable`. It converts keys and values with `Codec`s, optionally uses direct `CodecBuffer` fast paths, and mediates table cache behavior. The complete 634-line source was read for this report.

## Important APIs, Types, and Functions

It implements all `Table` methods plus cache APIs. Important fields are `rawTable`, `keyCodec`, `valueCodec`, `supportCodecBuffer`, reusable buffer capacity, and `TableCache`. It has nested `TypedTableIterator` and abstract `RawIterator<RAW>`. Important private helpers include encode/decode methods, direct-buffer `getFromTable`, `getFromTableIfExist`, and iterator construction.

## Control Flow

Construction chooses `FullTableCache`, `PartialTableCache`, or `TableNoCache`; full cache is populated by iterating the whole raw table with epoch `-1`. Reads first consult cache: `EXISTS` returns a copied value for `get`/`getIfExist`, `NOT_EXIST` returns null, and `MAY_EXIST` falls through to RocksDB. Direct-buffer reads allocate a resizable output buffer, retry when RocksDB reports a larger required size, and decode from `CodecBuffer`. Writes and deletes use direct buffers when both codecs support them; batch direct buffers are intentionally handed to the batch for release after commit. Iterators wrap raw byte-array or codec-buffer iterators and decode entries lazily.

## State and Persistence Behavior

Persistent state lives in `RDBTable`/RocksDB. In-memory state lives in `TableCache`, where entries can represent values or tombstones with epochs. `cleanupCache` delegates to the cache implementation. `dumpToFileWithPrefix` and `loadFromFile` expose RocksDB SST import/export through typed prefixes.

## Dependencies and Integration Points

It depends on `Codec`, `CodecBuffer`, `RDBTable`, cache classes, `TableCacheMetrics`, `MetadataKeyFilters`, Ratis `Preconditions`, and `CheckedBiFunction`. It is the standard typed API exposed by DB store builders to OM/SCM/HDDS metadata code.

## Risks and Edge Cases

Cache semantics differ by cache type: full cache treats a miss as definitive, partial/no cache require DB lookup. `getReadCopy` returns the cached object reference and requires caller synchronization. Direct-buffer batch paths must release buffers on error but not after successful batch enqueue. Buffer resizing assumes required size remains stable between retries. Full-cache construction can be expensive for large tables.

## Test Signals

Tests should cover all cache types, tombstones, copy versus read-copy semantics, full-cache initial load, codec-buffer and byte-array paths, buffer resizing for large values, batch ownership on success/failure, range decoding, prefix delete/export/import, and iterator close/seek/remove behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/TypedTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheKey.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheKey.java

## Purpose

`CacheKey<KEY>` wraps non-null table keys for use in table caches and sorted maps. The complete 64-line source was read for this report.

## Important APIs, Types, and Functions

It stores a final `KEY`, exposes `getCacheKey`, implements `equals`, `hashCode`, and `Comparable<CacheKey<KEY>>`.

## Control Flow

Construction rejects null keys. Equality/hash use the wrapped key. Ordering returns zero for equal keys and otherwise compares `key.toString()` values.

## State and Persistence Behavior

It is an in-memory cache identity object and has no persistence behavior.

## Dependencies and Integration Points

It depends on `java.util.Objects`. It is used by `FullTableCache`, `PartialTableCache`, `TableNoCache`, and `TypedTable` cache APIs.

## Risks and Edge Cases

The natural ordering is based on `toString`, not the key's own comparator or serialized bytes. Different keys with identical strings compare equal for sorted-map ordering even if `equals` is false, which can be risky in `ConcurrentSkipListMap` full cache usage.

## Test Signals

Tests should cover null rejection, equality/hash behavior, ordering with representative key types, and full-cache behavior when key `toString()` collisions are possible.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheResult.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheResult.java

## Purpose

`CacheResult<VALUE>` is the lookup result object for table cache checks. The complete 75-line source was read for this report.

## Important APIs, Types, and Functions

It stores a `CacheStatus` and optional `CacheValue<VALUE>`, exposes `getCacheStatus` and `getValue`, and implements `equals`/`hashCode`. `CacheStatus` values are `EXISTS`, `NOT_EXIST`, and `MAY_EXIST`.

## Control Flow

There is no complex control flow. Cache implementations construct results to tell callers whether a key is definitely present, definitely absent, or may require a RocksDB lookup.

## State and Persistence Behavior

It is an in-memory value object only.

## Dependencies and Integration Points

It depends on `CacheValue` and `Objects`. `TypedTable` switches on `CacheStatus` to decide whether to return cached values or query RocksDB.

## Risks and Edge Cases

The constructor permits inconsistent combinations such as `EXISTS` with null value; correctness relies on cache implementations. `MAY_EXIST` normally carries null value and is reused as a raw singleton in `TableCache`.

## Test Signals

Tests should cover equality/hash, status-driven `TypedTable` behavior, and cache implementations returning the expected statuses for misses, hits, and tombstones.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheStats.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheStats.java

## Purpose

`CacheStats` is an immutable snapshot of table cache hit, miss, and iteration counters. The complete 45-line source was read for this report.

## Important APIs, Types, and Functions

The constructor accepts `cacheHits`, `cacheMisses`, and `iterationTimes`. Getters return each count.

## Control Flow

There is no control flow beyond construction and getters.

## State and Persistence Behavior

It is an in-memory metrics snapshot. It does not reset counters or persist metrics.

## Dependencies and Integration Points

It is produced by `CacheStatsRecorder` and returned by `TableCache.getStats`, then exposed through `TableCacheMetrics`.

## Risks and Edge Cases

The class performs no validation against negative values. Snapshot freshness depends on the recorder.

## Test Signals

Tests should verify snapshot values through cache get/lookup/iterator operations and metrics source integration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheStats.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheStatsRecorder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheStatsRecorder.java

## Purpose

`CacheStatsRecorder` is a package-private atomic counter helper for table cache metrics. The complete 58-line source was read for this report.

## Important APIs, Types, and Functions

It owns `AtomicLong` counters for hits, misses, and iterations. Methods are `recordHit`, `recordMiss`, `recordValue`, `recordIteration`, and `snapshot`.

## Control Flow

`recordValue` treats a null `CacheValue` as a miss and a non-null value, including a tombstone, as a hit. `snapshot` returns a `CacheStats` object with current counter values.

## State and Persistence Behavior

State is in-memory and thread-safe through atomic counters. It has no persistence.

## Dependencies and Integration Points

It depends on `AtomicLong`, `CacheValue`, and `CacheStats`. Full and partial cache implementations call it on lookups and iterator creation.

## Risks and Edge Cases

Tombstone entries count as hits because the cache did contain information. Counters are monotonically increasing and do not reset.

## Test Signals

Tests should verify null/non-null hit accounting, iteration accounting, snapshot consistency under concurrent calls, and tombstone hit behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheStatsRecorder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheValue.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheValue.java

## Purpose

`CacheValue<VALUE>` stores a cached table value or delete tombstone together with an epoch used for cache cleanup. The complete 57-line source was read for this report.

## Important APIs, Types, and Functions

Static factories are `get(long epoch, V value)` for non-null values and `get(long epoch)` for null tombstones. Getters are `getCacheValue` and `getEpoch`.

## Control Flow

The value factory rejects null; the tombstone factory intentionally creates a null-valued cache entry. Cache cleanup compares epochs to remove flushed entries.

## State and Persistence Behavior

It is in-memory state reflecting table cache entries. Epochs typically correspond to Ratis transaction log indices and are used to decide when cached entries can be evicted after persistence.

## Dependencies and Integration Points

It depends on `Objects` and is used across `Table`, `TypedTable`, and all cache implementations.

## Risks and Edge Cases

Null value is overloaded to mean deletion/tombstone, so code must use the correct factory. The class has no `equals`, so `CacheResult.equals` compares values by object identity unless `CacheValue` instances are the same.

## Test Signals

Tests should cover null rejection, tombstone creation, epoch-based cleanup behavior, and callers correctly interpreting null as deletion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/CacheValue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/FullTableCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/FullTableCache.java

## Purpose

`FullTableCache` is the cache implementation whose in-memory state mirrors the entire table. It supports sorted iteration and definitive negative lookups. The complete 233-line source was read for this report.

## Important APIs, Types, and Functions

It implements `TableCache<KEY,VALUE>`. Important members are a `ConcurrentSkipListMap` cache, epoch-to-key map, scheduled cleanup executor, cleanup queue, read/write lock, and `CacheStatsRecorder`. Methods include `get`, `loadInitial`, `put`, `cleanup`, `evictCache`, `lookup`, `iterator`, `size`, `getEpochEntries`, `getStats`, and `getCacheType`.

## Control Flow

Startup calls `loadInitial` to fill cache without epoch tracking. Runtime `put` stores values or tombstones; only tombstones are added to epoch cleanup tracking. `cleanup` replaces the cleanup queue with requested epochs; a scheduled task wakes every second, drains queued epochs, and calls `evictCache`. `lookup` returns `EXISTS` for non-null entries and `NOT_EXIST` for missing entries or tombstones.

## State and Persistence Behavior

State is in-memory and intended to match persistent RocksDB state plus recent tombstones. Cleanup removes tombstones once epochs have been persisted. It does not write storage itself.

## Dependencies and Integration Points

It depends on Guava `ThreadFactoryBuilder`, concurrent collections, locks, and table cache value/result wrappers. `TypedTable` uses it when `CacheType.FULL_CACHE` is requested and initializes it from RocksDB.

## Risks and Edge Cases

Because misses are definitive, cache initialization and update ordering must be correct. The cache uses `CacheKey.compareTo`, so key string ordering/collisions affect storage. Cleanup queue `clear` means a newer cleanup call replaces pending epochs. `evictCache` assumes the epoch list is non-empty and sorted enough for the last element to be a high-water mark. The scheduled executor is not exposed for shutdown here.

## Test Signals

Tests should cover initial load, definitive miss semantics, tombstone lookup, epoch cleanup ordering, concurrent put/cleanup, sorted iteration, stats, and executor cleanup behavior in lifecycle tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/FullTableCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/PartialTableCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/PartialTableCache.java

## Purpose

`PartialTableCache` stores only recent or pending table entries and tombstones, so misses are not definitive and must fall back to RocksDB. The complete 189-line source was read for this report.

## Important APIs, Types, and Functions

It implements `TableCache<KEY,VALUE>` with a `ConcurrentHashMap` cache, epoch-to-key `ConcurrentSkipListMap`, single-thread cleanup executor, and `CacheStatsRecorder`. Methods mirror `FullTableCache`: `get`, `put`, `cleanup`, `evictCache`, `lookup`, `iterator`, `size`, `getEpochEntries`, `getStats`, and `getCacheType`.

## Control Flow

`loadInitial` is intentionally a no-op. `put` stores entries and tracks all entries by epoch. `cleanup` asynchronously executes `evictCache`, which scans epochs up to the supplied last epoch and removes entries whose current cache epoch still matches. `lookup` returns `MAY_EXIST` on misses, `EXISTS` for values, and `NOT_EXIST` for tombstones.

## State and Persistence Behavior

State is transient and represents mutations not yet cleaned after DB flush. Cleanup removes entries once epochs are safe. Persistent state remains in RocksDB.

## Dependencies and Integration Points

It integrates with `TypedTable` for `CacheType.PARTIAL_CACHE` and relies on higher-level Ozone locks around same-key updates, as described in comments.

## Risks and Edge Cases

`epochEntries` stores mutable `HashSet`s inside a concurrent map; concurrent writes to the same epoch set can race. Cleanup assumes the epoch list is non-empty and that the last element is the cutoff. The executor is not exposed for shutdown. Misses must never be treated as absence by callers.

## Test Signals

Tests should cover MAY_EXIST miss behavior, tombstones, epoch cleanup with overwritten entries, concurrent updates around cleanup, stats, and fallback-to-RocksDB behavior through `TypedTable`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/PartialTableCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/TableCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/TableCache.java

## Purpose

`TableCache` defines the cache contract for RocksDB-backed Ozone metadata tables. The complete 121-line source was read for this report.

## Important APIs, Types, and Functions

Methods are `get`, `loadInitial`, `put`, `cleanup`, `evictCache`, `size`, `iterator`, `lookup`, `getEpochEntries`, `getStats`, and `getCacheType`. It defines `MAY_EXIST` and enum `CacheType` with `FULL_CACHE`, `PARTIAL_CACHE`, and `NO_CACHE`.

## Control Flow

Implementations use `lookup` to distinguish definitive hit, definitive absence, and uncertain absence. `cleanup` removes entries matching persisted epochs depending on implementation and cleanup policy.

## State and Persistence Behavior

The interface owns no state. Implementations hold in-memory cache entries and use epochs to coordinate with persistence to RocksDB/Ratis-applied state.

## Dependencies and Integration Points

It uses `CacheKey`, `CacheValue`, `CacheResult`, `CacheStats`, and Java collection types. `TypedTable` consumes the interface to make cache decisions.

## Risks and Edge Cases

The raw static `MAY_EXIST` singleton requires unchecked casts in implementations. The contract assumes callers understand full versus partial cache semantics. Cleanup behavior depends on externally supplied epoch lists.

## Test Signals

Tests should be implementation contract tests for lookup statuses, cleanup semantics, metrics, and cache type reporting across full, partial, and no-cache implementations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/TableCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/TableNoCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/TableNoCache.java

## Purpose

`TableNoCache` is a singleton no-op cache implementation for tables that should always consult RocksDB on cache misses. The complete 101-line source was read for this report.

## Important APIs, Types, and Functions

It exposes `instance()` and implements all `TableCache` methods as no-ops or empty values. `lookup` returns `MAY_EXIST`; `getStats` returns static `EMPTY_STAT`; `getCacheType` returns `NO_CACHE`.

## Control Flow

All mutation and cleanup methods do nothing. Lookup never says a key is absent or present, forcing `TypedTable` to fall through to the raw table.

## State and Persistence Behavior

There is no cache state. Persistence is entirely delegated to the backing table.

## Dependencies and Integration Points

It is used by `TypedTable` when the cache type is neither full nor partial. It depends on Java empty collections and cache wrapper types.

## Risks and Edge Cases

Unchecked singleton casts are safe only because the implementation holds no typed values. Callers expecting cache iteration or size will always see empty results.

## Test Signals

Tests should verify singleton behavior, all methods being inert, `MAY_EXIST` lookup, empty stats, and `TypedTable` DB fallback under no-cache mode.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/TableNoCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.hdds.utils.db.cache` as utility classes for database caching. The complete 19-line source was read for this report.

## Important APIs, Types, and Functions

No executable APIs are defined. The package groups `TableCache`, full/partial/no-cache implementations, and cache key/value/result/stat helpers.

## Control Flow

There is no control flow.

## State and Persistence Behavior

The descriptor owns no state. Package contents provide in-memory cache state layered over persistent RocksDB tables.

## Dependencies and Integration Points

The package integrates with `TypedTable` and table cache metrics.

## Risks and Edge Cases

Documentation is minimal; behavioral contracts are in individual classes.

## Test Signals

No direct tests are needed beyond package compilation/javadoc checks and tests for contained classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.hdds.utils.db` as database interfaces for Ozone. The complete 21-line source was read for this report.

## Important APIs, Types, and Functions

No code is defined here. The package contains table abstractions, RocksDB wrappers, codecs, batches, checkpoints, and related DB utilities.

## Control Flow

There is no runtime control flow.

## State and Persistence Behavior

The descriptor owns no state. The package's implementation classes manage RocksDB persistent metadata and cache state.

## Dependencies and Integration Points

It is a package-level marker for HDDS DB utilities consumed throughout Ozone Manager, SCM, and datanode code.

## Risks and Edge Cases

Documentation is broad and does not state the package's resource-ownership rules; those must be read from individual classes.

## Test Signals

Compilation/javadoc checks are sufficient directly; behavioral tests belong to contained classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/package-info.java

## Purpose

This package descriptor describes `org.apache.hadoop.hdds.utils` as common routines for x509 identity framework creation and generic server-side utilities. The complete 22-line source was read for this report.

## Important APIs, Types, and Functions

No executable APIs are defined in this file.

## Control Flow

There is no control flow.

## State and Persistence Behavior

The descriptor owns no state or persistence.

## Dependencies and Integration Points

The broader package includes utilities used by HDDS services, including DB support and security/identity helpers.

## Risks and Edge Cases

The descriptor is high-level and may lag the actual package contents as utilities evolve.

## Test Signals

Direct testing is limited to compile/javadoc checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditAction.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditAction.java

## Purpose

`AuditAction` is the marker interface for component-specific audit operation enums. The complete 30-line source was read for this report.

## Important APIs, Types, and Functions

It declares one method: `String getAction()`.

## Control Flow

There is no control flow; enums in OM, SCM, datanode, and S3 gateway implement it to provide audit operation names.

## State and Persistence Behavior

It owns no state. Returned action names become part of audit log records.

## Dependencies and Integration Points

It is consumed by `AuditMessage.Builder.forOperation` and by component audit enums.

## Risks and Edge Cases

Action string stability matters because audit log parsing and debug-command filtering depend on operation names.

## Test Signals

Tests should ensure component action enums return expected stable strings and integrate with `AuditMessage` formatting/debug filters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditEventStatus.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditEventStatus.java

## Purpose

`AuditEventStatus` defines standard audit result strings for success and failure. The complete 36-line source was read for this report.

## Important APIs, Types, and Functions

Enum constants are `SUCCESS("SUCCESS")` and `FAILURE("FAILURE")`; `getStatus()` returns the string.

## Control Flow

There is no dynamic control flow beyond enum construction.

## State and Persistence Behavior

The enum values are emitted into audit logs as the `ret` field.

## Dependencies and Integration Points

It is consumed by `AuditMessage.Builder.withResult` and component audit builders.

## Risks and Edge Cases

Changing strings would break audit log expectations and parsers.

## Test Signals

Tests should verify message formatting includes `ret=SUCCESS` or `ret=FAILURE` and that downstream log parsers expect these exact values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditEventStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditLogger.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditLogger.java

## Purpose

`AuditLogger` wraps log4j2 `ExtendedLogger` for Ozone audit events, applying read/write/auth/performance markers, result-based log levels, and configurable debug-level operation filtering. The complete 242-line source was read for this report.

## Important APIs, Types, and Functions

Important methods are `logWriteSuccess`, `logWriteFailure`, `logAuthFailure`, `logReadSuccess`, `logReadFailure`, `logWrite`, `logPerformance`, `refreshDebugCmdSet`, and testing accessor `getLogger`. Nested `PerformanceStringBuilder` formats performance fields such as metadata latency, operation latency, pre-op latency, size, count, and stream mode.

## Control Flow

Construction selects the log4j2 logger by `AuditLoggerType` and loads debug command configuration. Success logs normally emit at INFO, but `shouldLogAtDebug` lowers configured operations to DEBUG. Failure and auth failure logs emit at ERROR with the throwable. `refreshDebugCmdSet` reads `ozone.audit.log.debug.cmd.list.<loggerType>` from a new or supplied `OzoneConfiguration` and atomically swaps a lowercase operation set.

## State and Persistence Behavior

The class owns an `ExtendedLogger`, logger type, atomic debug command set, and lowercase operation-name cache. Audit output is persisted according to log4j2 appenders configured outside this class. Performance string builders are per-message helpers.

## Dependencies and Integration Points

It depends on Ozone configuration, `AuditLoggerType`, `AuditMarker`, `AuditMessage`, log4j2 markers/levels, SLF4J, and Ratis/Java utilities. Component `Auditor` implementations build messages and call this logger.

## Risks and Edge Cases

Debug filtering lowercases operation strings and caches by original value; null operations would fail. `refreshDebugCmdSet()` without arguments creates a new configuration, which may not include dynamically supplied config in tests/services. Performance fields are formatted by string concatenation and not JSON. Audit parser compatibility makes output format changes high risk.

## Test Signals

Tests should verify marker/level selection, throwable propagation for failures, debug command refresh behavior, performance string formatting, operation-name case handling, and sample log format compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditLoggerType.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditLoggerType.java

## Purpose

`AuditLoggerType` enumerates named audit loggers for Ozone services. The complete 39-line source was read for this report.

## Important APIs, Types, and Functions

Constants are `DNLOGGER`, `OMLOGGER`, `SCMLOGGER`, `S3GLOGGER`, and `OMSYSTEMLOGGER`, each with a log4j2 logger name. `getType()` returns the configured name.

## Control Flow

Enum construction stores the logger name; `AuditLogger` uses it to fetch the corresponding log4j2 logger and debug config key suffix.

## State and Persistence Behavior

The enum has in-memory constant state only. Values select audit log destinations configured in log4j2.

## Dependencies and Integration Points

It integrates with `AuditLogger`, audit log4j2 properties, and Ozone service components.

## Risks and Edge Cases

Renaming values or type strings can break logging configuration and debug command configuration keys.

## Test Signals

Tests should verify each type maps to expected logger name and that `AuditLogger` resolves configured appenders/filters for those names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditLoggerType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditMarker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditMarker.java

## Purpose

`AuditMarker` defines log4j2 markers used to classify audit events. The complete 41-line source was read for this report.

## Important APIs, Types, and Functions

Constants are `WRITE`, `READ`, `AUTH`, and `PERFORMANCE`, each created through `MarkerManager.getMarker`. `getMarker()` returns the log4j2 marker.

## Control Flow

Enum construction creates markers once; `AuditLogger` attaches them to log calls.

## State and Persistence Behavior

Markers are in-memory log metadata that influence log4j2 filtering and routing.

## Dependencies and Integration Points

It depends on log4j2 `Marker` and `MarkerManager`, and integrates with log4j2 audit configuration.

## Risks and Edge Cases

Marker name changes would break marker-based filters and audit routing.

## Test Signals

Tests should verify logger methods use expected markers and log4j2 sample configurations filter each marker type correctly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditMarker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditMessage.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditMessage.java

## Purpose

`AuditMessage` is the log4j2 `Message` implementation for structured Ozone audit records. It formats user, IP, operation, JSON parameters, result, optional performance details, and optional throwable. The complete 149-line source was read for this report.

## Important APIs, Types, and Functions

Important APIs are `getFormattedMessage`, `getThrowable`, `getOp`, and nested `Builder` methods `setUser`, `atIp`, `forOperation`, `withParams`, `getParams`, `withResult`, `withException`, `setPerformance`, and `build`.

## Control Flow

The constructor memoizes message formatting via Ratis `MemoizedSupplier`, so repeated logging calls reuse the same formatted string. `formMessage` builds the audit format. Parameters are serialized with Jackson `ObjectMapper`; if JSON serialization fails, it falls back to `Map.toString()`.

## State and Persistence Behavior

State is immutable after construction except for lazy memoized message computation. Formatted output persists in audit logs through `AuditLogger`.

## Dependencies and Integration Points

It depends on Jackson, log4j2 `Message`, `AuditAction`, `AuditEventStatus`, `AuditLogger.PerformanceStringBuilder`, and Ratis memoization. Component `Auditor` implementations build it.

## Risks and Edge Cases

The builder does not validate required fields, so null user/IP/op/result can appear in logs. JSON serialization order depends on map implementation. Parameter values must avoid sensitive data unless callers filter them. Output format is parser-sensitive.

## Test Signals

Tests should verify full and minimal formatting, JSON fallback, throwable exposure, memoization, performance suffixes, and compatibility with documented audit parser expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/AuditMessage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/Auditor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/Auditor.java

## Purpose

`Auditor` is an interface for service actors that can build audit messages for successful and failed operations. The complete 33-line source was read for this report.

## Important APIs, Types, and Functions

It declares `buildAuditMessageForSuccess(AuditAction, Map<String,String>)` and `buildAuditMessageForFailure(AuditAction, Map<String,String>, Throwable)`.

## Control Flow

There is no implementation flow. Components implement these methods to centralize audit message construction.

## State and Persistence Behavior

The interface owns no state. Implementations provide metadata that is later persisted to audit logs.

## Dependencies and Integration Points

It depends on `AuditAction`, `AuditMessage`, and Java maps. It integrates with `AuditLogger` use in Ozone services.

## Risks and Edge Cases

Implementations must consistently include user, IP, parameters, and result status. Missing or inconsistent fields reduce audit value and parser reliability.

## Test Signals

Tests should cover component implementations for success/failure message fields, throwable propagation, and sensitive parameter filtering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/Auditor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/package-info.java

## Purpose

This package descriptor documents the Ozone audit logging framework, its log4j2 design, parser-sensitive format, marker filtering, and extension rules. The complete 142-line source was read for this report.

## Important APIs, Types, and Functions

It describes `Auditable`, `AuditAction`, `AuditEventStatus`, `AuditLogger`, `AuditLoggerType`, `AuditMarker`, `AuditMessage`, and `Auditor`, plus usage and extension guidance.

## Control Flow

There is no executable flow. The documented flow is: choose an `AuditLogger`, build an `AuditMessage`, log read/write success/failure, and rely on INFO/ERROR defaults plus marker filters.

## State and Persistence Behavior

The descriptor owns no state. It emphasizes that audit log output format is intended for future parser support and is persisted by log4j2 appenders.

## Dependencies and Integration Points

It documents integration with log4j2 properties, marker filters, asynchronous logging, and component action enums in OM/SCM/DN/S3G.

## Risks and Edge Cases

The file explicitly warns that changes can break logging. Key/value formatting constraints for auditable maps are parser-facing and should be treated as compatibility requirements.

## Test Signals

Tests should validate sample log4j2 configurations, marker filters, parser-compatible output, and extension instructions when new logger or marker types are added.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/audit/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/BlockGroup.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/BlockGroup.java

## Purpose

`BlockGroup` represents deleted blocks associated with one object key/group and converts between Java objects and SCM `KeyBlocks` protobufs. The complete 121-line source was read for this report.

## Important APIs, Types, and Functions

Fields are `groupID` and `List<DeletedBlock>`. APIs include `getDeletedBlocks`, `getGroupID`, `getProto`, static `getFromProto`, `newBuilder`, `toString`, and nested `Builder` methods `setKeyName`, `addAllDeletedBlocks`, and `build`.

## Control Flow

`getProto` iterates deleted blocks, adding block IDs and size fields to a `KeyBlocks.Builder`. `getFromProto` iterates protobuf block entries, reading optional size arrays by index and defaulting missing size, replicated size, or size-per-replica to `SIZE_NOT_AVAILABLE`.

## State and Persistence Behavior

The class is an in-memory DTO. Serialized protobufs may be persisted or sent over SCM protocols by callers.

## Dependencies and Integration Points

It depends on `BlockID`, `DeletedBlock`, and `ScmBlockLocationProtocolProtos.KeyBlocks`. It integrates with block deletion workflows between Ozone metadata and SCM.

## Risks and Edge Cases

The builder does not validate null group ID or deleted block list. `getFromProto` assumes block count drives all optional parallel size lists. Missing size data is represented as `-1`.

## Test Signals

Tests should cover proto round trips with full and missing size fields, empty block lists, null builder inputs if allowed by callers, and preservation of block IDs and sizes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/BlockGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/DeleteBlockGroupResult.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/DeleteBlockGroupResult.java

## Purpose

`DeleteBlockGroupResult` captures the result of deleting all blocks for an object key and converts block deletion results to/from SCM protobuf result messages. The complete 95-line source was read for this report.

## Important APIs, Types, and Functions

APIs include constructor, `getObjectKey`, `getBlockResultList`, `getBlockResultProtoList`, static `convertBlockResultProto`, `isSuccess`, and `getFailedBlocks`.

## Control Flow

`getBlockResultProtoList` maps each `DeleteBlockResult` into a `DeleteScmBlockResult` protobuf. `convertBlockResultProto` maps protobufs back to helper results. `isSuccess` returns false on the first non-success result. `getFailedBlocks` streams and collects block IDs whose result is not `Result.success`.

## State and Persistence Behavior

The object is an in-memory result DTO. Protobuf conversion allows RPC or persistence by callers.

## Dependencies and Integration Points

It depends on `BlockID`, SCM block location protobufs, and `DeleteBlockResult`. It integrates with SCM block deletion command/result paths.

## Risks and Edge Cases

Constructor does not defensively copy the result list. Empty lists count as success. Null lists or null result entries would fail at use time.

## Test Signals

Tests should cover all-success, partial-failure, empty-list, proto round trip, and failed block extraction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/DeleteBlockGroupResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/DeletedBlock.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/DeletedBlock.java

## Purpose

`DeletedBlock` is a DTO for a block pending or involved in deletion, carrying block identity and size accounting. The complete 65-line source was read for this report.

## Important APIs, Types, and Functions

Constructor arguments are `BlockID`, `size`, `replicatedSize`, and `sizePerReplica`. Getters expose each field, and `toString` prints container/local ID and sizes.

## Control Flow

There is no complex flow beyond string formatting.

## State and Persistence Behavior

It is an in-memory DTO. Values may be serialized through `BlockGroup.getProto`.

## Dependencies and Integration Points

It depends on `BlockID` and integrates with `BlockGroup` and delete block workflows.

## Risks and Edge Cases

There is no validation for null block ID or negative size sentinel values. `toString` dereferences nested block ID fields and will fail if block ID is null.

## Test Signals

Tests should verify getters, string formatting, sentinel sizes, and `BlockGroup` serialization of size fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/DeletedBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/Storage.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/Storage.java

## Purpose

`Storage` is an abstract base for Ozone component storage directory state. It validates root/current/VERSION layout, creates or reads `StorageInfo`, and persists layout/cluster/node metadata. The complete 301-line source was read for this report.

## Important APIs, Types, and Functions

Constants include `STORAGE_DIR_CURRENT`, `STORAGE_FILE_VERSION`, and `CONTAINER_DIR`. Enum `StorageState` has `NON_EXISTENT`, `NOT_INITIALIZED`, and `INITIALIZED`. Key methods are constructors, getters for storage dir/state/node/cluster/creation/layout, setters for cluster/layout/first-upgrade-action layout, `getCurrentDir`, `getVersionFile`, `initialize`, `forceInitialize`, `persistCurrentState`, abstract `getNodeProperties`, and static `getInitLayoutVersion`.

## Control Flow

Construction computes storage state. If initialized, it reads `StorageInfo` from the VERSION file; otherwise it creates a new `StorageInfo` with cluster ID/default layout and component-specific node properties. `getStorageState` checks root existence, directory status, writability, VERSION presence, and emptiness of `current/` before allowing initialization. `initialize` creates `current/` and writes VERSION. `forceInitialize` rewrites VERSION if already initialized.

## State and Persistence Behavior

Persistent state is the `current/VERSION` properties file, written last as the validity marker for a storage directory. `StorageInfo` holds cluster ID, node type, creation time, layout version, and component properties. `persistCurrentState` rewrites the current metadata state.

## Dependencies and Integration Points

It depends on `StorageInfo`, `InconsistentStorageStateException`, `OzoneConfiguration`, `NodeType`, Hadoop `Time`, and Ozone config constants. OM, SCM, and datanode storage implementations extend it with node-specific properties.

## Risks and Edge Cases

`initialize` fails if `mkdirs` returns false, including if the directory was concurrently created. Root writability checks can be platform-dependent. Non-empty `current/` without VERSION is treated as inconsistent. `setClusterId` is forbidden after initialization. VERSION write failures can leave partially initialized directories.

## Test Signals

Tests should cover non-existent, non-directory, unwritable, initialized, empty current, and non-empty current states; initialize/forceInitialize/persist behavior; layout version setters; cluster ID restrictions; and config default layout selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/Storage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/StorageInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/StorageInfo.java

## Purpose

`StorageInfo` owns the common properties stored in an Ozone storage VERSION file and validates them when read. The complete 211-line source was read for this report.

## Important APIs, Types, and Functions

Properties include `nodeType`, `clusterID`, `cTime`, `layoutVersion`, and `firstUpgradeActionLayoutVersion`. APIs include constructors from values or file, getters/setters/unsetters, `writeTo`, and static `newClusterID`.

## Control Flow

The value constructor populates required properties. The file constructor reads properties and verifies node type, cluster ID, creation time, and layout version. Missing layout version is defaulted to `0` with a warning. `newClusterID` prefixes a UUID with `OzoneConsts.CLUSTER_ID_PREFIX`.

## State and Persistence Behavior

State is held in a `Properties` object and persisted via `IOUtils.writePropertiesToFile`. Reads use `IOUtils.readPropertiesFromFile`. The layout version and first-upgrade-action layout version coordinate upgrade finalization state.

## Dependencies and Integration Points

It depends on `NodeType`, `IOUtils`, `OzoneConsts`, and `InconsistentStorageStateException`. `Storage` uses it for VERSION handling; upgrade finalizers update layout version through `Storage`.

## Risks and Edge Cases

`getLayoutVersion` returns `0` if absent, but verification mutates missing layout into `0`. Parsing invalid numeric fields throws. `Properties` is mutable and exposed indirectly through generic property methods. File writes must be atomic enough for storage semantics, which is delegated to `IOUtils`.

## Test Signals

Tests should cover reading valid/invalid VERSION files, node type mismatch, missing/empty cluster ID, missing layout version defaulting, first-upgrade-action property, cluster ID format, and write/read round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/StorageInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/package-info.java

## Purpose

This package descriptor identifies `org.apache.hadoop.ozone.common` as common Ozone classes. The complete 19-line source was read for this report.

## Important APIs, Types, and Functions

No executable APIs are defined. The package includes storage metadata and block deletion DTOs in this subset.

## Control Flow

There is no control flow.

## State and Persistence Behavior

The descriptor owns no state. Package classes include persistent VERSION file helpers and in-memory DTOs.

## Dependencies and Integration Points

The package is shared by Ozone services and protocol helpers.

## Risks and Edge Cases

Documentation is minimal and may not communicate compatibility constraints of contained classes.

## Test Signals

Direct checks are compile/javadoc only; behavioral coverage belongs to contained classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetrics.java

## Purpose

`GrpcMetrics` is a Hadoop metrics2 source for Ozone gRPC byte counters, message classification counters, queue/processing latency rates and quantiles, active client connections, and latest request type. The complete 224-line source was read for this report.

## Important APIs, Types, and Functions

Important APIs include static `create`, `unRegister`, `getMetrics`, byte/message increment methods, `addGrpcQueueTime`, `addGrpcProcessingTime`, connection count increment/decrement, getters for counters/rates, and request type setter/getter.

## Control Flow

Construction creates a `MetricsRegistry`, reads percentile interval configuration, and creates queue/processing `MutableQuantiles` arrays if enabled. `create` registers the source in the default metrics system. `getMetrics` snapshots the registry and adds a second record tagged with latest request type. Latency methods update the mutable rate and optional quantiles.

## State and Persistence Behavior

State is in-memory metrics counters/rates/quantiles. Persistence/export is handled by Hadoop metrics sinks. `unRegister` unregisters the source and stops quantile helpers.

## Dependencies and Integration Points

It depends on Hadoop metrics2, Ozone config keys/constants, `MetricUtil`, and is updated by the gRPC server interceptors and transport filter in this package.

## Risks and Edge Cases

Queue/processing time methods accept `int` values, while interceptors pass nanosecond differences cast to int even though metric names say milliseconds. `requestType` is a single mutable string shared across concurrent calls. Registration uses a fixed source name, so multiple instances may conflict.

## Test Signals

Tests should verify metrics registration/unregistration, byte counters, unknown message counters, quantile creation by config, active connection counts, request type tagging, and latency unit expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetricsServerRequestInterceptor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetricsServerRequestInterceptor.java

## Purpose

`GrpcMetricsServerRequestInterceptor` records received gRPC request sizes, request type, queue time, and processing time. The complete 98-line source was read for this report.

## Important APIs, Types, and Functions

The class implements `ServerInterceptor` with `interceptCall`. It wraps the listener in `SimpleForwardingServerCallListener` and overrides `onMessage` and `onComplete`.

## Control Flow

`interceptCall` stores `receivedTime` and starts the downstream call. `onMessage` records `startTime`, measures serialized size for protobuf `AbstractMessage`, increments unknown-message counter otherwise, increments received bytes, parses the first line of `message.toString()` as `cmdType`, updates metrics request type, then delegates. `onComplete` delegates, stores `endTime`, computes queue and processing deltas, and records them.

## State and Persistence Behavior

The interceptor stores timing fields as instance variables, not per-call local state. Metrics are in-memory in `GrpcMetrics` and exported by Hadoop metrics sinks.

## Dependencies and Integration Points

It depends on gRPC server interceptor APIs, protobuf `AbstractMessage`, and `GrpcMetrics`. It is installed on Ozone gRPC servers.

## Risks and Edge Cases

Instance fields make concurrent calls race if one interceptor instance handles multiple calls. Parsing request type from `toString()` assumes a non-empty first line with a colon. Nanosecond differences are cast to `int` and recorded as metric values named milliseconds. Unknown non-protobuf messages still call `toString()` and parsing can fail.

## Test Signals

Tests should cover protobuf and non-protobuf requests, malformed `toString`, concurrent calls, queue/processing time units, and request type extraction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetricsServerRequestInterceptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetricsServerResponseInterceptor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetricsServerResponseInterceptor.java

## Purpose

`GrpcMetricsServerResponseInterceptor` records serialized byte counts for gRPC responses and unknown response message counts. The complete 64-line source was read for this report.

## Important APIs, Types, and Functions

The class implements `ServerInterceptor` and overrides `interceptCall`, wrapping the `ServerCall` with `ForwardingServerCall.SimpleForwardingServerCall` and overriding `sendMessage`.

## Control Flow

For each outbound response, `sendMessage` calculates serialized size if the message is a protobuf `AbstractMessage`, otherwise increments unknown sent message count. It increments sent bytes and then delegates to the real server call.

## State and Persistence Behavior

No local persistent state is stored. Metrics are accumulated in `GrpcMetrics`.

## Dependencies and Integration Points

It depends on gRPC server call/interceptor APIs, protobuf `AbstractMessage`, and `GrpcMetrics`.

## Risks and Edge Cases

Non-protobuf messages count as unknown and contribute zero bytes. The raw `ForwardingServerCall` instantiation omits generic diamond syntax but functions. Exceptions from `getSerializedSize` or downstream send are not handled locally.

## Test Signals

Tests should cover protobuf response byte counts, unknown response counters, multiple response messages, and delegation ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetricsServerResponseInterceptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetricsServerTransportFilter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetricsServerTransportFilter.java

## Purpose

`GrpcMetricsServerTransportFilter` tracks active gRPC client connections. The complete 47-line source was read for this report.

## Important APIs, Types, and Functions

It extends `ServerTransportFilter` and overrides `transportReady` and `transportTerminated`.

## Control Flow

When a transport becomes ready, it increments active client connections and delegates to the superclass. When a transport terminates, it decrements the counter and delegates.

## State and Persistence Behavior

It holds a `GrpcMetrics` reference. Metrics are in-memory and exported by Hadoop metrics sinks.

## Dependencies and Integration Points

It depends on gRPC `Attributes` and `ServerTransportFilter`, and is installed on Ozone gRPC servers alongside interceptors.

## Risks and Edge Cases

Counter correctness depends on one termination event per ready event. The `GrpcMetrics` field is mutable and not final. Negative counts are possible if termination is observed without a matching ready or if duplicate termination occurs.

## Test Signals

Tests should cover ready/terminated increments, duplicate events, and integration with server lifecycle.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/GrpcMetricsServerTransportFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/package-info.java

## Purpose

This package descriptor identifies classes related to gathering gRPC metrics. The complete 22-line source was read for this report.

## Important APIs, Types, and Functions

No executable APIs are defined. The package contains `GrpcMetrics`, server request/response interceptors, and a transport filter.

## Control Flow

There is no control flow.

## State and Persistence Behavior

The descriptor owns no state. Package classes maintain in-memory metrics exported through Hadoop metrics2.

## Dependencies and Integration Points

The package integrates with gRPC server setup and Hadoop metrics.

## Risks and Edge Cases

Documentation is minimal and does not state concurrency/unit caveats present in the interceptors.

## Test Signals

Direct testing is compile/javadoc only; behavior belongs to contained metrics classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/grpc/metrics/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/Lease.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/Lease.java

## Purpose

`Lease<T>` represents a timed lease over a resource with optional expiration callback. The complete 189-line source was read for this report.

## Important APIs, Types, and Functions

Important methods are constructors, `hasExpired`, `getElapsedTime`, `getRemainingTime`, `getLeaseLifeTime`, `renew`, `equals`, `hashCode`, `toString`, package-private `getCallback`, `invalidate`, and static `messageForResource`.

## Control Flow

Construction stores resource, creation time from `Time.monotonicNow`, atomic timeout, optional callback, and non-expired state. Accessors throw `LeaseExpiredException` after invalidation. `renew` adds to the timeout atomically. Equality and hash code are based solely on resource.

## State and Persistence Behavior

State is in-memory only: resource, creation time, timeout, expired flag, and callback. There is no persistence.

## Dependencies and Integration Points

It depends on Hadoop `Time`, `Callable`, `AtomicLong`, and lease exception classes. `LeaseManager` creates, renews, invalidates, and monitors leases.

## Risks and Edge Cases

The `expired` flag is not volatile, though manager operations are partly synchronized and monitor reads may be concurrent. `renew` adds a delta rather than replacing expiration. Callback is nulled on invalidation. Resource equality must be stable.

## Test Signals

Tests should cover remaining/elapsed time, renew semantics, expired exceptions after invalidation, equality by resource, and callback clearing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/Lease.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseAlreadyExistException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseAlreadyExistException.java

## Purpose

`LeaseAlreadyExistException` reports an attempt to acquire a lease for a resource that already has one. The complete 46-line source was read for this report.

## Important APIs, Types, and Functions

It extends `LeaseException` with no-argument and message constructors.

## Control Flow

There is no internal control flow. `LeaseManager.acquire` throws it when `activeLeases` already contains the resource.

## State and Persistence Behavior

It has no state beyond exception message.

## Dependencies and Integration Points

It depends on `LeaseException` and is part of `LeaseManager` acquire API.

## Risks and Edge Cases

No cause constructor is provided.

## Test Signals

Tests should verify duplicate acquisition throws this checked exception with the resource message.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseAlreadyExistException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseCallbackExecutor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseCallbackExecutor.java

## Purpose

`LeaseCallbackExecutor` runs a lease expiration callback and logs failures without propagating them. The complete 63-line source was read for this report.

## Important APIs, Types, and Functions

It implements `Runnable`, stores `resource` and `Callable<Void> callback`, and defines `run`.

## Control Flow

`run` logs debug information, checks callback for null, calls it, and catches any exception to log a warning.

## State and Persistence Behavior

It is a short-lived in-memory runnable. Callback side effects are external.

## Dependencies and Integration Points

It depends on `Callable` and SLF4J. `LeaseManager.LeaseMonitor` submits it to an executor when a lease times out.

## Risks and Edge Cases

Callback failures are swallowed after logging, so callers cannot observe them directly. Long-running callbacks can consume cached-thread-pool resources.

## Test Signals

Tests should verify callback invocation, null callback no-op, exception logging/no propagation, and resource included in logs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseCallbackExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseException.java

## Purpose

`LeaseException` is the checked base exception for lease-specific failures. The complete 45-line source was read for this report.

## Important APIs, Types, and Functions

It extends `Exception` and provides no-argument and message constructors.

## Control Flow

There is no internal control flow.

## State and Persistence Behavior

It owns no state beyond inherited exception fields.

## Dependencies and Integration Points

It is the base for `LeaseAlreadyExistException`, `LeaseExpiredException`, and `LeaseNotFoundException`.

## Risks and Edge Cases

No cause constructor is provided.

## Test Signals

Direct tests can verify checked-exception hierarchy and messages; most coverage is through `LeaseManager`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseExpiredException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseExpiredException.java

## Purpose

`LeaseExpiredException` reports operations on an already expired/invalidated lease. The complete 45-line source was read for this report.

## Important APIs, Types, and Functions

It extends `LeaseException` with no-argument and message constructors.

## Control Flow

There is no internal flow. `Lease` throws it from time/lifetime/renew methods after invalidation.

## State and Persistence Behavior

It owns no state beyond inherited exception fields.

## Dependencies and Integration Points

It is used by `Lease` and caught by `LeaseManager.LeaseMonitor`.

## Risks and Edge Cases

No cause constructor is provided. Timeout detection itself is handled by `LeaseManager`; `Lease` only knows it was invalidated.

## Test Signals

Tests should verify invalidated leases throw this exception from elapsed/remaining/lifetime/renew methods.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseExpiredException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseManager.java

## Purpose

`LeaseManager<T>` manages timed leases for resources, preventing duplicate leases, monitoring expiration, releasing leases, and executing expiration callbacks. The complete 300-line source was read for this report.

## Important APIs, Types, and Functions

Public APIs are constructor, `start`, overloaded `acquire`, `get`, `release`, and `shutdown`. It owns `activeLeases`, a `Semaphore`, monitor thread, `LeaseMonitor`, default timeout, and running flag. Nested `LeaseMonitor` implements the expiration loop.

## Control Flow

`start` initializes the concurrent map, monitor, daemon thread, uncaught-exception handler, and running flag. `acquire` checks running state, rejects duplicate resources, creates a lease, stores it, and releases the semaphore to wake the monitor. `release` removes and invalidates a lease. `shutdown` disables monitor, wakes/interrupts it, releases all active leases without callbacks, and marks not running. The monitor scans active leases, releases expired leases, submits callbacks, and sleeps until the nearest remaining expiration or until the semaphore wakes it for a new lease.

## State and Persistence Behavior

All state is in-memory. There is no persistence; leases are lost on process restart. Callback side effects are external.

## Dependencies and Integration Points

It depends on lease classes, `ConcurrentHashMap`, `Semaphore`, `ExecutorService`, and SLF4J. Services use it for generic resource lease management.

## Risks and Edge Cases

The uncaught-exception handler calls `leaseMonitorThread.start()` on the same thread object, which cannot be restarted after termination. `isRunning` is not volatile and is set after thread start. `shutdown` calls `checkStatus`, so repeated shutdown throws `LeaseManagerNotRunningException`. The monitor uses `Long.MAX_VALUE` timeout in `tryAcquire`, which can be problematic. Callback executor is not explicitly shut down. Lease expiration state relies on `release` invalidation.

## Test Signals

Tests should cover acquire/get/release lifecycle, duplicate acquire, not-running behavior, expiration and callback execution, renew delaying expiration, shutdown releasing without callbacks, repeated shutdown behavior, monitor wakeup on new leases, and uncaught exception handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseManagerNotRunningException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseManagerNotRunningException.java

## Purpose

`LeaseManagerNotRunningException` reports lease manager API calls made before start or after shutdown. The complete 45-line source was read for this report.

## Important APIs, Types, and Functions

It extends `RuntimeException` and provides no-argument and message constructors.

## Control Flow

There is no internal control flow. `LeaseManager.checkStatus` throws it when `isRunning` is false.

## State and Persistence Behavior

It owns no state beyond inherited exception fields.

## Dependencies and Integration Points

It is used by `LeaseManager` public APIs except `start`.

## Risks and Edge Cases

It is unchecked, unlike most other lease exceptions. No cause constructor is provided.

## Test Signals

Tests should verify manager methods throw it before `start` and after `shutdown`, including repeated shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseManagerNotRunningException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseNotFoundException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseNotFoundException.java

## Purpose

`LeaseNotFoundException` reports lookup or release of a resource without an active lease. The complete 46-line source was read for this report.

## Important APIs, Types, and Functions

It extends `LeaseException` and provides no-argument and message constructors.

## Control Flow

There is no internal flow. `LeaseManager.get` and `release` throw it when no lease is found.

## State and Persistence Behavior

It owns no state beyond inherited exception fields.

## Dependencies and Integration Points

It is part of the `LeaseManager` get/release API and is caught by the monitor during concurrent expiration/release races.

## Risks and Edge Cases

No cause constructor is provided.

## Test Signals

Tests should verify missing get/release paths and concurrent release/monitor races do not break the monitor.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseNotFoundException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/package-info.java

## Purpose

This package descriptor describes a generic lease management API for services needing lease management. The complete 22-line source was read for this report.

## Important APIs, Types, and Functions

No executable APIs are defined. The package contains `Lease`, `LeaseManager`, callback executor, and lease exception types.

## Control Flow

There is no control flow in this descriptor.

## State and Persistence Behavior

The descriptor owns no state. Package classes manage in-memory lease lifecycle state.

## Dependencies and Integration Points

The package is generic and can be used by Ozone services to guard temporary resource ownership.

## Risks and Edge Cases

Documentation does not describe threading or shutdown behavior; callers must inspect `LeaseManager`.

## Test Signals

Direct testing is compile/javadoc only; lifecycle tests belong to lease classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/AbstractLayoutVersionManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/AbstractLayoutVersionManager.java

## Purpose

`AbstractLayoutVersionManager` is the generic base implementation for Ozone layout version managers. It tracks metadata layout version, software layout version, feature maps, upgrade state, and JMX exposure. The complete 228-line source was read for this report.

## Important APIs, Types, and Functions

Important methods are `init`, `getUpgradeState`, `setUpgradeState`, `finalized`, `getMetadataLayoutVersion`, `getSoftwareLayoutVersion`, `needsFinalization`, `isAllowed`, `getFeature`, `unfinalizedFeatures`, and `close`. It implements `LayoutVersionManager` and `LayoutVersionManagerMXBean`.

## Control Flow

`init` sets metadata version, initializes feature maps, sets software version to the highest feature layout version, rejects metadata newer than software, chooses initial upgrade state, logs the versions, and registers an MBean. `finalized` advances metadata layout version only if the finalized feature is exactly next; older features are tolerated as replay, newer-than-next features throw. Read/write locks protect version and state reads/writes.

## State and Persistence Behavior

State is in-memory and volatile/locked: metadata/software layout versions, feature maps, and upgrade state. Persistent layout version is updated elsewhere, usually through `BasicUpgradeFinalizer` and `Storage`.

## Dependencies and Integration Points

It depends on `LayoutFeature`, `UpgradeFinalization.Status`, Hadoop metrics `MBeans`, Guava `Preconditions`, and Java locks/maps. Component-specific version managers extend it with their layout feature enums.

## Risks and Edge Cases

`features.lastKey()` requires at least one feature. Feature names and layout versions must be unique. MBean registration lifecycle depends on callers invoking `close`. `featureMap` reads are not always under the lock, though maps are initialized during `init`.

## Test Signals

Tests should cover init states, metadata-newer-than-software rejection, duplicate feature rejection, finalization ordering/replay behavior, `isAllowed`, unfinalized feature snapshots, state transitions, and MBean registration/unregistration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/AbstractLayoutVersionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/BasicUpgradeFinalizer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/BasicUpgradeFinalizer.java

## Purpose

`BasicUpgradeFinalizer` is the base class for service-specific upgrade finalizers. It coordinates one finalization run, client ownership of status messages, layout feature finalization actions, VERSION file updates, and status transitions. The complete 343-line source was read for this report.

## Important APIs, Types, and Functions

Important methods are `finalize`, `reportStatus`, `getStatus`, `preFinalizeUpgrade`, `postFinalizeUpgrade`, `finalizeAndWaitForCompletion`, `isFinalizationDone`, `markFinalizationDone`, `getVersionManager`, abstract `finalizeLayoutFeature`, protected `finalizeLayoutFeature(LayoutFeature, Optional<UpgradeAction>, Storage)`, `runFinalizationAction`, `updateLayoutVersionInVersionFile`, and message/log helpers.

## Control Flow

`finalize` first returns finalized status if already done, then uses a `ReentrantLock` to ensure only one finalization thread runs. `initFinalize` validates current upgrade state and client ID ownership, transitions required finalization to `STARTING_FINALIZATION`, and records the initiating client/component. If required or interrupted in-progress, the executor runs finalization. `reportStatus` optionally transfers client ownership, verifies client ID, drains queued messages, and returns current state. `finalizeAndWaitForCompletion` starts finalization and polls status until timeout.

## State and Persistence Behavior

State includes version manager reference, initiating client ID, component context, executor, finalization lock, message queue, and testing done flag. Persistent state changes happen when `updateLayoutVersionInVersionFile` sets a `Storage` layout version and calls `persistCurrentState`; on write failure it rolls back the in-memory layout version before throwing.

## Dependencies and Integration Points

It depends on `AbstractLayoutVersionManager`, `DefaultUpgradeFinalizationExecutor`, `UpgradeFinalization`, `UpgradeException`, `LayoutFeature.UpgradeAction`, `Storage`, Ratis `NotLeaderException`, and Hadoop `Time`. Component finalizers subclass it to define per-feature finalization.

## Risks and Edge Cases

The executor is invoked while holding the finalization lock in this implementation, so long finalization blocks concurrent `finalize` calls but not synchronized status polling. `clientID` and message handling are synchronization-sensitive. Inconsistent version manager state results in invalid-request exceptions. Persistent VERSION update failure must roll back correctly. `isDone` is not volatile and is testing-focused.

## Test Signals

Tests should cover already-finalized, required, in-progress, and inconsistent states; one-run locking; client takeover/status message draining; wait timeout; feature action success/failure; VERSION update rollback; NotLeader handling; and injected executor failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/BasicUpgradeFinalizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/DefaultUpgradeFinalizationExecutor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/DefaultUpgradeFinalizationExecutor.java

## Purpose

`DefaultUpgradeFinalizationExecutor` drives the normal finalization sequence for a `BasicUpgradeFinalizer`. The complete 73-line source was read for this report.

## Important APIs, Types, and Functions

It implements `UpgradeFinalizationExecutor<T>` with `execute`. Protected `finalizeFeatures` iterates layout features and delegates to the finalizer.

## Control Flow

`execute` emits start, calls `preFinalizeUpgrade`, finalizes each unfinalized feature from the version manager, calls `postFinalizeUpgrade`, and emits finish. If any exception occurs and finalization is still needed, it resets upgrade state to `FINALIZATION_REQUIRED` and rethrows. The `finally` block marks finalization done for tests.

## State and Persistence Behavior

The executor holds no mutable state. Persistent layout/version changes are performed by the finalizer while finalizing features.

## Dependencies and Integration Points

It depends on `BasicUpgradeFinalizer`, `LayoutFeature`, `UpgradeException`, and `UpgradeFinalization.Status`. It is the default executor used by `BasicUpgradeFinalizer`.

## Risks and Edge Cases

If an exception occurs after `needsFinalization()` becomes false, it is swallowed after logging and done marking. `markFinalizationDone` is testing-oriented and can be true after failed attempts. Feature iteration order comes from the version manager.

## Test Signals

Tests should cover successful sequence ordering, exception reset behavior, no-reset behavior when finalization no longer needed, and overridden `finalizeFeatures` for injection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/DefaultUpgradeFinalizationExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/LayoutVersionManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/LayoutVersionManager.java

## Purpose

`LayoutVersionManager` is the read-only interface for a component's metadata/software layout version and feature availability. The complete 83-line source was read for this report.

## Important APIs, Types, and Functions

Methods are `getMetadataLayoutVersion`, `getSoftwareLayoutVersion`, `needsFinalization`, `isAllowed(LayoutFeature)`, `isAllowed(String)`, `getFeature(String)`, `getFeature(int)`, `unfinalizedFeatures`, default `getHandler`, and `close`.

## Control Flow

The interface has no implementation flow except default `getHandler`, which returns null.

## State and Persistence Behavior

Implementations maintain in-memory layout state and coordinate with persistent VERSION metadata externally.

## Dependencies and Integration Points

It depends on `LayoutFeature` and is implemented by `AbstractLayoutVersionManager`. Services query it to guard feature use before finalization.

## Risks and Edge Cases

Callers must handle null from `getFeature` or default `getHandler`. `isAllowed` is the primary compatibility gate and must be used consistently.

## Test Signals

Tests should exercise component implementations for feature gating, unfinalized feature ordering, handler overrides, and close lifecycle.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/LayoutVersionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/LayoutVersionManagerMXBean.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/LayoutVersionManagerMXBean.java

## Purpose

`LayoutVersionManagerMXBean` exposes layout version manager values over JMX. The complete 27-line source was read for this report.

## Important APIs, Types, and Functions

It declares `getMetadataLayoutVersion` and `getSoftwareLayoutVersion`.

## Control Flow

There is no implementation flow. `AbstractLayoutVersionManager` implements it and registers an MBean.

## State and Persistence Behavior

The interface owns no state. Implementations expose in-memory layout version values derived from persistent metadata and software feature definitions.

## Dependencies and Integration Points

It integrates with Hadoop `MBeans` registration in `AbstractLayoutVersionManager`.

## Risks and Edge Cases

JMX consumers rely on stable method names. Exposing only versions omits upgrade state, so monitoring must combine with other signals if needed.

## Test Signals

Tests should verify MBean registration exposes both attributes and unregisters on close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/LayoutVersionManagerMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeActionHdds.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeActionHdds.java

## Purpose

`UpgradeActionHdds` is a runtime annotation for classes that implement HDDS upgrade finalization actions for SCM or datanode components. The complete 46-line source was read for this report.

## Important APIs, Types, and Functions

Annotation members are `HDDSLayoutFeature feature()` and `Component component()`. Nested enum `Component` has `SCM` and `DATANODE`.

## Control Flow

There is no executable flow. Runtime reflection can discover annotated action classes and match them to layout features/components.

## State and Persistence Behavior

The annotation stores metadata in class files at runtime retention. It does not persist service state.

## Dependencies and Integration Points

It depends on `HDDSLayoutFeature` and Java annotation metadata. Upgrade action discovery/registration code consumes it.

## Risks and Edge Cases

Wrong feature or component annotation can run an action in the wrong service or skip it. Runtime retention makes reflection scanning necessary and testable.

## Test Signals

Tests should verify annotated action discovery, feature/component matching, and rejection or absence handling for misannotated classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeActionHdds.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeFinalizationExecutor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeFinalizationExecutor.java

## Purpose

`UpgradeFinalizationExecutor<T>` abstracts the execution strategy for running a `BasicUpgradeFinalizer`. The complete 32-line source was read for this report.

## Important APIs, Types, and Functions

It declares `void execute(T component, BasicUpgradeFinalizer<T, ?> finalizer) throws IOException`.

## Control Flow

There is no implementation flow. Implementations may run finalization synchronously, asynchronously, or with injected test behavior.

## State and Persistence Behavior

The interface owns no state. Implementations drive finalizers that update persistent layout version metadata.

## Dependencies and Integration Points

It depends on `BasicUpgradeFinalizer` and `IOException`. The default implementation is `DefaultUpgradeFinalizationExecutor`.

## Risks and Edge Cases

Custom executors must preserve finalizer state transitions and error semantics or upgrade state can become inconsistent.

## Test Signals

Tests should inject custom executors into `BasicUpgradeFinalizer` to verify ordering, failure, and asynchronous behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeFinalizationExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeFinalizer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeFinalizer.java

## Purpose

`UpgradeFinalizer<T>` defines the service-facing API for finalizing metadata upgrades and reporting progress. The complete 99-line source was read for this report.

## Important APIs, Types, and Functions

Methods are `finalize`, `finalizeAndWaitForCompletion`, `reportStatus`, and `getStatus`. It also defines a shared SLF4J `LOG`.

## Control Flow

The interface defines the expected flow: initiate finalization for a client ID and service context, optionally wait for completion, poll status messages, and read current status.

## State and Persistence Behavior

Implementations coordinate in-memory upgrade state and persistent layout version updates through `LayoutFeature` actions and storage VERSION files.

## Dependencies and Integration Points

It depends on `UpgradeFinalization.Status`, `StatusAndMessages`, `LayoutFeature.UpgradeAction`, and Ozone stability annotations. `BasicUpgradeFinalizer` is the base implementation.

## Risks and Edge Cases

Client ID ownership and takeover semantics are implementation-dependent. Finalization can be background-driven, so callers must poll and handle partial progress/failures.

## Test Signals

Contract tests should cover initiation, polling, takeover, wait timeout/success, and status consistency across service-specific finalizers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeFinalizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/package-info.java

## Purpose

This package descriptor identifies classes for Ozone upgrade and layout version management. The complete 22-line source was read for this report.

## Important APIs, Types, and Functions

No executable APIs are defined. The package includes layout version managers, finalizers, executors, and upgrade action annotations.

## Control Flow

There is no control flow.

## State and Persistence Behavior

The descriptor owns no state. Package classes coordinate in-memory upgrade state with persistent VERSION file layout versions.

## Dependencies and Integration Points

The package integrates with component storage, layout features, upgrade actions, JMX, and finalization RPC/CLI flows.

## Risks and Edge Cases

Documentation is broad and does not encode the finalization state-machine invariants; individual classes must be read for details.

## Test Signals

Direct testing is compile/javadoc only; package behavior is covered through version manager and finalizer tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/util/ObjectSerializer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/util/ObjectSerializer.java

## Purpose

`ObjectSerializer<T extends WithChecksum>` defines a generic serialization/deserialization contract for checksum-bearing objects. The complete 73-line source was read for this report.

## Important APIs, Types, and Functions

Methods are `load(File)`, `load(InputStream)`, `save(File,T)`, `verifyChecksum(T)`, and `close`.

## Control Flow

There is no implementation flow. Implementations load from files/streams, save to files, verify checksum integrity, and release resources on close.

## State and Persistence Behavior

The interface owns no state. Implementations persist serialized objects to files and may maintain serializer pools or buffers.

## Dependencies and Integration Points

It depends on `WithChecksum`, `Closeable`, `File`, `InputStream`, and `IOException`. `YamlSerializer` in the same package is a likely implementation.

## Risks and Edge Cases

The generic bound uses raw `WithChecksum`, losing the self-referential type parameter. Implementations must define checksum calculation and failure behavior consistently. `close` can throw `IOException`.

## Test Signals

Tests should cover file and stream load, save/load round trip, checksum success/failure, corrupt input handling, and close resource cleanup for implementations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/util/ObjectSerializer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/util/WithChecksum.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/util/WithChecksum.java

## Purpose

`WithChecksum<T>` marks copyable objects that expose a checksum string. The complete 28-line source was read for this report.

## Important APIs, Types, and Functions

It extends `CopyObject<T>` and declares `String getChecksum()`.

## Control Flow

There is no implementation flow.

## State and Persistence Behavior

Implementations own checksum state and copy behavior. The checksum is used by serializers to verify persisted data integrity.

## Dependencies and Integration Points

It depends on `org.apache.hadoop.hdds.utils.db.CopyObject` and is the type bound for `ObjectSerializer`.

## Risks and Edge Cases

The interface does not define checksum algorithm, encoding, nullability, or when checksums are recomputed. Implementations must provide stable copy semantics.

## Test Signals

Tests should verify implementation checksum stability, copy independence, serializer verification, and behavior for missing or stale checksum values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/util/WithChecksum.java -->
