# sources/storage-engines/rocksdb/java/rocksjni/options.cc lines 7873-8810

## Purpose

This chunk implements JNI bridge functions for the tail of `org.rocksdb.DBOptions`, all visible `org.rocksdb.WriteOptions`, `org.rocksdb.ReadOptions`, `org.rocksdb.ComparatorOptions`, and `org.rocksdb.FlushOptions` native methods in this line range. The functions translate Java `long` native handles into RocksDB C++ option objects, allocate/copy/delete those objects, and expose direct setters/getters for option fields used by write, read, comparator callback, and flush operations.

The code is intentionally thin: Java owns a `RocksObject` handle, calls one of these `Java_org_rocksdb_*` symbols, and the native method either mutates a C++ options struct field, returns a field value, or returns a pointer encoded as `jlong` using `GET_CPLUSPLUS_POINTER`.

## Important APIs, Types, and Functions

### DBOptions tail

- `Java_org_rocksdb_DBOptions_setMaxBgErrorResumeCount` and `maxBgerrorResumeCount` map Java `int` to/from `DBOptions::max_bgerror_resume_count`.
- `Java_org_rocksdb_DBOptions_setBgerrorResumeRetryInterval` and `bgerrorResumeRetryInterval` map Java `long` to/from `DBOptions::bgerror_resume_retry_interval` as `uint64_t`.
- `Java_org_rocksdb_DBOptions_setDailyOffpeakTimeUTC` copies a Java UTF string into `DBOptions::daily_offpeak_time_utc`; `dailyOffpeakTimeUTC` returns it as a new Java string.
- The chunk starts at line 7873, so `setMaxBgErrorResumeCount` begins in the previous chunk and is only partially visible here.

### WriteOptions

- `newWriteOptions` allocates `new ROCKSDB_NAMESPACE::WriteOptions`.
- `copyWriteOptions` constructs a shallow C++ copy from another `WriteOptions` handle.
- `disposeInternalJni` deletes the native object after asserting the handle is non-null.
- Field bridge pairs cover:
  - `sync`
  - `disableWAL`
  - `ignore_missing_column_families`
  - `no_slowdown`
  - `low_pri`
  - `memtable_insert_hint_per_batch`

### ReadOptions

- `newReadOptions__` allocates default `ReadOptions`.
- `newReadOptions__ZZ` allocates `ReadOptions(verify_checksums, fill_cache)`.
- `copyReadOptions` shallow-copies the native `ReadOptions`; Java separately keeps references to pointer-backed slice fields.
- `disposeInternalJni` deletes the native object.
- Boolean field bridges cover `verify_checksums`, `fill_cache`, `tailing`, `total_order_seek`, `prefix_same_as_start`, `pin_data`, `background_purge_on_iterator_cleanup`, `ignore_range_deletions`, `auto_prefix_mode`, and `async_io`.
- Numeric and enum bridges cover `readahead_size`, `max_skippable_internal_keys`, `read_tier`, `deadline`, `io_timeout`, and `value_size_soft_limit`.
- Pointer bridges cover:
  - `snapshot`, a `const Snapshot*` assigned from a Java `Snapshot` handle.
  - `iterate_upper_bound` and `iterate_lower_bound`, assigned from `Slice*` handles.
  - `timestamp` and `iter_start_ts`, assigned from `Slice*` handles.
  - `table_filter`, assigned from `TableFilterJniCallback::GetTableFilterFunction()`.

### ComparatorOptions

- `newComparatorOptions` allocates `ComparatorJniCallbackOptions`, not a RocksDB core options type. This struct configures Java comparator callback behavior.
- `reusedSynchronisationType` and `setReusedSynchronisationType` convert between Java byte enum values and C++ `ReusedSynchronisationType` through `ReusedSynchronisationTypeJni` in `portal.h`.
- `useDirectBuffer` and `setUseDirectBuffer` bridge `ComparatorJniCallbackOptions::direct_buffer`.
- `maxReusedBufferSize` and `setMaxReusedBufferSize` bridge `ComparatorJniCallbackOptions::max_reused_buffer_size`.
- `disposeInternalJni` deletes the callback-options object.

### FlushOptions

