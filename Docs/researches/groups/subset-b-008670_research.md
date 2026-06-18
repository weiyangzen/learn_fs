# Research: subset-b-008670

Grouped research for RocksDB option/configurable sources. Each section preserves the original source path and is intended for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/cf_options.cc -->
# sources/storage-engines/rocksdb/options/cf_options.cc

## Purpose
`cf_options.cc` implements RocksDB column-family option registration, parsing, serialization, comparison adapters, and derived mutable column-family calculations. It is the bridge between public `ColumnFamilyOptions`/`Options` structs and the generic `Configurable`/`OptionTypeInfo` infrastructure used by options files, `SetOptions`, and object-registry-backed factories. The file also preserves many deprecated option names so old `OPTIONS` files remain readable.

## Important APIs, Types, and Functions
The file defines `ParseCompressionOptions`, `TableFactoryParseFn`, `CFOptionsAsConfigurable(const MutableCFOptions&)`, `CFOptionsAsConfigurable(const ColumnFamilyOptions&, const unordered_map* opt_map)`, `ImmutableCFOptions` and `ImmutableOptions` constructors, `MultiplyCheckOverflow`, `MaxFileSizeForLevel`, `MaxFileSizeForL0MetaPin`, `MutableCFOptions::RefreshDerivedOptions`, `MutableCFOptions::Dump`, `GetMutableOptionsFromStrings`, and `GetStringFromMutableCFOptions`.

The large `cf_mutable_options_type_info` and `cf_immutable_options_type_info` maps are the main data contract. They map option names to offsets, scalar or structured types, verification modes, mutability flags, custom parse functions, and compatibility aliases/deprecated entries. Special nested maps cover `CompressionOptions`, FIFO compaction options, universal compaction options, and file-temperature age thresholds.

## Control Flow
Parsing generally enters through `OptionTypeInfo::ParseType`, `ConfigurableHelper`, or a `ConfigurableCFOptions` wrapper. Mutable and immutable maps drive field updates by offset. `ConfigurableCFOptions::ConfigureOptions` first delegates to generic configuration, then copies the parsed mutable and immutable snapshots back into a full `ColumnFamilyOptions`, and finally prepares nested options. `TableFactoryParseFn` handles the most complex branch: it first attempts mutable-only updates on an existing table factory, otherwise clones or creates a block/plain table factory, configures the clone, and swaps the shared pointer only on success.

Derived sizing flow is separate. `RefreshDerivedOptions` fills `max_file_size` for each level, treating universal L0 as unbounded and multiplying later levels with overflow protection. `MaxFileSizeForLevel` either indexes precomputed sizes directly or adjusts by dynamic base level for leveled compaction.

## State and Persistence Behavior
The file does not persist data itself, but it defines the serialized option names and compatibility behavior used to read/write RocksDB `OPTIONS` files and mutable option strings. Deprecated names are kept as parseable no-op or alias entries. Failed mutable parsing resets `new_options` to `base_options`; table-factory mutation avoids exposing partially configured clones. Raw pointers in immutable options are non-owning snapshots while shared pointers preserve ownership through public option structs.

## Dependencies and Integration Points
This file depends on `options_helper`, `options_parser`, `configurable_helper`, `rocksdb/options.h`, table factories, caches, merge operators, compaction filters, slice transforms, compression utilities, and `ObjectRegistry`-based factories. It integrates with DB open/options-file parsing, `SetOptions`, table factory instantiation, blob options, compaction logic, logging, and sanity comparison.

## Risks
Offset-based option maps are fragile: every field rename/type change must update the corresponding `offsetof` entry and flags. Backward-compatible parsers such as colon-delimited compression parsing and old FIFO scalar parsing can hide malformed input if not tested. `TableFactoryParseFn` is concurrency-sensitive; the clone-before-swap pattern is important because existing readers can observe the old factory. Derived sizes can become wrong when `RefreshDerivedOptions` is not called after mutating size-related fields.

## Test Signals
The companion configurable/customizable tests exercise CF option wrappers, table factory creation by name, nested configurable serialization, mutable-only behavior, and object registry loading. Additional coverage likely exists in RocksDB options-file and DB options tests because this file is a core parser for persisted `OPTIONS` content.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/cf_options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/cf_options.h -->
# sources/storage-engines/rocksdb/options/cf_options.h

