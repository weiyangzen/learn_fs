# subset-b-008658 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactRangeOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactRangeOptions.java

Purpose: Java `RocksObject` wrapper for `CompactRangeOptions` used by `RocksDB.compactRange` style manual compactions. Important APIs include fluent setters/getters for exclusive manual compaction, change-level/target-level/target-path behavior, bottommost-level compaction policy, write-stall allowance, subcompaction override, full-history timestamp low watermark, and cancellation.

Control flow is thin JNI forwarding through `nativeHandle_`; construction allocates a C++ option object and `disposeInternal` frees it. `BottommostLevelCompaction` maps explicit byte constants to C++ `BottommostLevelCompaction`, while `Timestamp` is a Java immutable pair used by timestamp-aware compaction. State is native and transient, not persisted by Java, but it changes compaction output placement, throttling, and history retention behavior. Dependencies include `RocksObject`, `RocksDB`, `Objects`, and C++ JNI symbols.

Risks: enum values must remain in C++ order, `fromRocksId` can return null for unknown native values, target path IDs are explicitly undefined when out of range, and cancellation/full-history timestamp semantics depend on native support. Test signals should cover JNI round-trips, enum mapping, timestamp equality/hash, disposal, and compact-range behavior with level movement and write-stall options.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactRangeOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionJobInfo.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionJobInfo.java

Purpose: exposes native compaction-job metadata to Java callers and `EventListener` callbacks. APIs return column family name, status, thread/job identifiers, input and output levels, input/output file names, table properties, compaction reason, output compression, and optional `CompactionJobStats`.

Control flow is accessor-only JNI forwarding. The public constructor owns a new native struct; the private JNI constructor calls `disOwnNativeHandle()` because callback-created instances borrow C++ memory. `inputFiles()` and `outputFiles()` convert native arrays to fixed-size Java lists; `stats()` checks for native handle `0` before wrapping. State is native event/job state, usually ephemeral and tied to callback timing. Dependencies include `Status`, `TableProperties`, `CompactionReason`, `CompressionType`, and `CompactionJobStats`.

Risks: borrowed handle lifetime is critical, array/list results may be immutable-size views, unknown compaction reason/compression bytes can throw through enum conversion, and stats ownership differs from the parent info. Tests should exercise callback construction, null stats, table-property maps keyed by files, and disposal of owned versus disowned handles.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionJobInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionJobStats.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionJobStats.java

Purpose: JNI wrapper for detailed compaction counters and timings. APIs include `reset()`, `add()`, elapsed microseconds, input/output record and file counts, manual-compaction flag, byte totals, replacement/deletion/corruption counters, background IO nanosecond timings, output key prefixes, and experimental single-delete metrics.

Control flow delegates each operation to native methods using `nativeHandle_`. The public constructor allocates a stats object, while the package constructor wraps a native handle passed from `CompactionJobInfo.stats()`. The object has no Java-side persistence; it reflects native compaction statistics and can aggregate another native stats handle. Dependencies include `RocksObject`, `ColumnFamilyOptions.reportBgIoStats()` semantics, and the `Experimental` annotation.

Risks: `add()` assumes the other stats object is live, IO timing fields are only meaningful when background IO stats are enabled, experimental counters may change, and byte-array key prefixes depend on native copy semantics. Test signals should verify reset/add behavior, all JNI field mappings, optional population from compaction callbacks, and safe disposal after stats are returned from job info.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionJobStats.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionOptions.java

Purpose: options object for `RocksDB.compactFiles(...)`. It controls output compression, output file size limit, and per-compaction subcompaction count.

Control flow is a native-handle option wrapper with fluent setters returning `this`. `compression()` converts a native byte through `CompressionType.getCompressionType`; `setCompression()` passes the enum byte, including the special `DISABLE_COMPRESSION_OPTION` behavior documented for deferring to column-family settings. `outputFileSizeLimit()` and `maxSubcompactions()` are direct native getters. State is native configuration consumed by a compact-files call rather than Java-persisted state. Dependencies include `RocksObject`, `CompressionType`, `RocksDB`, `ColumnFamilyOptions`, `ColumnFamilyHandle`, `CompactionJobInfo`, and `DBOptions`.

Risks: compression enum drift breaks native mapping, subcompaction values override DB-level settings only when positive, and disposal before the compaction call completes would invalidate the native pointer. Tests should round-trip every field, validate special compression selection, and cover compact-files calls with output file-size and subcompaction overrides.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionOptionsFIFO.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionOptionsFIFO.java

Purpose: native option wrapper for FIFO compaction policy. APIs configure table-file size trimming, intra-L0 compaction allowance, combined SST/blob data-file size limit, and key-value-ratio compaction.

