# sources/storage-engines/rocksdb/java/rocksjni/portal.h lines 1-7632

## Scope

This chunk covers the first and largest part of RocksDB's Java JNI portal header. It starts at the file header and includes the common JNI class/method lookup helpers, exception/status conversion, collection and byte/string utilities, native-handle portals for many Java wrapper classes, callback bridge method IDs, metadata object constructors, and a large set of Java/C++ enum mapping helpers. The chunk stops at line 7632 inside `CompactionReasonJni::toJavaCompactionReason()`, immediately after the `kRefitLevel` case label; the rest of that mapping and the remaining portals are in the next chunk.

## Purpose

`portal.h` is the central C++ helper layer used by RocksJNI code to cross the Java/C++ boundary. It caches or retrieves Java classes, method IDs, field IDs, constructors, enum values, and native object handles so JNI implementation files can avoid repeating fragile signature strings and local reference management.

The header also defines bidirectional conversion contracts between Java-visible RocksDB wrapper types and native RocksDB structures. In this chunk those contracts include `Status`, `RocksDBException`, Java arrays and collections, byte buffers, maps, write batch handlers, backup metadata, table properties, column family descriptors, transaction/deadlock objects, thread status, statistics tickers/histograms, compression/compaction/options enums, and several callback interfaces.

This file does not implement RocksDB storage behavior itself. It is glue code that makes Java API behavior line up with C++ RocksDB semantics, including exception propagation, native pointer ownership, enum ordinal stability, direct-buffer access, and metadata object construction.

## Important APIs, Types, and Functions

- `JavaClass::getJClass()` wraps `JNIEnv::FindClass()` and asserts the result. Every portal class builds on this pattern with the Java binary name for its wrapper type.
- `RocksDBNativeClass<PTR, DERIVED>` and `NativeRocksMutableObject<PTR, DERIVED>` are template bases for Java objects that carry native C++ handles. `NativeRocksMutableObject::setHandle()` calls Java `setNativeHandle(long, boolean)` using `GET_CPLUSPLUS_POINTER()`.
- `JavaException<DERIVED>` is the base for `IllegalArgumentExceptionJni`, `OutOfMemoryErrorJni`, and `RocksDBExceptionJni`. It centralizes `ThrowNew()` and reports unexpected class/constructor failures to `std::cerr`.
- `CodeJni`, `SubCodeJni`, and `StatusJni` translate between `org.rocksdb.Status`, `Status.Code`, `Status.SubCode`, and `ROCKSDB_NAMESPACE::Status`. `StatusJni::construct()` creates a Java `Status`; `StatusJni::toCppStatus()` reconstructs a native `Status` from Java code/subcode values.
- `RocksDBExceptionJni` constructs and throws Java `RocksDBException` from a native `Status`, either with only status or with a message plus status. It can also extract a native `Status` from a caught Java exception via `getStatus()`.
- `ListJni`, `MapJni`, and `HashMapJni` provide Java collection portals. `HashMapJni::fromCppMap()` converts C++ maps with string, `uint32_t`, or `uint64_t` values into Java `HashMap` instances using `String`, `Integer`, and `Long` wrappers.
- `ByteJni`, `ByteBufferJni`, `IntegerJni`, `LongJni`, and `StringBuilderJni` wrap common JDK types. `ByteBufferJni::constructWith()` can create direct buffers backed by C++ memory or heap `ByteBuffer`s filled from a C++ buffer.
- `JniUtil` is the main utility class. It attaches/detaches native threads to the JVM, copies strings and bytes between Java and C++, creates Java arrays with size checks, converts `byte[][]` to C++ strings through callback functions, performs array/direct-buffer key/value operations, converts arrays of native pointers, and copies C++ data into direct buffers.
- Native wrapper portals include `RocksDBJni`, `OptionsJni`, `DBOptionsJni`, `ColumnFamilyOptionsJni`, `WriteOptionsJni`, `ReadOptionsJni`, `WriteBatchJni`, `WriteBatchWithIndexJni`, `BackupEngineOptionsJni`, `BackupEngineJni`, `IteratorJni`, `FilterPolicyJni`, `ColumnFamilyHandleJni`, `FlushOptionsJni`, and `ComparatorOptionsJni`.
- `WriteBatchHandlerJni` exposes all Java `WriteBatch.Handler` callbacks needed by native batch iteration: put, merge, delete, single delete, delete range, log data, blob index put, transaction prepare/commit/rollback markers, no-op markers, timestamped commit markers, and `shouldContinue()`.
- Callback bridge portals include `AbstractCompactionFilterFactoryJni`, `AbstractTransactionNotifierJni`, `AbstractComparatorJniBridge`, `AbstractComparatorJni`, `LoggerJni`, and `AbstractTableFilterJni`. They expose Java callback method IDs consumed by C++ callback adapter classes included at the top of the file.
- Object construction portals include `ColumnFamilyOptionsJni::construct()`, `WriteBatchJni::construct()`, `WriteBatchSavePointJni::construct()`, `BackupInfoJni::construct0()`, `BackupInfoListJni::getBackupInfo()`, `BatchResultJni::construct()`, `TransactionJni::newWaitingTransactions()`, `TransactionDBJni::newDeadlockInfo()`, `KeyLockInfoJni::construct()`, `DeadlockPathJni::construct()`, `TablePropertiesJni::fromCppTableProperties()`, `ColumnFamilyDescriptorJni::construct()`, and `ThreadStatusJni::construct()`.
- Enum mapping classes in this chunk include `FilterPolicyTypeJni`, `WriteTypeJni`, `BottommostLevelCompactionJni`, `CompactionStopStyleJni`, `CompressionTypeJni`, `CompactionPriorityJni`, `WALRecoveryModeJni`, `TickerTypeJni`, `HistogramTypeJni`, `StatsLevelJni`, `RateLimiterModeJni`, `MemoryUsageTypeJni`, `PerfLevelTypeJni`, `TxnDBWritePolicyJni`, `IndexTypeJni`, `DataBlockIndexTypeJni`, `IndexSearchTypeJni`, `ChecksumTypeJni`, `IndexShorteningModeJni`, `PriorityJni`, `ThreadTypeJni`, `OperationTypeJni`, `OperationStageJni`, `StateTypeJni`, `CompactionStyleJni`, and the beginning of `CompactionReasonJni`.