## Purpose
`cf_options.h` declares RocksDB internal column-family option snapshots. It separates fields that are immutable over a DB/column-family lifetime from fields that may be changed through mutable options, and exposes helpers for derived compaction/file-size behavior plus string conversion.

## Important APIs, Types, and Functions
`ImmutableCFOptions` stores long-lived column-family configuration such as compaction style/priority, comparator and internal comparator, merge operator, compaction filters, memtable factory, bloom locality, number of levels, consistency flags, CF paths, blob direct-write settings, timestamp persistence, ingest-behind allowance, and batch lookup optimization.

`ImmutableOptions` combines `ImmutableDBOptions` with `ImmutableCFOptions` and provides constructors for public `Options`, split DB/CF options, and already immutable snapshots.

`MutableCFOptions` contains runtime-changeable memtable, compaction, blob, compression, temperature, protection, verification, and miscellaneous controls. It includes constructors from `ColumnFamilyOptions`, `Options`, and a zero/default constructor. Public methods include `RefreshDerivedOptions`, `MaxBytesMultiplerAdditional`, `Dump`, equality comparison, and helpers declared outside the struct: `MultiplyCheckOverflow`, `MaxFileSizeForLevel`, `MaxFileSizeForL0MetaPin`, `GetStringFromMutableCFOptions`, and `GetMutableOptionsFromStrings`.

## Control Flow
Construction from `ColumnFamilyOptions` copies public fields into a compact mutable snapshot and immediately calls `RefreshDerivedOptions(options.num_levels, options.compaction_style)`. Later callers that modify fields affecting derived state must call `RefreshDerivedOptions` again. Immutable construction copies non-owning raw pointers and owning shared pointers from the public options into an internal snapshot.

## State and Persistence Behavior
The header defines in-memory state only. Persistence is mediated by `cf_options.cc` option maps and serializers. `MutableCFOptions::max_file_size` is derived, not source-of-truth persisted state. Shared pointers in mutable options such as table factory, prefix extractor, compression manager, and immutable options such as merge operator and memtable factory preserve object lifetime; raw fields such as `user_comparator` and `compaction_filter` are explicitly non-owning.

## Dependencies and Integration Points
The header depends on `db/dbformat.h`, `options/db_options.h`, `rocksdb/options.h`, and compression utilities. It is consumed throughout the DB core for memtable creation, compaction picking, flush/write throttling, blob handling, iterator behavior, and option logging. The string conversion declarations integrate with `ConfigOptions` and the generic option parser.

## Risks
The largest risk is mismatch between public `ColumnFamilyOptions`, `MutableCFOptions`, and the `OptionTypeInfo` maps in the `.cc` file. Adding a mutable field requires constructor initialization, default initialization, serialization map entries, dump output if operationally useful, and derived refresh if it affects computed state. Missing `RefreshDerivedOptions` after mutable updates can leave compaction file-size decisions stale.

## Test Signals
Tests in `configurable_test.cc`, `customizable_test.cc`, and broader RocksDB options tests exercise the configurable wrappers and mutable-only configuration. Debug-only helpers expose accidental immutable entries in the mutable option map.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/cf_options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/configurable.cc -->
# sources/storage-engines/rocksdb/options/configurable.cc

## Purpose
`configurable.cc` implements the generic `Configurable` engine used by RocksDB option-bearing objects. It registers option maps against object substructures, configures options from strings/maps, serializes options back to text, lists option names, validates/prepares nested options, compares two objects for sanity, and parses object IDs plus property maps.

## Important APIs, Types, and Functions
Core `Configurable` methods include `RegisterOptions`, `PrepareOptions`, `ValidateOptions`, `GetOptionsPtr`, `ConfigureFromMap`, `ConfigureOptions`, `ConfigureFromString`, `ConfigureOption`, `ParseOption`, `GetOptionString`, `ToString`, `SerializeOptions`, `GetOption`, `GetOptionNames`, `AreEquivalent`, `OptionsAreEqual`, and static `GetOptionsMap`.

