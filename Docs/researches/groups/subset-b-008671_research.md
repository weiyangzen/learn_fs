# Research Group: subset-b-008671

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/db_options.cc -->
# sources/storage-engines/rocksdb/options/db_options.cc

Purpose: implements the DB-level option schema used by RocksDB's configurable options framework. It splits public `DBOptions` into `ImmutableDBOptions` and `MutableDBOptions`, registers option-name-to-field metadata, supports parsing/serialization/comparison, and emits option dumps for diagnostics.

Important APIs, types, and functions: the central data structures are the static `db_mutable_options_type_info` and `db_immutable_options_type_info` maps. They bind external option names to `offsetof(...)`, `OptionType`, verification mode, mutability flags, and optional custom parse/serialize/prepare/validate callbacks. `MutableDBConfigurable` registers mutable options and customizes equality for by-name fields and opt-map fallback. `DBOptionsConfigurable` extends that with immutable options, rebuilds a complete `DBOptions` through `BuildDBOptions`, and exposes the rebuilt object via `GetOptionsPtr`. Public helpers include `DBOptionsAsConfigurable`, `ImmutableDBOptions` and `MutableDBOptions` constructors, `Dump`, WAL-directory helpers, `GetMutableDBOptionsFromStrings`, `MutableDBOptionsAreEqual`, and `GetStringFromMutableDBOptions`.

Control flow: string parsing starts in the configurable layer, looks up each key in the static maps, and writes through offsets into an `ImmutableDBOptions` or `MutableDBOptions` instance. `DBOptionsConfigurable::ConfigureOptions` first lets `Configurable` parse registered fields, then rebuilds `db_options_` from the immutable/mutable snapshots and runs `PrepareOptions`. Equality flows through `OptionTypeInfo::AreEqual`, with `MutableDBConfigurable::OptionsAreEqual` suppressing false mismatches for by-name options that were absent from the parsed map. Dump flow is linear logging of all relevant fields.

State and persistence behavior: the file does not persist data directly, but defines which DB options are serializable, comparable, mutable, deprecated, or intentionally not serialized. Several runtime objects are marked `kCompareNever`, `kDontSerialize`, or by-name, including rate limiters, statistics, listeners, WAL filters, and file checksum factories. `ImmutableDBOptions` stores convenience pointers (`fs`, `clock`, `stats`, `logger`) derived from `Env` and shared pointers; callers must treat them as snapshots tied to the source `DBOptions`.

Dependencies and integration points: integrates with `options/options_helper.cc` for generic parsing/serialization, `options/options_parser.cc` for persisted option files, `Configurable`/`Customizable` registries, `Env`, `FileSystem`, `RateLimiter`, `EventListener`, `Statistics`, `WalFilter`, and cache-related types. The special `env` entry invokes `Env::CreateFromString`, `PrepareOptions`, and `ValidateOptions`; the `listeners` entry tokenizes listener strings and creates objects through `EventListener::CreateFromString`.

Risks: adding a new `DBOptions` field requires updating the correct static map, constructor split, `BuildDBOptions`, dumps, tests, and possibly persistence verification semantics. Offset-based parsing is fragile when fields are omitted or types change. `ImmutableDBOptions` assumes `env` is non-null in normal construction; `DBOptionsConfigurable` guards null env by substituting `Env::Default()` before snapshotting. Deprecated aliases intentionally parse as no-ops, which helps compatibility but can hide stale configuration. WAL directory equality falls back to string comparison when `Env::AreFilesSame` is unsupported.

Test signals: `options_settable_test.cc` has `DBOptionsAllFieldsSettable`, which detects fields not covered by `GetDBOptionsFromString` and checks `BuildDBOptions` writes all non-excluded fields. Parser round-trip verification in `PersistRocksDBOptions` exercises `DBOptionsAsConfigurable` through `VerifyDBOptions`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/db_options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/db_options.h -->
# sources/storage-engines/rocksdb/options/db_options.h

Purpose: declares RocksDB's internal DB option snapshots. `ImmutableDBOptions` captures fields that are fixed after open, while `MutableDBOptions` captures DB-level fields that can be adjusted through the mutable-options pipeline.

