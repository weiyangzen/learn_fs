# Research: subset-b-008655

Grouped research for RocksDB Java JNI bridge files under `sources/storage-engines/rocksdb/java/rocksjni`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/ratelimiterjni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/ratelimiterjni.cc

Purpose: Bridges `org.rocksdb.RateLimiter` to C++ `ROCKSDB_NAMESPACE::RateLimiter`, giving Java code access to construction, disposal, rate updates, blocking requests, and counters.

Important APIs/types/functions: `Java_org_rocksdb_RateLimiter_newRateLimiterHandle` calls `NewGenericRateLimiter` and stores it in a heap `std::shared_ptr<RateLimiter>` handle. `disposeInternalJni` deletes the shared pointer wrapper. `setBytesPerSecond`, `getBytesPerSecond`, `request`, `getSingleBurstBytes`, `getTotalBytesThrough`, and `getTotalRequests` forward to the underlying C++ object. `RateLimiterModeJni::toCppRateLimiterMode` converts the Java enum byte.

Control flow: Java passes primitive configuration and a native handle. The constructor translates the mode, creates the C++ limiter, wraps it, and returns the wrapper address as `jlong`. All later calls reinterpret the handle, dereference the shared pointer, and call RocksDB.

State and persistence behavior: The file owns only native process memory. No disk state is written directly; persistence impact is indirect through throttling RocksDB IO. The Java wrapper must call dispose to release the shared pointer wrapper.

Dependencies and integration points: Includes generated JNI header `org_rocksdb_RateLimiter.h`, `rocksdb/rate_limiter.h`, conversion helpers, and `portal.h`. The handle can be shared with options/configuration objects that accept a rate limiter.

Risks: Handles are unchecked; a stale, zero, or wrong handle will crash or corrupt memory. `request` always uses `Env::IO_TOTAL`, so this binding does not expose a Java-side choice of IO priority/type. Counter values are returned as signed `jlong`, so very large unsigned C++ counters depend on Java-side interpretation.

Test signals: Useful tests create a limiter, verify get/set rate, issue small requests, observe counters increasing, verify mode/auto-tune construction, and ensure dispose is idempotently guarded by the Java owning object.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/ratelimiterjni.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/remove_emptyvalue_compactionfilterjni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/remove_emptyvalue_compactionfilterjni.cc

Purpose: Exposes RocksDB's `RemoveEmptyValueCompactionFilter` utility to Java.

Important APIs/types/functions: `Java_org_rocksdb_RemoveEmptyValueCompactionFilter_createNewRemoveEmptyValueCompactionFilter0` allocates `ROCKSDB_NAMESPACE::RemoveEmptyValueCompactionFilter` and returns its pointer with `GET_CPLUSPLUS_POINTER`.

Control flow: There is a single constructor bridge. Java calls it, C++ allocates the filter, and Java stores the returned handle for use in compaction filter configuration.

State and persistence behavior: The native filter is stateless except for C++ object lifetime. Its effect is persistent only when RocksDB compaction applies it and removes entries whose values are empty.

Dependencies and integration points: Depends on generated `org_rocksdb_RemoveEmptyValueCompactionFilter.h`, `utilities/compaction_filters/remove_emptyvalue_compactionfilter.h`, and JNI pointer conversion. It integrates with compaction filter ownership/disposal logic elsewhere in RocksJNI.

Risks: This file has no disposal entry point, so correctness depends on the Java class hierarchy or another native base disposer deleting the returned filter. A missing disposal path would leak the filter. The bridge performs no error handling because `new` failures surface as native allocation failure rather than a RocksDB `Status`.

Test signals: Tests should configure this filter, compact a DB containing empty and non-empty values, and verify only empty-value keys are removed. Native leak checks should cover repeated create/dispose cycles through the Java wrapper.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/remove_emptyvalue_compactionfilterjni.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/restorejni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/restorejni.cc

Purpose: Bridges Java `RestoreOptions` to C++ `ROCKSDB_NAMESPACE::RestoreOptions` for backup engine restore calls.

Important APIs/types/functions: `Java_org_rocksdb_RestoreOptions_newRestoreOptions` allocates `RestoreOptions(keep_log_files)`. `Java_org_rocksdb_RestoreOptions_disposeInternalJni` asserts the handle and deletes it.

Control flow: Java passes the `keep_log_files` boolean to construction, then passes the returned native handle to backup/restore APIs. Disposal simply reinterprets the handle and deletes it.

State and persistence behavior: The object stores restore behavior only; it does not perform restore or write state itself. The option affects whether WAL/log files survive restore operations in backup engine code.

Dependencies and integration points: Includes generated `org_rocksdb_RestoreOptions.h`, `rocksdb/utilities/backup_engine.h`, and RocksJNI pointer helpers. It integrates with Java backup engine bindings that consume a `RestoreOptions` pointer.

Risks: `assert(ropt)` disappears in release builds, so invalid handles can still crash. The bridge exposes only the constructor boolean visible in this source; any future C++ fields require matching JNI additions.

Test signals: Restore tests should instantiate both `keep_log_files` modes, pass them through backup engine restore, and verify native dispose under leak sanitizers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/restorejni.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/rocks_callback_object.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/rocks_callback_object.cc

Purpose: Provides base disposal for Java callback objects backed by native subclasses of `JniCallback`.

Important APIs/types/functions: `Java_org_rocksdb_RocksCallbackObject_disposeInternal` deletes a native pointer as `ROCKSDB_NAMESPACE::JniCallback*`.

Control flow: Java callback wrappers eventually call the base disposer with a native callback handle. The function relies on virtual destructors so deleting through `JniCallback*` destroys the actual callback subtype.

