# subset-b-008665 Research

Grouped research report for the RocksDB Java test files assigned to `subset-b-008665`. Each section is source-tree-aligned and wrapped for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MergeTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MergeTest.java

### Purpose

`MergeTest` validates Java bindings for RocksDB merge operators. It covers merge operators set by registered name, merge operators set by Java wrapper instance, column-family-specific merge options, native object lifetime/reuse, string-append delimiter behavior, and invalid merge-operator-name inputs.

### Important APIs, Types, And Functions

Important APIs are `Options.setMergeOperatorName`, `ColumnFamilyOptions.setMergeOperatorName`, `Options.setMergeOperator`, `ColumnFamilyOptions.setMergeOperator`, `StringAppendOperator`, `UInt64AddOperator`, `RocksDB.merge`, `RocksDB.put`, `RocksDB.get`, `RocksDB.open`, `DBOptions`, `ColumnFamilyDescriptor`, and `ColumnFamilyHandle`. The helper methods `longToByteArray` and `longFromByteArray` encode/decode little-endian 64-bit values expected by the `uint64add` merge operator.

### Control Flow

Each test opens a temporary database, installs a merge operator, writes a base value, performs one merge, and asserts the resolved value. Column-family tests open or create additional CFs and close every handle in `finally`. GC behavior tests intentionally open and close DBs while reusing, replacing, or freshly constructing operator objects to ensure Java objects keep native merge-operator handles alive long enough.

### State And Persistence Behavior

The database state is temporary JUnit state under `TemporaryFolder`, but operations exercise durable RocksDB writes, merge operands, column-family metadata, and reopen behavior. Merge resolution is verified through `get`, so failures can indicate option propagation, native merge function lookup, byte order, or JNI lifetime issues.

### Dependencies And Integration Points

This test depends on the native RocksDB library resource, AssertJ, JUnit, Java `ByteBuffer`, `StringAppendOperator`, `UInt64AddOperator`, and column-family open/create APIs. It integrates with registered C++ merge operator names (`stringappend`, `uint64add`) and Java-owned native operator wrappers.

### Risks And Edge Cases

- `cFStringOption` uses `RocksDB.DEFAULT_COLUMN_FAMILY` twice in descriptors, while the later operator-instance CF tests use `"new_cf"`; duplicate default descriptors can obscure intended non-default CF coverage.
- `uint64add` requires little-endian eight-byte operands, so Java byte-order regressions would silently produce wrong sums.
- Native operator ownership is subtle because `Options`/`ColumnFamilyOptions` can outlive or replace Java merge operator wrappers.
- Empty merge operator names are allowed but `null` names must throw `IllegalArgumentException`.

### Test Signals

Signals are exact merged values (`aa,bb`, `aabb`, `aa<>bb`, `101`, `257`, `250`) and expected exceptions for null names. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MergeTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MergeVariantsTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MergeVariantsTest.java

### Purpose

`MergeVariantsTest` parameterizes equivalent Java `RocksDB.merge` overloads and verifies each overload writes the same merge operand to RocksDB.

### Important APIs, Types, And Functions

The central type is the `FunctionMerge<RocksDB, byte[], byte[]>` functional interface. Parameters cover plain byte-array `merge`, `WriteOptions` overloads, offset/length byte-array overloads, direct `ByteBuffer`, and heap `ByteBuffer` overloads. It reuses `MergeTest.longToByteArray` and `longFromByteArray` with `UInt64AddOperator`.

### Control Flow

JUnit `Parameterized` creates one test instance per merge function. The test opens a temporary DB with `UInt64AddOperator`, writes `100` under `"key"`, invokes the parameterized merge to add `1`, then reads and verifies `101`.

### State And Persistence Behavior

The state under test is one persisted key whose value is transformed by RocksDB's native merge machinery. Sliced byte-array overloads allocate larger arrays with prefixes/suffixes, checking JNI respects offsets and lengths rather than consuming the full backing arrays.

### Dependencies And Integration Points

This integrates RocksDB Java overload dispatch, `WriteOptions`, heap/direct `ByteBuffer` handling, UTF-8 string construction for padded arrays, and the native `UInt64AddOperator`.

### Risks And Edge Cases

- Direct and heap buffers must be flipped correctly so position/limit are honored.
- Offset/length overloads can corrupt keys or values if JNI uses backing array bounds incorrectly.
- Temporary `WriteOptions` created inside lambdas are not explicitly closed, so the test favors API coverage over strict resource accounting.

### Test Signals

All merge overloads must return `101` from the same key. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MergeVariantsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MixedOptionsTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MixedOptionsTest.java

### Purpose

`MixedOptionsTest` verifies behavior where DB-level and column-family-level options are combined into a single `Options` object, especially table format configuration and environment ownership.

### Important APIs, Types, And Functions

It uses `ColumnFamilyOptions`, `DBOptions`, `Options(DBOptions, ColumnFamilyOptions)`, `BlockBasedTableConfig`, `PlainTableConfig`, `BloomFilter`, `Env`, `RocksMemEnv`, `Priority`, and optimization helpers such as `optimizeUniversalStyleCompaction`, `optimizeLevelStyleCompaction`, `optimizeForPointLookup`, and `prepareForBulkLoad`.

### Control Flow

