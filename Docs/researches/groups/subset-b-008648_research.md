# subset-b-008648 RocksJNI research

Grouped source-aligned research report for the subset B work item. Each section is delimited for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/checkpoint.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/checkpoint.cc

## Purpose
Exposes `org.rocksdb.Checkpoint` creation, destruction, checkpoint directory creation, and column-family export. Important entry points are `newCheckpoint`, `disposeInternalJni`, `createCheckpoint`, and `exportColumnFamily`.

## Important APIs and Types
Checkpoint Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`newCheckpoint` casts a Java `long` DB handle to `rocksdb::DB*`, calls `Checkpoint::Create`, and returns the raw `Checkpoint*`. `createCheckpoint` converts a Java path with `GetStringUTFChars`, calls `CreateCheckpoint`, releases the string, then maps non-OK `Status` to `RocksDBExceptionJni`. `exportColumnFamily` also casts a `ColumnFamilyHandle*`, receives an allocated `ExportImportFilesMetaData*`, and returns its pointer to Java.

## State and Persistence Behavior
Native state is owned through Java handles. `Checkpoint*` is deleted here; exported metadata must be deleted by its own JNI wrapper. The checkpoint/export operations persist RocksDB files on the filesystem, but this file only forwards paths and errors.

## Dependencies and Integration Points
Depends on `rocksdb/utilities/checkpoint.h`, `rocksdb/db.h`, `portal.h`, and pointer conversion macros. Risks are unchecked `Checkpoint::Create` status, null DB/CF handles, and ensuring strings are always released. Tests should cover invalid paths, export disposal, and Java exception propagation.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/checkpoint.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/clock_cache.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/clock_cache.cc

## Purpose
Creates and disposes Java-owned `std::shared_ptr<rocksdb::Cache>` instances wrapping `NewClockCache`. The sole constructor JNI method is `ClockCache.newClockCache(capacity, shardBits, strictCapacityLimit)`.

## Important APIs and Types
ClockCache Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Control flow is a direct parameter cast to `size_t`, `int`, and `bool`, then allocation of a heap `shared_ptr<Cache>`. Disposal deletes only the wrapper `shared_ptr`, letting shared ownership release the underlying cache when references drain.

## State and Persistence Behavior
No persistence is introduced; state is cache-resident memory and RocksDB cache metadata. Java sees only an opaque handle.

## Dependencies and Integration Points
Integration is with RocksDB's experimental clock cache implementation and Java `Cache` options. Risks include negative Java capacity becoming a huge `size_t`, invalid shard bits, and misuse after disposal. Tests should create with boundary values and verify ColumnFamilyOptions can consume and release the cache.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/clock_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/columnfamilyhandle.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/columnfamilyhandle.cc

## Purpose
Implements Java accessors for a native `ColumnFamilyHandle`: `getName`, `getID`, `getDescriptor`, and disposal.

## Important APIs and Types
ColumnFamilyHandle Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Each accessor casts the opaque handle. `getName` copies the C++ string to a byte array, `getID` returns the 32-bit id, and `getDescriptor` fills a local `ColumnFamilyDescriptor`, constructs the Java descriptor on success, or throws `RocksDBExceptionJni` on failure.

## State and Persistence Behavior
The handle represents live DB column-family state; deletion here releases the native `ColumnFamilyHandle` object but does not delete on-disk column-family data. Descriptor construction snapshots options at call time.

## Dependencies and Integration Points
Depends on `portal.h` converters. Risks are double-free if Java ownership rules are violated, null handles, and descriptor conversion drift as RocksDB options evolve. Test signals include descriptor round trips, close/dispose order, and failure after DB/CF invalidation.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/columnfamilyhandle.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compact_range_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compact_range_options.cc

## Purpose
Wraps `rocksdb::CompactRangeOptions` with extra native storage for pointer fields Java cannot safely own directly: `full_history_ts_low` and `canceled`.

## Important APIs and Types
CompactRangeOptions Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The custom `Java_org_rocksdb_CompactRangeOptions` object contains the real options plus a `std::string` timestamp buffer and `std::atomic<bool>`. JNI getters/setters map booleans, integer levels, path ids, subcompactions, `BottommostLevelCompaction`, timestamp start/range encoded with fixed64, and cancellation state. The constructor returns the address of the embedded `compactRangeOptions`; disposal reconstructs the wrapper pointer and deletes it.

## State and Persistence Behavior
State is purely in-memory options consumed later by manual compaction calls. `canceled` can be observed by RocksDB while compaction runs, so atomic storage and lifetime are important.

## Dependencies and Integration Points
Depends on `rocksdb/options.h`, `portal.h` enum helpers, and `util/coding.h`. Major risk: `set_full_history_ts_low` allocates a new `Slice` each call without freeing the previous one, and returning the embedded field pointer relies on it being the first member. Tests should cover timestamp round trip, cancellation during compaction, and leak checks for repeated setters.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compact_range_options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_filter.cc

## Purpose
Contains the native disposer for Java-backed compaction filters.