State and persistence behavior: It frees native callback state, including global Java references owned by `JniCallback`. No persistent storage is touched.

Dependencies and integration points: Includes generated `org_rocksdb_RocksCallbackObject.h` and `jnicallback.h`. It is shared by callback families such as comparators, table filters, trace writers, and listeners.

Risks: The TODO documents the key contract: deletion through the base pointer is only safe if all callback inheritance paths have virtual destructors. Passing a non-`JniCallback` handle or double-disposing will be unsafe. Callback lifetimes must also outlive RocksDB native users.

Test signals: Tests should create and dispose concrete callback subclasses, use ASAN/leak checks, and verify callbacks are not invoked after Java disposal or after RocksDB takes ownership.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/rocks_callback_object.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/rocksdb_exception_test.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/rocksdb_exception_test.cc

Purpose: Native test helper for verifying Java `RocksDBException` construction from strings and C++ `Status` objects.

Important APIs/types/functions: `raiseException` throws with only a message. `raiseExceptionWithStatusCode` and `raiseExceptionNoMsgWithStatusCode` use `Status::NotSupported`. `raiseExceptionWithStatusCodeSubCode` and `raiseExceptionNoMsgWithStatusCodeSubCode` use `Status::TimedOut(kLockTimeout)`. `raiseExceptionWithStatusCodeState` uses `Status::NotSupported(Slice("test state"))`.

Control flow: Each JNI method directly calls `RocksDBExceptionJni::ThrowNew`; no native value is returned. Java tests catch the thrown exception and inspect message, status code, subcode, and state.

State and persistence behavior: No native state is retained and no persistent state is touched.

Dependencies and integration points: Includes generated `org_rocksdb_RocksDBExceptionTest.h`, `rocksdb/status.h`, `rocksdb/slice.h`, and exception conversion helpers from `portal.h`.

Risks: This is test-only surface; production risk is low. Its value depends on staying synchronized with Java exception fields and enum mappings.

Test signals: The file itself is a test signal. Java tests should assert each overload preserves message presence/absence, status code, subcode, and state bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/rocksdb_exception_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/rocksjni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/rocksjni.cc

Purpose: Main JNI bridge for `org.rocksdb.RocksDB`, exposing database open/close, column family management, CRUD, direct-buffer operations, multi-get, iterators, snapshots, properties, compaction, flushing, WAL and live-file metadata, external file ingestion, tracing, secondary catch-up, DB destruction, file deletion by ranges, and version reporting.

Important APIs/types/functions: Open helpers wrap `DB::Open`, `OpenForReadOnly`, and `OpenAsSecondary`, including column family descriptor conversion. CRUD functions bridge `Put`, `Delete`, `SingleDelete`, `DeleteRange`, `Merge`, `Write`, and `Get` variants. `JByteArraySlice`, `JByteArrayPinnableSlice`, `JDirectBufferSlice`, and `JDirectBufferPinnableSlice` from `kv_helper.h` manage key/value marshalling. `MultiGetJNIKeys` and `MultiGetJNIValues` handle byte-array and direct-buffer multi-get. Metadata conversion uses `LogFileJni`, `LiveFileMetaDataJni`, `ColumnFamilyMetaDataJni`, `TablePropertiesJni`, and `HashMapJni`. Admin bridges include `CompactRange`, `CompactFiles`, `Flush`, `FlushWAL`, `SyncWAL`, `GetUpdatesSince`, `IngestExternalFile`, `VerifyChecksum`, `StartTrace`, `EndTrace`, `DestroyDB`, `DeleteFilesInRanges`, and `version`.

Control flow: Most functions reinterpret Java `long` handles into RocksDB pointers, convert Java arrays/strings/buffers into C++ `Slice`, `std::string`, or vectors, call a RocksDB API, then translate `Status` into `RocksDBException` or return Java values. Open calls use `std::unique_ptr<DB>` and release ownership only after successful `Status`. Column-family open returns a `long[]` with the DB handle at index 0 and CF handles after it. `Get` variants distinguish not-found from errors by returning `null` or `KVException` codes. Direct operations delegate to `JniUtil::kv_op_direct` or `k_op_direct`. Snapshot calls simply pass through `GetSnapshot` and `ReleaseSnapshot`.

State and persistence behavior: This bridge directly controls durable RocksDB state through writes, deletes, range deletes, flush/WAL sync, external SST ingestion, compaction, background work control, file deletion disabling/enabling, and DB destruction. Native state lives in returned raw handles for `DB`, `ColumnFamilyHandle`, `Iterator`, `Snapshot`, `TransactionLogIterator`, `Slice`, and callback objects. Snapshot handles are borrowed from the DB and must be released through the same DB.

Dependencies and integration points: Includes RocksDB core headers (`db.h`, `options.h`, `convenience.h`, `perf_context.h`, `version.h`), generated `org_rocksdb_RocksDB.h`, conversion utilities, multi-get helpers, key/value helper classes, and `portal.h`. It is the central integration point for many other RocksJNI handle types: options, read/write options, column families, write batches, compaction options, flush options, ingest options, slices, trace writers, and metadata Java objects.

