# subset-b-008661 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksDB.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksDB.java

## Purpose
`RocksDB` is the primary Java facade for a native RocksDB database. It models a persistent ordered key/value map and exposes JNI-backed operations for opening databases, managing column families, reading and writing data, creating iterators and snapshots, querying properties, compacting data, flushing WAL/memtables, ingesting external SST files, tracing, secondary-instance catch-up, and destruction. The class extends `RocksObject`, so it owns an immutable native DB pointer until closed.

## Important APIs and Types
- Constants: `DEFAULT_COLUMN_FAMILY`, `NOT_FOUND`, and internal direct/heap ByteBuffer error text.
- Library lifecycle: `loadLibrary()`, `loadLibrary(List<String>)`, `rocksdbVersion()`, and nested `Version`.
- Open variants: default read-write, column-family read-write, read-only, read-only with WAL checking, and secondary open variants.
- Resource lifecycle: `closeE()`, `close()`, `isClosed()`, `disposeInternal(long)`, `makeDefaultColumnFamilyHandle()`.
- Column family APIs: `listColumnFamilies`, create/bulk-create/import, drop/bulk-drop, and `destroyColumnFamilyHandle`.
- Data APIs: overloaded `put`, `delete`, `singleDelete`, `deleteRange`, `merge`, `write`, `get`, `multiGetAsList`, `multiGetByteBuffers`, `keyExists`, and `keyMayExist`.
- Navigation APIs: `newIterator`, `newIterators`, `getSnapshot`, and `releaseSnapshot`.
- Admin/metadata APIs: `getProperty`, `getMapProperty`, long properties, approximate sizes, memtable stats, compaction methods, mutable option setters/getters, performance context, background-work controls, level metrics, `getName`, `getEnv`, flush/WAL methods, live files, WAL files, updates since, metadata, table properties, checksum, tracing, and `destroyDB`.
- Helper types: nested `CountAndSize`, nested `LiveFiles`, and nested `Version`.

## Control Flow
Library loading is guarded by an `AtomicReference<LibraryState>`. The winning thread transitions `NOT_LOADED -> LOADING`, loads optional compression libraries, loads `rocksdbjni`, initializes the static encoded native version, and publishes `LOADED`. Competing threads wait with a 10-second timeout and preserve interruption if interrupted.

Open methods normalize Java descriptors into `byte[][]` names and `long[]` option handles before invoking native open calls. Column-family opens require that the default column family is included. Returned native handles are converted into a `RocksDB` plus Java `ColumnFamilyHandle` wrappers, and owned handles are tracked in `ownedColumnFamilyHandles` so DB close can dispose them.

Most read/write overloads are thin normalization layers. They validate byte-array ranges with `CheckBounds` or local `checkBounds`, select default versus explicit column-family handles, select default versus explicit read/write options, and forward to native methods. ByteBuffer paths distinguish direct buffers from heap-backed buffers; mixed direct/indirect key/value pairs throw `RocksDBException`, and successful operations advance positions or adjust limits according to API contracts.

`closeE()` and `close()` first close tracked column-family handles, clear the list, then atomically flip inherited ownership and close the native database. `closeE()` propagates `RocksDBException`; `close()` suppresses it. Both call `disposeInternal()` in a finally path after native close.

## State and Persistence Behavior
Persistent state lives in the native RocksDB database files at the path passed to open. Java state mainly preserves native handles, default read options, an options reference to prevent premature GC, the default column-family handle, and a list of owned column-family handles. Writes, deletes, merges, flushes, WAL sync, compactions, file deletions, and external file ingestion mutate native persistent state. Snapshots expose stable sequence-numbered views but are released by the DB, not by the `Snapshot` object itself. `getLiveFiles`, `getSortedWalFiles`, `getUpdatesSince`, and metadata APIs expose persistence surfaces used by backup, replication, and inspection code.

