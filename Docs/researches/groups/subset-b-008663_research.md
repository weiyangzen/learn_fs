# subset-b-008663 Research

Grouped research for RocksDB Java transaction, WAL, write batch, utility, backup, blob, table config, comparator, and ByteBuffer regression files. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionDBOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionDBOptions.java

## Purpose
`TransactionDBOptions` is the Java JNI wrapper for native transaction database configuration. It extends `RocksObject`, owns a native `TransactionDBOptions` handle, and exposes lock-table and write-policy settings used when opening/configuring `TransactionDB`.

## Important APIs and Types
The public API is a fluent getter/setter surface: `get/setMaxNumLocks`, `get/setNumStripes`, `get/setTransactionLockTimeout`, `get/setDefaultLockTimeout`, and `get/setWritePolicy`. `setWritePolicy` maps `TxnDBWritePolicy` enum values to native bytes, while `getWritePolicy` maps the native byte back through `TxnDBWritePolicy.getTxnDBWritePolicy`.

## Control Flow, State, and Persistence
Construction calls `newTransactionDBOptions()` and stores the returned native pointer. Every accessor asserts `isOwningHandle()` before dispatching to JNI. The Java object itself persists no option values; all state lives in the native handle until `disposeInternal` calls `disposeInternalJni`. Lock timeout semantics are important: zero means no wait, negative can mean no timeout or fallback depending on setting, and comments warn about deadlocks when no timeout is used.

## Dependencies and Integration Points
This class depends on `RocksObject`, `TxnDBWritePolicy`, `TransactionOptions`, and native JNI implementations. It integrates with transaction DB open paths and external direct writes through default lock timeout behavior. The commented custom mutex factory block indicates unsupported or deferred Java binding for native transaction mutex customization.

## Risks and Test Signals
Risks concentrate around native lifetime, assertion-only disposed-handle checks, and invalid enum byte values from JNI producing `IllegalArgumentException`. Deadlock risk is explicitly documented for negative lock timeouts. In this subset, `AbstractTransactionTest` exercises transaction behavior broadly but does not directly validate these option getters/setters; coverage likely lives in transaction-specific tests outside this item.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionDBOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionLogIterator.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionLogIterator.java

## Purpose
`TransactionLogIterator` iterates over RocksDB transaction log batches exposed from the native WAL/transaction log reader. It stops at sequence gaps and returns sequence-numbered `WriteBatch` objects.

## Important APIs and Types
The iterator API includes `isValid()`, `next()`, `status()`, and `getBatch()`. `BatchResult` is a value holder containing a `long sequenceNumber` and a `WriteBatch` constructed from a native handle with ownership enabled.

## Control Flow, State, and Persistence
The iterator wraps a native handle supplied by package-private construction. `getBatch()` asserts validity, calls native `getBatch`, and returns Java objects backed by native batch state. `BatchResult.writeBatch()` exposes the batch object to callers, making resource ownership important. `status()` surfaces native failures as `RocksDBException`.

## Dependencies and Integration Points
The class depends on `RocksObject`, `WriteBatch`, and native WAL iteration JNI. It is normally obtained from DB APIs that expose updates since a sequence number. It integrates with replication, backup, and recovery code that consumes WAL batches.

## Risks and Test Signals
Caller misuse is possible if `getBatch()` is called after invalidation or before checking `status()`. The nested `WriteBatch` owns the native handle and must be closed. This subset contains backup and WAL-related enums but no direct transaction log iterator test; risk is therefore in native binding and lifecycle behavior not visible in Java-only assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionLogIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionOptions.java

## Purpose
`TransactionOptions` wraps native per-transaction options and implements the shared `TransactionalOptions<TransactionOptions>` contract. It configures snapshot creation, deadlock detection, lock timeout, expiration, deadlock traversal depth, and maximum write batch size.

## Important APIs and Types
Key methods include `isSetSnapshot/setSetSnapshot`, `isDeadlockDetect/setDeadlockDetect`, `get/setLockTimeout`, `get/setExpiration`, `get/setDeadlockDetectDepth`, and `get/setMaxWriteBatchSize`. Fluent setters return `this`.

## Control Flow, State, and Persistence
Construction initializes native state through `newTransactionOptions()`. Most methods assert ownership before native access, though the later deadlock-depth and write-batch-size methods do not assert explicitly. Java persists no local copies; the native handle owns all option state. Expiration and lock timeout settings affect transaction lock retention and commit validity.

## Dependencies and Integration Points
The class depends on `RocksObject`, `TransactionalOptions`, `Transaction`, `TransactionDBOptions`, and JNI. It is consumed by `TransactionalDB.beginTransaction(WriteOptions, T)` implementations, including regular and optimistic transactions.

## Risks and Test Signals
Important risks are deadlocks when lock timeouts are unbounded, forgotten transactions retaining locks when expiration is unset, and disposed-handle misuse. `AbstractTransactionTest` covers snapshot setting, transaction begin, commit/rollback, lock timeout mutation via `Transaction.setLockTimeout`, and write option behavior, but not every `TransactionOptions` property directly.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionalDB.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionalDB.java

## Purpose
`TransactionalDB` is a package-private generic interface for DB wrappers that can begin transactions. It unifies `TransactionDB` and optimistic transaction DB implementations behind a common Java test and usage contract.

## Important APIs and Types
It defines four `beginTransaction` overloads: with only `WriteOptions`, with transaction options, with an old `Transaction` for reuse, and with both transaction options and transaction reuse. The generic bound `T extends TransactionalOptions<T>` lets implementations accept either regular or optimistic transaction options.

## Control Flow, State, and Persistence
This file has no implementation state. Its control-flow role is contract enforcement: implementations allocate or reinitialize a `Transaction` and callers must close returned transaction objects.