Risks: The file is handle-heavy and trusts Java ownership discipline; stale or mismatched handles can crash. `closeDatabase` calls `RocksDBExceptionJni::ThrowNew(env, s)` unconditionally after `Close()`, so correctness depends on `ThrowNew` being a no-op for OK statuses. `createColumnFamilyWithImport` checks `j_metadata_handle_array == nullptr` after `GetLongArrayElements`, but the intended null check is likely the returned pointer. `key_may_exist_direct_helper` and `keyExistsDirect` validate offsets but build slices from `key` rather than `key + offset`, so direct-buffer offset handling appears wrong. `getPropertiesOfTablesInRange` builds a `TablePropertiesCollection` but returns `jrange_slice_handles` instead of a Java map, which looks like a clear bridge bug. Several functions use manual `new[]` and early returns, so exception paths need scrutiny. `StartTrace` transfers ownership of the Java-created `TraceWriterJniCallback` to RocksDB; Java must not dispose it after transfer.

Test signals: Coverage should include open/read-only/secondary with and without column families; all CRUD variants across default and explicit CFs; direct-buffer offsets; byte-array offsets; not-found return contracts; multi-get status/value filling; snapshot lifecycle; property and table-property map conversion; compaction/flush/WAL error propagation; external file ingestion; trace writer ownership; destroy/delete-files range behavior; and Java tests specifically targeting the direct-buffer offset and `getPropertiesOfTablesInRange` return-value issues.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/rocksjni.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/slice.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/slice.cc

Purpose: Bridges Java `AbstractSlice`, heap `Slice`, and `DirectSlice` wrappers to C++ `ROCKSDB_NAMESPACE::Slice`.

Important APIs/types/functions: `createNewSliceFromString`, `Slice_createNewSlice0/1`, and `DirectSlice_createNewDirectSlice0/1` construct C++ slices. Shared operations include `size0`, `empty0`, `toString0`, `compare0`, `startsWith0`, and `disposeInternalJni`. Heap-slice operations expose `data0`, `clear0`, `removePrefix0`, and `disposeInternalBuf`. Direct-slice operations expose direct `ByteBuffer` creation, byte access, length mutation, clear/remove-prefix, and buffer disposal.

Control flow: Constructors allocate or reference backing memory, create a `Slice` pointing at it, and return the slice pointer. Data access copies slice bytes into Java arrays or returns a direct byte buffer. Prefix removal and clear mutate `Slice::data_`/`size_` behavior through RocksDB's public/private exposed members in this codebase.

State and persistence behavior: Slice state is in native memory and can either own a heap buffer allocated by the JNI bridge or reference Java direct-buffer memory. No RocksDB persistence occurs directly, but these slices are passed to DB range/property APIs elsewhere.

Dependencies and integration points: Depends on generated slice JNI headers, `rocksdb/slice.h`, pointer conversion, and `portal.h`. Many RocksJNI APIs consume the handles this file creates for ranges, SST writer keys, and suggested compaction ranges.

Risks: Buffer ownership is subtle. `createNewSliceFromString` allocates `len + 1` but constructs `Slice(buf)` relying on null termination. `clear0` and `disposeInternalBuf` compute the allocation base from `slice->data_ - internalBufferOffset`; mismatched offsets can free the wrong address. Direct slices depend on Java direct-buffer lifetime and support; non-direct buffers throw `IllegalArgumentException`. `DirectSlice_createNewDirectSlice1` uses `Slice(ptrData)` and therefore treats the direct buffer as null-terminated rather than using capacity.

Test signals: Tests should verify binary data with embedded zeros, offset disposal after `removePrefix`, direct and heap slice data round-trips, invalid non-direct buffer errors, compare/startsWith semantics, and leak/double-free behavior under sanitizers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/slice.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/snapshot.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/snapshot.cc

Purpose: Exposes `Snapshot::GetSequenceNumber` to Java.

Important APIs/types/functions: `Java_org_rocksdb_Snapshot_getSequenceNumber` reinterprets a snapshot handle and returns `snapshot->GetSequenceNumber()`.

Control flow: Java obtains a snapshot handle from `RocksDB.getSnapshot`, then this method reads its sequence number. Release is handled in `rocksjni.cc`, not here.

State and persistence behavior: Snapshot state is owned by the DB. This file only reads the sequence number and does not mutate persistence.

Dependencies and integration points: Includes generated `org_rocksdb_Snapshot.h`, `rocksdb/db.h`, and `portal.h`. Integrates with the DB snapshot lifecycle in `rocksjni.cc`.

Risks: No null/stale handle checks. Using this after `ReleaseSnapshot` or DB close is unsafe.

Test signals: Tests should assert sequence numbers are stable for a snapshot and increase across writes/new snapshots, and that Java wrappers prevent use after release.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/snapshot.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_manager.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/sst_file_manager.cc

Purpose: Bridges Java `SstFileManager` to C++ `ROCKSDB_NAMESPACE::SstFileManager` for tracking and throttling SST/trash file deletion and space usage.

Important APIs/types/functions: `newSstFileManager` calls `NewSstFileManager` with an `Env`, optional `Logger`, delete rate, trash ratio, and delete chunk size. Accessors/mutators expose max allowed space, compaction buffer size, max-space flags, total size, tracked files map, delete rate, and max trash DB ratio. Disposal deletes the heap `std::shared_ptr<SstFileManager>` wrapper.

Control flow: Constructor receives native `Env` and optional shared logger handles, calls the factory, checks `Status`, and wraps the raw manager in a shared pointer. Map conversion for tracked files builds a Java `HashMap<String,Long>`.

State and persistence behavior: The manager tracks RocksDB-managed SST/trash files and can affect deletion throttling and allowed-space decisions. The file itself stores process-local shared pointer state.

Dependencies and integration points: Depends on `rocksdb/sst_file_manager.h`, generated `org_rocksdb_SstFileManager.h`, conversion utilities, and `portal.h`. The returned shared pointer is typically installed into DB options.