## Important APIs and Types
AbstractCompactionFilter disposal bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`AbstractCompactionFilter.disposeInternal` casts the handle to `CompactionFilterJniCallback*` and deletes it. The actual filter logic lives in the callback class elsewhere.

## State and Persistence Behavior
State is callback-owned global Java references and any Java filter object reachable through them. There is no persistence, but compaction may call the filter while files are being rewritten.

## Dependencies and Integration Points
Depends on the callback type and JNI lifecycle discipline. Risk centers on deleting a filter still referenced by an active compaction or shared factory output. Tests should close filters after DB shutdown and exercise filter invocation during compaction.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory.cc

## Purpose
Creates and disposes a shared pointer to `CompactionFilterFactoryJniCallback` for Java factories.

## Important APIs and Types
AbstractCompactionFilterFactory bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`createNewCompactionFilterFactory0` allocates a callback with the Java factory object, wraps it in `std::shared_ptr`, then heap-allocates the `shared_ptr` for Java handle storage. Disposal deletes the heap wrapper, reducing shared ownership.

## State and Persistence Behavior
The factory persists as long as RocksDB options keep the shared pointer. It creates per-compaction filter instances through the callback file.

## Dependencies and Integration Points
Integration is with `CompactionFilterFactory` in column-family options. Risks include Java callback exceptions during factory construction and stale Java objects if disposal happens while DB still owns a shared copy. Tests should use Java factories, dispose options/DB in different orders, and verify no callbacks after close.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory_jnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory_jnicallback.cc

## Purpose
Implements the C++ `CompactionFilterFactory` subclass that calls Java for `name()` and `createCompactionFilter()`.

## Important APIs and Types
CompactionFilterFactory JNI callback implementation. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The constructor caches Java method IDs and copies the factory name. `Name()` returns the cached C string. `CreateCompactionFilter` attaches the current thread as needed, calls the Java factory with context arguments, reads the returned Java filter's native handle, wraps it as `std::unique_ptr<CompactionFilter>`, and releases the JNI environment.

## State and Persistence Behavior
Persistent state is the global Java factory reference inherited from `JniCallback`, cached method ids, and cached name. Each created filter becomes native-owned by RocksDB compaction for that compaction run.

## Dependencies and Integration Points
Depends on `portal.h` factory/filter helpers and `JniCallback`. Risks are exception handling from Java callbacks, returned null filters, ownership transfer of a Java-created native handle, and thread attach/detach correctness. Tests should force Java factory exceptions and verify compaction handles null or thrown callbacks predictably.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory_jnicallback.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory_jnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory_jnicallback.h

## Purpose
Declares the bridge class deriving from `JniCallback` and `rocksdb::CompactionFilterFactory`.

## Important APIs and Types
CompactionFilterFactoryJniCallback declaration. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The header exposes a constructor, `Name()`, and `CreateCompactionFilter(const Context&)`, plus private fields for cached `jmethodID`s and factory name.

## State and Persistence Behavior
State consists of JNI global callback ownership inherited from `JniCallback` and cached IDs/name for repeated background compaction calls.

## Dependencies and Integration Points
Integration is consumed by `compaction_filter_factory.cc` and RocksDB option wiring. Risks are ABI/API drift when Java factory methods or RocksDB `Context` change. Header-level tests are compile/link coverage plus Java factory behavior tests.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_filter_factory_jnicallback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_job_info.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_job_info.cc

## Purpose
Wraps `rocksdb::CompactionJobInfo` for Java event listeners and manual inspection.

## Important APIs and Types
CompactionJobInfo Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Constructs/deletes a native info object and exposes column-family name, status, thread/job ids, input/output levels, input/output file lists, table properties map, compaction reason, compression type, and stats. Maps use `HashMapJni`, Java strings, and `TablePropertiesJni`; stats returns a new copied `CompactionJobStats` handle.

## State and Persistence Behavior
This is an in-memory snapshot of a compaction event. It references file names and table properties describing persisted SST outputs but does not mutate state.

## Dependencies and Integration Points
Depends on status, compression, compaction reason, table properties, and stats converters. Risks include large maps/lists causing OOM, local reference pressure, and stale pointer use after disposal. Tests should validate listener-created info fields for successful and failed compactions.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_job_info.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_job_stats.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_job_stats.cc

## Purpose
Provides constructors, mutation helpers, and field accessors for `rocksdb::CompactionJobStats`.

## Important APIs and Types
CompactionJobStats Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`newCompactionJobStats`, `disposeInternalJni`, `reset`, and `add` manage the native struct. Accessors return elapsed time, input/output record and file counts, bytes, deletion/corruption counters, file I/O nanoseconds, output key prefixes, and single-delete diagnostics.

## State and Persistence Behavior
State is a native stats aggregate copied or accumulated in memory. It summarizes compaction work that rewrote persisted SSTs, but does not itself persist anything.