## Control Flow

The common portal flow is: find the Java class, retrieve a method/field/constructor ID with a literal JNI signature, call the Java method or construct the object, check `ExceptionCheck()`, clean up local references, and return either the Java reference/value or `nullptr`/a boolean error signal.

Exception flow is explicit. Simple Java exceptions use `JavaException::ThrowNew()`. `RocksDBExceptionJni` is more involved: it finds the Java exception class, gets the constructor accepting a `Status` or `(String, Status)`, builds a Java `Status` through `StatusJni::construct()`, creates a `jthrowable`, calls `Throw()`, then deletes local references. If any JNI step fails, the function leaves the pending Java exception intact and returns true when an exception is pending.

Status conversion is bidirectional. Native-to-Java conversion maps C++ `Status::Code` and `Status::SubCode` to stable byte values, copies the optional state string with `NewStringUTF()`, and invokes the Java `Status(byte, byte, String)` constructor. Java-to-native conversion calls `getCode()`, `getSubCode()`, each enum's `getValue()`, and `getState()`, then uses `StatusJni::toCppStatus(jbyte, jbyte)` to construct an equivalent native status. The current chunk reads the Java state object but does not use its contents when building the native `Status`, so only code/subcode semantics are restored here.

Data-copy control flow in `JniUtil` carefully selects JNI array APIs based on use case. `copyStrings()` iterates a Java `String[]`, gets UTF chars, copies into `std::string`, releases UTF chars, and deletes local refs. `stringsBytes()` builds a Java `byte[][]` by allocating each byte array, writing with `SetByteArrayRegion()`, installing it into the object array, and releasing local refs. `byteString()` and `byteStrings()` use `GetByteArrayElements()` and release with `JNI_ABORT` because the C++ code only reads. `kv_op()`, `k_op()`, and `v_op()` wrap common byte-array-to-`Slice` flows for write batch and lookup helpers.

Direct-buffer helpers avoid copying but validate buffer shape before creating a `Slice`. `kv_op_direct()`, `k_op_direct()`, and `copyToDirect()` call `GetDirectBufferAddress()` and check `GetDirectBufferCapacity()` against offset plus length. Invalid direct-buffer arguments become Java `RocksDBException`s rather than native crashes.

Object construction helpers follow the same pattern: locate class and constructor, convert dependent fields, construct the Java object, and delete temporary local references on error paths. `TablePropertiesJni::fromCppTableProperties()` is the broadest example, converting numeric fields, byte-array column family name, optional string fields, and two C++ string maps before calling a long Java constructor.