Risks: If `NewSstFileManager` returns an error, the code deletes any non-null raw manager and throws, but still proceeds to allocate and return a shared pointer after throwing; JNI callers will usually observe the pending exception, but the native return path is not guarded by an explicit `return 0`. Map conversion can leak local references on large maps if helper behavior does not clean each pair. Handle misuse remains unsafe.

Test signals: Tests should construct with and without a logger, assert failed construction raises, verify tracked file map conversion, mutate rate/ratio/space settings, and validate disposal under leak checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_manager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_reader_iterator.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/sst_file_reader_iterator.cc

Purpose: Provides Java access to `ROCKSDB_NAMESPACE::Iterator` instances returned by `SstFileReader`.

Important APIs/types/functions: Methods wrap iterator lifecycle (`disposeInternalJni`), movement (`isValid0Jni`, `seekToFirst0Jni`, `seekToLast0Jni`, `next0Jni`, `prev0Jni`), seeking (`seek0Jni`, `seekForPrev0Jni`, direct and byte-array seek variants), status checking, key/value retrieval as arrays, direct-buffer copies, byte-array buffer copies, and `Refresh` with or without a snapshot.

Control flow: Java methods pass the iterator handle. Seek methods convert Java key data into temporary `Slice`s and call `Seek`/`SeekForPrev`. Key/value methods read `it->key()` or `it->value()` and either allocate arrays or copy into caller buffers, returning the full required length for buffer APIs. `status0Jni` and refresh methods translate non-OK statuses into exceptions.

State and persistence behavior: Iterator position and status live in the native iterator. No persistent data is changed. Snapshot refresh can bind the iterator to a supplied snapshot view.

Dependencies and integration points: Includes generated `org_rocksdb_SstFileReaderIterator.h`, `rocksdb/iterator.h`, and `portal.h`. Created by `sst_file_readerjni.cc` and consumed by Java SST inspection APIs.

Risks: Methods assume `Valid()` before key/value access; invalid iterator access is undefined by RocksDB contract. The OOM branches after `new char[jtarget_len]` are ineffective with throwing `new`. The `FindClass` string for OOM is `"/lang/java/OutOfMemoryError"`, which looks malformed. Byte-array copy methods rely on Java to provide valid offsets and do not explicitly check exceptions after `SetByteArrayRegion`.

Test signals: Tests should iterate an SST forward/backward, seek using arrays/direct/byte-buffer paths, verify truncation return lengths, check `status()` after corruption or bad reads, refresh with snapshots, and exercise invalid/non-direct buffers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_reader_iterator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_readerjni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/sst_file_readerjni.cc

Purpose: Bridges Java `SstFileReader` to C++ `ROCKSDB_NAMESPACE::SstFileReader` for offline SST file inspection.

Important APIs/types/functions: `newSstFileReader` constructs from `Options`. `open` opens a file path and throws on non-OK `Status`. `newIterator` returns an iterator for supplied `ReadOptions`. `verifyChecksum` checks file integrity. `getTableProperties` converts C++ `TableProperties` to Java. `disposeInternalJni` deletes the reader.

Control flow: Java creates a reader handle, opens a path, asks for iterators or metadata, and disposes. String paths are copied with `GetStringUTFChars` and released before exception propagation.

State and persistence behavior: The reader owns native open-file/metadata state for an existing SST file. It does not mutate RocksDB state.

Dependencies and integration points: Depends on generated `org_rocksdb_SstFileReader.h`, `rocksdb/sst_file_reader.h`, options/env/comparator headers, and `portal.h`. Iterators returned here are managed by `sst_file_reader_iterator.cc`.

Risks: `getTableProperties` dereferences `tp.get()` without checking for null; if called before open or after an error path that yields no properties, it may crash. Iterator ownership is transferred to Java and must be disposed.

Test signals: Tests should open valid and invalid SST paths, iterate contents, verify checksums, assert table properties after open, and ensure pre-open property calls are handled by Java or fail predictably.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_readerjni.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_writerjni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/sst_file_writerjni.cc

Purpose: Bridges Java `SstFileWriter` to C++ `ROCKSDB_NAMESPACE::SstFileWriter` for generating external SST files.

Important APIs/types/functions: Constructors create writers with `EnvOptions`, `Options`, and optionally a comparator handle/type. `open` starts an SST file. `put`, `merge`, and `delete` are exposed for slice handles, byte arrays, and direct buffers. `fileSize` returns current file size, `finish` completes the file, and `disposeInternalJni` deletes the writer.

Control flow: Java constructs the writer, opens a path, appends sorted operations, finishes, and later ingests the file through DB APIs. Byte-array variants pin key/value arrays, create `Slice`s, call the writer API, release arrays, and throw on non-OK status. Direct put uses `JniUtil::kv_op_direct`.

State and persistence behavior: The writer creates and mutates an SST file on disk. Native state tracks open writer state until finish/dispose.

Dependencies and integration points: Includes generated `org_rocksdb_SstFileWriter.h`, RocksDB comparator/env/options/SST writer headers, conversion utilities, and `portal.h`. It integrates with comparator JNI callbacks and external file ingestion in `rocksjni.cc`.

Risks: Comparator type values are magic bytes with no default error path; an unknown type silently uses a null comparator. The byte-array method comments contain mismatched signatures but implementation is clear. Java must enforce key ordering and finish semantics; RocksDB returns errors otherwise. Direct-buffer offset correctness is delegated to `JniUtil`.

Test signals: Tests should write a valid SST with byte-array and slice APIs, use a custom comparator path, verify file size and checksum through `SstFileReader`, test merge/delete entries, test direct-buffer offsets, and assert errors for unsorted keys or double finish.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_writerjni.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_partitioner.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/sst_partitioner.cc

