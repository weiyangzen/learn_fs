# Research: subset-b-008662

Grouped research for RocksDB Java bindings under `sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb`. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileMetaData.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileMetaData.java

## Purpose
`SstFileMetaData` is an immutable Java data transfer object describing one SST file as reported by native RocksDB metadata APIs. It captures identity, path, file size, key range, sequence number range, read/compaction state, entry/deletion counts, and optional full-file checksum bytes.

## Important APIs and Types
The protected constructor is intended for JNI construction and stores all supplied values directly. Public accessors include `fileName()`, `path()`, `size()`, `smallestSeqno()`, `largestSeqno()`, `smallestKey()`, `largestKey()`, `numReadsSampled()`, `beingCompacted()`, `numEntries()`, `numDeletions()`, and `fileChecksum()`.

## Control Flow
There is no active control flow beyond construction and simple field access. Native code creates instances with already-collected metadata; Java callers consume the read-only getters.

## State and Persistence Behavior
The object mirrors persistent SST-file metadata but does not persist anything itself. `byte[]` fields are stored and returned directly, so Java callers can mutate arrays that conceptually represent immutable metadata.

## Dependencies and Integration Points
The class integrates with RocksDB JNI metadata conversion, typically from DB/file property APIs that enumerate live files. It has no superclass and no direct native methods.

## Risks and Test Signals
Tests should verify JNI field ordering, optional checksum behavior, null/empty key handling, and that read state such as `beingCompacted` and read-sampling count reflects native metadata. The main risk is aliasing of `byte[]` fields because defensive copies are intentionally omitted.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileMetaData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileReader.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileReader.java

## Purpose
`SstFileReader` wraps the native RocksDB `SstFileReader` so Java code can open and inspect external SST files without opening them as a database.

## Important APIs and Types
The constructor takes `Options` and calls native `newSstFileReader`. Public methods are `open(String filePath)`, `newIterator(ReadOptions)`, `verifyChecksum()`, and `getTableProperties()`. It returns `SstFileReaderIterator` and `TableProperties`.

## Control Flow
Construction allocates the native reader. `open` binds the reader to an SST file path. `newIterator` asserts ownership, asks native code for an iterator handle, and wraps it with this reader as the owning parent. Checksum and property calls delegate directly to native code and throw `RocksDBException` on native failures.

## State and Persistence Behavior
The Java object owns a native reader handle and releases it through `disposeInternalJni`. The underlying SST file is read-only; this class does not mutate the file, except that failed reads/checksum verification expose native status.

## Dependencies and Integration Points
It extends `RocksObject`, uses `Options`, `ReadOptions`, `SstFileReaderIterator`, `TableProperties`, and `RocksDBException`, and depends on matching JNI implementations.

## Risks and Test Signals
Tests should cover opening valid/invalid SST paths, checksum failure propagation, iterator lifetime after reader close, and table-property parity with files written by `SstFileWriter`. The class comment appears copied from transaction iterators and mentions uncommitted transaction keys, which is misleading for an SST-file reader.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileReaderIterator.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileReaderIterator.java

## Purpose
`SstFileReaderIterator` is the iterator wrapper used by `SstFileReader` to traverse key/value entries in an opened SST file.

## Important APIs and Types
It extends `AbstractRocksIterator<SstFileReader>`. Public APIs add `key()`, `key(ByteBuffer)`, `value()`, and `value(ByteBuffer)` while inherited iterator movement/status APIs are implemented through native overrides such as `seekToFirst0`, `seek0`, `next0`, `prev0`, `refresh0`, and `status0`.

## Control Flow
The constructor binds a native iterator handle to the owning reader. Movement methods are inherited and routed to JNI. Array-returning key/value calls allocate Java byte arrays from native slices. Buffer overloads choose direct-buffer JNI paths when `ByteBuffer.isDirect()` is true and array-backed paths otherwise, then adjust the buffer limit to expose the bytes actually copied.

## State and Persistence Behavior
The iterator owns a native iterator handle and is valid only while the associated native resources remain live. It does not persist state; current position is native state. Returned array data is copied, while buffer overloads write into caller-provided buffers.

## Dependencies and Integration Points
It depends on `AbstractRocksIterator`, `SstFileReader`, `ByteBuffer`, and the native SST iterator implementation. It is created only by `SstFileReader.newIterator`.

## Risks and Test Signals
Tests should exercise direct and heap `ByteBuffer` reads, too-small buffers and returned required sizes, seeking and reverse iteration, `status()` error propagation, and behavior after close. A notable risk is heap buffer handling assumes accessible backing arrays; read-only or non-array heap buffers would fail at runtime.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileReaderIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileWriter.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileWriter.java

## Purpose
`SstFileWriter` wraps native external SST creation. It lets Java callers build an SST file with sequence number zero that can later be ingested into a RocksDB instance.

