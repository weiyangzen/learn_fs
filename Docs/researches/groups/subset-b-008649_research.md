# subset-b-008649 Research

Grouped research report for RocksDB RocksJNI merge operators, native comparator wrapper test support, optimistic transaction DB, and optimistic transaction options. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/merge_operator.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/merge_operator.cc

## Purpose
Implements the JNI bridge for Java `StringAppendOperator` and `UInt64AddOperator`, exposing built-in C++ `ROCKSDB_NAMESPACE::MergeOperator` factories to RocksJava. The file lets Java option objects hold a native handle to a heap-allocated `std::shared_ptr<MergeOperator>` that can be passed into DB, column-family, SST writer, and transaction configuration paths.

## Important APIs, Types, And Functions
The exported JNI entry points are `Java_org_rocksdb_StringAppendOperator_newSharedStringAppendOperator__C`, `Java_org_rocksdb_StringAppendOperator_newSharedStringAppendOperator__Ljava_lang_String_2`, `Java_org_rocksdb_StringAppendOperator_disposeInternalJni`, `Java_org_rocksdb_UInt64AddOperator_newSharedUInt64AddOperator`, and `Java_org_rocksdb_UInt64AddOperator_disposeInternalJni`. They allocate or delete `std::shared_ptr<ROCKSDB_NAMESPACE::MergeOperator>` objects, wrapping results from `MergeOperators::CreateStringAppendOperator` and `MergeOperators::CreateUInt64AddOperator`. `GET_CPLUSPLUS_POINTER` converts native pointers to `jlong` handles for Java.

## Control Flow
The char-delimiter constructor casts the Java `jchar` to `char`, constructs the C++ string append merge operator, stores the returned shared pointer in a heap-allocated shared-pointer wrapper, and returns that wrapper's address. The string-delimiter overload calls `JniUtil::copyStdString`; if copying throws or reports an exception, it returns `0` immediately, otherwise it constructs the merge operator with the copied delimiter. Disposal receives the Java handle, reinterprets it as a pointer to the heap-allocated shared pointer, and deletes only that wrapper, letting normal `shared_ptr` reference counting release the underlying merge operator when no C++ options still retain it. The UInt64 operator path follows the same allocation/disposal pattern without delimiter conversion.

## State And Persistence Behavior
This file does not persist RocksDB data directly. Its durable effect is indirect: the merge operator selected here changes how later merge operands are combined during writes, reads, flushes, and compactions. Native state consists only of heap allocations and shared ownership around `MergeOperator` instances. Java is responsible for calling the matching `disposeInternalJni` through `RocksObject` lifecycle; options or column-family options that copy the shared pointer can keep the operator alive after the Java wrapper is closed.

## Dependencies And Integration Points
The bridge depends on generated JNI headers for `StringAppendOperator` and `UInt64AddOperator`, `rocksdb/merge_operator.h`, `utilities/merge_operators.h`, `rocksjni/portal.h`, and `rocksjni/cplusplus_to_java_convert.h`. Java callers are `StringAppendOperator.java` and `UInt64AddOperator.java`, and integration usually happens through `Options.setMergeOperator`, `ColumnFamilyOptions.setMergeOperator`, `SstFileWriter`, and transaction tests that configure merge behavior for column families.

## Risks And Edge Cases
The `jchar` to `char` cast truncates non-8-bit delimiters; callers needing multi-byte or non-ASCII delimiters must use the string overload. A null or uncopyable Java string relies on `copyStdString` to signal a JNI exception and returns a null native handle. Misordered lifecycle between Java merge operators and options is mitigated by `shared_ptr`, but an invalid or double-disposed handle would still be unsafe at the JNI boundary. The file allocates with `new` and has no local RAII guard between allocation and returning the handle; current paths are simple enough that only allocation failure or JNI exceptions before allocation matter.

