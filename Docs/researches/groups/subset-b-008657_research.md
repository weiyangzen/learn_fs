# Group Research: subset-b-008657

Work item `subset-b-008657` covers 31 RocksDB Java API/JNI wrapper files under `sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb`. Each section preserves the source path in its title and is delimited for deterministic splitting into the required source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractImmutableNativeReference.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractImmutableNativeReference.java

- **Purpose:** Thread-safe ownership base for immutable native references. It extends `AbstractNativeReference` and centralizes close-time release for Java objects that may or may not own a native C++ RocksDB pointer.
- **Important APIs/types/functions:** `owningHandle_` is an `AtomicBoolean`; constructor records ownership; `isOwningHandle()` exposes current ownership; `disOwnNativeHandle()` transfers/revokes deletion responsibility; `close()` atomically transitions owner to non-owner and calls subclass `disposeInternal()`.
- **Control flow:** Subclasses construct with an initial owner flag. Close is idempotent because only the successful `compareAndSet(true, false)` path releases native resources. Ownership transfer uses `disOwnNativeHandle()` before another wrapper or C++ owner is expected to delete the object.
- **State and persistence behavior:** State is in-memory Java ownership state plus the native object lifetime behind subclasses. There is no durable persistence, but incorrect ownership affects native memory persistence/leakage across JVM execution.
- **Dependencies:** Depends on `AbstractNativeReference` and `java.util.concurrent.atomic.AtomicBoolean`; release work is delegated to subclass JNI disposal.
- **Integration points:** Used by RocksDB Java wrappers needing immutable native handle ownership semantics, especially callback/native resource objects where double-free must be avoided.
- **Risks:** Misusing `disOwnNativeHandle()` leaks native memory; failing to call `close()` keeps native C++ memory live. Post-close method calls on subclasses are undefined by the base contract. Thread safety only protects the ownership flag, not subclass state.
- **Test signals:** Unit tests should exercise double close, ownership transfer before close, subclass `disposeInternal()` invocation exactly once, and try-with-resources behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractImmutableNativeReference.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractMutableOptions.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractMutableOptions.java

- **Purpose:** Shared Java representation and builder/parser for RocksDB mutable option strings. It is named abstract for the C++ concept, but the Java class is concrete with a protected constructor for subclass use.
- **Important APIs/types/functions:** Constants define `;`, `=`, and `:` separators. `keys` and `values` store option string entries. `toString()` serializes key/value pairs. Nested `AbstractMutableOptionsBuilder<T,U,K>` manages typed `MutableOptionValue<?>` entries keyed by `MutableOptionKey`, unknown parsed entries, and typed setters/getters for double, long, int, boolean, int array, string, and enum.
- **Control flow:** Builders collect options in insertion order, validate each setter against the key's declared `ValueType`, and `build()` emits parallel key/value arrays. `fromParsed()` walks `OptionString.Entry` objects, rejects empty keys and malformed values, delegates to `fromOptionString()`, optionally records unknown keys, and converts known strings into typed `MutableOptionValue` instances.
- **State and persistence behavior:** The final object persists option state as arrays that serialize back to RocksDB's mutable option string format. Builder state is transient and preserves insertion order through `LinkedHashMap`; unknown parsed options are retained for callers but not included in `build()`.
- **Dependencies:** Depends on `MutableOptionKey`, `MutableOptionValue`, `OptionString`, `CompressionType`, `PrepopulateBlobCache`, Java collections, and number parsing.
- **Integration points:** Used by mutable DB/column-family option classes and by `RocksDB#setOptions(...)` style APIs that consume RocksDB option strings. It bridges parsed hierarchical option strings with Java's typed mutable-option builders.
- **Risks:** `getKeys()`/`getValues()` return internal arrays. Boolean parsing uses Java's permissive `Boolean.parseBoolean`, so misspellings silently become false. Error text for unknown keys prints `null` instead of the actual key. Only selected enum names are parsed; adding new enum-valued options requires updating the parser. Numeric strings like `9.00` can round to integral values, which is intentional but can hide formatting errors.
- **Test signals:** Round-trip serialization, parser acceptance of int/long values written as whole-number doubles, rejection of wrong value types, unknown-key behavior with both strict and ignore modes, enum parsing for compression and prepopulate blob cache, and int-array separator handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractMutableOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractNativeReference.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractNativeReference.java

- **Purpose:** Root contract for Java RocksDB objects that hold native C++ pointers. It documents explicit resource release and replaces any expectation of finalizer-based cleanup.
- **Important APIs/types/functions:** Implements `AutoCloseable`; declares protected `isOwningHandle()` and abstract `close()`.
- **Control flow:** There is no executable release implementation here. Subclasses define ownership checks and close behavior, usually by invoking JNI disposal when they own the native handle.
- **State and persistence behavior:** The class itself stores no state. Its contract governs native pointer lifetime, which is outside Java GC visibility and can persist until explicit close.
- **Dependencies:** Only Java `AutoCloseable`; subclasses such as `RocksObject`, `RocksMutableObject`, and callback objects implement the actual handle storage/disposal.
- **Integration points:** Base type for most RocksDB Java wrappers and try-with-resources use throughout the Java API.
- **Risks:** Forgetting to close resources leaks native memory/file handles. Calling methods after close has undefined behavior. The javadoc references finalization context but intentionally does not provide finalizer cleanup.
- **Test signals:** Static/API tests should verify wrappers implement `AutoCloseable`, document explicit close requirements, and throw or assert appropriately when methods are used after disposal in concrete subclasses.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractNativeReference.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractRocksIterator.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractRocksIterator.java