## Dependencies and Integration Points
The class depends on a large set of RocksJNI wrappers: `Options`, `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `ReadOptions`, `WriteOptions`, `WriteBatch`, `WriteBatchWithIndex`, `Range`, `Slice`, `Status`, `ByteBufferGetStatus`, `KeyMayExist`, `PerfLevel`, `PerfContext`, `FlushOptions`, metadata classes, trace writers, and many option classes. It integrates with native code through an extensive private native method table, with `NativeLibraryLoader` and `Environment` for library loading, and with Java collections and `ByteBuffer` for data movement.

## Risks
- Native handle ownership is central. Closing a DB before closing dependent iterators, snapshots, options, or column-family handles can produce native misuse.
- Several ByteBuffer methods rely on assertions for directness/null checks, so production JVMs with assertions disabled may pass bad buffers into JNI unless native code defends itself.
- `singleDelete` is explicitly experimental and has strict write-history preconditions; misuse can produce undefined data behavior.
- Multi-key APIs protect some size mismatches to avoid segmentation faults; any new overload must preserve those checks.
- `get` returning `NOT_FOUND` and possible native negative statuses is documented as an API wart.
- `getLiveFiles(boolean)` returns null if native returns null and encodes manifest size in the final string, so callers and native changes must preserve that convention.
- `startTrace` transfers trace-writer ownership to C++; missing the `disOwnNativeHandle()` pattern would double free.

## Test Signals
Strong tests would cover concurrent `loadLibrary`, all open variants including missing default CF rejection, close idempotence, column-family ownership cleanup, byte-array range validation, direct/heap ByteBuffer behavior and position/limit changes, multi-get size mismatch errors, `keyMayExist` holder encodings, snapshot release behavior, live-file parsing, mutable option round trips, and JNI exception propagation. Integration tests need real RocksDB instances to validate persistence, WAL/flush behavior, compaction/file metadata, secondary catch-up, and external SST ingestion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksDB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksDBException.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksDBException.java

## Purpose
`RocksDBException` is the checked exception used by RocksJNI APIs to report failures from native RocksDB operations. It carries the Java exception message and, when available, the native `Status` object that explains the RocksDB error code/subcode/state.

## Important APIs and Types
- Extends `Exception`.
- Stores nullable `Status status`.
- Constructors accept a plain message, message plus `Status`, or a `Status` alone.
- `getStatus()` exposes the native status wrapper or null.

## Control Flow
Message-only construction delegates to the message/status constructor with `null`. Status-only construction derives the exception message from `status.getState()` when present, otherwise from `status.getCodeString()`, then stores the status. API callers catch `RocksDBException` from higher-level wrappers such as `RocksDB`, iterators, environments, and managers.

## State and Persistence Behavior
The class has no persistence behavior. Its only state is immutable after construction: the inherited exception message/stack trace and the stored `Status`. It does not own or close native resources.

## Dependencies and Integration Points
It depends on `org.rocksdb.Status`. It is the shared error contract for JNI methods declared across the package, allowing callers to inspect structured status when native code provided one.

## Risks
Status is annotated only by comment as nullable, so callers must check for null. The status-only constructor assumes the input status is non-null. If native bindings construct exceptions inconsistently, downstream code may see a generic message without structured status.

## Test Signals
Tests should verify message derivation from status state versus code string, null status behavior for message constructors, and that JNI paths preserve `Status` metadata when throwing.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksDBException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksEnv.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksEnv.java

## Purpose
`RocksEnv` is an `Env` wrapper for a native RocksDB environment handle. It represents operating-system services such as filesystem access and is documented as thread-safe for concurrent use.

## Important APIs and Types
- Extends `Env`.
- Package-private constructor `RocksEnv(long handle)`.
- Overrides `disposeInternal(long)` to call `disposeInternalJni(long)`.

## Control Flow
Instances are created internally when a native environment handle needs a Java wrapper, notably from `RocksDB.getEnv()` when the DB environment is not the default. The constructor passes the handle to `Env`. Disposal delegates to JNI, although callers creating wrappers for non-owned handles typically disown them.

## State and Persistence Behavior
The Java object stores the inherited native environment handle. It does not itself persist data, but the native environment controls how RocksDB accesses persistent files. The constructor documentation states ownership remains with the caller, so disposing a wrapper created for a borrowed handle should be a no-op after ownership is disowned.

## Dependencies and Integration Points
It depends on `Env` and native JNI implementation. It integrates with `RocksDB.getEnv()`, which returns `Env.getDefault()` for the default handle or a disowned `RocksEnv` for other DB environments.

## Risks
Ownership semantics are subtle. If a borrowed environment wrapper is not disowned by its creator, Java close could free an environment still owned by native DB/options code. Conversely, owned environment subclasses must still dispose correctly.

## Test Signals
Tests should cover `RocksDB.getEnv()` returning the singleton default for default DBs, returning a disowned wrapper for custom environments, and safe close behavior for borrowed handles.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksEnv.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksIterator.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksIterator.java

## Purpose
`RocksIterator` is the concrete DB iterator for key/value traversal over a RocksDB column family or DB. It extends `AbstractRocksIterator<RocksDB>` and supplies key/value access plus JNI implementations for seek, movement, refresh, validity, status, and disposal.

## Important APIs and Types
- Constructors are protected and bind a parent `RocksDB` plus native iterator handle.
- Key access: `key()`, `key(byte[])`, `key(byte[], int, int)`, `key(ByteBuffer)`.
- Value access: `value()`, `value(byte[])`, `value(byte[], int, int)`, `value(ByteBuffer)`.
- Native iterator operations override abstract hooks: validity, seek first/last, next/prev, refresh, seek/seekForPrev for arrays and direct buffers, status, and dispose.

## Control Flow
High-level navigation methods are inherited from `AbstractRocksIterator`, which calls the overridden native hooks. `key` and `value` methods assert handle ownership, validate array bounds where offsets are exposed, then invoke JNI. ByteBuffer variants choose direct JNI access for direct buffers and array JNI access for heap buffers, then reduce the buffer limit to the actual returned length or current limit, whichever is smaller.

## State and Persistence Behavior
The iterator owns a native iterator handle and references its parent DB to keep the DB alive while the iterator exists. It does not mutate persistent data; it reads the DB state selected by its creation/read options/snapshot. `refresh` can retarget the native iterator to latest DB state or a supplied snapshot and invalidates positioning until the caller seeks again.

## Dependencies and Integration Points
It depends on `AbstractRocksIterator`, `RocksDB`, `Snapshot`, `RocksDBException`, `ByteBuffer`, and `BufferUtil.CheckBounds`. Instances are produced by `RocksDB.newIterator` and `RocksDB.newIterators`.

## Risks
The public docs require `isValid()` before reading key/value, but Java methods rely on native enforcement. Returned byte arrays copy from native storage, while buffer reads can be partial if the buffer is too small. The ByteBuffer methods set limits rather than advancing positions, so caller expectations must match the contract. Thread safety allows concurrent const methods only; navigation requires external synchronization.

## Test Signals
Tests should verify invalid iterator behavior, key/value copy and partial-buffer lengths, offset validation, direct and heap ByteBuffer paths, position/limit updates, refresh invalidation, status exception propagation, and closing iterators before DB close.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksIteratorInterface.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksIteratorInterface.java

## Purpose
`RocksIteratorInterface` defines the common traversal contract for iterators over RocksDB-backed sources such as DBs and write batches. It isolates navigation, validity, status checking, and refresh behavior from concrete iterator implementations.

## Important APIs and Types
- Positioning: `seekToFirst()`, `seekToLast()`, `seek(byte[])`, `seekForPrev(byte[])`, `seek(ByteBuffer)`, `seekForPrev(ByteBuffer)`.
- Movement: `next()`, `prev()`.
- State/error: `isValid()`, `status()`.
- Refresh: `refresh()` and `refresh(Snapshot)`.

## Control Flow
Implementations maintain a current cursor. Seek methods establish a valid or invalid position based on target and source contents. `next` and `prev` require a valid iterator and move forward/backward. `status` reports deferred native errors. Refresh changes the DB state the iterator reads and invalidates the cursor until a future seek.

## State and Persistence Behavior
The interface itself has no state. It describes read-only cursor state over persistent or batch-backed data. Snapshot refresh pins a stable DB state for future reads.

## Dependencies and Integration Points
It depends on `ByteBuffer`, `Snapshot`, and `RocksDBException`. `AbstractRocksIterator`, `RocksIterator`, and write-batch iterator implementations are expected consumers.

## Risks
The interface documents direct-buffer support for ByteBuffer seek methods, but enforcement is implementation-specific. Callers must observe `isValid()` preconditions before movement or key/value access on concrete iterators. Refresh support may vary and can throw when unsupported.

## Test Signals
Contract tests should exercise seek boundary cases, forward/backward traversal, invalid movement, status error propagation, refresh invalidation, and ByteBuffer directness requirements across every implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksIteratorInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksMemEnv.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksMemEnv.java

## Purpose
`RocksMemEnv` is an in-memory `Env` implementation. It stores file data in memory while delegating non-file-storage tasks to a supplied base environment.

## Important APIs and Types
- Extends `Env`.
- Public constructor `RocksMemEnv(Env baseEnv)`.
- Native factory `createMemEnv(long baseEnvHandle)`.
- Overrides disposal through `disposeInternalJni(long)`.

## Control Flow
Construction reads `baseEnv.nativeHandle_` and passes the returned native mem-env handle to `Env`. When closed, disposal delegates to JNI. The base environment must remain alive while the mem-env is in use.

## State and Persistence Behavior
The native mem-env handle owns an in-memory filesystem. Data stored through this environment is volatile and process-local unless native implementation provides otherwise. Since it delegates non-storage tasks, behavior also depends on the base environment lifetime and configuration.

## Dependencies and Integration Points
It depends on `Env` and native RocksDB mem-env support. It can be used through DB/options environment settings to run RocksDB on an in-memory file abstraction.

## Risks
The constructor directly accesses the base native handle and does not retain an explicit Java reference, so callers must keep `baseEnv` live. Closing the base environment too early can invalidate the native mem-env. The TODO indicates naming may be legacy.

## Test Signals
Tests should validate DB creation on `RocksMemEnv`, absence of durable files, cleanup on close, base-env lifetime behavior, and error handling when the base environment is invalid.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksMemEnv.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksMutableObject.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksMutableObject.java

## Purpose
`RocksMutableObject` is a base class for native RocksDB wrappers whose native pointer can change after construction. It is deliberately discouraged except when mutability is required because it adds synchronization and ownership complexity.

## Important APIs and Types
- Extends `AbstractNativeReference`.
- Mutable fields: `nativeHandle_` and `owningHandle_`.
- Constructors for empty and owned native handle states.
- Handle mutation: `resetNativeHandle(long, boolean)` and `setNativeHandle(long, boolean)`.
- Lifecycle: synchronized `isOwningHandle()`, `getNativeHandle()`, `close()`, `disposeInternal()`, abstract `disposeInternal(long)`.

## Control Flow
`resetNativeHandle` closes the current owned handle, then installs a new handle and ownership flag. `setNativeHandle` installs without closing first. `close` checks ownership, disposes the current native handle, then clears ownership and sets the handle to zero. All handle operations are synchronized to serialize mutation and close.

## State and Persistence Behavior
The class stores only a pointer and an ownership flag. Persistence behavior belongs to the native object being wrapped. Closing can free native persistent or transient resources depending on subclass implementation.

## Dependencies and Integration Points
It depends on `AbstractNativeReference`. Mutable native wrappers such as slice-like or reusable option objects can extend it when immutable `RocksObject` is insufficient.

## Risks
Calling `setNativeHandle` over an owned live handle leaks unless `resetNativeHandle` is used. `getNativeHandle` relies on an assertion to reject zero handles, so production code may still pass zero to JNI if assertions are disabled and callers misuse it. Subclasses must implement correct native disposal for the dynamic handle type.

## Test Signals
Tests should cover reset closing previous handles, set without close when intentionally borrowed, idempotent close, ownership false close no-op, synchronization under concurrent reset/close, and subclass disposal being called exactly once per owned handle.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksMutableObject.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksObject.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksObject.java

## Purpose
`RocksObject` is the preferred base class for Java wrappers around immutable native RocksDB pointers. It provides stable handle storage and delegates native deletion to subclasses.

## Important APIs and Types
- Extends `AbstractImmutableNativeReference`.
- Protected final `nativeHandle_`.
- Constructor marks the wrapper as owning by default.
- `disposeInternal()` delegates to abstract `disposeInternal(long)`.
- `getNativeHandle()` exposes the pointer.

## Control Flow
Subclasses call the constructor with a native pointer. Close behavior is inherited from `AbstractImmutableNativeReference`; when disposal is needed, it invokes the no-arg `disposeInternal`, which passes the immutable handle to subclass-specific native deletion code.

## State and Persistence Behavior
The class stores a stable native pointer and inherited ownership state. It does not persist data itself, but many subclasses wrap persistent resources such as databases, column-family handles, snapshots, options, envs, and managers.

## Dependencies and Integration Points
It depends on `AbstractImmutableNativeReference` and is used broadly across RocksJNI as the base for native-backed objects. `RocksDB` extends it directly.

## Risks
The public `getNativeHandle()` can expose raw native pointers to package consumers or external callers, making lifecycle misuse possible. Subclasses must correctly disown borrowed handles to prevent double-free and must implement disposal for the exact native type.

## Test Signals
Tests should focus on subclass lifecycle: owned close calls native dispose once, disowned handles do not dispose, immutable handle remains stable, and native handle exposure matches expected pointer values.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksObject.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SanityLevel.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SanityLevel.java

## Purpose
`SanityLevel` is an enum for compatibility or validation strictness. It maps Java enum constants to byte values expected by native RocksDB APIs.

## Important APIs and Types
- Values: `NONE(0x0)`, `LOOSELY_COMPATIBLE(0x1)`, `EXACT_MATCH(0xFF)`.
- Package-private `getValue()` returns the native byte.
- Package-private `fromValue(byte)` decodes native bytes.

## Control Flow
`fromValue` scans all enum values and returns the first byte match. Unknown bytes throw `IllegalArgumentException` with the numeric byte value in the message.

## State and Persistence Behavior
Enum instances are static and immutable. The byte values may be persisted indirectly if passed into native options or metadata compatibility checks, but this class stores no external state.

## Dependencies and Integration Points
It has no external dependencies beyond Java enum mechanics. It integrates with option or import/export APIs that need sanity-level conversion between Java and native code.

## Risks
`0xFF` is stored in a signed Java byte as `-1`; comparisons remain correct, but diagnostics may print a signed value. Adding native sanity levels requires updating both enum constants and `fromValue` expectations.

## Test Signals
Tests should verify all byte mappings, exact decoding of `0xFF`, and exception behavior for unknown bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SanityLevel.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SizeApproximationFlag.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SizeApproximationFlag.java

## Purpose
`SizeApproximationFlag` defines bit flags for `RocksDB.getApproximateSizes` to select whether size estimates include memtables, SST files, blob files, or no extra sources.

## Important APIs and Types
- Values: `NONE(0x0)`, `INCLUDE_MEMTABLES(0x1)`, `INCLUDE_FILES(0x2)`, `INCLUDE_BLOB_FILES(0x4)`.
- Package-private `getValue()` returns the native byte bit.

## Control Flow
The enum itself has no branching beyond construction. `RocksDB.getApproximateSizes` ORs each flag's byte value into a single mask before invoking JNI.

## State and Persistence Behavior
Flags are immutable. They do not persist state but influence native estimation over persisted files, blob files, and memory-resident memtables.

## Dependencies and Integration Points
It imports `java.util.List` only for Javadoc linking to `RocksDB.getApproximateSizes(ColumnFamilyHandle, List, SizeApproximationFlag...)`. Native code must interpret the same bit layout.

## Risks
Flag values are package-private, so only package code can encode them. Any native bit-layout change must be mirrored here. Combining `NONE` with other flags is allowed and harmless because it contributes zero.

## Test Signals
Tests should verify masks generated by single and combined flags and JNI behavior for memtable/file/blob inclusion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SizeApproximationFlag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SkipListMemTableConfig.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SkipListMemTableConfig.java

## Purpose
`SkipListMemTableConfig` configures RocksDB's skip-list memtable representation, specifically the seek lookahead optimization.

## Important APIs and Types
- Extends `MemTableConfig`.
- Constant `DEFAULT_LOOKAHEAD = 0`.
- Constructor initializes `lookahead_`.
- Fluent setter `setLookahead(long)`.
- Getter `lookahead()`.
- Overrides `newMemTableFactoryHandle()` to call native `newMemTableFactoryHandle0(long)`.

## Control Flow
Users configure the object by calling `setLookahead`, then options code calls `newMemTableFactoryHandle()` to allocate the native memtable factory with the configured value. Native code may throw `IllegalArgumentException` for invalid lookahead values.

## State and Persistence Behavior
The only Java state is `lookahead_`. It affects future native memtable factory creation and therefore runtime write-path/read-seek behavior inside RocksDB, but it does not itself persist data. Once applied to DB options, the native factory participates in in-memory write buffering.

## Dependencies and Integration Points
It depends on `MemTableConfig` and JNI. It integrates with column-family/options configuration that accepts memtable factories.

## Risks
No Java-side validation is performed on `lookahead`; invalid values are deferred to native code. Because the setter is mutable and unsynchronized, callers should finish configuration before sharing it. The optimization is workload-specific and can hurt if configured blindly.

## Test Signals
Tests should verify default value, fluent setter return identity, getter accuracy, native factory creation for valid values, and native rejection for invalid values.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SkipListMemTableConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Slice.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Slice.java

## Purpose
`Slice` is the byte-array-backed concrete `AbstractSlice<byte[]>`. It wraps native RocksDB slice memory and is optimized for small keys and values; larger data may use `DirectSlice`.

## Important APIs and Types
- Extends `AbstractSlice<byte[]>`.
- Tracks `cleared` and `internalBufferOffset`.
- Private no-arg constructor for JNI-created Java objects without an initial native object.
- Package constructors for native handles with borrowed or explicit ownership.
- Public constructors from `String`, `byte[]`, and `byte[]` plus offset.
- Overrides `clear()`, `removePrefix(int)`, `disposeInternal()`, and native `data0(long)`.

## Control Flow
Public constructors allocate a native slice from copied Java data. `clear()` calls native clear with whether an internal buffer still needs freeing, then marks the slice cleared. `removePrefix` adjusts the native slice and increments `internalBufferOffset` so disposal knows where the original internal allocation begins. `disposeInternal` frees buffered data if not already cleared, then disposes the native slice pointer through the superclass path.

## State and Persistence Behavior
The Java object owns or borrows a native slice pointer and may own an internal native buffer copied from Java data. It is transient memory, not persisted storage. If used by RocksDB instances or options, its lifetime must outlast native consumers.

## Dependencies and Integration Points
It depends on `AbstractSlice`, native slice allocation/free functions, and RocksDB APIs that accept `Slice` or `Range` boundaries. It integrates with `RocksDB.toRangeSliceHandles`, approximate-size queries, table-property range queries, and suggested compaction ranges.

## Risks
Memory ownership is delicate. Disposing while a DB still references a slice is documented as undefined behavior. `removePrefix` changes disposal offset and must stay synchronized with native allocation semantics. The private JNI constructor relies on external native setup and disowned ownership semantics.

## Test Signals
Tests should cover data round trips from string/byte arrays, offset constructor behavior, `removePrefix` data and disposal correctness, idempotent `clear`, borrowed-handle no double-free behavior, and lifecycle with range-consuming DB APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Slice.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Snapshot.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Snapshot.java

## Purpose
`Snapshot` wraps a native RocksDB snapshot handle, representing a stable database sequence view for reads and iterators.

## Important APIs and Types
- Extends `RocksObject`.
- Package-private constructor accepts a native snapshot handle and immediately disowns it.
- `getSequenceNumber()` returns the snapshot sequence number.
- `disposeInternal(long)` intentionally does nothing.

## Control Flow
`RocksDB.getSnapshot()` creates `Snapshot` when native returns a non-zero handle. The constructor calls `disOwnNativeHandle()` because the DB, not the Java snapshot, releases the native snapshot. `RocksDB.releaseSnapshot(snapshot)` is the actual release path.

## State and Persistence Behavior
The snapshot handle points to native DB state pinned at a sequence number. It does not own persistent data, but it can keep older data versions/files alive until released by the DB. Java close of `Snapshot` does not release the native snapshot.

## Dependencies and Integration Points
It depends on `RocksObject` and JNI. It integrates with `ReadOptions`/iterator refresh flows that read under a snapshot and with `RocksDB.releaseSnapshot`.

## Risks
The no-op `disposeInternal` means forgetting to call `RocksDB.releaseSnapshot` leaks native snapshot state even if the Java object is closed/GC'd. Using a snapshot after release is forbidden by `RocksDB.releaseSnapshot` documentation. DB lifetime must dominate snapshot use.

## Test Signals
Tests should verify sequence number retrieval, disowned close no-op behavior, release through DB, repeated release/null behavior at DB API level, and resource retention/release effects on file cleanup where practical.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Snapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileManager.java -->
# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileManager.java

## Purpose
`SstFileManager` tracks SST files across one or more RocksDB instances and controls deletion rate and disk-space related write throttling/failures. It is final and documented as thread-safe.

## Important APIs and Types
- Extends `RocksObject`.
- Defaults: delete rate, delete existing trash, max trash/DB ratio, and max delete chunk bytes.
- Constructor chain accepts `Env`, optional `Logger`, deletion rate, max trash ratio, and delete chunk size.
- Space controls: `setMaxAllowedSpaceUsage`, `setCompactionBufferSize`, `isMaxAllowedSpaceReached`, `isMaxAllowedSpaceReachedIncludingCompactions`.
- Tracking: `getTotalSize`, `getTrackedFiles`.
- Deletion throttling: `getDeleteRateBytesPerSecond`, `setDeleteRateBytesPerSecond`, `getMaxTrashDBRatio`, `setMaxTrashDBRatio`.
- Disposal delegates to `disposeInternalJni`.

## Control Flow
Constructors progressively fill defaults and end at a native `newSstFileManager` call using the environment handle, optional logger handle or zero, rate, ratio, and chunk size. Public methods pass the manager native handle to JNI setters/getters. The manager can then be supplied through RocksDB options outside this file to track SST files and enforce limits.

## State and Persistence Behavior
Java state is the native manager pointer. Native state tracks SST file paths/sizes, trash deletion scheduling, deletion rate limiting, max allowed space, and compaction buffer reservation. It influences persistence by delaying or chunking file deletion and by causing writes to fail when tracked SST usage exceeds configured limits.

## Dependencies and Integration Points
It depends on `Env`, `Logger`, `RocksDBException`, `Map`, and native RocksDB SstFileManager. It integrates with DB options that accept an SstFileManager and with filesystem behavior supplied by `Env`.

## Risks
The constant name `MAX_TRASH_DB_RATION_DEFAULT` appears misspelled but is part of the public API. Incorrect `Env` or `Logger` lifetimes can invalidate native construction/use. Space-limit APIs can intentionally make RocksDB writes fail, so operational tests must distinguish expected limit failures from corruption. `getTrackedFiles` returns native-derived paths and sizes whose consistency depends on active DB tracking.

## Test Signals
Tests should cover constructor overload default propagation, invalid native argument handling, total size/tracked file updates after DB writes/compactions, delete-rate setter/getter round trips, max-trash-ratio behavior, max-space-reached behavior including compactions, and thread-safe concurrent getters/setters.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileManager.java -->
