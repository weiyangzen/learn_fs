# subset-b-008646 Research

Grouped research report for RocksDB utility public headers under `sources/storage-engines/rocksdb/include/rocksdb/utilities`. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/customizable_util.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/customizable_util.h

## Purpose
Provides template helpers used by RocksDB configurable/customizable classes to create objects from strings, option maps, and the runtime `ObjectRegistry`. It is the public convenience layer behind many `CreateFromString` implementations.

## Important APIs, Types, And Functions
`NewSharedObject`, `LoadSharedObject`, `NewManagedObject`, `LoadManagedObject`, `NewUniqueObject`, `LoadUniqueObject`, `NewStaticObject`, and `LoadStaticObject` cover shared, managed singleton-like, unique, and raw/static pointer ownership models. All templates require the target type to participate in the customizable API, including registry factory lookup and `ConfigureFromMap` or `Customizable::ConfigureNewObject`.

## Control Flow
The `Load*` helpers parse a string using `Customizable::GetOptionsMap`, producing an object id and option map. The `New*` helpers call the configured registry to instantiate the requested id, optionally ignore unsupported ids, and then configure the new instance from the parsed option map. Empty values reset shared/unique/static pointers when no options are present; managed objects require a non-empty id and reuse existing registry-managed instances.

## State And Persistence Behavior
The file itself has no durable persistence. State changes are in caller-owned pointer outputs and in `ObjectRegistry` managed-object caches for managed objects. Managed-object creation configures only newly created objects; existing managed objects are returned as-is and ignore the new option map.

## Dependencies And Integration Points
Depends on `rocksdb/customizable.h`, `rocksdb/convenience.h`, `Status`, and `ObjectRegistry`. It integrates with option parsing, plugin/object registration, configurable object serialization, and factory methods for caches, table factories, comparators, environments, merge operators, and other extension points.

## Risks And Edge Cases
Ignoring unsupported options converts `NotSupported` into `OK`, which can silently leave outputs unchanged or null depending on the path. Empty ids with non-empty option maps return `NotSupported`. Static/raw pointer creation requires the factory to return an unguarded object, while shared/unique creation requires guarded ownership; wrong factory ownership mode yields invalid-argument errors. Managed-object reuse means later configuration strings do not reconfigure an already cached id.

## Test Signals
Useful tests cover valid and invalid factory ids, id-only strings, braced option maps, empty-string reset behavior, ownership mismatch errors, managed-object reuse, and the `ignore_unsupported_options`/`ignore_unknown_options` flags.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/customizable_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/db_ttl.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/db_ttl.h

## Purpose
Defines `DBWithTTL`, a `StackableDB` wrapper that stores creation timestamps in values and removes expired entries during compaction. It gives RocksDB users a non-strict time-to-live database interface.

## Important APIs, Types, And Functions
`DBWithTTL::Open` has single-column-family and multi-column-family overloads with per-CF TTL vectors. `CreateColumnFamilyWithTtl`, `SetTtl`, `SetTtl(ColumnFamilyHandle*)`, and `GetTtl` expose runtime TTL control. The class derives from `StackableDB` and forwards most DB operations through the wrapper.

## Control Flow
Open wraps a base DB in TTL behavior. Writes append an internal timestamp suffix to values, and compaction filters compare timestamp plus TTL with current time to decide expiration. Reads and iterators can still observe expired data until a compaction processes it. Read-only opens do not run compactions, so expiration cleanup is disabled.

## State And Persistence Behavior
TTL metadata is persisted inside stored values as timestamp suffixes, which makes the DB incompatible with direct `DB::Open` for normal interpretation. TTL values are wrapper configuration, not a rewrite of existing timestamps, and different opens can use different TTLs.

## Dependencies And Integration Points
Depends on `rocksdb/db.h` and `StackableDB`. It integrates with column-family creation, compaction filtering, normal DB reads/writes, and operational compaction scheduling.

## Risks And Edge Cases
Non-positive TTL means effectively infinite TTL. Small positive TTL values can make a whole database eligible for deletion after compaction. Reopening with plain `DB::Open` exposes timestamp-suffixed values and loses expiration behavior. Expiration is best-effort, not a strict read-time guarantee.

## Test Signals
Tests should cover timestamp suffix compatibility, expired values remaining before compaction, deletion after compaction, read-only mode not expiring data, multi-CF TTL vectors, and runtime `SetTtl`/`GetTtl`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/db_ttl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/debug.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/debug.h

## Purpose
Exposes debug utilities for inspecting internal key versions in a user-key range. It is a public diagnostic API for understanding snapshots, sequence numbers, and value types present in the LSM.

## Important APIs, Types, And Functions
`KeyVersion` stores `user_key`, `value`, `sequence`, and integer `type`, with `GetTypeName()` for readable type names. `GetAllKeyVersions` has overloads for default and explicit column families and accepts optional begin/end keys plus `max_num_ikeys`.

## Control Flow
The implementation scans internal versions for an inclusive user-key range and appends copied `KeyVersion` records to the caller-provided vector until the range is exhausted or the maximum internal-key count is reached.

## State And Persistence Behavior
No DB state is mutated. The API materializes copies of keys and values into memory, so the result is a snapshot-like diagnostic copy at the time of traversal rather than a persistent artifact.

## Dependencies And Integration Points
Depends on `DB`, `ColumnFamilyHandle`, `OptSlice`, and `SequenceNumber`. It integrates with internal iterators and versioned-key visibility, although only the public declaration is in this header.

## Risks And Edge Cases
Large ranges can consume large memory because keys and values are copied. The range is inclusive-inclusive, which differs from many RocksDB half-open range APIs. Results may include tombstones, merges, and multiple versions that normal reads hide.

## Test Signals
Tests should check sequence ordering, type-name mapping, inclusive end-key handling, column-family overloads, empty ranges, tombstones/merges, and enforcement of `max_num_ikeys`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/env_mirror.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/env_mirror.h

## Purpose
Defines `EnvMirror`, an `EnvWrapper` that mirrors filesystem operations to two backing environments and asserts matching results. It is primarily a validation tool for new `Env` implementations against a known-good backend.