## Important APIs and Types
Construction takes `EnvOptions` and `Options`. Public methods include `open(String)`, overloaded `put` for `Slice`, `DirectSlice`, `ByteBuffer`, and `byte[]`, overloaded `merge`, overloaded `delete`, `finish()`, and `fileSize()`.

## Control Flow
The constructor allocates a native writer. `open` starts output to a file path. Mutating calls delegate to native writer operations. Direct `ByteBuffer` `put` asserts both buffers are direct, passes position/remaining to native code, then advances both positions to their limits. `finish` closes/finalizes the SST. `fileSize` reports native writer size.

## State and Persistence Behavior
The object owns a native writer handle. State transitions are native: allocated, opened, receiving sorted records, and finished. The class writes persistent SST data to the filesystem via the native writer but stores no Java-side record data.

## Dependencies and Integration Points
It extends `RocksObject`, depends on `EnvOptions`, `Options`, `Slice`, `DirectSlice`, `ByteBuffer`, and `RocksDBException`, and integrates with external file ingestion workflows elsewhere in RocksJava.

## Risks and Test Signals
Tests should check sorted-key requirements, duplicate keys, merge/delete records, file-size updates, missing `finish`, invalid file paths, and ingestion compatibility. The `ByteBuffer` `put` path relies on Java assertions for directness, so with assertions disabled an invalid buffer can reach JNI; tests should cover invalid buffer handling at native boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstPartitionerFactory.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstPartitionerFactory.java

## Purpose
`SstPartitionerFactory` is the abstract Java handle type for native SST partitioner factories used from `ColumnFamilyOptions`.

## Important APIs and Types
It extends `RocksObject` and exposes only a protected constructor accepting a native handle. Concrete subclasses provide allocation and disposal.

## Control Flow
There is no behavior beyond `RocksObject` initialization. Native factory handles are passed through subclasses to options code.

## State and Persistence Behavior
The only state is the owned native handle. It does not persist data and does not define partitioning itself.

## Dependencies and Integration Points
It integrates with `ColumnFamilyOptions` and concrete factories such as `SstPartitionerFixedPrefixFactory`.

## Risks and Test Signals
Tests should verify option wiring keeps the factory alive long enough for native use and that subclass disposal is correct. The base class is intentionally minimal, so most risk sits in native factory implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstPartitionerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstPartitionerFixedPrefixFactory.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstPartitionerFixedPrefixFactory.java

## Purpose
`SstPartitionerFixedPrefixFactory` creates a native SST partitioner factory that partitions SST output by a fixed-length key prefix.

## Important APIs and Types
The public constructor takes `prefixLength`, calls `newSstPartitionerFixedPrefixFactory0`, and inherits the handle contract from `SstPartitionerFactory`. `disposeInternal` releases the native factory through JNI.

## Control Flow
Construction delegates allocation to native code. Disposal delegates native cleanup. Actual partition decisions happen in C++.

## State and Persistence Behavior
The Java object owns only the factory handle. Prefix length is not retained in Java after construction; native state owns it.

## Dependencies and Integration Points
It depends on `SstPartitionerFactory`, `RocksObject`, and JNI. It is meant to be attached to column-family configuration that controls SST writing and compaction output.

## Risks and Test Signals
Tests should validate zero/negative/large prefix lengths, option serialization into native column-family options, and whether generated SST boundaries match fixed prefixes. Since Java does not validate input, native validation is the safety boundary.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstPartitionerFixedPrefixFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StateType.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StateType.java

## Purpose
`StateType` maps native RocksDB thread-state identifiers to Java enum values for thread-status reporting.

## Important APIs and Types
Values are `STATE_UNKNOWN` and `STATE_MUTEX_WAIT`, each with a byte value. Package-private `getValue()` returns the JNI code, and static `fromValue(byte)` maps a native byte back to the enum or throws.

## Control Flow
Mapping is a simple linear scan over enum values. Unknown values fail fast with `IllegalArgumentException`.

## State and Persistence Behavior
There is no mutable state or persistence. Enum byte values must remain synchronized with native RocksDB state constants.

## Dependencies and Integration Points
`ThreadStatus` uses `StateType.fromValue` during JNI object construction and `ThreadStatus.getStateName` passes `getValue()` back to native helpers.

## Risks and Test Signals
Tests should cover all native values, unknown-value failures, and version drift when native adds new states. Missing enum updates can break thread-status construction for newer native libraries.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StateType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Statistics.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Statistics.java

## Purpose
`Statistics` is the Java owner/wrapper for RocksDB's native statistics object, exposing ticker counters, histograms, stats-level configuration, reset, copying, and formatted output.

## Important APIs and Types
Constructors allocate empty statistics, copy another `Statistics`, or allocate/copy while ignoring selected `HistogramType` values. Public APIs include `statsLevel()`, `setStatsLevel(StatsLevel)`, `getTickerCount(TickerType)`, `getAndResetTickerCount(TickerType)`, `getHistogramData(HistogramType)`, `getHistogramString(HistogramType)`, `reset()`, and `toString()`.