- **Purpose:** Shared base implementation for RocksDB Java iterators backed by native iterator handles, parameterized by the parent `RocksObject` that created the iterator.
- **Important APIs/types/functions:** Implements `RocksIteratorInterface`; stores `parent_`; exposes `isValid`, seek operations for `byte[]` and `ByteBuffer`, `next`, `prev`, `refresh`, `refresh(Snapshot)`, and `status`. Declares abstract native hook methods such as `seek0`, `seekDirect0`, `refresh0`, and `status0`.
- **Control flow:** Public iterator methods assert ownership, convert Java inputs to handle/offset/length arguments, and dispatch to subclass JNI methods. Direct `ByteBuffer` paths pass the buffer directly; heap-backed paths pass the backing array with adjusted offset. Both ByteBuffer seek methods advance the buffer position to its limit after use. Disposal releases the iterator only if the parent still owns its native handle.
- **State and persistence behavior:** Iterator position and status live in the native iterator. Java keeps a strong parent reference to influence GC/release ordering and avoid freeing the parent before iterator cleanup.
- **Dependencies:** Depends on `RocksObject`, `RocksIteratorInterface`, `Snapshot`, `RocksDBException`, and `java.nio.ByteBuffer`; concrete iterator subclasses provide JNI implementations.
- **Integration points:** Used by database, column-family, transaction, and snapshot iterator wrappers. Parent ownership connects iterator lifetime to database/transaction lifetime.
- **Risks:** Assertions are not runtime validation unless enabled. Heap ByteBuffer paths call `array()` and fail for read-only/non-array buffers. If parent is closed first, iterator disposal skips native release to avoid double-free, which can make lifetime bugs hard to diagnose. The class documents const/non-const thread-safety constraints but does not enforce synchronization.
- **Test signals:** Iterator seek/next/prev/status behavior, direct and heap ByteBuffer seeks with position advancement, refresh with and without snapshots, parent-close-before-iterator-close scenarios, and JNI exception propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractRocksIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractSlice.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractSlice.java

- **Purpose:** Generic base for RocksDB slice wrappers used to expose efficient key/value bytes to Java. Public concrete variants decide whether access is through byte arrays or direct buffers.
- **Important APIs/types/functions:** Constructors support new mutable objects and existing native handles. `data()` delegates to subclass `data0(long)`. Abstract mutators are `removePrefix(int)` and `clear()`. Common APIs include `size`, `empty`, `toString(boolean hex)`, `compare`, `equals`, `hashCode`, and `startsWith`. Native helpers include `createNewSliceFromString`, `size0`, `toString0`, `compare0`, and `disposeInternalJni`.
- **Control flow:** Accessors fetch the current native handle from `RocksMutableObject`. Comparison delegates to native compare only when both slices own handles; if neither owns a handle they compare equal, otherwise the owning slice sorts after/before the non-owner according to local logic. Disposal always calls JNI deletion for the owned slice handle.
- **State and persistence behavior:** Slice content is native memory, often borrowed from comparator/callback contexts. Java equality/hash depend on `toString()` content and ownership fallback behavior. No durable data is written, but slice lifetime is tightly tied to RocksDB native callbacks and comparator objects.
- **Dependencies:** Depends on `RocksMutableObject` and native slice JNI. Referenced by comparators, compaction filters, trace writers, and direct slice variants.
- **Integration points:** Used in Java comparator callbacks and RocksDB callback bridges where native C++ constructs Java slice objects. Also underpins `Slice` and `DirectSlice`.
- **Risks:** Comparing two non-owning slices returns equality without inspecting data. `hashCode()` uses `toString()`, which can be expensive or encoding-sensitive. Closing a slice while RocksDB still references it is documented as undefined behavior. Null checking for compare uses `assert`, not always-on validation.
- **Test signals:** Slice construction from strings, data access for concrete subclasses, prefix removal/clear, compare/equality/startsWith across owned and non-owned handles, hex string output, and close timing with callback-owned slices.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractSlice.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractTableFilter.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractTableFilter.java

- **Purpose:** Base Java callback wrapper for RocksDB table filters.
- **Important APIs/types/functions:** Extends `RocksCallbackObject` and implements `TableFilter`. Constructor delegates to the callback base. `initializeNative(...)` creates the native table-filter callback object via `createNewTableFilter()`.
- **Control flow:** Instantiation calls into `RocksCallbackObject`, which invokes `initializeNative`; the native side later calls the `TableFilter` methods implemented by subclasses.
- **State and persistence behavior:** The Java object owns a native callback handle managed by `RocksCallbackObject`. It keeps no Java-side table state.
- **Dependencies:** Depends on `RocksCallbackObject`, `TableFilter`, and JNI implementation of `createNewTableFilter`.
- **Integration points:** Plugs Java filtering logic into native RocksDB table-processing paths.
- **Risks:** Subclasses must remain alive as long as native RocksDB may callback. Disposal order is important; premature close can leave native code with an invalid callback target.
- **Test signals:** Creating a concrete filter, verifying native handle allocation, exercising callback invocation from table-reader code, and closing while no database references remain.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractTableFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractTraceWriter.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractTraceWriter.java

- **Purpose:** Base callback bridge for Java trace writers used by RocksDB tracing.
- **Important APIs/types/functions:** Extends `RocksCallbackObject` and implements `TraceWriter`. `initializeNative()` calls `createNewTraceWriter()`. Private JNI callback proxies `writeProxy(long sliceHandle)` and `closeWriterProxy()` translate Java `RocksDBException` into packed status shorts. `statusToShort` packs `Status.Code` and `Status.SubCode`.
- **Control flow:** Native code calls the private proxy methods. `writeProxy` wraps the borrowed native slice handle in a non-owning `Slice`, calls user `write(Slice)`, and returns OK or the exception status. `closeWriterProxy` calls `closeWriter()` and performs the same status conversion. Null status/code values fall back to `IOError`/`None`.
- **State and persistence behavior:** Trace persistence is delegated to subclass `write`/`closeWriter` implementations; this class only manages native callback bridging and status encoding.
- **Dependencies:** Depends on `RocksCallbackObject`, `TraceWriter`, `Slice`, `Status`, and `RocksDBException`; native code must decode the short in the same high-byte/low-byte layout.
- **Integration points:** Used by RocksDB tracing APIs to let Java write trace records to custom sinks while native code receives RocksDB-style status results.
- **Risks:** The slice handle is borrowed; Java code must not retain it beyond callback lifetime. Status packing is only two bytes and must stay aligned with enum values. Unexpected unchecked exceptions are not caught and can cross JNI poorly.
- **Test signals:** Successful write/close callbacks, exception-to-status-code translation, null-status fallback, short packing compatibility, and borrowed slice lifetime behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractTraceWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractTransactionNotifier.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractTransactionNotifier.java

