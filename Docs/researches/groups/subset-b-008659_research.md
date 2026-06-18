# subset-b-008659 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IndexSearchType.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IndexSearchType.java research

## Purpose

`IndexSearchType` is a small Java enum mirroring RocksDB's block-based table index search modes. It lets Java users configure how block index entries are searched when the enum is passed through `BlockBasedTableConfig` and JNI into native table options.

## Important APIs and types

The enum values are `kBinary`, `kInterpolation`, and `kAuto`, each carrying a byte value that must match the C++ enum. `getValue()` is package-private, which keeps byte serialization inside the `org.rocksdb` binding layer rather than exposing it as a public API.

## Control flow

There is no runtime branching beyond construction and byte retrieval. Java table-option code calls `getValue()`, JNI receives the byte, and native RocksDB interprets it as the corresponding index-search strategy.

## State and persistence behavior

The only state is the immutable byte value stored in each enum constant. The selected mode affects newly configured table readers or table options, not Java-side persistence. Any durable effect comes from native RocksDB options files or SSTs written with the selected table configuration.

## Dependencies and integration points

The enum depends only on `org.rocksdb` package conventions. It integrates with block-based table configuration and native enum parity; interpolation and auto modes require compatible bytewise comparators according to the comments.

## Risks and test signals

The main risk is JNI enum drift: a byte mismatch would silently configure the wrong native mode. Tests should assert byte parity through table option round-trips or JNI option construction, and should cover rejection or behavior differences when non-bytewise comparators are used with interpolation-oriented modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IndexSearchType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IndexShorteningMode.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IndexShorteningMode.java research

## Purpose

`IndexShorteningMode` exposes the RocksDB choice for how much block index separator keys may be shortened. It trades index size against iterator seek precision, especially for direct-IO or no-cache workloads where an over-shortened separator can force unnecessary data block reads.

## Important APIs and types

The enum values are `kNoShortening`, `kShortenSeparators`, and `kShortenSeparatorsAndSuccessor`. Each stores a native byte, returned by package-private `getValue()`. The detailed class comment is the most important API documentation: it explains separator placement between blocks and the special cost of shortening the final file upper-bound key.

## Control flow

There is no active Java control flow. Configuration code serializes the chosen constant to a byte; native table-building code decides how to encode index keys when writing new tables.

## State and persistence behavior

The Java state is immutable enum metadata. The selected value affects newly written SST index entries and can therefore become part of persistent table-file layout. Existing SST files are not rewritten by changing the Java option.

## Dependencies and integration points

This enum is used with block-based table configuration and is related to `IndexType.kBinarySearchWithFirstKey`, direct reads, and iterator seek behavior. Correctness depends on native RocksDB interpreting the byte values identically.

## Risks and test signals

Byte-value drift would change SST index encoding policy. Behavioral tests should build tables under each mode and verify table-option round-trips, iterator seek correctness, and performance-sensitive signals such as unnecessary block reads under `PerfContext`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IndexShorteningMode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IndexType.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IndexType.java research

## Purpose

`IndexType` maps Java block-based table index choices to RocksDB's native table factory. It lets Java applications choose between compact binary-search indexes, prefix hash indexes, two-level indexes, and binary indexes that include each data block's first key.

## Important APIs and types

The enum values are `kBinarySearch`, `kHashSearch`, `kTwoLevelIndexSearch`, and `kBinarySearchWithFirstKey`. `getValue()` is public and returns the byte passed to JNI. The comments document important prerequisites and costs, such as prefix extractor dependence for hash search and larger indexes for first-key indexes.

## Control flow

The enum itself has no logic beyond constant construction. Configuration classes read `getValue()` and pass the byte to native table factory creation, where RocksDB chooses the concrete index implementation.

## State and persistence behavior

Only immutable byte constants are stored in Java. The chosen index type affects newly built SST files and table readers; for persisted SSTs, index layout is part of the file format produced by native RocksDB.

## Dependencies and integration points

It integrates with `BlockBasedTableConfig`, prefix extractors, comparators, and `IndexShorteningMode`. Java must preserve parity with native C++ enum ordering and values.

## Risks and test signals

The sharp edge is that `kHashSearch` depends on a prefix extractor and `kBinarySearchWithFirstKey` can substantially increase index size. Tests should cover option creation, native option round-trips, opening DBs with each mode, prefix lookup behavior for hash indexes, and iterator block-read counters for first-key indexes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IndexType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/InfoLogLevel.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/InfoLogLevel.java research

## Purpose

`InfoLogLevel` is the Java representation of RocksDB's native logging levels. It is used by `Options`, `DBOptions`, and `Logger` to configure filtering and to decode native log-level bytes back into Java constants.

## Important APIs and types

The constants are `DEBUG_LEVEL`, `INFO_LEVEL`, `WARN_LEVEL`, `ERROR_LEVEL`, `FATAL_LEVEL`, `HEADER_LEVEL`, and `NUM_INFO_LOG_LEVELS`. `getValue()` returns the native byte. `getInfoLogLevel(byte)` performs a linear lookup and throws `IllegalArgumentException` for unknown bytes.

## Control flow

Setter code passes `getValue()` to JNI. Getter code retrieves a byte from native state and calls `getInfoLogLevel()`. Java callback loggers receive decoded levels when native code invokes the Java logging callback.

## State and persistence behavior

The enum stores immutable byte constants. The selected level is held in native options or logger state and can affect which log records are emitted to persistent LOG files or Java logging sinks.

## Dependencies and integration points

It integrates directly with `Logger`, `LoggerInterface`, `Options.setInfoLogLevel()`, and native RocksDB logging. The byte mapping is a JNI contract.

## Risks and test signals

Risks are enum drift and invalid native bytes causing exceptions in getter paths or logger callbacks. Tests should verify all byte round-trips, invalid-byte rejection, and that `Options` and custom `Logger` instances observe level changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/InfoLogLevel.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IngestExternalFileOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IngestExternalFileOptions.java research

## Purpose

`IngestExternalFileOptions` is a `RocksObject` wrapper for native options consumed by `RocksDB.ingestExternalFile(...)`. It controls how externally produced SST files are copied or moved into a DB, how they interact with snapshots and sequence numbers, and whether ingestion may block on memtable flushes.

## Important APIs and types

The default constructor creates native defaults. The four-argument constructor initializes `moveFiles`, `snapshotConsistency`, `allowGlobalSeqNo`, and `allowBlockingFlush`. Fluent setters and getters cover those fields plus `ingestBehind` and `writeGlobalSeqno`. All public mutators return `this`; all real storage lives behind `nativeHandle_`.

## Control flow

Construction calls `newIngestExternalFileOptions(...)`. Each getter and setter is a direct JNI call. Disposal calls `disposeInternalJni(handle)`. There is no Java-side validation of combinations such as ingest-behind requiring DB-level `allowIngestBehind`.