The first test installs a block-based table with Bloom filter, checks the table factory name, switches to plain table, then constructs `Options` from DB and CF options and checks the table factory propagated. It also invokes optimization/preparation methods for both CF and combined option types. The second test verifies default env identity, switches DB options to a `RocksMemEnv`, adjusts background thread counts, and confirms combined `Options` exposes the selected env.

### State And Persistence Behavior

No database is opened. State is native option-object state and environment configuration, including mutable background thread counts on default and memory environments.

### Dependencies And Integration Points

This test integrates Java option wrappers with native table factories, filter policy ownership, default env singleton behavior, memory env wrapping, and priority-specific background thread settings.

### Risks And Edge Cases

- Env assertions show setting thread counts through `memEnv` and `Env.getDefault()` can both affect observed values, which is subtle for wrapper identity and shared underlying env state.
- Table factory name propagation depends on `Options(DBOptions, ColumnFamilyOptions)` copying CF table config correctly.
- Optimization helper methods are smoke-tested only for linkability, not for specific option deltas.

### Test Signals

Signals are table factory names (`BlockBasedTable`, `PlainTable`), env identity (`sameAs`/`notSameAs`), and expected background thread counts. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MixedOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MultiColumnRegressionTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MultiColumnRegressionTest.java

### Purpose

`MultiColumnRegressionTest` is a regression test for transactional multi-column-family problems referenced by RocksDB issue 9006. It checks transaction reads/writes across several column-family handles with both normal and extremely long CF names.

### Important APIs, Types, And Functions

The test uses parameterized `Params(numColumns, keySize)`, `TransactionDB.open`, `OptimisticTransactionDB.open`, `Transaction.put`, `Transaction.get`, `Transaction.commit`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `DBOptions`, and `TransactionDBOptions`.

### Control Flow

For `TransactionDB`, it builds `numColumns` descriptors whose names include a long repeated suffix, creates them in a plain `RocksDB`, reopens as `TransactionDB` with those descriptors plus default, writes one key per CF and one default key in a transaction, commits, reopens, and reads each CF key in a new transaction. For optimistic transactions, descriptors are intentionally all named `"default"` plus another default descriptor, then an `OptimisticTransactionDB` writes and rereads through the returned handles.

### State And Persistence Behavior

The test persists CF metadata and transaction writes across close/reopen. It verifies that handle ordering and native column-family identity remain consistent despite large descriptor names and repeated descriptor names in the optimistic path.

### Dependencies And Integration Points

It integrates JUnit parameterization, RocksDB CF creation/opening, `TransactionDB`, `OptimisticTransactionDB`, and transaction read/write APIs.

### Risks And Edge Cases

- The optimistic test uses duplicate default CF names, which may target wrapper regression coverage but is unusual compared with normal CF usage.
- Handles must be closed manually after transaction DB close scopes; leaks or wrong close order would affect JNI resource lifetime.
- Long CF names stress native vector/string handling and Java array marshalling.

### Test Signals

Each CF key must return `"value" + (i - 7)` after reopen, for both moderate and very large CF-name sizes. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MultiColumnRegressionTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MultiGetManyKeysTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MultiGetManyKeysTest.java

### Purpose

`MultiGetManyKeysTest` stresses `multiGetAsList` and transactional multi-get APIs with very large key-list sizes, including 750,000 keys on 64-bit systems.

### Important APIs, Types, And Functions

It uses `RocksDB.multiGetAsList`, `Transaction.multiGetAsList`, `Transaction.multiGetForUpdateAsList`, CF variants of those methods, `TransactionDB.open`, `ColumnFamilyDescriptor`, and helper methods for random key/value generation. The private `Key` wrapper provides content-based equality and hashing for `byte[]` keys.

### Control Flow

Parameterized tests generate random four-byte keys, randomly assign values to about 10 percent of them, write those values to the DB or a non-default CF, reopen as plain or transactional DB, perform multi-get, and compare every returned position to the expected map. A `BeforeClass` assumption skips the class on 32-bit systems.

### State And Persistence Behavior

Data is written in one DB handle and read after reopening, so values must survive close/open and be addressable by large Java collections. Transactional variants read without committing modifications, but `multiGetForUpdateAsList` also exercises lock/conflict bookkeeping paths.

### Dependencies And Integration Points

This integrates Java collection marshalling, native batch point lookup, transaction DB wrappers, CF handle lists sized to the key list, and platform detection via `org.rocksdb.util.Environment`.

### Risks And Edge Cases

- Four-byte random keys can collide; the map and DB overwrite semantics use the later value, but duplicate keys can make coverage less uniform.
- Very large lists stress JNI array/list conversion, native vector sizing, memory pressure, and 32-bit size limits.
- CF tests depend on matching every key with the same CF handle and closing handles after transaction use.

### Test Signals

The returned value list size must equal the key list size, and each element must match the stored byte array or `null`. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MultiGetManyKeysTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MultiGetTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MultiGetTest.java

### Purpose

`MultiGetTest` exercises the Java multi-get surface comprehensively: list-returning byte-array APIs, direct and heap `ByteBuffer` APIs, read-option overloads, column-family overloads, error validation, truncated buffers, and ignored huge-value overflow scenarios.

### Important APIs, Types, And Functions