- **Purpose:** Java callback base for notifications when `Transaction#setSnapshotOnNextOperation()` materializes a snapshot.
- **Important APIs/types/functions:** Extends `RocksCallbackObject`; declares abstract `snapshotCreated(Snapshot newSnapshot)`; private JNI hook `snapshotCreated(long snapshotHandle)` wraps the native handle; `initializeNative()` calls `createNewTransactionNotifier()`; disposal calls `disposeInternalJni`.
- **Control flow:** Native transaction code invokes the private long-handle method, which constructs a `Snapshot` wrapper and calls the subclass callback. Native allocation/disposal is controlled by the callback base and explicit dispose path.
- **State and persistence behavior:** No durable state. The callback transfers observation of a native snapshot handle into Java; snapshot lifetime/ownership semantics depend on the `Snapshot` wrapper and transaction lifecycle.
- **Dependencies:** Depends on `RocksCallbackObject`, `Snapshot`, `Transaction`, and JNI notifier functions.
- **Integration points:** Used by transactional RocksDB Java APIs that defer snapshot creation until the next operation and need to hand the created snapshot to Java callers.
- **Risks:** The disposal comment references comparator/transactions and signals lifecycle sensitivity. Retaining the created `Snapshot` beyond its valid transaction/database lifetime can expose invalid native handles. Callback exceptions are not caught here.
- **Test signals:** Snapshot-on-next-operation callback invocation, correct snapshot handle wrapping, callback disposal after transaction close, and behavior when notifier is closed too early.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractTransactionNotifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractWalFilter.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractWalFilter.java

- **Purpose:** Base Java callback bridge for RocksDB write-ahead-log filtering during WAL replay/processing.
- **Important APIs/types/functions:** Extends `RocksCallbackObject` and implements `WalFilter`. `initializeNative()` calls `createNewWalFilter()`. Private `logRecordFoundProxy(...)` creates Java `WriteBatch` wrappers around borrowed native batch handles and packs `LogRecordFoundResult` into a short.
- **Control flow:** Native code calls `logRecordFoundProxy` with log metadata and two batch handles. The method delegates to user `logRecordFound(...)` and encodes the returned WAL processing option in the high byte plus `batchChanged` in the low bit.
- **State and persistence behavior:** The filter can affect WAL replay behavior and optionally modify replacement write batches; durable consequences are in recovered database state, not Java fields.
- **Dependencies:** Depends on `RocksCallbackObject`, `WalFilter`, `WriteBatch`, and native callback allocation.
- **Integration points:** Used by database open/recovery paths that support application filtering or rewriting of WAL records.
- **Risks:** `WriteBatch` wrappers are created for handles the filter does not own; retaining or closing them incorrectly can corrupt native recovery. Null `LogRecordFoundResult` is not guarded. Bit packing must stay compatible with native enum values.
- **Test signals:** WAL replay with keep/skip/stop options, `batchChanged` propagation, replacement batch mutation, borrowed-handle lifecycle, and native decode of packed results.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractWalFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractWriteBatch.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractWriteBatch.java

- **Purpose:** Shared implementation of `WriteBatchInterface` operations for native write batch wrappers and subclasses.
- **Important APIs/types/functions:** Extends `RocksObject`; implements `count`, `put`, `merge`, `delete`, `singleDelete`, `deleteRange`, `putLogData`, `clear`, `setSavePoint`, `rollbackToSavePoint`, `popSavePoint`, `setMaxBytes`, and `getWriteBatch`. Abstract hooks map each operation to native methods with explicit handle/length/cf-handle parameters.
- **Control flow:** Public byte-array methods pass arrays with their lengths. Column-family overloads append the `ColumnFamilyHandle.nativeHandle_`. Direct `ByteBuffer` put/delete methods pass current position and remaining bytes, then advance positions to limits. Savepoint and rollback operations delegate to native stack behavior.
- **State and persistence behavior:** Batch state is native and represents pending write operations, savepoints, log data, and max-byte constraints. Persistence occurs only when a database writes the batch; this class does not itself write to disk.
- **Dependencies:** Depends on `RocksObject`, `WriteBatchInterface`, `ColumnFamilyHandle`, `WriteBatch`, `RocksDBException`, and `ByteBuffer`.
- **Integration points:** Base for `WriteBatch`, `WriteBatchWithIndex`, transaction write batch access, WAL filters, and database write APIs.
- **Risks:** Direct ByteBuffer `put` uses assertions to require direct buffers; with assertions disabled, invalid buffers can reach JNI. Byte-array methods do not null-check. Borrowed write batches returned by callbacks require careful ownership. Column-family handles must outlive operations.
- **Test signals:** All operation overloads, direct-buffer position advancement, savepoint rollback/pop errors, count tracking, max byte enforcement, column-family writes, and exception propagation from native write batch operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractWriteBatch.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AdvancedColumnFamilyOptionsInterface.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AdvancedColumnFamilyOptionsInterface.java