## Control Flow
Public calls assert ownership then pass enum byte values to native functions. Constructors load the RocksDB JNI library before allocation. `toArrayValues` converts `EnumSet<HistogramType>` into native byte identifiers.

## State and Persistence Behavior
The native statistics object accumulates in-memory counters and histograms for a DB/options configuration. It is not persisted by this wrapper. `reset` clears native statistics, and `getAndResetTickerCount` atomically observes and clears one ticker.

## Dependencies and Integration Points
It extends `RocksObject` and integrates with `DBOptions#statistics()`, `Options`/`DBOptions` attachment, `TickerType`, `HistogramType`, `HistogramData`, and `StatsLevel`.

## Risks and Test Signals
Tests should verify library loading, copy semantics, ignored histogram behavior, enum byte mapping, reset behavior, and use-after-close failures. Performance-sensitive tests should distinguish stats levels because `StatsLevel.ALL` enables expensive timing in mutex paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Statistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatisticsCollector.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatisticsCollector.java

## Purpose
`StatisticsCollector` periodically samples one or more `Statistics` instances and invokes user callbacks for every ticker and histogram.

## Important APIs and Types
The constructor takes a `List<StatsCollectorInput>` and a polling interval in milliseconds. `start()` submits the collector loop to a single-thread executor. `shutDown(int)` stops the loop, interrupts executor work, and waits for termination.

## Control Flow
The private `collectStatistics()` runnable loops while `_isRunning`, checks interruption, iterates each input, emits all `TickerType` values except `TICKER_ENUM_MAX`, emits all `HistogramType` values except `HISTOGRAM_ENUM_MAX`, then sleeps for the configured interval. Interrupted sleeps restore interrupt state and exit; other exceptions are wrapped in `RuntimeException`.

## State and Persistence Behavior
State is in-memory: input list, executor, interval, and volatile running flag. The collector does not persist samples; persistence is delegated to callback implementations. Statistics objects must remain live until shutdown finishes.

## Dependencies and Integration Points
It depends on `StatsCollectorInput`, `StatisticsCollectorCallback`, `Statistics`, `TickerType`, `HistogramType`, `HistogramData`, and Java concurrency utilities.

## Risks and Test Signals
Tests should cover shutdown before statistics disposal, interruption, callback exceptions, empty input lists, interval timing, and exclusion of enum sentinels. A key risk is that callback thread safety is not guaranteed, and a thrown callback exception kills the collector task.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatisticsCollector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatisticsCollectorCallback.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatisticsCollectorCallback.java

## Purpose
`StatisticsCollectorCallback` defines the callback contract used by `StatisticsCollector` to deliver sampled ticker and histogram values.

## Important APIs and Types
The interface declares `tickerCallback(TickerType, long)` and `histogramCallback(HistogramType, HistogramData)`.

## Control Flow
Implementations are invoked synchronously on the collector's executor thread for each sampled metric.

## State and Persistence Behavior
The interface owns no state. Implementations decide whether to store, aggregate, export, or discard metric samples.

## Dependencies and Integration Points
It depends on RocksDB metric enums and `HistogramData`; `StatsCollectorInput` pairs a callback with a `Statistics` object.

## Risks and Test Signals
Tests should validate callback ordering only if callers depend on it and should exercise implementations under concurrent collectors. The contract states thread safety is the user's responsibility when a callback instance is shared.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatisticsCollectorCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatsCollectorInput.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatsCollectorInput.java

## Purpose
`StatsCollectorInput` is a small holder pairing one `Statistics` object with the callback that should receive samples from it.

## Important APIs and Types
The constructor stores `Statistics` and `StatisticsCollectorCallback`; getters are `getStatistics()` and `getCallback()`.

## Control Flow
There is no branching or native logic. `StatisticsCollector` reads each input in its polling loop.

## State and Persistence Behavior
It is immutable after construction but stores references directly. It performs no lifecycle management; callers must keep the statistics and callback valid.

## Dependencies and Integration Points
It integrates only with `StatisticsCollector` and the callback interface.

## Risks and Test Signals
Tests should cover null handling expectations and lifecycle hazards, especially disposing a `Statistics` instance before collector shutdown. If nulls are passed, failures occur later in the collector loop rather than at construction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatsCollectorInput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatsLevel.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatsLevel.java

## Purpose
`StatsLevel` maps RocksDB statistics collection levels into Java, controlling how much timing/counter work the native engine performs.

## Important APIs and Types
Values are `EXCEPT_DETAILED_TIMERS`, `EXCEPT_TIME_FOR_MUTEX`, and `ALL`, each with a byte mapping. `getValue()` returns the native byte and `getStatsLevel(byte)` maps native bytes back to Java.

## Control Flow
Reverse mapping linearly scans enum values and throws `IllegalArgumentException` on unknown input.