Enum helpers are almost entirely switch statements. They map C++ enum constants to stable Java `jbyte` or `jint` values and, where needed, map those Java values back to C++ defaults. Several mappings reserve or pin values for compatibility, especially `TickerTypeJni` and `HistogramTypeJni`, where the Java representation is a signed byte and newer RocksDB enum values are assigned negative byte values.

## State and Persistence Behavior

The file itself has no persistent storage. Its "state" is JNI lookup state cached in function-local `static jmethodID` or `static jfieldID` variables and, in one template path, a function-local `static jclass`. These caches are process-local and persist for the lifetime of the native library.

Native pointer state is represented as Java `long` values. Portal classes pass pointers through `GET_CPLUSPLUS_POINTER()` and Java constructors such as `<init>(J)V`; Java-side wrappers are expected to store and eventually release or ignore those handles according to their ownership flag. `NativeRocksMutableObject::setHandle()` explicitly includes a `java_owns_handle` boolean to tell Java whether it manages native lifetime.

Memory ownership is mixed and must be respected by callers. `ColumnFamilyOptionsJni::construct()` allocates a fresh native `ColumnFamilyOptions` copy and passes ownership to Java through the native handle. `BatchResultJni::construct()` releases ownership from `batch_result.writeBatchPtr` after constructing the Java object, transferring the write batch pointer to Java. `ByteBufferJni::constructWith(direct=true, buf=nullptr)` allocates a new `char[]` and wraps it in a direct `ByteBuffer`; this depends on the corresponding Java/direct-buffer lifecycle elsewhere to avoid leaking the native allocation.

Local JNI references are short-lived and manually deleted in many paths, especially when loops build Java collections or when constructors allocate multiple intermediate strings/arrays. Some successful construction paths intentionally leave returned local refs alive for the caller, while temporary refs are generally deleted on error. A few successful paths do not delete every temporary ref in this chunk, which is tolerable for small calls but risky in large loops.

The enum byte values are part of the Java API persistence/compatibility surface. `TickerTypeJni` and `HistogramTypeJni` comments explicitly pin values across releases, including reserved max enum values and skipped byte slots. Changing these mappings would break serialized/configured Java clients or cross-version assumptions even though the code is not writing persistent files itself.

## Dependencies and Integration Points

- JNI core: `jni.h`, `JNIEnv`, `JavaVM`, `jclass`, `jmethodID`, `jfieldID`, `jobject`, primitive arrays, direct buffers, local refs, pending exceptions, and thread attachment APIs.
- RocksDB public C++ APIs: `rocksdb/db.h`, `status.h`, `table.h`, `filter_policy.h`, `perf_level.h`, `rate_limiter.h`, backup engine, memory util, transaction DB, and write batch with index.
- RocksJNI callback adapters: `compaction_filter_factory_jnicallback.h`, `comparatorjnicallback.h`, `event_listener_jnicallback.h`, `loggerjnicallback.h`, `table_filter_jnicallback.h`, `trace_writer_jnicallback.h`, `transaction_notifier_jnicallback.h`, `wal_filter_jnicallback.h`, and `writebatchhandlerjnicallback.h`.
- Java RocksDB classes: the code assumes exact class names under `org/rocksdb`, including nested classes such as `Status$Code`, `WriteBatch$Handler`, `TransactionLogIterator$BatchResult`, `TransactionDB$DeadlockInfo`, and `WBWIRocksIterator$WriteType`.
- Java standard library integration: `java/lang/String`, `StringBuilder`, boxed numeric wrappers, exceptions, `java/util/List`, `Iterator`, `ArrayList`, `Map`, `HashMap`, and `java/nio/ByteBuffer`.
- Native implementation files include this header to obtain method IDs and conversion helpers while implementing JNI entry points for RocksDB, options, iterators, write batches, transactions, backup, statistics, and callbacks.

## Risks and Edge Cases