- **Purpose:** Contract for advanced non-mutable column-family options that complement the mutable options interface and are implemented by `ColumnFamilyOptions`.
- **Important APIs/types/functions:** Declares setters/getters for memtable merge thresholds, inplace updates, bloom locality, compression per level, level count, dynamic level bytes, max compaction bytes, compaction style/priority/options, optimize-filters-for-hits, and force consistency checks.
- **Control flow:** This interface has no implementation. It defines fluent setter return types through generic `T extends AdvancedColumnFamilyOptionsInterface<T> & ColumnFamilyOptionsInterface<T>`.
- **State and persistence behavior:** Implementations persist settings into native `rocksdb::ColumnFamilyOptions`; the options affect LSM layout, compaction behavior, filter memory use, consistency checks, and future SST generation.
- **Dependencies:** References `CompressionType`, `CompactionStyle`, `CompactionPriority`, `CompactionOptionsUniversal`, `CompactionOptionsFIFO`, `ColumnFamilyOptionsInterface`, and `@Experimental`.
- **Integration points:** Part of the public Java API for database/column-family creation and tuning, especially options not dynamically mutable after open.
- **Risks:** Many options materially affect storage layout and performance; dynamic-level bytes is marked experimental and can cause unexpected existing-DB LSM structure changes. Implementations must keep enum mappings and C++ option availability synchronized.
- **Test signals:** API compatibility tests, implementation coverage in `ColumnFamilyOptions`, native option round-trips, and integration tests opening databases with level/universal/FIFO compaction configurations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AdvancedColumnFamilyOptionsInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AdvancedMutableColumnFamilyOptionsInterface.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AdvancedMutableColumnFamilyOptionsInterface.java

- **Purpose:** Contract for advanced column-family options that can be changed through mutable option flows and `RocksDB#setOptions(...)`.
- **Important APIs/types/functions:** Declares setters/getters for write-buffer count, inplace-update locks, memtable bloom/mempurge/huge-page settings, arena block size, L0 slowdown/stop triggers, target file sizes, level-size multipliers, pending compaction limits, sequential-skip limits, merge limits, paranoid file checks, background IO stats, TTL, periodic compaction, integrated BlobDB settings, read-triggered compaction, blob readahead, blob starting level, and prepopulate blob cache.
- **Control flow:** No executable code. The interface documents which options are dynamically changeable and which depend on other DB settings such as `maxOpenFiles == -1`.
- **State and persistence behavior:** Implementations project values into native mutable CF options. Settings affect memtable memory, write stalls, compaction scheduling, file aging, blob-file creation/GC, and read-triggered compaction behavior.
- **Dependencies:** References `CompressionType`, `PrepopulateBlobCache`, `MutableColumnFamilyOptionsInterface`, `MutableDBOptionsInterface`, `RocksDB`, and `ColumnFamilyHandle`.
- **Integration points:** Implemented by `ColumnFamilyOptions` and mirrored by mutable-options builders used for live option updates.
- **Risks:** Interface comments include duplicated javadoc terminators in a few spots, indicating doc drift risk. Several setters document 32-bit overflow exceptions that implementations must enforce in JNI. Blob options have dependencies on `enable_blob_files`/GC flags; setting dependent values alone has no effect.
- **Test signals:** Live `RocksDB#setOptions` updates, string mutable-option builder parsing for blob and compression enums, 32-bit overflow guards, and round-trip getters for dynamically changed values.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AdvancedMutableColumnFamilyOptionsInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BackgroundErrorReason.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BackgroundErrorReason.java

- **Purpose:** Java enum for native RocksDB background error sources.
- **Important APIs/types/functions:** Values are `FLUSH`, `COMPACTION`, `WRITE_CALLBACK`, and `MEMTABLE`, mapped to bytes 0 through 3. `getValue()` returns the native representation. `fromValue(byte)` maps native bytes back to enum values.
- **Control flow:** `fromValue` linearly scans enum constants and throws `IllegalArgumentException` on unknown byte values.
- **State and persistence behavior:** Stateless enum; values classify background errors surfaced from native RocksDB state.
- **Dependencies:** None beyond Java enum support.
- **Integration points:** Used by status/listener/error reporting APIs that expose the reason behind background errors.
- **Risks:** Native and Java byte values must remain synchronized. Package-private conversion methods limit external use but JNI-facing code depends on them.
- **Test signals:** Byte mapping for all enum values and rejection of unknown bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BackgroundErrorReason.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BackupEngine.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BackupEngine.java

- **Purpose:** Java wrapper for RocksDB backup/restore engine operations.
- **Important APIs/types/functions:** Static `open(Env, BackupEngineOptions)` creates the native engine. Instance APIs include `createNewBackup`, `createNewBackupWithMetadata`, `getBackupInfo`, `getCorruptedBackups`, `garbageCollect`, `purgeOldBackups`, `deleteBackup`, `restoreDbFromBackup`, and `restoreDbFromLatestBackup`. JNI hooks perform all native work and `disposeInternalJni` releases the engine.
- **Control flow:** Callers open an engine from an environment and options, call backup/restore management methods, and close the wrapper. Backup creation optionally flushes memtables first and optionally attaches metadata. Restore methods pass backup ID/latest, target DB/WAL directories, and `RestoreOptions`.
- **State and persistence behavior:** Native backup engine manages backup directories, shared SST files, WAL inclusion, metadata, corrupted backup tracking, deletion, and restore output directories. Java state is just the native handle.
- **Dependencies:** Depends on `Env`, `BackupEngineOptions`, `RocksDB`, `RestoreOptions`, `BackupInfo`, `RocksObject`, `RocksDBException`, and native backup-engine JNI.
- **Integration points:** Used by application backup workflows and tests needing consistent database snapshots or backup pruning.
- **Risks:** Methods are documented as not thread-safe for backup creation. Restore from non-latest backups can conflict with shared table files if newer backups remain. Assertions guard ownership but are optional. Native filesystem failures surface as `RocksDBException`.
- **Test signals:** Open/close, backup with and without flush, metadata round-trip, corrupted-backup listing, garbage collection, purge/delete, restore latest/specific backup, and behavior with WAL-disabled writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BackupEngine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BackupEngineOptions.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BackupEngineOptions.java