Important APIs include `RocksDB.multiGetAsList`, `RocksDB.multiGetByteBuffers`, `ByteBufferGetStatus`, `Status.Code`, `ReadOptions`, `ColumnFamilyHandle`, `TestUtil.bufferBytes`, and `StringAppendOperator` for huge merged values. Helpers include `putNThenMultiGetHelper`, `putNThenMultiGetHelperWithMissing`, `bbDirect`, `createIntOverflowValue`, and `checkIntOVerflowValue`.

### Control Flow

Small tests write three keys and read them by byte-array list or ByteBuffer list, with and without missing keys. Direct-buffer tests allocate key/value buffers, flip key buffers, call multi-get, then assert status, required size, and returned value buffer content. CF tests create CFs, check default-CF misses, single-handle shorthand, one-handle-per-key lists, mixed CF routing, and argument-count validation. Ignored tests generate multi-gigabyte logical values through repeated string-append merges and verify direct-buffer incomplete status or heap-list allocation failure.

### State And Persistence Behavior

Normal tests use temporary DB state in one handle. Huge-value tests would persist very large merged operands and intentionally probe Java/native size boundaries; they are `@Ignore` due to disk and time cost. Short-buffer tests ensure the API reports full `requiredSize` while returning only capacity-limited bytes.

### Dependencies And Integration Points

This file integrates RocksDB native point lookup vectors, Java NIO direct and heap buffers, CF handle mapping rules, status propagation, AssertJ exception assertions, and `TestUtil.bufferBytes`.

### Risks And Edge Cases

- Some assertions in sliced and short-buffer cases compare `requiredSize` or expected values in a way that appears order-sensitive and could conceal copy/paste mistakes.
- Direct buffer position/limit/capacity handling is a common JNI risk, especially for sliced buffers and truncated values.
- CF handle lists may be either one handle for all keys or one per key; wrong validation would break both convenience and strict forms.
- Ignored overflow tests document behavior but do not protect CI.

### Test Signals

Signals are ordered result size, `Ok`/`NotFound`/`Incomplete` statuses, exact values, `requiredSize`, and expected `IllegalArgumentException` or `RocksDBException` messages. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MultiGetTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MutableColumnFamilyOptionsTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MutableColumnFamilyOptionsTest.java

### Purpose

`MutableColumnFamilyOptionsTest` validates Java builder, serialization, and parsing behavior for mutable column-family options.

### Important APIs, Types, And Functions

The core APIs are `MutableColumnFamilyOptions.builder`, `MutableColumnFamilyOptionsBuilder` setters/getters, `build`, `getKeys`, `getValues`, `toString`, and `MutableColumnFamilyOptions.parse`. Covered option groups include memtable, miscellaneous, blob, compaction, compression, and enum options such as `PrepopulateBlobCache` and `CompressionType`.

### Control Flow

Tests set selected builder fields and assert getters, verify unset getters throw `NoSuchElementException`, build key/value arrays, check semicolon serialization, parse escaped/list syntax, and parse a canned `RocksDB.getOptions` output string while ignoring unhandled non-mutable fields.

### State And Persistence Behavior

This is in-memory option state only. It models strings exchanged with RocksDB native APIs, including values with braces, colons, booleans, doubles, longs, and enums.

### Dependencies And Integration Points

It integrates Java parsing code with C++-style options output from `RocksDB.getOptions`, especially for fields that are mutable at runtime.

### Risks And Edge Cases

- Parser correctness depends on handling nested option blocks while selecting only supported mutable CF options.
- Escaped list syntax such as `2:{3}:{5}` must round-trip into integer arrays.
- C++ option output changes can add names or formatting that the parser must ignore or parse safely.

### Test Signals

Signals include exact key/value ordering, exact serialized string, parsed numeric/boolean/enum values, and expected exception for unset getters. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MutableColumnFamilyOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MutableDBOptionsTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MutableDBOptionsTest.java

### Purpose

`MutableDBOptionsTest` verifies mutable DB option builder behavior, string parsing/serialization, and live retrieval from an opened RocksDB instance.

### Important APIs, Types, And Functions

It uses `MutableDBOptions.builder`, `MutableDBOptionsBuilder`, `MutableDBOptions.parse`, `MutableDBOptions.DBOption`, `RocksDB.getDBOptions`, `Options`, `DBOptions`, and CF-descriptor open overloads.

### Control Flow

Builder tests set `bytes_per_sync`, `max_background_jobs`, and `avoid_flush_during_shutdown`, then assert getter values. Serialization tests assert key/value arrays and semicolon strings. Parsing tests include escaped colon handling for `daily_offpeak_time_utc`. Live tests open DBs through both `Options` and `DBOptions` paths, call `getDBOptions`, and assert defaults plus configured off-peak time.

### State And Persistence Behavior

The test exercises in-memory builder state and native DB option state exposed by a live DB. `daily_offpeak_time_utc` is persisted in the opened DB option object and read back from native state.

### Dependencies And Integration Points

It integrates JUnit temporary directories, native library loading, mutable option string parsing, and both single-CF and descriptor-list DB open paths.

### Risks And Edge Cases

- Escaped colons are required in option strings; incorrect unescaping would break off-peak schedule parsing.
- Defaults such as `max_open_files == -1` and `avoid_flush_during_shutdown == false` are asserted against native defaults and can drift with RocksDB changes.
- `listDBOptions2` leaves returned column-family handles unclosed, a small resource-lifetime risk in the test.

### Test Signals

