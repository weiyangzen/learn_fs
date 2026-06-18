# Grouped Research: subset-b-008656

This grouped report covers RocksDB Java JNI transaction, write batch, TTL, WAL filter, callback, sample, and abstract callback source files. Each file section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/transaction.cc

## Purpose
This file is the JNI bridge for `org.rocksdb.Transaction`, exposing C++ `ROCKSDB_NAMESPACE::Transaction` behavior to Java. It translates Java native handles, byte arrays, direct byte buffers, transaction options, snapshots, savepoints, lock metadata, write batches, and transaction lifecycle calls into C++ transaction method calls.

## Important APIs, Types, and Functions
The exported JNI functions cover snapshot control (`setSnapshot`, `setSnapshotOnNextOperation`, `getSnapshot`, `clearSnapshot`), lifecycle (`prepare`, `commit`, `rollback`, `disposeInternal`), savepoints (`setSavePoint`, `rollbackToSavePoint`), reads (`get`, `getDirect`, `multiGet`, `getForUpdate`, `multiGetForUpdate`), writes (`put`, `merge`, `delete`, `singleDelete`), untracked writes, indexing toggles, log data, counters, write options, locking helpers (`undoGetForUpdate`), recovery helpers (`rebuildFromWriteBatch`, `getCommitTimeWriteBatch`), transaction naming, IDs, waiting transaction inspection, and state mapping. Helper typedefs and functions such as `FnWriteKVParts`, `txn_write_kv_parts_helper`, `FnWriteK`, and `txn_write_k_helper` centralize callback binding for fragmented key/value operations.

## Control Flow
Most functions reinterpret a Java `long` as a RocksDB pointer, build `Slice` or `PinnableSlice` wrappers from Java inputs, call the C++ transaction API, and translate `Status` or `KVException` results back to Java exceptions or return codes. Single-key array operations use `JByteArraySlice`; direct buffer paths use `JDirectBufferSlice`; fixed-output reads use `JByteArrayPinnableSlice` or `JDirectBufferPinnableSlice` and return either copied bytes or fetch result codes. Multi-get paths use `MultiGetJNIKeys`, optional column-family handle vectors, RocksDB multi-get APIs, and `MultiGetJNIValues` for result array construction. Fragmented key/value writes iterate `byte[][]`, pin each element, build `SliceParts`, call the bound transaction method, and release all JNI references afterward.

## State and Persistence Behavior
The file mutates live transaction state: snapshots, savepoints, prepare/commit/rollback state, write batch contents, lock tracking, lock timeout, transaction name, log number, indexing state, and write options. Persistence is indirect through transaction commit and WAL/write batch integration. Returned snapshot and write batch handles are borrowed C++ pointers, while `disposeInternal` deletes the transaction object owned by the Java wrapper.

## Dependencies and Integration Points
It depends on RocksDB transaction utilities, `portal.h` JNI helpers, `kv_helper.h`, `jni_multiget_helpers.h`, and `cplusplus_to_java_convert.h`. It integrates with Java `Transaction`, `ReadOptions`, `WriteOptions`, `ColumnFamilyHandle`, `Snapshot`, `TransactionNotifier`, `WriteBatch`, and nested transaction metadata types through generated JNI headers and portal constructors.

## Risks and Edge Cases
Handle casts assume Java passes valid live native handles. Fragmented writes explicitly rely on enough JNI local references; the helper throws a RocksDB exception if `EnsureLocalCapacity` fails. Multi-part key/value helpers must release all pinned arrays on every exception path. Direct buffer paths require direct buffers and valid offsets. The transaction state enum is manually mapped to byte constants, so Java and C++ enum ordering must remain synchronized. `getName` uses `NewStringUTF(name.data())`, so embedded NUL handling depends on transaction names being UTF-compatible C strings. `getWaitingTxns` and state/ID access expose live transaction internals without ownership transfer.

## Test Signals
Coverage should exercise byte-array and direct-buffer reads/writes, column-family overloads, not-found return conventions, `getForUpdate` conflict behavior, fragmented `SliceParts` writes, savepoint rollback, transaction state byte values, waiting transaction object construction, and exception paths for RocksDB `Status`. The Java transaction samples in this subset provide behavioral signals for read committed, snapshot isolation, `getForUpdate`, savepoints, rollback, and commit conflict handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction_db.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/transaction_db.cc

## Purpose
This file bridges `org.rocksdb.TransactionDB` to C++ `TransactionDB`. It opens transaction-aware databases, creates transactions, closes and disposes native database handles, and exposes prepared transaction, lock, and deadlock inspection APIs to Java.

## Important APIs, Types, and Functions
Key JNI exports include two `open` overloads, `disposeInternalJni`, `closeDatabase`, transaction creation overloads with optional `TransactionOptions` and reusable old transaction handles, `getTransactionByName`, `getAllPreparedTransactions`, `getLockStatusData`, `getDeadlockInfoBuffer`, and `setDeadlockInfoBufferSize`. It uses `Options`, `DBOptions`, `TransactionDBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyOptions`, `ColumnFamilyHandle`, `Transaction`, `KeyLockInfo`, `DeadlockPath`, and `DeadlockInfo`.

## Control Flow
The simple open path converts a Java path string, calls `TransactionDB::Open`, releases the string, and returns a DB pointer or throws `RocksDBException`. The column-family open path converts Java `byte[][]` names and `long[]` option handles to descriptor vectors, calls the column-family open overload, and returns a `long[]` whose first element is the DB handle followed by column-family handles. Transaction creation reinterprets write option and transaction option handles and calls `BeginTransaction`. Metadata getters convert native vectors and maps into Java arrays, maps, and nested objects through portal helpers.

## State and Persistence Behavior
Opening creates persistent database state on disk. Begin-transaction calls allocate or reuse C++ transaction objects. `closeDatabase` calls `TransactionDB::Close`, while `disposeInternalJni` deletes the database object. Prepared transaction and lock/deadlock methods expose in-memory transaction manager state. `setDeadlockInfoBufferSize` mutates native diagnostic buffer capacity.