Control flow is simple JNI setter/getter forwarding after construction through `newCompactionOptionsFIFO()`. State lives in the native options object and is later embedded in column-family compaction options, affecting file deletion and compacting behavior under FIFO style. Integration points include `ColumnFamilyOptions`, FIFO compaction style selection, blob-file aware size accounting, and L0 file compaction thresholds described in comments.

Risks: defaults and triggering logic are enforced in C++ and can drift from Java comments, `maxDataFilesSize` changes FIFO accounting from SST-only to SST+blob, and enabling compaction can unexpectedly increase write amplification. Tests should verify Java/native round-trips, default values, behavior when blob files exist, and lifecycle disposal. The JNI signatures are the main contract to keep in sync with native RocksDB options.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionOptionsFIFO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionOptionsUniversal.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionOptionsUniversal.java

Purpose: native option wrapper for universal compaction. APIs configure size ratio, minimum/maximum merge width, maximum size amplification, compression size percent, compaction stop style, and trivial-move allowance.

Control flow is fluent Java-to-JNI forwarding. `stopStyle()` maps the native byte through `CompactionStopStyle.getCompactionStopStyle`; `setStopStyle()` passes the enum byte to native options. State is not persisted by Java but becomes part of column-family options and influences universal compaction picking and output compression strategy. Dependencies include `RocksObject`, `CompactionStopStyle`, and the C++ universal compaction option layout.

Risks: the options have strong performance implications and defaults live natively; invalid values are not validated in Java, unknown stop-style bytes throw, and native enum drift would break mapping. Tests should round-trip each property, cover stop-style conversion, and use integration compaction tests to ensure merge width and amplification settings affect compaction scheduling as expected.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionOptionsUniversal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionPriority.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionPriority.java

Purpose: enum for level-compaction file picking priorities. Values include compensated size, oldest largest sequence, oldest smallest sequence, minimum overlapping ratio, and round-robin.

Control flow is Java-only enum mapping: each constant has a byte value, `getValue()` exposes it to option JNI callers, and `getCompactionPriority(byte)` scans values and throws for unknown bytes. State is immutable and not persisted by Java; the byte is persisted/consumed only through native option serialization or RocksDB configuration. Dependencies are minimal but semantic integration is with `ColumnFamilyOptions` compaction priority and C++ enum values.

Risks: byte values must match native RocksDB; adding a native priority without updating Java causes exceptions when reading options. Tests should assert all byte mappings, invalid-byte exceptions, and option round-trips through configuration parsing or JNI getters.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionPriority.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionReason.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionReason.java

Purpose: enum describing why RocksDB scheduled a compaction, used mainly by `CompactionJobInfo` and event/listener reporting. It covers level, universal, FIFO, manual, ingestion, TTL, blob GC, temperature, round-robin TTL, and refit-level causes.

Control flow is package-level byte conversion: each enum has an internal byte value, and `fromValue(byte)` scans values or throws. State is immutable and mirrors native event metadata; no Java persistence exists. Dependencies include `CompactionJobInfo` and native listener/job-info code that supplies the byte.

Risks: values are sparse and must align with C++; `kFilesMarkedForCompaction` uses `0x10`, with later reasons around it, so accidental ordinal assumptions are unsafe. Tests should verify every byte mapping, unknown-byte failure, and callback population for representative compaction causes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionReason.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionStopStyle.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionStopStyle.java

Purpose: enum for universal compaction stop style. `CompactionStopStyleSimilarSize` stops when file sizes diverge, and `CompactionStopStyleTotalSize` uses total size criteria.

Control flow is byte mapping for JNI options: `getValue()` exposes the byte and `getCompactionStopStyle(byte)` scans/throws. State is immutable and consumed by `CompactionOptionsUniversal`. There is no persistence behavior in Java beyond native option serialization.