`ConfigurableHelper` implements the workhorse static functions declared in `configurable_helper.h`: `FindOption`, `ConfigureOptions`, `ConfigureSomeOptions`, `ConfigureSingleOption`, `ConfigureCustomizableOption`, `ConfigureOption`, `GetOption`, `SerializeOptions`, `ListOptions`, and `AreEquivalent`.

## Control Flow
`RegisterOptions` stores a name, `OptionTypeInfo` map pointer, and byte offset from the object to the registered substructure. Later operations use `ApplyOffset` to recover the current pointer even after copying the object.

`ConfigureFromString` chooses between map parsing (`;` or `=` present) and class-specific `ParseStringOptions`. `ConfigureOptions` snapshots current serialized state before changes when unknown options are not ignored, applies updates with prepare disabled, invokes `PrepareOptions` at the end if requested, and rolls back by reconfiguring from the snapshot on failure.

`ConfigureSomeOptions` repeatedly scans remaining option pairs until no further entries are consumed. That supports ordering-sensitive nested configurable updates where one option may instantiate an object and later options configure its children. Unsupported options are tracked separately from invalid parsed options so ignore flags can control the final status.

`ConfigureCustomizableOption` handles `Customizable` ID changes, nested property assignment, mutable-only constraints, null values, and property maps for existing objects. Serialization and comparison iterate registered maps and delegate scalar/nested work to `OptionTypeInfo`.

## State and Persistence Behavior
The class itself persists only registration metadata in `options_`. It does not own registered option memory. Serialized strings are used for options files, rollback snapshots, and equivalence round-trips. Rollback is best-effort and relies on the object's serializer being detailed enough to reconstruct the prior state.

## Dependencies and Integration Points
Dependencies include logging, `options_helper`, `configurable_helper`, `Customizable`, `ObjectRegistry`, `OptionTypeInfo`, coding helpers, and string utilities. This implementation is shared by DB options, CF options, table factories, caches, filters, merge operators, statistics, encryption providers, and tests.

## Risks
Offset arithmetic requires registered pointers to remain subobjects of the configurable instance; misuse with external storage would produce invalid pointers. Rollback can miss non-serialized or non-deterministic fields. Mutable-only mode is subtle for nested configurables and customizables because mutable parent flags temporarily clear the child mutable-only constraint. `AreEquivalent` assumes comparable objects expose the same registered option names and compatible type maps.

## Test Signals
`configurable_test.cc` exercises basic parsing, bad-option rollback, nested unique/shared/raw pointer configuration, structs, enum options, mutable-only behavior, deprecated/alias/dont-serialize/compare-never flags, null option maps, prepare/validate recursion, and round-trip serialization. `customizable_test.cc` further stresses the customizable branch.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/configurable.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/configurable_helper.h -->
# sources/storage-engines/rocksdb/options/configurable_helper.h

## Purpose
`configurable_helper.h` declares `ConfigurableHelper`, a static helper class that keeps the public `Configurable` class small while centralizing parsing, serialization, option lookup, listing, and equivalence logic.

## Important APIs, Types, and Functions
Public static APIs include `ConfigureOptions`, `ConfigureSomeOptions`, `ConfigureSingleOption`, `ConfigureOption`, `GetOption`, `SerializeOptions`, `ListOptions`, and `AreEquivalent`. Private helpers include `FindOption` and `ConfigureCustomizableOption`.

The declarations define the expected semantics for status returns: `OK` for fully applied or intentionally ignored options, `NotFound` for unknown names, `NotSupported` for known names that cannot be converted or instantiated, and `InvalidArgument` for parse or prepare failures.

## Control Flow
Callers pass a `ConfigOptions` object, a target `Configurable`, maps of `OptionTypeInfo`, textual option pairs, and a pointer to the registered option storage. The helper finds the relevant option metadata, delegates conversion to `OptionTypeInfo` or nested `Configurable`/`Customizable` objects, removes consumed map entries, and returns unused entries if requested.