Signals are exact builder values, exact serialized strings, expected `NoSuchElementException`, and live `getDBOptions` values. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MutableDBOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MutableOptionsGetSetTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MutableOptionsGetSetTest.java

### Purpose

`MutableOptionsGetSetTest` validates round trips between Java mutable option builders and RocksDB native state through `createColumnFamily`, `setOptions`, `getOptions`, `setDBOptions`, and `getDBOptions`.

### Important APIs, Types, And Functions

Covered APIs include `ColumnFamilyOptions` setters for blob, memtable, compaction, and report options; `MutableColumnFamilyOptions.builder`; `RocksDB.setOptions` with and without CF handle; `RocksDB.getOptions`; `MutableDBOptions.builder`; `RocksDB.setDBOptions`; and `RocksDB.getDBOptions`.

### Control Flow

The first test creates two CFs with different `ColumnFamilyOptions` and asserts `getOptions(handle)` returns each configured value. The second creates CFs with default options, flushes, applies mutable CF options through `setOptions(handle, ...)`, then reads them back. The third applies mutable CF options to the default CF with `setOptions(...)`. The last applies mutable DB options and verifies live DB option values.

### State And Persistence Behavior

This file exercises live mutable native configuration. CF option changes affect per-CF runtime state; DB option changes affect DB-wide runtime state such as background jobs, WAL size, sync bytes, stats periods, and file buffer sizes. Data persistence is not the focus, but DB handles and CF handles must remain valid through native option updates.

### Dependencies And Integration Points

It integrates Java option builders with native RocksDB option mutation APIs, blob files, compaction thresholds, memtable behavior, and DB-level runtime controls.

### Risks And Edge Cases

- Some C++ constraints normalize values; comments call out ratio constraints, so exact assertions are sensitive to native option validation.
- Mutable and immutable options are easy to mix; only mutable fields should be accepted by `setOptions`.
- Blob-related options span feature enablement and GC thresholds, so partial round-trip failures can hide until blob DB behavior is used.

### Test Signals

Signals are exact `getOptions` and `getDBOptions` values after create or set, including two CFs with intentionally different values. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MutableOptionsGetSetTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/NativeComparatorWrapperTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/NativeComparatorWrapperTest.java

### Purpose

`NativeComparatorWrapperTest` verifies that a Java wrapper around a native comparator can be installed in `Options` and used to order keys across DB reopen.

### Important APIs, Types, And Functions

It uses `NativeComparatorWrapper`, `Options.setComparator`, `RocksDB.put`, `RocksIterator`, and a nested `NativeStringComparatorWrapper` whose `initializeNative` calls a native `newStringComparator()` method.

### Control Flow

The test generates 1,000 unique random lowercase keys, writes each to a DB configured with the native string comparator, sorts the Java copy of keys with `Comparator.naturalOrder`, reopens the DB with the same options, iterates from first to last, and compares iterator keys with the sorted Java array.

### State And Persistence Behavior

Keys are persisted to the temporary DB. The test specifically checks comparator metadata and ordering survive close/reopen when the same comparator wrapper is supplied.

### Dependencies And Integration Points

This integrates JNI comparator initialization, native comparator ownership under `Options`, iterator ordering, Java random key generation, and RocksDB library loading through a static `RocksDB.loadLibrary`.

### Risks And Edge Cases

- Duplicate random keys are skipped by checking `db.get`; the loop decrements to maintain exactly 1,000 stored keys.
- Comparator wrapper native lifetime must remain valid while options and reopened DB handles use it.
- Natural Java string order is assumed to match the native comparator created by `newStringComparator`.

### Test Signals

The iterator must produce exactly the Java-sorted key sequence. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/NativeComparatorWrapperTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/NativeLibraryLoaderTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/NativeLibraryLoaderTest.java

### Purpose

`NativeLibraryLoaderTest` verifies extraction of the RocksDB JNI library from the jar into a caller-specified temporary directory.

### Important APIs, Types, And Functions

It uses `NativeLibraryLoader.getInstance().loadLibraryFromJarToTemp`, `Environment.getJniLibraryFileName`, `TemporaryFolder`, `Files.exists`, and `Files.isReadable`.

### Control Flow

One test extracts the library and checks the expected platform-specific file exists and is readable. The second extracts twice into the same directory and asserts the originally returned file still exists, covering overwrite/replacement behavior.

### State And Persistence Behavior

The only persistent state is a native library file copied into JUnit temporary storage. No DB is opened.

### Dependencies And Integration Points

This integrates jar resource extraction, platform-specific JNI naming, filesystem permissions, and singleton loader behavior.

### Risks And Edge Cases

- Existing library replacement must handle platforms that lock loaded shared libraries.
- The expected filename depends on OS/architecture mapping in `Environment`.
- Tests validate readability but not that the extracted library can actually be loaded.

### Test Signals

Signals are file existence/readability and successful repeated extraction. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/NativeLibraryLoaderTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptimisticTransactionDBTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptimisticTransactionDBTest.java

### Purpose

`OptimisticTransactionDBTest` validates opening, column-family handling, transaction creation, base DB access, and iterator behavior for `OptimisticTransactionDB`.

### Important APIs, Types, And Functions

It uses `OptimisticTransactionDB.open` overloads, `beginTransaction`, `OptimisticTransactionOptions`, `WriteOptions`, `getBaseDB`, `isOwningHandle`, `newIterator`, `ColumnFamilyDescriptor`, and `ColumnFamilyHandle`.