- **Purpose:** Java wrapper for native backup engine configuration.
- **Important APIs/types/functions:** Constructor validates a writable directory and calls `newBackupEngineOptions`. Options include backup directory, backup `Env`, shared table files, info log, sync, destroy old data, log-file backup, numeric backup/restore rate limits, rate limiter objects, checksum-based sharing, max background operations, and callback trigger interval.
- **Control flow:** Construction rejects null/non-directory/non-writable paths. Fluent setters assert ownership, call JNI setters, and retain Java references for objects that native code uses (`Env`, `Logger`, `RateLimiter`) to prevent premature GC/close. Rate limit setters normalize non-positive values to zero.
- **State and persistence behavior:** Native options persist backup behavior. Java fields retain referenced native wrappers; scalar getters read from native state except retained-object getters return Java references.
- **Dependencies:** Depends on `File`, `Env`, `Logger`, `RateLimiter`, `BackupEngine`, `RocksObject`, and JNI option functions.
- **Integration points:** Passed to `BackupEngine.open`; controls filesystem I/O, rate limiting, shared-file semantics, logging, and callback cadence for backup/restore operations.
- **Risks:** Constructor requires directory to already exist and be writable. Passing null to object setters is not handled. Java-retained object references must outlive the options/engine. `destroyOldData` and shared-file settings can delete or reuse backup data in ways that require careful tests.
- **Test signals:** Path validation, scalar setter/getter round-trips, retained object getters, non-positive rate limit normalization, backup engine behavior under sync/share/log-file settings, and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BackupEngineOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BackupInfo.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BackupInfo.java

- **Purpose:** Immutable Java value object describing one backup known to `BackupEngine`.
- **Important APIs/types/functions:** Package-private constructor takes backup ID, timestamp, size, file count, and application metadata. Public accessors are `backupId()`, `timestamp()`, `size()`, `numberFiles()`, and `appMetadata()`.
- **Control flow:** Instances are constructed from JNI when `BackupEngine.getBackupInfo()` materializes native backup metadata.
- **State and persistence behavior:** Stores a snapshot of backup metadata in final fields. It does not own native resources and does not mutate backup storage.
- **Dependencies:** References `BackupEngine` in javadoc; otherwise plain Java data.
- **Integration points:** Returned from backup listing APIs and used by applications/tests to inspect available backup IDs and metadata.
- **Risks:** No defensive validation; JNI must provide coherent values. `appMetadata()` may be null and callers must handle that.
- **Test signals:** Metadata values returned after creating backups, metadata null/non-null cases, file count/size consistency, and immutability expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BackupInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BlockBasedTableConfig.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BlockBasedTableConfig.java

- **Purpose:** Java configuration object for RocksDB block-based table/SST format, the default table format.
- **Important APIs/types/functions:** Extends `TableFormatConfig`. It exposes fluent setters/getters for cache/index/filter pinning, index/data-block index types, checksum type, cache objects, persistent cache, block sizes/restart intervals, metadata block size, partition filters, filter policy, whole-key filtering, compression verification, read amplification tracking, format version, separate key/value layout, index compression, alignment, index shortening/search type, and deprecated cache/hash-index options. `newTableFactoryHandle()` converts Java state to a native table factory handle.
- **Control flow:** Default constructor initializes Java defaults matching current RocksDB expectations. A private JNI constructor reconstructs Java config from native values and can wrap a native filter policy, disowning its handle before retaining it. `newTableFactoryHandle()` resolves optional object handles to zero when absent, then calls the large JNI factory constructor with scalar and enum byte values.
- **State and persistence behavior:** State is Java-side configuration until `ColumnFamilyOptions.setTableFormatConfig()` creates a native table factory. Referenced `Cache`, `PersistentCache`, and `Filter` objects are retained to keep native handles live. Settings affect future SST layout, filter construction, block-cache behavior, on-disk format compatibility, and read-amplification instrumentation.
- **Dependencies:** Depends on many RocksDB enums (`IndexType`, `DataBlockIndexType`, `ChecksumType`, `IndexShorteningMode`, `IndexSearchType`), `Cache`, `PersistentCache`, `Filter`, `FilterPolicyType`, `TableFormatConfig`, and JNI.
- **Integration points:** Usually installed via `ColumnFamilyOptions.setTableFormatConfig(new BlockBasedTableConfig()...)`; returned from native descriptor fetches; interacts with `BloomFilter`, block caches, and column-family options.
- **Risks:** No consistent Java validation for most values; invalid combinations rely on native sanitization or failure. `setFormatVersion` uses `assert` for non-negative checks. Deprecated cache-size fields still flow to JNI if no explicit cache is set. Native/Java enum ordinal assumptions in the private constructor must remain aligned. Filter/cache objects must not be closed before options/users close.
- **Test signals:** Default values, each setter/getter, native table factory creation, table format round-trip via column-family descriptor, filter/cache retention, format-version compatibility, and deprecated option behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BlockBasedTableConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BloomFilter.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BloomFilter.java

- **Purpose:** Java wrapper for RocksDB's built-in Bloom filter policy.
- **Important APIs/types/functions:** Extends `Filter`; default constructor uses 10 bits/key; public constructor creates native filter with a configurable bits/key; package constructor wraps an existing handle; deprecated two-argument constructor ignores block-based mode; `equals`/`hashCode` compare recorded `bitsPerKey`; JNI hook is `createNewBloomFilter(double)`.
- **Control flow:** Construction creates or wraps a native filter handle and stores the bits/key value for Java equality. The obsolete mode argument is ignored and delegates to the current constructor.
- **State and persistence behavior:** Native filter policy affects SST filter generation and read behavior when installed in a table config. Java records only the bits/key for equality; the native handle is owned through `Filter`.
- **Dependencies:** Depends on `Filter`, `Objects`, and native filter creation.
- **Integration points:** Commonly passed to `BlockBasedTableConfig.setFilterPolicy()` and then to `ColumnFamilyOptions`.
- **Risks:** Equality ignores native handle identity and any future filter parameters besides bits/key. Custom comparators that ignore key bytes must not use this filter unless semantics match. The filter must outlive table/options/users referencing it.
- **Test signals:** Native filter creation, default bits/key, equality/hash code, obsolete constructor behavior, and database reads with Bloom-filter-enabled table config.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BloomFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BuiltinComparator.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BuiltinComparator.java

