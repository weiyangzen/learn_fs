# sources/storage-engines/rocksdb/java/rocksjni/options.cc lines 1-7872

## Scope

This chunk covers the first 7,872 lines of RocksDB's Java JNI options bridge. It starts with the native implementation for `org.rocksdb.Options`, continues through the full `org.rocksdb.ColumnFamilyOptions` bridge, and then covers the beginning and most of the `org.rocksdb.DBOptions` bridge through `DBOptions.setMaxBgErrorResumeCount`. The remaining tail of `DBOptions` plus `WriteOptions`, `ReadOptions`, `ComparatorOptions`, and `FlushOptions` continue after this chunk and are out of scope here.

The file is intentionally broad and mostly mechanical: each JNI entry point translates Java handles, primitive values, strings, arrays, callbacks, and enum bytes into fields or helper method calls on RocksDB C++ `Options`, `ColumnFamilyOptions`, and `DBOptions` objects. The nontrivial behavior is in native object ownership, Java/C++ array conversion, status-to-exception handling, enum conversion through portal helpers, shared-pointer copying, callback lifetime expectations, and option-string parsing.

## Purpose

- Expose the combined `rocksdb::Options` object to Java, including construction from separate `DBOptions` and `ColumnFamilyOptions`, copying, disposal, and optimization helpers.
- Expose standalone `ColumnFamilyOptions` and `DBOptions` objects so Java callers can configure DB-wide and column-family-specific state independently.
- Let Java configure core RocksDB behavior that is ultimately consumed by DB open, recovery, WAL handling, memtables, table factories, compaction, blob files, logging, statistics, rate limiting, and event callbacks.
- Convert Java-friendly values into C++ option fields: `jboolean` to bool, `jbyte` enum ordinals to RocksDB enums, `jlong` handles to C++ pointers, Java strings to `std::string`, and Java arrays to C++ vectors.
- Preserve ownership boundaries between Java wrapper objects and native RocksDB objects by copying `std::shared_ptr` instances where expected, taking raw ownership for factories stored in `unique_ptr` fields, and storing raw callback pointers for comparator/filter/WAL callback APIs.
- Provide parsing entry points for option-property strings through `GetColumnFamilyOptionsFromString()` and `GetDBOptionsFromString()`.

## Important APIs, Types, And Functions

- `Java_org_rocksdb_Options_newOptions__`, `newOptions__JJ`, `copyOptions`, and `disposeInternalJni` allocate, combine, clone, and delete native `rocksdb::Options` instances returned to Java as `jlong` handles.
- `Java_org_rocksdb_ColumnFamilyOptions_newColumnFamilyOptions`, `copyColumnFamilyOptions`, `newColumnFamilyOptionsFromOptions`, and `disposeInternalJni` provide the same lifecycle for `rocksdb::ColumnFamilyOptions`.
- `Java_org_rocksdb_DBOptions_newDBOptions`, `copyDBOptions`, `newDBOptionsFromOptions`, and `disposeInternalJni` provide the lifecycle for `rocksdb::DBOptions`.
- `getColumnFamilyOptionsFromProps` and `getDBOptionsFromProps` allocate new option objects, parse semicolon/property-style option strings with optional `ConfigOptions`, return `0` on parse failure, and delete failed allocations to avoid leaks.
- Comparator bridge methods accept either built-in comparator IDs or Java/native comparator handles. Built-in ID `1` maps to `ReverseBytewiseComparator()`, and the default maps to `BytewiseComparator()`. Custom handles are stored as raw `Comparator*`.
- Merge, compaction filter, WAL filter, event listener, logger, table filter, and table-property collector hooks integrate Java callbacks or wrapper objects with native `Options` fields.
- Shared resource setters copy `std::shared_ptr` payloads from Java-owned wrapper handles into option fields, including `StatisticsJni`, `RateLimiter`, `SstFileManager`, `Cache` row cache, `WriteBufferManager`, `CompactionFilterFactory`, `SstPartitionerFactory`, and `ConcurrentTaskLimiter`.
- Factory setters such as `setMemTableFactory` and `setTableFactory` reset native `unique_ptr` fields from raw handles, transferring ownership to the options object.
- `rocksdb_convert_cf_paths_from_java_helper()` validates Java path and size arrays, rejects mismatched lengths and negative target sizes, and returns `std::vector<DbPath>` for both `Options` and `ColumnFamilyOptions`.
- `rocksdb_convert_cf_paths_to_java_helper<T>()` writes native `cf_paths` back into caller-provided Java string and long arrays for either `Options` or `ColumnFamilyOptions`.
- `Options.setDbPaths` and `DBOptions.setDbPaths` separately convert DB path arrays. Unlike the shared CF-path helper, these functions do not explicitly check matching path/size lengths before indexing the Java long array.
- `rocksdb_set_event_listeners_helper()` and `rocksdb_get_event_listeners_helper()` convert between Java arrays of listener native handles and C++ vectors of `std::shared_ptr<EventListener>`, assuming the listeners are Java-backed `EventListenerJniCallback` objects on readback.
- `rocksdb_compression_vector_helper()` and `rocksdb_compression_list_helper()` translate per-level compression arrays between Java `byte[]` and `std::vector<CompressionType>`.
- Portal conversions in `rocksjni/portal.h` handle enum mappings for `CompressionType`, `CompactionStyle`, `CompactionPriority`, `WALRecoveryMode`, and `PrepopulateBlobCache`.
- Option tuning wrappers call native helpers: `IncreaseParallelism`, `OldDefaults`, `OptimizeForSmallDb`, `OptimizeForPointLookup`, `OptimizeLevelStyleCompaction`, `OptimizeUniversalStyleCompaction`, and `PrepareForBulkLoad`.
- Getter/setter pairs cover DB-open flags, file IO behavior, background jobs, logging, WAL retention and recovery, write-thread behavior, stats persistence, direct IO, memtable sizing, compression, compaction triggers, universal/FIFO compaction options, blob file options, and range deletion conversion thresholds.