`ConfigureSingleOption` is the single-name path used by direct property updates. `SerializeOptions` is the inverse of configuration and appends `name=value` pairs using the configured delimiter. `AreEquivalent` iterates the registered maps of two configurables and compares fields according to sanity levels and option flags.

## State and Persistence Behavior
The header stores no state. Its functions operate on the state registered inside a `Configurable` instance and on serialized text used for options persistence, rollback, and comparison.

## Dependencies and Integration Points
The file depends on `rocksdb/configurable.h`, `rocksdb/convenience.h`, `OptionTypeInfo`, STL containers, and `Status`. It is included by `configurable.cc`, option wrappers such as `cf_options.cc`, and tests that need direct helper visibility.

## Risks
Because this helper reaches into `Configurable` internals, changes to registration layout or option naming semantics must stay synchronized with implementation. The customizable configuration path is particularly sensitive: it must distinguish replacing an object, configuring its existing mutable children, and accepting no-op ID assignments in mutable-only mode.

## Test Signals
`configurable_test.cc` includes this header directly and validates the behavior described by these declarations. `customizable_test.cc` covers the private customizable behavior indirectly through custom pointer `OptionTypeInfo` entries.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/configurable_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/configurable_test.cc -->
# sources/storage-engines/rocksdb/options/configurable_test.cc

## Purpose
`configurable_test.cc` is the unit test suite for the generic `Configurable` framework. It builds small test configurables and verifies parsing, serialization, preparation, validation, nested option propagation, mutable-only restrictions, aliases/deprecations, comparison flags, and real RocksDB DB/CF/table option adapters.

## Important APIs, Types, and Functions
The file defines `StringLogger`, `SimpleConfigurable`, `ValidatedConfigurable`, parameterized `ConfigurableParamTest`, and a local factory table for `"Simple"`, `"Struct"`, `"Unique"`, `"Shared"`, `"Nested"`, `"Mutable"`, `"ThreeDeep"`, `"DBOptions"`, `"CFOptions"`, and `"BlockBased"` objects. Tests are written with RocksDB test harness macros such as `ASSERT_OK`, `ASSERT_NOK`, `ASSERT_TRUE`, and `ASSERT_EQ`.

## Control Flow
Most tests construct a configurable, mutate it through `ConfigureFromMap`, `ConfigureFromString`, or `ConfigureOption`, then read back fields through `GetOptions<T>`, `GetOption`, or `GetOptionString`. Round-trip tests serialize a configured object and configure a fresh object from the serialized text, then call `AreEquivalent`.

The parameterized flow configures an object from a string, serializes it, reconstructs a copy, then also rebuilds another copy by iterating `GetOptionNames` and applying each individual option. It retries deferred options that were initially unsupported, which mirrors real nested-object ordering where a parent object may need to exist before children can be configured.

## State and Persistence Behavior
The tests validate in-memory state transitions and serialization strings rather than on-disk persistence. They explicitly check rollback behavior after bad parse input: a failed full string containing a valid `int` update plus an unused option leaves the previous integer value intact. Prepare/validate tests track counters and boolean state to ensure recursion and `kDontPrepare` flags work.

## Dependencies and Integration Points
The test includes configurable headers, options helpers/parser, RocksDB public options, DB/CF configurable adapters, block-based table factories, and the test harness. It verifies that generic `Configurable` logic applies not only to synthetic structs but also to `DBOptionsAsConfigurable`, `CFOptionsAsConfigurable`, and `NewBlockBasedTableFactory`.

## Risks Covered
The suite targets common parser risks: unknown options, invalid scalar conversion, mutable-only mutation of immutable fields, nested unique/shared/raw pointer propagation, alias serialization suppression, deprecated no-op entries, `kDontSerialize`, `kCompareNever`, null type maps, and inconsistent comparison direction. It also catches prepare recursion regressions and stale offset bugs after object copy.

## Test Signals
The file is itself the primary test signal. It does not cover every production option in `cf_options.cc`, but it heavily covers the generic machinery used by those option maps. Broader RocksDB options-file tests are still needed for production option name compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/configurable_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/configurable_test.h -->
# sources/storage-engines/rocksdb/options/configurable_test.h