## Important APIs, Types, And Functions
`EnvMirror` overrides file creation/opening, directory operations, existence checks, child listing, file size/modification time, rename/link, lock, and unlock operations. `FileLockMirror` stores paired locks from the two backends. Forward-declared file mirror classes handle sequential, random-access, and writable file wrappers in the implementation.

## Control Flow
For each mirrored operation, the wrapper invokes environment `a_` and `b_`, compares `Status` values with `assert`, compares returned metadata or child lists where applicable, and returns the primary environment's result to the caller. Reads from mirrored file wrappers are expected to read both backends and assert identical content.

## State And Persistence Behavior
The two backing environments receive the same mutating operations, so file state is duplicated across them. `EnvMirror` optionally owns either backend through `free_a_` and `free_b_`; its destructor deletes only those marked owned. Lock state is represented by paired backend locks.

## Dependencies And Integration Points
Depends on `rocksdb/env.h`, `EnvWrapper`, `SequentialFile`, `RandomAccessFile`, `WritableFile`, `Directory`, and `FileLock`. It integrates with DB opens and tests that need to validate filesystem semantics.

## Risks And Edge Cases
The class uses `assert`, so mismatch detection can disappear in builds with assertions disabled. It assumes mirrored operations have identical status behavior, which can be too strict for environments with small timing differences; modification times allow only a tolerance. If one backend succeeds and the other fails on a mutating operation, side effects may already be divergent before the assert fires. Ownership flags must match caller allocation expectations.

## Test Signals
Tests should inject mismatched statuses, child ordering differences, size mismatches, read mismatches in file wrappers, lock/unlock behavior, and destructor ownership paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/env_mirror.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/info_log_finder.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/info_log_finder.h

## Purpose
Declares a utility for listing RocksDB information log files associated with an open DB.

## Important APIs, Types, And Functions
`GetInfoLogList(DB* db, std::vector<std::string>* info_log_list)` is the only API. It returns a `Status` and populates the caller-provided vector with log file names or paths.

## Control Flow
The implementation is expected to inspect the DB's environment, options, and log directory naming conventions, then append discovered info logs to the output vector.

## State And Persistence Behavior
The function is read-only with respect to the database. It observes filesystem state for current and rotated logs.

## Dependencies And Integration Points
Depends on `DB`, `Options`, `Status`, and the filesystem environment behind the DB. It integrates with operational tooling that needs to collect diagnostics or archive logs.

## Risks And Edge Cases
Null DB or output pointers, custom info-log directories, missing files during rotation, and environment errors are the main edge cases. Consumers should not assume stable ordering unless the implementation documents it.

## Test Signals
Tests should cover default log locations, custom DB/log paths, rotated logs, empty log directories, and filesystem errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/info_log_finder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/ldb_cmd.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/ldb_cmd.h

## Purpose
Declares the command abstraction and runner for RocksDB's `ldb` command-line tooling. It centralizes argument parsing, DB opening modes, option overrides, formatting helpers, and command execution state.

## Important APIs, Types, And Functions
`LDBCommand` exposes static option names, `ParsedParams`, `SelectCommand`, `ParseSingleParam`, `InitFromCmdLineArgs`, `ValidateCmdLineOptions`, `PrepareOptions`, `OverrideBaseOptions`, `OverrideBaseCFOptions`, `Run`, `DoCommand`, `GetExecuteState`, `HexToString`, `StringToHex`, and print/parse helpers. `LDBCommandRunner::RunCommand` is the top-level CLI entry, with `PrintHelp` for usage output.

## Control Flow
Command-line args are parsed into command tokens, options, and flags. A selector constructs the concrete command. `Run()` prepares/open DB state unless `NoDBOpen()` is true, dispatches `DoCommand()`, and records an `LDBCommandExecuteResult`. Opening can choose normal DB, read-only DB, secondary DB, TTL DB, or `TransactionDB` based on flags.

## State And Persistence Behavior
The command object owns DB handles and column-family handles for the command lifetime, plus parsed option maps, flags, configured options, environment guards, TTL/transaction pointers, and execution result state. Individual concrete commands may mutate persistent DB contents through puts, deletes, compactions, ingestion, and option changes.

## Dependencies And Integration Points
Depends on `DB`, `Env`, `Iterator`, `LDBOptions`, `Options`, `DBWithTTL`, `LDBCommandExecuteResult`, and `TransactionDB`. It integrates with the `ldb` binary, tests through `TEST_GetOptionMap`/`TEST_GetFlags`, option-file loading, blob options, timestamp reads, and column-family handling.

## Risks And Edge Cases
Command option validation must reject unsupported flags for each command. Hex parsing/printing must be consistent for keys and values separately. DB open mode combinations such as TTL plus transaction or secondary paths need careful handling. `ReadOptions::timestamp`, column-family comparators, and user-defined timestamps require correct encoding. Since the destructor calls `CloseDB`, ownership and handle cleanup are critical.

## Test Signals
Tests should cover parser tokenization, command selection, invalid options, hex and non-hex key/value formatting, TTL timestamp output, transaction flags, secondary/leader paths, loading options from files, blob flags, and status strings returned by `RunCommand`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/ldb_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/ldb_cmd_execute_result.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/ldb_cmd_execute_result.h

## Purpose
Defines a small result object used by `ldb` commands to track whether execution has not started, succeeded, or failed, plus a printable message.

## Important APIs, Types, And Functions
`LDBCommandExecuteResult::State` contains `EXEC_NOT_STARTED`, `EXEC_SUCCEED`, and `EXEC_FAILED`. The class provides constructors, `ToString`, `Reset`, `SetState`, `SetMessage`, `IsSucceed`, `IsFailed`, `GetState`, and `GetMessage`.

## Control Flow
Commands update state and message while running. `ToString()` prefixes failed results with `Failed: ` and not-started results with `Not started: `, while successful results print only the message if any.

## State And Persistence Behavior
State is purely in-memory and owned by the command object. `Reset()` returns to `EXEC_NOT_STARTED` and clears the message.

## Dependencies And Integration Points
Depends only on the RocksDB namespace header and `std::string`. It is embedded in `LDBCommand` and consumed by command runner status handling and tests.