## Dependencies and Integration Points
Depends mainly on `CompactionJobStats` layout and `JniUtil::copyBytes`. Risks are Java/native field drift, unsigned-to-signed narrowing in `jlong`, and null handles. Tests should compare Java values against event-listener stats and verify `reset`/`add` semantics.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_job_stats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_options.cc

## Purpose
Exposes native `rocksdb::CompactionOptions` for manual compaction calls.

## Important APIs and Types
CompactionOptions Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The file allocates/deletes the options struct and maps compression type, output file size limit, and max subcompactions through simple getters/setters. Compression uses `CompressionTypeJni` enum conversion.

## State and Persistence Behavior
Options state is in-memory and affects future compaction output layout/compression. It has no standalone persistence.

## Dependencies and Integration Points
Integration is with Java manual compaction APIs. Risks include enum drift, negative size/subcompaction values cast to unsigned or wider native types, and options used after disposal. Tests should validate manual compaction observes compression and file-size choices.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_options_fifo.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_options_fifo.cc

## Purpose
Wraps `rocksdb::CompactionOptionsFIFO` for FIFO compaction style configuration.

## Important APIs and Types
CompactionOptionsFIFO Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
JNI methods allocate the struct, expose `max_table_files_size`, `allow_compaction`, `max_table_files_size`/`max_data_files_size`, `ttl`, and `age_for_warm`, plus `use_kv_ratio_compaction`, then delete the struct on dispose.

## State and Persistence Behavior
The struct is transient configuration that influences future FIFO compaction and file deletion. Persistent effects are indirect through RocksDB deciding which SSTs to keep or compact.

## Dependencies and Integration Points
Depends on RocksDB options layout. Risks include Java values outside native ranges and field-name/API drift. Tests should run FIFO-style DBs with configured limits and verify compaction/deletion behavior.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_options_fifo.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_options_universal.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compaction_options_universal.cc

## Purpose
Exposes universal compaction tuning through JNI.

## Important APIs and Types
CompactionOptionsUniversal Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Allocates/deletes `CompactionOptionsUniversal` and maps size ratio, min/max merge width, max size amplification percent, compression size percent, stop style enum, and allow-trivial-move.

## State and Persistence Behavior
State is in-memory options consumed by column-family options; persistence impact is indirect through generated SST layout and compaction scheduling.

## Dependencies and Integration Points
Depends on `CompactionStopStyleJni` conversion. Risks include invalid enum bytes and signed Java values used for unsigned thresholds. Tests should verify Java setters round-trip and a universal-compaction DB opens with the configured options.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compaction_options_universal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/comparator.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/comparator.cc

## Purpose
Creates a native `ComparatorJniCallback` for Java comparators and exposes whether the callback uses direct buffers.

## Important APIs and Types
AbstractComparator Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`createNewComparator` builds `ComparatorJniCallbackOptions` from Java booleans/enum values, allocates the callback, wraps it in `std::shared_ptr<Comparator>`, and returns the wrapper pointer. `usingDirectBuffers` reads callback options from an existing handle. Native comparator disposal deletes the shared pointer wrapper.

## State and Persistence Behavior
Comparator state is long-lived in DB/column-family options and affects key ordering, SST layout, and read correctness. It must outlive every DB component that uses it.

## Dependencies and Integration Points
Depends on `comparatorjnicallback.*` and Java bridge method IDs. Risks are catastrophic if Java comparison is inconsistent, if disposal outpaces DB use, or if direct-buffer reuse is unsafely synchronized. Tests need comparator ordering, DB reopen with comparator name, and concurrent read/write paths.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/comparator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/comparatorjnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/comparatorjnicallback.cc

## Purpose
Implements RocksDB `Comparator` by calling Java comparator methods, including optimized direct-buffer reuse paths.

## Important APIs and Types
ComparatorJniCallback implementation. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The constructor caches class refs, method IDs, Java name, and optional reusable buffers. `Compare` prepares buffers, optionally locks based on reuse synchronization mode, calls Java `compareInternal`, checks exceptions, and returns the result. `FindShortestSeparator` and `FindShortSuccessor` call Java bridge methods and copy changed bytes back into C++ strings. Helper methods allocate/reuse/delete direct byte buffers.

## State and Persistence Behavior
State includes global refs, method IDs, cached name, callback object, optional buffers, thread-local buffer holders, and mutex/unsafe reuse policy. Comparator decisions shape all persisted key ordering in SSTs and memtables.

## Dependencies and Integration Points
Dependencies include `JniCallback`, `portal.h`, `ByteBufferJni`, and `port::Mutex`. Risks are Java exception handling inside `noexcept` comparator paths, local/global ref leaks, invalid direct buffer lifetimes, comparator inconsistency, and synchronization mode misuse. Tests should stress concurrent comparison, separator/successor mutation, exception callbacks, and direct vs byte-array modes.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/comparatorjnicallback.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/comparatorjnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/comparatorjnicallback.h

## Purpose
Defines `ReusedSynchronisationType`, `ComparatorJniCallbackOptions`, and the `ComparatorJniCallback` class interface.