## State and persistence behavior

Java state is the owned native handle. The options influence persistent DB state during ingestion: files may be moved rather than copied, global sequence numbers can be assigned or written into files for compatibility, snapshots can be protected from newly ingested keys, and ingest-behind places files at the bottommost level with sequence number zero.

## Dependencies and integration points

The class integrates with `RocksDB.ingestExternalFile(ColumnFamilyHandle, List, IngestExternalFileOptions)`, external SST creation flows, DB-level `allowIngestBehind`, snapshots, memtables, and sequence-number assignment in native RocksDB.

## Risks and test signals

The main risks are unsafe option combinations delegated to native code, lifecycle misuse after `close()`, and compatibility surprises around `writeGlobalSeqno`. Tests should cover getter/setter round-trips, default values, ingestion with overlapping key ranges, snapshot visibility, move-vs-copy file behavior, ingest-behind prerequisites, and downgrade-compatible global-seqno writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/IngestExternalFileOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/KeyMayExist.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/KeyMayExist.java research

## Purpose

`KeyMayExist` is an immutable result object for RocksDB key-existence probes. It represents whether native `KeyMayExist` determined a key is absent, may exist without returning a value, or may exist with a value length.

## Important APIs and types

`KeyMayExistEnum` has `kNotExist`, `kExistsWithoutValue`, and `kExistsWithValue`. The public final fields are `exists` and `valueLength`. The constructor sets both fields, and `equals()`/`hashCode()` compare them.

## Control flow

There is no behavior beyond object construction and equality checks. Native-facing RocksDB methods can create or return this value to Java callers as a compact status carrier.

## State and persistence behavior

Instances are immutable and hold no native resources. The class does not persist anything; it only describes a point-in-time lookup signal.

## Dependencies and integration points

It depends on `java.util.Objects` for hashing. It integrates with RocksDB point lookup APIs that expose "may exist" semantics, where Bloom filters and caches can answer absence cheaply but existence can remain uncertain.

## Risks and test signals

The object deliberately exposes fields instead of accessor methods, so API compatibility depends on those names. Tests should assert equality/hash behavior, all enum states, and JNI conversion from native existence results including value length when a value is available.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/KeyMayExist.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LRUCache.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LRUCache.java research

## Purpose

`LRUCache` is the Java wrapper for RocksDB's sharded least-recently-used cache. It is used as a block cache, row cache, or other cache dependency by table options and DB options.

## Important APIs and types

The overloaded constructors progressively expose `capacity`, `numShardBits`, `strictCapacityLimit`, `highPriPoolRatio`, and `lowPriPoolRatio`. All constructors delegate to the native `newLRUCache(...)` and then to the `Cache` superclass. Disposal calls `disposeInternalJni(handle)`.

## Control flow

Construction is the only active path: Java computes default constructor arguments and native RocksDB builds the cache. Cache operations are inherited from `Cache`; this class only selects the LRU implementation.

## State and persistence behavior

State is native cache memory behind `nativeHandle_`. It is process-local and non-persistent. Cache contents affect read latency and memory pressure but are not durable DB state.

## Dependencies and integration points

`LRUCache` extends `Cache` and is consumed by `Options`, `BlockBasedTableConfig`, `WriteBufferManager`, and memory usage utilities. Its shard and priority-pool choices integrate with native cache partitioning and high/low priority block admission.

## Risks and test signals

Risks include native memory leaks if not closed, invalid capacities or ratios surfacing only from native code, and strict-capacity insert failures changing performance. Tests should verify constructor coverage, cache property counters through DB reads, memory usage reporting, and close/dispose behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LRUCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LevelMetaData.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LevelMetaData.java research

## Purpose

`LevelMetaData` is a Java snapshot of native RocksDB metadata for one LSM level. It is returned by metadata APIs to describe level number, total file bytes, and the SST files in that level.

## Important APIs and types

The private constructor is called from JNI with `level`, `size`, and an array of `SstFileMetaData`. Public accessors are `level()`, `size()`, and `files()`, which returns `Arrays.asList(files)`.

## Control flow

Native code constructs the object. Java callers then read the immutable fields. No Java logic refreshes the metadata; callers must request a new metadata object to observe DB changes.

## State and persistence behavior

The class stores a point-in-time Java copy of metadata. It does not own files or native handles. `size` reflects persistent SST file sizes at collection time; compaction, flush, or deletion can make it stale.

## Dependencies and integration points

It depends on `SstFileMetaData` and is typically nested under `ColumnFamilyMetaData` or related RocksDB metadata APIs. It provides Java visibility into compaction layout and storage usage.

## Risks and test signals

`files()` exposes a fixed-size list backed by the internal array, so callers cannot add/remove but can observe mutable `SstFileMetaData` objects if those objects expose mutable internals. Tests should cover JNI construction, correct level aggregation, empty levels, and staleness expectations after compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LevelMetaData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LiveFileMetaData.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LiveFileMetaData.java research

## Purpose

`LiveFileMetaData` extends `SstFileMetaData` with column-family name and level information for live SST files. It is used by live-file APIs and by native interop that needs to pass a Java metadata object back into C++.

## Important APIs and types

JNI calls the private constructor with column-family bytes, level, file identity, key bounds, sequence bounds, read samples, compaction state, entry/delete counts, and checksum bytes. Public accessors are `columnFamilyName()` and `level()`. `newLiveFileMetaDataHandle()` builds a native metadata handle from the Java fields.

## Control flow

Native code creates Java instances for metadata reads. Java callers can inspect fields or request a new native handle; that call copies Java field values back over JNI.

## State and persistence behavior

The object is a point-in-time metadata copy and does not keep a live file pinned by itself. File names, key bounds, and checksums describe persistent SST state at collection time. `columnFamilyName()` returns the internal byte array, so caller mutation can affect subsequent `newLiveFileMetaDataHandle()` calls.

## Dependencies and integration points

It depends on `SstFileMetaData` and integrates with live-file APIs, backup/checkpoint tooling, and any JNI path that reconstructs native live-file metadata.

## Risks and test signals

The internal array exposure is a mutability risk. Another sharp edge is that `newLiveFileMetaDataHandle()` passes most metadata fields but not the checksum parameter visible in the constructor. Tests should verify metadata round-trips, column-family bytes, level accuracy, and handle creation with unusual key bounds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LiveFileMetaData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LogFile.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LogFile.java research

## Purpose

`LogFile` is a Java value object describing a RocksDB write-ahead log file. It is returned from WAL metadata APIs such as sorted WAL file listing.

## Important APIs and types

The private JNI constructor accepts `pathName`, `logNumber`, a native WAL type byte, `startSequence`, and `sizeFileBytes`. Accessors expose each field. The constructor decodes the type through `WalFileType.fromValue(...)`.

## Control flow