## Risks And Edge Cases
The constructor takes `std::string&` rather than `const std::string&`, limiting construction from temporaries. `ToString()` has no default branch for unknown enum values. An `EXEC_SUCCEED` with empty message returns an empty string, so callers must inspect state when they need explicit success.

## Test Signals
Tests should assert each `ToString()` prefix, reset behavior, state predicates, empty messages, and message mutation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/ldb_cmd_execute_result.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/leveldb_options.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/leveldb_options.h

## Purpose
Provides a LevelDB-compatible options struct and conversion function so applications can configure RocksDB using the familiar LevelDB option surface.

## Important APIs, Types, And Functions
`LevelDBOptions` includes comparator, creation flags, paranoid checks, environment/log pointers, write buffer size, open-file limit, block cache, block size, restart interval, compression, and filter policy. `ConvertOptions(const LevelDBOptions&)` produces a RocksDB `Options`.

## Control Flow
Callers fill a `LevelDBOptions` instance, then call `ConvertOptions` before `DB::Open`. The implementation maps LevelDB-style fields to modern RocksDB options, including table/block-based settings.

## State And Persistence Behavior
The header has no persistent state. Some options, such as comparator, compression, and block/filter layout, affect durable DB/table compatibility and future read behavior.

## Dependencies And Integration Points
Depends on compression types and forward declarations for `Cache`, `Comparator`, `Env`, `FilterPolicy`, `Logger`, `Options`, and `Snapshot`. It integrates with legacy LevelDB migrations and compatibility layers.

## Risks And Edge Cases
Comparator identity and ordering must match previous DB opens. Pointer fields are non-owning and must outlive DB use as required by RocksDB. Some LevelDB defaults and semantics do not map one-to-one to RocksDB internals, especially table options and cache behavior.

## Test Signals
Tests should validate default constructor values, conversion of every field, comparator-name compatibility, bloom filter/table mapping, and opening a DB with converted options.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/leveldb_options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/memory_util.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/memory_util.h

## Purpose
Declares `MemoryUtil`, a utility for aggregating approximate memory usage across DB instances and explicit cache sets.

## Important APIs, Types, And Functions
`MemoryUtil::UsageType` categorizes memtable total, unflushed memtables, table readers, and caches. `GetApproximateMemoryUsageByType` is a template that accepts vectors of `DB*`-like or `unique_ptr<DB>`-like entries, a set of `Cache*`, and returns a map from usage type to bytes.

## Control Flow
The implementation queries each DB for memory consumers, aggregates memtable and table-reader usage, and separately sums the caches explicitly supplied in `cache_set`.

## State And Persistence Behavior
The utility is read-only and returns approximate in-memory state at the time of measurement. It does not persist metrics and intentionally does not include DB-internal caches unless they are supplied in `cache_set`.

## Dependencies And Integration Points
Depends on `Cache`, `DB`, `Status`, STL maps/vectors, and unordered cache sets. It integrates with monitoring, tests, and memory-tuning tools.

## Risks And Edge Cases
The cache set is passed by value, which copies the unordered set. Cache memory is counted only for the input set, so callers can undercount or double count if they misunderstand cache ownership. Approximate DB memory can change concurrently while it is measured.

## Test Signals
Tests should cover raw and smart DB pointer vectors, empty inputs, cache-only measurements, shared cache deduplication, and expected usage categories after writes/flushes/table opens.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/memory_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/object_registry.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/object_registry.h

## Purpose
Defines RocksDB's runtime object factory and managed-object registry. It lets configurable components instantiate extension objects by name or pattern, register plugins/libraries, and share named objects across option parsing.

## Important APIs, Types, And Functions
`FactoryFunc`, `RegistrarFunc`, and `ConfigureFunc` describe factory, plugin registration, and post-create configuration callbacks. `ObjectLibrary` stores factory entries and exposes `PatternEntry`, `FindFactory`, `AddFactory`, `Register`, factory-name/type inspection, `Dump`, and `Default`. `ObjectRegistry` exposes `NewInstance`, `Default`, library addition, `NewObject`, `NewUniqueObject`, `NewSharedObject`, `NewStaticObject`, managed-object setters/getters/listing, `GetOrCreateManagedObject`, plugin registration, and factory introspection.

## Control Flow
Libraries hold factories keyed by target type and matched by `PatternEntry`. Registry factory lookup searches libraries in reverse addition order, then delegates to the parent registry if no local match exists. Object creation calls the selected factory, checks whether ownership mode matches the requested pointer type, and returns `NotSupported` or `InvalidArgument` on missing or failed factories. Managed-object lookup first checks the parent, then a weak-pointer map, and creates/configures a new shared object if no live object exists.

## State And Persistence Behavior
State is in-memory: registered libraries, built-in plugin registrars, plugin names, and weak managed-object mappings by `type://id`. Weak pointers mean managed entries can expire when no external shared ownership remains. Parent registries provide inherited factories and managed objects.

## Dependencies And Integration Points
Depends on `Status`, `Customizable`, `Logger`, STL containers, and mutexes. It integrates with `ConfigOptions::registry`, customizable object creation, plugin registration, options-file deserialization, and extension points such as comparators, environments, caches, and table factories.

## Risks And Edge Cases
Pattern matching is regex-like but deliberately not a full regex engine, so complex patterns can surprise plugin authors. Library search order gives later-added libraries precedence. Factory ownership mode must match requested static/shared/unique creation. Managed-object keys can be stored under both input id and configured object id, and existing managed objects are not reconfigured. Thread safety relies on separate mutexes for libraries and objects.

## Test Signals
Tests should cover pattern separators/suffixes/numbers/alternative names, library precedence, parent lookup, plugin registration, factory failure messages, ownership-mode mismatch errors, weak managed-object expiration, and concurrent registration/lookup.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/object_registry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/optimistic_transaction_db.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/optimistic_transaction_db.h

## Purpose
Defines the optimistic transaction DB wrapper and options. Optimistic transactions do not acquire pessimistic locks during operation; they validate conflicts at commit time.