## Dependencies and Integration Points
It depends on `AutoCloseable`, `WriteOptions`, `Transaction`, and `TransactionalOptions`. `AbstractTransactionTest.DBContainer` mirrors this contract at test level, allowing shared tests across transaction implementations.

## Risks and Test Signals
The principal risk is lifecycle ownership: callers must close transactions, and reuse overloads must safely reinitialize old native transaction handles. `AbstractTransactionTest` exercises begin/close patterns through try-with-resources, but reuse overload behavior is not covered in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionalDB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionalOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionalOptions.java

## Purpose
`TransactionalOptions` is the small package-private interface shared by transaction option types. It captures snapshot-on-begin behavior while preserving fluent subtype returns.

## Important APIs and Types
The API has `isSetSnapshot()` and `setSetSnapshot(boolean)`. The generic self type `T extends TransactionalOptions<T>` lets setters return the concrete option type.

## Control Flow, State, and Persistence
There is no implementation or storage in this file. Implementors map the setting to native option state. Semantically, `setSetSnapshot(true)` is equivalent to calling `Transaction.setSnapshot()` after the transaction starts.

## Dependencies and Integration Points
It references `Transaction` in documentation and is used by `TransactionalDB<T>`, `TransactionOptions`, and likely optimistic transaction option classes.

## Risks and Test Signals
Risk is mainly semantic consistency across all implementors: snapshot timing must match `Transaction.setSnapshot()`. `AbstractTransactionTest` validates `setSnapshot`, `setSnapshotOnNextOperation`, `getSnapshot`, and `clearSnapshot` on transactions, providing indirect expectations for options that enable snapshots.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionalOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TtlDB.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TtlDB.java

## Purpose
`TtlDB` is the Java wrapper for RocksDB databases opened with time-to-live semantics. It extends `RocksDB` and ensures values are interpreted with internal timestamp suffixes so expired entries can be removed during compaction.

## Important APIs and Types
Static `open` overloads support default-column-family TTL and multi-column-family TTL lists. `createColumnFamilyWithTtl` creates TTL-enabled column families. `closeE()` closes with exception reporting, while `close()` closes owned column-family handles and suppresses close errors.

## Control Flow, State, and Persistence
The single-CF `open` calls native `open`, stores the options object, and stores the default column-family handle. The multi-CF `open` validates `columnFamilyDescriptors.size() == ttlValues.size()`, extracts names and option handles, requires the default column family, converts boxed TTLs to `int[]`, calls `openCF`, wraps returned handles, records owned handles, and stores the default handle by descriptor index. TTL state is persisted in values by native code via timestamp suffixing; expired entries are removed only during compaction, and read-only opens do not compact.