## Important APIs and Types
ComparatorJniCallback declarations. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The options record captures direct-buffer use, reuse-buffer use, max reusable size, and synchronization strategy. The class declares RocksDB comparator overrides plus buffer-management helpers and JNI cached fields.

## State and Persistence Behavior
Persistent state is comparator identity/name and Java callback references; reuse buffers are in-memory optimization state. Comparator identity is persisted indirectly in DB metadata through the comparator name.

## Dependencies and Integration Points
This header is the ABI contract for `comparator.cc` and `comparatorjnicallback.cc`. Risks are option default changes, thread-safety policy drift, and mismatched Java bridge signatures. Tests should compile all modes and run DB operations with every reuse/synchronization option.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/comparatorjnicallback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compression_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/compression_options.cc

## Purpose
Wraps `rocksdb::CompressionOptions` fields used by Java compression configuration.

## Important APIs and Types
CompressionOptions Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Allocates/deletes the struct and exposes window bits, level, strategy, max dictionary bytes, zstd max train bytes, max dict buffer bytes, zstd dict trainer enablement, and general enabled flag.

## State and Persistence Behavior
All state is in-memory configuration that affects future block compression and dictionary training. Persistent impact is indirect in SST compression format and size.

## Dependencies and Integration Points
Depends on RocksDB compression option fields. Risks are value-range mismatch with specific compression libraries and Java/native field drift. Tests should round-trip setters and create compressed SSTs with zstd dictionary options enabled/disabled.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/compression_options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/concurrent_task_limiter.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/concurrent_task_limiter.cc

## Purpose
Creates and manages `std::shared_ptr<ConcurrentTaskLimiter>` for Java code.

## Important APIs and Types
ConcurrentTaskLimiter Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Constructor converts a Java name to `std::string`, calls `NewConcurrentTaskLimiter`, wraps the shared pointer on heap, and returns it. Accessors expose name, max outstanding task mutation/reset, outstanding task count, and disposal of the wrapper.

## State and Persistence Behavior
Limiter state is shared in memory and can be referenced by RocksDB background work. It does not persist across process restart.

## Dependencies and Integration Points
Depends on `JniUtil` string conversion and RocksDB task limiter API. Risks include null name conversion, negative limits, lifetime while DB options hold shared refs, and concurrency races in user expectations. Tests should validate limit changes under concurrent compaction/flush scheduling.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/concurrent_task_limiter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/config_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/config_options.cc

## Purpose
Wraps `rocksdb::ConfigOptions` for parsing and stringifying RocksDB option configurations.

## Important APIs and Types
ConfigOptions Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
JNI methods allocate/delete `ConfigOptions`, set `env`, delimiter, ignore-unknown-options, input-strings-escaped, and sanity level via `SanityLevelJni`. `setDelimiter` copies a Java string into the native delimiter field.

## State and Persistence Behavior
State is parser configuration only; persistence effects occur when other APIs use it to load/save option strings or files.

## Dependencies and Integration Points
Depends on Env handles and portal enum converters. Risks are dangling `env` pointer if Java disposes the env too early, delimiter encoding surprises, and sanity-level enum drift. Tests should parse option strings with custom delimiter and invalid options.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/config_options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cplusplus_to_java_convert.h -->
# sources/storage-engines/rocksdb/java/rocksjni/cplusplus_to_java_convert.h

## Purpose
Provides the canonical pointer-to-`jlong` macro used throughout RocksJNI.

## Important APIs and Types
C++ pointer conversion helpers. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The header defines `GET_CPLUSPLUS_POINTER` as a `reinterpret_cast<jlong>` of a C++ pointer. It is intentionally small but central to every opaque native handle crossing the JNI boundary.

## State and Persistence Behavior
It stores no state and persists nothing; it defines handle representation for Java-owned native state.

## Dependencies and Integration Points
All bridge files depend on this convention. Risks are portability if pointer width exceeds `jlong`, misuse with non-pointer values, and lack of type safety. Test signal is broad JNI handle construction/disposal coverage on supported architectures.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/cplusplus_to_java_convert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/env.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/env.cc

## Purpose
Exposes RocksDB `Env` operations and env wrappers to Java: default env, background thread controls, thread list, memory env, and timed env.

## Important APIs and Types
Env Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Default env returns `Env::Default()` without ownership. `RocksEnv.disposeInternal` deletes only non-default/env wrappers. Thread methods cast priority enums and call background-thread APIs. `getThreadList` fills a vector of `ThreadStatus`, builds a Java array, and throws on non-OK status. `RocksMemEnv` and `TimedEnv` allocate wrapper envs and delete them on dispose.

## State and Persistence Behavior
Env state governs filesystem and background execution. Memory env stores file contents in process memory; timed env wraps another env for timing instrumentation. Persistent behavior is indirect through all DB file I/O.

## Dependencies and Integration Points
Depends on Env APIs, memory/timed env utilities, `ThreadStatusJni`, and priority converters. Risks include deleting an env still used by DB/options, treating default env as owned, thread-list local refs/OOM, and wrapper env lifetimes tied to base env. Tests should cover default vs wrapper disposal and thread status retrieval.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/env.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/env_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/env_options.cc

