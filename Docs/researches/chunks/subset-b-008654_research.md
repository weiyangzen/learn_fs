# sources/storage-engines/rocksdb/java/rocksjni/portal.h lines 7633-9355

## Scope

This chunk covers the tail of RocksJava's JNI portal header. It starts inside `CompactionReasonJni`'s Java-to-C++ mapping and then defines portal helpers for WAL file types, log/live/SST/level/column-family metadata objects, trace writers, WAL filters, WAL processing options, reused synchronization/config sanity/blob-cache enums, enabled event callback masks, event-listener method IDs, event payload wrappers, compact-range timestamps, and reconstruction of Java `BlockBasedTableConfig` from native `BlockBasedTableOptions`.

The code is mostly bridge code: it does not implement RocksDB storage algorithms directly, but it is on the boundary where C++ state, persistent metadata, background-event information, and table options become Java objects or Java callback invocations.

## Purpose

- Keep Java enum byte values synchronized with native RocksDB enum values used by compaction reasons, WAL file types, WAL replay decisions, synchronization strategy, config sanity checks, and blob-cache prepopulation.
- Convert native metadata structs into immutable Java-facing value objects for logs, live files, SST files, levels, column families, flush jobs, table-file creation/deletion, external ingestion, memtable sealing, write stalls, file IO, and compact-range timestamp spans.
- Cache JNI class and method lookup results for callback-heavy paths such as trace writing, WAL filtering, event listener callbacks, and table option reconstruction.
- Expose C++ callback implementations to Java subclasses of `AbstractTraceWriter`, `AbstractWalFilter`, and `AbstractEventListener` through `RocksDBNativeClass` pointer-handle helpers.
- Preserve important storage/persistence details across the Java boundary, including WAL file identity and type, LSM file levels and sequence-number ranges, checksums, table properties, status objects, background-error reasons, and block-based table format/cache/filter settings.

## Important APIs, Types, And Functions

- `CompactionReasonJni::toCppCompactionReason()` maps Java `org.rocksdb.CompactionReason` bytes to native `CompactionReason`, defaulting unknown bytes to `kUnknown`. This chunk includes values through forced blob GC, round-robin TTL, and refit-level compactions.
- `WalFileTypeJni` maps native `WalFileType::{kArchivedLogFile,kAliveLogFile}` to Java bytes and back; unknown Java input defaults to alive log files.
- `LogFileJni::fromCppLogFile()` creates `org.rocksdb.LogFile` from `LogFile::PathName()`, `LogNumber()`, `Type()`, `StartSequence()`, and `SizeFileBytes()`.
- `LiveFileMetaDataJni::fromCppLiveFileMetaData()` converts `LiveFileMetaData` into Java `LiveFileMetaData`, including column-family bytes, level, file name, DB path, size, sequence bounds, smallest/largest keys, sampled reads, compaction flag, entry/delete counts, and file checksum.
- `SstFileMetaDataJni::fromCppSstFileMetaData()` is the non-column-family variant for Java `SstFileMetaData`, carrying file/path strings, size, sequence bounds, key bounds, sampled reads, compaction flag, entry/delete counts, and checksum.
- `LevelMetaDataJni::fromCppLevelMetaData()` builds an array of Java `SstFileMetaData` for every file in a native level and wraps it in `org.rocksdb.LevelMetaData`.
- `ColumnFamilyMetaDataJni::fromCppColumnFamilyMetaData()` builds Java `ColumnFamilyMetaData` from total size, file count, CF name bytes, and an array of `LevelMetaData`.
- `AbstractTraceWriterJni` resolves `AbstractTraceWriter` methods `writeProxy(long)`, `closeWriterProxy()`, and `getFileSize()` for native trace-writer callbacks.
- `AbstractWalFilterJni` resolves `AbstractWalFilter` methods `columnFamilyLogNumberMap(Map, Map)`, `logRecordFoundProxy(long,String,long,long)`, and `name()` for WAL replay filtering.
- `WalProcessingOptionJni` maps Java replay actions to `WalFilter::WalProcessingOption`: continue, ignore current record, stop replay, or mark corrupted. Unknown Java input defaults to `kCorruptedRecord`.
- `ReusedSynchronisationTypeJni`, `SanityLevelJni`, and `PrepopulateBlobCacheJni` translate smaller configuration enums used by Java options/configuration APIs.
- `EnabledEventCallbackJni::toCppEnabledEventCallbacks()` decodes a Java bitmask into a `std::set<EnabledEventCallback>` by scanning `NUM_ENABLED_EVENT_CALLBACK` bits.
- `AbstractEventListenerJni` resolves method IDs for all Java event callbacks in this range: flush begin/completed, table-file deletion/creation/creation-started, compaction begin/completed, memtable sealed, CF handle deletion, external file ingestion, background error, write stall changes, file IO operation completions, file-IO notification opt-in, error recovery begin, and error recovery completed.
- `FlushJobInfoJni`, `TableFileDeletionInfoJni`, `TableFileCreationInfoJni`, `TableFileCreationBriefInfoJni`, `MemTableInfoJni`, `ExternalFileIngestionInfoJni`, `WriteStallInfoJni`, and `FileOperationInfoJni` construct Java event payloads from native event structs.
- `CompactionJobInfoJni::fromCppCompactionJobInfo()` creates Java `CompactionJobInfo` with a raw native pointer handle instead of eagerly copying all fields.
- `CompactRangeOptionsTimestampJni::fromCppTimestamp()` wraps a native `start` and `range` pair into Java `CompactRangeOptions.Timestamp`.
- `BlockBasedTableOptionsJni::construct()` creates Java `BlockBasedTableConfig` from native `BlockBasedTableOptions`, including cache/index/filter booleans, index and checksum enum translations, block sizes/restarts, format version, key-value separation, compression/index-search settings, super-block alignment settings, and filter-policy type/handle.