- **Purpose:** Public enum selecting RocksDB built-in key comparators from Java.
- **Important APIs/types/functions:** Values are `BYTEWISE_COMPARATOR` and `REVERSE_BYTEWISE_COMPARATOR`.
- **Control flow:** No methods; `ColumnFamilyOptions.setComparator(BuiltinComparator)` passes `ordinal()` to native code.
- **State and persistence behavior:** Stateless enum. Selection affects on-disk key ordering and must remain stable for a database's lifetime.
- **Dependencies:** Used by `ColumnFamilyOptions`; no direct imports.
- **Integration points:** Database and column-family creation options.
- **Risks:** Native mapping currently relies on ordinal order, so reordering enum constants would be a compatibility bug. Changing comparator after database creation is not allowed by RocksDB semantics.
- **Test signals:** Opening DB/CFs with each comparator and verifying native order/mapping.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BuiltinComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ByteBufferGetStatus.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ByteBufferGetStatus.java

- **Purpose:** Result container for `RocksDB#multiGetByteBuffers(...)` calls, combining operation status, required value size, and the filled buffer.
- **Important APIs/types/functions:** Public final fields are `status`, `requiredSize`, and `value`. One package-private constructor represents success/partial success with a buffer; the other represents failure with `requiredSize = 0` and `value = null`.
- **Control flow:** Constructed by RocksDB Java internals/JNI when batch get calls complete. Callers inspect `status`, compare `requiredSize` to buffer capacity, and read `value` when present.
- **State and persistence behavior:** Immutable result object; no native ownership or durable state.
- **Dependencies:** Depends on `Status`, `ByteBuffer`, and `List` for API references.
- **Integration points:** Multi-get byte-buffer APIs that avoid per-value byte-array allocation and need to report buffer-too-small conditions.
- **Risks:** Public fields allow direct access but no methods enforce status/value consistency. Failure cases intentionally expose null value; callers must guard. Required size may exceed supplied buffer capacity.
- **Test signals:** Success, not-found/error statuses, insufficient buffer behavior, required-size reporting, and null value on failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ByteBufferGetStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Cache.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Cache.java

- **Purpose:** Abstract base for native RocksDB cache wrappers.
- **Important APIs/types/functions:** Extends `RocksObject`; protected constructor accepts a native cache handle. Public APIs are `getUsage()` and `getPinnedUsage()`, both dispatching to JNI.
- **Control flow:** Concrete caches allocate native handles and inherit usage accessors. Accessors assert ownership and call native methods with `nativeHandle_`.
- **State and persistence behavior:** Cache entries and pinned bytes are native in-memory state. There is no durable persistence, but cache lifetime impacts memory pressure and table-reader performance.
- **Dependencies:** Depends on `RocksObject` and native cache usage JNI.
- **Integration points:** Parent for `LRUCache`, `ClockCache`, HyperClock cache wrappers, and table/backup option references to caches.
- **Risks:** Assertions are optional; use after close can reach JNI with an invalid handle. Options retaining cache handles require the cache object to outlive users.
- **Test signals:** Usage/pinned usage values before and after database/table reads, disposal behavior, and integration with block-based table configs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Cache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CassandraCompactionFilter.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CassandraCompactionFilter.java

- **Purpose:** Thin Java wrapper around RocksDB's native Cassandra compaction filter.
- **Important APIs/types/functions:** Extends `AbstractCompactionFilter<Slice>`. Constructor accepts `purgeTtlOnExpiration` and `gcGracePeriodInSeconds`, then calls native `createNewCassandraCompactionFilter0`.
- **Control flow:** Construction creates the native filter; filtering behavior is implemented entirely in C++.
- **State and persistence behavior:** Native filter state/config influences compaction output by purging Cassandra TTL/tombstone data. Java stores no extra fields.
- **Dependencies:** Depends on `AbstractCompactionFilter`, `Slice`, and the Cassandra native utility implementation.
- **Integration points:** Installed with `ColumnFamilyOptions.setCompactionFilter()` for Cassandra-format value compaction.
- **Risks:** Correctness depends on native Cassandra value encoding and TTL semantics. The filter object must stay alive as long as options/DB can use it.
- **Test signals:** Compaction behavior with Cassandra values, TTL expiration/purge behavior, gc grace period handling, and filter disposal after DB close.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CassandraCompactionFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CassandraValueMergeOperator.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CassandraValueMergeOperator.java

- **Purpose:** Java wrapper for the native Cassandra wide-column value merge operator.
- **Important APIs/types/functions:** Extends `MergeOperator`; constructors accept `gcGracePeriodInSeconds` and optional `operandsLimit`; native `newSharedCassandraValueMergeOperator` allocates the shared operator; `disposeInternal` calls `disposeInternalJni`.
- **Control flow:** Construction creates a native merge operator with GC grace and operand limit settings. Merge logic runs in C++ during reads/compaction; Java only owns/releases the handle.
- **State and persistence behavior:** Native merge operator affects persisted values produced by merges and compactions. Java has no additional state beyond the native handle.
- **Dependencies:** Depends on `MergeOperator` and Cassandra native merge code.
- **Integration points:** Passed to `ColumnFamilyOptions.setMergeOperator()` for Cassandra-compatible value merging.
- **Risks:** Operand limit and GC grace semantics must match Cassandra value encoding. Native shared operator ownership must be released exactly once.
- **Test signals:** Merge correctness with Cassandra values, operand-limit behavior, GC grace behavior, database reopen/compaction behavior, and close idempotence inherited from native wrapper base.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CassandraValueMergeOperator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Checkpoint.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Checkpoint.java