Important APIs, types, and functions: `ImmutableDBOptions` exposes constructors from default `DBOptions` or an existing `DBOptions`, `Dump(Logger*)`, WAL directory helpers, and a broad set of DB-level fields including creation flags, file system/environment objects, WAL controls, logging, cache, checksum, compaction service, follower catchup knobs, and write temperatures. `MutableDBOptions` exposes analogous constructors and `Dump(Logger*)` for runtime-tunable fields such as background jobs, WAL size, sync rates, manifest limits, stats cadence, off-peak window, and SST open behavior. Free functions serialize, parse, and compare mutable DB options.

Control flow: callers create snapshots from public `DBOptions`, pass them through configurable helpers for parsing or comparison, and rebuild a public `DBOptions` using functions declared in `options_helper.h`. WAL helper methods choose either the explicit `wal_dir` or the first DB path/default path supplied by the caller.

State and persistence behavior: this header is state-definition only, but it establishes persistence boundaries. Immutable fields are usually written to options files as DB options and are not expected to change live. Mutable fields can be serialized with `GetStringFromMutableDBOptions` and parsed from maps for dynamic updates. Convenience members (`fs`, `clock`, `stats`, `logger`) are derived, not independent persisted options.

Dependencies and integration points: includes `rocksdb/options.h` and references `SystemClock`, `Logger`, `Env`, `RateLimiter`, `SstFileManager`, `Statistics`, `WriteBufferManager`, `EventListener`, `Cache`, `WalFilter`, `FileChecksumGenFactory`, and `CompactionService`. It is consumed by `db_options.cc`, `options_helper.cc`, parser verification, DB open/reconfiguration paths, and diagnostic dump paths.

Risks: the struct declarations must stay synchronized with static option metadata in `db_options.cc`, copy/build functions in `options_helper.cc`, and all-fields settable tests. Adding fields without updating those locations can silently break options-file persistence, dynamic configuration, or byte-coverage tests. Direct access to `wal_dir` can be wrong; callers should use `GetWalDir`/`IsWalDirSameAsDBPath` as the comment states.

Test signals: the main direct signal is `DBOptionsAllFieldsSettable`, which enumerates excluded non-scalar fields and asserts string parsing plus snapshot rebuild covers the rest. Parser round-trip tests elsewhere also depend on these declarations matching the registered option maps.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/db_options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/offpeak_time_info.cc -->
# sources/storage-engines/rocksdb/options/offpeak_time_info.cc

Purpose: implements parsing and evaluation for the daily off-peak UTC time range used by mutable DB options such as `daily_offpeak_time_utc`.

Important APIs, types, and functions: `OffpeakTimeOption::OffpeakTimeOption()` delegates to the string constructor with an empty range. `SetFromOffpeakTimeString` calls `TryParseTimeRangeString` to populate `daily_offpeak_start_time_utc` and `daily_offpeak_end_time_utc`, and only updates `daily_offpeak_time_utc` when parsing succeeds. `GetOffpeakTimeInfo` evaluates a Unix-time-like `current_time` and returns `OffpeakTimeInfo` with `is_now_offpeak` and `seconds_till_next_offpeak_start`.

Control flow: parsing saves the old start/end values, attempts to parse the new string, commits the display string on success, and restores start/end on failure. Evaluation returns default false/zero if start equals end, floors current time to the nearest minute for in-window checks, handles both same-day and overnight ranges, and computes the next start by either subtracting from today's start or wrapping by one day.

State and persistence behavior: state is in-memory and consists of the original accepted string plus parsed start/end seconds from midnight UTC. Invalid updates do not overwrite the accepted string or parsed times, so a bad runtime option update leaves the previous schedule intact. The option string itself is persisted as a regular mutable DB option by the surrounding options machinery.

Dependencies and integration points: uses `TryParseTimeRangeString` from `util/string_util.h`; includes `rocksdb/system_clock.h` but this implementation takes the current timestamp as an argument instead of reading a clock directly. It integrates with `MutableDBOptions::daily_offpeak_time_utc` and compaction scheduling logic that can use the returned `OffpeakTimeInfo`.