## Important APIs, Types, And Functions
`OptimisticTransactionOptions` controls initial snapshot creation and comparator for `WriteBatchWithIndex`. `OccValidationPolicy` selects serial versus parallel validation. `OccLockBuckets` and `MakeSharedOccLockBuckets` expose a shareable lock-bucket pool for parallel validation. `OptimisticTransactionDBOptions` configures validation policy and lock buckets. `OptimisticTransactionDB::Open` and `BeginTransaction` are the public entry points.

## Control Flow
Open wraps a base DB in an optimistic transaction layer. `BeginTransaction` creates or reuses a transaction handle. Reads/writes are tracked in the transaction's indexed batch, and commit validates the tracked keys according to the selected OCC policy before writing.

## State And Persistence Behavior
The wrapper owns the underlying DB through `StackableDB`. Transaction state is in-memory until commit. Successful commits persist through normal RocksDB writes; failed conflict validation leaves the DB unchanged. Shared lock buckets are process-memory coordination structures and may be shared across DB instances.

## Dependencies And Integration Points
Depends on `Comparator`, `DB`, `Transaction`, `StackableDB`, and write-batch indexing behavior. It integrates with examples, transaction APIs in `transaction.h`, and validation performance tuning.

## Risks And Edge Cases
Range deletions are incompatible and return non-OK status. A non-default comparator must be supplied in transaction options to keep write-batch ordering consistent. Parallel validation reduces write-group contention but adds lock-bucket memory and lock ordering requirements. Reusing old transaction handles may retain allocated memory.

## Test Signals
Tests should cover conflict detection, snapshot isolation, serial versus parallel validation, shared lock-bucket memory usage, custom comparators, range-delete rejection, and handle reuse.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/optimistic_transaction_db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/option_change_migration.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/option_change_migration.h

## Purpose
Declares best-effort migration helpers that restructure an existing DB so it can be reopened with a new option set.

## Important APIs, Types, And Functions
`OptionChangeMigration(dbname, old_opts, new_opts)` handles a single column family. The multi-CF overload accepts old/new `DBOptions` and matching vectors of `ColumnFamilyDescriptor`.

## Control Flow
The implementation opens or processes the DB with old options, performs necessary LSM restructuring such as full compaction, and returns without applying the new options. The caller must reopen with the new options after successful migration.

## State And Persistence Behavior
This utility can rewrite persistent LSM state and run compactions. It does not modify the option files to apply `new_opts`; compatibility is achieved through data layout changes.

## Dependencies And Integration Points
Depends on `DB`, `Options`, `ColumnFamilyDescriptor`, and `Status`. It integrates with operational migrations between compaction styles or other format-sensitive options.

## Risks And Edge Cases
It is best-effort and can fail. Single-CF migration does not support multiple column families. Multi-CF migration requires the same CF count and names in the same order and does not add or drop CFs. Migrating from non-FIFO to FIFO with a low `max_table_files_size` can cause the DB to be dropped after migration if data exceeds the FIFO limit.

## Test Signals
Tests should cover valid option migration, CF count/name/order validation, migration failure propagation, post-migration reopen with new options, and the FIFO warning scenario with bounded test data.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/option_change_migration.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/options_type.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/options_type.h

## Purpose
Provides the public metadata framework used to parse, serialize, compare, prepare, and validate RocksDB options and custom extension options.

## Important APIs, Types, And Functions
`OptionType` enumerates supported storage/semantic types, including primitives, enums, structs, vectors, arrays, configurable/customizable objects, encoded strings, and string maps. `OptionVerificationType` controls comparison semantics such as by-name, deprecated, and alias. `OptionTypeFlags` controls mutability, pointer ownership, comparison level, nullability, serialization, preparation, and name-only serialization. `OptionTypeInfo` stores offset, type, flags, verification, and parse/serialize/equal/prepare/validate callbacks. Factory helpers include `Enum`, `Struct`, `Array`, `Vector`, `StringMap`, `AsCustomSharedPtr`, `AsCustomUniquePtr`, and `AsCustomRawPtr`.

## Control Flow
`OptionTypeInfo::Parse` converts a string into the value at an offset, either through custom callbacks or built-in type logic. `Serialize` emits a string representation. `AreEqual` compares two option values according to sanity level and verification mode. Static helpers parse whole option maps, nested structs, arrays, vectors, and brace-delimited tokens. Custom pointer helpers call `T::CreateFromString` and reset pointers on empty `id` assignments.

## State And Persistence Behavior
The metadata objects are normally static tables. Parsing mutates caller-owned option structs at configured byte offsets. Serialization produces option-file strings that affect durable compatibility checks, but the header itself persists nothing.

## Dependencies And Integration Points
Depends on `ConfigOptions`, `DBOptions`, `ColumnFamilyOptions`, `Status`, `Slice`, and STL containers. It is used by options parsing, options-file load/check, configurable object implementations, object registry integration, and extension/plugin authors.

## Risks And Edge Cases
Offset-based mutation is type-unsafe if metadata does not match the struct layout. Deprecated and alias options parse but do not serialize or compare. `ignore_unsupported_options` behavior for arrays/vectors temporarily disables and then selectively ignores unsupported elements. Brace/token parsing must handle nested braces and separators correctly. String maps hex-encode keys and values. Pointer flags must match actual ownership type.

## Test Signals
Tests should cover enum mapping failures, struct field addressing, nested brace tokenization, arrays with too few/many elements, vectors with unsupported elements, string-map hex round trips, custom pointer reset behavior, sanity-level comparisons, mutable-only parsing, prepare/validate hooks, and alias/deprecated serialization suppression.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/options_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/options_util.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/options_util.h

## Purpose
Declares utilities for loading RocksDB options from persisted option files and checking supplied options for compatibility with a DB's latest stored options.

## Important APIs, Types, And Functions
`LoadLatestOptions`, `LoadOptionsFromFile`, `GetLatestOptionsFileName`, and `CheckOptionsCompatibility` are the main functions. They populate `DBOptions`, `ColumnFamilyDescriptor` vectors, and optionally a shared block cache pointer.