Native code constructs instances, Java callers inspect them, and invalid WAL type bytes fail during construction through `WalFileType` validation.

## State and persistence behavior

The class is immutable Java metadata. It describes persistent WAL files by relative path, creation-number ordering, archive/live state, starting sequence number, and byte size. It does not own or pin WAL files.

## Dependencies and integration points

It depends on `WalFileType` and integrates with WAL inspection, backup, replication, and diagnostics code using RocksDB's Java API.

## Risks and test signals

Metadata can be stale if WAL files are archived or deleted after collection. Tests should cover JNI construction, type decoding, live and archived path examples, ordering by `logNumber`, and invalid native type handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LogFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Logger.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Logger.java research

## Purpose

`Logger` is the abstract Java callback logger for RocksDB. It lets native RocksDB send log records into Java logging frameworks instead of only writing filesystem LOG files.

## Important APIs and types

The active constructor accepts `InfoLogLevel`. Deprecated constructors derive the level from `Options` or `DBOptions`. `initializeNative(...)` creates a native callback logger from one log-level argument. `setInfoLogLevel()`, `infoLogLevel()`, `getNativeHandle()`, and `getLoggerType()` implement `LoggerInterface`. Subclasses implement `protected abstract void log(InfoLogLevel, String)`.

## Control flow

Construction goes through `RocksCallbackObject`, then `initializeNative()` calls native `newLogger`. Native RocksDB checks the configured level and invokes the Java `log` callback for accepted messages. Disposal uses a specialized native path because the underlying C++ object is held through `std::shared_ptr`.

## State and persistence behavior

The object owns a native callback handle and has no durable state. It can redirect persistent logging away from DB LOG files depending on options. Java subclasses may persist records through their chosen logging backend.

## Dependencies and integration points

It integrates with `Options.setLogger(LoggerInterface)`, `InfoLogLevel`, `LoggerType.JAVA_IMPLEMENTATION`, and the `RocksCallbackObject` lifecycle. It crosses JNI on every emitted log message.

## Risks and test signals

The class warns about production overhead from native-to-Java transitions and native allocations for verbose levels. Risks include callback exceptions, premature disposal while native options still reference the logger, and incorrect level filtering. Tests should cover custom logger callbacks, level round-trips, disposal, and `Options.setLogger()` integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Logger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LoggerInterface.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LoggerInterface.java research

## Purpose

`LoggerInterface` defines the minimum Java contract for objects that can be installed as RocksDB loggers. It abstracts both Java callback loggers and native/stderr-backed logger implementations.

## Important APIs and types

The interface requires `setInfoLogLevel(InfoLogLevel)`, `infoLogLevel()`, `getNativeHandle()`, and `getLoggerType()`. These methods provide both configuration and enough identity for `Options.setLogger(...)` to pass the correct native handle and logger-kind byte over JNI.

## Control flow

Implementations perform the actual work. `Options` consumes the interface, calls `getNativeHandle()` and `getLoggerType().getValue()`, and native RocksDB adopts or references the logger according to the implementation type.

## State and persistence behavior

The interface has no state. Implementations may own native handles or Java callback state. Log persistence depends on the concrete logger.

## Dependencies and integration points

It depends on `InfoLogLevel` and `LoggerType`. The main implementation in this subset is `Logger`; other native logger wrappers can implement the same interface.

## Risks and test signals

Implementations must return a native handle whose lifetime covers native use. Tests should verify that every implementation reports the correct `LoggerType`, supports level changes, and works when installed in `Options`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LoggerInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LoggerType.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LoggerType.java research

## Purpose

`LoggerType` is an internal enum used to tell JNI what kind of logger handle is being passed. It distinguishes Java callback loggers from native stderr loggers.

## Important APIs and types

The constants are `JAVA_IMPLEMENTATION` and `STDERR_IMPLEMENTATION`. `getValue()` is package-private. `getLoggerType(byte)` decodes native bytes and throws `IllegalArgumentException` on unknown values.

## Control flow

`LoggerInterface` implementations report a type. `Options.setLogger()` passes the type byte with the native handle, and native code chooses the correct adapter or ownership behavior.

## State and persistence behavior

The enum stores only immutable bytes. Logger type affects runtime logging routing, not DB persistence by itself.

## Dependencies and integration points

It is used by `Logger`, `LoggerInterface`, and options JNI. The byte values must match native RocksJava expectations.

## Risks and test signals

Byte drift or wrong implementation reporting can make native code treat a handle as the wrong logger kind. Tests should cover byte decode, invalid-byte failure, and setting both Java and stderr logger implementations when available.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LoggerType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemTableConfig.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemTableConfig.java research

## Purpose

`MemTableConfig` is the abstract base for Java configuration objects that create native RocksDB memtable factories. It lets Java users select alternative in-memory write-buffer representations through `Options.setMemTableConfig(...)`.

## Important APIs and types

The only method is protected abstract `newMemTableFactoryHandle()`, which subclasses implement to return a native `MemTableRepFactory` handle. The class itself owns no native resource.

## Control flow

Applications instantiate a concrete subclass, pass it to `Options.setMemTableConfig`, and `Options` calls `newMemTableFactoryHandle()` to install the native factory.

## State and persistence behavior

Subclasses may store configuration fields, but this base has none. Memtable factory choice affects in-memory write buffering and flush behavior; persistence happens when native RocksDB flushes memtables into SSTs.

## Dependencies and integration points

It integrates with `Options`, native memtable factory creation, and concrete configs such as skip-list, vector, hash-linked-list, or hash-skip-list configurations elsewhere in the package.

## Risks and test signals

The main risks are native handle lifetime and invalid subclass parameters. Tests should assert that each concrete config installs successfully, reports the expected `memTableFactoryName()`, and can open/write/flush a DB.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemTableConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemTableInfo.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemTableInfo.java research

## Purpose

`MemTableInfo` is an immutable Java metadata object describing one memtable: its column family, sequence-number range signals, entry count, and delete count.

## Important APIs and types

The package-private constructor is intended for JNI and tests. Accessors expose `columnFamilyName`, `firstSeqno`, `earliestSeqno`, `numEntries`, and `numDeletes`. `equals()`, `hashCode()`, and `toString()` make it suitable for assertions and diagnostics.

## Control flow

Native code or tests construct instances. Java callers read fields or compare objects. No refresh or native calls occur after construction.

## State and persistence behavior

The class is a point-in-time metadata snapshot. It describes in-memory memtable state, not durable SST state. Sequence-number fields help reason about what writes may be present in this memtable or later memtables.

## Dependencies and integration points

It depends on `java.util.Objects` and integrates with RocksDB metadata APIs that expose memtable state to Java.

## Risks and test signals

Metadata can become stale quickly as writes and flushes proceed. Tests should verify equality semantics, string output for diagnostics, JNI construction, and sequence/entry counts after controlled writes and deletes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemTableInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemoryUsageType.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemoryUsageType.java research