## State and Persistence Behavior
No mutable state exists. Stats level affects native in-memory statistics behavior when applied through `Statistics.setStatsLevel`.

## Dependencies and Integration Points
`Statistics` uses it for `statsLevel()` and `setStatsLevel()`. Documentation warns that collecting mutex timings can reduce scalability.

## Risks and Test Signals
Tests should cover every byte mapping, invalid byte failures, and performance behavior at `ALL`. Native/Java enum drift would break `Statistics.statsLevel()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatsLevel.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Status.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Status.java

## Purpose
`Status` is the Java serializable representation of RocksDB native status values, primarily attached to `RocksDBException`.

## Important APIs and Types
The class stores `Code`, optional `SubCode`, and optional state string. Public APIs are getters, `getCodeString()`, `equals`, and `hashCode`. `Code` maps high-level status values such as `Ok`, `NotFound`, `Corruption`, `InvalidArgument`, `IOError`, `Busy`, `TimedOut`, and `TryAgain`. `SubCode` maps more specific causes such as `LockTimeout`, `NoSpace`, `Deadlock`, `StaleFile`, and `MemoryLimit`.

## Control Flow
JNI can construct status through a private byte-based constructor that calls `Code.getCode` and `SubCode.getSubCode`. Reverse mapping methods linearly scan enum values and throw for unknown bytes. `getCodeString` appends a non-`None` subcode in parentheses.

## State and Persistence Behavior
The object is immutable and serializable. It does not persist native state; it snapshots status information into Java fields.

## Dependencies and Integration Points
It integrates with `RocksDBException` and many transactional/event DTOs such as `TableFileCreationInfo` and `TableFileDeletionInfo`. Comments explicitly require synchronization with native `status.h` and JNI portal mapping.

## Risks and Test Signals
Tests should cover byte mappings, serialization compatibility, null subcodes, code-string formatting, equality, and behavior for future native codes. The main risk is enum drift between Java, native headers, and JNI conversion code.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Status.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StringAppendOperator.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StringAppendOperator.java

## Purpose
`StringAppendOperator` exposes RocksDB's built-in string-append merge operator to Java.

## Important APIs and Types
It extends `MergeOperator`. Constructors select a comma delimiter by default, a single `char` delimiter, or a `String` delimiter. Native allocation uses `newSharedStringAppendOperator`.

## Control Flow
Construction creates a shared native merge-operator handle. Disposal releases it through `disposeInternalJni`.

## State and Persistence Behavior
The Java object owns a native merge operator. Merge effects are persisted only when attached to options and used by database writes/compaction; the wrapper stores no values itself.

## Dependencies and Integration Points
It integrates with column-family/options merge-operator configuration and native merge implementation.

## Risks and Test Signals
Tests should verify delimiter overloads, UTF-16 to native string handling, lifecycle when attached to options, and merge results across put/merge/get/compaction. Native ownership semantics are the main integration risk.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StringAppendOperator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFileCreationBriefInfo.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFileCreationBriefInfo.java

## Purpose
`TableFileCreationBriefInfo` is an event DTO for table-file creation callbacks, carrying basic identity and cause data.

## Important APIs and Types
The protected JNI constructor stores database name, column-family name, file path, job id, and maps a reason byte to `TableFileCreationReason`. Public getters expose each field, and the class implements `equals`, `hashCode`, and `toString`.

## Control Flow
Construction maps native reason bytes through `TableFileCreationReason.fromValue`; invalid bytes throw immediately. All other behavior is value access/comparison.

## State and Persistence Behavior
It snapshots native event metadata into immutable Java fields. It does not persist or manage table files.

## Dependencies and Integration Points
It is used directly for brief listener notifications and as the superclass for `TableFileCreationInfo`.

## Risks and Test Signals
Tests should cover all reason mappings, equality/hash/toString, null field behavior, and callback construction from JNI. Enum drift or bad native reason bytes will fail event delivery.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFileCreationBriefInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFileCreationInfo.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFileCreationInfo.java

## Purpose
`TableFileCreationInfo` is the detailed table-file creation event DTO, extending the brief info with file size, table properties, and operation status.

## Important APIs and Types
The protected JNI constructor forwards DB/cf/path/job/reason to `TableFileCreationBriefInfo` and stores `fileSize`, `TableProperties`, and `Status`. Getters expose these detailed fields; `equals`, `hashCode`, and `toString` are overridden.

## Control Flow
Construction performs superclass reason mapping, then stores detailed fields. Access is passive afterward.

## State and Persistence Behavior
It snapshots creation-event data; it does not modify created files or table properties. `TableProperties` and `Status` are held by reference.

## Dependencies and Integration Points
It integrates with RocksDB event listeners and table-property conversion. It depends on `TableFileCreationBriefInfo`, `TableProperties`, `Status`, and `TableFileCreationReason`.

## Risks and Test Signals
Tests should cover JNI construction, detailed status propagation on failed creation, and equality behavior. A notable risk is that `equals` and `hashCode` only compare subclass fields and ignore inherited DB name, column family, file path, job id, and reason, so two distinct file events can compare equal if their detailed fields match.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFileCreationInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFileCreationReason.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFileCreationReason.java

## Purpose
`TableFileCreationReason` maps native reasons for SST/table-file creation into Java enum values.

## Important APIs and Types
Values are `FLUSH`, `COMPACTION`, `RECOVERY`, and `MISC`. Package-private `getValue()` returns the native byte and static `fromValue(byte)` performs reverse mapping.

## Control Flow
Reverse mapping scans enum values and throws `IllegalArgumentException` on unknown bytes.

## State and Persistence Behavior
There is no mutable state. Values describe why persistent table files were created but do not manage files.

## Dependencies and Integration Points
`TableFileCreationBriefInfo` and `TableFileCreationInfo` use it when converting native event payloads.

## Risks and Test Signals
Tests should verify all mappings and failure behavior for unknown native values. Native additions must be mirrored here or Java event construction can fail.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFileCreationReason.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFileDeletionInfo.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFileDeletionInfo.java

## Purpose
`TableFileDeletionInfo` is a value object describing a table-file deletion event.

## Important APIs and Types
It stores database name, deleted file path, job id, and `Status`. Public getters expose all fields, and it implements `equals`, `hashCode`, and `toString`.

## Control Flow
The package-private constructor is intended for JNI and testing. There is no native method or branch logic in the class itself.

## State and Persistence Behavior
It snapshots deletion-event data. The actual file deletion is performed by RocksDB native code; this class does not persist or delete anything.

## Dependencies and Integration Points
It integrates with event listener callbacks and uses `Status` to represent success or failure.

## Risks and Test Signals
Tests should cover event construction, failure status propagation, equality/hash/toString, and null handling. Since constructor access is package-private, JNI signature and tests must remain in sync.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFileDeletionInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFilter.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFilter.java

## Purpose
`TableFilter` is a Java callback interface that lets scans decide whether a table should be scanned based on `TableProperties`.

## Important APIs and Types
It declares one method: `boolean filter(TableProperties tableProperties)`.

## Control Flow
During iterator/table scan setup, native or Java bridge code can call `filter` with each table's properties. Returning `false` skips that table for iterator scans; point lookups are unaffected.

## State and Persistence Behavior
The interface has no state. Implementations may carry arbitrary state, but the filter itself only influences read-path table selection.

## Dependencies and Integration Points
It depends on `TableProperties` and is used by read/iterator options that support table-level filtering.

## Risks and Test Signals
Tests should verify that filters skip iterator table access, do not affect point lookups, receive correct table properties, and propagate callback exceptions as expected. Implementations must be efficient because they can run on scan setup paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFormatConfig.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFormatConfig.java

## Purpose
`TableFormatConfig` is the abstract base for configuring a RocksDB table factory from Java.

## Important APIs and Types
It declares protected abstract `newTableFactoryHandle()`, which concrete table-format configurations implement to allocate a native table-factory handle.

## Control Flow
The method is intended to be called by `Options.setTableFormatConfig()`, which creates a native shared pointer to the corresponding C++ table factory.

## State and Persistence Behavior
The base class owns no state. Concrete subclasses hold configuration that affects future SST/table file format and layout.

## Dependencies and Integration Points
It integrates with `Options.setTableFormatConfig()` and concrete formats such as block-based or plain-table configs elsewhere in RocksJava.

## Risks and Test Signals
Tests should verify concrete subclass handles, options ownership/lifetime, and table files generated with each config. Because the method is protected and native ownership is external, lifecycle tests are important.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFormatConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableProperties.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableProperties.java

## Purpose
`TableProperties` is the Java immutable snapshot of read-only SST/table properties exposed by RocksDB.

## Important APIs and Types
The package-private constructor accepts native-supplied values for data/index/filter sizes, key/value raw sizes, block and entry counts, delete/merge/range-delete counts, format metadata, column-family identity, creation/oldest-key times, compression estimates, external SST global sequence offset, policy/comparator/operator names, user-collected properties, and readable properties. Getters expose each field. Equality and hash code compare all fields, including `columnFamilyName` with `Arrays.equals`.

## Control Flow
The class performs no computation beyond storing constructor values and returning them. Equality performs a field-by-field comparison; hash code combines object fields and the byte-array hash.

## State and Persistence Behavior
It is a Java snapshot of persistent table metadata but does not persist or mutate anything. `columnFamilyName`, `userCollectedProperties`, and `readableProperties` are stored and returned directly, so caller mutation can alter the apparent value object.

## Dependencies and Integration Points
It is returned by `SstFileReader.getTableProperties`, table properties APIs, event DTOs, and table filters. It references `IndexType#kTwoLevelIndexSearch` in documentation.