## Dependencies and Integration Points
Dependencies include `Options`, `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `RocksDB.DEFAULT_COLUMN_FAMILY`, native `open/openCF/createColumnFamilyWithTtl/closeDatabase`, and inherited RocksDB handle management.

## Risks and Test Signals
Opening a TTL DB later through plain `RocksDB.open` can expose timestamp-suffixed values and disable TTL behavior. A small positive TTL can remove most data quickly, and expired values may remain visible until compaction. The Java code also assumes `columnFamilyHandles.get(defaultColumnFamilyIndex)` exists after wrapping native handles. This subset has no direct `TtlDB` test; coverage is mostly contract documentation and native integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TtlDB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TxnDBWritePolicy.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TxnDBWritePolicy.java

## Purpose
`TxnDBWritePolicy` enumerates when transactional writes become visible in the underlying DB relative to commit/prepare phases.

## Important APIs and Types
Values are `WRITE_COMMITTED`, `WRITE_PREPARED`, and `WRITE_UNPREPARED`, each backed by a byte. `getValue()` exposes the JNI representation and `getTxnDBWritePolicy(byte)` maps native bytes back to enum values.

## Control Flow, State, and Persistence
The enum has immutable byte state. Conversion scans all values and throws `IllegalArgumentException` for unknown bytes. Persistence behavior is semantic rather than local: selected write policy determines whether only committed data, prepared data, or unprepared data can be written into DB storage.

## Dependencies and Integration Points
Used by `TransactionDBOptions.getWritePolicy/setWritePolicy` and native transaction DB configuration. It must remain byte-compatible with RocksDB C++ enum values.

## Risks and Test Signals
The main risk is byte drift between Java and native constants, which would misconfigure transaction durability/visibility. Unknown native bytes fail fast. This subset does not include direct tests for enum conversion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TxnDBWritePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/UInt64AddOperator.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/UInt64AddOperator.java

## Purpose
`UInt64AddOperator` is a Java wrapper for RocksDB's unsigned 64-bit additive merge operator. It lets users configure merge semantics that accumulate integer values.

## Important APIs and Types
The only public API is the constructor, which calls `newSharedUInt64AddOperator()` and passes the native handle to `MergeOperator`. Disposal delegates to `disposeInternalJni`.

## Control Flow, State, and Persistence
All merge behavior is native. The Java object owns a native shared merge operator handle and releases it on disposal. Persistent effects occur when configured on DB/column family options and used by merge writes.

## Dependencies and Integration Points
Depends on `MergeOperator` and JNI. It integrates with `Options`/`ColumnFamilyOptions` merge operator configuration and write paths such as `WriteBatch.merge` and `Transaction.merge`.

## Risks and Test Signals
Risks include native handle lifetime and correct encoding of unsigned 64-bit values by callers. `AbstractTransactionTest` exercises merge behavior through other configured string append operators, not this specific operator.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/UInt64AddOperator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/VectorMemTableConfig.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/VectorMemTableConfig.java

## Purpose
`VectorMemTableConfig` configures RocksDB's vector memtable representation from Java. It extends `MemTableConfig` and supplies a native memtable factory handle.

## Important APIs and Types
`DEFAULT_RESERVED_SIZE` is zero. `setReservedSize(int)` stores the initial vector capacity and returns `this`; `reservedSize()` returns it. `newMemTableFactoryHandle()` passes the size to native code.

## Control Flow, State, and Persistence
Unlike many wrapper files, this class keeps Java state in `reservedSize_` until a native factory is requested. Native creation can throw `IllegalArgumentException`. Once the factory is installed in options, memtable behavior is native and affects in-memory write buffering, not directly persistent file format.

## Dependencies and Integration Points
It depends on `MemTableConfig` and native `newMemTableFactoryHandle`. It integrates with options APIs that accept memtable config objects.

## Risks and Test Signals
Invalid or extreme reserved sizes can produce native argument errors or memory pressure. There are no direct tests for vector memtables in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/VectorMemTableConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WALRecoveryMode.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WALRecoveryMode.java

## Purpose
`WALRecoveryMode` models RocksDB write-ahead-log recovery strictness. It controls how recovery handles corrupted or incomplete WAL records.

## Important APIs and Types
Values are `TolerateCorruptedTailRecords`, `AbsoluteConsistency`, `PointInTimeRecovery`, and `SkipAnyCorruptedRecords`, each with a native byte. `getValue()` and `getWALRecoveryMode(byte)` perform JNI conversion.

## Control Flow, State, and Persistence
The enum is immutable. Recovery behavior is external: choices range from legacy tolerance of trailing incomplete records to strict clean-shutdown recovery, point-in-time stop on inconsistency, or salvage mode that skips corruption.

## Dependencies and Integration Points
This enum is consumed by DB option bindings that configure WAL recovery. It must remain aligned with native constants and persisted WAL semantics.

## Risks and Test Signals
Misconfiguration changes durability and data-loss tradeoffs. Unknown native bytes throw `IllegalArgumentException`. Backup tests in this subset rely on WAL-backed DB behavior, but they do not exercise explicit recovery modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WALRecoveryMode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WBWIRocksIterator.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WBWIRocksIterator.java

## Purpose
`WBWIRocksIterator` iterates over entries in a `WriteBatchWithIndex`. It adapts native indexed write-batch iteration to the shared `AbstractRocksIterator` API and exposes entry type, key, and optional value.

## Important APIs and Types
The central API is `entry()`, which returns a reusable `WriteEntry`. `WriteType` maps native operation ids for put, merge, delete, single delete, delete range, log, and XID. `WriteEntry` exposes `getType`, `getKey`, `getValue`, `equals`, `hashCode`, and `close`.

## Control Flow, State, and Persistence
`entry()` calls native `entry1`, interprets the returned pointer array as type/key/value, and resets two `DirectSlice` wrappers. The returned `WriteEntry` is only valid until iterator repositioning and is not thread-safe because fields are updated non-atomically. All movement, seeking, status, and refresh operations delegate to JNI methods required by `AbstractRocksIterator`. `close()` releases the reusable entry slices before closing the iterator.

## Dependencies and Integration Points
Depends on `AbstractRocksIterator<WriteBatchWithIndex>`, `DirectSlice`, `ByteBuffer`, and native iterator methods. It is created by `WriteBatchWithIndex.newIterator` and can be used to inspect uncommitted batch contents.

## Risks and Test Signals
Risks include stale slices after movement, null value for delete/log entries, non-thread-safe reuse, and enum id drift. `WriteEntry.hashCode` relies on key string representation and may not fit exotic comparators. This subset has indirect transaction write-batch inspection via `AbstractTransactionTest.getWriteBatch`, but no direct `WBWIRocksIterator` assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WBWIRocksIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WalFileType.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WalFileType.java

## Purpose
`WalFileType` describes whether a WAL file is archived or live. It is a small JNI-facing enum used when exposing WAL file metadata.

## Important APIs and Types
Values are `kArchivedLogFile` and `kAliveLogFile`. Package-private `getValue()` returns the native byte and `fromValue(byte)` converts bytes to enum constants.

## Control Flow, State, and Persistence
There is no runtime control flow beyond conversion. The enum describes persistent WAL file location/lifecycle: live logs are in the DB directory, while archived logs are retained under archive cleanup policies.

## Dependencies and Integration Points
It integrates with WAL file metadata APIs elsewhere in the RocksDB Java binding and must match native constants.

## Risks and Test Signals
Unknown byte values fail with `IllegalArgumentException`. This subset has no direct WAL file metadata tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WalFileType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WalFilter.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WalFilter.java

## Purpose
`WalFilter` is a Java callback interface allowing applications to inspect or alter WAL replay during recovery.

## Important APIs and Types
`columnFamilyLogNumberMap` receives column-family id/log-number and name/id mappings. `logRecordFound` receives the current log number, file name, original `WriteBatch`, and mutable `newBatch`, returning `LogRecordFoundResult`. `name()` returns a diagnostic filter name. `LogRecordFoundResult` carries a `WalProcessingOption` and a `batchChanged` flag, with `CONTINUE_UNCHANGED` as a shared default.

## Control Flow, State, and Persistence
Native recovery calls into Java for mappings and each log record. The callback can continue, ignore a record, stop replay, mark corruption, or populate a replacement batch. If `batchChanged` is false, `newBatch` is ignored. The replacement batch must not contain more records than the original, or recovery fails.

## Dependencies and Integration Points
Depends on `Map`, `WriteBatch`, and `WalProcessingOption`. It integrates with RocksDB recovery and JNI callback plumbing.

## Risks and Test Signals
WAL filters are high-risk because incorrect return options or oversized replacement batches can discard logs or fail recovery. Callback exceptions and Java/native lifetime of batches are also sensitive. No direct WAL filter tests are included in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WalFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WalProcessingOption.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WalProcessingOption.java

## Purpose
`WalProcessingOption` enumerates possible recovery actions returned by a `WalFilter`.

## Important APIs and Types
Values are `CONTINUE_PROCESSING`, `IGNORE_CURRENT_RECORD`, `STOP_REPLAY`, and `CORRUPTED_RECORD`, each with a native byte. Package-private `getValue()` and public `fromValue(byte)` bridge JNI.

## Control Flow, State, and Persistence
The enum itself is immutable. In recovery, these values decide whether WAL replay proceeds, skips a record, discards logs from the current point onward, or treats the record as corrupt.

## Dependencies and Integration Points
Used by `WalFilter.LogRecordFoundResult` and native recovery callbacks. Constants must stay byte-aligned with RocksDB C++.

## Risks and Test Signals
`STOP_REPLAY` has destructive recovery semantics because subsequent logs are discarded. Unknown byte conversion fails fast. This subset includes no direct test for these options.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WalProcessingOption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBatch.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBatch.java

## Purpose
`WriteBatch` is the Java wrapper for an atomic ordered collection of RocksDB updates. It extends `AbstractWriteBatch` and adds serialization, iteration, WAL termination, operation flags, and callback support.

## Important APIs and Types
Constructors create empty, reserved-size, serialized, or native-backed batches. Public methods include `iterate(Handler)`, `data()`, `getDataSize()`, `hasPut/hasDelete/hasSingleDelete/hasDeleteRange/hasMerge/hasBeginPrepare/hasEndPrepare/hasCommit/hasRollback`, `markWalTerminationPoint()`, and `getWalTerminationPoint()`. `Handler` is a JNI callback object with abstract callbacks for puts, merges, deletes, range deletes, log data, blob indexes, and 2PC markers. `SavePoint` records batch size, count, and content flags.

## Control Flow, State, and Persistence
Mutation methods required by `AbstractWriteBatch` delegate to native put/merge/delete/single-delete/delete-range/log/savepoint functions. Native state stores ordered operations and serialized bytes. The constructor from native handle may disown the handle when C++ manages lifetime; `BatchResult` uses the owning variant. `data()` returns serialized state that can reconstruct another `WriteBatch`.

## Dependencies and Integration Points
Depends on `AbstractWriteBatch`, `RocksCallbackObject`, `ColumnFamilyHandle`, `ByteBuffer`, and JNI. It integrates with `RocksDB.write`, transactions, WAL iteration, backups, and `WriteBatchWithIndex.getWriteBatch`.

## Risks and Test Signals
Thread safety is limited: const methods can be concurrent, mutations require external synchronization. Native handle ownership differs by constructor. Single-delete semantics are constrained by RocksDB rules. `AbstractTransactionTest.rebuildFromWriteBatch` and `getCommitTimeWriteBatch` exercise transaction integration, while backup and ByteBuffer tests use write batches indirectly and directly.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBatch.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBatchInterface.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBatchInterface.java

## Purpose
`WriteBatchInterface` defines the common mutation contract for `WriteBatch`, `WriteBatchWithIndex`, and transaction-like batch wrappers.

## Important APIs and Types
The interface covers `count`, byte-array and `ByteBuffer` `put`, column-family variants, `merge`, `delete`, experimental `singleDelete`, `deleteRange`, `putLogData`, `clear`, savepoint operations, `setMaxBytes`, and `getWriteBatch`.

## Control Flow, State, and Persistence
This file has no implementation state. It defines operation ordering and persistence semantics for implementors: writes are staged in a batch, log data is WAL-only and does not consume sequence numbers, savepoints can roll back staged entries, and `getWriteBatch` exposes the underlying batch for DB writes.

## Dependencies and Integration Points
Depends on `ByteBuffer`, `ColumnFamilyHandle`, `RocksDBException`, `Status`, `Experimental`, and `WriteBatch`. It is the shared API implemented by abstract/native batch classes and used by higher-level transaction code.

## Risks and Test Signals
The contract documents undefined behavior for misuse of `singleDelete`; direct buffer methods require buffers whose position/limit define key/value slices. `AbstractTransactionTest` heavily exercises batch-like operations through transactions, including byte arrays, parts arrays, direct and heap `ByteBuffer`, column families, savepoints, and log data.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBatchInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBatchWithIndex.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBatchWithIndex.java

## Purpose
`WriteBatchWithIndex` augments `WriteBatch` semantics with a searchable key index and read-your-own-writes functionality. It extends `AbstractWriteBatch`.

## Important APIs and Types
Constructors allow default bytewise comparison, configurable duplicate-key overwrite, and custom fallback comparator/reserved bytes. APIs include `newIterator`, `newIteratorWithBase`, `getFromBatch`, `getFromBatchAndDB`, and `getWriteBatch`.

## Control Flow, State, and Persistence
Mutations delegate to native functions that both append to the underlying write batch and update the index. Iterators over batch state return `WBWIRocksIterator`; iterators with a base DB iterator create a merged `RocksIterator` and disown the base iterator because native code takes ownership. `getFromBatch` reads only staged writes and may fail with merge-in-progress if merges cannot be resolved; `getFromBatchAndDB` combines batch and DB state using the DB merge operator.

## Dependencies and Integration Points
Depends on `AbstractWriteBatch`, `AbstractComparator`, `ColumnFamilyHandle`, `RocksIterator`, `ReadOptions`, `DBOptions`, `RocksDB`, `WBWIRocksIterator`, `ByteBuffer`, and JNI. Transactions expose their internal indexed batch through `Transaction.getWriteBatch()`.

## Risks and Test Signals
Updating a batch while using an iterator on the current key can invalidate key/value memory. Delete range is explicitly marked unsupported in `WriteBatchWithIndex` despite native methods existing. Base iterator ownership transfer can surprise callers. `AbstractTransactionTest.getWriteBatch` validates non-owning transaction batch exposure and count; broader read-your-own-writes behavior is covered by transaction get/iterator tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBatchWithIndex.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBufferManager.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBufferManager.java

## Purpose
`WriteBufferManager` wraps native RocksDB write buffer memory accounting and optional stalling. It lets DB instances bound memtable memory together with a block cache.

## Important APIs and Types
Constructors accept `bufferSizeBytes`, a `Cache`, and optional `allowStall`. `allowStall()` returns the Java-cached flag.

## Control Flow, State, and Persistence
Construction ensures the RocksDB native library is loaded, then creates the native write buffer manager with the cache handle. The only Java state is `allowStall_`; memory usage is native and runtime-only. Disposal releases the native manager.

## Dependencies and Integration Points
Depends on `RocksObject`, `Cache`, `RocksDB.loadLibrary`, and JNI. It integrates with DB/table options that accept a write buffer manager and with cache-backed memory budgets.

## Risks and Test Signals
The cache handle must remain valid for native manager creation/use. `allowStall=true` changes write latency behavior under memory pressure. This subset has no direct write buffer manager tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBufferManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteOptions.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteOptions.java

## Purpose
`WriteOptions` wraps native per-write configuration controlling durability, WAL use, missing column-family handling, slowdown behavior, priority, and memtable insert hints.

## Important APIs and Types
APIs include `setSync/sync`, `setDisableWAL/disableWAL`, `setIgnoreMissingColumnFamilies/ignoreMissingColumnFamilies`, `setNoSlowdown/noSlowdown`, `setLowPri/lowPri`, and `setMemtableInsertHintPerBatch/memtableInsertHintPerBatch`. There is a default constructor, a package-private non-owning native-handle constructor, and a shallow copy constructor.

## Control Flow, State, and Persistence
Options are stored in native memory. Setters mutate the native handle and return `this`; getters read native state. `sync` controls fsync-like durability, while `disableWAL` weakens crash recovery and backup assumptions. `noSlowdown` and `lowPri` affect behavior under write stalls/compaction lag.

## Dependencies and Integration Points
Depends on `RocksObject`, `Status.Code`, `RocksDB.write`, transactions, backup engine semantics, and JNI. Transactions can expose and update write options.

## Risks and Test Signals
The copy constructor is shallow for native pointer members. Disabling WAL can lose unflushed memtable data and requires flush-before-backup safety. `AbstractTransactionTest.writeOptions` verifies a transaction receives non-owning write options, preserves `disableWAL`, and reflects updated `sync` state.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteStallCondition.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteStallCondition.java

## Purpose
`WriteStallCondition` enumerates write controller states reported to Java listeners or info objects.

## Important APIs and Types
Values are `DELAYED`, `STOPPED`, and `NORMAL`, each backed by a native byte. Package-private `getValue()` and `fromValue(byte)` bridge native values.

## Control Flow, State, and Persistence
The enum is immutable. It represents runtime write stall state, not persistent data. `fromValue` scans constants and throws on unknown bytes.

## Dependencies and Integration Points
Used by `WriteStallInfo`, likely in event listener callbacks from native RocksDB.

## Risks and Test Signals
Byte mismatch would misreport stall states. This subset has no direct write stall tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteStallCondition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteStallInfo.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteStallInfo.java

## Purpose
`WriteStallInfo` is an immutable Java data object describing a column family's write stall transition.

## Important APIs and Types
It stores `columnFamilyName`, `currentCondition`, and `previousCondition`. Getters expose each field. `equals`, `hashCode`, and `toString` support value comparisons and diagnostics.

## Control Flow, State, and Persistence
The package-private constructor is intended for JNI and tests. It converts condition bytes through `WriteStallCondition.fromValue`, so invalid native values fail during construction. The object is runtime event state only.

## Dependencies and Integration Points
Depends on `Objects` and `WriteStallCondition`. It likely integrates with RocksDB event listener callbacks for write stall changes.

## Risks and Test Signals
Risks are invalid native enum bytes and null/encoding behavior for column-family names. This subset includes no direct `WriteStallInfo` tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteStallInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/BufferUtil.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/BufferUtil.java

## Purpose
`BufferUtil` provides a compact bounds-check helper for offset/length/size validation.

## Important APIs and Types
`CheckBounds(int offset, int len, int size)` throws `IndexOutOfBoundsException` if any component is negative or if `offset + len` exceeds `size`.

## Control Flow, State, and Persistence
The method uses a bitwise aggregate check: `(offset | len | (offset + len) | (size - (offset + len))) < 0`. There is no state or persistence.

## Dependencies and Integration Points
It depends only on `String.format`/JDK exceptions and is intended for buffer-oriented JNI wrapper methods.

## Risks and Test Signals
The compact check relies on two's-complement overflow behavior; very large `offset + len` overflow is intentionally caught as negative. No direct tests for this helper are in the subset, though ByteBuffer transaction tests cover adjacent buffer behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/BufferUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/ByteUtil.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/ByteUtil.java

## Purpose
`ByteUtil` contains small byte utility methods used by Java comparators.

## Important APIs and Types
`bytes(String)` returns UTF-8 bytes. `memcmp(ByteBuffer x, ByteBuffer y, int count)` compares the first `count` bytes as unsigned values and returns a signed difference like C `memcmp`.

## Control Flow, State, and Persistence
`memcmp` loops from zero to `count - 1`, using absolute `ByteBuffer.get(idx)` and masking with `0xff`. It does not alter buffer positions and has no state.

## Dependencies and Integration Points
Depends on `ByteBuffer` and `StandardCharsets.UTF_8`. `BytewiseComparator` uses `memcmp` for lexicographic ordering.

## Risks and Test Signals
`memcmp` assumes both buffers have at least `count` accessible bytes from absolute index zero, which is consistent with comparator callbacks but can be surprising if buffers have non-zero positions. Comparator behavior is indirectly validated by `BuiltinComparatorTest` for native comparators; Java comparator coverage is adjacent through `ByteBufferUnsupportedOperationTest` using `ReverseBytewiseComparator`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/ByteUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/BytewiseComparator.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/BytewiseComparator.java

## Purpose
`BytewiseComparator` is a Java implementation of RocksDB's bytewise comparator. It exists mainly for benchmarking or specialized Java comparator use because JNI callback overhead is slower than built-in native comparators.

## Important APIs and Types
It extends `AbstractComparator`, implements `name()`, `compare(ByteBuffer, ByteBuffer)`, static `_compare`, `findShortestSeparator`, and `findShortSuccessor`.

## Control Flow, State, and Persistence
Comparison uses unsigned byte lexicographic order and falls back to length. Separator shortening finds the first differing byte, increments where safe, and truncates the `start` buffer by setting its limit. If incrementing would cross the limit, it searches for a later non-`0xff` byte. Short successor increments the first non-`0xff` byte and truncates. There is no persistent state beyond inherited native comparator registration.

## Dependencies and Integration Points
Depends on `AbstractComparator`, `ComparatorOptions`, `ByteBuffer`, `Slice` docs, and `ByteUtil.memcmp`. It integrates with options/table configuration when a Java comparator is installed.

## Risks and Test Signals
The methods mutate buffer limits and bytes, so caller-provided buffers must be writable. Absolute indexing with `remaining()` assumes callback buffers are presented from relevant zero-based slices. Built-in comparator tests cover native bytewise ordering; this Java implementation is indirectly related but not directly asserted here.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/BytewiseComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/Environment.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/Environment.java

## Purpose
`Environment` detects OS, architecture, libc variant, and constructs RocksDB JNI library names and filenames.

## Important APIs and Types
OS/arch helpers include `isAarch64`, `isPowerPC`, `isS390x`, `isRiscv64`, `isWindows`, `isFreeBSD`, `isMac`, `isAix`, `isUnix`, `isSolaris`, `isOpenBSD`, and `is64Bit`. Library helpers include `getSharedLibraryName/FileName`, `getLibcName`, `getJniLibraryName/FileName`, fallback JNI name/file, and `getJniLibraryExtension`.

## Control Flow, State, and Persistence
Static fields cache lowercased `os.name`, `os.arch`, and `ROCKSDB_MUSL_LIBC`. Musl detection is lazy to avoid suspicious Windows IO. Detection first honors explicit env var, then runs `ldd /usr/bin/env | grep -q musl`, then scans `/lib` for architecture-specific or prefix-matching musl files. The only mutable state is cached `MUSL_LIBC`.

## Dependencies and Integration Points
Depends on `File`, `IOException`, `Locale`, and `ProcessBuilder`. It integrates with `RocksDB.loadLibrary` and native resource extraction/loading.

## Risks and Test Signals
Risks include process execution on constrained systems, interrupted waits swallowing interruption, incomplete OS detection, and cached static values making tests order-sensitive. No direct `Environment` test is in this subset, but all native tests depend on correct library loading through `RocksNativeLibraryResource`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/Environment.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/IntComparator.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/IntComparator.java

## Purpose
`IntComparator` is a Java comparator for four-byte integer keys in ascending numeric order.

## Important APIs and Types
It extends `AbstractComparator`, implements `name()` and `compare(ByteBuffer, ByteBuffer)`, and uses private `compareIntKeys`.

## Control Flow, State, and Persistence
`compareIntKeys` reads one `int` from each buffer using relative `getInt()`, computes the difference as `long`, and clamps the result into `int` range to avoid overflow. It has no persistent state beyond inherited comparator registration.

## Dependencies and Integration Points
Depends on `AbstractComparator`, `ComparatorOptions`, and `ByteBuffer`. It can be installed on RocksDB options for integer-key databases.

## Risks and Test Signals
Keys must contain at least four bytes, and relative `getInt()` advances buffer positions. Incorrect key sizes will fail at runtime. This subset includes no direct tests for `IntComparator`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/IntComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/ReverseBytewiseComparator.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/ReverseBytewiseComparator.java

## Purpose
`ReverseBytewiseComparator` is the Java implementation of reverse bytewise ordering. It is mainly useful for testing or benchmarking because the native built-in comparator is preferred for performance.

## Important APIs and Types
It extends `AbstractComparator`, implements `name()`, `compare`, and `findShortestSeparator`. `compare` negates `BytewiseComparator._compare`.

## Control Flow, State, and Persistence
Separator shortening finds the first differing byte. For reverse order, when the start byte is greater than the limit byte and there are trailing bytes, it truncates `start` after the differing byte while preserving reverse-order invariants. It does not implement some prefix cases. There is no local persistent state.

## Dependencies and Integration Points
Depends on `AbstractComparator`, `BuiltinComparator`, `ComparatorOptions`, `Slice` docs, `ByteBuffer`, and `BytewiseComparator`. `ByteBufferUnsupportedOperationTest` installs it on a column family.

## Risks and Test Signals
Comparator callbacks mutate buffers and are slower than native comparators. Unsupported prefix shortening cases may reduce optimization but should preserve correctness. `ByteBufferUnsupportedOperationTest` stress-tests writes and iteration with this comparator, guarding against a previously intermittent unsupported operation failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/ReverseBytewiseComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/SizeUnit.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/SizeUnit.java

## Purpose
`SizeUnit` defines binary size constants for Java code that configures RocksDB sizes.

## Important APIs and Types
Constants are `KB`, `MB`, `GB`, `TB`, and `PB`, each computed as powers of 1024. The private constructor prevents instantiation.

## Control Flow, State, and Persistence
There is no control flow or mutable state. Constants are compile-time/runtime Java values and do not persist any RocksDB state.

## Dependencies and Integration Points
No external dependencies. Tests and option code can use these constants for readability.

## Risks and Test Signals
The constants use `long` and remain within range through `PB`. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/SizeUnit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/StdErrLogger.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/StdErrLogger.java

## Purpose
`StdErrLogger` is a native-backed logger implementation that redirects RocksDB log messages to standard error.

## Important APIs and Types
Constructors accept `InfoLogLevel` and optional prefix. It implements `LoggerInterface` methods `setInfoLogLevel`, `infoLogLevel`, and `getLoggerType`, returning `LoggerType.STDERR_IMPLEMENTATION`.

## Control Flow, State, and Persistence
Construction creates a native stderr logger with log level and prefix. Level changes and reads dispatch to JNI. Disposal is native. Logging output goes to process stderr rather than DB log files.

## Dependencies and Integration Points
Depends on `InfoLogLevel`, `LoggerInterface`, `LoggerType`, `RocksObject`, and JNI. It integrates with DB/backup/options APIs that accept RocksDB loggers.

## Risks and Test Signals
Risks include native handle lifetime, stderr noise in embedded applications, and null-prefix handling. Backup and table tests create other logger implementations but do not directly test `StdErrLogger`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/StdErrLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/AbstractTransactionTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/AbstractTransactionTest.java

## Purpose
`AbstractTransactionTest` is a shared JUnit base for regular and optimistic transaction tests. It defines common behavioral expectations for transaction snapshots, commit/rollback, reads/writes, column families, buffers, merge, untracked operations, indexing, write options, and batch rebuilding.

## Important APIs and Types
The abstract `startDb()` returns a `DBContainer`, which supplies `beginTransaction()` overloads and access to a test column family. Tests cover `Transaction`, `ReadOptions`, `WriteOptions`, `WriteBatch`, `WriteBatchWithIndex`, `Snapshot`, `GetStatus`, and `ColumnFamilyHandle`. `TestTransactionNotifier` records snapshots from `setSnapshotOnNextOperation`.

## Control Flow, State, and Persistence
Each test creates a temporary DB container and uses try-with-resources to close DBs, options, and transactions. Commit tests verify persisted visibility after transaction close; rollback/savepoint tests verify staged writes are removed. Byte-array and `ByteBuffer` tests inspect target-buffer positions, required sizes, and partial reads. Merge tests rely on configured merge operators with different default/CF delimiters. Untracked operations are committed and reopened to validate persistence. `rebuildFromWriteBatch` imports a separate batch into a transaction.

## Dependencies and Integration Points
Depends on JUnit, AssertJ, `TemporaryFolder`, `PlatformRandomHelper`, UTF-8 utilities, and the RocksDB Java transaction API. Concrete subclasses provide DB setup and merge/operator configuration.

## Risks and Test Signals
This file is a major test signal for transaction API stability. It catches handle ownership (`getSnapshot`, `getWriteBatch`, `getWriteOptions`, commit-time batch), buffer handling, column-family overload symmetry, savepoints, lock timeout, log number state, and merge behavior. Some helper methods for heap `ByteBuffer` merge lack `@Test`, so subclasses or future changes should confirm intended coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/AbstractTransactionTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BackupEngineOptionsTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BackupEngineOptionsTest.java

## Purpose
`BackupEngineOptionsTest` verifies Java getter/setter bindings and disposed-handle assertions for `BackupEngineOptions`.

## Important APIs and Types
Tests cover `backupDir`, `backupEnv`, `shareTableFiles`, `infoLog`, `sync`, `destroyOldData`, `backupLogFiles`, `backupRateLimit`, `backupRateLimiter`, `restoreRateLimit`, `restoreRateLimiter`, `shareFilesWithChecksum`, `maxBackgroundOperations`, and `callbackTriggerIntervalSize`.

## Control Flow, State, and Persistence
Each option test constructs `BackupEngineOptions` in try-with-resources, mutates native-backed state, and asserts the getter value. Negative backup/restore rate limits are expected to map to zero. Disposed-handle tests close the options object, set `ExpectedException` to `AssertionError`, then invoke methods on the closed object.

## Dependencies and Integration Points
Depends on `RocksNativeLibraryResource`, AssertJ, JUnit `ExpectedException`, `RocksMemEnv`, `Env`, `Logger`, `RateLimiter`, and `PlatformRandomHelper`. It validates backup option integration with envs, loggers, and rate limiters.

## Risks and Test Signals
The test gives strong binding coverage for options but relies on Java assertions being enabled for disposed-handle failures. It also confirms constructor validation rejects null backup directories. It does not create real backups; `BackupEngineTest` covers operational behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BackupEngineOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BackupEngineTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BackupEngineTest.java

## Purpose
`BackupEngineTest` verifies end-to-end backup engine operations against temporary RocksDB instances.

## Important APIs and Types
Tests cover `createNewBackup`, `createNewBackupWithMetadata`, `deleteBackup`, `purgeOldBackups`, `restoreDbFromLatestBackup`, `restoreDbFromBackup`, `getCorruptedBackups`, `garbageCollect`, and `getBackupInfo`.

## Control Flow, State, and Persistence
Each test opens a temporary DB, writes known key/value pairs, creates backups under a temporary backup folder, and validates backup counts. Restore tests mutate DB values after backups, close the DB, restore from latest or selected backup, reopen the DB, and assert value suffixes reflect restored versions. `verifyNumberOfValidBackups` ensures no corrupted backups, runs garbage collection, and returns backup metadata.

## Dependencies and Integration Points
Depends on `Options`, `RocksDB`, `BackupEngineOptions`, `BackupEngine`, `RestoreOptions`, `BackupInfo`, `TemporaryFolder`, AssertJ, and `ThreadLocalRandom`.

## Risks and Test Signals
This is a strong integration signal for backup persistence, metadata, deletion, purge retention, and restore correctness. It also exercises filesystem cleanup and DB close/reopen ordering. It does not explicitly test WAL-disabled backup hazards described in `WriteOptions`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BackupEngineTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BlobOptionsTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BlobOptionsTest.java

## Purpose
`BlobOptionsTest` validates blob-related option bindings and real blob file creation behavior for default and non-default column families.

## Important APIs and Types
It covers `Options`, `ColumnFamilyOptions`, `MutableColumnFamilyOptionsBuilder`, `PrepopulateBlobCache`, `CompressionType`, `FlushOptions`, `RocksDB`, `ColumnFamilyDescriptor`, and `ColumnFamilyHandle`.

## Control Flow, State, and Persistence
Helper methods build small and large keys/values and count `.sst`/`.blob` files in the temp DB folder. Option tests assert defaults, fluent setter returns, getters, and mutable option key/value serialization. `testBlobWriteAboveThreshold` enables blob files, flushes a small value and confirms no blob, then flushes a large value and confirms a blob file plus readable values. The column-family test creates CFs with and without blob options, reopens with descriptors, verifies fetched mutable options, flushes large writes, and confirms only the blob-enabled CF creates a blob file.

## Dependencies and Integration Points
Depends on RocksDB native library, JUnit, AssertJ, temp folders, collection utilities, UTF-8 encoding, and RocksDB option/flush/CF APIs.

## Risks and Test Signals
The tests validate persistent file side effects, option round-tripping, and CF-specific blob behavior. Risks include filesystem listing assumptions, flush timing, and handle cleanup for column families created without retaining returned handles in the first open phase.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BlobOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BlockBasedTableConfigTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BlockBasedTableConfigTest.java

## Purpose
`BlockBasedTableConfigTest` validates Java bindings for block-based table configuration and several integration effects involving OPTIONS files, caches, persistent cache, and invalid format versions.

## Important APIs and Types
It covers `BlockBasedTableConfig`, `IndexType`, `DataBlockIndexType`, `ChecksumType`, `IndexSearchType`, `IndexShorteningMode`, `Cache`, `LRUCache`, `Statistics`, `TickerType`, `PersistentCache`, `Logger`, `DBOptions`, `Options`, `BloomFilter`, and `RocksDB`.

## Control Flow, State, and Persistence
Simple tests set one option and assert the getter. `jniPortal` opens DBs with selected table config values, reads generated `OPTIONS` files via `Files.walk`, and asserts native option serialization contains expected strings. Cache integration opens multiple shard DBs sharing an LRU cache and statistics, flushes/reads a key, and expects block cache add ticker increments. Invalid format version tests assert negative versions fail Java assertion and huge versions fail DB open. Deprecated tests document no-op or legacy behavior.

## Dependencies and Integration Points
Depends on JUnit, AssertJ, temp folders, Java NIO filesystem APIs, RocksDB native library, and table/cache/statistics bindings.

## Risks and Test Signals
This is strong coverage for JNI option translation and persistence into OPTIONS files. It is sensitive to options-file formatting, ticker semantics, and native defaults. An ignored import exists but no active ignored test. Filesystem cleanup calls `RocksDB.destroyDB` after reading options.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BlockBasedTableConfigTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BuiltinComparatorTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BuiltinComparatorTest.java

## Purpose
`BuiltinComparatorTest` verifies built-in bytewise and reverse-bytewise comparator behavior through real DB iteration.

## Important APIs and Types
Tests use `BuiltinComparator.BYTEWISE_COMPARATOR`, `BuiltinComparator.REVERSE_BYTEWISE_COMPARATOR`, `Options.setComparator`, `RocksDB`, and `RocksIterator`.

## Control Flow, State, and Persistence
Each comparator test opens a temp DB, writes keys `abc1` through `abc3`, iterates from first to end, checks key order and values, seeks to last, and checks seek behavior. The enum test verifies ordinal stability, value count, and `valueOf`.

## Dependencies and Integration Points
Depends on RocksDB native library, JUnit, AssertJ, temp folders, and DB iterator APIs.

## Risks and Test Signals
The tests protect comparator ordering and enum compatibility. They also confirm reverse comparator seek semantics differ from forward ordering. They do not test Java comparator implementations directly, but they provide baseline expectations for native built-ins referenced by util comparator docs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BuiltinComparatorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ByteBufferUnsupportedOperationTest.java -->
# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ByteBufferUnsupportedOperationTest.java

## Purpose
`ByteBufferUnsupportedOperationTest` is a regression/stress test for a previously intermittent unsupported-operation failure involving Java reverse comparator-backed column families, write batches, and iteration.

## Important APIs and Types
It defines a nested `Handler` that owns a `RocksDB` instance and a concurrent map of `UUID` to `ColumnFamilyHandle`. It uses `Options`, `ColumnFamilyOptions`, `ReverseBytewiseComparator`, `ComparatorOptions`, `ColumnFamilyDescriptor`, `WriteBatch`, `WriteOptions`, and `RocksIterator`.

## Control Flow, State, and Persistence
`Handler` destroys and opens a DB at `testDB`, creates column families with reverse bytewise Java comparator and universal compaction, batches key/value writes into a target CF, and scans values by iterator. `inner` creates 1000 key/value pairs, writes them, and verifies every value is found. The JUnit test repeats `inner` ten times to raise the chance of reproducing intermittent failures, printing the repeat index on runtime exception.

## Dependencies and Integration Points
Depends on JUnit, Rocks native library loading, `TemporaryFolder` though the test currently uses the literal path `testDB`, Java UUID/collections/concurrency utilities, and util `ReverseBytewiseComparator`.

## Risks and Test Signals
The literal DB path can collide with working-directory state and does not use the `TemporaryFolder` rule. `Options` and `ColumnFamilyOptions` are not consistently closed in `Handler`. Despite that, the test is a useful signal for Java comparator, write batch, column family, and iterator interaction under repeated writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ByteBufferUnsupportedOperationTest.java -->