## Purpose
Wraps `rocksdb::EnvOptions`, including construction from defaults or `DBOptions`, file I/O flags, sync/readahead sizes, buffer sizes, and rate limiter pointer.

## Important APIs and Types
EnvOptions Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
JNI methods allocate from default constructor or `DBOptions`, delete the struct, and expose mmap/direct read/write booleans, fallocate, close-on-exec, bytes-per-sync, keep-size fallocate, compaction readahead, writable-file buffer size, and rate limiter assignment.

## State and Persistence Behavior
State is transient file I/O configuration passed into RocksDB file operations. It affects how persisted SST/WAL files are opened and written but does not persist itself.

## Dependencies and Integration Points
Depends on `EnvOptions`, `DBOptions`, and rate-limiter handle conventions. Risks include dangling `RateLimiter*`, platform-specific unsupported flags, and negative Java sizes cast to `size_t`/`uint64_t`. Tests should round-trip fields and exercise direct/mmap options where supported.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/env_options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/event_listener.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/event_listener.cc

## Purpose
Creates and disposes Java-backed RocksDB `EventListener` instances.

## Important APIs and Types
AbstractEventListener Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`createNewEventListener` converts an enabled-callback bitset/enum from Java, allocates `EventListenerJniCallback`, wraps it in `std::shared_ptr<EventListener>`, and returns the wrapper pointer. Disposal deletes the heap shared pointer wrapper.

## State and Persistence Behavior
Listeners are long-lived in DB options and observe flush, compaction, file I/O, errors, and recovery. They hold Java references but do not persist state themselves.

## Dependencies and Integration Points
Depends on `event_listener_jnicallback.*` and enabled callback conversion. Risks are callbacks after Java object disposal, thread attachment, and event-method signature drift. Tests should register listeners with selective enabled callbacks and verify callback count/ordering.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/event_listener.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/event_listener_jnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/event_listener_jnicallback.cc

## Purpose
Implements RocksDB event callbacks by dispatching to Java listener methods.

## Important APIs and Types
EventListenerJniCallback implementation. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Constructor caches method IDs for enabled events. Each `On...` method checks enabled flags, prepares Java event info objects through portal converters, attaches the thread, calls the Java method, checks/describes exceptions, and cleans local refs. File I/O completion callbacks share `OnFileOperation`; background error and recovery callbacks can pass mutable status objects back to Java.

## State and Persistence Behavior
State is inherited Java global callback reference plus cached method IDs and enabled-event mask. It observes persisted-file lifecycle events but does not own DB state. Some callbacks run on RocksDB background threads.

## Dependencies and Integration Points
Depends heavily on `portal.h` event-info converters and `JniCallback`. Risks include exception swallowing/printing rather than propagating, local reference leaks under high event volume, callback reentrancy, and mutable status handling in error callbacks. Tests should stress all enabled callback bits, background-thread events, and Java exceptions.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/event_listener_jnicallback.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/event_listener_jnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/event_listener_jnicallback.h

## Purpose
Defines the enabled callback bit flags and C++ listener class that bridges RocksDB events to Java.

## Important APIs and Types
EventListenerJniCallback declarations. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The header enumerates callback bits for flush, table file events, compaction, memtable, CF deletion, ingestion, background errors, stalls, file I/O, and recovery. The class declares overrides for all corresponding `EventListener` hooks plus helper methods for method-ID initialization and callback setup/cleanup.

## State and Persistence Behavior
State is the enabled mask and cached Java method IDs. No persistence, but listener decisions can influence error recovery if Java mutates status in supported callbacks.

## Dependencies and Integration Points
Integration is with `event_listener.cc` and RocksDB DBOptions listeners. Risks are bitmask drift with Java constants and missing method IDs for newly added events. Tests should compile against every declared override and verify disabled events do not call Java.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/event_listener_jnicallback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/export_import_files_metadatajni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/export_import_files_metadatajni.cc

## Purpose
Contains the disposer for metadata returned by checkpoint column-family export.

## Important APIs and Types
ExportImportFilesMetaData disposal bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`ExportImportFilesMetaData.disposeInternal` casts the opaque handle to `ExportImportFilesMetaData*` and deletes it.

## State and Persistence Behavior
The metadata describes exported SST files for later import. This file only manages the in-memory metadata object; exported files remain on disk.

## Dependencies and Integration Points
Depends on `rocksdb/utilities/checkpoint.h`. Risk is double-free or leak if Java import/export APIs disagree on ownership. Tests should export a column family, inspect/use metadata, then dispose exactly once.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/export_import_files_metadatajni.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/filter.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/filter.cc

## Purpose
Creates and disposes native filter policies, currently Bloom filters.