## Control Flow
`LoadLatestOptions` finds the newest options file under a DB path and parses it. `LoadOptionsFromFile` parses a specified file. Pointer-valued options are initialized to defaults unless loadable through the object registry; block-based table factory options receive extra support. `CheckOptionsCompatibility` compares supplied options against persisted ones for options that cannot safely change.

## State And Persistence Behavior
The utilities read option files and produce in-memory option structs. They do not mutate the DB. Compatibility checks help prevent opening with incompatible persistent format-affecting options such as comparator, prefix extractor, table factory, merge operator, and user-defined timestamp persistence.

## Dependencies And Integration Points
Depends on `ConfigOptions`, `DBOptions`, `ColumnFamilyDescriptor`, `Env`, `Cache`, and the options parser. It integrates with `ldb`, examples, DB open workflows, and object registry customization for comparator/env/merge operator loading.

## Risks And Edge Cases
Forward compatibility depends on `ignore_unknown_options`. Pointer options often need caller repair after load. Missing options files return `NotFound`, which callers may treat differently from parse errors. Custom table factories and pointer-heavy table options may not fully round-trip.

## Test Signals
Tests should cover latest-file selection, missing options files, parse errors, unknown options with and without ignore flags, object-registry loading, block-based table options, compatibility mismatch messages, and multi-CF descriptors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/options_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/replayer.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/replayer.h

## Purpose
Defines the query-level trace replay interface used to replay captured RocksDB operations, either directly through DB APIs or tools like `db_bench`.

## Important APIs, Types, And Functions
`ReplayOptions` configures thread count and replay speed via `fast_forward`. `Replayer` exposes `Prepare`, `GetHeaderTimestamp`, `Next`, `Execute`, and `Replay`. `TraceRecord` and `TraceRecordResult` are forward-declared trace model types.

## Control Flow
Callers prepare the replayer, then either iterate records with `Next` and execute them manually with `Execute`, or call `Replay` to process the whole stream with timing delays adjusted by `fast_forward`. Result callbacks receive both wrapper execution status and operation-specific trace results.

## State And Persistence Behavior
Replayer state includes trace-reader position, prepared/reset state, and execution scheduling. Executing traces can mutate the target DB according to the captured operations. The trace stream itself is read, not modified.

## Dependencies And Integration Points
Depends on `Status`, callback functions, trace readers/writers through DB factory methods, and DB operation implementations. `DB::NewDefaultReplayer` in `StackableDB` forwards creation to the underlying DB.

## Risks And Edge Cases
`Next` and `Execute` can return `Incomplete` if `Prepare` was not called or the stream is exhausted. Unsupported trace types return `NotSupported`. Multi-threaded replay changes concurrency and timing, so results may differ from original execution if the workload has races. `fast_forward` values below, equal to, or above one have different timing semantics.

## Test Signals
Tests should cover prepare/reset behavior, header timestamp parsing, end-of-stream `Incomplete`, unsupported record types, result callback delivery, single-thread versus multi-thread replay, and timing scaling.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/replayer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/secondary_index.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/secondary_index.h

## Purpose
Defines the experimental transaction-layer secondary index interface and iterator used to query index entries by secondary value while exposing primary keys.

## Important APIs, Types, And Functions
`SecondaryIndex` configures primary/secondary column families, identifies the primary column name, optionally transforms primary column values, derives and finalizes secondary key prefixes, and optionally produces secondary values. `SecondaryIndexIterator` wraps an underlying iterator and provides `Seek`, `Next`, `Prev`, `PrepareValue`, `key`, `value`, `columns`, `timestamp`, `status`, `Valid`, and `GetProperty`.

## Control Flow
During transactional primary writes, RocksDB asks applicable indexes to update primary column value, compute a secondary key prefix, finalize that prefix, and generate optional secondary value. It then adds/removes secondary entries in the same transaction. Querying builds an iterator over the secondary column family; `Seek(target)` finalizes the search target and positions the underlying iterator on matching prefixed entries, while returned keys strip the secondary prefix.

## State And Persistence Behavior
Interface implementations hold column-family pointers and index-specific configuration. Secondary index entries are persisted as RocksDB key-values in the configured secondary column family, maintained transactionally with the primary write.

## Dependencies And Integration Points
Depends on `Iterator`, `Slice`, `Status`, `WideColumns`, `ColumnFamilyHandle`, `std::optional`, and `std::variant`. It integrates with `TransactionDBOptions::secondary_indices` and the transaction write path.

## Risks And Edge Cases
The feature is experimental. Applications must avoid primary and secondary key-space conflicts when sharing column families. Index methods must be thread-safe after initialization and deterministic for both maintenance and query paths. Non-OK status from an index method rolls back related transaction operations. Iterator validity depends on prefix matching and underlying iterator status.

## Test Signals
Tests should cover insert/update/delete maintenance, plain and wide-column indexing, separate versus shared CFs, prefix finalization, iterator forward/backward traversal, prepared-value mode, error rollback from each callback, and concurrent transaction updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/secondary_index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/secondary_index_faiss.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/secondary_index_faiss.h

## Purpose
Declares an experimental `SecondaryIndex` implementation backed by a FAISS inverted-file vector index for K-nearest-neighbor lookup over embedding columns.

## Important APIs, Types, And Functions
`FaissIVFIndex` owns a `faiss::IndexIVF`, stores a primary column name, primary/secondary CF pointers, implements all `SecondaryIndex` callbacks, and adds `FindKNearestNeighbors`. Helper functions `ConvertFloatsToSlice` and `ConvertSliceToFloats` convert between float embeddings and RocksDB slices.

## Control Flow
Transactional maintenance extracts embeddings from the primary column, maps them through the FAISS IVF index into secondary key prefixes/values, and persists secondary entries. KNN search uses a `SecondaryIndexIterator` for this index, validates target dimensionality and positive neighbor/probe counts, probes FAISS inverted lists, and returns primary keys with distances.

## State And Persistence Behavior
The object owns the FAISS index and an internal adapter. Secondary entries are persisted in RocksDB through transaction-layer index maintenance. Column-family pointers are runtime handles and are not owned by the index.

## Dependencies And Integration Points
Depends on FAISS `IndexIVF`, `SecondaryIndex`, `Slice`, `Status`, and STL vectors/pairs. It integrates with transaction secondary-index maintenance and vector search consumers.