### Control Flow

Tests open an optimistic transaction DB with simple options, open with default plus custom CF descriptors, assert missing default CF descriptors are rejected, create transactions with and without `OptimisticTransactionOptions`, verify `getBaseDB` returns a non-owning base `RocksDB` wrapper, and write/iterate a simple key/value pair.

### State And Persistence Behavior

Temporary DB state includes CF metadata and a single iterator-visible key. `getBaseDB` ownership assertions protect native handle ownership so closing the wrapper does not double-close the optimistic DB.

### Dependencies And Integration Points

This integrates optimistic transaction DB wrappers with base RocksDB APIs, CF descriptor validation, transaction options, write options, and iterator creation.

### Risks And Edge Cases

- Column-family open requires default CF presence; missing it must fail before native misuse.
- Non-owning base DB wrapper lifetime is subtle and must be tied to the owning optimistic transaction DB.
- Column-family handles are manually closed and must not outlive the DB.

### Test Signals

Signals are non-null DB/transaction/iterator objects, expected `IllegalArgumentException`, non-owning base DB handle, and exact iterator key/value. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptimisticTransactionDBTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptimisticTransactionOptionsTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptimisticTransactionOptionsTest.java

### Purpose

`OptimisticTransactionOptionsTest` checks the Java getter/setter binding for optimistic transaction snapshot behavior.

### Important APIs, Types, And Functions

The file uses `OptimisticTransactionOptions`, especially `setSetSnapshot` and `isSetSnapshot`, with native library loading through `RocksNativeLibraryResource`.

### Control Flow

The test constructs an options object, asserts the default snapshot flag, toggles it, and asserts the value changed.

### State And Persistence Behavior

Only in-memory native option state is involved. No DB or transaction is opened.

### Dependencies And Integration Points

This is a focused JNI binding test for options passed later to `OptimisticTransactionDB.beginTransaction`.

### Risks And Edge Cases

- Default value changes in native RocksDB would break the assertion.
- The test does not verify behavioral snapshot semantics, only option state.

### Test Signals

The snapshot flag must round-trip through Java and native getters/setters. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptimisticTransactionOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptimisticTransactionTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptimisticTransactionTest.java

### Purpose

`OptimisticTransactionTest` extends shared transaction tests with optimistic-transaction-specific behavior: unsupported prepare/two-phase commit, conflict detection for `getForUpdate` and multi-get-for-update, undoing tracked keys, transaction naming restrictions, and DB container setup.

### Important APIs, Types, And Functions

It uses `AbstractTransactionTest`, `OptimisticTransactionDB`, `OptimisticTransactionOptions`, `Transaction`, `getForUpdate`, `multiGetForUpdate`, `multiGetForUpdateAsList`, `undoGetForUpdate`, `commit`, `setName`, `Status.Code.Busy`, and `Status.Code.InvalidArgument`.

### Control Flow

Tests first establish committed baseline values, then run overlapping transactions. One transaction reads keys for update, another writes and commits conflicting changes, and the first transaction must fail on commit with `Busy`. Undo tests call `undoGetForUpdate` before the conflicting write and then commit successfully. The prepare test confirms optimistic transactions reject `prepare`, and the name test confirms `setName` is invalid.

### State And Persistence Behavior

Committed writes persist in the temporary DB. Optimistic transactions track read-for-update conflict state client-side/native-side until commit. Undo operations remove keys from the conflict set without rolling back any DB write. The container opens default and test CFs with distinct string-append merge operators and closes options, handles, write options, transaction options, and DB.

### Dependencies And Integration Points

The file integrates with shared transaction test infrastructure, CF merge options, optimistic transaction native conflict checking, deprecated and current multi-get APIs, and status-code propagation through `RocksDBException`.

### Risks And Edge Cases

- Optimistic transactions do not support two-phase commit; callers must not assume parity with `TransactionDB`.
- Deprecated array-returning multi-get APIs are still covered alongside list APIs.
- `undoGetForUpdate` must match CF-aware and default-CF key tracking exactly, or conflicts may be missed or falsely retained.
- Resource close order in the custom container is important for native handle ownership.

### Test Signals

Expected signals are `Busy` on conflicting commits, successful commits after undo, an error message for prepare, and `InvalidArgument` for transaction names. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptimisticTransactionTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptionsTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptionsTest.java

### Purpose

`OptionsTest` is broad getter/setter and ownership coverage for the combined Java `Options` wrapper, which spans `DBOptions` and `ColumnFamilyOptions` behavior.

### Important APIs, Types, And Functions

It covers copy construction, compaction/memtable/level options, DB creation flags, WAL/logging paths, background work settings, direct I/O and mmap flags, stats controls, write-buffer managers, caches, WAL filters, env, optimization helper methods, compression settings, compaction styles/options, rate limiter, SST file manager, prefix extractors, memtable factories, statistics, compaction filters/factories, old-default helpers, CF/db paths, recovery options, listeners, and table-properties collector factories.

### Control Flow

Most tests create an `Options` object, assert a default or current value, call a setter, assert fluent `this` return where expected, and verify the getter returns the new value. More complex tests construct dependent native objects (`WriteBufferManager`, `Cache`, `RateLimiter`, `SstFileManager`, `AbstractWalFilter`, listeners, collectors), attach them to options, and verify reference identity or collection contents.