## Risks and Test Signals
Tests should validate JNI constructor field ordering, null optional strings, map conversion, equality/hash behavior, compression estimate fields, external SST global seqno offset, and direct-return mutability. A risk is value-object aliasing through arrays/maps; another is that new native table properties require constructor and equality updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableProperties.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TablePropertiesCollectorFactory.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TablePropertiesCollectorFactory.java

## Purpose
`TablePropertiesCollectorFactory` is the Java handle wrapper for native table-properties collector factories, including RocksDB's compact-on-deletion collector.

## Important APIs and Types
The abstract class extends `RocksObject` with a private native-handle constructor. `NewCompactOnDeletionCollectorFactory(long sliding_window_size, long deletion_trigger, double deletion_ratio)` allocates a native compact-on-deletion factory and returns an anonymous subclass that deletes it. `newWrapper(long)` wraps an existing native handle for internal use.

## Control Flow
Factory construction delegates to native allocation. The returned anonymous subclass implements `disposeInternal` by calling `deleteCompactOnDeletionCollectorFactory`.

## State and Persistence Behavior
State is a native factory handle. When attached to options, native collectors can add table properties and influence compaction behavior, but this Java wrapper stores no table data.

## Dependencies and Integration Points
It integrates with column-family/table factory options and native collector APIs.