- **Purpose:** Java wrapper for RocksDB checkpoint and column-family export functionality.
- **Important APIs/types/functions:** Static `create(RocksDB db)` validates a non-null initialized DB. Instance methods are `createCheckpoint(String checkpointPath)` and `exportColumnFamily(ColumnFamilyHandle, String)`. Native hooks create/dispose checkpoint objects and write checkpoint/export data.
- **Control flow:** `create` performs Java validation before constructing a native checkpoint handle from the DB handle. `createCheckpoint` delegates to native checkpoint creation. `exportColumnFamily` passes checkpoint and column-family handles and wraps the returned metadata handle in `ExportImportFilesMetaData`.
- **State and persistence behavior:** Native checkpoint creation persists an openable snapshot directory using hard links/copies. Export persists files/metadata for a column family. Java state is only the checkpoint native handle.
- **Dependencies:** Depends on `RocksDB`, `ColumnFamilyHandle`, `ExportImportFilesMetaData`, `RocksObject`, and `RocksDBException`.
- **Integration points:** Used for backups/snapshots, cloning, export/import workflows, and tests needing filesystem snapshots of live DBs.
- **Risks:** Checkpoint path/export path filesystem errors surface from native code. The DB and column-family handles must remain valid. Hard-link behavior assumes same-disk support for efficient checkpoints.
- **Test signals:** Null/closed DB validation, checkpoint directory contents and reopenability, column-family export/import metadata, invalid paths, and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Checkpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ChecksumType.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ChecksumType.java

- **Purpose:** Enum of checksum algorithms for block-based table files.
- **Important APIs/types/functions:** Values are `kNoChecksum`, `kCRC32c`, `kxxHash`, `kxxHash64`, and `kXXH3`, mapped to byte values 0 through 4. `getValue()` exposes the native byte.
- **Control flow:** No reverse lookup in this file; users pass byte values to native code, and some callers use `ChecksumType.values()[byte]` when reconstructing config.
- **State and persistence behavior:** Stateless enum. Selection affects checksums written to new SST/table files and read-time verification compatibility.
- **Dependencies:** Used by `BlockBasedTableConfig`.
- **Integration points:** Table format configuration and native block-based table factory creation.
- **Risks:** Java enum order and byte values must stay aligned with RocksDB C++ `ChecksumType`. `kNoChecksum` is documented as not implemented yet.
- **Test signals:** Byte mapping, table creation with each supported checksum, and config round-trip from native table descriptors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ChecksumType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ClockCache.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ClockCache.java

- **Purpose:** Deprecated compatibility wrapper that preserves the old ClockCache Java API while native implementation returns an LRU-compatible cache due to removal of the old clock cache.
- **Important APIs/types/functions:** Extends `Cache`; constructors accept capacity, optional shard bits, and optional strict capacity limit. Native `newClockCache` creates the underlying replacement cache; disposal uses `disposeInternalJni`.
- **Control flow:** Constructors normalize missing shard bits to `-1` and strict limit to false, then delegate to native allocation.
- **State and persistence behavior:** Native cache is in-memory only. Despite class name, behavior is documented as LRU fallback rather than old clock algorithm.
- **Dependencies:** Depends on `Cache` and native cache factory/disposal functions.
- **Integration points:** Legacy applications using `new ClockCache(...)` and table configs expecting a `Cache`.
- **Risks:** Deprecated class name can mislead performance expectations. HyperClockCache requires extra parameters not represented here. Tests should not assume clock-cache eviction behavior.
- **Test signals:** Constructor compatibility, returned cache usability as block cache, usage metrics, strict-capacity argument propagation, and deprecation/API compatibility checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ClockCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyDescriptor.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyDescriptor.java

- **Purpose:** Java value object pairing a column-family name with `ColumnFamilyOptions`.
- **Important APIs/types/functions:** Constructors accept a name with default options or explicit options. `getName()` returns the stored byte array. `getOptions()` returns the options object. `equals` compares name bytes and native options handle identity; `hashCode` combines the same.
- **Control flow:** Construction stores references directly; no copying. Equality requires same class, equal name bytes, and equal options native handle value.
- **State and persistence behavior:** Descriptor is Java-side configuration used when creating/opening column families. It does not own DB state, but its options may own native resources.
- **Dependencies:** Depends on `Arrays` and `ColumnFamilyOptions`.
- **Integration points:** Passed to `RocksDB.open`/create column-family APIs and returned by `ColumnFamilyHandle.getDescriptor()`.
- **Risks:** Name array is stored and returned directly, so callers can mutate descriptor identity after construction. Equality by native handle means two semantically identical options objects compare unequal.
- **Test signals:** Default option creation, explicit option retention, name mutation behavior, equality/hash behavior, and use in multi-column-family open/create calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyDescriptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyHandle.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyHandle.java

- **Purpose:** Java wrapper for native RocksDB `ColumnFamilyHandle` pointers.
- **Important APIs/types/functions:** Constructors create owned handles tied to a `RocksDB` parent or non-owning handles from JNI. Public APIs include `getName()`, `getID()`, and `getDescriptor()`. Equality/hash use DB native handle, column-family ID, and name. `disposeInternal()` frees the handle only if the parent DB still owns its handle.
- **Control flow:** Owned constructor retains the parent DB to bias lifecycle ordering. JNI constructor disowns the native handle because Java likely already has an owner. Accessors assert owned/default handle and delegate to JNI. `isDefaultColumnFamily()` compares against `rocksDB_.getDefaultColumnFamily()`.
- **State and persistence behavior:** Native handle identifies a column family inside a live DB. Java retains parent DB reference; no durable state is stored here.
- **Dependencies:** Depends on `RocksDB`, `ColumnFamilyDescriptor`, `RocksObject`, `RocksDBException`, `Arrays`, and `Objects`.
- **Integration points:** Used across reads/writes/options/metadata APIs to select a column family. JNI-created non-owning handles appear in callbacks/descriptors.
- **Risks:** `equals`, `hashCode`, and `isDefaultColumnFamily()` assume `rocksDB_` is non-null, so non-owning JNI-created handles are risky in those paths. Closing the DB before handles skips native handle deletion to avoid double-free. Exceptions in equality/hash are wrapped as runtime exceptions.
- **Test signals:** Name/ID/descriptor retrieval, equality/hash for handles from the same and different DBs, default column-family behavior, non-owning handle safety, and close ordering with DB close.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyHandle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyMetaData.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyMetaData.java