### State And Persistence Behavior

The tested state is native option-object state. Most tests do not open a DB, but dependent objects represent resources that affect DB persistence and runtime behavior when used: WAL filtering, log/recovery controls, cache ownership, write-buffer memory limits, compaction behavior, and event callbacks.

### Dependencies And Integration Points

This file integrates nearly the full RocksDB Java option surface with native handles, AssertJ/JUnit assertions, random test values, custom listeners/filters, and factory objects.

### Risks And Edge Cases

- It is sensitive to native default changes because many tests assert exact defaults.
- Object ownership is subtle for caches, filters, listeners, write-buffer managers, and collector factories.
- Some option names are legacy or misspelled in method names (`unordredWrite`, table cache shard bits), so Java API compatibility is part of the signal.
- Listener and collector tests check list retention after options mutation/collector close, a key lifetime risk.

### Test Signals

Signals are exact getter values after setters, identity equality for attached objects, expected non-null lists, callback invocations after listener retrieval, and collector list size. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptionsUtilTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptionsUtilTest.java

### Purpose

`OptionsUtilTest` verifies loading RocksDB OPTIONS files through Java and reconstructing DB options, CF descriptors, and block-based table format configuration.

### Important APIs, Types, And Functions

It uses `OptionsUtil.loadLatestOptions`, `OptionsUtil.loadOptionsFromFile`, `OptionsUtil.getLatestOptionsFileName`, `ConfigOptions`, `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyOptions`, `BlockBasedTableConfig`, `BloomFilter`, and `LoaderUnderTest`.

### Control Flow

Loader tests pass a strategy object that either loads the latest options by DB path or loads an explicit OPTIONS filename. `verifyOptions` creates a DB with a second CF and custom DB/CF settings, closes it, loads options back, and compares DB options and both CF descriptors. `verifyTableFormatOptions` repeats that pattern with a custom `BlockBasedTableConfig` and delegates detailed comparison to `verifyBlockBasedTableConfig`.

### State And Persistence Behavior

The file relies on RocksDB writing OPTIONS files to the DB directory. It then parses that persisted configuration into Java option objects, so it tests config file format compatibility rather than live DB data.

### Dependencies And Integration Points

This integrates `ConfigOptions` flags (`ignoreUnknownOptions`, `inputStringsEscaped`, `Env`), RocksDB option-file persistence, CF descriptor ordering, block-based table config parsing, and filter policy comparison.

### Risks And Edge Cases

- OPTIONS file format changes can break strict loading when `ignoreUnknownOptions(false)`.
- Some table config objects, especially cache instances, are intentionally not read back, so coverage excludes ownership-heavy fields.
- Loader variants with default `ConfigOptions` may behave differently from explicit escaped-string/env settings.

### Test Signals

Signals are a non-null `OPTIONS-*` latest filename, two loaded CF descriptors in expected order, exact DB/CF option values, and exact block-based table config fields. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptionsUtilTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PerfContextTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PerfContextTest.java

### Purpose

`PerfContextTest` validates Java access to RocksDB per-thread performance counters and string formatting.

### Important APIs, Types, And Functions

It uses `RocksDB.setPerfLevel`, `RocksDB.getPerfContext`, `PerfContext.reset`, JavaBeans `Introspector`, `PerfContext` getters, `getBlockReadCpuTime`, `getPostProcessTime`, and `PerfContext.toString`.

### Control Flow

Each test opens a DB with default and non-default CFs, sets a perf level that enables time and CPU counters, performs put/compact/get operations, retrieves the perf context, and asserts reset or getter behavior. The all-getters test reflects over bean properties to ensure every getter is linked and returns a `Long`.

### State And Persistence Behavior

The DB writes and compaction create enough native activity to populate counters. Perf context state is runtime per-thread diagnostic state, not persisted DB state.

### Dependencies And Integration Points

It integrates perf-level configuration, native perf context JNI getters, JavaBeans introspection, compaction, and platform assumptions. `getBlockReadCpuTime` is skipped on OpenBSD and Windows.

### Risks And Edge Cases

- Counter values can be platform-sensitive and workload-sensitive.
- Reflection can start testing new getters automatically when properties are added.
- CPU-time counters require OS support and correct perf-level selection.

### Test Signals

Signals are non-null context, all reflected getter results as `Long`, positive selected counters, and non-empty string output. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PerfContextTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PerfLevelTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PerfLevelTest.java

### Purpose

`PerfLevelTest` verifies valid and invalid `PerfLevel` enum handling through Java `RocksDB` APIs.

### Important APIs, Types, And Functions

It uses `RocksDB.setPerfLevel`, `RocksDB.getPerfLevel`, and `PerfLevel` enum constants including `UNINITIALIZED`, `OUT_OF_BOUNDS`, `DISABLE`, `ENABLE_COUNT`, `ENABLE_TIME_EXCEPT_FOR_MUTEX`, `ENABLE_TIME_AND_CPU_TIME_EXCEPT_FOR_MUTEX`, and `ENABLE_TIME`.

### Control Flow

The fixture opens a DB with two CF descriptors. One test asserts invalid sentinel levels throw `IllegalArgumentException`. The other iterates all valid levels, sets each one, and asserts the getter returns the same enum, then resets to `DISABLE`.