## Risks and Test Signals
Tests should cover parameter validation, disposal, option attachment lifetime, compaction triggered by deletion ratio/window settings, and internal wrapper ownership. A risk is that `newWrapper` uses the compact-on-deletion deleter for any wrapped handle, so it must only wrap compatible native handles.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TablePropertiesCollectorFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ThreadStatus.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ThreadStatus.java

## Purpose
`ThreadStatus` represents a native RocksDB thread-status snapshot for Java monitoring and diagnostics.

## Important APIs and Types
The private JNI constructor stores thread id, `ThreadType`, DB name, column-family name, `OperationType`, elapsed microseconds, `OperationStage`, operation properties, and `StateType`. Public getters expose fields. Static helpers call native functions to translate thread type, operation, elapsed time, stage, operation property names/values, and state into readable forms.

## Control Flow
JNI construction maps byte identifiers through enum `fromValue` methods, failing on unknown values. Static formatting/interpreting APIs pass enum byte values and property arrays back to native helper functions.

## State and Persistence Behavior
It is an immutable snapshot of current thread activity. It does not persist monitoring data. The `long[] operationProperties` array is returned directly, so callers can mutate the snapshot.

## Dependencies and Integration Points
It depends on `ThreadType`, `OperationType`, `OperationStage`, `StateType`, and native monitoring helpers. It is consumed by APIs that expose RocksDB thread status.

## Risks and Test Signals
Tests should cover enum mapping drift, null DB/CF names, property interpretation for each operation type, elapsed-time formatting, and direct array aliasing. Native additions to operations/stages/states must be mirrored in Java enums or construction will fail.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ThreadStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ThreadType.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ThreadType.java

## Purpose
`ThreadType` maps native RocksDB thread-pool/user-thread categories to Java enum values.

## Important APIs and Types
Values are `HIGH_PRIORITY`, `LOW_PRIORITY`, `USER`, and `BOTTOM_PRIORITY`. Package-private `getValue()` returns the native byte and static `fromValue(byte)` maps back.

## Control Flow
Mapping is a linear enum scan with `IllegalArgumentException` for unknown bytes.

## State and Persistence Behavior
There is no mutable state. Values describe monitoring snapshots only.

## Dependencies and Integration Points
`ThreadStatus` uses it during construction and for human-readable native name lookup.

## Risks and Test Signals
Tests should cover all mappings and unknown values. The primary risk is native enum expansion without Java update.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ThreadType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TickerType.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TickerType.java

## Purpose
`TickerType` is the large Java enum mapping RocksDB native ticker counters into byte identifiers usable through JNI statistics APIs.

## Important APIs and Types
The enum covers counters for block cache, secondary/compressed cache, Bloom filters, persistent/simulated cache, memtable and get hits, compaction key drops, write/read byte counts, iterator activity, WAL activity, write grouping, compaction/flush bytes, compression/decompression, row cache, read amplification, rate limiting, BlobDB, transaction overhead, delete scheduler, error handler, backup, remote compaction, tiered storage, last-level/non-last-level reads and seeks, checksum verification, async read, timestamp filtering, FIFO compactions, prefetch, corruption retry, WBWI ingest, user-defined index load failures, multiscans, read-path tombstone conversion, manifest validation, and `TICKER_ENUM_MAX`.

## Control Flow
Each enum stores a byte value. `getTickerType(byte)` scans all enum values and returns the matching type or throws. `Statistics` and `StatisticsCollector` use `getValue()` to request native counts.

## State and Persistence Behavior
No mutable state exists. Tickers represent in-memory native statistics counters; persistence/export is handled by callers or callbacks.