Risks: `current_time % 86400` assumes non-negative epoch seconds; negative timestamps would produce negative seconds since midnight in C++. The range comparison is inclusive at both start and end after minute truncation. Empty or invalid ranges collapse to start == end, which disables off-peak behavior. The function computes seconds to next start even when already off-peak, returning the next day's start rather than zero.

Test signals: no local test in this subset directly targets `OffpeakTimeOption`; indirect coverage comes from `DBOptionsAllFieldsSettable`, which parses `daily_offpeak_time_utc=08:30-19:00` as a mutable DB string field. Dedicated boundary tests for overnight windows, invalid updates, and minute rounding would reduce risk.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/offpeak_time_info.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/offpeak_time_info.h -->
# sources/storage-engines/rocksdb/options/offpeak_time_info.h

Purpose: declares the small off-peak scheduling model used by RocksDB options code to represent daily UTC maintenance windows.

Important APIs, types, and functions: `OffpeakTimeInfo` is a result struct containing `is_now_offpeak` and `seconds_till_next_offpeak_start`. `OffpeakTimeOption` stores constants for day/hour/minute lengths, constructors, the original `daily_offpeak_time_utc` string, parsed `daily_offpeak_start_time_utc` and `daily_offpeak_end_time_utc`, plus `SetFromOffpeakTimeString` and `GetOffpeakTimeInfo`.

Control flow: users construct or update the option from a string, then ask for off-peak status at a supplied timestamp. The implementation is intentionally clock-independent at the public method boundary, which makes scheduling callers responsible for obtaining UTC time.

State and persistence behavior: the persisted representation is the string form; parsed integer fields are derived runtime state. Defaults leave all fields empty/zero, which the implementation treats as no off-peak window.

Dependencies and integration points: references `rocksdb/rocksdb_namespace.h` and forward-declares `SystemClock`. It is conceptually tied to `MutableDBOptions::daily_offpeak_time_utc` and compaction trigger scheduling but has no heavy RocksDB dependencies in the header.

Risks: callers may confuse UTC strings with local time. Start/end seconds are public fields, so external mutation can bypass parse validation. The all-zero default is both a valid internal sentinel and a possible parsed equal-start/end state, so consumers should rely on `GetOffpeakTimeInfo`.

Test signals: this header has no direct test in the subset. It is indirectly represented by DB options parsing tests for the string field; algorithmic tests should cover same-day ranges, overnight ranges, equal endpoints, invalid strings, and exact boundary minutes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/offpeak_time_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/options.cc -->
# sources/storage-engines/rocksdb/options/options.cc

Purpose: implements constructors, dump methods, compatibility defaults, and tuning helpers for public RocksDB option classes.

Important APIs, types, and functions: constructors include `AdvancedColumnFamilyOptions`, `ColumnFamilyOptions`, `DBOptions`, and conversions from combined `Options`. Dump methods include `DBOptions::Dump`, `ColumnFamilyOptions::Dump`, `Options::Dump`, and `Options::DumpCFOptions`. Tuning helpers include `PrepareForBulkLoad`, `OptimizeForSmallDb`, `DisableExtraChecks`, `OldDefaults`, `OptimizeForPointLookup`, `OptimizeLevelStyleCompaction`, `OptimizeUniversalStyleCompaction`, and `IncreaseParallelism`. It also defines simple `ReadOptions` and `WriteOptions` constructors.

Control flow: constructors copy fields from combined `Options` into narrower option structs and ensure vector sizes such as `max_bytes_for_level_multiplier_additional` match `num_levels`. Dump functions log DB and CF fields in a deterministic diagnostic pass, delegating DB dumps through `ImmutableDBOptions` and `MutableDBOptions`. Optimization helpers mutate the receiver in place and return `this` for fluent use.

State and persistence behavior: this file mutates in-memory option objects but does not directly persist them. Its defaults and optimization helpers influence what later gets serialized by the options parser. `OldDefaults` intentionally rewrites fields to emulate prior RocksDB versions, affecting compatibility and restored behavior from old configurations.

Dependencies and integration points: relies on logging, compression helpers, cache/table factories, bloom filters, memtable/table/merge/filter abstractions, and `options/db_options.h`. `IncreaseParallelism` reaches into `Env` to set LOW and HIGH background thread counts, so it has side effects beyond the option object. `OptimizeForSmallDb` shares an LRU cache between DB and block-based table options through `WriteBufferManager` and `BlockBasedTableFactory`.