### State And Persistence Behavior

Perf level is runtime diagnostic state on the DB/thread context, not persisted database data.

### Dependencies And Integration Points

The test integrates enum ordinal/native value mapping, Java exception validation, and DB-level perf controls.

### Risks And Edge Cases

- Enum additions require updating valid-level coverage.
- Invalid sentinel constants must remain blocked at the Java boundary to avoid undefined native behavior.

### Test Signals

Signals are expected `IllegalArgumentException` for sentinels and exact round-trip for each valid perf level. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PerfLevelTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PlainTableConfigTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PlainTableConfigTest.java

### Purpose

`PlainTableConfigTest` validates Java getter/setter bindings for `PlainTableConfig` and confirms installing it changes an `Options` object's table factory.

### Important APIs, Types, And Functions

It covers `setKeySize`, `setBloomBitsPerKey`, `setHashTableRatio`, `setIndexSparseness`, `setHugePageTlbSize`, `setEncodingType`, `setFullScanMode`, `setStoreIndexInFile`, `Options.setTableFormatConfig`, and `Options.tableFactoryName`.

### Control Flow

Each scalar test constructs a config, sets one field, and asserts the getter. The integration test attaches the config to `Options` and expects `tableFactoryName()` to be `PlainTable`.

### State And Persistence Behavior

Only option/config native state is mutated. No DB is opened, so table layout persistence is not exercised.

### Dependencies And Integration Points

This integrates `PlainTableConfig`, `EncodingType`, native table factory selection, and RocksDB native library loading.

### Risks And Edge Cases

- Defaults are not checked; only setter round trips are covered.
- The table factory name string is a stable contract used by Java tests but supplied by native code.

### Test Signals

Signals are exact getter values and `PlainTable` table factory name. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PlainTableConfigTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PlatformRandomHelper.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PlatformRandomHelper.java

### Purpose

`PlatformRandomHelper` is a test utility that chooses a `Random` implementation appropriate for 32-bit versus 64-bit platforms.

### Important APIs, Types, And Functions

It exposes `isOs64Bit()` and `getPlatformSpecificRandomFactory()`. The nested `Random32Bit` extends `Random` and overrides `nextLong()` to return a non-negative 32-bit-sized value from `nextInt(Integer.MAX_VALUE)`.

### Control Flow

`isOs64Bit` checks `ProgramFiles(x86)` on Windows and `os.arch` containing `"64"` elsewhere. The factory returns normal `Random` on 64-bit systems and `Random32Bit` on 32-bit systems.

### State And Persistence Behavior

There is no persistent state. The utility affects randomized test inputs, particularly where native `size_t` or Java long values could exceed 32-bit platform limits.

### Dependencies And Integration Points

It depends on JVM system properties and environment variables and integrates with tests that need platform-bounded random values.

### Risks And Edge Cases

- Architecture detection is heuristic and may miss unusual JVM/OS names.
- `Random32Bit.nextLong()` changes the distribution and never returns negative values.
- The class predates newer Java unsigned helpers and exists mainly for JNI size compatibility.

### Test Signals

This file has no tests itself; consumers should verify generated values fit platform constraints. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PlatformRandomHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PutCFVariantsTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PutCFVariantsTest.java

### Purpose

`PutCFVariantsTest` parameterizes `RocksDB.put` overloads that target explicit column-family handles and verifies each variant writes readable bytes.

### Important APIs, Types, And Functions