## Important APIs and Types
Filter policy Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`BloomFilter.createNewBloomFilter(bitsPerKey, useBlockBasedMode)` calls `NewBloomFilterPolicy`, wraps the returned filter policy in `std::shared_ptr<const FilterPolicy>`, and returns a heap pointer to that shared pointer. Generic `Filter.disposeInternalJni` deletes the shared pointer wrapper.

## State and Persistence Behavior
Filter policy state is configuration used by table builders/readers. Persistent impact is indirect: generated SST filter blocks encode the selected policy.

## Dependencies and Integration Points
Depends on RocksDB filter policy API. Risks include invalid bits-per-key, use after disposal while options still refer to the shared policy, and compatibility of persisted SST filter blocks. Tests should open DB with Bloom filter, query misses, and dispose after DB close.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/filter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/hyper_clock_cache.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/hyper_clock_cache.cc

## Purpose
Creates and disposes `std::shared_ptr<Cache>` wrapping `HyperClockCacheOptions::MakeSharedCache`.

## Important APIs and Types
HyperClockCache Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Constructor fills options from capacity, estimated entry charge, shard bits, memory allocator handle, and strict capacity limit; then returns a heap shared pointer. Disposal deletes the shared pointer wrapper.

## State and Persistence Behavior
State is in-memory cache state. The optional memory allocator may be shared external state and must outlive cache creation/use.

## Dependencies and Integration Points
Depends on hyper clock cache API and memory allocator handle convention. Risks include null or stale allocator handles, negative capacity/charge casts, and option compatibility across RocksDB versions. Tests should construct with and without allocator and run block-cache reads.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/hyper_clock_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/import_column_family_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/import_column_family_options.cc

## Purpose
Wraps `rocksdb::ImportColumnFamilyOptions`, currently exposing `move_files`.

## Important APIs and Types
ImportColumnFamilyOptions Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
JNI methods allocate/delete the struct and set/get the `move_files` boolean controlling whether imported files are moved or copied.

## State and Persistence Behavior
Options are transient but directly affect filesystem persistence during column-family import: move can transfer ownership of files, while copy leaves source files intact.

## Dependencies and Integration Points
Depends on import-column-family utility API. Risks include data loss expectations around move semantics and use after dispose. Tests should import with move true/false and verify source/destination file existence.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/import_column_family_options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/ingest_external_file_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/ingest_external_file_options.cc

## Purpose
Wraps `rocksdb::IngestExternalFileOptions` for external SST ingestion.

## Important APIs and Types
IngestExternalFileOptions Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Provides default and boolean constructor overloads, getters/setters for `move_files`, `snapshot_consistency`, `allow_global_seqno`, `allow_blocking_flush`, `ingest_behind`, and `write_global_seqno`, plus disposal.

## State and Persistence Behavior
These options directly affect persisted external-file ingestion: moving/copying files, sequence-number assignment, snapshot guarantees, flushing, and ingest-behind behavior.

## Dependencies and Integration Points
Depends on RocksDB ingestion API. Risks are combinations that can violate user expectations for snapshots or file ownership, and Java boolean constructor drift when fields are added. Tests should ingest generated SSTs across option combinations and verify sequence/snapshot behavior.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/ingest_external_file_options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/iterator.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/iterator.cc

## Purpose
Implements Java iterator movement, seeking, status checks, and key/value extraction for byte arrays and direct buffers.

## Important APIs and Types
RocksIterator Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Movement methods cast the handle and call `SeekToFirst`, `SeekToLast`, `Next`, `Prev`, `Refresh`, `Seek`, and `SeekForPrev`. Seek overloads copy Java byte arrays or validate direct buffers via `JniUtil`. `status0Jni` throws on non-OK iterator status. Key/value methods return new byte arrays or copy into caller-provided direct/byte-array buffers and return the full native slice length.

## State and Persistence Behavior
Iterator state is native cursor state over a DB snapshot/read options. It does not persist data but exposes persisted keys/values and can become invalid as DB state changes unless refreshed.

## Dependencies and Integration Points
Depends on `portal.h` and JNI buffer helpers. Risks include reading key/value when invalid, buffer-size truncation semantics, direct buffer validation, exception handling for refresh/status, and iterator use after DB/CF close. Tests should cover all seek/copy overloads, small target buffers, invalid iterator status, and refresh with snapshots.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/iterator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jni_multiget_helpers.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/jni_multiget_helpers.cc

## Purpose
Implements reusable helpers for RocksDB Java MultiGet paths: key extraction, value/status materialization, and column-family handle validation.

## Important APIs and Types
MultiGet JNI helper implementation. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`MultiGetJNIKeys` builds vectors of `Slice` and backing storage from Java byte arrays or byte buffers. `MultiGetJNIValues::byteArrays` turns `PinnableSlice` results into Java 2D arrays with per-key status handling. `fillByteBuffersAndStatusObjects` copies into direct buffers, marks incomplete when buffers are too small, and fills Java status objects. `ColumnFamilyJNIHelpers` validates handle arrays and single handles.

## State and Persistence Behavior
State is per-call stack/heap vectors retaining key backing memory until the RocksDB call completes. It does not persist, but handles pinned values and statuses from reads.