## Control Flow

Most conversion helpers follow the same JNI pattern. They first resolve the Java class with `JavaClass::getJClass()` or `RocksDBNativeClass::getJClass()`, then resolve a constructor or method signature with `GetMethodID()`, convert native strings/slices/status/table-properties to Java objects, call `NewObject()` or return a cached method ID, and clean up local references on error paths.

Nested metadata conversion is bottom-up. `SstFileMetaDataJni` converts one native SST metadata entry. `LevelMetaDataJni` allocates a Java object array sized to `level_meta_data->files`, fills it by repeatedly calling `SstFileMetaDataJni::fromCppSstFileMetaData()`, and then creates one Java level object. `ColumnFamilyMetaDataJni` repeats the same pattern for levels before constructing the column-family metadata object.

Event-listener dispatch is split between method-ID portals and payload portals. `AbstractEventListenerJni` only looks up Java callback method IDs and their exact signatures. Separate payload classes create the Java argument objects passed to those callbacks, for example `FlushJobInfoJni` for `onFlushBeginProxy`/`onFlushCompletedProxy`, `TableFileCreationInfoJni` for `onTableFileCreated`, and `FileOperationInfoJni` for file IO completion callbacks.

Enum conversion uses explicit `switch` statements over Java byte constants or C++ enum values. Undefined native enum values usually map to `0x7F` or `-0x01` for Java "unknown"; undefined Java enum bytes map to conservative native defaults such as `kUnknown`, `kAliveLogFile`, `kCorruptedRecord`, `ADAPTIVE_MUTEX`, `kSanityLevelExactMatch`, or `kDisable`.

`BlockBasedTableOptionsJni::construct()` has a longer flow. It resolves `BlockBasedTableConfig`'s large constructor signature, detects the native filter policy by compatibility name, exposes the native filter-policy pointer only for recognized built-in policy types, and then passes all supported table-option fields in constructor order.

## State And Persistence Behavior

- This header does not persist data itself; it preserves persisted or runtime RocksDB state when presenting it to Java.
- WAL state crosses the bridge through `LogFileJni` and `WalFileTypeJni`: Java receives the WAL path, log number, alive/archive classification, start sequence, and size.
- Live-file and SST metadata expose LSM persistence state to Java, including levels, file paths, sizes, key bounds, sequence-number bounds, entry/delete counts, compaction state, and checksums.
- Column-family metadata preserves the hierarchy `ColumnFamilyMetaData -> LevelMetaData[] -> SstFileMetaData[]`, matching the source tree's LSM layout rather than flattening it.
- Flush/table-file/external-ingestion event payloads carry persisted-file identities, table properties, global sequence numbers, statuses, job IDs, reasons, and file sizes that Java listeners can use for audit or monitoring.
- File-operation payloads expose path, offset, length, start timestamp, duration, and status, which are observability state from RocksDB's environment/file-system layer.
- `CompactionJobInfoJni` intentionally passes a native pointer handle to Java, so the lifetime of the pointed-to native `CompactionJobInfo` is part of the callback contract.
- `BlockBasedTableOptionsJni::construct()` serializes native block-table configuration into Java configuration state, including filter-policy pointer handles for recognized policies. The resulting Java object is a mirror of native options, not an owner of storage-engine state.

## Dependencies And Integration Points