Purpose: Exposes `NewSstPartitionerFixedPrefixFactory` to Java.

Important APIs/types/functions: `newSstPartitionerFixedPrefixFactory0` creates a `std::shared_ptr<SstPartitionerFactory>` from a prefix length and returns a native handle. `disposeInternalJni` deletes the shared pointer wrapper.

Control flow: Java passes a prefix length, C++ creates the fixed-prefix factory, and options code can consume the returned shared pointer. Disposal releases the wrapper.

State and persistence behavior: The factory is process-local configuration. It affects how RocksDB partitions generated SSTs but does not persist state by itself.

Dependencies and integration points: Depends on `rocksdb/sst_partitioner.h`, generated `org_rocksdb_SstPartitionerFixedPrefixFactory.h`, and pointer conversion helpers. The returned factory integrates with table/compaction options.

Risks: The source comment says SstFileManager, but the code is for SstPartitioner. Prefix length is not validated in JNI; invalid values rely on RocksDB factory behavior. Handle misuse can crash.

Test signals: Tests should install the factory in options, write data with varying prefixes, verify partition behavior where observable, and check repeated create/dispose cycles.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_partitioner.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/statistics.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/statistics.cc

Purpose: Bridges Java `Statistics` to a JNI-specific `StatisticsJni` subclass of RocksDB `StatisticsImpl`.

Important APIs/types/functions: Overloaded `newStatistics` constructors optionally clone/wrap another statistics shared pointer and accept a byte array of histograms to ignore. `disposeInternalJni` deletes the shared pointer wrapper. Accessors expose stats level, ticker counts, get-and-reset ticker counts, histogram data/string, reset, and `ToString`.

Control flow: Constructor paths funnel into `newStatistics___3BJ`, convert Java histogram enum bytes to C++ `Histograms`, copy an optional existing shared pointer, allocate `std::shared_ptr<StatisticsJni>`, and return it. Accessors reinterpret the handle as `std::shared_ptr<Statistics>*` and call virtual methods.

State and persistence behavior: Statistics are in-memory counters and histograms. Reset mutates them. Persistence is indirect only through observability/logging outside this file.

Dependencies and integration points: Depends on `rocksdb/statistics.h`, generated `org_rocksdb_Statistics.h`, conversion helpers for ticker/histogram/stats-level enums, `HistogramDataJni`, `RocksDBExceptionJni`, and `statisticsjni.h`.

Risks: Histogram ignore-list naming is inverted at the Java API level if callers expect enabled histograms; the actual subclass disables listed types. Handles are asserted but not runtime-validated. HistogramData construction depends on cached Java class/method lookups. Very large unsigned counters are cast to `jlong`.

Test signals: Tests should verify ignored histograms are disabled, stats level mapping, ticker count and get-and-reset behavior, histogram data object fields, reset error propagation, and cloning/forwarding from another statistics instance.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/statistics.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/statisticsjni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/statisticsjni.cc

Purpose: Implements `StatisticsJni`, a `StatisticsImpl` subclass that can disable selected histogram types for Java-created statistics objects.

Important APIs/types/functions: Constructors forward an optional underlying `std::shared_ptr<Statistics>` to `StatisticsImpl` and store `m_ignore_histograms`. `HistEnabledForType` returns false for out-of-range types and for any type in the ignore set.

Control flow: Statistics recording calls the virtual `HistEnabledForType`; this override gates histogram collection based on `HISTOGRAM_ENUM_MAX` and the ignore set.

State and persistence behavior: The only local state is the immutable set of ignored histogram IDs. It affects in-memory metrics collection only.

Dependencies and integration points: Includes `rocksjni/statisticsjni.h`, which depends on RocksDB monitoring internals. Constructed by `statistics.cc`.

Risks: The constructor takes the ignore set by value and stores a copy, which is safe but maybe unnecessarily copies. Type IDs are `uint32_t`; enum conversion correctness depends on `HistogramTypeJni`.

Test signals: Unit tests should call through Java statistics constructors with ignored histogram IDs and verify `getHistogramData` remains empty/unchanged while non-ignored histograms collect data.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/statisticsjni.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/statisticsjni.h -->
# sources/storage-engines/rocksdb/java/rocksjni/statisticsjni.h

Purpose: Declares the JNI-specific `StatisticsJni` class used by Java `Statistics` bindings.

Important APIs/types/functions: `class StatisticsJni : public StatisticsImpl` declares two constructors and overrides `bool HistEnabledForType(uint32_t type) const`. Private member `m_ignore_histograms` stores disabled histogram IDs.

Control flow: The header defines the type contract; construction and histogram filtering implementation live in `statisticsjni.cc`, and allocation lives in `statistics.cc`.

State and persistence behavior: Declares process-local in-memory metric filtering state. No persistence.

Dependencies and integration points: Includes `monitoring/statistics_impl.h` and `rocksdb/statistics.h`, so it uses RocksDB internal statistics implementation rather than only public interfaces. Included by `statistics.cc`.

Risks: Depending on `monitoring/statistics_impl.h` couples the Java binding to RocksDB internal headers. Any change to `StatisticsImpl` virtual methods or constructor signatures can break this bridge.

Test signals: Build compatibility across RocksDB versions is the main signal. Runtime tests should confirm the override is invoked through base `Statistics` handles returned to Java.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/statisticsjni.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/stderr_logger.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/stderr_logger.cc

Purpose: Bridges Java `org.rocksdb.util.StdErrLogger` to C++ `ROCKSDB_NAMESPACE::StderrLogger`.