## Control Flow

The normal flow for a Java options object starts with a Java wrapper calling a native constructor. The C++ side allocates the corresponding RocksDB option object with `new`, casts its address through `GET_CPLUSPLUS_POINTER`, and returns it as a `jlong`. Later Java setter calls pass that handle back; the JNI function casts it to the expected C++ type and mutates one field or invokes one RocksDB option helper. Disposal casts the handle back and deletes it, guarded only by an `assert` against null.

For composite `Options`, `newOptions__JJ` takes already-created `DBOptions` and `ColumnFamilyOptions` handles, dereferences both, and constructs a combined `rocksdb::Options(*dbOpt, *cfOpt)`. Conversely, `newColumnFamilyOptionsFromOptions` and `newDBOptionsFromOptions` project the relevant base subobject out of a combined `Options`.

String setters usually call `GetStringUTFChars`, check for null or exception, assign to a `std::string`, and release the UTF chars. Parsing functions follow a similar flow but run `GetColumnFamilyOptionsFromString()` or `GetDBOptionsFromString()` before returning a handle. If parsing fails, the freshly allocated option object is deleted and Java receives `0` rather than a thrown exception in this chunk.

Array conversion follows a defensive JNI pattern in most helpers: obtain array elements, loop over entries, create or copy C++ values, check `ExceptionCheck()` after object-array writes, release with `JNI_ABORT` when Java input arrays should not be modified, and release with commit mode when writing native data into Java output arrays. Compression and multiplier arrays allocate temporary C++ buffers, fill Java primitive arrays, and delete the temporary buffers on both success and exception paths.

Callback and shared-resource setters are mostly direct handle transfers. Shared-pointer-backed wrappers are dereferenced and copied into the native option object so lifetime is extended by C++ ownership. Raw callback pointers such as comparators, compaction filters, WAL filters, and table filters are stored directly, so the Java wrapper layer must keep the callback object alive as long as the native options or opened DB can use it.

The `DBOptions` section mirrors many `Options` DB-wide setters. This chunk stops while processing background-error resume options, so later `DBOptions` properties are documented by the next chunk.

## State And Persistence Behavior

The JNI code itself does not write persistent data. It mutates in-memory option structures whose values are later consumed by RocksDB open, write, flush, compaction, recovery, and administrative code. Some fields configured here affect persistent behavior indirectly:

- `create_if_missing`, `create_missing_column_families`, `error_if_exists`, and `paranoid_checks` control DB open and recovery semantics.
- WAL fields such as `max_total_wal_size`, `WAL_ttl_seconds`, `WAL_size_limit_MB`, `wal_recovery_mode`, `allow_2pc`, `two_write_queues`, `manual_wal_flush`, `atomic_flush`, and `write_dbid_to_manifest` affect recovery, WAL retention, transaction support, and MANIFEST contents once a DB is opened.
- File and manifest options such as `db_paths`, `cf_paths`, `db_log_dir`, `wal_dir`, `max_manifest_file_size`, `manifest_preallocation_size`, `use_fsync`, mmap/direct IO flags, `bytes_per_sync`, `wal_bytes_per_sync`, and `strict_bytes_per_sync` influence where RocksDB stores files and how durable/synchronized writes are performed.
- Memtable and write-buffer options influence flush frequency and write stalls, including `write_buffer_size`, `max_write_buffer_number`, `min_write_buffer_number_to_merge`, `db_write_buffer_size`, `write_buffer_manager`, and `allow_concurrent_memtable_write`.
- Compaction options influence future SST layout and rewrite behavior: compression settings, level sizes, L0 triggers, compaction style, compaction priority, dynamic level bytes, universal/FIFO options, TTL, periodic compaction, and blob garbage collection knobs.
- `Statistics`, event listeners, loggers, table property collectors, rate limiters, caches, partitioners, and factories stored here become dependencies of the DB or column family created from these options.

Native ownership state is important. Objects allocated in this chunk are owned by Java wrapper handles until `disposeInternalJni` is called. Options fields may then own copied `shared_ptr` references or `unique_ptr` factories. Some returned getters allocate new native wrapper state, such as statistics shared-pointer copies and table-property collector wrapper arrays; Java must dispose those according to the corresponding Java wrapper contract.