## Dependencies and Integration Points
Depends on `JniUtil`, `StatusJni`, `ByteJni`, and RocksDB `PinnableSlice`. Risks include local ref pressure for large batches, direct buffer capacity truncation, mismatched CF/key counts, and keeping slices beyond backing storage lifetime. Tests should cover byte-array and direct-buffer MultiGet, partial buffers, null CF arrays, and non-OK statuses.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jni_multiget_helpers.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jni_multiget_helpers.h -->
# sources/storage-engines/rocksdb/java/rocksjni/jni_multiget_helpers.h

## Purpose
Declares helper classes `MultiGetJNIKeys`, `MultiGetJNIValues`, and `ColumnFamilyJNIHelpers` for Java MultiGet implementations.

## Important APIs and Types
MultiGet JNI helper declarations. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The key helper owns arrays/vectors and exposes `data()`/`size()` for RocksDB calls. The value helper declares byte-array and byte-buffer materialization APIs. Column-family helpers declare conversion from `jlongArray` and single handles into native pointer vectors or status errors.

## State and Persistence Behavior
The classes manage per-call transient memory only. Correct lifetime is crucial because `Slice` entries reference storage owned by the helper.

## Dependencies and Integration Points
Integration is with RocksDB Java DB MultiGet JNI files. Risks are accidental copying/moving that invalidates slice pointers, count mismatches, and status-vector ownership confusion. Tests should include compile coverage plus MultiGet behavior with varying key counts and CF handles.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jni_multiget_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jni_perf_context.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/jni_perf_context.cc

## Purpose
Exposes RocksDB thread-local `PerfContext` counters to Java through a large set of primitive getters plus reset and string conversion.

## Important APIs and Types
PerfContext Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Every getter casts a `PerfContext*` handle and returns one field as `jlong`; `reset` calls `Reset()`, and `toString` returns the native `ToString()` result as a Java string. Covered fields span block/cache reads, blob reads, skipped internal keys, memtable/output-file timing, write timing, DB mutex waits, table iterator timings, bloom hits/misses, Env operation timings, CPU timings, encryption/decryption, and async seek count.

## State and Persistence Behavior
State is thread/perf-context memory, usually tied to RocksDB perf instrumentation. It is observational and non-persistent.

## Dependencies and Integration Points
Depends on exact `PerfContext` struct fields. Main risk is native/Java drift when fields are added/removed or renamed; this file is mechanically repetitive and easy to miss in upgrades. Tests should enable perf level, perform reads/writes/seeks, verify nonzero expected counters, reset behavior, and `toString` conversion.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jni_perf_context.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/jnicallback.cc

## Purpose
Provides shared global-reference and thread-attachment behavior for Java-backed C++ callback classes.

## Important APIs and Types
JniCallback base implementation. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The constructor stores the current `JavaVM` and creates a global ref to the Java callback object. `getJniEnv` and `releaseJniEnv` delegate to `JniUtil` for thread attach/detach tracking. The destructor attaches if needed, deletes the global ref, and releases the environment.

## State and Persistence Behavior
State is a global Java object reference and VM pointer held by native callback objects. This is non-persistent but controls callback object lifetime across RocksDB background threads.

## Dependencies and Integration Points
Used by comparator, logger, event listener, and compaction filter factory callbacks. Risks are destructor execution after JVM teardown, null global refs on OOM, and mismatched attach/detach flags. Tests should create callbacks invoked from background threads and dispose them without leaks.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jnicallback.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/jnicallback.h

## Purpose
Declares the base class shared by RocksJNI callback bridges.

## Important APIs and Types
JniCallback base declaration. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The class stores `JavaVM*` and `jobject m_jcallback_obj`, declares constructor/destructor, and protected `getJniEnv`/`releaseJniEnv` helpers.

## State and Persistence Behavior
State is callback lifetime metadata only; no persistence. The global reference prevents Java callback collection while native RocksDB may invoke it.

## Dependencies and Integration Points
Integration spans comparator, logger, event listener, and compaction filter factory. Risks are subclasses assuming `m_jcallback_obj` is valid after constructor exceptions and lifecycle during JVM shutdown. Compile tests plus callback lifecycle tests are the primary signal.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jnicallback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/kv_helper.h -->
# sources/storage-engines/rocksdb/java/rocksjni/kv_helper.h

## Purpose
Defines RAII-style helpers for byte-array and direct-buffer key/value transfer plus a `KVException` helper for throwing Java exceptions from low-level buffer code.

## Important APIs and Types
Key/value JNI helper classes. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`JByteArraySlice` and `JDirectBufferSlice` expose Java key memory as RocksDB `Slice`s. `JByteArrayPinnableSlice` and `JDirectBufferPinnableSlice` copy native `PinnableSlice` values into Java byte arrays or direct buffers, returning full native lengths and handling partial copies. `KVException` centralizes throwing RocksDB or argument exceptions.