It uses the `FunctionCFPut` functional interface, CF `put` overloads with and without `WriteOptions`, offset/length byte arrays, direct and heap `ByteBuffer`, `DBOptions`, `ColumnFamilyOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, and the `UInt64AddOperator` byte helpers from `MergeTest`.

### Control Flow

For each put overload, the test opens a DB with default and `"new_cf"` column families, writes little-endian `100` to `"cfkey"` in the non-default CF through the parameterized function, reads it back, creates a third CF, writes `200` through the normal CF put API, reads it, and asserts both values.

### State And Persistence Behavior

State is temporary DB data in non-default and dynamically created column families. The test verifies writes reach the intended CF and are not routed to default.

### Dependencies And Integration Points

It integrates parameterized JUnit, Java NIO buffers, offset/length JNI marshalling, column-family handles, and merge-operator-configured CF options.

### Risks And Edge Cases

- Offset/length overloads must ignore array padding.
- Heap/direct `ByteBuffer` position and limit handling must be exact.
- Temporary `WriteOptions` inside lambdas are not explicitly closed.

### Test Signals

All overloads must produce `100` in `"new_cf"` and `200` in the dynamically created CF. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PutCFVariantsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PutMultiplePartsTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PutMultiplePartsTest.java

### Purpose

`PutMultiplePartsTest` validates transaction APIs that accept multipart keys and values as `byte[][]`, concatenating the parts into one logical key and value.

### Important APIs, Types, And Functions

It uses `TransactionDB`, `Transaction.put`, `Transaction.putUntracked`, CF overloads of both methods, `syncWal`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, and helper methods `generateItems`, `generateItemsAsList`, `validateResults`, and `validateResultsCF`.

### Control Flow

Parameterized tests run with 2, 3, 250, and 20,000 parts. Each test opens a transaction DB, begins a transaction, generates key parts like `key0:`, `key1:`, and value parts like `value0`, `value1`, calls tracked or untracked multipart put with or without CF handle, commits, syncs WAL, closes, then reopens a normal DB and reads the concatenated key.

### State And Persistence Behavior

The transaction writes one logical key/value assembled by native RocksDB from many Java byte arrays. `syncWal` reinforces durability before validation after close/reopen.

### Dependencies And Integration Points

This integrates transaction DB, tracked/untracked write paths, CF routing, Java array-of-array marshalling, WAL sync, and reopen validation.

### Risks And Edge Cases

- Very large part counts stress JNI loops and native `SliceParts` construction.
- Key and value part counts must match; this test does not cover mismatch errors.
- CF validation reopens descriptors in non-standard order (`cfTest`, `default`) and relies on handle index 0 for `cfTest`.

### Test Signals

The read value for the concatenated key must equal the concatenation of all value parts for default and CF variants. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PutMultiplePartsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PutVariantsTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PutVariantsTest.java

### Purpose

`PutVariantsTest` parameterizes default-column-family `RocksDB.put` overloads and verifies each writes the intended key/value bytes.

### Important APIs, Types, And Functions

It uses `FunctionPut`, `RocksDB.put` byte-array overloads, `WriteOptions` overloads, offset/length overloads, direct and heap `ByteBuffer` overloads, and `MergeTest` byte helpers for little-endian longs.

### Control Flow

For each put function, the test opens a DB with `UInt64AddOperator` configured, writes long `100` under `"key"` through the parameterized function, reads the key, decodes the long, and asserts `100`.

### State And Persistence Behavior

The only persisted state is one key in the default CF. The merge operator is configured but not used by this test; it mainly provides a known binary value format shared with merge tests.

### Dependencies And Integration Points

This integrates Java overload dispatch, `WriteOptions`, offset/length JNI marshalling, and direct/heap ByteBuffer handling.

### Risks And Edge Cases

- Offset/length overloads must use only the intended slices of padded arrays.
- ByteBuffer overloads require correct flip/limit handling.
- Temporary write options in lambdas are not explicitly closed.

### Test Signals

Every overload must round-trip the binary long value `100`. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PutVariantsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/RateLimiterTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/RateLimiterTest.java

### Purpose

`RateLimiterTest` validates basic Java binding behavior for RocksDB's native rate limiter.

### Important APIs, Types, And Functions

It uses the `RateLimiter` constructor, constants `DEFAULT_REFILL_PERIOD_MICROS`, `DEFAULT_FAIRNESS`, `DEFAULT_MODE`, `DEFAULT_AUTOTUNE`, `getBytesPerSecond`, `setBytesPerSecond`, `getSingleBurstBytes`, `getTotalBytesThrough`, and `getTotalRequests`.

### Control Flow

Each test constructs a rate limiter in a try-with-resources block, checks a getter, and closes it. The autotune test enables autotune and only asserts a positive byte-per-second value.

### State And Persistence Behavior

Rate limiter counters are runtime native object state only. No DB is opened, and no throttled IO is performed, so total bytes/requests remain zero.

### Dependencies And Integration Points

This integrates native rate limiter construction, Java constants, basic counters, mutable rate setting, and native handle closing.

### Risks And Edge Cases

- Single burst bytes are expected to be `100` for a 1000 B/s rate with default refill period; native default math changes would break the test.
- Autotune is smoke-tested but not exercised under load.
- Counters are not validated after actual requests.

### Test Signals

Signals are positive rates, single burst bytes of `100`, zero initial counters, and successful autotune construction. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/RateLimiterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ReadOnlyTest.java -->
## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ReadOnlyTest.java

### Purpose

`ReadOnlyTest` verifies read-only RocksDB open modes, CF selection, mutation rejection, write-batch rejection, and WAL-file existence protection.

### Important APIs, Types, And Functions

It uses `RocksDB.openReadOnly` overloads, `RocksDB.open`, `DBOptions`, `Options`, `ColumnFamilyOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `WriteBatch`, `WriteOptions`, `put`, `delete`, `write`, and `Files.write`.

### Control Flow

The main test writes data in read-write mode, reopens read-only and reads it, then creates extra CFs, writes data to `new_cf2`, and checks that read-only opening with only default cannot see it while opening with `new_cf2` can. Mutation tests open read-only and expect `RocksDBException` from plain/CF `put`, plain/CF `delete`, and write-batch writes. The WAL test creates a fake `.log` file and opens read-only with `errorIfWalFileExists=true`, expecting failure.

### State And Persistence Behavior

Temporary DB state persists across read-write close and read-only reopen. Read-only handles must not mutate DB files. The WAL existence check protects users from opening a DB read-only when unapplied WALs might exist.

### Dependencies And Integration Points

This integrates read-only DB open paths, CF descriptor lists, write APIs, write batch APIs, filesystem WAL checks, and exception propagation.

### Risks And Edge Cases

- Read-only CF descriptors control visibility; missing CFs should not be accidentally read through default handles.
- Mutating APIs must fail even though Java exposes them on the `RocksDB` type.
- The WAL test writes a synthetic `999999.log`, depending on RocksDB's WAL filename detection.

### Test Signals

Signals are successful reads for visible data, `null` for absent/wrong CF data, and expected `RocksDBException` for all read-only mutations and WAL conflict. Static research only; no test command was run.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ReadOnlyTest.java -->