- `newFlushOptions` allocates `new ROCKSDB_NAMESPACE::FlushOptions`.
- `setWaitForFlush` and `waitForFlush` bridge `FlushOptions::wait`.
- `setAllowWriteStall` and `allowWriteStall` bridge `FlushOptions::allow_write_stall`.
- `disposeInternalJni` deletes the native object.

## Control Flow

The dominant control flow is one JNI call per Java option operation:

1. Java stores a native pointer as `long nativeHandle_`.
2. Java calls a static or instance native method with that handle.
3. C++ casts the `jlong` back to the expected C++ type with `reinterpret_cast`.
4. C++ reads or writes a field, constructs an object, copies an object, deletes an object, or returns a subordinate pointer.
5. Return values are cast back to JNI primitives or `jlong`.

Only a few functions have extra control flow:

- `setDailyOffpeakTimeUTC` calls `GetStringUTFLength` and `GetStringUTFChars`, checks for a pending Java exception, copies the bytes into `std::string`, then releases the UTF chars. If `GetStringUTFChars` fails, the function returns early with the Java exception still pending.
- `setTableFilter` casts the Java table-filter handle to `TableFilterJniCallback*` and stores the callback object's `std::function` into `ReadOptions::table_filter`. Later RocksDB iterator construction invokes that function from core read paths.
- Lifecycle functions assert non-null before `delete`, but otherwise do not validate handle ownership.

## State and Persistence Behavior

The options objects are process-memory state only. This chunk does not write files or persist configuration. Persistence effects happen later when these options are passed into RocksDB operations:

- `WriteOptions::sync` and `disableWAL` directly affect crash durability. `sync=true` requests durable syncing before write completion; `disableWAL=true` skips WAL logging and can lose recent writes after crash unless data is flushed/backed up appropriately.
- `WriteOptions::ignore_missing_column_families`, `no_slowdown`, `low_pri`, and `memtable_insert_hint_per_batch` affect write admission, error behavior, and performance but not on-disk format.
- `ReadOptions` fields affect read consistency, iterator bounds, cache population, IO behavior, and timestamp visibility. Snapshot and slice fields are borrowed pointers, so their Java/C++ lifetime must outlive reads using this `ReadOptions`.
- `FlushOptions::wait` controls whether flush calls block until completion. `allow_write_stall` decides whether a flush may proceed even when it can stall foreground writes.
- `ComparatorOptions` affect Java comparator callback memory and synchronization behavior; they are consumed when constructing comparator callbacks and do not themselves persist.

## Dependencies and Integration Points

This chunk depends on:

- RocksDB public C++ types from `rocksdb/options.h`, including `DBOptions`, `WriteOptions`, `ReadOptions`, and `FlushOptions`.
- `rocksdb/db.h` for `Snapshot` and related DB-facing types.
- `rocksdb/slice.h` transitively for `Slice` pointer fields.
- JNI generated headers such as `include/org_rocksdb_WriteOptions.h`, `include/org_rocksdb_ReadOptions.h`, `include/org_rocksdb_ComparatorOptions.h`, and `include/org_rocksdb_FlushOptions.h`.
- `rocksjni/comparatorjnicallback.h` for `ComparatorJniCallbackOptions`.
- `rocksjni/table_filter_jnicallback.h` for `TableFilterJniCallback`.
- `rocksjni/portal.h` for enum conversion helpers and `GET_CPLUSPLUS_POINTER`.

Java integration points include:

- `java/src/main/java/org/rocksdb/WriteOptions.java`, which calls the write-option allocation, copy, field, and disposal natives.
- `java/src/main/java/org/rocksdb/ReadOptions.java`, which calls the read-option natives and holds Java references to lower/upper bound and timestamp slices so the borrowed native `Slice*` values remain valid.
- `java/src/main/java/org/rocksdb/ComparatorOptions.java`, which exposes comparator callback synchronization and buffer reuse settings.
- `java/src/main/java/org/rocksdb/FlushOptions.java`, which wraps flush option allocation and field access.
- `AbstractTableFilter` and `TableFilterJniCallback`, where Java callback objects are converted into a C++ function stored in `ReadOptions::table_filter`.
- RocksDB operation JNI code elsewhere, such as DB `put`, `write`, `get`, iterator, and flush calls, consumes these option handles by reference.