## Purpose

`MemoryUsageType` names the categories returned by RocksDB approximate memory-usage reporting. It maps native byte keys to Java enum constants for memtables, table readers, and caches.

## Important APIs and types

The constants are `kMemTableTotal`, `kMemTableUnFlushed`, `kTableReadersTotal`, `kCacheTotal`, and `kNumUsageTypes`. `getValue()` returns the native byte. `getMemoryUsageType(byte)` decodes bytes and throws for unknown values.

## Control flow

`MemoryUtil` receives a native `Map<Byte, Long>` and decodes every key through `getMemoryUsageType()`. Unknown bytes fail the call rather than being silently ignored.

## State and persistence behavior

The enum stores immutable native category IDs. It reports memory state only; it has no persistence behavior.

## Dependencies and integration points

It integrates with `MemoryUtil.getApproximateMemoryUsageByType(...)` and the native `rocksdb::MemoryUtil` category ordering.

## Risks and test signals

The key risk is native enum drift or introduction of a new category without Java updates. Tests should cover all known byte mappings, invalid-byte rejection, and non-empty memory reports for DBs and caches.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemoryUsageType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemoryUtil.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemoryUtil.java research

## Purpose

`MemoryUtil` is a static JNI facade for approximate RocksDB memory usage. It aggregates usage across supplied DB instances and caches and returns a Java map keyed by `MemoryUsageType`.

## Important APIs and types

`getApproximateMemoryUsageByType(List<RocksDB>, Set<Cache>)` accepts nullable DB and cache collections. It converts them to native handle arrays, calls native `getApproximateMemoryUsageByType(long[], long[])`, and converts the returned byte-keyed map to `Map<MemoryUsageType, Long>`.

## Control flow

The method computes counts, fills arrays by iterating the list and set, calls JNI once, then decodes each map key with `MemoryUsageType.getMemoryUsageType()`. Cache iteration uses an explicit index because sets do not expose indexed iteration.

## State and persistence behavior

The class owns no state. It samples process memory associated with live native handles. Results are approximate and transient; no DB files are modified.

## Dependencies and integration points

It depends on `RocksDB`, `Cache`, `MemoryUsageType`, and native memory-util code. It deliberately reports cache usage only for caches passed in the cache set, not caches reachable through the DB list.

## Risks and test signals

Risks include passing closed objects, duplicate caches collapsed by `Set`, and unknown native category bytes. Tests should cover null inputs, empty inputs, multiple DBs, shared caches, closed-handle behavior, and byte-to-enum conversion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemoryUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MergeOperator.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MergeOperator.java research

## Purpose

`MergeOperator` is the abstract Java base for native RocksDB merge operators. It represents a native operator that combines merge operands for a key during reads or compaction.

## Important APIs and types

The only constructor is protected and accepts a native handle, passing it to `RocksObject`. Concrete subclasses provide actual operators, typically by creating named or native merge-operator handles.

## Control flow

Subclasses construct native merge operators and call this constructor. `Options.setMergeOperator(MergeOperator)` passes the stored native handle to native options.

## State and persistence behavior

The class owns a native merge operator handle through `RocksObject`. Merge operators affect logical value computation and compaction output, which can become durable in SST files after compaction or flush.

## Dependencies and integration points

It integrates with `Options`, column-family options, read paths, write paths using merge operands, and native compaction.

## Risks and test signals

Risks are lifecycle misuse and operator/DB incompatibility when reopening without the same operator. Tests should verify installation, merge semantics across get/compaction/reopen, and proper close behavior for concrete operators.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MergeOperator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableColumnFamilyOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableColumnFamilyOptions.java research

## Purpose

`MutableColumnFamilyOptions` is the Java representation of dynamically changeable column-family options. It builds the key/value arrays consumed by `RocksDB.setOptions(...)` and parses RocksDB-style option strings into a typed builder.

## Important APIs and types

`builder()` creates `MutableColumnFamilyOptionsBuilder`; `parse(String, boolean)` parses semicolon-separated options via `OptionString.Parser`. Internal enum groups implement `MutableOptionKey`: `MemtableOption`, `CompactionOption`, `BlobOption`, and `MiscOption`. Each key declares a `ValueType`. The builder extends `AbstractMutableOptionsBuilder` and implements `MutableColumnFamilyOptionsInterface`, exposing fluent setters/getters for memtable, compaction, blob, compression, and miscellaneous options.

## Control flow

Builder methods call typed helpers such as `setLong`, `setBoolean`, `setIntArray`, and `setEnum`, which store validated values in the abstract builder. `build(keys, values)` creates the immutable `MutableColumnFamilyOptions` wrapper around string arrays. Parsing first builds `OptionString.Entry` objects, then resolves keys through `ALL_KEYS_LOOKUP`, optionally ignoring unknown keys.

## State and persistence behavior

The final object stores option keys and serialized string values, not native handles. Applying it changes live native column-family state and can influence future flushes, compactions, blob files, TTL, and write throttling. Some changes affect only future files.

## Dependencies and integration points

It depends on `AbstractMutableOptions`, `AbstractMutableOptionsBuilder`, `MutableOptionKey`, `MutableOptionValue`, `OptionString`, `CompressionType`, and `PrepopulateBlobCache`. It is consumed by `RocksDB.setOptions(ColumnFamilyHandle, MutableColumnFamilyOptions)`.

## Risks and test signals

Risks include Java key lists falling behind native mutable options, deprecated keys lingering, parse ambiguity for enum values, and typed conversions losing precision. Tests should cover parse/build round-trips, unknown-key behavior, each `ValueType`, native `setOptions` application, and getter failure for unset options if the abstract builder enforces presence.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableColumnFamilyOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableColumnFamilyOptionsInterface.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableColumnFamilyOptionsInterface.java research

## Purpose

`MutableColumnFamilyOptionsInterface` defines the public fluent API for the core dynamically changeable column-family options. It extends `AdvancedMutableColumnFamilyOptionsInterface` to combine common and advanced mutable CF settings.

## Important APIs and types

The interface is generic, returning `T` from setters to support fluent use by both full `Options` and mutable-options builders. It declares write buffer size, automatic compaction disablement, level-0 compaction trigger, max compaction bytes, max bytes for level base, and compression type accessors.

## Control flow

There is no implementation. Implementers map these calls either to immediate native setter/getter calls (`Options`) or to deferred key/value storage (`MutableColumnFamilyOptionsBuilder`).

## State and persistence behavior

The interface owns no state. Implementations can either mutate native options immediately or create serialized mutable-option payloads. The documented options affect in-memory buffering, background compaction, and future SST compression/layout.

## Dependencies and integration points

It depends on `CompressionType` and the advanced mutable CF interface. It is a shared contract between live `Options`, parsed mutable options, and `RocksDB.setOptions` call sites.

## Risks and test signals