Risks: tuning helpers encode policy, not validation; bad caller-provided budgets can produce awkward derived values such as tiny file sizes. `IncreaseParallelism` mutates the environment immediately, which can surprise callers expecting option-only changes. Dump code must stay synchronized with evolving option fields or diagnostics will omit important settings. Compatibility defaults depend on version comparisons and can drift when defaults change elsewhere.

Test signals: this subset's settable test checks copy paths through DB/CF mutable and immutable conversions. Broader RocksDB tests likely exercise tuning helpers via DB open and compaction behavior. There is no direct assertion here that every dumped field is complete.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/options_helper.cc -->
# sources/storage-engines/rocksdb/options/options_helper.cc

Purpose: provides the generic option parsing, serialization, comparison, validation, and conversion machinery used by DB, column-family, table, and nested configurable options.

Important APIs, types, and functions: `ConfigOptions` constructors initialize an object registry and environment. `ValidateOptions` delegates validation to DB and CF configurables. `BuildDBOptions`, `BuildColumnFamilyOptions`, and `UpdateColumnFamilyOptions` copy immutable/mutable snapshots back into public option structs. Static maps translate enum values for compaction style/priority/stop style, temperature, checksum, compression, encoding, and blob cache prepopulation. `StringToMap` and `MapToString` convert semicolon-delimited option strings while preserving nested braced values. `GetStringFrom*` and `Get*FromString/Map` are public conversion entry points. `OptionTypeInfo` methods implement tokenization, brace stripping, parse, serialize, equality, prepare, validate, and nested lookup behavior.

Control flow: parse entry points turn strings into maps, create a `Configurable` wrapper for the base options, and call `ConfigureFromMap`. Each key is resolved through `OptionTypeInfo::Find`; scalar types go through `ParseOptionHelper`, custom/configurable/customizable fields go through callbacks or object registries, and unrecognized fields either populate an unused map or raise depending on `ConfigOptions`. Serialization iterates type maps, skips deprecated or non-serializable options, and appends `key=value` using the configured delimiter. Equality iterates registered fields and respects configured sanity levels, by-name verification, custom equality functions, and nested configurable comparisons.

State and persistence behavior: the helpers are the backbone for options-file persistence and runtime updates. They copy from a caller-provided base object, so failed string-map parsing usually preserves the base. Braced nested values are deliberately preserved by `StringToMap`, then stripped one layer for scalar parsing where needed. `BuildDBOptions` and `UpdateColumnFamilyOptions` are the canonical persistence-to-runtime reconstruction paths.

Dependencies and integration points: integrates with `cf_options.h`, `db_options.h`, `rocksdb/convenience.h`, cache/filter/memtable/table factories, object registries, compression utilities, and low-level unaligned integer helpers. Parser code, `SetOptions`, options-file verification, and tests all depend on this file's semantics.

Risks: this file is highly schema-sensitive. Every new field needs map metadata, copy/update logic, and often tests. Offset-based writes require exact field types and alignment handling. `StringToMap` must balance compatibility with unambiguous nested parsing; changes can break persisted option strings. Serialization order follows unordered maps for some schemas, so consumers should not rely on stable textual order unless the higher layer imposes one. By-name comparison can mask object differences when only names are available.

Test signals: `options_settable_test.cc` directly targets this machinery by verifying all settable fields are covered for block table options, table properties, DB options, and column-family options. Options parser round-trip verification also exercises `GetStringFromDBOptions`, `GetStringFromColumnFamilyOptions`, and equivalence checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/options_helper.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/options_helper.h -->
# sources/storage-engines/rocksdb/options/options_helper.h

Purpose: declares the shared option helper API and enum-name registries used across RocksDB options parsing, serialization, validation, and conversion.

Important APIs, types, and functions: exposes supported compression/checksum discovery, `ValidateOptions`, DB/CF rebuild helpers, configurable wrapper factories, `StringToMap`, `GetStringFromCompressionType`, and the `OptionsHelper` static registry holder. `OptionsHelper` publishes canonical names for DB and CF option structs and maps for compaction styles, priorities, stop styles, temperatures, checksum types, compression types, prepopulate blob cache modes, and encodings. Header-level aliases provide convenient references to those maps.