## Dependencies and Integration Points
The bridge depends on `rocksdb/utilities/transaction_db.h`, `rocksdb/options.h`, transaction utilities, and RocksJNI portal conversion helpers. It integrates with Java `TransactionDB`, `Transaction`, `TransactionDBOptions`, `TransactionOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `TransactionDB.KeyLockInfo`, `TransactionDB.DeadlockInfo`, and `TransactionDB.DeadlockPath`.

## Risks and Edge Cases
The column-family open path has many JNI cleanup branches; leaks or missed releases would pin Java arrays or strings. The `beginTransaction_withOld` overload asserts that RocksDB returns the same transaction pointer that Java supplied, which is a critical ownership assumption. `getAllPreparedTransactions` returns raw native transaction pointers without allocating Java-owned C++ transactions. In `getDeadlockInfoBuffer`, the inner `jdeadlock_infos` array length is set from `deadlock_info_buffer.size()` instead of `deadlock_infos.size()`, which can create wrong-sized Java arrays and should be tested. Local references for constructed deadlock objects are not always deleted after array insertion.

## Test Signals
Tests should cover simple open, column-family open result ordering, close error propagation, transaction reuse, named prepared transaction lookup, lock status map conversion, deadlock info array conversion with paths of varying lengths, and deadlock buffer sizing. Recovery tests with prepared transactions are especially relevant because the file returns native transaction handles discovered from the transaction DB.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction_db.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction_db_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/transaction_db_options.cc

## Purpose
This file exposes C++ `TransactionDBOptions` fields to Java `TransactionDBOptions`. It is a thin native options bridge for lock table sizing, lock timeout behavior, and write policy.

## Important APIs, Types, and Functions
Exports include `newTransactionDBOptions`, getters and setters for `max_num_locks`, `num_stripes`, `transaction_lock_timeout`, `default_lock_timeout`, and `write_policy`, plus `disposeInternalJni`. The write policy conversion uses `TxnDBWritePolicyJni::toJavaTxnDBWritePolicy` and `toCppTxnDBWritePolicy`.

## Control Flow
The constructor allocates a new `TransactionDBOptions` and returns its pointer. Each getter casts the Java handle and returns a field value. Each setter casts the handle and directly assigns a C++ field. Disposal deletes the native options object.

## State and Persistence Behavior
The file only mutates an in-memory options object. These options affect future `TransactionDB::Open` behavior but are not persisted by this bridge. The Java wrapper owns the allocated native options handle until disposal.

## Dependencies and Integration Points
It depends on the generated `org_rocksdb_TransactionDBOptions` header, RocksDB transaction DB utilities, pointer conversion helpers, and portal enum conversion helpers. It is consumed by Java `TransactionDBOptions` and by `transaction_db.cc` open calls.

## Risks and Edge Cases
There is no range validation in JNI; Java must validate or RocksDB must tolerate invalid lock counts, stripe counts, and timeout values. Write policy byte conversion depends on Java and portal enum mappings remaining synchronized. Passing a disposed or null handle would lead to undefined native behavior.

## Test Signals
Tests should verify round-trip getters/setters, enum conversion for all write policies, disposal behavior through Java ownership, and that configured options affect `TransactionDB.open` behavior where observable, such as lock timeout behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction_db_options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction_log.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/transaction_log.cc

## Purpose
This file bridges Java `TransactionLogIterator` to C++ `TransactionLogIterator`, allowing Java to iterate WAL transaction log batches.

## Important APIs, Types, and Functions
Exports include `disposeInternalJni`, `isValid`, `next`, `status`, and `getBatch`. It uses `rocksdb/transaction_log.h`, `BatchResult`, and `BatchResultJni::construct`.

## Control Flow
Each method casts the Java `long` handle to `TransactionLogIterator*`. Validity and movement directly call `Valid()` and `Next()`. `status` retrieves iterator status and throws a Java `RocksDBException` on errors. `getBatch` calls `GetBatch()` and constructs the Java `TransactionLogIterator.BatchResult` object through portal conversion.

## State and Persistence Behavior
The iterator reads persistent WAL state from an existing RocksDB instance but does not mutate database contents. `next` advances iterator state. `disposeInternalJni` deletes the native iterator object.

## Dependencies and Integration Points
This bridge integrates with Java APIs that obtain transaction log iterators from RocksDB and then inspect batch sequence numbers and write batches. It depends on RocksJNI portal conversion for batch result construction.

## Risks and Edge Cases
Calling `getBatch` when the iterator is invalid depends on C++ iterator preconditions and Java wrapper discipline. `status` must be checked by callers after iteration. Invalid or double-disposed handles would crash. The returned batch result may contain a write batch handle whose ownership semantics are governed by the portal constructor.

## Test Signals
Tests should write data, obtain updates since a sequence number, iterate batches, verify `isValid` and `next`, inspect returned batch contents, and assert that iterator errors propagate through `status`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction_log.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction_notifier.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/transaction_notifier.cc

## Purpose
This file creates and disposes native callback wrappers for Java `AbstractTransactionNotifier`. It lets Java code provide a transaction notifier used when a transaction snapshot is created on the next operation.

## Important APIs, Types, and Functions
The file exports `createNewTransactionNotifier` and `disposeInternalJni`. Creation allocates a `TransactionNotifierJniCallback`, wraps it in a `std::shared_ptr`, and returns a pointer to that shared pointer.

## Control Flow
Creation receives the Java callback object, constructs the C++ callback with the current `JNIEnv`, then allocates a shared pointer wrapper. Disposal casts the handle back to `std::shared_ptr<TransactionNotifierJniCallback>*` and deletes the wrapper, decrementing the reference count.

## State and Persistence Behavior
The native state is callback ownership and lifetime only. No RocksDB data is persisted. The shared pointer is passed to transaction code through `transaction.cc` when Java calls `setSnapshotOnNextOperation`.

## Dependencies and Integration Points
It depends on `TransactionNotifierJniCallback`, pointer conversion helpers, and the generated Java notifier header. It integrates with Java `AbstractTransactionNotifier` and C++ `Transaction::SetSnapshotOnNextOperation`.

## Risks and Edge Cases
Ownership is nontrivial because Java stores a pointer to a shared pointer, not the callback object itself. Disposing while a transaction still holds a shared reference is safe at the C++ object level, but disposing too early must not leave Java-side assumptions inconsistent. The TODO notes possible future refactoring around callback ownership.

## Test Signals
Tests should verify notifier creation, callback invocation when snapshots are created, and disposal after use. Lifetime tests should include a notifier passed to a transaction and disposed after the transaction no longer needs it.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction_notifier.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction_notifier_jnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/transaction_notifier_jnicallback.cc

## Purpose
This file implements the C++ callback class that forwards RocksDB `TransactionNotifier::SnapshotCreated` events into Java.

## Important APIs, Types, and Functions
It defines `TransactionNotifierJniCallback::TransactionNotifierJniCallback` and `SnapshotCreated`. The constructor caches the Java `snapshotCreated` method ID using `AbstractTransactionNotifierJni`. `SnapshotCreated` calls the Java callback with the native snapshot pointer.

## Control Flow
When RocksDB invokes `SnapshotCreated`, the callback attaches or retrieves a `JNIEnv` through `getJniEnv`, calls the cached Java method on the global callback object, passes `GET_CPLUSPLUS_POINTER(newSnapshot)`, describes any Java exception to stderr, and releases the JNI environment if it attached the current thread.

## State and Persistence Behavior
The callback stores only a method ID and the inherited global Java callback reference. It does not own the snapshot and does not persist data. The snapshot pointer is passed into Java for wrapper construction or notification use.

## Dependencies and Integration Points
It depends on `transaction_notifier_jnicallback.h`, `cplusplus_to_java_convert.h`, and `portal.h`. It is allocated by `transaction_notifier.cc` and passed through `transaction.cc` into transaction snapshot-on-next-operation flow.

## Risks and Edge Cases
The constructor does not explicitly handle a null method ID beyond storing it; later callback invocation would fail if method lookup threw. `SnapshotCreated` asserts that a JNI environment is available, so callback execution from unexpected threads relies on `JniCallback` attach support. Java exceptions are described but not propagated back into RocksDB transaction control flow.

## Test Signals
Tests should subclass `AbstractTransactionNotifier`, trigger snapshot creation, verify the Java method receives a valid snapshot handle, and exercise exception behavior in the Java callback to ensure it does not crash native code.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction_notifier_jnicallback.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction_notifier_jnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/transaction_notifier_jnicallback.h

## Purpose
This header declares the JNI callback adapter that implements RocksDB `TransactionNotifier` using a Java callback object.

## Important APIs, Types, and Functions
`TransactionNotifierJniCallback` inherits from `JniCallback` and `TransactionNotifier`. It declares a constructor accepting `JNIEnv*` and a Java notifier object, and overrides `SnapshotCreated(const Snapshot*)`. The private state is `jmethodID m_jsnapshot_created_methodID`.

## Control Flow
The header establishes the cross-language callback contract. RocksDB calls `SnapshotCreated`; the implementation must attach to the JVM, call Java, and release thread attachment state.

## State and Persistence Behavior
The class stores callback identity through `JniCallback` and the cached Java method ID. It does not store or own snapshots and has no persistent database behavior.

## Dependencies and Integration Points
It includes RocksDB transaction utilities and the RocksJNI `jnicallback.h` base. It is used by `transaction_notifier.cc`, `transaction_notifier_jnicallback.cc`, and `transaction.cc` snapshot notifier paths.

## Risks and Edge Cases
The header comment explicitly notes that snapshot Java object allocation is not optimized or cached, so high-frequency snapshot notifications may allocate heavily. As with all callback adapters, Java callback lifetime and native callback lifetime must remain aligned.

## Test Signals
Compile-time tests should catch signature drift against RocksDB `TransactionNotifier`. Runtime tests should validate notifier subclassing, method dispatch, snapshot handle validity, and cleanup after callback disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction_notifier_jnicallback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/transaction_options.cc

## Purpose
This file exposes C++ `TransactionOptions` to Java `TransactionOptions`. It configures per-transaction behavior such as snapshot creation, deadlock detection, lock timeout, expiration, deadlock depth, and maximum write batch size.

## Important APIs, Types, and Functions
Exports include `newTransactionOptions`, `isSetSnapshot`, `setSetSnapshot`, `isDeadlockDetect`, `setDeadlockDetect`, `getLockTimeout`, `setLockTimeout`, `getExpiration`, `setExpiration`, `getDeadlockDetectDepth`, `setDeadlockDetectDepth`, `getMaxWriteBatchSize`, `setMaxWriteBatchSize`, and `disposeInternalJni`.

## Control Flow
Construction allocates `TransactionOptions`. Getters cast the native handle and return raw C++ fields. Setters cast and assign raw fields. Disposal deletes the native options object.

## State and Persistence Behavior
The file mutates only an in-memory options object. These fields affect future `BeginTransaction` calls but are not persisted directly. Ownership is tied to the Java wrapper.

## Dependencies and Integration Points
It depends on the generated `org_rocksdb_TransactionOptions` JNI header, RocksDB transaction DB utilities, and pointer conversion helpers. It integrates with Java `TransactionOptions`, `TransactionDB.beginTransaction`, and optimistic transaction option analogs in the broader RocksJava API.

## Risks and Edge Cases
JNI does no validation for negative or overly large timeouts, expiration values, deadlock depth, or max write batch size. Boolean assignments rely on `jboolean` conversion to C++ `bool`. Java and native ownership must prevent use after disposal.

## Test Signals
Tests should verify option round-trips, transaction creation with `set_snapshot`, lock timeout behavior, deadlock detection toggles, expiration effects, and disposal through try-with-resources.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/transaction_options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/ttl.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/ttl.cc

## Purpose
This file bridges Java `TtlDB` to C++ `DBWithTTL`, enabling databases and column families with time-to-live expiration semantics.

## Important APIs, Types, and Functions
Exports include `open`, `openCF`, `disposeInternalJni`, `closeDatabase`, and `createColumnFamilyWithTtl`. It uses `Options`, `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyOptions`, `ColumnFamilyHandle`, and `DBWithTTL`.

## Control Flow
The simple open path converts the database path string, calls `DBWithTTL::Open`, releases the path, and returns the DB handle or throws. The column-family path converts Java column family names with `JniUtil::byteStrings`, maps Java option handles to descriptors, copies Java TTL integers into a vector, opens the TTL DB, and returns a `long[]` containing the DB handle followed by column family handles. `createColumnFamilyWithTtl` pins the Java column family name, calls `CreateColumnFamilyWithTtl`, releases the array, and returns the handle.

## State and Persistence Behavior
Open and create-column-family operations create or access persistent RocksDB state with TTL behavior. Expiration behavior is implemented by RocksDB and compaction, not directly by JNI. `disposeInternalJni` deletes the `DBWithTTL` object. `closeDatabase` is intentionally disabled and does not close, pending an upstream issue noted in a TODO.

## Dependencies and Integration Points
It depends on `rocksdb/utilities/db_ttl.h`, generated `TtlDB` JNI headers, conversion helpers, and portal utilities. Java `TtlDB` extends RocksDB, so the bridge reuses ordinary RocksDB handle conventions.

## Risks and Edge Cases
`closeDatabase` is a no-op, so lifecycle differs from other DB wrappers and relies on disposal for cleanup. The column-family open path assumes the number and ordering of names, options, and TTLs line up. Invalid TTL values are not validated here. Error branches must release strings and arrays correctly.

## Test Signals
Tests should cover simple open, column-family open with multiple TTLs, read-only mode, creating a TTL column family, cleanup behavior despite no-op close, and expiration semantics after compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/ttl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/wal_filter.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/wal_filter.cc

## Purpose
This file constructs native WAL filter callback objects for Java `AbstractWalFilter` implementations.

## Important APIs, Types, and Functions
It exports `createNewWalFilter`, which allocates `WalFilterJniCallback` with the Java callback object and returns its native pointer.

## Control Flow
Java calls the native constructor hook. JNI receives the Java filter object, creates the C++ callback adapter, and returns the pointer with `GET_CPLUSPLUS_POINTER`. Disposal is handled by the Java callback object hierarchy and related native callback infrastructure, not in this file.

## State and Persistence Behavior
The file only creates callback state. The callback is later used during WAL recovery to observe and optionally modify WAL processing, but no persistence is done at construction time.

## Dependencies and Integration Points
It depends on the generated `AbstractWalFilter` JNI header, pointer conversion helpers, and `wal_filter_jnicallback.h`. It integrates with RocksDB options that accept a WAL filter.

## Risks and Edge Cases
Allocation failures are not explicitly handled. Correct lifetime depends on Java owning and disposing the callback consistently with RocksDB options and database lifetime. The Java object must remain valid while RocksDB may call into the filter.

## Test Signals
Tests should instantiate a Java WAL filter, open a DB with it, force WAL recovery, and verify that the callback methods are invoked and that native callback disposal occurs after DB shutdown.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/wal_filter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/wal_filter_jnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/wal_filter_jnicallback.cc

## Purpose
This file implements the C++ `WalFilterJniCallback` that forwards RocksDB WAL filter calls into Java `AbstractWalFilter`.

## Important APIs, Types, and Functions
The constructor caches the Java filter name and method IDs for `columnFamilyLogNumberMap` and `logRecordFoundProxy`. It implements `ColumnFamilyLogNumberMap`, `LogRecordFound`, and `Name`.

## Control Flow
Construction calls Java `name()`, copies the string into `m_name`, and caches method IDs. `ColumnFamilyLogNumberMap` attaches to the JVM, converts C++ maps to Java hash maps, calls the Java callback, deletes local refs, describes exceptions, and releases the environment. `LogRecordFound` converts the log file name to Java, calls the Java proxy with log number and native write batch handles, decodes a packed short into a `WalProcessingOption` byte and `batch_changed` flag, then returns the converted C++ option.

## State and Persistence Behavior
The callback stores the immutable filter name and method IDs. During WAL replay it may influence recovery state by returning processing options and indicating whether a replacement write batch was produced. It does not itself persist data.

## Dependencies and Integration Points
It depends on conversion helpers, portal method lookups, `WalFilter`, `WriteBatch`, and Java `AbstractWalFilter`. It is constructed by `wal_filter.cc` and used by RocksDB WAL recovery.

## Risks and Edge Cases
If Java name or method lookup fails in the constructor, the object may be partially initialized. Exceptions inside callbacks are described to stderr and often degrade to `kCorruptedRecord`, which can affect recovery. The packed short contract between Java and C++ must keep high byte as processing option and low byte as `batch_changed`. `Name()` returns `m_name.get()`, so `m_name` must be set.

## Test Signals
Tests should verify name caching, map conversion for column-family/log-number metadata, all `WalProcessingOption` values, `batch_changed` propagation with replacement batches, and callback exception behavior during recovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/wal_filter_jnicallback.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/wal_filter_jnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/wal_filter_jnicallback.h

## Purpose
This header declares the C++ adapter that implements RocksDB `WalFilter` by calling a Java filter object.

## Important APIs, Types, and Functions
`WalFilterJniCallback` inherits from `JniCallback` and `WalFilter`. It declares overrides for `ColumnFamilyLogNumberMap`, `LogRecordFound`, and `Name`. Private state includes `std::unique_ptr<const char[]> m_name` and cached method IDs.

## Control Flow
The header defines the callback surface RocksDB will use during WAL recovery. Implementations must convert native maps, log metadata, and write batch pointers into Java callback parameters and convert Java decisions back to RocksDB enums.

## State and Persistence Behavior
State is limited to callback identity, cached method IDs, and immutable name. Persistence effects are indirect through WAL recovery decisions made by Java.

## Dependencies and Integration Points
It includes `rocksdb/wal_filter.h` and RocksJNI `jnicallback.h`. It is used by `wal_filter.cc` and `wal_filter_jnicallback.cc`, and integrates with Java `AbstractWalFilter`.

## Risks and Edge Cases
The callback object must outlive any RocksDB recovery path using it. Name and method ID initialization failures can leave an unusable adapter. The C++ and Java packed-result protocol must stay synchronized.

## Test Signals
Compile-time tests should catch signature changes in RocksDB `WalFilter`. Runtime tests should validate Java subclass dispatch, name stability, recovery decisions, and cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/wal_filter_jnicallback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/write_batch.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/write_batch.cc

## Purpose
This file bridges Java `WriteBatch` and `WriteBatch.Handler` to C++ `WriteBatch`, exposing batch construction, mutation, serialization, iteration, savepoints, operation presence flags, WAL termination point metadata, and disposal.

## Important APIs, Types, and Functions
Exports include constructors from reserved bytes and serialized bytes, `count0Jni`, `clear0Jni`, savepoint APIs, `setMaxBytesJni`, put/merge/delete/singleDelete/deleteRange overloads with optional column family, direct-buffer put/delete helpers, `putLogDataJni`, `iterate`, `data`, `getDataSize`, operation flag getters, WAL termination point setters/getters, disposal, and handler creation.

## Control Flow
Most mutation methods cast the `WriteBatch*`, build lambdas around the appropriate C++ method, and use `JniUtil::kv_op`, `k_op`, or direct-buffer helpers to convert Java byte arrays or buffers into `Slice`s. Status results are converted to Java `RocksDBException`s. Iteration casts the handler handle to `WriteBatchHandlerJniCallback` and calls `WriteBatch::Iterate`. Serialization copies `WriteBatch::Data()` to a Java byte array.

## State and Persistence Behavior
The file mutates the in-memory write batch sequence of operations. Batches are persisted only when written to a DB by other APIs. Savepoint and max-bytes state live inside the batch. WAL termination point state is exposed through `MarkWalTerminationPoint` and `GetWalTerminationPoint`. Disposal deletes the C++ batch.

## Dependencies and Integration Points
It depends on RocksDB write batch APIs, internal write batch headers, generated Java JNI headers, portal conversions, and `writebatchhandlerjnicallback.h`. It integrates with Java `WriteBatch`, `WriteBatch.Handler`, `WriteOptions`, `RocksDB.write`, transaction code, and WAL/log inspection.

## Risks and Edge Cases
Direct-buffer overloads accept a nullable column-family handle to mean default column family, unlike array overloads that assert non-null for column-family variants. Handler iteration depends on callback exception conversion. Serialized constructor accepts arbitrary byte arrays and trusts RocksDB parsing later. `getWalTerminationPoint` returns a Java savepoint object from native state that must match Java expectations.

## Test Signals
Tests should cover every operation type, column-family and default variants, direct-buffer variants, serialized round trip, savepoint rollback/pop errors, handler iteration callbacks, operation presence flags, data size, WAL termination point, and disposal through try-with-resources. `write_batch_test.cc` provides native helpers for deeper internal test assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/write_batch.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/write_batch_test.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/write_batch_test.cc

## Purpose
This file exposes test-only JNI helpers for Java write batch tests. It inspects internal write batch contents by applying a batch to a temporary memtable and exposes internal sequence and append helpers.

## Important APIs, Types, and Functions
Exports include `WriteBatchTest.getContents`, `WriteBatchTestInternalHelper.setSequence`, `sequence`, and `append`. It uses `WriteBatchInternal`, `MemTable`, `ColumnFamilyMemTablesDefault`, `InternalKeyComparator`, `SkipListFactory`, `WriteBufferManager`, and internal iterator APIs.

## Control Flow
`getContents` casts the batch, creates a temporary memtable configured with bytewise comparator and skip-list factory, inserts the batch with `WriteBatchInternal::InsertInto`, iterates internal keys, parses each `InternalKey`, appends a textual representation of operation type, key, value, and sequence, checks count consistency, releases the memtable, and returns the text as a Java byte array. Internal helper methods cast write batch handles and call `WriteBatchInternal` sequence and append functions.

## State and Persistence Behavior
The file does not persist data. It builds temporary in-memory memtable state for inspection. `setSequence` mutates the sequence number stored in a write batch, and `append` mutates the first batch by appending the second.

## Dependencies and Integration Points
This file depends on RocksDB internal DB headers, test harness utilities, and generated Java test JNI headers. It is intended for RocksJava tests rather than production runtime code.

## Risks and Edge Cases
Because it uses internal RocksDB APIs, it is sensitive to internal type and constructor changes. It manually formats expected strings, so test expectations depend on exact internal operation ordering and sequence display. The temporary memtable must be ref/unref balanced; the code calls `mem->Ref()` and `delete mem->Unref()`.

## Test Signals
It is itself a test signal for Java `WriteBatch`: operation formatting should cover put, merge, delete, single delete, range delete, log data, sequence numbers, count mismatches, append behavior, and sequence mutation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/write_batch_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/write_batch_with_index.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/write_batch_with_index.cc

## Purpose
This file bridges Java `WriteBatchWithIndex` and `WBWIRocksIterator` to C++ `WriteBatchWithIndex` and `WBWIIterator`. It supports indexed batch mutation, batch reads, merged DB reads, iterator navigation, and write-entry extraction.

## Important APIs, Types, and Functions
Exports include constructors with default, overwrite-key, and comparator/reserved-bytes options; count, put, merge, delete, single delete, delete range, log data, clear, savepoint, max bytes, `getWriteBatch`, iterator creation, `getFromBatch`, `getFromBatchAndDB`, disposal, WBWI iterator navigation, seek variants, status, entry extraction, and unsupported refresh methods.

## Control Flow
Mutation methods mirror `write_batch.cc`, using `JniUtil` conversion helpers around C++ `WriteBatchWithIndex` methods. Constructors choose either bytewise comparator or a fallback comparator based on a Java comparator type byte. Read helpers build lambdas for `GetFromBatch` or `GetFromBatchAndDB` and call `JniUtil::v_op`. Iterator constructors allocate C++ iterators. Seek methods copy byte-array targets or use direct-buffer helpers. `entry1` reads `WBWIIterator::Entry`, allocates native `Slice` wrappers for key and optional value, and returns a three-element `long[]` of write type, key slice handle, and value slice handle.

## State and Persistence Behavior
The object stores an in-memory write batch plus an index for lookup and iteration. It can read through to a base DB, but persistence occurs only when the underlying write batch is later written. Iterator state advances independently. `getWriteBatch` exposes the underlying batch pointer to Java, and disposal deletes the `WriteBatchWithIndex`.

## Dependencies and Integration Points
It depends on `rocksdb/utilities/write_batch_with_index.h`, generated `WriteBatchWithIndex` and `WBWIRocksIterator` headers, comparator types, and RocksJNI portal utilities. It integrates with Java comparators, `DirectSlice`, `WriteBatch`, `DBOptions`, `ReadOptions`, `RocksDB`, and column-family handles.

## Risks and Edge Cases
The `putDirectJni` and `deleteDirectJni` implementations cast the handle to `WriteBatch*` even though the Java method name is for `WriteBatchWithIndex`; this is suspicious because it may bypass or corrupt the indexed batch object unless Java passes an underlying write batch handle. `getWriteBatch` has a TODO about ownership, making wrapper disposal semantics important. `entry1` returns heap-allocated `Slice` wrappers that Java must close via `DirectSlice`. Seek methods allocate arrays based on Java lengths and must handle exceptions. Refresh is explicitly unsupported and always throws.

## Test Signals
Tests should cover all mutation variants, comparator-backed construction, overwrite-key behavior, indexed lookup with and without DB fallback, iterator order, column-family iteration, direct and indirect seek variants, `entry1` slice cleanup, unsupported refresh exceptions, and ownership of `getWriteBatch`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/write_batch_with_index.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/write_buffer_manager.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/write_buffer_manager.cc

## Purpose
This file bridges Java `WriteBufferManager` to C++ `WriteBufferManager`, creating a shared native manager backed by a shared cache.

## Important APIs, Types, and Functions
Exports include `newWriteBufferManager` and `disposeInternalJni`. The constructor takes buffer size, a native handle to `std::shared_ptr<Cache>`, and an `allow_stall` flag, then returns a pointer to `std::shared_ptr<WriteBufferManager>`.

## Control Flow
Creation casts the cache handle to `std::shared_ptr<Cache>*`, constructs a `std::shared_ptr<WriteBufferManager>` with `std::make_shared`, allocates a wrapper shared pointer on the heap, and returns it. Disposal casts the handle back and deletes the wrapper, decrementing the shared manager reference.

## State and Persistence Behavior
The manager controls in-memory write buffer accounting and optional write stall behavior. It does not persist database data directly, but it influences memory pressure and write flow for DB instances using it.

## Dependencies and Integration Points
It depends on `rocksdb/write_buffer_manager.h`, `rocksdb/cache.h`, generated `WriteBufferManager` JNI headers, and pointer conversion helpers. It integrates with Java cache wrappers and options that accept a write buffer manager.

## Risks and Edge Cases
The cache handle must be a valid `std::shared_ptr<Cache>*`; invalid handles cause undefined behavior. Buffer size and stall flag are not validated here. The double-shared-pointer ownership pattern must align with Java disposal and any options holding the manager.

## Test Signals
Tests should construct with an LRU cache, attach to DB options, verify memory accounting or stall behavior where observable, and dispose after DB/options release without double-free.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/write_buffer_manager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/writebatchhandlerjnicallback.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/writebatchhandlerjnicallback.cc

## Purpose
This file implements the C++ `WriteBatchHandlerJniCallback` that lets a Java `WriteBatch.Handler` receive callbacks while RocksDB iterates a native write batch.

## Important APIs, Types, and Functions
The constructor caches Java method IDs for put, merge, delete, single delete, delete range, log data, blob index, prepare/commit/rollback/noop markers, commit-with-timestamp, and continue. It implements `WriteBatch::Handler` methods such as `PutCF`, `Put`, `MergeCF`, `DeleteCF`, `SingleDeleteCF`, `DeleteRangeCF`, `LogData`, `PutBlobIndexCF`, `MarkBeginPrepare`, `MarkEndPrepare`, `MarkNoop`, `MarkRollback`, `MarkCommit`, `MarkCommitWithTimestamp`, and `Continue`. Helper methods `kv_op` and `k_op` convert native slices to Java byte arrays and convert Java `RocksDBException` back to C++ `Status`.

## Control Flow
For key/value callbacks, the handler copies slices into Java byte arrays, calls the matching Java method, deletes local refs, and returns OK or a status extracted from a thrown `RocksDBException`. Key-only callbacks follow the same pattern with one byte array. Marker methods either call Java directly or use `k_op`/`kv_op` for transaction IDs and timestamps. `Continue` calls the Java continue method and returns whether iteration should proceed.

## State and Persistence Behavior
The callback stores cached method IDs and a `JNIEnv*` captured at construction. It does not mutate persistence directly; it observes batch contents during iteration. Java callbacks may throw RocksDB exceptions that influence native iteration status.

## Dependencies and Integration Points
It depends on `writebatchhandlerjnicallback.h` and `portal.h`. It is created by `write_batch.cc` and passed into `WriteBatch::Iterate`, integrating with Java `WriteBatch.Handler`.

## Risks and Edge Cases
The file stores `m_env` rather than attaching per callback, so it assumes iteration occurs on the same Java-attached thread used to create the handler. Unexpected Java exceptions that are not convertible to RocksDB `Status` are described and often result in OK for status-returning callbacks, as marked by TODO comments. Frequent slice copying can be expensive for large batches. Constructor method lookup failures leave partially initialized callback objects.

## Test Signals
Tests should verify every callback type, column-family IDs, transaction marker callbacks, Java `continue` stopping iteration, Java `RocksDBException` conversion to native `Status`, behavior for unexpected exceptions, and local reference cleanup on large batches.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/writebatchhandlerjnicallback.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/writebatchhandlerjnicallback.h -->
# sources/storage-engines/rocksdb/java/rocksjni/writebatchhandlerjnicallback.h

## Purpose
This header declares the JNI adapter that implements RocksDB `WriteBatch::Handler` by dispatching each write batch record to Java.

## Important APIs, Types, and Functions
`WriteBatchHandlerJniCallback` inherits from `JniCallback` and `WriteBatch::Handler`. It declares overrides for write operations, range deletes, blob index records, transaction prepare/commit/rollback markers, `Continue`, and private helpers `kv_op` and `k_op`. Private state includes `JNIEnv* m_env` and cached `jmethodID`s for all Java callbacks.

## Control Flow
The class contract is callback driven: RocksDB iteration invokes handler methods, the implementation converts `Slice` data into Java arrays, calls Java methods, and maps Java exceptions to C++ statuses where the RocksDB handler API supports status returns.

## State and Persistence Behavior
The class stores callback identity and method IDs only. It does not own write batch data and does not persist data. It can influence iteration status through returned `Status` and `Continue`.

## Dependencies and Integration Points
It includes RocksDB `write_batch.h` and RocksJNI `jnicallback.h`. It is used by `write_batch.cc` and the Java `WriteBatch.Handler` API.

## Risks and Edge Cases
Because the header includes `JNIEnv*` as object state, thread-affinity assumptions are part of the design. API drift in RocksDB `WriteBatch::Handler` would require header updates. Exception conversion behavior depends on portal helpers.

## Test Signals
Compile-time checks should catch missing handler overrides. Runtime tests should cover callback dispatch for every declared method, stopping iteration, exception-to-status conversion, and handler disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/writebatchhandlerjnicallback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/samples/src/main/java/OptimisticTransactionSample.java -->
# sources/storage-engines/rocksdb/java/samples/src/main/java/OptimisticTransactionSample.java

## Purpose
This sample demonstrates Java `OptimisticTransactionDB` usage with read committed behavior, repeatable-read snapshot isolation, and monotonic atomic views using multiple snapshots.

## Important APIs, Types, and Functions
The class uses `Options`, `OptimisticTransactionDB`, `WriteOptions`, `ReadOptions`, `OptimisticTransactionOptions`, `Transaction`, `Snapshot`, `RocksDBException`, and `Status.Code.Busy`. Helper methods are `readCommitted`, `repeatableRead`, and `readCommitted_monotonicAtomicViews`.

## Control Flow
`main` opens an optimistic transaction DB at `/tmp/rocksdb_optimistic_transaction_example`, creates read/write options, and calls three scenario helpers. `readCommitted` starts a transaction, reads missing data, writes inside the transaction, verifies outside reads do not see it, writes another key outside, and commits. `repeatableRead` starts with `setSetSnapshot(true)`, captures the transaction snapshot, writes the same key outside, reads for update through the snapshot, expects commit conflict as `Busy`, and rolls back. The monotonic atomic view example advances snapshots during a transaction so an outside write can become visible without creating a conflict.

## State and Persistence Behavior
The sample writes to a persistent DB under `/tmp`. It mutates transaction-local write batches, DB state on commit, and read option snapshot state. `finally` blocks clear snapshots from `ReadOptions` after snapshot invalidation.

## Dependencies and Integration Points
It integrates public Java APIs with the native bridges in transaction and optimistic transaction JNI code. It is a user-facing example rather than a formal test, but it exercises snapshot and conflict semantics.

## Risks and Edge Cases
The fixed `/tmp` path can leave state between runs. Assertions require JVM assertions to be enabled to enforce checks. The monotonic view example contains `txn.put(valueX, valueX)` after reading key `x`, likely intentional or a sample typo, since it uses the value bytes as the key.

## Test Signals
The sample signals expected behavior for optimistic conflicts: outside writes to a read key should produce `Status.Code.Busy`, while unrelated outside writes should not block commit. It also signals that `ReadOptions.setSnapshot(null)` is required after transaction snapshot lifetime ends.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/samples/src/main/java/OptimisticTransactionSample.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/samples/src/main/java/RocksDBColumnFamilySample.java -->
# sources/storage-engines/rocksdb/java/samples/src/main/java/RocksDBColumnFamilySample.java

## Purpose
This sample demonstrates Java column-family creation, reopening a DB with multiple column families, writing to specific column families, atomic batch writes across column families, and dropping a column family.

## Important APIs, Types, and Functions
The class uses `RocksDB.loadLibrary`, `Options`, `RocksDB.open`, `ColumnFamilyDescriptor`, `ColumnFamilyOptions`, `ColumnFamilyHandle`, `DBOptions`, `WriteBatch`, and `WriteOptions`. The only entry point is `main`.

## Control Flow
The program expects a database path argument. It first opens a DB with `createIfMissing`, creates `new_cf`, and closes. It then builds descriptors for the default column family and `new_cf`, opens both, writes a key to the non-default family, creates a `WriteBatch` containing writes to both column families and a delete in `new_cf`, writes the batch atomically, drops `new_cf`, and finally closes all column family handles.

## State and Persistence Behavior
The sample creates persistent column-family metadata and key/value data under the provided path. It demonstrates that non-default column families must be listed when reopening and that column-family handles require explicit close.

## Dependencies and Integration Points
It exercises public Java DB and write-batch APIs, which route through JNI bridge files including RocksDB open code and `write_batch.cc`.

## Risks and Edge Cases
Assertions depend on JVM assertion settings. The sample creates `ColumnFamilyOptions` inside descriptors without explicit closing, which may be acceptable for a sample but is a lifecycle signal. The DB path argument is user-controlled and the sample drops the created column family.

## Test Signals
Useful checks include verifying column-family descriptor ordering, write-batch atomicity across column families, proper handle closure in finally, and drop-column-family behavior after writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/samples/src/main/java/RocksDBColumnFamilySample.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/samples/src/main/java/RocksDBSample.java -->
# sources/storage-engines/rocksdb/java/samples/src/main/java/RocksDBSample.java

## Purpose
This broad sample demonstrates core RocksJava APIs: options configuration, table and memtable factories, cache/filter/rate limiter setup, basic put/get/delete, write batches, statistics, iterators, and multi-get.

## Important APIs, Types, and Functions
It uses `Options`, `Filter`, `BloomFilter`, `ReadOptions`, `Statistics`, `RateLimiter`, `RocksDB`, compression and compaction enums, memtable configs, `PlainTableConfig`, `BlockBasedTableConfig`, `Cache`, `LRUCache`, `WriteOptions`, `WriteBatch`, ticker and histogram enums, `RocksIterator`, and `multiGetAsList`.

## Control Flow
The program validates a DB path argument, tries opening a missing DB and expects an exception, configures options and asserts round-trip option values, switches memtable and table factories, opens a DB for basic property checks, then reopens for a larger scenario. It writes multiplication-table keys, uses write batches for more keys, tests byte-array `get` overloads with insufficient and sufficient buffers, deletes data, writes with explicit `WriteOptions`, reads statistics, iterates forward and backward, seeks, collects keys, and multi-gets values with and without read options.

## State and Persistence Behavior
The sample creates persistent DB state at the provided path and many test keys. It mutates option objects, cache/filter/rate-limiter configuration, DB data, and iterator state. Resources are mostly scoped with try-with-resources.

## Dependencies and Integration Points
It exercises many public Java APIs and their JNI bridges, including ordinary DB operations, write batch bridges, iterator bridges, option bridges, statistics, and multi-get conversion.

## Risks and Edge Cases
Assertions require `-ea`. Existing DB contents may affect iteration and multi-get assumptions. Some resources such as `Cache cache` are not in try-with-resources in this sample. The sample catches final `RocksDBException` by printing rather than failing.

## Test Signals
This file is a compact integration smoke test for option setters/getters, open failure handling, byte-array get length contracts, not-found constants, write batch persistence, statistics enum coverage, iterator validity/status, seek behavior, and multi-get result size matching.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/samples/src/main/java/RocksDBSample.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/samples/src/main/java/TransactionSample.java -->
# sources/storage-engines/rocksdb/java/samples/src/main/java/TransactionSample.java

## Purpose
This sample demonstrates `TransactionDB` usage with read committed transactions, snapshot isolation, `getForUpdate` conflict detection, savepoints, rollback, and commit.

## Important APIs, Types, and Functions
The class uses `Options`, `TransactionDBOptions`, `TransactionDB`, `WriteOptions`, `ReadOptions`, `TransactionOptions`, `Transaction`, `Snapshot`, `RocksDBException`, and `Status.Code.Busy`. Scenario helpers are `readCommitted`, `repeatableRead`, and `readCommitted_monotonicAtomicViews`.

## Control Flow
`main` opens a transaction DB under `/tmp/rocksdb_transaction_example`, creates read/write options, and runs three scenarios. `readCommitted` writes inside a transaction, verifies outside reads do not see the uncommitted write, writes another key outside, and commits. `repeatableRead` starts with a transaction snapshot, writes the same key outside, sets the snapshot on `ReadOptions`, expects `getForUpdate` to throw `Busy`, and rolls back. The monotonic view scenario advances snapshots, uses a savepoint, reads for update after an outside write, writes the key, rolls back to the savepoint, then commits.

## State and Persistence Behavior
The sample writes persistent DB state under a fixed `/tmp` path and mutates transaction-local state, locks, savepoints, snapshots, and `ReadOptions`. It clears the snapshot from read options in finally blocks.

## Dependencies and Integration Points
It exercises Java transaction APIs backed by `transaction.cc`, `transaction_db.cc`, `transaction_options.cc`, and `transaction_db_options.cc`.

## Risks and Edge Cases
Fixed DB path can retain state across runs. Assertions need JVM assertion enablement. Snapshot lifetime must be respected by clearing `ReadOptions`. The scenario intentionally uses `Status.Code.Busy` as the conflict signal.

## Test Signals
The sample gives concrete expected behavior for transaction conflict detection, rollback, savepoint rollback, snapshot advancement, and commit visibility. It is a useful smoke test for JNI transaction and transaction option bridges.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/samples/src/main/java/TransactionSample.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/spotbugs-exclude.xml -->
# sources/storage-engines/rocksdb/java/spotbugs-exclude.xml

## Purpose
This XML file is the SpotBugs exclusion baseline for RocksJava. It suppresses known or accepted static-analysis findings so builds can focus on unsuppressed regressions.

## Important APIs, Types, and Functions
The file uses SpotBugs `FindBugsFilter` syntax with repeated `Match` blocks. It suppresses patterns such as `UPM_UNCALLED_PRIVATE_METHOD`, `MS_EXPOSE_REP`, `EI_EXPOSE_REP`, `EI_EXPOSE_REP2`, `BIT_IOR_OF_SIGNED_BYTE`, `ST_WRITE_TO_STATIC_FROM_INSTANCE_METHOD`, and `DMI_HARDCODED_ABSOLUTE_FILENAME`. It targets classes including callback bridge classes, options/descriptors, metadata DTOs, transaction info classes, iterator write entries, and backup/statistics/range wrappers.

## Control Flow
There is no runtime control flow. SpotBugs consumes the filter during static analysis and omits matching warnings. A commented-out `TransactionDB$KeyLockInfo` exclusion is retained as a way to test that CI reports a consequent SpotBugs error.

## State and Persistence Behavior
The file persists static-analysis policy, not application state. It influences CI and local analysis outcomes.

## Dependencies and Integration Points
It integrates with the Java build's SpotBugs configuration. The exclusions reflect JNI and wrapper patterns where private methods are invoked from native code or arrays are intentionally exposed for performance/API compatibility.

## Risks and Edge Cases
Broad suppressions, especially class-level or pattern-only matches, can hide real defects. The header comments say the baseline should be justified or removed, indicating technical debt. Duplicate `BackupEngineOptions` entries suggest the file may need cleanup.

## Test Signals
Static-analysis tests should confirm that removing the documented test exclusion produces a SpotBugs error. Maintenance should review whether each exposed-representation suppression is still required and whether JNI callback private methods are better annotated or configured.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/spotbugs-exclude.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractCompactionFilter.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractCompactionFilter.java

## Purpose
This Java base class represents a compaction filter backed by a native C++ implementation. It lets Java API users hold and dispose a native filter while exposing compaction context metadata.

## Important APIs, Types, and Functions
`AbstractCompactionFilter<T extends AbstractSlice<?>>` extends `RocksObject`. Its nested `Context` class stores `fullCompaction` and `manualCompaction` booleans with accessors `isFullCompaction` and `isManualCompaction`. The protected constructor accepts a native handle. `disposeInternal(long handle)` is a final native method.

## Control Flow
Subclasses are constructed with native handles produced elsewhere, often through a factory callback. Java calls close/dispose through `RocksObject`, which invokes the final native dispose method for the handle.

## State and Persistence Behavior
The class stores native object ownership through `RocksObject.nativeHandle_`. Disposal deletes the underlying C++ compaction filter pointer. The context object is immutable and describes one compaction invocation. Filtering can affect persistent DB contents during compaction, but this base class does not implement filtering logic itself.

## Dependencies and Integration Points
It integrates with compaction filter factories, native compaction filter callback bridges, `AbstractSlice` implementations, and RocksDB options that accept compaction filters.

## Risks and Edge Cases
The documentation warns that disposing while any RocksDB instance still references the filter causes undefined behavior. Because the native dispose method is final, subclasses cannot customize cleanup. Generic type `T` documents slice type but this file does not enforce callback behavior.

## Test Signals
Tests should verify context flag accessors, disposal after DB close, and that premature disposal is avoided by option/DB lifecycle tests. Factory-driven tests should confirm filters are disowned when C++ takes ownership.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractCompactionFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractCompactionFilterFactory.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractCompactionFilterFactory.java

## Purpose
This Java base class lets users implement compaction filter factories in Java while native RocksDB requests new filter instances for individual compactions.

## Important APIs, Types, and Functions
`AbstractCompactionFilterFactory<T extends AbstractCompactionFilter<?>>` extends `RocksCallbackObject`. It has a public constructor, `initializeNative`, private JNI-called `createCompactionFilter(boolean fullCompaction, boolean manualCompaction)`, abstract `createCompactionFilter(Context)`, abstract `name`, custom `disposeInternal`, and native methods `createNewCompactionFilterFactory0` and static `disposeInternal(long)`.

## Control Flow
Construction starts with a zero native handle and initialization creates the native factory callback. When C++ needs a filter, JNI calls the private `createCompactionFilter` method, which builds a `Context`, calls the user's abstract factory method, disowns the returned filter's native handle because C++ takes ownership through `unique_ptr`, and returns the native handle.

## State and Persistence Behavior
The factory owns a native callback wrapper, while individual filters are transferred to C++ ownership. Compaction filters created by the factory can affect persistent key/value retention or modification during compaction, but the factory itself stores no persistent data.

## Dependencies and Integration Points
It integrates with `RocksCallbackObject`, `AbstractCompactionFilter`, native `compaction_filter_factory_jnicallback.cc`, and options APIs that configure compaction filters.

## Risks and Edge Cases
The private JNI method suppresses close-resource warnings because ownership transfer is deliberate. If a user returns null or an invalid filter, native code may fail. The class-level SpotBugs exclusion in this subset includes this class, suggesting known static-analysis complexity around resource ownership.

## Test Signals
Tests should verify Java factory invocation, context flag propagation, name callback, native ownership transfer via `disOwnNativeHandle`, and disposal of the factory shared pointer after DB shutdown.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractCompactionFilterFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractComparator.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractComparator.java

## Purpose
This Java abstract base class lets users implement RocksDB key comparators in Java. It keeps the public comparator API focused while native callback plumbing is handled by other bridge classes.

## Important APIs, Types, and Functions
The class extends `RocksCallbackObject`. It provides constructors, `initializeNative`, package-private `getComparatorType`, abstract `name`, abstract `compare(ByteBuffer a, ByteBuffer b)`, optional `findShortestSeparator`, optional `findShortSuccessor`, `usingDirectBuffers`, and native methods `usingDirectBuffers(long)` and `createNewComparator(long)`.

## Control Flow
Subclasses define a total order in `compare` and optionally shorten separator/successor keys by mutating byte buffer position/limit semantics. Initialization creates a native comparator wrapper using `ComparatorOptions`. Native code calls through `AbstractComparatorJniBridge` for callback dispatch.

## State and Persistence Behavior
The comparator's native handle is callback state. Comparator behavior affects persistent SST ordering and DB compatibility. The `name` contract is critical because RocksDB uses it to detect comparator mismatch when reopening DBs.

## Dependencies and Integration Points
It integrates with `ComparatorOptions`, `ComparatorType`, `RocksCallbackObject`, `AbstractComparatorJniBridge`, and native comparator callback code. `WriteBatchWithIndex` can also accept Java comparator handles for fallback index comparison.

## Risks and Edge Cases
A comparator must define a stable total order; changing comparator semantics without changing `name` can corrupt or make existing DBs unreadable. ByteBuffer mutation is allowed only within documented bounds. Direct-buffer support depends on native wrapper configuration. The package-private default constructor restricts uncontrolled use.

## Test Signals
Tests should cover comparator ordering, DB reopen mismatch detection through names, separator/successor mutation behavior, direct versus indirect buffer configuration, and integration with `WriteBatchWithIndex` fallback comparators.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractComparatorJniBridge.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractComparatorJniBridge.java

## Purpose
This package-private bridge class contains private static methods invoked from JNI to call Java `AbstractComparator` methods while preserving public API cleanliness and ByteBuffer bounds.

## Important APIs, Types, and Functions
Private JNI-called methods are `compareInternal`, `findShortestSeparatorInternal`, and `findShortSuccessorInternal`. They accept an `AbstractComparator`, one or two `ByteBuffer`s, and native-provided lengths.

## Control Flow
`compareInternal` marks and limits each buffer when a length is provided, calls `comparator.compare`, resets marked buffers, and returns the comparison result. Separator/successor methods set buffer limits, call the corresponding comparator method, and return the remaining byte count, which native code interprets as the new key length.

## State and Persistence Behavior
The bridge mutates ByteBuffer position/limit state temporarily or intentionally for key shortening. It does not persist data, but comparator decisions affect RocksDB ordering and persisted SST structure.

## Dependencies and Integration Points
It is used by native comparator JNI callback code and interacts with `AbstractComparator`. SpotBugs/PMD suppressions are necessary because methods are private and only invoked by native code.

## Risks and Edge Cases
`compareInternal` uses `mark`/`reset` only when length is provided; comparator implementations that modify position can affect reset semantics if they alter marks unexpectedly. Separator/successor methods do not restore limits because the remaining length is the output contract. Invalid native lengths can cause `IllegalArgumentException` from ByteBuffer limit changes.

## Test Signals
Tests should call comparators through native RocksDB paths and verify correct bounds, no buffer aliasing between inputs, separator/successor output length handling, and exception propagation for invalid comparator behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractComparatorJniBridge.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractEventListener.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractEventListener.java

## Purpose
This base class lets Java code implement RocksDB event listeners. It provides no-op implementations for all listener callbacks, optional callback selection, and private JNI proxy methods that wrap native DB handles into Java objects without transferring ownership.

## Important APIs, Types, and Functions
`AbstractEventListener` extends `RocksCallbackObject` and implements `EventListener`. The nested `EnabledEventCallback` enum maps callback names to byte values and supports `fromValue`. Constructors either enable all callbacks or pack selected callbacks into a bitmask. It implements no-op listener methods for flush, compaction, table file, memtable, column-family handle deletion, external ingestion, background error, stall, file IO, error recovery, and recovery completion. Proxy methods include `onFlushCompletedProxy`, `onFlushBeginProxy`, `onCompactionBeginProxy`, `onCompactionCompletedProxy`, `onExternalFileIngestedProxy`, `onBackgroundErrorProxy`, and `onErrorRecoveryBeginProxy`. Native methods create and dispose the native listener.

## Control Flow
Construction packs selected enum values into a long bitmask and passes it through `RocksCallbackObject` initialization. Native code invokes private proxy methods for callbacks needing a temporary `RocksDB` wrapper or enum conversion. Proxies create wrappers from native DB handles, call `disOwnNativeHandle` to avoid deleting non-owned DBs, and dispatch to overridable public methods. Default public implementations are no-ops or return conservative defaults.

## State and Persistence Behavior
The listener stores native callback state through `RocksCallbackObject`. It does not persist data directly, but callbacks observe and can respond to persistence-related events such as flush, compaction, file IO, background errors, and recovery. Error recovery callbacks can influence continuation by returning a boolean.

## Dependencies and Integration Points
It integrates with `EventListener`, `RocksDB`, many event info DTOs, `BackgroundErrorReason`, `Status`, and native event listener callback code. The enablement bitmask allows native code to avoid calling unneeded Java callbacks.

## Risks and Edge Cases
Enum byte values are part of the native contract and must stay synchronized with C++ callback dispatch. The default constructor enables all callbacks, which may be expensive; the selective constructor is preferred for performance. Temporary DB wrappers must always disown native handles to avoid double-free. Callback exceptions and threading behavior are handled in native code outside this file.

## Test Signals
Tests should verify bitmask packing for selected callbacks, `fromValue` validation, dispatch for each proxy and no-op method, handle disowning, background/error recovery enum conversion, and disposal of the native listener.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractEventListener.java -->