Important APIs/types/functions: `newStdErrLogger` constructs a shared `StderrLogger` with an `InfoLogLevel` and optional prefix string. `setInfoLogLevel`, `infoLogLevel`, and `disposeInternal` mutate/read/delete the shared pointer wrapper.

Control flow: Constructor casts the Java log-level byte to `InfoLogLevel`; if a prefix exists, it copies it with `JniUtil::copyStdString`. Later methods dereference the shared pointer and call logger accessors.

State and persistence behavior: The logger writes to stderr when used by RocksDB. This file stores only the native logger object and its level/prefix.

Dependencies and integration points: Includes `util/stderr_logger.h`, generated `org_rocksdb_util_StdErrLogger.h`, conversion helpers, and `portal.h`. The shared logger handle can be passed into options and SST file manager construction.

Risks: Log-level byte is cast directly with no validation. Prefix copy failure returns 0 with a pending exception. Handle misuse can crash. The logger's stderr side effects can affect tests that assert clean output.

Test signals: Tests should verify prefix/no-prefix construction, log-level get/set, integration with options or SstFileManager, and clean disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/stderr_logger.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/table.cc

Purpose: Bridges Java table configuration classes to C++ table factory objects for plain and block-based table formats.

Important APIs/types/functions: `PlainTableConfig_newTableFactoryHandle` fills `PlainTableOptions` and returns `NewPlainTableFactory(options)`. `BlockBasedTableConfig_newTableFactoryHandle` fills `BlockBasedTableOptions`, including cache/index/filter settings, checksum/index enum conversions, block sizes, format version, key-value separation settings, compression options, block alignment, index shortening/search type, and optional cache construction.

Control flow: Java passes a long parameter list representing table config fields. C++ maps each primitive/handle to an options struct. Existing `Cache`, `PersistentCache`, and `FilterPolicy` shared pointer handles are dereferenced into options. If no block cache handle is supplied but a non-negative size is, a new LRU cache is created.

State and persistence behavior: The returned table factory configures how RocksDB writes and reads SST tables. It affects persisted SST format/layout but this bridge only creates factory objects.

Dependencies and integration points: Depends on generated table config headers, `rocksdb/table.h`, cache/filter policy headers, conversion helpers, and `portal.h`. The returned factories are consumed by options JNI code.

Risks: The block-based signature is very wide, so Java/C++ parameter ordering must stay exactly synchronized. `super_block_alignment_space_overhead_ratio` is assigned through `static_cast<size_t>` even though its Java name suggests a ratio, which deserves API compatibility review. If no cache handle and negative cache size are supplied, the bridge forces `no_block_cache`. Enum conversion helpers must reject or handle invalid bytes.

Test signals: Tests should inspect options through created DB/table behavior, verify cache handle vs size-created cache paths, filter policy installation, enum mappings, and Java signature regeneration after parameter additions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_filter.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/table_filter.cc

Purpose: Constructs native `TableFilterJniCallback` objects for Java `AbstractTableFilter`.

Important APIs/types/functions: `Java_org_rocksdb_AbstractTableFilter_createNewTableFilter` allocates `ROCKSDB_NAMESPACE::TableFilterJniCallback(env, jtable_filter)` and returns the native pointer.

Control flow: Java subclass creation calls this function; C++ creates a callback wrapper that stores method IDs and a global callback reference through `JniCallback`.

State and persistence behavior: The callback is native process state. It influences RocksDB table filtering decisions during operations that accept table filters but does not persist data.

Dependencies and integration points: Includes generated `org_rocksdb_AbstractTableFilter.h`, pointer conversion helpers, and `table_filter_jnicallback.h`. Disposal is through `RocksCallbackObject` base handling.

Risks: Lifetime must cover any RocksDB background or iterator use of the filter. Constructor exceptions leave a returned object with possibly missing method IDs unless Java checks pending exceptions.

Test signals: Tests should install a Java table filter, assert it receives table properties, verify true/false decisions affect table selection, and validate disposal through the callback base.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_filter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_filter_jnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/table_filter_jnicallback.cc

Purpose: Implements the C++ callback adapter that lets RocksDB invoke a Java `AbstractTableFilter`.

Important APIs/types/functions: `TableFilterJniCallback::TableFilterJniCallback` resolves `AbstractTableFilterJni::getFilterMethod` and creates `m_table_filter_function`. `GetTableFilterFunction` returns the stored `std::function<bool(const TableProperties&)>`.

Control flow: When RocksDB calls the function, the adapter attaches/obtains a thread-local `JNIEnv`, converts C++ `TableProperties` to a Java object, invokes the Java boolean filter method, describes any exception to stderr, releases the JNI environment if attached, and returns false on conversion/call failure.

State and persistence behavior: Stores method ID and Java callback reference inherited from `JniCallback`. No persistent state is written. The return value influences whether RocksDB includes/excludes table data in operations using the filter.

Dependencies and integration points: Depends on `table_filter_jnicallback.h` and `portal.h`, including `TablePropertiesJni` and `AbstractTableFilterJni`. Created by `table_filter.cc` and often passed into DB table-property APIs/options.

Risks: On the success path the local `jtable_properties` reference is not explicitly deleted before returning, which can pressure local reference tables if invoked repeatedly on an attached thread. Exceptions are described and swallowed as `false`, so Java errors may become silent filtering behavior rather than propagated operation failures. Method ID lookup failure leaves the object in a partially initialized state.

Test signals: Tests should force callback success, callback false, Java exception, and high-volume invocation to detect local-reference leaks. Threaded tests should validate attach/release behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_filter_jnicallback.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_filter_jnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/table_filter_jnicallback.h