## Risks And Edge Cases
The feature is experimental and requires a correctly trained FAISS IVF index. Embedding slices must exactly match `dim * sizeof(float)` and are endian/layout dependent. `reinterpret_cast` conversion assumes contiguous float memory and compatible alignment for reading. Search may return fewer than K results if probed lists are exhausted.

## Test Signals
Tests should cover construction preconditions, embedding dimension validation, primary/secondary CF configuration, index maintenance, KNN result ordering/distances, invalid neighbors/probes, insufficient candidates, and float slice conversion round trips.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/secondary_index_faiss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/secondary_index_simple.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/secondary_index_simple.h

## Purpose
Declares an experimental simple secondary index that indexes the configured primary column value as-is.

## Important APIs, Types, And Functions
`SimpleSecondaryIndex` implements `SecondaryIndex` and stores `primary_column_name_`, `primary_column_family_`, and `secondary_column_family_`. It implements column-family setters/getters, `GetPrimaryColumnName`, `UpdatePrimaryColumnValue`, `GetSecondaryKeyPrefix`, `FinalizeSecondaryKeyPrefix`, and `GetSecondaryValue`.

## Control Flow
For each maintained primary write, the simple index uses the primary column value directly as the secondary lookup component, finalizes the prefix to make entries unambiguous, and generally does not need to transform the stored primary column value.

## State And Persistence Behavior
The class holds only runtime configuration and CF handles. Persistent state is the secondary entries inserted/deleted by the transaction layer.

## Dependencies And Integration Points
Depends on `SecondaryIndex` and the transaction secondary-index machinery. It is a reference/simple implementation for value-to-primary-key lookup.

## Risks And Edge Cases
Indexing values as-is can create ambiguous or large secondary keys unless prefix finalization encodes boundaries safely. Applications still need key-space separation if primary and secondary entries share a CF. The implementation must remain deterministic and thread-safe after initialization.

## Test Signals
Tests should cover plain and wide-column values, duplicate values mapping to multiple primary keys, update/delete cleanup, prefix boundary safety, shared/dedicated CF usage, and iterator queries.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/secondary_index_simple.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/sim_cache.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/sim_cache.h

## Purpose
Declares a simulated cache wrapper used to estimate block-cache hit rates for alternate capacities without allocating the full simulated memory.

## Important APIs, Types, And Functions
`NewSimCache` creates a `SimCache` around a real cache or around separate simulation and real caches. `SimCache` derives from `CacheWrapper` and exposes `GetSimCapacity`, `GetSimUsage`, `SetSimCapacity`, hit/miss counters, `reset_counter`, `ToString`, and activity logging controls.

## Control Flow
The wrapper forwards normal cache behavior to the real cache while maintaining simulated cache metadata for lookups/adds. Capacity can be adjusted dynamically, purging simulated entries when needed. Optional activity logging records cache activity until stopped or size-limited.

## State And Persistence Behavior
Runtime state includes simulated cache entries, configured simulation capacity, hit/miss counters, and background logging status. Activity logs are persisted to the provided environment path when enabled; cache contents themselves are in-memory.

## Dependencies And Integration Points
Depends on `advanced_cache.h`, `CacheWrapper`, `Env`, `Statistics`, `Slice`, and `Status`. It integrates with block cache tuning, instrumentation, and performance experiments.

## Risks And Edge Cases
Pinned usage is always reported as zero because handlers are not exposed, so behavior is not identical to a real cache. Simulated capacity is not actual memory use; overhead depends on entry and block sizes. Logging can fail asynchronously and must be checked through `GetActivityLoggingStatus`. Capacity shrink must evict simulated entries correctly.

## Test Signals
Tests should cover hit/miss accounting, capacity changes, eviction on shrink, wrapping real cache operations, string stats, activity log start/stop/status, max log size, and shard-bit behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/sim_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/sorted_run_builder.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/sorted_run_builder.h

## Purpose
Declares `SortedRunBuilder`, a utility that uses an internal temporary RocksDB instance as an external sort engine to produce sorted SST files suitable for ingestion.

## Important APIs, Types, And Functions
`SortedRunBuilderOptions` configures temp directory, comparator, target SST size, compression, compaction threads, write-buffer memory, max write buffers, table factory, and `keep_temp_db`. `SortedRunBuilder::Create`, `Add`, `AddBatch`, `Finish`, `GetOutputFiles`, `GetNumEntries`, `GetDataSize`, `NewIterator`, and `Cleanup` define the lifecycle.

## Control Flow
Callers create a builder, add keys or write batches, call `Finish()` to flush and compact the temp DB into sorted non-overlapping SST files with sequence number zero, then retrieve output files or iterate sorted output. `Cleanup()` removes temporary state unless retention is requested.

## State And Persistence Behavior
Persistent temporary DB files are created under `temp_dir`. After finish, output SST files can be ingested into another DB with specific ingestion options. If `keep_temp_db` is true, the destructor does not clean up and callers must call `Cleanup()` explicitly.

## Dependencies And Integration Points
Depends on `Options`, `Comparator`, `Iterator`, `WriteBatch`, `TableFactory`, `Slice`, and `Status`. It integrates with `IngestExternalFile` workflows for bulk loading sorted data.

## Risks And Edge Cases
`temp_dir` is required. `Add` and `AddBatch` are thread-safe, but other methods must not run concurrently. Counts and size are approximate before `Finish()` and exact after. Duplicate keys can overcount before finish and are resolved in output. Wrong ingestion options can break snapshot consistency or file acceptance.

## Test Signals
Tests should cover empty and populated runs, duplicate keys, concurrent `Add`, `AddBatch`, custom comparator ordering, compression/table options, finish output file validity, iterator output, cleanup with and without `keep_temp_db`, and ingestion into a target DB.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/sorted_run_builder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/stackable_db.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/stackable_db.h

## Purpose
Defines `StackableDB`, a base wrapper for composing DB decorators such as TTL or transaction layers while forwarding the public `DB` API to an underlying root DB.