Risks: byte mapping must stay synced with native `CompactionStopStyle`; unknown native bytes throw when read from options. Tests should cover both values, invalid input, and round-trips through `CompactionOptionsUniversal.setStopStyle()`/`stopStyle()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionStopStyle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionStyle.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionStyle.java

Purpose: enum selecting RocksDB compaction strategy: level, universal, FIFO, or none. It is used by column-family/options APIs to encode native compaction style.

Control flow is immutable enum byte exposure through `getValue()`. Unlike several other enums, this file has no reverse lookup method, so reverse conversion is handled elsewhere if needed. State is not Java-persisted; it affects native DB behavior through option setters and option files.

Risks: byte constants must match native order, and lack of local reverse lookup means callers may need separate conversion logic. Tests should assert byte values against JNI option round-trips and cover each compaction style’s interaction with its dedicated option class (`CompactionOptionsFIFO`, `CompactionOptionsUniversal`).
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionStyle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ComparatorOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ComparatorOptions.java

Purpose: native options controlling Java `AbstractComparator` callback buffering. APIs configure reused-buffer synchronization, whether direct byte buffers are used, and maximum reused buffer size.

Control flow asserts handle ownership before JNI get/set calls, then returns `this` for setters. State lives in a native comparator-options object and affects callback memory allocation/locking, especially the five retained comparator buffers described in comments. Dependencies include `RocksObject`, `AbstractComparator`, and `ReusedSynchronisationType`.

Risks: callers must dispose instances to release native memory; disabling direct buffers or changing reuse size changes callback allocation behavior and retained memory; assertions only run when enabled, so misuse may surface natively. Tests should round-trip all fields, verify invalid synchronization bytes through `ReusedSynchronisationType`, exercise Java comparator callbacks with reused buffers, and confirm disposal is safe.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ComparatorOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ComparatorType.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ComparatorType.java

Purpose: enum distinguishing comparator callback implementation strategy: byte-array comparator or direct-buffer comparator.

Control flow is a small immutable byte mapping with package-visible `getValue()`. It has no reverse lookup and is consumed by comparator/native binding code. State is not persisted by Java except as a native option/config value where applicable. Dependencies are minimal and sit in the comparator integration area.

Risks: byte drift with native comparator type constants would select the wrong callback ABI. Tests should verify the byte values indirectly through comparator construction, one byte-array comparator path, and one direct-buffer comparator path.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ComparatorType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompressionOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompressionOptions.java

Purpose: native wrapper for compression tuning. APIs set/get window bits, compression level, strategy, maximum dictionary bytes, zstd training bytes, and an `enabled` flag for bottommost compression options.

Control flow is one-to-one JNI forwarding after allocating `newCompressionOptions()`. State lives in the native object and is used by column-family compression settings and bottommost compression settings; Java does not validate codec-specific ranges. Dependencies include `RocksObject`, compression libraries through native RocksDB, and column-family option consumers.

Risks: invalid codec parameters are accepted at Java level and may fail or degrade behavior natively; comments describe bottommost-option semantics that can be subtle because `enabled=false` means different things depending on which option slot consumes it. Tests should round-trip every property, cover zstd dictionary training settings, verify bottommost compression behavior, and assert disposal frees the native handle.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompressionOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompressionType.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompressionType.java

Purpose: enum of RocksDB compression algorithms/options: no compression, Snappy, zlib, bzip2, LZ4, LZ4HC, Xpress, ZSTD, and disabled option.

Control flow is byte mapping through `getValue()` and `getCompressionType(byte)`, which scans values and throws on unknown bytes. State is immutable and integrated with `CompactionOptions`, `ColumnFamilyOptions`, and option-file parsing/serialization. Java does not check whether a codec is compiled into the native library.

Risks: native codec availability differs by build, unknown bytes throw, and `DISABLE_COMPRESSION_OPTION` is semantically different from `NO_COMPRESSION`. Tests should verify byte mappings, invalid-byte behavior, compact-files behavior with disabled option, and native builds with/without optional codecs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompressionType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ConcurrentTaskLimiter.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ConcurrentTaskLimiter.java

Purpose: abstract native-backed base class for limiting concurrent background tasks. APIs define `name()`, `setMaxOutstandingTask(int)`, `resetMaxOutstandingTask()`, and `outstandingTask()`.

Control flow is polymorphic: the base class only stores the native handle via `RocksObject`; concrete classes implement JNI behavior. State is native limiter state, shared with RocksDB components that consult outstanding task counts. It is not Java-persisted. Dependencies include `RocksObject` and concrete `ConcurrentTaskLimiterImpl`.

Risks: API documentation says `0` blocks new tasks and negative means unlimited, but enforcement is native. Tests should cover concrete implementation behavior, limit changes under concurrent tasks, disposal, and any DB options that accept a limiter.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ConcurrentTaskLimiter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ConcurrentTaskLimiterImpl.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ConcurrentTaskLimiterImpl.java

Purpose: concrete JNI implementation of `ConcurrentTaskLimiter`. Constructor creates a named native limiter with a maximum outstanding task count.

Control flow asserts ownership before forwarding `name`, `setMaxOutstandingTask`, `resetMaxOutstandingTask`, and `outstandingTask` calls to native code. Setters return the base type for fluent use. State is fully native and can affect task admission in RocksDB subsystems that use the limiter. Dependencies include `ConcurrentTaskLimiter`, `RocksObject` disposal, and JNI symbols.

Risks: ownership assertions may be disabled, concurrent updates rely on native synchronization, and the typo in the abstract parameter name is harmless but can obscure API review. Tests should verify construction, name persistence, zero/negative/positive limit semantics, outstanding count observation during task execution, and native disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ConcurrentTaskLimiterImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ConfigOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ConfigOptions.java

Purpose: native wrapper for parsing/serializing RocksDB option strings and files. APIs configure delimiter, unknown-option handling, environment, escaped input strings, and sanity-check level.

Control flow loads the RocksDB library before native allocation, then forwards setters to native config options. `setEnv(Env)` passes the environment native handle but does not retain a Java field, so callers must ensure relevant lifetime. `setSanityLevel` maps `SanityLevel` to a byte. State is transient native parser configuration used by APIs such as `DBOptions.getDBOptionsFromProps`.

Risks: no Java-side getters for verification, env lifetime is not retained here, invalid delimiter/escape combinations can alter parsing, and unknown-option tolerance can hide config drift. Tests should parse representative option strings/properties with strict and permissive modes, exercise escaped values, sanity levels, and env-backed parsing.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ConfigOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DBOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DBOptions.java

Purpose: concrete native-backed implementation of `DBOptionsInterface<DBOptions>`, representing database-wide RocksDB options. It also supports construction from defaults, copy construction, conversion from `Options`, and parsing from `Properties`.

Important APIs cover environment/threading, open/create flags, rate limiting, SST manager, logger/log level, file limits, statistics, fsync, DB/WAL paths, background jobs, log/manifest/WAL sizing, direct/mmap IO, stats persistence, write buffering, listeners, write pipeline behavior, WAL recovery, 2PC, row cache, WAL filter, flush/recovery behavior, ingest-behind, atomic flush, DB ID manifest writing, log readahead, best-efforts recovery, background-error retry settings, and off-peak time. `setDbPaths` converts `Collection<DbPath>` to parallel path/target-size arrays; `dbPaths()` reconstructs Java `DbPath` objects from native arrays.

Control flow is almost entirely JNI forwarding using `nativeHandle_`. It retains Java references for collaborators whose native handles are installed into C++ (`env_`, `rateLimiter_`, `rowCache_`, `walFilter_`, `writeBufferManager_`) to reduce premature GC/disposal risk. State is native options state and can be persisted by RocksDB options files, manifests, WAL behavior, or stats history depending on individual settings. Dependencies span `Env`, `RateLimiter`, `SstFileManager`, `LoggerInterface`, `Statistics`, `DbPath`, `WriteBufferManager`, `AbstractEventListener`, `WALRecoveryMode`, `Cache`, `AbstractWalFilter`, and native RocksDB.

Risks: the huge JNI surface is vulnerable to signature drift; setters generally do no Java validation; deprecations for background flush/compaction coexist with `maxBackgroundJobs`; retained collaborator lifetimes must remain coherent; `getDBOptionsFromProps` parsing depends on `ConfigOptions`; and path arrays must preserve order/length. Tests should include field-by-field round-trips, copy constructor behavior, option-string parsing, listener retention, path conversion, disposal, and integration open tests for WAL/recovery/direct-IO/stat settings.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DBOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DBOptionsInterface.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DBOptionsInterface.java

Purpose: generic fluent contract for database-wide option types. `T extends DBOptionsInterface<T>` allows setters to return the concrete option type while sharing API documentation across `DBOptions` and related composite option classes.

The interface declares the DB-level option surface: environment, parallelism, creation/open flags, rate limiting, SST manager, logging, statistics, fsync, DB/WAL paths, obsolete-file cleanup, background job/subcompaction controls, log/manifest/WAL sizes, direct/mmap IO, file allocation, stats dump/persist/history, write buffer manager, event listeners, write pipeline/concurrency/yield settings, WAL recovery/2PC, caches/filters, recovery/flush behavior, ingest/atomic flush, stats-to-disk, DB ID manifest, log readahead, best-efforts recovery, background-error retry, and daily off-peak time.

Control flow is declarative only; implementations supply native forwarding. State and persistence behavior are described in comments and realized by implementers and native RocksDB. Dependencies include many RocksDB Java types and option consumers.

Risks: documentation drift from `DBOptions` or C++ defaults, default/deprecated behavior ambiguity, and generic implementers missing newly added methods. Tests should compile all implementers, run documentation-backed round-trips in `DBOptions`, and verify new methods are added consistently to implementations and JNI.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DBOptionsInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DataBlockIndexType.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DataBlockIndexType.java

Purpose: enum for block-based table data block indexing: binary search only or binary plus hash.

Control flow is immutable byte exposure through package-visible `getValue()`. State is not Java-persisted but is sent through table option JNI and persisted in table/options metadata according to RocksDB behavior. Dependencies include `BlockBasedTableConfig` or equivalent block-based table option consumers.

Risks: byte values must match C++ `DataBlockIndexType`, and there is no reverse lookup in this file. Tests should verify option round-trips and table creation with hash indexing, including prefix-extractor requirements where applicable.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DataBlockIndexType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DbPath.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DbPath.java

Purpose: Java tuple of database path and target size used by `DBOptions.setDbPaths`/`dbPaths`.

Control flow is pure Java value-object behavior: constructor stores package-visible final fields, `equals` compares path and target size with null handling, and `hashCode` combines both. State is immutable in Java and later converted by `DBOptions` into native path and target-size arrays that guide DB file placement across multiple paths.

Risks: fields are package-private rather than accessor-based, path nulls are allowed by equality but may fail native option conversion, and target size unit/meaning depends on RocksDB. Tests should cover equality/hash behavior, DBOptions conversion order, null-path rejection or behavior, and multi-path DB placement integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DbPath.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DirectSlice.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DirectSlice.java

Purpose: direct-`ByteBuffer` backed slice implementation for efficient native data access, especially for larger keys/values. It extends `AbstractSlice<ByteBuffer>` and exposes `NONE`.

Control flow has three construction paths: package-private JNI/default without native object, string constructor that allocates internal native buffer, and direct `ByteBuffer` constructors that require `data.isDirect()`. Accessors call native methods for `data0`, `get`, `clear`, `removePrefix`, and `setLength`. `removePrefix` advances `internalBufferOffset`; `disposeInternal` frees internal string buffer only if it has not been cleared, then disposes the slice handle.

State includes native slice handle, whether Java owns internal buffer memory, cleared flag, and offset. Dependencies include `AbstractSlice`, direct `ByteBuffer`, and native slice helpers.

Risks: non-direct buffers throw, internal buffer ownership/offset must be exact to avoid leaks or double free, volatile flags protect visibility but not full lifecycle synchronization, and disposed slices invalidate native access. Tests should cover string and direct-buffer construction, prefix removal before clear/dispose, setLength/get bounds through native code, and `NONE` behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DirectSlice.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/EncodingType.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/EncodingType.java

Purpose: enum for block/table encoding choices, including plain, prefix, and reserved values.

Control flow is immutable byte mapping through `getValue()` with no reverse lookup in this file. State is consumed by table configuration JNI and native RocksDB encoding logic; Java does not persist it directly. Dependencies are table option classes that accept encoding values.

Risks: reserved/native values must remain aligned, and unsupported encodings could be accepted until native validation. Tests should verify bytes through option round-trips and table creation/readback with supported encodings.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/EncodingType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Env.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Env.java

Purpose: abstract base for RocksDB environment implementations. It exposes the default environment and background thread-pool controls, queue length, IO/CPU priority lowering, and thread-list inspection.

Control flow for `getDefault()` uses an `AtomicReference<RocksEnv>` and CAS loop. It loads the library, creates a `RocksEnv` around the native default env, then calls `disOwnNativeHandle()` because C++ owns the singleton. Other methods forward native calls with `Priority` byte values. State includes only the Java singleton reference; thread pools and env resources are native. Integration points include `DBOptions.setEnv`, `EnvOptions`, `RocksEnv`, `ThreadStatus`, and background flush/compaction execution.

Risks: default env must never be freed by Java, CAS loop must avoid leaking multiple temporary wrappers, priority byte mapping must match native, and thread-list retrieval can throw `RocksDBException`. Tests should cover singleton identity, no-op disposal of default env, thread-pool setters/getters, priority lowering calls, and concurrent `getDefault()` access.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Env.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/EnvOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/EnvOptions.java

Purpose: native file IO option wrapper used while opening files. It can be default-constructed or constructed from `DBOptions`.

APIs configure mmap reads/writes, direct reads/writes, fallocate, fd close-on-exec, bytes-per-sync, keep-size fallocate, compaction readahead, writable-file max buffer size, and a write `RateLimiter`. Control flow loads the RocksDB library for default allocation and forwards all fields to native methods. `setRateLimiter` stores a Java reference and passes its native handle, so state includes native options plus a retained limiter reference.

Persistence is indirect: options affect file-opening and IO behavior, not Java storage. Dependencies include `RocksObject`, `DBOptions`, and `RateLimiter`.

Risks: comments include platform-specific semantics; Java does no validation of direct/mmap compatibility; constructing from `DBOptions` depends on source options lifetime during the call; rate limiter lifetime is retained only after setter use. Tests should round-trip every option, construct from DBOptions, exercise direct IO/mmap combinations where supported, and validate limiter retention/disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/EnvOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/EventListener.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/EventListener.java

Purpose: callback interface for RocksDB events, enabling Java code to observe flushes, compactions, file IO, table-file lifecycle, memtable changes, write stalls, error recovery, and external file ingestion.

Control flow is callback-driven from native RocksDB through listener wrappers. The interface documentation is a major behavioral contract: callbacks run on the actual RocksDB event thread, without DB mutexes held, and should return quickly; long DB operations should be offloaded to another thread. Callback arguments are either copied Java value objects or native-backed structs depending on event type. State is implementation-defined in user listeners; RocksDB stores listener registrations through options.

Dependencies include `RocksDB`, `FlushJobInfo`, `CompactionJobInfo`, `FileOperationInfo`, `TableFileCreationInfo`, `TableFileDeletionInfo`, `MemTableInfo`, `WriteStallInfo`, `ExternalFileIngestionInfo`, and error-recovery payload types.

Risks: blocking callbacks can stall flush/compaction/write paths, borrowed native objects may have limited lifetime, and listener exceptions crossing JNI need careful handling. Tests should register listeners, verify callback ordering/payloads, ensure no DB mutex deadlock for safe offloaded operations, and cover listener retention in `DBOptions`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/EventListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Experimental.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Experimental.java

Purpose: source-retention annotation marking APIs that may change, be removed, or be re-engineered.

Control flow is declarative Java annotation metadata: `@Documented`, `@Retention(SOURCE)`, and `@Target(TYPE, METHOD)`, with one required `String value()`. It has no runtime state, native dependency, or persistence behavior. Integration points include experimental classes and methods such as `HyperClockCache` and selected compaction stats.

Risks: because retention is SOURCE, runtime reflection cannot detect it; tooling must inspect sources or generated docs. Tests are mostly compile/documentation checks verifying intended APIs are annotated and no runtime dependency assumes retention.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Experimental.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ExportImportFilesMetaData.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ExportImportFilesMetaData.java

Purpose: native-backed metadata describing exported column-family files for later import. It is used by export/import column-family workflows.

Control flow is minimal: package-private constructor wraps a native handle, and `disposeInternal(long)` is native. No public accessors are present in this file, so Java treats it as an opaque token passed to import APIs. State is native metadata and may reference exported files/column-family descriptors. Dependencies include `RocksObject`, `RocksDB.createColumnFamilyWithImport`, and `ImportColumnFamilyOptions`.

Risks: opaque native ownership is the key concern; disposing too early invalidates import, while not disposing leaks native metadata. Tests should cover export-to-import lifecycle, disposal, and error behavior when metadata is reused or paired with incompatible options.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ExportImportFilesMetaData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ExternalFileIngestionInfo.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ExternalFileIngestionInfo.java

Purpose: immutable Java value object for external SST ingestion event data. It records column family name, external file path, internal DB file path, assigned global sequence number, and `TableProperties`.

Control flow is package-private construction from JNI/tests, public getters, and value-object `equals`, `hashCode`, and `toString`. State is copied into Java fields, so it can safely outlive the callback if nested `TableProperties` is also safe. Dependencies include `Objects`, `TableProperties`, and `EventListener` ingestion callbacks.

Risks: equality depends on `TableProperties.equals`, paths are raw strings, and constructor visibility means production instances originate from native code. Tests should compare value semantics, callback payload population, null field handling if native permits it, and sequence-number correctness for ingested files.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ExternalFileIngestionInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FileOperationInfo.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FileOperationInfo.java

Purpose: Java representation of `FileOperationInfo` from RocksDB listener APIs. It captures path, offset, length, start timestamp, duration, and `Status` for file operations.

Control flow is package-private construction from JNI, getters, and value-object equality/hash/toString. State is copied Java data used by `EventListener` callbacks such as file read/write/flush/sync events. There is no Java persistence, but timestamp/duration units are nanoseconds according to comments. Dependencies include `Status`, `Objects`, and listener native payload conversion.

Risks: status object semantics and nullability depend on native conversion; timestamp origin must match C++ docs; large offsets/lengths require long precision. Tests should validate callback payloads, equality/hash, failed-operation statuses, and unit expectations for duration fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FileOperationInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Filter.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Filter.java

Purpose: abstract native-backed base class for filter policies, such as Bloom filters, used by table options.

Control flow stores the native handle in `RocksObject`; `disposeInternal()` delegates to handle-based disposal, which calls native `disposeInternalJni`. Concrete subclasses supply construction and behavior. State is native filter-policy configuration; Java does not persist it directly, but table options can persist filter metadata in SSTs.

Dependencies include `RocksObject`, concrete filters like `BloomFilter`, and `FilterPolicyType`. Risks center on native ownership and ensuring subclasses use correct handles. Tests should create/dispose concrete filters, attach them to block-based table options, read/write data to exercise filter construction, and verify no double free when filters are shared or option objects are disposed.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Filter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FilterPolicyType.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FilterPolicyType.java

Purpose: enum for filter policy types used with block-based tables: unknown, bloom, and ribbon.

Control flow exposes byte values and has `createFilter(long, double)`, which currently constructs a `BloomFilter` only for `kBloomFilterPolicy`; other values return null. State is immutable; native filter handles and parameters are handled by concrete filters. Dependencies include `Filter`, `BloomFilter`, and block-based table options.

Risks: returning null for ribbon/unknown requires callers to handle unsupported creation; byte values must match native; creation semantics assume the passed handle is suitable for `BloomFilter`. Tests should verify bytes, bloom creation, non-bloom null behavior, and integration with block table filter options.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FilterPolicyType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FlushJobInfo.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FlushJobInfo.java

Purpose: immutable Java payload for flush completion/start events. It captures column family ID/name, output file path, thread/job ID, write slowdown/stop flags, sequence-number range, table properties, and flush reason.

Control flow is package-private construction from JNI/tests; constructor converts the native flush-reason byte using `FlushReason.fromValue`. Public getters expose fields, and value-object methods compare all fields. State is copied Java callback data, not native-owned state, except nested objects must be valid Java wrappers. Dependencies include `TableProperties`, `FlushReason`, `Objects`, and `EventListener`.

Risks: unknown flush-reason bytes throw during construction, table-properties equality affects value semantics, and slowdown/stop flags are point-in-time signals. Tests should cover construction for all flush reasons, equality/hash/toString, listener payload correctness, and behavior when RocksDB enters L0 write slowdown/stop conditions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FlushJobInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FlushOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FlushOptions.java

Purpose: native options object for `RocksDB.flush` operations. APIs control whether flush waits for completion and whether the flush may immediately proceed even if it stalls writes.

Control flow loads the native library before allocation, asserts handle ownership in getters/setters, forwards to native methods, and disposes the native handle. State is native and consumed by flush calls; Java does not persist it. Dependencies include `RocksObject` and `RocksDB`.

Risks: `newFlushOptionsInance` contains a misspelling but is private; write-stall behavior can materially affect availability; assertions may be disabled. Tests should round-trip `waitForFlush` and `allowWriteStall`, exercise synchronous/asynchronous flush behavior, verify write-stall option semantics under load, and ensure disposal invalidates no in-flight operation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FlushOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FlushReason.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FlushReason.java

Purpose: enum for reasons RocksDB flushed memtables, including shutdown, external ingestion, manual compaction/flush, write-buffer pressure, delete files, auto compaction, error recovery, WAL full, and catch-up after recovery.

Control flow is package-level byte mapping with `getValue()` and `fromValue(byte)` scanning values and throwing on unknown bytes. State is immutable and used by `FlushJobInfo`. Dependencies include native listener payload conversion.

Risks: byte values must track native `FlushReason`, and unknown bytes fail construction of `FlushJobInfo`. Tests should assert every mapping, invalid-byte behavior, and listener events that produce representative reasons.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/FlushReason.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/GetStatus.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/GetStatus.java

Purpose: result object for fetch-into-buffer operations where the destination may be too small. It carries a `Status` and `requiredSize`.

Control flow is package-private construction plus `fromStatusCode(Status.Code, int)`, which creates a `Status` with subcode zero and null state. Fields are public final, making the object immutable. State is copied Java result data, not native-owned. Dependencies include `Status.Code` and `Status.SubCode`.

Risks: `requiredSize` can be larger than the supplied buffer and must be checked by callers; `fromStatusCode` discards richer status state/subcode. Tests should cover success, not-found/error statuses, too-small buffer size reporting, and callers that retry with the required size.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/GetStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HashLinkedListMemTableConfig.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HashLinkedListMemTableConfig.java

Purpose: Java `MemTableConfig` for hash linked-list memtable representation, requiring a prefix extractor for intended behavior. It configures fixed bucket count, huge page TLB size, bucket-entry logging threshold, whether to log bucket distribution at flush, and threshold to fall back/use skiplist.

Control flow is Java-side mutable configuration with defaults, fluent setters/getters, and native factory creation through `newMemTableFactoryHandle(...)`. State is stored in Java fields until the memtable factory handle is requested by options. Dependencies include `MemTableConfig`, prefix-extractor option APIs, and native memtable factory code.

Risks: without a prefix extractor RocksDB falls back to skiplist and logs a warning; defaults include a typo constant `DEFAUL_THRESHOLD_USE_SKIPLIST`; large bucket counts or huge pages affect memory; native factory receives current field values only at creation time. Tests should verify defaults, setters, factory creation, prefix-extractor integration, and fallback behavior when prefix extraction is absent.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HashLinkedListMemTableConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HashSkipListMemTableConfig.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HashSkipListMemTableConfig.java

Purpose: Java `MemTableConfig` for hash skip-list memtable representation. It configures bucket count, skip-list height, branching factor, and huge page TLB size.

Control flow is Java-side mutable configuration initialized with defaults. Fluent setters update fields, getters return current values, and the native memtable factory handle is created from those fields. State persists only in the config object until installed into column-family options; native RocksDB owns runtime memtables. Dependencies include `MemTableConfig`, prefix-extractor options, and native hash skip-list factory.

Risks: like hash linked-list, this representation depends on prefix extraction; invalid height/branching/bucket values are not Java-validated; huge page settings are platform-sensitive. Tests should cover default values, setter/getters, native factory creation, DB open/write behavior with prefix extractor, and fallback/warning behavior without one.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HashSkipListMemTableConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HistogramData.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HistogramData.java

Purpose: immutable Java data holder for histogram statistics: median, P95, P99, average, standard deviation, max, count, sum, and min.

Control flow is constructor-only assignment plus simple getters. The older constructor fills max/count/sum/min with zero defaults, preserving compatibility. State is copied Java metrics data, likely created by `Statistics` JNI calls. Dependencies include statistics/histogram APIs but no native handle.

Risks: no equality/toString helpers, sum is `long` while other distribution fields are `double`, and the compatibility constructor can hide absent min/max/count fields as zero. Tests should verify constructor field order, values from `Statistics.getHistogramData`, and behavior for empty histograms.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HistogramData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HistogramType.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HistogramType.java

Purpose: enum of RocksDB histogram metric identifiers for DB operations, compaction, IO, blob DB, flush, multiget/multiscan, async IO, ingestion, and related timing/size distributions.

Control flow maps each histogram to an explicit byte, exposes `getValue()`, and provides `getHistogramType(byte)` with invalid-byte exception. State is immutable and consumed by `Statistics` APIs to select a histogram. Dependencies include `Statistics`, `HistogramData`, and native ticker/histogram definitions.

Risks: byte values are extensive and sparse (`0x3E` reserved/max, `0x3F` used after it), making ordinal assumptions unsafe; new native metrics require Java updates. Tests should verify all byte mappings, invalid-byte behavior, selected statistics lookups, and compatibility when native exposes unknown metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HistogramType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Holder.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Holder.java

Purpose: simple generic mutable reference wrapper for APIs needing an output parameter or mutable capture.

Control flow is pure Java: optional-value constructor, default null constructor, `getValue()`, and `setValue()`. State is one nullable reference; there is no synchronization, native handle, or persistence behavior. Dependencies are none beyond Java generics.

Risks: not thread-safe, nullability is only expressed in comments, and mutable holders can obscure ownership/lifetime of stored RocksDB objects. Tests are minimal: constructor/get/set behavior, null handling, and any API using `Holder` as an out parameter.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Holder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HyperClockCache.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HyperClockCache.java

Purpose: experimental `Cache` implementation wrapping RocksDB HyperClockCache, intended as a CPU-efficient block-cache alternative under high parallelism/contention.

Control flow is constructor-only JNI allocation with capacity, estimated entry charge, shard bits, and strict capacity limit; disposal forwards to native `disposeInternalJni`. State is native cache state inherited through `Cache`, used primarily by `BlockBasedTableOptions.block_cache`. Dependencies include `Cache`, `Experimental`, and block-based table options.

Risks: marked experimental; comments warn it is not a general cache, requires tuning `estimatedEntryCharge`, can dilute priorities, and can perform poorly for small/pinned caches. Changing capacity may reduce efficiency. Tests should cover construction/disposal, use as block cache in a DB, strict-capacity behavior, shard-bit settings, and performance/regression benchmarks versus LRUCache under contention.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HyperClockCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ImportColumnFamilyOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ImportColumnFamilyOptions.java

Purpose: native options for `RocksDB.createColumnFamilyWithImport(...)`. The exposed option controls whether imported files are moved into place or copied/linked according to native behavior.

Control flow allocates a native options object, exposes `moveFiles()` and fluent `setMoveFiles(boolean)`, and relies on inherited `RocksObject` disposal. State is native import configuration consumed with `ColumnFamilyDescriptor` and `ExportImportFilesMetaData`. Dependencies include `RocksDB`, `ColumnFamilyDescriptor`, and export/import metadata.

Risks: moving files has destructive/lifetime implications for exported file locations; Java does not expose additional import validation; disposal timing matters around import calls. Tests should round-trip `moveFiles`, import a column family with move enabled/disabled, verify source file handling, and cover error behavior for missing or incompatible metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ImportColumnFamilyOptions.java -->