## Purpose
`configurable_test.h` provides reusable test scaffolding for RocksDB configurable option tests. It defines small option structs, option metadata maps, enum mappings, configuration mode flags, and a templated configurable base used by `configurable_test.cc`.

## Important APIs, Types, and Functions
The header defines `TestEnum`, `test_enum_map`, `TestOptions`, `simple_option_info`, `enum_option_info`, `unique_option_info`, `shared_option_info`, and `pointer_option_info`. `TestConfigMode` is a bitmask controlling which option groups and nested pointer forms are registered. `TestConfigurable<T>` derives from `Configurable`, stores a name/prefix and `TestOptions`, and exposes `unique_`, `shared_`, and raw `pointer_` members for nested tests.

## Control Flow
The `TestConfigurable` constructor registers simple options when `kSimpleMode` is set and enum options when `kEnumMode` is set. Derived test classes add unique/shared/raw nested registrations based on mode bits. The destructor deletes the raw pointer member, allowing tests to exercise `OptionTypeFlags::kRawPointer` without leaking the owned test object.

## State and Persistence Behavior
All state is in-memory test state. The option maps model the same offset-based registration used by production code, so serialization and mutation in tests pass through the same `OptionTypeInfo` machinery as real RocksDB options.

## Dependencies and Integration Points
The header includes `configurable_helper.h`, `rocksdb/configurable.h`, and `rocksdb/utilities/options_type.h`. It forward-declares `ColumnFamilyOptions` and `DBOptions` for validation signatures. Its definitions are consumed directly by `configurable_test.cc`.

## Risks
Because the header defines static option maps in a header, it is intended for test use only. Extending tests with additional translation units could create duplicate independent maps, which is fine for tests but not a shared production registry pattern. Raw pointer ownership in the scaffold is manual and depends on the destructor.

## Test Signals
This file is support code rather than an executable suite. Its adequacy is demonstrated by the broad `configurable_test.cc` coverage across simple, enum, unique, shared, raw pointer, nested, and mutable configuration modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/configurable_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/customizable.cc -->
# sources/storage-engines/rocksdb/options/customizable.cc

## Purpose
`customizable.cc` implements the `Customizable` specialization of `Configurable`. A `Customizable` is an option-bearing object with an identity string that can be created or compared by name through RocksDB object registries, such as table factories, filters, caches, merge operators, and other plugin-like components.

## Important APIs, Types, and Functions
Implemented methods include `GetOptionName`, `GenerateIndividualId`, `GetOption`, `SerializeOptions`, `AreEquivalent`, static `GetOptionsMap`, and static `ConfigureNewObject`.

`GetOptionName` strips a leading `<Name>.` prefix before delegating to `Configurable`, allowing serialized property names to be addressed relative to a custom object. `GenerateIndividualId` builds a process-local identity from `Name()`, object address, and process ID. `GetOption` exposes the synthetic `id` property. `SerializeOptions` emits either only the ID or an `id=<id>` plus detailed parent options depending on depth.

## Control Flow
Serialization first obtains `GetId()`. For detailed depth and non-empty IDs, it asks the base configurable to serialize child options. If there are no child properties, the object serializes as just the ID; otherwise it serializes as an ID property followed by the parent option string. Equivalence checks compare IDs at nonzero sanity levels and only compare child configurable options at stricter-than-loose compatibility levels.

`GetOptionsMap` parses a customizable value into an ID and property map. If an existing object is supplied and the parsed ID is the same instance type, it merges current serialized options into the property map before applying new properties, preserving unspecified current fields during reconfiguration.

## State and Persistence Behavior
The file does not own persistent state, but it defines the serialized identity format for custom objects. Empty and `nullptr` values map to no object. `GenerateIndividualId` is suitable for managed object identities but is process/address dependent and not stable across restarts.

## Dependencies and Integration Points
Dependencies include `options_helper`, `Configurable`, `Status`, `OptionTypeInfo`, string utilities, and platform process ID helpers. It is used by all RocksDB components that derive from `Customizable` and by `OptionTypeInfo` custom pointer loaders.