- JNI dependencies include `JNIEnv`, `jclass`, `jmethodID`, `jobject`, `jobjectArray`, `jstring`, `jbyteArray`, primitive JNI casts, local-reference cleanup, `ExceptionCheck()`, `GetMethodID()`, `NewObject()`, and `NewObjectArray()`.
- Portal base classes are `JavaClass` and `RocksDBNativeClass`, with native-pointer exposure through `GET_CPLUSPLUS_POINTER`.
- Utility dependencies include `JniUtil::toJavaString()`, `JniUtil::copyBytes()`, `StatusJni::construct()`, `TablePropertiesJni::fromCppTableProperties()`, and enum helpers such as `IndexTypeJni`, `DataBlockIndexTypeJni`, `ChecksumTypeJni`, `IndexShorteningModeJni`, `IndexSearchTypeJni`, and `FilterPolicyJni`.
- Native RocksDB types bridged here include `LogFile`, `LiveFileMetaData`, `SstFileMetaData`, `LevelMetaData`, `ColumnFamilyMetaData`, `TraceWriterJniCallback`, `WalFilterJniCallback`, `EventListenerJniCallback`, `FlushJobInfo`, `TableFileDeletionInfo`, `CompactionJobInfo`, `TableFileCreationInfo`, `TableFileCreationBriefInfo`, `MemTableInfo`, `ExternalFileIngestionInfo`, `WriteStallInfo`, `FileOperationInfo`, `BlockBasedTableOptions`, and several RocksDB enums.
- Java classes integrated by exact name/signature include `org.rocksdb.LogFile`, `LiveFileMetaData`, `SstFileMetaData`, `LevelMetaData`, `ColumnFamilyMetaData`, `AbstractTraceWriter`, `AbstractWalFilter`, `AbstractEventListener`, event info classes, `CompactRangeOptions$Timestamp`, and `BlockBasedTableConfig`.
- The callback portals are used by native callback adapter implementations outside this range. Those adapters call the cached `jmethodID`s and payload constructors when RocksDB emits flush, compaction, file IO, WAL replay, trace-writing, or error-recovery events.

## Risks And Edge Cases

- Constructor and method descriptors are hard-coded. Any Java signature change must be mirrored here exactly or runtime `NoSuchMethodError`/assert failures will occur.
- Several methods use `assert(mid != nullptr)` or `assert(jclazz != nullptr)` after lookup. In release builds, a missing method may produce a null method ID that is used later if the assertion is compiled out.
- Local-reference cleanup is inconsistent. Many error paths delete earlier local references, but some successful object-construction paths return without deleting all local refs, relying on JNI frame cleanup. Callback-heavy code should avoid creating excessive local references.
- `FlushJobInfoJni::fromCppFlushJobInfo()` deletes `jfile_path` instead of `jcf_name` when file-path string creation reports an exception. That appears suspicious because `jfile_path` may not be a valid local reference on that path.
- `TableFileDeletionInfoJni::fromCppTableFileDeletionInfo()` creates the file-path Java string inline in `NewObject()` and does not separately check conversion failure or delete the local reference.
- `SstFileMetaDataJni` casts `smallest_seqno` to `jint` while the constructor descriptor expects a `J` long slot. If the native field can exceed 32 bits, Java metadata can be truncated or the varargs call can be ABI-sensitive.
- Enum byte values are a compatibility contract with Java enums. Adding a native enum without updating Java and these switches can silently produce Java "undefined" or default to a potentially wrong native behavior.
- Unknown WAL processing options default to `kCorruptedRecord`, which is fail-closed for replay but can change recovery behavior if Java emits an invalid byte.
- `EnabledEventCallbackJni` shifts `1ULL << i`; correctness depends on `NUM_ENABLED_EVENT_CALLBACK` staying within the width of `jlong`/64-bit masks and Java using the same bit ordering.
- `CompactionJobInfoJni` exposes a native pointer rather than copying fields. Java code must not retain or use it beyond the valid native callback lifetime.
- `BlockBasedTableOptionsJni::construct()` exposes a filter-policy handle only when the compatibility name is recognized. Unknown/custom policies are represented as unknown with handle `0`, which can lose detail when mirroring options to Java.
- `super_block_alignment_space_overhead_ratio` is cast to `jlong` even though the Java constructor slot in the descriptor is `J` and the native option name suggests a ratio; if the native type is non-integral, this conversion deserves scrutiny.

## Test Signals

- RocksJava JNI build/tests should fail quickly if any hard-coded Java constructor or callback method descriptor in this chunk diverges from the corresponding Java class.
- Metadata API tests should check that `getSortedWalFiles`, live-file metadata, SST metadata, level metadata, and column-family metadata expose names, paths, sequence numbers, levels, sizes, checksums, and array nesting accurately.
- Event-listener tests should cover every method ID in `AbstractEventListenerJni`: flush begin/completed, compaction begin/completed, table-file created/deleted/creation-started, memtable sealed, CF handle deletion, external file ingestion, background error, stall changes, file IO completion methods, file-IO opt-in, and error recovery callbacks.
- WAL-filter tests should validate `columnFamilyLogNumberMap`, `logRecordFoundProxy`, callback naming, and all `WalProcessingOption` outcomes: continue, ignore, stop replay, and corrupted record.
- Enum round-trip tests are useful for `CompactionReason`, `WalFileType`, `WalProcessingOption`, `ReusedSynchronisationType`, `SanityLevel`, and `PrepopulateBlobCache`, including undefined-byte behavior.
- Block-based table config tests should compare Java configs constructed from native `BlockBasedTableOptions` against expected cache, block size, checksum, index, filter-policy, format-version, compression, and alignment settings.
- Stress or callback-frequency tests should watch for local-reference table growth and pending Java exceptions in event payload conversion paths.
- Boundary tests should include large sequence numbers for `SstFileMetaData`, custom filter policies in `BlockBasedTableOptions`, invalid enabled-event bitmasks, and Java callbacks throwing exceptions during native event delivery.