Purpose: Declares `TableFilterJniCallback`, the C++ holder for a Java table-filter callback.

Important APIs/types/functions: The class inherits `JniCallback`, exposes a constructor and `GetTableFilterFunction`, and stores a `jmethodID` plus a `std::function<bool(const TableProperties&)>`.

Control flow: The header defines the callback contract used by `table_filter_jnicallback.cc`. RocksDB receives the returned `std::function`; Java disposal treats the object as a `JniCallback`.

State and persistence behavior: Declares process-local callback state only.

Dependencies and integration points: Includes JNI, `<functional>`, `<memory>`, `rocksdb/table_properties.h`, and `rocksjni/jnicallback.h`.

Risks: The stored `std::function` captures `this`, so it must not outlive the callback object. No copy/move restrictions are declared, so accidental copying would duplicate a pointer-owning callback wrapper if ever used that way.

Test signals: Compile tests catch signature drift. Runtime tests should ensure functions obtained before disposal are not used after disposal and that Java callbacks work from non-Java RocksDB threads.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_filter_jnicallback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_properties_collector_factory.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/table_properties_collector_factory.cc

Purpose: Bridges Java `TablePropertiesCollectorFactory` to RocksDB's compact-on-deletion table properties collector factory.

Important APIs/types/functions: `newCompactOnDeletionCollectorFactory` allocates `TablePropertiesCollectorFactoriesJniWrapper`, fills its shared pointer with `NewCompactOnDeletionCollectorFactory(sliding_window_size, deletion_trigger, deletion_ratio)`, and returns the wrapper pointer. `deleteCompactOnDeletionCollectorFactory` deletes the wrapper.

Control flow: Java creates a factory with compaction-on-deletion thresholds, passes the handle into options code, then calls delete when done. The wrapper exists because Java needs a stable pointer to a shared pointer field.

State and persistence behavior: The collector factory is in-memory configuration that affects table property collection and compaction decisions when RocksDB builds tables. It does not directly persist data, but generated table properties become part of SST metadata.

Dependencies and integration points: Includes its local header, generated `org_rocksdb_TablePropertiesCollectorFactory.h`, pointer conversion, `rocksdb/db.h`, and `rocksdb/utilities/table_properties_collectors.h`. Options code must understand `TablePropertiesCollectorFactoriesJniWrapper`.

Risks: The local header path uses `java/rocksjni/...`, unlike many neighboring includes that use `rocksjni/...`; build include roots must support this. The delete function does not null-check handles. Threshold values are not validated in JNI.

Test signals: Tests should configure compact-on-deletion, write/delete workloads that trigger collected properties, verify factory disposal, and cover build/include portability.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_properties_collector_factory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_properties_collector_factory.h -->
# sources/storage-engines/rocksdb/java/rocksjni/table_properties_collector_factory.h

Purpose: Declares the native wrapper used to pass a shared table properties collector factory through Java handles.

Important APIs/types/functions: `struct TablePropertiesCollectorFactoriesJniWrapper` contains `std::shared_ptr<rocksdb::TablePropertiesCollectorFactory> table_properties_collector_factories`.

Control flow: Allocation/deletion happens in `table_properties_collector_factory.cc`; other option bridges can reinterpret the handle and read the shared pointer field.

State and persistence behavior: Holds only process-local shared ownership of a collector factory.

Dependencies and integration points: Includes `rocksdb/table_properties.h` and `rocksdb/utilities/table_properties_collectors.h`. It is a C++ bridge type, not a generated JNI header.

Risks: The include guard name is generic (`ROCKSDB_TABLE_PROPERTIES_COLLECTOR_FACTORY_H`) and could collide with a broader RocksDB header guard. The plural field name is awkward and must be referenced exactly by consumers.

Test signals: Build tests should include this header with RocksDB headers in different orders. Runtime tests should verify option consumers correctly extract the shared pointer.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/table_properties_collector_factory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/testable_event_listener.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/testable_event_listener.cc

Purpose: Native test helper that invokes every event-listener callback with populated RocksDB event structures so Java listener adapters can be tested without orchestrating real DB events.

Important APIs/types/functions: `newTablePropertiesForTest` creates a `TableProperties` object with maxed numeric fields, string fields, and user/readable properties. `Java_org_rocksdb_test_TestableEventListener_invokeAllCallbacks` unwraps a shared `EventListener` and calls flush, table deletion, compaction, table creation, memtable, CF deletion, external ingestion, background error, stall, file IO, notification, and error recovery callbacks.

Control flow: Java passes an event listener shared pointer handle. The helper builds representative C++ event structs (`FlushJobInfo`, `CompactionJobInfo`, `TableFileCreationInfo`, `MemTableInfo`, `ExternalFileIngestionInfo`, `WriteStallInfo`, `FileOperationInfo`, etc.) and invokes each listener method directly.

State and persistence behavior: No DB persistence occurs; all event structures are synthetic in-memory test data. Some callbacks may mutate Java-side test counters or status fields.

Dependencies and integration points: Depends on generated test JNI header, `rocksdb/listener.h`, `rocksdb/status.h`, and `rocksdb/table_properties.h`. It exercises Java event-listener callback conversion code elsewhere.

Risks: It constructs a `shared_ptr<TableProperties>` with a no-op deleter pointing at a stack object for compaction properties; this is safe only within synchronous callback execution. If listener code stores the shared pointer, it becomes dangling. Max integer values intentionally stress conversion but can expose signed truncation.

Test signals: This file is itself a test signal. Java tests should assert every callback is invoked, all converted fields match expected sentinel values, status/subcode conversion works, file timestamps are converted, and no callback stores stack-backed data beyond the call.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/testable_event_listener.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/thread_status.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/thread_status.cc