The risk is contract divergence: implementers must preserve method names, return types, and semantics. Tests should ensure `Options` and `MutableColumnFamilyOptionsBuilder` both implement the same calls and that generated mutable options apply successfully to an open column family.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableColumnFamilyOptionsInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableDBOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableDBOptions.java research

## Purpose

`MutableDBOptions` is the Java payload for dynamically changeable database-wide options. It supports fluent construction and parsing of RocksDB-style option strings for `RocksDB.setDBOptions(...)`.

## Important APIs and types

`builder()` creates `MutableDBOptionsBuilder`; `parse(String, boolean)` uses `OptionString.Parser`. The `DBOption` enum lists supported keys and `ValueType`s, including background jobs, shutdown flush behavior, file buffering, delayed write rate, WAL size, obsolete-file deletion period, stats intervals, max open files, sync settings, compaction readahead, wakeup interval, and daily off-peak time.

## Control flow

Builder methods call typed abstract builder helpers and expose corresponding getters. `ALL_KEYS_LOOKUP` maps option names to enum keys. Parsing resolves entries against that map and either rejects or ignores unknown keys according to the caller flag.

## State and persistence behavior

The built object stores key/value strings. Applying it changes live DB-wide native state. Some options affect runtime scheduling or throttling immediately; others influence future logging, WAL management, stats persistence, or file I/O behavior.

## Dependencies and integration points

It depends on `AbstractMutableOptions`, `AbstractMutableOptionsBuilder`, `MutableOptionKey`, `OptionString`, and `MutableDBOptionsInterface`. It integrates with `RocksDB.setDBOptions(MutableDBOptions)` and mirrors the mutable subset also implemented directly by `Options`.

## Risks and test signals

Risks include incomplete key coverage, deprecated `max_background_compactions` behavior, string format changes, and Java/native value-type drift. Tests should cover parse/build round-trips, unknown-key behavior, all builder methods, native application to an open DB, and off-peak time validation in native code.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableDBOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableDBOptionsInterface.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableDBOptionsInterface.java research

## Purpose

`MutableDBOptionsInterface` is the shared Java contract for DB-wide options that can be changed dynamically. It is implemented by full `Options` for immediate native mutation and by `MutableDBOptionsBuilder` for deferred `setDBOptions` payload creation.

## Important APIs and types

The generic setter return type supports fluent chaining. Methods cover background job counts, deprecated background compactions, shutdown flush policy, writable-file buffer size, delayed write rate, total WAL size, obsolete-file cleanup period, stats dump/persist/history settings, max open files, bytes-per-sync and WAL bytes-per-sync, strict sync throttling, compaction readahead, compaction trigger wakeup, and daily UTC off-peak time.

## Control flow

The interface contains no implementation. Its Javadocs encode runtime behavior and persistence caveats, such as `avoidFlushDuringShutdown` potentially losing unpersisted WAL-disabled writes and `strictBytesPerSync` not adding durability guarantees.

## State and persistence behavior

Implementations alter or serialize DB-level runtime state. The options influence WAL retention and flushing, background work, logging/statistics persistence, file I/O, throttling, and off-peak compaction timing.

## Dependencies and integration points

It references `RocksEnv`, `Priority`, `DBOptionsInterface`, column-family options, and `RocksDB.setDBOptions(...)`. It also aligns with native RocksDB option names used in OPTIONS files and mutable option strings.

## Risks and test signals

The long documentation is part of the API contract; mismatches with native behavior are a risk. Tests should verify both implementers, deprecated background compaction compatibility, dynamic application to open DBs, WAL/flush side effects under controlled workloads, and invalid off-peak strings.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableDBOptionsInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableOptionKey.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableOptionKey.java research

## Purpose

`MutableOptionKey` is the small internal interface that lets mutable-option builders treat enum constants from different option groups uniformly.

## Important APIs and types

`ValueType` enumerates the supported serialized types: `DOUBLE`, `LONG`, `INT`, `BOOLEAN`, `INT_ARRAY`, `ENUM`, and `STRING`. Implementers must provide `name()` and `getValueType()`. Java enums automatically provide `name()`, so option-key enums only implement value typing.

## Control flow

Abstract mutable-option builders use `name()` to serialize the native option key and `getValueType()` to parse or validate `MutableOptionValue` instances.

## State and persistence behavior

The interface has no state. It helps produce string key/value payloads that native RocksDB applies to live DB or column-family options.

## Dependencies and integration points

It is implemented by `MutableDBOptions.DBOption` and the option groups inside `MutableColumnFamilyOptions`. It works with `MutableOptionValue` and `AbstractMutableOptionsBuilder`.

## Risks and test signals

Adding a native mutable option requires selecting the correct `ValueType`; wrong typing can cause Java parse failures or native rejection. Tests should cover every value type and option-key group during parse/build and native application.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableOptionKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableOptionValue.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableOptionValue.java research

## Purpose

`MutableOptionValue` is the typed value wrapper used by mutable-option builders. It centralizes conversion between Java objects and the string forms sent to RocksDB's mutable-option APIs.

## Important APIs and types

Static factories create wrappers for strings, doubles, longs, ints, booleans, int arrays, and enums. Abstract conversion methods include `asDouble`, `asLong`, `asInt`, `asBoolean`, `asIntArray`, `asString`, and `asObject`. Nested classes implement type-specific conversions and serialization; int arrays are joined with `AbstractMutableOptions.INT_ARRAY_INT_SEPARATOR`, and enum values serialize as `name()`.

## Control flow

Builders create or parse `MutableOptionValue` instances, then request the conversion required by a `MutableOptionKey.ValueType`. Unsupported conversions throw `NumberFormatException` or `IllegalStateException`. Numeric conversions can downcast with range checks for int.

## State and persistence behavior

Each wrapper stores an immutable reference or primitive value, except int arrays are stored by reference. The values become serialized strings in mutable-option payloads; persistence effects depend on the option being applied.

## Dependencies and integration points

It depends on `AbstractMutableOptions.INT_ARRAY_INT_SEPARATOR` and is used by `AbstractMutableOptionsBuilder`, `MutableDBOptions`, and `MutableColumnFamilyOptions`.

## Risks and test signals

Risks include array mutability after wrapping, `Boolean.parseBoolean` treating unknown strings as false, numeric truncation from double/long to int arrays, and inconsistent exception types. Tests should cover all valid and invalid conversions, enum serialization, int-array separator handling, and defensive behavior around mutable arrays.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableOptionValue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/NativeComparatorWrapper.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/NativeComparatorWrapper.java research

## Purpose

`NativeComparatorWrapper` adapts a comparator implemented directly in C++ so it can be installed through Java APIs that expect an `AbstractComparator`.

## Important APIs and types

