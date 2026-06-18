# subset-b-008652 Research

Grouped research report for RocksDB Java JNI option-loading and persistent-cache bridge files. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/options_util.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/options_util.cc

## Purpose
Implements the native side of `org.rocksdb.OptionsUtil`, bridging Java callers to RocksDB C++ options-file utilities. It loads DB and column-family options from the latest DB `OPTIONS-*` file or from an explicit options file, exposes latest-options-file discovery, and reconstructs supported table-format configuration for Java-side `ColumnFamilyOptions`.

## Important APIs, Types, And Functions
The helper `build_column_family_descriptor_list(JNIEnv*, jobject, std::vector<ColumnFamilyDescriptor>&)` converts C++ `ColumnFamilyDescriptor` objects into Java `ColumnFamilyDescriptor` instances and appends them to the caller-provided `java.util.List`.

The JNI exports are `Java_org_rocksdb_OptionsUtil_loadLatestOptions`, `Java_org_rocksdb_OptionsUtil_loadOptionsFromFile`, `Java_org_rocksdb_OptionsUtil_getLatestOptionsFileName`, and `Java_org_rocksdb_OptionsUtil_readTableFormatConfig`. They wrap C++ `LoadLatestOptions`, `LoadOptionsFromFile`, `GetLatestOptionsFileName`, and table factory option extraction.

Important JNI support types come from `rocksjni/portal.h`: `JniUtil::copyStdString`, `ListJni`, `ColumnFamilyDescriptorJni`, `BlockBasedTableOptionsJni`, `RocksDBExceptionJni`, and `IllegalArgumentExceptionJni`. Native handles are interpreted as `ConfigOptions*`, `DBOptions*`, `Env*`, and `ColumnFamilyOptions*`.

## Control Flow
`loadLatestOptions` copies the Java DB path into a `std::string`, reinterprets the config and DB option handles, calls `LoadLatestOptions`, and either throws a Java `RocksDBException` or appends the returned column-family descriptors to `jcfds`. `loadOptionsFromFile` follows the same flow using an explicit options-file path and `LoadOptionsFromFile`.

`build_column_family_descriptor_list` first resolves `List.add`. For each descriptor, it constructs the Java descriptor wrapper, checks for pending JNI exceptions, calls `List.add`, and stops immediately if construction, Java method invocation, or list insertion fails. It does not clear the target list before appending.

`getLatestOptionsFileName` copies the DB path, calls `GetLatestOptionsFileName` with the provided `Env*`, throws on non-OK status, and returns a new Java UTF string for the resulting file name. `readTableFormatConfig` validates the `ColumnFamilyOptions` handle, checks that a table factory exists, supports only `BlockBasedTable`, extracts `BlockBasedTableOptions`, and constructs the matching Java `BlockBasedTableConfig`.

## State And Persistence Behavior
This file does not create or mutate RocksDB database contents. It reads persisted options metadata from DB directories or options files and writes the parsed values into caller-owned `DBOptions` plus newly constructed Java `ColumnFamilyDescriptor` wrappers. The persistent state it depends on is the RocksDB `OPTIONS-*` file set and the filesystem view exposed through `Env`.

Native ownership remains with the Java wrapper pattern: the method receives raw native handles owned by Java `ConfigOptions`, `DBOptions`, `Env`, and `ColumnFamilyOptions` objects. The constructed Java column-family descriptors encapsulate copied native option state created by the portal helpers. Local JNI references are deleted only on early error paths; on successful list insertion the local references are left for normal JNI frame cleanup.

## Dependencies And Integration Points
The public Java companion `OptionsUtil.java` calls these natives, then runs `loadTableFormatConfig` over returned descriptors so each `ColumnFamilyOptions` receives the fetched Java `TableFormatConfig`. `OptionsUtilTest.java` exercises loading latest options, loading from file, block-based table format restoration, and latest filename discovery.

The file integrates with RocksDB utility parsing (`rocksdb/utilities/options_util.h`), DB option structures (`rocksdb/db.h`), environment abstraction (`rocksdb/env.h`), and the Java binding conversion layer. The table-format branch is coupled to `TableFactory::kBlockBasedTableName()` and `BlockBasedTableOptionsJni::construct`.

## Risks And Edge Cases
There are no null-handle checks for `ConfigOptions*`, `DBOptions*`, `Env*`, or the Java list in the load and filename methods, so the Java layer must pass valid live objects. `readTableFormatConfig` does validate the column-family options handle and table factory, but unsupported table factories throw `IllegalArgumentException`.