## Risks
`AreEquivalent` uses `static_cast<const Customizable*>(other)` after only checking pointer inequality and sanity level, so callers must ensure the other object is actually the same configurable class family. ID-only shallow serialization is intentional but can hide child option differences unless detailed depth is requested. Merging current options in `GetOptionsMap` ignores serialization errors, which favors best-effort preservation over strict failure.

## Test Signals
`customizable_test.cc` covers creation by ID, detailed and shallow serialization, equivalence at strict and loose sanity levels, null handling, prepare failures, managed IDs, wrapped inner objects, vector serialization, and many registry-backed RocksDB object types.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/customizable.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/customizable_test.cc -->
# sources/storage-engines/rocksdb/options/customizable_test.cc

## Purpose
`customizable_test.cc` validates RocksDB's `Customizable` and object-registry loading infrastructure. It covers synthetic custom objects, configurable fields that hold unique/shared/raw custom pointers, managed object identity reuse, inner/wrapper type discovery, vectors of custom objects, mutable-only nested custom updates, and creation of many built-in/plugin-style RocksDB interfaces by string name.

## Important APIs, Types, and Functions
The file defines `TestCustomizable`, `ACustomizable`, `BCustomizable`, `SimpleConfigurable`, custom option structs/maps, factory registration functions, `CustomizableTest`, and `LoadCustomizableTest`. It also defines numerous mock RocksDB interfaces: secondary cache, statistics, flush block policy factory, slice transform, memory allocator, encryption provider/cipher, file system, table properties collector factory, SST partitioner factory, file checksum generator factory, filter policy, and cache.

Helper methods in `LoadCustomizableTest` include `RegisterTests`, `TestCreateStatic`, `ExpectCreateShared`, `TestExpectedBuiltins`, `TestSharedBuiltins`, and `TestStaticBuiltins`, which enumerate built-in/default/plugin factories and verify `CreateFromString` plus `IsInstanceOf`.

## Control Flow
The first test group registers local `TestCustomizable` factories and configures `SimpleConfigurable` through forms such as `unique={id=A;int=1}`, `unique.id=A`, `unique.A.int=1`, and direct `unique=A`. It round-trips through `GetOptionString`, property parsing, and `ConfigureFromMap`.

Failure tests toggle `ignore_unknown_options` and `ignore_unsupported_options` to distinguish bad factories, missing factories, and bad nested options. Prepare tests instantiate custom objects with `invoke_prepare_options`, checking that failed preparation prevents object installation.

The managed-object tests create objects by individual IDs, verify registry reuse for the same ID, observe weak-reference cleanup when shared pointers are released, and set aliases through `SetManagedObject`. The loading tests then register local factories and attempt built-in and plugin names for table factories, file systems, secondary caches, partitioners, checksum generators, collectors, comparators, slice transforms, statistics, memtable factories, merge operators, compaction filters, event listeners, encryption providers/ciphers, clocks, memory allocators, filter policies, flush block policies, and caches.

## State and Persistence Behavior
The tests focus on serialized object identities and option strings rather than files. They verify that empty IDs, empty values, and `nullptr` clear unique/shared/raw custom pointers. Unnamed custom objects are omitted from serialization and therefore are not recreated on round-trip. Managed-object state lives in `ObjectRegistry` and is reused while shared references remain alive.

## Dependencies and Integration Points
The file integrates with a wide range of RocksDB subsystems: DB test utilities, options parsing, object registries, table factories, filters, caches, memory allocators, encryption, file systems, statistics, merge operators, compaction filters, event listeners, and block-based table options. This makes it a broad integration test for the string-to-object plugin contract.

## Risks Covered
Coverage targets name-pattern parsing, URL-like IDs containing `=` or `;`, missing/failing factory error classification, null custom pointer handling, mutable-only restrictions that allow nested mutable fields but prevent immutable object replacement, serialization of only named customizables, and `IsInstanceOf`/`CheckedCast` behavior through wrapper chains.

## Test Signals
This file is a strong integration signal for custom object loading. Some tests allow environment-dependent failures for optional memory allocators such as jemalloc nodump or memkind. Factory enumeration means test behavior can vary when additional plugins are registered, but failures are collected and reported with factory names.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/customizable_test.cc -->