## Test Signals
Direct behavior is covered indirectly by Java merge tests such as `MergeTest`, `MergeVariantsTest`, `MergeCFVariantsTest`, `PutVariantsTest`, `PutCFVariantsTest`, `RocksDBTest`, and SST reader/writer tests that configure `StringAppendOperator` or `UInt64AddOperator` and assert merge results. Optimistic transaction tests also configure string append operators for default and named column families, exercising compatibility with transaction DB open paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/merge_operator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/native_comparator_wrapper_test.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/native_comparator_wrapper_test.cc

## Purpose
Provides a tiny native comparator implementation used by RocksJava's `NativeComparatorWrapperTest`. It verifies that Java can wrap a native `ROCKSDB_NAMESPACE::Comparator` in a Java comparator object, configure it on `Options`, write data, reopen the database, and observe iteration order produced by the native comparator.

## Important APIs, Types, And Functions
`NativeComparatorWrapperTestStringComparator` is a test-only `Comparator` subclass. It implements `Name`, `Compare`, `FindShortestSeparator`, and `FindShortSuccessor`. The JNI factory `Java_org_rocksdb_NativeComparatorWrapperTest_00024NativeStringComparatorWrapper_newStringComparator` creates the comparator and returns its pointer as a `jlong` with `GET_CPLUSPLUS_POINTER`.

## Control Flow
Java test class `NativeComparatorWrapperTest.NativeStringComparatorWrapper` calls `initializeNative`, which invokes the JNI `newStringComparator`. The native factory allocates `NativeComparatorWrapperTestStringComparator` and returns the handle. RocksDB later calls `Compare` during memtable/table operations and iteration; the implementation converts both `Slice` arguments to `std::string` and uses `std::string::compare` for bytewise lexicographic ordering. Separator and successor shortening are explicit no-ops, so RocksDB keeps keys unchanged during index-boundary optimization callbacks.

## State And Persistence Behavior
The comparator object has no mutable fields and persists no data itself. Its ordering affects the physical and logical ordering of keys written to the test database, so the same comparator must be supplied when reopening the DB. The JNI allocation transfers native pointer ownership into the Java `NativeComparatorWrapper` lifecycle; this file contains only the factory, while disposal is inherited from comparator-wrapper infrastructure.

## Dependencies And Integration Points
Depends on the generated nested-class JNI header `org_rocksdb_NativeComparatorWrapperTest_NativeStringComparatorWrapper.h`, `rocksdb/comparator.h`, `rocksdb/slice.h`, and pointer conversion helpers. It integrates with `NativeComparatorWrapperTest.java`, `Options.setComparator`, `RocksDB.open`, and `RocksIterator`. Because the class is inside `ROCKSDB_NAMESPACE`, it matches the comparator ABI expected by the C++ DB implementation.

## Risks And Edge Cases
`Compare` materializes both slices as `std::string`, which is acceptable for a test comparator but would be inefficient for production hot paths. No-op separator methods are legal but can reduce table-index optimization opportunities. The comparator name is fixed; changing it can make existing RocksDB data with the older comparator name fail comparator consistency checks. Since this is a native test helper, leaks or double-free behavior would surface through Java wrapper ownership rather than code in this file.

## Test Signals
The primary signal is `NativeComparatorWrapperTest.rountrip`, which writes 1,000 random string keys, sorts the expected strings with Java natural ordering, reopens the DB with the same comparator, iterates from first to last, and checks that RocksDB iteration matches the comparator's ordering. Build/link correctness is also tested by successful loading of the nested JNI symbol name containing `_00024`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/native_comparator_wrapper_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/optimistic_transaction_db.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/optimistic_transaction_db.cc

## Purpose
Implements the JNI bridge for Java `OptimisticTransactionDB`, exposing open, close, transaction creation, transaction reuse, and base-DB access over C++ `ROCKSDB_NAMESPACE::OptimisticTransactionDB`. This is the native layer behind RocksJava optimistic transactions, where conflicts are checked optimistically at commit time rather than through the pessimistic lock manager used by `TransactionDB`.