Control flow: callers use this header to route option conversion without knowing implementation details. DB and CF modules register themselves as `Configurable` through the declared factories; parser and convenience APIs convert between strings/maps and option objects through the declared helpers.

State and persistence behavior: the header declares global static maps whose contents define persisted textual enum names. Changing a string or removing an alias can break options-file compatibility. `StringToMap`'s contract is important for persistence because nested option values remain reusable in `key=value;` contexts.

Dependencies and integration points: includes advanced/public RocksDB option headers, status, and table APIs; forward declares DB/CF mutable and immutable option structs. It sits between `db_options.cc`, `cf_options.cc`, table option code, parser persistence, and public convenience functions.

Risks: static aliases in a header make the registry easy to use but increase coupling to initialization and naming. The checksum helper assumes a contiguous enum range from `kNoChecksum` to `kXXH3`; future enum layout changes would need review. Declared helpers must stay consistent with implementations in `options_helper.cc`.

Test signals: settable tests and parser verification indirectly validate the maps and helper declarations. Unsupported compression discovery depends on runtime compression support and is harder to cover deterministically across builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/options_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/options_parser.cc -->
# sources/storage-engines/rocksdb/options/options_parser.cc

Purpose: implements RocksDB options-file persistence, parsing, validation, and round-trip verification for DB, column-family, and table-factory options.

Important APIs, types, and functions: `PersistRocksDBOptions` writes the options file and verifies it. `RocksDBOptionsParser::Reset`, `Parse`, `IsSection`, `ParseSection`, `ParseStatement`, `CheckSection`, `EndSection`, `ParseVersionNumber`, `ValidityCheck`, and `TrimAndRemoveComment` implement the parser. Static verification helpers compare parsed files against live `DBOptions`, `ColumnFamilyOptions`, and `TableFactory` instances.

Control flow: persistence builds a `ConfigOptions`, writes a header, `[Version]`, `[DBOptions]`, one `[CFOptions "name"]` per column family, and optional `[TableOptions/<factory> "name"]` sections, then syncs/closes the file and calls `VerifyRocksDBOptionsFromFile`. Parsing resets state, opens a sequential file, reads line by line with optional readahead, strips comments, ends the previous section when a new section starts, parses section titles/arguments or `name=value` statements, and dispatches each completed section in `EndSection`. If parsing hits corruption/invalid argument and the filesystem supports verify-and-reconstruct reads, it retries once with reconstruction.

State and persistence behavior: parser state includes parsed `DBOptions`, raw DB option map, CF names/options/maps, version presence, DB/default-CF presence, and parsed RocksDB/options-file versions. Validity requires one DB options section and a default CF section. Section order matters: the default CF must be first, table options require a previously declared CF, duplicate DB/version/CF sections are rejected. Unknown options may be ignored only according to `ConfigOptions` and version logic.

Dependencies and integration points: uses file readers/writers, `FileSystem`, `WritableFileWriter`, DB/CF option conversion helpers, `TableFactory::CreateFromString`, public convenience APIs, sync points for tests, and string escape/unescape helpers. DB open and OPTIONS file management depend on this code for durable option snapshots.

Risks: parser supports only single-line statements, so serializers must keep nested content compatible with that format. Comment stripping treats unescaped `#` as a comment boundary. Unknown-option handling changes after reading the version section if the file was not generated by a higher RocksDB version. Table-factory deserialization is optional; unsupported factories result in a null table factory and OK status, which verification may only catch depending on sanity level and factory availability.

Test signals: persistence has `TEST_SYNC_POINT` hooks. Round-trip verification exercises `VerifyDBOptions`, `VerifyCFOptions`, and `VerifyTableFactory`. Settable tests feed the helper layer used here, but this subset does not include parser-specific tests for malformed sections, reconstruction retry, or comments.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/options_parser.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/options_parser.h -->
# sources/storage-engines/rocksdb/options/options_parser.h

Purpose: declares the RocksDB options file format constants, persistence entry points, and parser class API.