The list builder appends to the supplied list and can leave a partially populated list if a later descriptor conversion or `List.add` fails. `CallBooleanMethod` returning false is treated as failure but no explicit Java exception is thrown in that case. `NewStringUTF` failure is not checked after successful filename lookup, so an allocation failure relies on the JVM's pending exception behavior. The table-format support is intentionally narrow: non-block-based table factories and pointer-valued table options are not reconstructed here.

## Test Signals
Direct Java coverage is in `OptionsUtilTest`. The main signals are restored DB option values, restored column-family names and options, successful reconstruction of `BlockBasedTableConfig` fields, and filenames beginning with `OPTIONS-`. Useful regression tests should also cover unsupported table factories, null/invalid handles where Java can expose them, pre-populated descriptor lists, and JNI exception paths during descriptor construction or list insertion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/options_util.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/persistent_cache.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/persistent_cache.cc

## Purpose
Implements the native side of `org.rocksdb.PersistentCache`, creating and disposing a C++ `std::shared_ptr<rocksdb::PersistentCache>` for Java callers. The object is used by Java table configuration code to attach a persistent read cache to block-based table options.

## Important APIs, Types, And Functions
`Java_org_rocksdb_PersistentCache_newPersistentCache` receives Java handles for `Env` and `Logger`, a cache directory path, size, and `optimizedForNvm` flag. It calls C++ `NewPersistentCache` and returns a native pointer to a heap-allocated `std::shared_ptr<PersistentCache>`.

`Java_org_rocksdb_PersistentCache_disposeInternalJni` deletes that heap-allocated `std::shared_ptr`, decrementing the C++ shared ownership count. Important dependencies include `rocksdb/persistent_cache.h`, `loggerjnicallback.h`, `portal.h`, `cplusplus_to_java_convert.h`, and the generated JNI header `org_rocksdb_PersistentCache.h`.

## Control Flow
Creation reinterprets `jenv_handle` as `Env*`, copies the Java path to `std::string`, reinterprets `jlogger_handle` as `std::shared_ptr<LoggerJniCallback>*`, allocates a new `std::shared_ptr<PersistentCache>` initialized to `nullptr`, and passes that pointer as the output parameter to `NewPersistentCache`. If path conversion raises a JNI exception it returns `0`. If `NewPersistentCache` returns a non-OK `Status`, it throws a Java `RocksDBException` but still returns the allocated shared-pointer wrapper.

Disposal is a single cast from `jlong` back to `std::shared_ptr<PersistentCache>*` followed by `delete`. The actual cache object remains alive if other C++ options structures copied the shared pointer.

## State And Persistence Behavior
The cache itself is persistent storage under the supplied path and size limit, managed by RocksDB's `PersistentCache` implementation rather than this bridge. This file only manages the Java-visible native handle and shared pointer lifetime. The `optimizedForNvm` boolean is forwarded to cache construction and can change how the underlying cache is tuned for the medium.

The heap-allocated shared-pointer wrapper is the native state owned by Java `PersistentCache`. It can be copied into `BlockBasedTableOptions.persistent_cache` through `table.cc`, allowing options to retain cache ownership independently of the Java wrapper object's native handle.

## Dependencies And Integration Points
The Java constructor in `PersistentCache.java` calls `newPersistentCache`, and `BlockBasedTableConfig.setPersistentCache` later passes the returned handle into table-option construction. `table.cc` dereferences the same handle type and copies the shared pointer into `BlockBasedTableOptions`.

The logger handle is expected to point at a Java-backed `LoggerJniCallback` shared pointer. This lets C++ cache code emit logs through Java logging callbacks. The environment handle determines filesystem behavior for the cache path.

## Risks And Edge Cases
The bridge assumes non-null, valid `Env` and logger handles. A null or already-disposed logger handle would be dereferenced before status handling. Size is cast from signed Java `long` to `uint64_t`; negative values would become very large unless rejected by lower layers.

On `NewPersistentCache` failure, the code throws but returns a non-zero pointer to a shared pointer that may still hold `nullptr`. That matches the common Java pattern only if object construction is aborted and the handle is not used; otherwise callers could retain an invalid native object. The allocation occurs before construction status is known, so exception paths rely on Java wrapper cleanup or process lifetime to avoid leaks. Disposal is not idempotent at the native level; Java must call it once per live handle.

## Test Signals
Coverage is indirect in `BlockBasedTableConfigTest.persistentCache`, which constructs a `PersistentCache`, installs it in `BlockBasedTableConfig`, builds `Options`, and checks the resulting table factory name. Stronger tests would assert creation failure behavior for invalid paths/sizes, logger callback safety, disposal after table options copy the shared pointer, and negative-size handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/persistent_cache.cc -->