## Important APIs, Types, And Functions
The file exports two overloaded `open` JNI functions: one for `Options` plus path and one for `DBOptions`, path, column-family names, and column-family option handles. It also exports `disposeInternalJni`, `closeDatabase`, `beginTransaction` overloads with `WriteOptions` and optional `OptimisticTransactionOptions`, `beginTransaction_withOld` overloads for reusing an existing `Transaction`, and `getBaseDB`. Key native types are `OptimisticTransactionDB`, `Options`, `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyOptions`, `ColumnFamilyHandle`, `WriteOptions`, `OptimisticTransactionOptions`, `Transaction`, `Status`, and `RocksDBExceptionJni`.

## Control Flow
The simple `open` path obtains a UTF-8 database path from the Java string, casts the options handle, calls `OptimisticTransactionDB::Open(*options, db_path, &otdb)`, releases the Java string, and returns the DB pointer on success or throws a Java `RocksDBException` on failure. The column-family `open` path converts Java byte-array family names plus parallel option handles into `std::vector<ColumnFamilyDescriptor>`, opens the DB with `OptimisticTransactionDB::Open(*db_options, db_path, column_families, &handles, &otdb)`, and returns a `long[]` containing the DB handle followed by each `ColumnFamilyHandle` pointer. JNI cleanup paths release strings, byte arrays, long arrays, and local references on most conversion failures.

`closeDatabase` calls `OptimisticTransactionDB::Close()` and throws through `RocksDBExceptionJni` if the status is not OK. `disposeInternalJni` deletes the native DB object after the Java side has decided it owns the handle. New transaction functions cast DB and write-option handles and call `BeginTransaction`, returning the native `Transaction*`. Reuse functions pass an existing transaction pointer as `old_txn`; both assert that RocksDB returns the same pointer, preserving the Java assumption that no new `Transaction` wrapper should be allocated. `getBaseDB` returns the underlying `DB*`, which Java wraps in a non-owning `RocksDB` by calling `disOwnNativeHandle`.

## State And Persistence Behavior
Opening an optimistic transaction DB initializes or opens on-disk RocksDB state at the provided path and may open multiple column families. The JNI bridge itself stores no global state, but it hands Java durable native handles for the DB and column-family handles. Transactions returned by `BeginTransaction` hold native transaction state, write batches, snapshots if configured through `OptimisticTransactionOptions`, and conflict-check metadata until commit, rollback, reuse, or disposal. `closeDatabase` closes the DB without fsyncing WALs by itself, matching Java documentation that callers needing sync must call `syncWal` or a synced write first. `getBaseDB` deliberately exposes a non-owning base DB view so Java cannot delete the same C++ DB twice.

## Dependencies And Integration Points
Depends on generated `org_rocksdb_OptimisticTransactionDB.h`, `rocksdb/utilities/optimistic_transaction_db.h`, `rocksdb/utilities/transaction.h`, `rocksdb/options.h`, pointer conversion helpers, and `rocksjni/portal.h` for exception translation. Java integration is in `OptimisticTransactionDB.java`, which stores option references, creates Java `ColumnFamilyHandle` objects from returned native handles, manages default column-family ownership, wraps returned transaction handles in `Transaction`, and asserts old-transaction reuse. Behavior parallels `transaction_db.cc` but omits `TransactionDBOptions` because optimistic transactions do not use the same lock-table configuration.

## Risks And Edge Cases
JNI array conversion assumes Java passes parallel column-family name and option arrays with compatible lengths; Java constructs these arrays from descriptors, but native code does not independently validate the option-array length. If creating the result `jlongArray` fails after a successful open, this function returns `nullptr` without closing the newly opened DB or column-family handles, creating a native leak on an out-of-memory edge path. In the column-family success path, `SetLongArrayRegion` exception handling returns without deleting handles or DB; this is also an exceptional leak path. The no-column-family branch avoids `GetLongArrayElements`, but Java normally requires at least the default family for this overload. Assertions on DB and old-transaction pointers catch invalid internal use in debug builds but do not protect release builds from bad handles. Correctness depends on Java closing column-family handles before closing the DB, which `OptimisticTransactionDB.close()` does through `ownedColumnFamilyHandles`.