- **Purpose:** Immutable metadata snapshot describing a column family's size, file count, name, and per-level metadata.
- **Important APIs/types/functions:** Private JNI constructor sets final fields. Public accessors are `size()`, `fileCount()`, `name()`, and `levels()`.
- **Control flow:** Native code constructs instances when metadata APIs are called. `levels()` wraps the backing array with `Arrays.asList`.
- **State and persistence behavior:** Stores a point-in-time Java snapshot of native LSM metadata. It does not own native resources or mutate DB state.
- **Dependencies:** Depends on `LevelMetaData`, `Arrays`, and `List`.
- **Integration points:** Returned by RocksDB column-family metadata APIs for diagnostics, monitoring, and tests.
- **Risks:** `name()` returns the internal byte array; `levels()` returns a fixed-size list backed by the internal array. Metadata can become stale immediately after DB activity.
- **Test signals:** Metadata values after writes/flushes/compactions, level list contents, file count/size consistency, and immutability/staleness expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyMetaData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyOptions.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyOptions.java

- **Purpose:** Concrete Java wrapper for native `rocksdb::ColumnFamilyOptions`, implementing both creation-time and mutable column-family option interfaces.
- **Important APIs/types/functions:** Constructors allocate native options, shallow-copy another options object, derive from `Options`, or wrap a native handle. Static `getColumnFamilyOptionsFromProps` parses property strings through native code. Methods cover comparator/merge/filter configuration, write buffers, compression, levels, compaction, memtable/table factories, CF paths, bloom/mempurge settings, L0 triggers, pending compaction limits, TTL/periodic compaction, SST partitioner, compaction limiter, range-deletion controls, and integrated BlobDB options. A large native-method block maps Java calls to C++ options.
- **Control flow:** Most setters assert ownership, pass Java scalar/enum/native-handle values to JNI, and return `this`. Object-valued setters also retain Java references (`comparator_`, filters, table/memtable configs, compression/compaction options, factories, limiters) so native pointers remain valid. List/array setters convert compression and CF path structures to byte/string/long arrays. Getters either read native state or return retained Java objects. `newColumnFamilyOptionsInstance()` loads the native library before allocation.
- **State and persistence behavior:** Native options state controls column-family creation and live option changes. Java reference fields are lifetime anchors, not always complete mirrors of native state; getters for object-valued settings return retained Java objects, while scalar getters query native state. Options shape SST files, LSM layout, compaction behavior, blob files, write stalls, and background checks.
- **Dependencies:** Depends on the option interfaces, many RocksDB enum/config classes (`CompressionType`, `CompactionStyle`, `MemTableConfig`, `TableFormatConfig`, `DbPath`, etc.), `RocksDB.loadLibrary`, `Paths`, collections, and extensive JNI.
- **Integration points:** Passed in `ColumnFamilyDescriptor`, used by database open/create APIs, copied from full `Options`, returned by descriptor fetches, and used for live mutable option updates.
- **Risks:** Copy constructor is shallow for pointer-valued options, so lifetimes are shared. Many setters lack null checks and rely on JNI/assertions. `setDisableAutoCompactions` calls the native setter twice. Enum mappings must match native byte values. Object-valued getters may be null even when native state exists unless Java set the object or fetched config populated it. Java comments show some javadoc drift, so generated docs should not be treated as validation.
- **Test signals:** Constructor/load behavior, property parsing success/failure, every setter/getter native round-trip, object lifetime retention, shallow-copy behavior, table/memtable factory installation, CF path conversion, blob options, compaction style/priority, and database open/write/compact workflows using configured options.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyOptionsInterface.java -->
# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyOptionsInterface.java

- **Purpose:** Main public Java interface for column-family creation/configuration options. It extends `AdvancedColumnFamilyOptionsInterface` and is implemented by `ColumnFamilyOptions`.
- **Important APIs/types/functions:** Declares optimizer helpers, comparator and merge operator setters, compaction filter/factory accessors, prefix extractors, L0 triggers, level multiplier, FIFO table size, memtable/table format configs, CF paths, bottommost/general compression options, SST partitioner factory, range-deletion conversion/max settings, compaction thread limiter, and `DEFAULT_COMPACTION_MEMTABLE_MEMORY_BUDGET`.
- **Control flow:** No implementation. Generic fluent type `T extends ColumnFamilyOptionsInterface<T>` lets concrete options return their own type from setters.
- **State and persistence behavior:** Implementations persist these settings into native column-family options and associated Java-retained helper objects. Settings can affect database open compatibility, compaction output, file placement, memory usage, and callback invocation.
- **Dependencies:** References core RocksDB Java types including `BuiltinComparator`, `AbstractComparator`, `MergeOperator`, compaction filters/factories, `MemTableConfig`, `TableFormatConfig`, `DbPath`, compression options, `SstPartitionerFactory`, and `ConcurrentTaskLimiter`.
- **Integration points:** Public API used by applications when constructing `ColumnFamilyOptions`, `ColumnFamilyDescriptor`, and database open/create flows.
- **Risks:** Interface includes both object-lifetime contracts and storage-layout options; implementations must retain callback/config objects long enough for native use. Comparator changes are creation-time only. Name/comment drift exists, including a duplicated `useFixedLengthPrefixExtractor` declaration in the source view, so implementation and compile checks are important.
- **Test signals:** Compile/API compatibility for implementers, `ColumnFamilyOptions` method coverage, object lifetime with comparators/filters/factories, open/create DB workflows, and option persistence through descriptors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ColumnFamilyOptionsInterface.java -->