## Important APIs, Types, And Functions
Constructors support raw-pointer sole ownership, shared ownership, and unique ownership. `GetBaseDB` returns the immediate wrapped DB, and `GetRootDB` delegates through wrappers. The class overrides a broad DB surface: column-family lifecycle, reads/writes, entity/wide-column APIs, ingestion, snapshots, iterators, properties, compaction, background work, flush/WAL operations, live-file metadata, tracing/replay, options changes, table properties, WAL iteration, secondary catch-up, and resume.

## Control Flow
Each override forwards directly to `db_`, usually with `using DB::...` to preserve overloads. The destructor either deletes a raw owned DB or asserts that the shared pointer still matches `db_`. Wrapper subclasses override selected methods and inherit forwarding for the rest.

## State And Persistence Behavior
Local state is the wrapped `DB*` and optional owning `shared_ptr<DB>` that can actually hold either shared or unique ownership. Persistent behavior is whatever the underlying DB performs; `StackableDB` itself adds no durable state.

## Dependencies And Integration Points
Depends on `rocksdb/db.h` and is used by `DBWithTTL`, `TransactionDB`, `OptimisticTransactionDB`, and other wrappers. It integrates with virtually every DB operation by forwarding.

## Risks And Edge Cases
Forwarding wrappers must stay current with new `DB` virtual methods or wrapper users can hit base defaults unexpectedly. Raw-pointer ownership can double-delete if caller ownership assumptions are wrong. Some wrapper layers may need to intercept methods but accidentally inherit direct forwarding. Destruction requires the wrapped DB to outlive outstanding handles/iterators as usual.

## Test Signals
Tests should cover ownership constructor/destructor paths, `GetBaseDB`/`GetRootDB`, forwarding for representative read/write/admin methods, subclass overrides, close behavior, and API coverage when new DB methods are added.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/stackable_db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/table_properties_collectors.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/table_properties_collectors.h

## Purpose
Declares table-property collector factories for compaction triggers and helpers for extracting Unix write-time statistics from table properties.

## Important APIs, Types, And Functions
`CompactOnDeletionCollectorFactory` marks files for compaction based on tombstones in a sliding window or whole-file deletion ratio, with atomic setters/getters for window size, deletion trigger, deletion ratio, and minimum file size. `NewCompactOnDeletionCollectorFactory` constructs it. `CompactForTieringCollectorFactory` marks tiering-eligible files based on a trigger ratio and writes user properties. `DataCollectionUnixWriteTimeInfo` stores min/max/average write time plus tracked/untracked counts and helpers `DataCollectionIsEmpty`, `TrackedDataRatio`, and `HasInfinitelyOldData`. `GetDataCollectionUnixWriteTimeInfoForFile` and `GetDataCollectionUnixWriteTimeInfoForLevels` decode stats from table properties.

## Control Flow
Collector factories are installed in table options. During table building, collectors observe user keys and write table properties or mark files needing compaction based on current atomic thresholds. Write-time helpers read existing table properties and aggregate per-file or per-level statistics.

## State And Persistence Behavior
Factory thresholds are in-memory atomics and can be changed while the factory is reused. Collector outputs persist as SST table properties and `need_compaction` flags. Write-time info is derived from persisted table properties and returned in allocated structs.

## Dependencies And Integration Points
Depends on `TablePropertiesCollectorFactory`, `TableProperties`, `SystemClock`, and `Status`. It integrates with compaction picking, tiered storage decisions, table building, and DB property inspection.

## Risks And Edge Cases
Deletion-ratio values outside `(0,1]` disable ratio triggering. Sliding window size is rounded by the factory helper. File-size estimates during table building can be approximate. Tiering collector is disabled for CFs without tiering even if configured. Write-time ratios must be checked before interpreting min/max/average values.