## Dependencies And Integration Points

- JNI headers and generated Java headers define the exported names and method signatures for `Options`, `ColumnFamilyOptions`, `DBOptions`, `WriteOptions`, `ReadOptions`, `ComparatorOptions`, and `FlushOptions`.
- Core RocksDB option types come from `rocksdb/options.h`, `rocksdb/db.h`, `rocksdb/table.h`, `rocksdb/comparator.h`, `rocksdb/memtablerep.h`, `rocksdb/merge_operator.h`, `rocksdb/rate_limiter.h`, `rocksdb/slice_transform.h`, `rocksdb/sst_partitioner.h`, and `rocksdb/statistics.h`.
- Convenience parsing uses `rocksdb/convenience.h` and `ConfigOptions`.
- Built-in merge operator lookup uses `utilities/merge_operators.h`.
- Java callback integration depends on RocksJNI callback classes and portal helpers: comparator callbacks, logger callbacks, event listener callbacks, WAL/table filters, table-property collector factories, statistics wrappers, `CplusplusToJavaConvert`, and enum conversion helpers in `rocksjni/portal.h`.
- Public Java API integration is through `org.rocksdb.Options`, `ColumnFamilyOptions`, `DBOptions`, and related Java wrappers that hold the `nativeHandle_` values passed into these functions.
- Runtime integration happens when RocksJava passes these populated option objects to DB open, column-family creation, compaction configuration, iterator/read/write paths, and recovery.

## Risks And Edge Cases

- Most setters trust the incoming `jlong` handle type. Passing a stale handle or a handle for the wrong option class can corrupt memory because the code uses `reinterpret_cast` without runtime type checks.
- Many numeric setters cast signed Java values to unsigned or narrower native types. A subset uses `JniUtil::check_if_jlong_fits_size_t()`, but many fields do not reject negative Java values before casting to `uint64_t`, `size_t`, or `uint32_t`.
- `Options.setDbPaths` and `DBOptions.setDbPaths` index the target-size array in parallel with the path array without the length check used by `rocksdb_convert_cf_paths_from_java_helper()`.
- `dbPaths()` and `cfPaths()` assume the caller-provided Java output arrays are at least as long as the native vector length being read. Bounds failures are handled as Java exceptions after the attempted write, but native code has already indexed `opt->*_paths[i]` according to the Java array length.
- Some readback functions write `DbPath::target_size` into a `jlong` array through `static_cast<jint>`, which can truncate large target sizes.
- Raw callback fields (`Comparator*`, `CompactionFilter*`, `WalFilter*`, table filters) require Java-side lifetime discipline. The options object does not copy or own all of these callback objects.
- `setMemTableFactory` and `setTableFactory` transfer raw pointer ownership into `unique_ptr` fields. Reusing the same native factory handle elsewhere after transfer risks double deletion or use-after-free.
- Event listener readback assumes every stored listener is an `EventListenerJniCallback` and `static_cast`s from `EventListener*`; native C++ listeners added in the future would break that assumption.
- Logger setters validate unknown logger type bytes, but comparator-type setters do not throw on unknown bytes and can leave the comparator null.
- Several getters allocate new native wrappers or arrays of wrapper handles. Leaks are possible if Java code does not dispose returned wrapper handles.
- Parse-from-string APIs return `0` on invalid input rather than throwing here. Java callers must translate or check the zero handle correctly.
- The chunk contains many duplicated `Options`, `ColumnFamilyOptions`, and `DBOptions` setters. A field added to one class can easily be missed in the others, causing Java API drift from C++ options.

## Test Signals

- RocksJava option lifecycle tests should cover constructor/copy/dispose paths for `Options`, `ColumnFamilyOptions`, and `DBOptions`, including constructing combined `Options` from separate DB/CF options.
- Property-string tests should cover successful and failed `getColumnFamilyOptionsFromProps` and `getDBOptionsFromProps`, with and without explicit `ConfigOptions`, and confirm failed parses do not return live handles.
- JNI conversion tests should exercise DB paths, CF paths, compression-per-level arrays, max-bytes multiplier arrays, event listener arrays, and table-property collector factory arrays, including mismatched lengths and large target sizes.
- Enum mapping tests should cover compression type, bottommost compression, blob compression, compaction style, compaction priority, WAL recovery mode, and prepopulate blob cache values round-tripping through Java bytes.
- Ownership tests should verify Java callback objects remain usable when assigned as comparators, merge operators, compaction filters/factories, WAL filters, loggers, event listeners, table filters, and table-property collectors.
- Option behavior tests should open DBs with configured values and observe effects: create-if-missing, missing column-family creation, WAL directories and recovery modes, direct IO/mmap flags, rate limiting, statistics persistence, row cache, compaction options, blob options, prefix extractors, and table/memtable factories.
- Boundary tests should include negative Java values for unsigned native fields, `size_t` overflow checks where implemented, large path target sizes, invalid logger/comparator type bytes, null or disposed native handles, and Java exceptions raised during string or array conversion.