- Most method and field IDs are found by literal JNI signatures. Any Java method rename, signature change, nested-class rename, or constructor reorder breaks native code at runtime.
- `JavaClass::getJClass()` asserts non-null after `FindClass()`. In release builds without assertions, callers still depend on subsequent null checks; in debug builds, a class-loading issue can abort rather than propagate cleanly.
- JNI local reference cleanup is inconsistent in some success paths. Repeated construction of backup info, table properties, or transaction objects in large loops can pressure the local reference table if callers do not manage frames or if temporary refs are not deleted.
- `StatusJni::toCppStatus(JNIEnv*, jobject)` obtains `jstate` but does not copy the state string into the constructed native `Status`, so round-tripping Java status state through this path loses detail beyond code/subcode.
- `JniUtil::check_if_jlong_fits_size_t()` casts `jlong` to `uint64_t`; negative Java values become huge and fail the size check, which is likely intentional for sizes but important for callers expecting signed semantics.
- `JniUtil::k_op_region()` attempts `FindClass("/lang/java/OutOfMemoryError")`, which looks like an invalid Java class name compared with `java/lang/OutOfMemoryError`. If allocation ever fails here, exception construction may not behave as intended.
- `ByteBufferJni::constructWith(direct=true)` can allocate native memory and hand it to `NewDirectByteBuffer()` without a visible deallocation path in this chunk. The matching Java/native cleanup contract must be verified in callers.
- Direct-buffer helpers validate capacity against `offset + length` without explicitly checking negative offsets or lengths before arithmetic. JNI callers should validate Java arguments before using these helpers.
- `KeyLockInfoJni::construct()` allocates a `jlongArray` sized to transaction IDs but does not populate it in this chunk; Java may see an all-zero ID array unless another path fills it.
- `DeadlockPathJni::construct()` requests constructor signature `"([LDeadlockInfo;Z)V"`, which lacks the full package/binary class name normally required for object arrays. That is a high-risk signature if not matched by JNI resolution behavior elsewhere.
- `FilterPolicyJni::getFilterPolicyType()` recognizes `"rocksdb.BuiltinBloomFilter"` but the enum includes `kRibbonFilterPolicy`; ribbon policy detection is not present in this chunk.
- Enum mappings use default fallbacks rather than throwing for unknown values. That preserves compatibility but can silently turn bad Java values into valid RocksDB defaults, changing behavior without a visible error.
- `TickerTypeJni` uses signed `jbyte` values and negative constants for many newer tickers. Java enum value code and tests must preserve signed-byte semantics exactly.
- The chunk ends in the middle of `CompactionReasonJni::toJavaCompactionReason()`, so this report cannot validate the complete compaction-reason mapping. The following chunk must confirm the rest of the cases and the reverse conversion.

## Test Signals

- Java/C++ class signature tests should instantiate every portal-backed Java class and call JNI paths that resolve each cached method, field, and constructor. This catches stale literal signatures.
- Status and exception tests should verify all `Status::Code` and `Status::SubCode` values round-trip to Java and back, including unknown/default behavior and `RocksDBException.getStatus()` extraction.
- Error-path tests should simulate Java allocation failures or pending exceptions around string, array, and object construction to verify local refs are cleaned and pending exceptions are preserved.
- Byte conversion tests should cover empty arrays, large arrays near Java array limits, `byte[][]`, UTF strings, null or empty optional strings, and `Slice` values containing embedded zero bytes.
- Direct-buffer tests should cover valid direct buffers, non-direct buffers, too-small capacities, nonzero offsets, negative Java arguments after entry-point validation, and `copyToDirect()` truncation semantics.
- Native-handle tests should verify Java ownership flags, pointer transfer through constructors, `BatchResultJni` write batch ownership release, and `ColumnFamilyOptionsJni` copy ownership.
- Collection conversion tests should check `HashMapJni::fromCppMap()` for string/string, string/int, string/long, and int/long maps, including null treatment for empty values.
- Callback tests should exercise Java compaction filter factory, transaction notifier, comparator bridge methods, table filter, logger, and write batch handler callbacks from native code.
- Metadata construction tests should validate `BackupInfo`, `WriteBatch.SavePoint`, `TableProperties`, `ColumnFamilyDescriptor`, `ThreadStatus`, waiting transaction, deadlock info/path, and key lock info fields visible on the Java side.
- Enum tests should assert every Java enum value maps to the intended C++ enum and back for compression, compaction, WAL recovery, stats, rate limiter, memory usage, perf level, transaction policy, table options, thread status, ticker, and histogram mappings.
- Compatibility tests should pin `TickerTypeJni` and `HistogramTypeJni` byte values, especially negative ticker values, reserved max values, and skipped histogram slots.
- Boundary tests for this chunk should ensure `CompactionStyleJni` is complete and should be paired with the next chunk's tests for the complete `CompactionReasonJni` mapping.