## Test Signals
Tests should cover tombstone-window triggering, ratio triggering, disabled thresholds, minimum file size, dynamic setter effects, tiering user property output, write-time info extraction, empty/untracked data, level aggregation, and `ToString()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/table_properties_collectors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/transaction.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/transaction.h

## Purpose
Defines the core transaction interface shared by optimistic and pessimistic transaction DBs, including snapshots, reads, tracked writes, savepoints, conflict tracking, two-phase commit hooks, and transaction state.

## Important APIs, Types, And Functions
Type aliases include `TransactionName`, `TransactionID`, `TxnTimestamp`, and `kMaxTxnTimestamp`. `Endpoint` models finite and prefix-range endpoints with optional infinity suffix. `TransactionNotifier` reports deferred snapshot creation. `Transaction` exposes `SetSnapshot`, `SetSnapshotOnNextOperation`, `GetSnapshot`, timestamped snapshots, `ClearSnapshot`, `Prepare`, `Commit`, `CommitAndTryCreateSnapshot`, `Rollback`, savepoint APIs, transactional reads, `GetForUpdate`, range locks, iterators, coalescing/attribute iterators, tracked and untracked `Put`/`PutEntity`/`Merge`/`Delete`/`SingleDelete`, `CollapseKey`, log data, indexing control, counters, write-batch access, lock/deadlock timeout setters, write options, `UndoGetForUpdate`, rebuild, commit-time batch, names/ids, wait-for graph inspection, state access, and timestamp validation/commit setters.

## Control Flow
A transaction collects operations in an indexed write batch. Reads can see pending writes, while `GetForUpdate` also tracks or locks keys for conflict control. Snapshots define validation points, either immediately or on next operation. `Prepare` enters 2PC prepared state, `Commit` writes atomically and validates conflicts/locks, and `Rollback` discards or writes rollback state. Savepoints allow undoing recent batched operations. Indexing can be disabled for future writes, trading read-your-own-write behavior for performance.

## State And Persistence Behavior
Transaction state is mostly in-memory until commit or prepare. Prepared transactions can have durable WAL state and must be committed or rolled back before DB close. `log_number_`, transaction name, atomic transaction state, and id track lifecycle. Commit-time write batches bypass normal concurrency control and require caution. Timestamped snapshots can outlive the transaction through shared ownership.

## Dependencies And Integration Points
Depends on `DB`, `Comparator`, `Status`, `Iterator`, `WriteBatchWithIndex`, `ColumnFamilyHandle`, `Snapshot`, wide-column APIs, and transaction DB implementations. It integrates with both `OptimisticTransactionDB` and `TransactionDB`, examples, WAL recovery, 2PC, user-defined timestamps, and secondary index maintenance.

## Risks And Edge Cases
The object is not internally synchronized for caller access. `Commit` after successful `Prepare` can leave a transaction needing resolution on non-OK status. `Rollback` can itself return retryable I/O errors for prepared transactions. Disabling indexing makes later reads of those pending keys undefined. Direct writes to `GetWriteBatch()` can bypass transaction metadata. Commit-time batches bypass concurrency control. `UndoGetForUpdate` has count/savepoint restrictions. Snapshot pointers from `GetSnapshot()` become invalid after snapshot changes or transaction destruction.

## Test Signals
Tests should cover snapshot conflict boundaries, deferred snapshot notifier, 2PC prepare/commit/rollback recovery, savepoints, read-your-own-writes, merge-in-progress behavior, lock/conflict statuses, untracked writes, indexing disabled behavior, commit-time batch restrictions, transaction states, timestamp validation, and range locks where supported.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/transaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/transaction_db.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/transaction_db.h

## Purpose
Defines the pessimistic transaction DB wrapper, transaction DB options, lock manager extension points, deadlock reporting structures, timestamped snapshot APIs, and write optimization hints.

## Important APIs, Types, And Functions
`TxnDBWritePolicy` selects write-committed, write-prepared, or write-unprepared. `LockManagerHandle` and `RangeLockManagerHandle` expose custom/range lock managers, escalation barriers, lock status, counters, and range deadlock buffers. `NewRangeLockManager` constructs a range lock manager. `TransactionDBOptions` configures lock limits, deadlock buffers, lock table stripes, lock timeouts, custom mutex factory, write policy, rollback behavior, lock manager, concurrency-control skipping, write-batch flush thresholds, rollback deletion callback, UDT validation, secondary indices, and commit-bypass threshold. `TransactionOptions` configures per-transaction snapshots, deadlock detection, lock timeout, expiration, write-batch limits, prepare requirements, timestamp tracking, and large-transaction commit optimizations. `TransactionDB` adds optimized `Write`, disables direct transactional `DeleteRange`, static `Open`/`PrepareWrap`/`WrapDB`/`WrapStackableDB`, `BeginTransaction`, prepared transaction lookup, lock/deadlock status, and timestamped snapshot management.

## Control Flow
Open prepares DB/CF options, wraps a base DB, and installs transaction locking according to options. `BeginTransaction` creates or reuses a transaction that acquires locks on updates or `GetForUpdate`. Direct `Write` can use optimization hints to skip conflict checks when the caller guarantees safety. Timestamped snapshots are created and released through the DB wrapper, and prepared transaction lists expose recovery/management state.

## State And Persistence Behavior
The wrapper owns the base DB through `StackableDB` and maintains in-memory lock tables, deadlock buffers, transaction-name mappings, timestamped snapshot mappings, and optional secondary-index configuration. Committed transactions persist through DB writes; write-prepared and write-unprepared policies can persist prepared/uncommitted state requiring recovery and rollback handling.

## Dependencies And Integration Points
Depends on `DB`, `Comparator`, `StackableDB`, `Transaction`, `SecondaryIndex`, and custom mutex factory interfaces. It integrates with lock managers, range locking, MyRocks-specific compatibility options, secondary index maintenance, WAL recovery, timestamped snapshots, and DB open/wrap workflows.

## Risks And Edge Cases
Experimental write-prepared/write-unprepared policies have compatibility caveats. Negative lock timeouts can block indefinitely and lead to deadlocks. Forgotten transactions can hold locks forever unless expiration is set. `skip_concurrency_control` and write optimization hints rely on application correctness. Direct `DeleteRange` is not supported except through carefully optimized `Write`. Large-transaction memtable bypass is experimental and unsupported for some operation types. Secondary indices are experimental and require thread-safe deterministic implementations.

## Test Signals
Tests should cover lock acquisition/timeouts, deadlock detection buffers, range lock manager status/escalation, transaction expiration, prepared transaction recovery, write policies, optimized writes, direct `DeleteRange` rejection, timestamped snapshot lifecycle, secondary index maintenance, custom mutex factories, and large transaction commit bypass.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/transaction_db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/transaction_db_mutex.h -->
# sources/storage-engines/rocksdb/include/rocksdb/utilities/transaction_db_mutex.h

## Purpose
Declares pluggable mutex and condition-variable interfaces for applications that need custom synchronization primitives in `TransactionDB` locking.

## Important APIs, Types, And Functions
`TransactionDBMutex` exposes `Lock`, `TryLockFor`, and `UnLock`. `TransactionDBCondVar` exposes `Wait`, `WaitFor`, `Notify`, and `NotifyAll`. `TransactionDBMutexFactory` allocates mutex and condition-variable instances for the transaction DB.

## Control Flow
When configured through `TransactionDBOptions::custom_mutex_factory`, TransactionDB asks the factory for mutexes and condition variables. Locking code calls `Lock` or timed `TryLockFor`, waits on condition variables with the mutex held, and later notifies waiters when locks are released.

## State And Persistence Behavior
All state is runtime synchronization state in the custom primitives. Nothing is persisted. Correctness affects transactional lock ownership and wakeups.

## Dependencies And Integration Points
Depends on `Status` and `std::shared_ptr`. It integrates with pessimistic transaction lock tables and optional range lock managers.

## Risks And Edge Cases
Implementations must honor ownership, unlock, timeout, and spurious wakeup expectations. `WaitFor` may ignore timeouts, but doing so changes TransactionDB lock-timeout behavior. Returning non-OK statuses aborts waiting/acquisition. `UnLock` naming is fixed by the interface despite unusual casing. Implementations must not throw because RocksDB is not exception-safe.

## Test Signals
Tests should cover successful lock/unlock, timed lock timeout, condition wait/notify/notify-all, spurious wakeups, non-OK abort paths, integration with transaction lock timeout, and factory allocation counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/transaction_db_mutex.h -->