## Dependencies and Integration Points
It is used by `Statistics.getTickerCount`, `Statistics.getAndResetTickerCount`, and `StatisticsCollector`. The file documents an important compatibility decision: native ticker values are wider than Java signed bytes, so newer mappings use the negative byte range instead of preserving native numeric identity.

## Risks and Test Signals
Tests should verify every byte value is unique, sentinel exclusion in collectors, reverse mapping, and synchronization with native ticker mappings in JNI portal code. The biggest risk is byte-space exhaustion or drift when native adds counters; `TICKER_ENUM_MAX` is not numerically last because compatibility requires stable assigned bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TickerType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TimedEnv.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TimedEnv.java

## Purpose
`TimedEnv` wraps a base `Env` with native timing instrumentation for filesystem operations, reporting timings through RocksDB `PerfContext` variables.

## Important APIs and Types
The constructor takes a base `Env` and calls native `createTimedEnv`. Disposal releases the timed environment through `disposeInternalJni`.

## Control Flow
Construction passes the base environment handle to native code. All timed filesystem behavior is implemented by the native environment wrapper.

## State and Persistence Behavior
The Java object owns the native timed environment. The base environment must remain live while the timed wrapper is in use. No filesystem data is persisted by this class itself.

## Dependencies and Integration Points
It extends `Env` and integrates with options/configuration paths that accept an environment handle. It reports to `PerfContext` rather than Java fields.

## Risks and Test Signals
Tests should cover base-env lifetime, disposal ordering, timing values appearing in `PerfContext`, and behavior with default/custom envs. The main lifecycle risk is closing the base environment too early.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TimedEnv.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TraceOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TraceOptions.java

## Purpose
`TraceOptions` configures trace capture, currently by bounding maximum trace file size.

## Important APIs and Types
The default constructor sets `maxTraceFileSize` to 64 GiB. The alternate constructor accepts a byte count. `getMaxTraceFileSize()` exposes the value.

## Control Flow
There is no native logic in this class. `RocksDB.startTrace(TraceOptions, AbstractTraceWriter)` consumes the value when trace writing starts.

## State and Persistence Behavior
It is an immutable value object. It does not write traces itself; it only constrains trace output size in the tracing subsystem.

## Dependencies and Integration Points
It integrates with `RocksDB#startTrace` and trace-writer abstractions such as `AbstractTraceWriter`/`TraceWriter`.

## Risks and Test Signals
Tests should cover default size, custom sizes, zero/negative handling at consuming APIs, and enforcement by trace writers. Since Java does no validation, native/startTrace validation must guard nonsensical sizes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TraceOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TraceWriter.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TraceWriter.java

## Purpose
`TraceWriter` is a Java interface for exporting RocksDB trace records to an arbitrary sink.

## Important APIs and Types
It declares `write(Slice data)`, `closeWriter()`, and `getFileSize()`. `write` and close can throw `RocksDBException`.

## Control Flow
Trace infrastructure calls `write` for each trace data slice, queries size through `getFileSize`, and calls `closeWriter` to finish the sink.

## State and Persistence Behavior
The interface owns no state. Implementations define persistence behavior, such as writing to files, streams, or remote systems. `getFileSize` is part of trace-size limiting.

## Dependencies and Integration Points
It depends on `Slice` and `RocksDBException` and integrates with tracing APIs via `AbstractTraceWriter`.

## Risks and Test Signals
Tests for implementations should cover slice lifetime, partial write failures, close failures, size accounting, and idempotent close behavior. Implementations must not retain a native `Slice` beyond its valid callback lifetime unless copied.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TraceWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Transaction.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Transaction.java

## Purpose
`Transaction` is the main Java wrapper for RocksDB optimistic and pessimistic transactions. It exposes transaction lifecycle, snapshot isolation, reads including uncommitted writes, conflict-tracking reads, write-batch mutation, savepoints, two-phase commit preparation, diagnostics, and native transaction metadata.

## Important APIs and Types
Lifecycle APIs include `setSnapshot`, `setSnapshotOnNextOperation`, `getSnapshot`, `clearSnapshot`, `prepare`, `commit`, `rollback`, `setSavePoint`, and `rollbackToSavePoint`. Read APIs include overloaded `get`, `multiGetAsList`, deprecated array `multiGet`, `getForUpdate`, and `multiGetForUpdateAsList`. Mutation APIs include overloaded tracked `put`, `merge`, `delete`, experimental `singleDelete`, untracked variants, `putLogData`, `disableIndexing`, and `enableIndexing`. Introspection APIs include counters, elapsed time, `getWriteBatch`, write options, lock timeout, `undoGetForUpdate`, rebuild/commit-time batch, log number, transaction name/ID, deadlock state, waiting transactions, `getState`, and experimental `getId`. Nested types are `TransactionState` and `WaitingTransactions`.