Important APIs, types, and functions: defines `ROCKSDB_OPTION_FILE_MAJOR` and `ROCKSDB_OPTION_FILE_MINOR`, `OptionSection`, and `opt_section_titles`. Declares two `PersistRocksDBOptions` overloads, one with default config and one with explicit `ConfigOptions`. `RocksDBOptionsParser` exposes `Parse`, `Reset`, accessors for parsed DB/CF options and raw maps, `GetCFOptions`, `NumColumnFamilies`, verification helpers, `ExtraParserCheck`, and `ParseStatement`. Protected methods cover section parsing/checking, section finalization, validity checks, error construction, and version parsing.

Control flow: clients either persist live options to a named file or instantiate a parser, call `Parse`, and inspect `db_opt`, `cf_names`, `cf_opts`, and maps. Verification helpers are static so persistence and external callers can compare a file against expected option objects without manually walking parser state.

State and persistence behavior: member state records one DB option object/map, ordered CF names/options/maps, required-section flags, and version arrays. The format is section-based: version, DB options, CF options, and table-options sections identified by title prefixes and optional quoted arguments.

Dependencies and integration points: includes filesystem environment and public options headers. It is implemented by `options_parser.cc` and consumed by DB option file persistence/open verification paths. Table factories and configurable option registries are integrated behind the implementation boundary.

Risks: `opt_section_titles` is a static array in the header, so translation units get their own internal copy; this is acceptable for constants but not suitable for mutable shared state. The parser API returns pointers to internal vectors/maps, so callers must not retain them after parser reset/destruction. Format version constants require coordinated changes to parser compatibility logic.

Test signals: static `ParseStatement` and `TrimAndRemoveComment` are easy unit-test targets. Persistence verification is the strongest integration signal because it writes then parses and compares all sections.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/options_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/options_settable_test.cc -->
# sources/storage-engines/rocksdb/options/options_settable_test.cc

Purpose: provides regression tests that detect newly added option fields that cannot be set through RocksDB's string/configuration parsing APIs.

Important APIs, types, and functions: helper routines `FillWithSpecialChar`, `NumUnsetBytes`, and `CompareBytes` operate on raw object storage while skipping excluded field ranges. Test cases include `BlockBasedTableOptionsAllFieldsSettable`, `TablePropertiesAllFieldsSettable`, `DBOptionsAllFieldsSettable`, and `ColumnFamilyOptionsAllFieldsSettable`. The test binary installs the stack trace handler, initializes GoogleTest, and optionally parses gflags.

Control flow: each test allocates raw memory for the target option struct, fills all non-excluded bytes with a sentinel, constructs or copies a default object to count padding bytes, then parses a comprehensive option string into a second sentinel-filled object. The assertion compares remaining sentinel bytes against the expected padding count; if a real field remains untouched, the count changes and the test fails. Some tests add explicit semantic checks for pointer/custom fields or nested structs that must be excluded from raw byte comparison.

State and persistence behavior: tests do not persist files, but they validate the in-memory parse targets that persisted option strings rely on. `DBOptionsAllFieldsSettable` also checks that `BuildDBOptions({}, {}, *options)` initializes all non-excluded fields. The CF test checks round-tripping from `ColumnFamilyOptions` through `MutableCFOptions` and back using byte comparison over mutable fields.

Dependencies and integration points: includes `cf_options.h`, `db_options.h`, `options_helper.h`, public convenience APIs, and RocksDB test harness. It exercises block-based table option parsing, `TableProperties::Parse`, `GetDBOptionsFromString`, `GetColumnFamilyOptionsFromString`, `BuildDBOptions`, `MutableCFOptions`, and `BuildColumnFamilyOptions`.

Risks: the file openly depends on compiler behavior around padding bytes and is disabled for clang, UBSAN, and some status-check configurations. Excluded offset ranges must stay sorted and accurate; wrong exclusions can hide missing parser coverage or produce false failures. Because tests use large hand-written option strings, schema updates require careful edits in multiple places.

Test signals: these are themselves the test signals for the options schema. Failing comments explain the required fix path: add the new option to the appropriate parser/config metadata and update the test string or excluded list for complex fields. The platform guards mean CI coverage may be incomplete on unsupported compiler/sanitizer combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/options_settable_test.cc -->