## Test Signals
`OptimisticTransactionDBTest` exercises simple open, column-family open, missing default-family validation from Java, begin transaction with and without options, old-transaction reuse, close behavior, and base DB access. `OptimisticTransactionTest` and `AbstractTransactionTest` provide broader transaction semantics coverage for reads, writes, savepoints, conflict detection, merges, snapshots, and column families. `OptimisticTransactionSample` demonstrates read-committed, repeatable-read via `setSetSnapshot(true)`, and conflict behavior, serving as an integration signal for the JNI methods in realistic use.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/optimistic_transaction_db.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/optimistic_transaction_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/optimistic_transaction_options.cc

## Purpose
Implements the JNI bridge for Java `OptimisticTransactionOptions`, allowing Java to allocate, configure, inspect, and dispose C++ `ROCKSDB_NAMESPACE::OptimisticTransactionOptions`. These options are passed to `OptimisticTransactionDB::BeginTransaction` to control snapshot setup and comparator use for optimistic transaction conflict tracking.

## Important APIs, Types, And Functions
The exported JNI functions are `Java_org_rocksdb_OptimisticTransactionOptions_newOptimisticTransactionOptions`, `Java_org_rocksdb_OptimisticTransactionOptions_isSetSnapshot`, `Java_org_rocksdb_OptimisticTransactionOptions_setSetSnapshot`, `Java_org_rocksdb_OptimisticTransactionOptions_setComparator`, and `Java_org_rocksdb_OptimisticTransactionOptions_disposeInternalJni`. They operate on `OptimisticTransactionOptions::set_snapshot` and `OptimisticTransactionOptions::cmp`, using native handles for `OptimisticTransactionOptions` and `Comparator`.

## Control Flow
Construction allocates a default `OptimisticTransactionOptions` and returns its pointer as a Java long handle. `isSetSnapshot` casts the handle and returns the current `set_snapshot` field. `setSetSnapshot` casts the handle and writes the Java boolean into `set_snapshot`. `setComparator` casts both the options handle and comparator handle and stores the comparator pointer in `opts->cmp`. Disposal deletes the options object behind the handle.

## State And Persistence Behavior
The options object is transient configuration, not persisted DB state. `set_snapshot` affects future transactions begun with the options: RocksDB can take a transaction snapshot at begin time, enabling repeatable-read style behavior. `cmp` is a borrowed pointer to a comparator owned elsewhere; it affects key comparison inside optimistic transaction internals when a DB uses a non-default comparator. The native options object must remain alive until `BeginTransaction` has consumed it, and the comparator object must remain alive for any transaction logic that dereferences `cmp`.

## Dependencies And Integration Points
Depends on generated `org_rocksdb_OptimisticTransactionOptions.h`, `rocksdb/utilities/optimistic_transaction_db.h`, `rocksdb/comparator.h`, and pointer conversion helpers. Java integration is in `OptimisticTransactionOptions.java`, whose fluent methods call these native functions after checking `isOwningHandle()`. The options are consumed by `optimistic_transaction_db.cc` `beginTransaction` overloads. Comparator handles commonly come from `AbstractComparator` subclasses such as `BytewiseComparator`, and the Java API documents this as needed for DBs with non-default comparators.

## Risks And Edge Cases
`setComparator` stores a raw borrowed `Comparator*` without increasing lifetime ownership, so Java code must keep the comparator alive at least as long as options and any transactions needing it. There is no null-handle validation; invalid handles become undefined native behavior. Boolean conversion relies on `jboolean` mapping cleanly into the C++ bool field. Disposal is straightforward, but using an options handle after close or passing it concurrently while mutating fields from Java would be unsafe in the usual RocksJNI native-handle model.

## Test Signals
`OptimisticTransactionOptionsTest.setSnapshot` sets a random boolean and reads it back through JNI, directly covering `setSetSnapshot` and `isSetSnapshot`. `OptimisticTransactionOptionsTest.comparator` constructs a direct-buffer `BytewiseComparator` and calls `setComparator`, covering handle assignment and basic lifecycle. `OptimisticTransactionDBTest` and `OptimisticTransactionSample` exercise these options when beginning transactions, especially `setSetSnapshot(true)` for repeatable-read examples.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/optimistic_transaction_options.cc -->