## Control Flow
The object is package-constructed by `TransactionDB` or `OptimisticTransactionDB` and keeps references to the parent DB and default column family. Nearly every public method asserts ownership then delegates to native code. Overloads mostly normalize default column-family usage, list/array conversion, offset/length calculation, `ByteBuffer` direct-vs-array dispatch, and Java result wrapping (`GetStatus` for buffer reads). Multi-get with explicit column families validates key/CF counts before crossing JNI to avoid native crashes. Iterator creation wraps a native iterator handle with the parent DB. `setSnapshotOnNextOperation` optionally registers a native notifier handle.

## State and Persistence Behavior
Core state is native: transaction write batch, conflict tracking/locks, snapshots, savepoints, transaction state, log number, name, and commit-time batch. Tracked writes participate in conflict validation; untracked writes bypass conflict checking but may still acquire locks in pessimistic transactions. `commit` atomically writes batched changes to the DB; `rollback` and savepoint rollback discard pending operations. `disableIndexing` changes whether future writes are searchable by transaction reads. Java-side state is limited to parent/default-CF references and native handle ownership.

## Dependencies and Integration Points
It depends on `RocksObject`, `RocksDB`, `TransactionDB`, `OptimisticTransactionDB`, `ColumnFamilyHandle`, `ReadOptions`, `WriteOptions`, `TransactionOptions`, `Snapshot`, `AbstractTransactionNotifier`, `RocksIterator`, `WriteBatch`, `WriteBatchWithIndex`, `GetStatus`, `Status`, `RocksDBException`, and JNI implementations for all transaction operations.

## Risks and Test Signals
Tests should cover optimistic vs pessimistic conflict behavior, snapshot timing, `setSnapshotOnNextOperation` notifier callbacks, `get` versus `getForUpdate`, exclusive/shared locks, lock timeouts, `doValidate=false`, savepoint rollback, 2PC prepare/commit recovery, untracked write visibility, indexing disabled reads, iterator invalidation after commit/rollback/savepoint rollback, multi-CF validation, old transaction reuse, and ownership after close. Buffer overloads require all buffers in a call to be either direct or array-backed; mixed buffers throw `RocksDBException`. Several APIs return direct native-backed wrappers (`Snapshot`, write options, write batches) whose lifetimes need explicit testing. Some `ByteBuffer` merge paths do not advance positions consistently in the default-CF overload, so buffer-position behavior deserves regression tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Transaction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionDB.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionDB.java

## Purpose
`TransactionDB` is the RocksJava database wrapper for pessimistic transaction support. It opens transaction-capable RocksDB instances, begins transactions, recovers prepared transactions, exposes lock/deadlock diagnostics, and manages native DB lifecycle.

## Important APIs and Types
Static `open` overloads support simple `Options` and multi-column-family `DBOptions`/`ColumnFamilyDescriptor` opening with `TransactionDBOptions`. Transaction APIs implement `TransactionalDB<TransactionOptions>`: `beginTransaction(WriteOptions)`, `beginTransaction(WriteOptions, TransactionOptions)`, and old-transaction reuse overloads. Recovery/diagnostics include `getTransactionByName`, `getAllPreparedTransactions`, `getLockStatusData`, `getDeadlockInfoBuffer`, and `setDeadlockInfoBufferSize`. Nested DTOs are `KeyLockInfo`, `DeadlockInfo`, and `DeadlockPath`.

## Control Flow
`open(Options, ...)` calls native open, stores Java option references to prevent GC, stores transaction options, and creates/stores the default column family handle. The multi-CF open builds native arrays of column-family names and option handles, verifies the default column family is present, calls native open, wraps returned handles, records ownership, and stores the default CF. `closeE` closes native DB with exception propagation, while `close` first closes owned column-family handles and suppresses close errors. `beginTransaction` wraps native transaction handles. Old-transaction reuse asserts native returns the same handle. Named/prepared transaction lookups wrap non-owned transaction handles and call `disOwnNativeHandle`.

## State and Persistence Behavior
The class owns a native `TransactionDB` handle and Java references to options and transaction DB options. Persistent DB state lives on disk at the opened path. Transactions commit through native RocksDB; prepared transactions may survive process restart and be retrieved by name/all-prepared APIs. Lock and deadlock information is diagnostic in-memory native state.

## Dependencies and Integration Points
It extends `RocksDB`, implements `TransactionalDB<TransactionOptions>`, and depends on `Options`, `DBOptions`, `TransactionDBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `WriteOptions`, `TransactionOptions`, `Transaction`, and native JNI functions.

## Risks and Test Signals
Tests should cover simple and multi-CF opens, missing default-CF validation, option lifetime retention, close vs `closeE`, transaction begin with and without options, old-transaction reuse assumptions, prepared transaction lookup ownership, lock-status map construction, deadlock buffer shape/limit behavior, and restart recovery for prepared transactions. Risks include non-owned transaction wrappers being closed incorrectly, default-CF handle ownership ordering, and native open overload drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionDB.java -->