Purpose: Bridges Java `ThreadStatus` helper methods to C++ `ROCKSDB_NAMESPACE::ThreadStatus` static formatting and interpretation APIs.

Important APIs/types/functions: Methods expose thread type name, operation name, microsecond formatting, operation stage name, operation property name, operation property interpretation, and state name. Enum conversion helpers map Java bytes to C++ enum values.

Control flow: Simple name methods convert enum bytes, call `ThreadStatus` static methods, and convert strings back to Java. `interpretOperationProperties` copies a Java `long[]` into a `uint64_t[]`, calls `InterpretOperationProperties`, and converts the resulting map to Java.

State and persistence behavior: Stateless conversion only. No DB or persistent state is touched.

Dependencies and integration points: Includes `rocksdb/thread_status.h`, generated `org_rocksdb_ThreadStatus.h`, and `portal.h` for enum and map/string conversion.

Risks: `interpretOperationProperties` assumes the Java array has the expected length for the operation type; RocksDB interpretation may read required positions from the provided pointer. Enum conversion correctness depends on generated Java constants. Large unsigned properties may be sign-represented as Java longs.

Test signals: Tests should verify enum name mappings, microsecond formatting, property names by operation/index, interpreted property maps for known arrays, and invalid enum/short-array handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/thread_status.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/trace_writer.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/trace_writer.cc

Purpose: Constructs native `TraceWriterJniCallback` objects for Java `AbstractTraceWriter` implementations.

Important APIs/types/functions: `Java_org_rocksdb_AbstractTraceWriter_createNewTraceWriter` allocates `ROCKSDB_NAMESPACE::TraceWriterJniCallback(env, jobj)` and returns the native pointer.

Control flow: Java creates a trace writer object, calls this native constructor, and later passes the handle to `RocksDB.startTrace`, where ownership is transferred to RocksDB.

State and persistence behavior: The callback object is in-memory state. Actual trace persistence depends on the Java writer implementation invoked by `trace_writer_jnicallback.cc`.

Dependencies and integration points: Includes generated `org_rocksdb_AbstractTraceWriter.h`, pointer conversion helpers, and `trace_writer_jnicallback.h`. Integrates with `rocksjni.cc` `startTrace`.

Risks: The file comment mentions `CompactionFilterFactory`, but the implementation is trace writer creation. Ownership changes after `startTrace`; Java must not double-dispose. Constructor method-ID lookup failures need Java-side exception handling.

Test signals: Tests should create a Java trace writer, start/end tracing, verify write/close/file-size callbacks, and confirm ownership/disposal behavior after start.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/trace_writer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/trace_writer_jnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/trace_writer_jnicallback.cc

Purpose: Implements a C++ `TraceWriter` that delegates trace writes, close, and file-size queries to a Java `AbstractTraceWriter`.

Important APIs/types/functions: Constructor resolves Java proxy method IDs for write, close, and get-file-size. `Write(const Slice&)` calls Java `writeProxy(long-like Slice pointer)`, unpacks a short status code/subcode into C++ `Status`. `Close()` does the same for close. `GetFileSize()` calls the Java file-size method and returns a `uint64_t`.

Control flow: RocksDB tracing calls the C++ virtual methods. Each method obtains/attaches a `JNIEnv`, invokes the cached Java method, handles pending exceptions by describing them and returning an IO error or zero, converts Java status encoding through `StatusJni::toCppStatus`, and releases the JNI environment.

State and persistence behavior: The callback holds method IDs and a Java callback reference through `JniCallback`. Trace bytes are persisted or buffered by Java-side writer behavior, not by this C++ file.

Dependencies and integration points: Depends on `trace_writer_jnicallback.h` and `portal.h` for `StatusJni`, callback environment handling, and `Slice` exposure. Created by `trace_writer.cc` and consumed by `RocksDB.startTrace`.

Risks: `Write` passes `&data` directly to Java as an argument matching the generated proxy signature; Java must treat it as a temporary native slice valid only during the call. Exceptions are printed to stderr and converted to generic IO errors, losing Java exception detail. Method lookup failure leaves cached IDs null. Status packing into `jshort` must remain synchronized with Java.

Test signals: Tests should make Java write return OK and non-OK statuses, throw exceptions, verify close status conversion, assert file size conversion, and ensure Java does not retain the temporary slice pointer.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/trace_writer_jnicallback.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/trace_writer_jnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/trace_writer_jnicallback.h

Purpose: Declares the JNI-backed C++ `TraceWriter` implementation.

Important APIs/types/functions: `class TraceWriterJniCallback : public JniCallback, public TraceWriter` declares constructor and overrides `Status Write(const Slice&)`, `Status Close()`, and `uint64_t GetFileSize()`. It stores method IDs for write, close, and file size.

Control flow: RocksDB sees this object through the `TraceWriter` interface, while Java disposal/ownership uses `JniCallback` behavior.

State and persistence behavior: Declares process-local callback state. Persistent trace output is delegated to Java-side methods.

Dependencies and integration points: Includes JNI, `rocksdb/trace_reader_writer.h`, and `rocksjni/jnicallback.h`. Implemented in `trace_writer_jnicallback.cc`.

Risks: Multiple inheritance requires both base classes to have compatible virtual destruction. The callback must outlive RocksDB trace usage and is owned by `StartTrace` after transfer.

Test signals: Compile tests catch virtual signature drift. Runtime tests should cover ownership transfer, virtual dispatch through `TraceWriter`, and destruction through callback/base paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/trace_writer_jnicallback.h -->