## Risks and Edge Cases

- Handle casts are unchecked. Passing the wrong native handle type or a disposed handle can corrupt memory or crash the JVM.
- Copy constructors for `WriteOptions` and `ReadOptions` are shallow. For `ReadOptions`, pointer fields such as snapshot and slices are copied as raw pointers; Java tries to retain slice references in its copy constructor, but snapshot and table-filter lifetimes still require caller discipline.
- `ReadOptions::snapshot` returns a borrowed `Snapshot*` encoded as `jlong`; Java wraps it as a `Snapshot` but does not own the DB snapshot lifecycle. Releasing the snapshot while options or iterators still use it is unsafe.
- `iterate_lower_bound`, `iterate_upper_bound`, `timestamp`, and `iter_start_ts` are raw `Slice*` pointers. Java retains references for set values, but returned wrappers are non-owning for bounds; timestamp accessors in Java should be checked carefully for ownership semantics because the native pointer is still owned outside the returned wrapper.
- `setTableFilter` does not null-check the callback handle. Passing null from Java would dereference a null `TableFilterJniCallback*`. The Java method accepts `AbstractTableFilter tableFilter` and immediately accesses `tableFilter.nativeHandle_`, so normal Java calls fail before JNI on null, but native misuse remains unsafe.
- `setDailyOffpeakTimeUTC` does not release UTF chars if an exception is raised after `GetStringUTFChars` but before release; in the visible code, the only checked exception point is immediately after acquisition, before the string copy.
- Several numeric casts can reinterpret negative Java values as large unsigned C++ values, e.g. `bgerror_resume_retry_interval`, `readahead_size`, `max_skippable_internal_keys`, and `value_size_soft_limit`.
- `deadline` and `io_timeout` cast Java `long` through `int64_t` into `std::chrono::microseconds`; negative or overflow-prone inputs are not rejected here.
- The C++ `asyncIo` methods are declared with a `jobject` second parameter and a handle argument, while `ReadOptions.java` declares them as non-static native methods with a single `long` handle. That matches JNI instance-native shape, but differs from the mostly static native pattern in the same class and should be covered by tests.
- `bestEffortsRecovery` just before this chunk returns `static_cast<jlong>` from a `jboolean` function. Although outside the requested start line except for context, it is adjacent enough to be a useful review signal for this region.
- `FlushOptions.java` names its loader helper `newFlushOptionsInance`, a typo that is harmless if consistently referenced, but generated-header or manual binding changes could miss it.

## Test Signals

Useful tests for this chunk are JNI round-trip tests and operation-level behavior tests:

- Construct, copy, mutate, read back, and dispose `WriteOptions`, `ReadOptions`, `ComparatorOptions`, and `FlushOptions` from Java.
- Verify `WriteOptions` defaults and setters for `sync`, `disableWAL`, missing column-family handling, slowdown behavior, low-priority writes, and memtable insert hints.
- Exercise `ReadOptions` with checksums, fill-cache, tailing iterators, total-order seek, prefix-same-as-start, pinning, readahead, max-skippable keys, read tier, deadlines, IO timeout, value soft limit, and async IO.
- Use a live DB snapshot in `ReadOptions`, read through it, release it after use, and assert no stale reads or crashes.
- Use lower and upper bound slices, then let local Java variables go out of scope while `ReadOptions` still exists, confirming the Java retention fields protect native slice pointers.
- Use timestamp and iter-start timestamp slices with a timestamp-aware comparator if the feature is enabled in the test matrix.
- Install an `AbstractTableFilter` on `ReadOptions` and verify iterator table skipping invokes the Java callback and handles callback exceptions as expected.
- Verify `ComparatorOptions` conversion for every `ReusedSynchronisationType`, direct vs heap byte-buffer callbacks, and reused buffer size zero/small/large cases.
- Flush with `wait=true/false` and `allow_write_stall=true/false`, checking API return behavior under write-pressure scenarios.
- Run JNI signature/linkage tests, especially for overloaded `newReadOptions`, instance-style `asyncIo` methods, and the `FlushOptions` allocation path.