`getComparatorType()` returns `ComparatorType.JAVA_NATIVE_COMPARATOR_WRAPPER`. The Java comparator methods `name`, `compare`, `findShortestSeparator`, and `findShortSuccessor` are final and throw `IllegalStateException` because native code owns the implementation. `disposeInternal()` calls a native disposal function.

## Control flow

Subclasses or JNI create a wrapper around a native comparator handle. `Options.setComparator(AbstractComparator)` passes that handle and comparator type to native options. Any accidental Java-side comparator invocation fails loudly.

## State and persistence behavior

State is the native comparator handle inherited from callback/reference machinery. Comparator choice affects key ordering and therefore persistent SST and WAL interpretation; DBs must be reopened with a compatible comparator.

## Dependencies and integration points

It depends on `AbstractComparator`, `ComparatorType`, `ByteBuffer`, and options comparator installation. It is specifically for native comparators extending `rocksdb::Comparator`.

## Risks and test signals

The class prevents Java fallback, so wrong dispatch will fail at runtime. Lifecycle is delicate because the object is not a normal Java callback despite extending callback infrastructure. Tests should install a native comparator, verify ordering through writes/iterators, assert Java method calls throw, and verify disposal does not double-free.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/NativeComparatorWrapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/NativeLibraryLoader.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/NativeLibraryLoader.java research

## Purpose

`NativeLibraryLoader` loads the RocksDB JNI library for Java clients. It first tries libraries available through `java.library.path`, then falls back to extracting a bundled JNI library resource from the jar into a temporary file and loading it.

## Important APIs and types

`getInstance()` returns the singleton. `loadLibrary(String tmpDir)` is synchronized and tries `System.loadLibrary(sharedLibraryName)`, `System.loadLibrary(jniLibraryName)`, optional fallback JNI library name, and finally `loadLibraryFromJar(tmpDir)`. `loadLibraryFromJarToTemp()` locates primary or fallback resource names. `createTemp()` creates either a JVM temp file or a named file under a caller-provided directory.

## Control flow

The load sequence catches `UnsatisfiedLinkError` from path-based attempts and optionally prints diagnostics when `ROCKS_JAVA_DEBUG_NLL=true`. Jar extraction uses `getClass().getClassLoader().getResourceAsStream`, copies with `Files.copy(..., REPLACE_EXISTING)`, marks temp files for deletion on exit, and calls `System.load()` once guarded by `initialized`.

## State and persistence behavior

Static state includes computed platform-specific library names and the `initialized` flag for jar loading. Extracted native libraries are temporary filesystem artifacts and registered for deletion on JVM exit; provided `tmpDir` files are overwritten after deletion.

## Dependencies and integration points

It depends on `org.rocksdb.util.Environment`, `java.io`, and NIO file copying. It is used by `RocksDB.loadLibrary()` and indirectly by constructors that need native methods.

## Risks and test signals

Risks include classloader resource absence, tmpDir not existing, stale files that cannot be deleted, concurrent load behavior across classloaders, and `initialized` only guarding the jar path. Tests should simulate path-load success, jar extraction success, fallback resource success, missing resources, invalid tmpDir, debug logging, and repeated synchronized calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/NativeLibraryLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OperationStage.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OperationStage.java research

## Purpose

`OperationStage` maps native thread-operation stage bytes to Java constants for RocksDB thread status reporting. It identifies fine-grained phases inside flush and compaction work.

## Important APIs and types

Constants include unknown, flush run/write-L0, compaction prepare/run/process/install/sync, memtable pick, rollback, and install-flush-results stages. `getValue()` returns the internal byte. Package-private `fromValue(byte)` decodes native bytes and throws on unknown values.

## Control flow

Native status code passes a byte into Java; Java calls `fromValue()` while constructing thread status objects. Unknown stage bytes produce an `IllegalArgumentException`.

## State and persistence behavior

The enum has only immutable byte values. It reports live runtime state and has no persistence behavior.

## Dependencies and integration points

It integrates with thread-status APIs and native operation-stage enums. Package-private access keeps it within the binding layer.

## Risks and test signals

Native enum drift is the main risk. Tests should decode every native stage, reject invalid bytes, and verify thread tracking reports expected stages during flush or compaction workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OperationStage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OperationType.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OperationType.java research

## Purpose

`OperationType` maps high-level native thread operation bytes to Java constants for RocksDB thread status reporting.

## Important APIs and types

Constants are `OP_UNKNOWN`, `OP_COMPACTION`, `OP_FLUSH`, and `OP_DBOPEN`. `getValue()` returns the byte. Package-private `fromValue(byte)` performs byte decoding and throws `IllegalArgumentException` for unknown values.

## Control flow

Thread-status JNI constructs Java status objects by decoding native operation bytes. Java code then exposes operation type to callers.

## State and persistence behavior

The enum is immutable and reports transient runtime state only. It does not affect DB files or native operation scheduling.

## Dependencies and integration points

It integrates with thread tracking and status APIs, and must remain byte-compatible with the native operation type enum.

## Risks and test signals

Tests should verify byte mappings, invalid-byte rejection, and status reporting under controlled DB open, flush, and compaction activity.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OperationType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptimisticTransactionDB.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptimisticTransactionDB.java research

## Purpose

`OptimisticTransactionDB` is the Java wrapper for RocksDB's optimistic transaction database. It extends `RocksDB` and implements `TransactionalDB<OptimisticTransactionOptions>`, adding transaction creation and optimistic conflict handling support through native code.

## Important APIs and types

Static `open(Options, String)` opens a default-column-family DB and stores the `Options` reference plus default handle. Static `open(DBOptions, String, List<ColumnFamilyDescriptor>, List<ColumnFamilyHandle>)` opens multiple column families, validates that the default column family descriptor is present, fills caller-provided handles, records owned handles, and stores the default handle. `beginTransaction(...)` overloads create new `Transaction` wrappers or reuse an existing transaction. `getBaseDB()` returns a disowned `RocksDB` wrapper around the underlying base DB.

## Control flow

Open methods marshal option and column-family handles into native arrays, call native `open`, then build Java wrappers around returned handles. Reusing `oldTransaction` asserts native returned the same handle. `close()` closes owned column-family handles, clears the list, closes the native DB while swallowing exceptions, and disposes. `closeE()` propagates close errors but directly closes the DB handle.

## State and persistence behavior

The object owns a native optimistic transaction DB handle and column-family handles. Transactions write to the same persistent RocksDB storage as ordinary writes but check conflicts at commit time. Closing does not fsync WAL files; callers needing durability must sync WAL or issue a sync write first.

## Dependencies and integration points