## State and Persistence Behavior
State is per-call pinned/copy buffers and `PinnableSlice` storage. It is transient and must not outlive JNI local references or Java buffers.

## Dependencies and Integration Points
Depends on `portal.h`, `Slice`, `PinnableSlice`, and JNI array/direct-buffer APIs. Risks include forgetting to release pinned byte arrays, direct buffer null/address validation, buffer truncation semantics, and exception paths in destructors/cleanup. Tests should cover gets into arrays/direct buffers, small buffers, and invalid offsets/lengths.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/kv_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/loggerjnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/loggerjnicallback.cc

## Purpose
Implements RocksDB `Logger` by forwarding log records to a Java `Logger` callback.

## Important APIs and Types
LoggerJniCallback implementation. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The constructor caches the Java `log` method and global refs for all `InfoLogLevel` enum constants. `Logv(level, format, ap)` filters by current log level, formats the varargs message with `vsnprintf`, attaches the thread, creates a Java string, calls Java, describes exceptions, and deletes locals. JNI methods create a shared pointer wrapper, set/get log level, and dispose it. Destructor deletes enum global refs.

## State and Persistence Behavior
Logger state is in-memory level plus Java callback/global enum refs. It observes RocksDB operations but does not persist logs itself unless Java does.

## Dependencies and Integration Points
Depends on `JniCallback`, `LoggerJni`, and `InfoLogLevelJni`. Risks are formatting failures/OOM, Java exceptions being printed not propagated, callback during DB background threads, and global ref cleanup after JVM teardown. Tests should log at every level, change thresholds, and force Java callback exceptions.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/loggerjnicallback.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/loggerjnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/loggerjnicallback.h

## Purpose
Declares the Java-backed RocksDB logger class.

## Important APIs and Types
LoggerJniCallback declaration. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The class derives from `JniCallback` and `Logger`, exposes `GetInfoLogLevel`/`SetInfoLogLevel`, overrides both `Logv` variants, and stores method id plus global refs for Java level enums. A private `format_str` helper builds log messages.

## State and Persistence Behavior
State is logger threshold and cached Java references. No persistence unless Java callback stores messages.

## Dependencies and Integration Points
Integration is with DBOptions logger configuration and `loggerjnicallback.cc`. Risks are method/enum signature drift and inherited callback lifecycle. Tests should compile against Java generated headers and exercise native logging through DB open/write/read paths.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/loggerjnicallback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/lru_cache.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/lru_cache.cc

## Purpose
Creates and disposes Java-owned shared pointers to RocksDB LRU cache instances.

## Important APIs and Types
LRUCache Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`newLRUCache` calls `NewLRUCache` with capacity, shard bits, strict capacity, high-priority pool ratio, default allocator/adaptive mutex/metadata charge policy, and low-priority pool ratio. It returns a heap `std::shared_ptr<Cache>*`; disposal deletes the wrapper.

## State and Persistence Behavior
State is in-memory cache contents and metadata. It is shared through options but not persisted.

## Dependencies and Integration Points
Depends on `cache/lru_cache.h`. Risks include negative capacity/shard bits, ratio validation left to RocksDB, and lifetime while DB options/DB hold shared references. Tests should use high/low-priority pools and verify no leak/double delete on option disposal.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/lru_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/memory_util.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/memory_util.cc

## Purpose
Exposes approximate memory usage by type for sets of DB and cache handles.

## Important APIs and Types
MemoryUtil Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The JNI method converts DB handle arrays via `JniUtil::fromJPointers`, converts cache shared-pointer handles into an unordered set of raw `Cache*`, calls `MemoryUtil::GetApproximateMemoryUsageByType`, constructs a Java `HashMap`, and maps enum keys to boxed bytes and usage values to boxed longs.

## State and Persistence Behavior
State is observational; it reads live DB/cache memory usage and returns a Java map. No persistence.

## Dependencies and Integration Points
Depends on memory util, `HashMapJni`, enum converters, and boxed primitive helpers. Risks include null arrays/handles, caches disposed while queried, non-OK status returning null without Java exception, and local ref cleanup for map entries. Tests should query multiple DBs/caches and validate expected keys are present.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/memory_util.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/memtablejni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/memtablejni.cc

## Purpose
Creates native `MemTableRepFactory` implementations from Java memtable configuration classes.

## Important APIs and Types
MemTable factory Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
Provides constructors for hash skip list, hash linked list, vector, and skip list factories. Each checks Java `long` values fit in `size_t` before allocation, throws `IllegalArgumentExceptionJni` on overflow, and returns raw factory pointers for options ownership.

## State and Persistence Behavior
Factories are in-memory configuration objects used by column-family options; they influence memtable structure for future writes and flushes. Persistent effects are indirect through memtable flush output ordering/performance.

## Dependencies and Integration Points
Depends on `rocksdb/memtablerep.h` and size-check helpers. Risks include ownership transfer clarity, unsupported factory combinations, and parameter range overflow. Tests should create each factory, open DBs with them, and cover overflow exception paths.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/memtablejni.cc -->