It depends on `Options`, `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `WriteOptions`, `OptimisticTransactionOptions`, `Transaction`, and base `RocksDB` ownership helpers. It is used by Java clients needing transactional write batches without pessimistic locks.

## Risks and test signals

Risks include missing default column-family descriptors, handle ownership mistakes, close-vs-closeE differences, reused transaction lifecycle ambiguity, and durability assumptions on close. Tests should cover single-CF and multi-CF open, default CF validation, begin/commit conflict behavior, transaction reuse assertions, base DB wrapper disowning, and close ordering with outstanding handles.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptimisticTransactionDB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptimisticTransactionOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptimisticTransactionOptions.java research

## Purpose

`OptimisticTransactionOptions` wraps native options for optimistic transactions. It controls whether transactions take snapshots and which comparator should be used when the DB has a non-default comparator.

## Important APIs and types

The constructor creates a native options object. It implements `TransactionalOptions<OptimisticTransactionOptions>` through `isSetSnapshot()` and `setSetSnapshot(boolean)`. `setComparator(AbstractComparator)` passes a comparator native handle for transaction write-batch indexing.

## Control flow

Each public method asserts ownership and calls a direct native getter or setter. Disposal calls `disposeInternalJni(handle)`.

## State and persistence behavior

State lives in the native options handle. Snapshot choice affects transaction read/conflict semantics. Comparator choice affects in-memory transaction indexing; persistent correctness depends on matching the DB comparator.

## Dependencies and integration points

It integrates with `OptimisticTransactionDB.beginTransaction(...)`, `Transaction`, `WriteBatchWithIndex`, and `AbstractComparator`.

## Risks and test signals

Risks include using a closed comparator or forgetting to set a non-default comparator, which can break transaction conflict/index ordering. Tests should cover getter/setter round-trips, transactions with and without snapshots, custom comparator transactions, and disposal behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptimisticTransactionOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptionString.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptionString.java research

## Purpose

`OptionString` parses RocksDB-style option strings into structured key/value entries for Java mutable option builders. It supports simple scalar/list values and nested complex values wrapped in braces.

## Important APIs and types

`Value` holds either `List<String>` or `List<Entry>`, with `isList()`, `fromList()`, `fromComplex()`, and `toString()`. `Entry` stores a key and `Value`. `Parser.parse(String)` returns a list of top-level entries or throws `Parser.Exception`, a runtime exception with context around the parse position.

## Control flow

The parser keeps a mutable `StringBuilder` of unconsumed input. It skips whitespace, parses keys from alphanumeric/underscore characters, requires `=`, then parses either complex `{...}` values or list-like simple values separated by `:`. Complex values are sequences of options separated by `;`. After top-level parsing, leftover input is an error.

## State and persistence behavior

Parser state is local and transient. Parsed entries feed builders that can produce mutable option payloads; any persistence effect comes from applying those options to RocksDB.

## Dependencies and integration points

It depends only on Java collections and `Objects`. It is used by `MutableDBOptions.parse()` and `MutableColumnFamilyOptions.parse()`.

## Risks and test signals

The grammar is intentionally narrow: keys cannot include dots, values have limited character support, braces serve both complex and wrapped simple values, and escaping is minimal. Tests should cover whitespace, empty embedded vectors, complex values, wrapped values, list separators, malformed input context, and round-trips with mutable option builders.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptionString.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Options.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Options.java research

## Purpose

`Options` is the combined Java wrapper for native `rocksdb::Options`, implementing DB-wide, column-family, and mutable option interfaces. It is the main configuration object passed to `RocksDB.open(...)` and a fluent bridge for almost all common native RocksDB options.

## Important APIs and types

Constructors create native options from defaults, from `DBOptions` plus `ColumnFamilyOptions`, or by shallow-copying another `Options`. `getOptionStringFromProps(Properties)` converts Java properties to RocksDB option-string syntax. The class implements `DBOptionsInterface`, `MutableDBOptionsInterface`, `ColumnFamilyOptionsInterface`, and `MutableColumnFamilyOptionsInterface`. Method groups cover DB creation/open flags, env and paths, logging, WAL, background jobs, file I/O, statistics, write pipeline behavior, memtable and table factories, comparators, merge operators, compaction filters, compression, compaction sizing, blob files, TTL/periodic compaction, consistency checks, and table-properties collector factories.

## Control flow

Most methods assert the object owns its native handle, call a native setter/getter, and return `this`. Java-owned collaborators such as `Env`, comparators, filters, factories, caches, rate limiters, write-buffer managers, compression options, WAL filters, partitioners, and limiters are stored in fields to keep them reachable while native options reference their handles. Collection setters marshal Java lists into arrays of strings, target sizes, bytes, or native handles.

## State and persistence behavior

The primary state is the native `rocksdb::Options` handle. Java fields preserve dependency lifetimes and expose selected configured objects. Options influence both runtime behavior and durable DB state: comparator choice defines key ordering, WAL and recovery settings affect crash recovery, table/memtable factories affect file layout and flush behavior, compression/blob options affect persisted SST/blob files, and stats/log settings can write metadata to disk. The copy constructor is shallow for pointer options, so copied options share Java/native dependencies.

## Dependencies and integration points

`Options` is a central integration class for nearly every RocksJava option type: `Env`, `DBOptions`, `ColumnFamilyOptions`, `AbstractComparator`, `MergeOperator`, compaction filters/factories, `MemTableConfig`, `TableFormatConfig`, `RateLimiter`, `SstFileManager`, `LoggerInterface`, `Statistics`, `Cache`, `WriteBufferManager`, `CompressionOptions`, compaction options, WAL filters, event listeners, `SstPartitionerFactory`, `ConcurrentTaskLimiter`, blob enums, and table-properties collector factories. It also triggers `RocksDB.loadLibrary()` before native allocation.

## Risks and test signals

The class is a broad JNI surface, so risks include enum byte drift, missing Java reference retention, shallow-copy surprises, inconsistent assertions, native validation surfacing late, and options that only affect future files. Table-properties collector getters return wrapper objects that must be closed. Tests should cover constructor/copy behavior, every object-retention setter, option getter/setter round-trips, DB open with representative option combinations, reopen compatibility for persistent options, mutable option interface parity, collector factory lifecycle, and invalid argument propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Options.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptionsUtil.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptionsUtil.java research

## Purpose

`OptionsUtil` exposes static helpers for loading RocksDB OPTIONS files into Java `DBOptions` and `ColumnFamilyDescriptor` objects. It bridges native option-file parsing with Java option wrappers.

## Important APIs and types

`loadLatestOptions(ConfigOptions, String, DBOptions, List<ColumnFamilyDescriptor>)` loads the newest options file from a DB directory. `loadOptionsFromFile(ConfigOptions, String, DBOptions, List<ColumnFamilyDescriptor>)` loads a specified file. `getLatestOptionsFileName(String, Env)` returns the selected options file path. Private `loadTableFormatConfig(...)` reads native table-format config for each returned column-family option.

## Control flow

Public load methods call native parsing functions with config and DB option handles plus the descriptor list, then iterate descriptors and call `ColumnFamilyOptions.setFetchedTableFormatConfig(readTableFormatConfig(...))`. The class cannot be instantiated.

## State and persistence behavior

The utility owns no state. It reads persisted OPTIONS files and mutates caller-provided `DBOptions` and descriptor lists. Pointer options generally get defaults after loading, with special support for block-based table options excluding pointer sub-options such as block cache and flush-block policy.

## Dependencies and integration points

It depends on `ConfigOptions`, `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyOptions`, `Env`, `TableFormatConfig`, and native option parsing. It is used by applications that reopen DBs from generated OPTIONS files.

## Risks and test signals

Risks include incomplete pointer-option reconstruction, table factory type loss, and caller confusion about defaults that must be reattached manually. Tests should load latest and explicit OPTIONS files, verify column-family descriptors and fetched table format configs, cover missing or malformed files, and validate custom pointer options are documented as defaults.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptionsUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PerfContext.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PerfContext.java research

## Purpose

`PerfContext` is the Java wrapper for RocksDB's per-thread performance counters. It exposes counters and timings for reads, writes, cache activity, iterators, blob reads, environment operations, transaction locks, encryption, CPU time, and async seek behavior.

## Important APIs and types

The protected constructor wraps a native handle. `reset()` clears counters. Dozens of getters call native methods and return `long` counters or nanosecond timings. `toString()` delegates to `toString(true)`, while `toString(boolean excludeZeroCounters)` asks native code for a formatted summary. `disposeInternal()` intentionally does nothing because the perf context is valid for the application lifetime.

## Control flow

Java code obtains a `PerfContext` from higher-level RocksDB APIs, performs DB operations with perf collection enabled through `PerfLevel`, then reads counters or calls `toString`. Every getter is a direct JNI call into the native context.

## State and persistence behavior

State lives in native thread-local or process-managed perf context memory. It is transient diagnostic state and does not persist to DB files. `reset()` affects only the active context counters.

## Dependencies and integration points

It depends on `RocksObject` for handle storage but bypasses normal disposal. It integrates with `PerfLevel`, DB read/write/iterator paths, block cache, blob cache, secondary cache, memtables, Env wrappers such as timed or encrypted envs, and transaction lock managers.

## Risks and test signals

Risks include counters requiring the correct `PerfLevel`, thread-local interpretation, stale data if not reset, and native method drift as counters are added or renamed. Tests should enable each relevant perf level, reset before controlled operations, assert non-zero expected counters for gets/iterators/writes/cache hits, verify `excludeZeroCounters`, and ensure close/dispose is harmless.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PerfContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PerfLevel.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PerfLevel.java research

## Purpose

`PerfLevel` exposes native RocksDB performance-counter collection levels to Java. It lets callers trade overhead for count, time, CPU-time, and mutex timing detail.

## Important APIs and types

Constants are `UNINITIALIZED`, `DISABLE`, `ENABLE_COUNT`, `ENABLE_TIME_EXCEPT_FOR_MUTEX`, `ENABLE_TIME_AND_CPU_TIME_EXCEPT_FOR_MUTEX`, `ENABLE_TIME`, and deprecated `OUT_OF_BOUNDS`. `getValue()` returns the native byte. `getPerfLevel(byte)` decodes a byte or throws `IllegalArgumentException`.

## Control flow

Java code passes `getValue()` to native perf-level setters and decodes native bytes through `getPerfLevel()`. `PerfContext` counters then reflect the configured collection level.

## State and persistence behavior

The enum stores only immutable bytes. Perf level changes runtime diagnostics only and has no persistence effect except any external logging performed by callers.

## Dependencies and integration points

It integrates with perf context APIs and native RocksDB perf instrumentation. The deprecated out-of-bounds constant exists only for C++ API parity.

## Risks and test signals

The typo in the exception message is harmless but visible. The important risk is byte parity. Tests should cover all mappings, invalid-byte rejection, deprecated constant behavior, and counter differences between disabled/count/time levels.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PerfLevel.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PersistentCache.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PersistentCache.java research

## Purpose

`PersistentCache` wraps RocksDB's persistent read cache, intended for caching I/O pages on persistent media such as SSD or NVM.

## Important APIs and types

The constructor accepts `Env`, cache path, size, `Logger`, and `optimizedForNvm`, then calls native `newPersistentCache(...)`. Disposal calls `disposeInternalJni(handle)`.

## Control flow

Construction creates the native persistent cache or throws `RocksDBException`. Java code then passes the cache to table or DB configuration paths that support persistent cache use. There are no Java getters or mutators in this wrapper.

## State and persistence behavior

The object owns a native cache handle. Unlike `LRUCache`, cache data can live on persistent storage under the configured path, but it remains a cache: DB correctness must not depend on cached contents.

## Dependencies and integration points

It depends on `Env`, `Logger`, `RocksObject`, and native persistent-cache creation. It integrates with table reader/block cache configuration outside this file.

## Risks and test signals

Risks include path permissions, size validation, logger lifetime, native memory/resource cleanup, and cache contents surviving process restarts in ways tests must account for. Tests should create a cache in a temp directory, attach it to read options/table config where supported, verify reads populate/hit it, and close it cleanly.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PersistentCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PlainTableConfig.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PlainTableConfig.java research

## Purpose

`PlainTableConfig` configures RocksDB's plain-table SST format for Java. Plain tables target low-latency memory or very low-latency media and support prefix hashing.

## Important APIs and types

Defaults include variable-length keys, 10 bloom bits per key, hash table ratio 0.75, index sparseness 16, no huge TLB, plain encoding, full-scan mode disabled, and store-index-in-file disabled. Fluent setters/getters cover key size, bloom bits, hash table ratio, index sparseness, huge page TLB size, `EncodingType`, full scan mode, and storing index/bloom in the file. `newTableFactoryHandle()` creates the native table factory from the stored fields.

## Control flow

Applications configure fields in Java, pass the config to `Options.setTableFormatConfig(...)`, and `Options` calls `newTableFactoryHandle()`. Native RocksDB then builds or reads plain-table SSTs according to these settings.

## State and persistence behavior

The object stores Java configuration fields. Encoding type and store-index choices can affect newly written SST files and may be persisted in file metadata. Existing files can coexist with different encoding choices according to the comments.

## Dependencies and integration points

It extends `TableFormatConfig`, depends on `EncodingType`, and integrates with `Options.setTableFormatConfig`. It interacts with prefix extractor choices, bloom filters, hash-table sizing, mmap/read behavior, and table factory creation in native RocksDB.

## Risks and test signals

Risks include invalid ratios or sizes being rejected only by native code, huge-page configuration depending on OS setup, and performance regressions from sparse or disabled indexes. Tests should cover default values, fluent setter round-trips, DB open/write/read using plain tables, fixed and variable key sizes, full-scan mode, store-index-in-file reopen behavior, and native validation failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PlainTableConfig.java -->
