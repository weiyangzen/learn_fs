<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/cassandra_serialize_test.cc -->
# sources/storage-engines/rocksdb/utilities/cassandra/cassandra_serialize_test.cc

## Purpose
This file is the focused unit test for Cassandra utility integer serialization. It verifies that the helpers in `utilities/cassandra/serialize.h` encode and decode signed `int8_t`, `int32_t`, and `int64_t` values as big-endian byte strings.

## Important APIs, Types, and Functions
The tests use RocksDB's `test_util/testharness.h` macros and directly call the template specializations `Serialize<T>(T, std::string*)` and `Deserialize<T>(const char*, std::size_t)`. Test cases are split by width and direction: `SerializeI64`, `DeserializeI64`, `SerializeI32`, `DeserializeI32`, `SerializeI8`, and `DeserializeI8`. The file-level `main` installs the RocksDB stack trace handler, initializes GoogleTest, and runs all tests.

## Control Flow
Each serialization test clears or appends to a `std::string`, serializes representative values, and compares the exact byte sequence. Each deserialization test records the current string size as an offset, appends a serialized value, and deserializes from that offset to prove offset-aware decoding works when multiple values are packed together.

## State and Persistence Behavior
The tests are purely in-memory. The only mutable state is a local `std::string dest` reused across assertions. No filesystem or database state is created.

## Dependencies and Integration Points
This is the lowest-level signal for Cassandra row encoding because all higher-level row, column, tombstone, and merge operator serialization depends on these byte helpers. It also indirectly constrains RocksDB/Cassandra compatibility by making byte order stable across host endianness.

## Risks and Edge Cases
The tests cover zero, one, negative one, positive max, and negative boundary-like values for each width. They do not test unsigned types, arbitrary offsets beyond the append pattern, invalid/truncated buffers, or template instantiation failures for unsupported types. The negative integer serialization relies on implementation behavior of right-shifting signed values, which is common but worth noting for portability-sensitive changes.

## Test Signals
Passing this file confirms exact big-endian encoding for signed integer values used by Cassandra value formats. Failures would usually indicate a wire-format regression that could make persisted Cassandra merge operands unreadable or incorrectly ordered.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/cassandra_serialize_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/format.cc -->
# sources/storage-engines/rocksdb/utilities/cassandra/format.cc

## Purpose
This file implements the Cassandra row-value binary format and merge semantics used by RocksDB's Cassandra merge operator. It serializes/deserializes normal columns, expiring columns, column tombstones, and row tombstones, and it defines how multiple row versions collapse into one latest visible row.

## Important APIs, Types, and Functions
`ColumnBase` stores the shared `mask` and `index` fields, serializes them, and dispatches `Deserialize` to `Tombstone`, `ExpiringColumn`, or `Column` based on `DELETION_MASK` and `EXPIRATION_MASK`. `Column` adds `timestamp`, value length, and a value pointer. `ExpiringColumn` adds TTL handling, expiration checks, and conversion to a `Tombstone`. `Tombstone` stores local deletion time and delete timestamp and can decide whether it is collectable after a GC grace period.

`RowValue` is the central type. It can represent either a row tombstone or a vector of column objects. It exposes `Size`, `IsTombstone`, `LastModifiedTime`, `Serialize`, `Deserialize`, `RemoveExpiredColumns`, `ConvertExpiredColumnsToTombstones`, `RemoveTombstones`, `Empty`, and static `Merge`. Local constants `kDefaultLocalDeletionTime` and `kDefaultMarkedForDeleteAt` distinguish live rows from tombstone rows.

## Control Flow
Deserialization starts by reading row-level deletion fields. If the buffer ends there, a row tombstone is returned. Otherwise the deletion fields must be defaults, and the code repeatedly dispatches column deserialization until the offset reaches the buffer size, computing `last_modified_time` as the max column timestamp.

`RowValue::Merge` sorts input rows by descending `LastModifiedTime`. It iterates from newest to oldest, accumulating the best column per index in a `std::map`. If the newest encountered row is a tombstone before any column is selected, the tombstone wins immediately. If a tombstone is found after newer columns have been selected, its timestamp becomes a cutoff; selected columns whose timestamp is older than or equal to that cutoff are filtered out before the merged row is returned.

## State and Persistence Behavior
Serialization appends a compact binary row image into caller-owned strings. Deserialized `Column` and `ExpiringColumn` instances keep `const char*` pointers into the source buffer for value bytes, so the source buffer must outlive the row objects if they are later serialized or inspected. Expiration and tombstone collectability depend on `std::chrono::system_clock::now()`, making behavior time-dependent.

## Dependencies and Integration Points
The implementation depends on `utilities/cassandra/serialize.h` for big-endian integer encoding, `rocksdb::Slice`-compatible storage through raw buffer pointers, and the merge operator in `merge_operator.cc`. It is also exercised by Cassandra test utilities and any DB configured with `CassandraValueMergeOperator`.

## Risks and Edge Cases
Most validation is via `assert`, so malformed persisted values can become unchecked memory reads in release builds. The use of raw `const char*` value pointers makes lifetime management critical after deserialization. The mask dispatch treats any mask with the deletion bit set as a tombstone even if other bits are present. Time-based expiration can make tests or compactions nondeterministic if timestamps are close to wall clock. The merge algorithm returns an empty live row if all selected columns are hidden by an older row tombstone rather than returning the tombstone itself.

## Test Signals
Expected coverage comes from Cassandra serialization tests and merge-operator tests elsewhere in the suite. Important signals are round-trip row/column encoding, latest-column selection by index, row tombstone cutoff behavior, expired-column removal/conversion, and tombstone GC grace filtering.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/format.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/format.h -->
# sources/storage-engines/rocksdb/utilities/cassandra/format.h

## Purpose
This header declares the in-memory representation and binary layout contract for Cassandra row values stored in RocksDB merge operands. It documents the row tombstone fields, column masks, normal/expiring/tombstone column layouts, and the merge-facing `RowValue` API.

## Important APIs, Types, and Functions
`ColumnTypeMask` defines `DELETION_MASK` and `EXPIRATION_MASK`. `ColumnBase` is the abstract common interface for column-like values, exposing `Timestamp`, `Mask`, `Index`, `Size`, `Serialize`, and static `Deserialize`. `Column`, `Tombstone`, and `ExpiringColumn` implement the concrete wire layouts. `Columns` aliases a vector of shared column pointers.

`RowValue` exposes constructors for row tombstones and live rows, move-only ownership, binary sizing and serialization, expiration/tombstone cleanup helpers, static deserialization, and static multi-row merge. `get_columns()` exposes the stored column vector for tests and callers that need direct inspection.

## Control Flow
The header itself has no implementation flow, but the declared API implies a two-stage parse: row-level deletion fields first, then zero or more columns selected by mask. The merge API accepts a vector of row values and returns a newly assembled row based on timestamps and tombstone visibility.

## State and Persistence Behavior
The classes model persisted binary records. `RowValue` owns a vector of shared column objects, while `Column` stores a pointer to the value bytes rather than owning a copy. Row tombstones have no columns and use deletion metadata as their last-modified time. Live rows use default deletion sentinels and track a cached last-modified timestamp.

## Dependencies and Integration Points
The declarations depend on RocksDB namespace and merge-related headers, plus standard `chrono`, `memory`, and `vector`. They are consumed by the Cassandra merge operator, test utilities, and serialization tests. The documented layout must remain compatible with persisted RocksDB values and merge operands.

## Risks and Edge Cases
The header exposes mutable implementation assumptions: raw value pointers, signed integer field sizes, and timestamp units. `get_columns()` returns a non-const method exposing a const reference, which is useful in tests but leaks representation. Any change in field order, size, mask interpretation, or sentinel defaults is a storage-format compatibility change.

## Test Signals
The best signals are exact serialization byte tests, row round-trip tests, merge behavior tests, and compaction tests using `CassandraValueMergeOperator`. Review should also check that new column types or mask bits do not accidentally route to existing concrete classes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/merge_operator.cc -->
# sources/storage-engines/rocksdb/utilities/cassandra/merge_operator.cc

## Purpose
This file implements RocksDB's `MergeOperator` for Cassandra row values. It turns existing values and merge operands into `RowValue` objects, merges them according to Cassandra timestamp/tombstone rules, optionally collects tombstones, and writes the merged binary value back to RocksDB.

## Important APIs, Types, and Functions
The file defines `merge_operator_options_info`, registering `CassandraOptions` fields `gc_grace_period_in_seconds` and `operands_limit` for RocksDB's options infrastructure. `CassandraValueMergeOperator` constructs its option object and calls `RegisterOptions`.

`FullMergeV2` handles full merge requests with an optional existing value and a list of operands. `PartialMergeMulti` merges only operands and is used to reduce queued merge operands before a base value is read.

## Control Flow
`FullMergeV2` clears the output, deserializes the existing value if present, deserializes every operand, calls `RowValue::Merge`, removes collectable tombstones using the configured GC grace period, reserves output capacity from the merged size, serializes the result, and returns true. `PartialMergeMulti` follows the same pattern for operands only but does not perform tombstone GC cleanup.

## State and Persistence Behavior
The operator is stateless across calls except for `CassandraOptions`. It reads persisted binary row values from slices and writes a new persisted binary value to a string owned by RocksDB's merge machinery. Full merges can physically remove collectable column tombstones, while partial merges preserve them so future full merges can still honor tombstone semantics.

## Dependencies and Integration Points
The implementation depends on RocksDB's merge operator API, option type registration, `utilities/cassandra/format.h`, and `utilities/merge_operators.h`. It is integrated by configuring a DB column family with `CassandraValueMergeOperator` or loading the operator by class name/options.

## Risks and Edge Cases
All operands are deserialized eagerly into memory, so very large operand lists can be expensive until `ShouldMerge` controls compaction frequency. Deserialization relies on asserts in the format layer rather than returning merge failure for malformed values. Partial merge omits tombstone GC by design; changing that could make deleted columns reappear incorrectly. `FullMergeV2` returns true unconditionally, so corrupt input is not reported through merge status unless it crashes/asserts.

## Test Signals
Signals should include full merge with base values, partial merge of operands, option parsing, `ShouldMerge` thresholds, row tombstone cutoff behavior, and GC grace tombstone removal. Cassandra row format tests are prerequisite because this operator trusts the format layer.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/merge_operator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/merge_operator.h -->
# sources/storage-engines/rocksdb/utilities/cassandra/merge_operator.h

## Purpose
This header declares `CassandraValueMergeOperator`, the RocksDB merge operator that applies Cassandra row-value reconciliation rules.

## Important APIs, Types, and Functions
The class derives from `MergeOperator` and overrides `FullMergeV2`, `PartialMergeMulti`, `Name`, `AllowSingleOperand`, and `ShouldMerge`. The constructor accepts `gc_grace_period_in_seconds` and optional `operands_limit`. `kClassName()` returns the stable option-loading name `CassandraValueMergeOperator`.

## Control Flow
The header defines policy hooks used by RocksDB's merge engine. `AllowSingleOperand` returns true so a single operand may be passed through merge processing. `ShouldMerge` requests operand merging when `operands_limit` is positive and the operand count reaches that threshold.

## State and Persistence Behavior
The only stored state is `CassandraOptions options_`, carrying tombstone GC and operand-limit settings. The persisted state is outside the class in encoded Cassandra row values; merge calls read and rewrite those values.

## Dependencies and Integration Points
It depends on RocksDB merge APIs, `Slice`, and `utilities/cassandra/cassandra_options.h`. The class name and options registration in the `.cc` file tie it to RocksDB's customizable/options system.

## Risks and Edge Cases
`ShouldMerge` is disabled when `operands_limit` is zero, so merge operands can accumulate until RocksDB's other merge triggers act. The header promises Cassandra row merge semantics but does not expose input validation or error-reporting controls. Any class-name change would break string-based configuration compatibility.

## Test Signals
Tests should verify the merge operator can be selected by name/options, honors `operands_limit`, allows single operands, and produces encoded rows compatible with `RowValue::Deserialize`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/merge_operator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/serialize.h -->
# sources/storage-engines/rocksdb/utilities/cassandra/serialize.h

## Purpose
This header provides small template specializations that serialize and deserialize signed integer fields in Cassandra row values as big-endian bytes.

## Important APIs, Types, and Functions
Generic declarations exist for `Serialize<T>` and `Deserialize<T>`, with inline specializations for `int8_t`, `int32_t`, and `int64_t`. Constants `kCharMask` and `kBitsPerByte` drive byte extraction and reconstruction.

## Control Flow
Serialization appends the high-order byte first and the low-order byte last for 32-bit and 64-bit values; 8-bit values append a single byte. Deserialization reads bytes from `src + offset`, casts each byte to `unsigned char` for the wider types, shifts them into position, and ORs them into the result.

## State and Persistence Behavior
The functions mutate only the destination string supplied by the caller and read from raw source memory supplied by the caller. They define the durable byte order for Cassandra row-value fields.

## Dependencies and Integration Points
The header depends only on standard integer/string headers and `rocksdb/rocksdb_namespace.h`. It is used by `format.cc` and tested by `cassandra_serialize_test.cc`.

## Risks and Edge Cases
There is no bounds checking on `src` or `offset`. Unsupported template types have declarations but no definitions, causing link failures if accidentally used. Right-shifting negative signed integers during serialization can be implementation-sensitive. The anonymous namespace constants in a header create internal-linkage copies in each translation unit, which is acceptable here but unusual.

## Test Signals
`cassandra_serialize_test.cc` verifies exact byte sequences and offset-aware round trips for representative signed values. Additional fuzzing with random values would strengthen confidence in round-trip symmetry.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/serialize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/test_utils.cc -->
# sources/storage-engines/rocksdb/utilities/cassandra/test_utils.cc

## Purpose
This file implements helpers for Cassandra row-value tests. It creates deterministic normal columns, tombstone columns, expiring columns, row tombstones, and assertion helpers for column contents.

## Important APIs, Types, and Functions
It defines test constants `kData`, `kExpiringData`, `kTtl`, and mask/index constants `kColumn`, `kTombstone`, and `kExpiringColumn`. `CreateTestColumn` constructs the appropriate `ColumnBase` subclass based on the mask. `CreateTestColumnSpec` packages a mask/index/timestamp tuple. `CreateTestRowValue` builds a live `RowValue` from specs and computes the max timestamp. `CreateRowTombstone` builds a row tombstone. `VerifyRowValueColumns` compares timestamp, mask, and index. `ToMicroSeconds` and `ToSeconds` convert timestamp units.

## Control Flow
The main branch point is `CreateTestColumn`: deletion masks create `Tombstone`, expiration masks create `ExpiringColumn`, and all other masks create `Column`. `CreateTestRowValue` loops over specs, constructs each column, updates `last_modified_time`, and returns a moved row value.

## State and Persistence Behavior
All helper-generated column value pointers point at file-scope static arrays, so their lifetime is stable for tests. Timestamps are interpreted as microseconds for column timestamps and converted to seconds for local deletion time.

## Dependencies and Integration Points
These helpers depend on `format.h`, `serialize.h`, and RocksDB's test harness. They are meant to reduce duplication in Cassandra format and merge tests.

## Risks and Edge Cases
The helper uses masks rather than the exported `kColumn`/`kTombstone`/`kExpiringColumn` constants to choose the concrete type, so callers must pass mask bits correctly. The test data sizes include raw array lengths and no terminating nulls. `ToSeconds` truncates microseconds, matching Cassandra local deletion time but potentially surprising in tests near second boundaries.

## Test Signals
This file is support code, not a test itself. Its correctness is visible through Cassandra format/merge tests that assert column ordering, timestamp selection, row tombstones, and TTL behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/test_utils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/test_utils.h -->
# sources/storage-engines/rocksdb/utilities/cassandra/test_utils.h

## Purpose
This header declares reusable helpers and constants for testing Cassandra row-value serialization and merge behavior.

## Important APIs, Types, and Functions
It declares static data constants, column kind constants, `CreateTestColumn`, `CreateTestColumnSpec`, `CreateTestRowValue`, `CreateRowTombstone`, `VerifyRowValueColumns`, `ToMicroSeconds`, and `ToSeconds`.

## Control Flow
The header has no runtime flow; it defines the test helper contract used by Cassandra test files.

## State and Persistence Behavior
The declared constants are defined in the `.cc` file and provide stable backing storage for test column values. Helper-created rows are ordinary `RowValue` objects that can be serialized into persistent-format bytes.

## Dependencies and Integration Points
It includes the RocksDB test harness and Cassandra format/serialize headers. It integrates tests with the production Cassandra row model without exposing these helpers to production code.

## Risks and Edge Cases
Because the header includes the test harness, it should remain test-only. Any change to helper constants or timestamp conversion can alter expected test semantics. Callers depend on the tuple layout for column specs.

## Test Signals
Indirect signal comes from all tests that include this header. Compile failures catch signature drift between helpers and production Cassandra classes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/cassandra/test_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/checkpoint/checkpoint_impl.cc -->
# sources/storage-engines/rocksdb/utilities/checkpoint/checkpoint_impl.cc

## Purpose
This file implements RocksDB checkpoints and column-family SST export. Checkpoints create an openable point-in-time DB directory by staging live files, linking or copying them, writing replacement metadata files, and atomically renaming the staging directory into place.

## Important APIs, Types, and Functions
`Checkpoint::Create` instantiates `CheckpointImpl`. Base `Checkpoint` methods return `NotSupported` when not backed by an implementation. `CheckpointImpl::CreateCheckpoint` is the public checkpoint path. `CleanStagingDirectory` removes stale temporary files and directories. `CreateCustomCheckpoint` contains the generic live-file walking logic parameterized by link/copy/create callbacks. `ExportColumnFamily` flushes a column family, copies/links its live SSTs to an export directory, and returns `ExportImportFilesMetaData`. `ExportFilesInMetaData` iterates `ColumnFamilyMetaData` table files and handles link-to-copy fallback.

## Control Flow
`CreateCheckpoint` rejects an existing or invalid destination, derives a sibling `.tmp` staging path, cleans it, creates it, disables file deletions when supported, and calls `CreateCustomCheckpoint`. The default callbacks hard-link files into staging, copy files when links are unsupported or when `trim_to_size` is required, and create replacement files such as `CURRENT`. After copying/linking, file deletions are re-enabled, staging is renamed to the destination, and the destination directory is fsynced. Failures log and clean the staging directory.

`CreateCustomCheckpoint` records the latest sequence number, calls `GetLiveFilesStorageInfo` with WAL flush/checksum/atomic-flush options, rejects multi-directory non-WAL layouts, then processes every live file. Replacement contents are written through `create_file_cb`; otherwise files are linked first when possible and copied after `NotSupported` or when trimming is required.

`ExportColumnFamily` rejects existing or invalid export directories, creates a temporary export directory, flushes the target CF, disables file deletions, obtains CF metadata, exports table files, re-enables deletions, renames the temp dir, fsyncs it, and fills comparator and file metadata. Failure cleans whichever export directory currently owns staged files.

## State and Persistence Behavior
Checkpoint creation writes to `<checkpoint_dir>.tmp`, then renames it to the requested checkpoint path. It may hard-link SST/blob/WAL/metadata files, copy files, and create replacement metadata contents. It temporarily disables DB file deletion to keep live files stable. Export similarly writes to `<export_dir>.tmp` and returns heap-allocated metadata to the caller. Sequence number output is set only on successful checkpoint creation.

## Dependencies and Integration Points
This implementation integrates with `DB::GetLiveFilesStorageInfo`, `DisableFileDeletions`, `EnableFileDeletions`, `CopyFile`, `CreateFile`, `ParseFileName`, `ColumnFamilyMetaData`, `ExportImportFilesMetaData`, file checksum metadata, `Temperature`, and filesystem directory fsync APIs. It is used by public `rocksdb/utilities/checkpoint.h` and by backup/checkpoint tests.

## Risks and Edge Cases
`CleanStagingDirectory` deletes only direct children as files before deleting the directory, so nested unexpected contents could fail cleanup. Checkpoints and backup do not support multiple non-WAL directories (`db_paths`/CF paths). If `EnableFileDeletions` fails after a successful disable, the status is asserted in checkpoint creation but handled more softly in export. Link fallback switches to copying after `NotSupported`, but other link failures abort. Export has a FIXME around atomic flush and temperature handling. Destination paths that are empty or root-like are rejected after existence checks.

## Test Signals
`checkpoint_test.cc` covers checkpoint openability, blob files, CF export metadata, invalid paths, concurrent CURRENT changes, 2PC WAL constraints, read-only DBs, WAL locking, db_paths rejection, archived WAL handling, deletion behavior, atomic flush override paths, and backup interactions. Fault-injection tests validate durability when unsynced file data is dropped.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/checkpoint/checkpoint_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/checkpoint/checkpoint_impl.h -->
# sources/storage-engines/rocksdb/utilities/checkpoint/checkpoint_impl.h

## Purpose
This header declares `CheckpointImpl`, the concrete implementation of the public RocksDB checkpoint utility.

## Important APIs, Types, and Functions
`CheckpointImpl` derives from `Checkpoint` and stores a raw `DB*`. It overrides `CreateCheckpoint` and `ExportColumnFamily`. It also declares `CreateCustomCheckpoint`, which lets callers customize link, copy, and file-creation behavior. Private helpers are `CleanStagingDirectory` and `ExportFilesInMetaData`.

## Control Flow
The header defines the extension points used by the implementation. `CreateCustomCheckpoint` accepts callback functions for each file action and options for sequence output, WAL flush threshold, checksum collection, and atomic flush behavior.

## State and Persistence Behavior
The implementation object does not own the DB; callers must keep the DB alive. Persistent effects are all through the underlying DB environment and filesystem when checkpoint/export methods are invoked.

## Dependencies and Integration Points
It depends on RocksDB DB APIs, filename parsing types, and the public checkpoint utility header. The callback signatures expose `FileType`, checksum strings, file size limits, and `Temperature`, making checkpoint logic reusable by backup-like code.

## Risks and Edge Cases
The raw `DB*` lifetime is not protected. Callback contracts must correctly preserve file contents, truncation limits, checksums, and directory fsync requirements, or generated checkpoints can be non-openable. `CreateCustomCheckpoint` is powerful enough for tests and backup code but easy to misuse.

## Test Signals
Compile and behavior coverage comes from `checkpoint_test.cc` and backup tests using the same live-file metadata machinery. Tests that mock custom callbacks are especially useful for link/copy fallback and checksum propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/checkpoint/checkpoint_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/checkpoint/checkpoint_test.cc -->
# sources/storage-engines/rocksdb/utilities/checkpoint/checkpoint_test.cc

## Purpose
This file is the main test suite for RocksDB checkpoint, export, WAL, atomic-flush, and related backup behavior. It verifies that checkpoints and exports are durable, openable, and consistent across column families, blob files, transaction/WAL cases, read-only DBs, and failure-sensitive filesystem scenarios.

## Important APIs, Types, and Functions
`CheckpointTest` is the fixture. It manages DB paths, alternate WAL paths, snapshot/export paths, DB handles, CF handles, and exported metadata. Helper methods open/reopen/destroy DBs, create column families, compact, flush, put/delete/get keys, open read-only DBs, and query table-file counts. `CheckpointTestWithWalParams` parameterizes WAL behavior by log flush threshold, WAL manifest tracking, manual WAL flush, and background inactive WAL close. `CheckpointDestroyTest` parameterizes slow deletion behavior.

Key tests include `GetSnapshotLink`, `CheckpointWithBlob`, `ExportColumnFamilyWithLinks`, `ExportEmptyColumnFamily`, `ExportColumnFamilyNegativeTest`, `CheckpointCF`, `CheckpointCFNoFlush`, `CurrentFileModifiedWhileCheckpointing`, `CurrentFileModifiedWhileCheckpointing2PC`, `CheckpointInvalidDirectoryName`, `CheckpointWithParallelWrites`, `CheckpointWithUnsyncedDataDropped`, read-only and WAL-lock cases, blob-direct-write rejection, `CheckpointWithDbPath`, archived WAL handling, delete-scheduler behavior, atomic flush override tests, mixed atomic/non-atomic flush queue tests, and backup atomic-flush/blob-direct-write tests.

## Control Flow
Most tests create data, take a checkpoint/export, mutate or destroy the original DB, then open the checkpoint/export/backup and verify data or metadata. Race-sensitive tests use `SyncPoint` dependencies and callbacks to pause checkpointing around flushes, manifest rollover, transaction commit, or atomic flush scheduling. Parameterized WAL tests use `FaultInjectionTestFS` to drop unsynced data after checkpoint creation and ensure the checkpoint remains openable.

## State and Persistence Behavior
The fixture creates real RocksDB databases under per-thread test paths plus snapshot, export, backup, and restore directories. Checkpoints are staged and opened as independent DBs. Export tests produce SST copies/links plus `ExportImportFilesMetaData`. Some tests intentionally destroy the original DB, drop unsynced file data, or inspect delete scheduler foreground/background behavior.

## Dependencies and Integration Points
The suite integrates checkpoint implementation, `DBImpl`, backup engine, transaction DB, blob files, column-family metadata, env/file utilities, `FaultInjectionEnv`, `FaultInjectionFS`, `SstFileManager`, delete scheduler, `SyncPoint`, and RocksDB's GoogleTest harness.

## Risks and Edge Cases
The tests cover many timing-sensitive behaviors, so they depend on stable sync-point names and internal sequencing. Some tests are expensive, especially the 2PC loop and backup/restore cases. Several assertions rely on exact status text fragments for blob direct write rejection. Fixture cleanup must destroy CF handles and metadata correctly to avoid leaks. The test name `CheckpointWithArchievedLog` preserves a spelling typo and should not be renamed casually if referenced by scripts.

## Test Signals
A passing suite gives strong confidence that checkpoint directories are openable, contain required blob/WAL/SST metadata, survive unsynced-data loss, reject unsupported layouts, preserve CF data under flush races, honor atomic-flush controls, and interact correctly with backup behavior. Failures usually point to durability, file-lifetime, metadata, or flush/WAL regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/checkpoint/checkpoint_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/compaction_filters.cc -->
# sources/storage-engines/rocksdb/utilities/compaction_filters.cc

## Purpose
This file registers and loads RocksDB compaction filters from string configuration. It provides the built-in registration hook for `RemoveEmptyValueCompactionFilter`.

## Important APIs, Types, and Functions
`RegisterBuiltinCompactionFilters` adds a factory for `RemoveEmptyValueCompactionFilter::kClassName()` to the default `ObjectLibrary`. `CompactionFilter::CreateFromString` registers built-ins once with `std::call_once`, then calls `LoadStaticObject`. `CompactionFilterFactory::CreateFromString` delegates to `LoadSharedObject` and currently has no built-in factories to register.

## Control Flow
The first `CreateFromString` call initializes built-in filter factories. Then the requested string value is resolved through RocksDB's static object loader into a `CompactionFilter*`. Factory loading simply attempts shared/static configuration loading and returns the resulting status.

## State and Persistence Behavior
The only persistent state is the process-global registration in `ObjectLibrary::Default()` guarded by a static `once_flag`. Created filters are returned to callers according to RocksDB's customizable object conventions.

## Dependencies and Integration Points
This file depends on `rocksdb/compaction_filter.h`, options/customizable loading, and the remove-empty-value filter implementation. It is used by options parsing and configuration strings that name compaction filters.

## Risks and Edge Cases
Only a single built-in `CompactionFilter` is registered; built-in factories are explicitly absent. The code casts through `const_cast` because the public API returns a const filter pointer, so ownership and lifetime must follow the customizable loader contract. A missing or misspelled class name returns a loader error rather than a fallback.

## Test Signals
Useful tests parse `RemoveEmptyValueCompactionFilter` by class name, verify unknown filters fail, and ensure factory string loading still works for user-registered/shared filters.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/compaction_filters.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/compaction_filters/layered_compaction_filter_base.h -->
# sources/storage-engines/rocksdb/utilities/compaction_filters/layered_compaction_filter_base.h

## Purpose
This header defines a helper base class for compaction filters that wrap or layer behavior on top of a user-provided compaction filter.

## Important APIs, Types, and Functions
`LayeredCompactionFilterBase` derives from `CompactionFilter`. Its constructor accepts either a raw user filter pointer or a `unique_ptr` created by a factory, stores ownership when provided, and chooses the effective `user_comp_filter_`. `user_comp_filter()` returns that inner filter. `Inner()` overrides `Customizable::Inner` so option/introspection tooling can see the wrapped object.

## Control Flow
Construction resolves the inner filter once: if the raw pointer is null, it uses the owned factory-created filter. Runtime calls are expected to be implemented by subclasses that consult `user_comp_filter()`.

## State and Persistence Behavior
The class stores a non-owning pointer plus an optional owning `unique_ptr`. No DB state is modified by this base class itself.

## Dependencies and Integration Points
It depends on RocksDB's compaction filter API and is referenced by layered filters such as blob-index or TTL filters. It integrates with the customizable object tree through `Inner()`.

## Risks and Edge Cases
If both constructor arguments are null, `user_comp_filter_` remains null and subclasses must handle that. The raw pointer is non-owning and must outlive the layered filter unless the owned pointer is used. The base class does not forward any filtering calls itself.

## Test Signals
Coverage should come from concrete layered filters verifying that user filters are invoked, owned factory filters remain alive, and `Inner()` reports the wrapped filter for option introspection.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/compaction_filters/layered_compaction_filter_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/compaction_filters/remove_emptyvalue_compactionfilter.cc -->
# sources/storage-engines/rocksdb/utilities/compaction_filters/remove_emptyvalue_compactionfilter.cc

## Purpose
This file implements a simple compaction filter that removes key-value entries whose existing value is empty.

## Important APIs, Types, and Functions
`RemoveEmptyValueCompactionFilter::Filter` overrides `CompactionFilter::Filter`. It ignores level, key, output value, and value-changed parameters, and returns `existing_value.empty()`.

## Control Flow
Every compaction-filter callback is a single predicate check. Empty values return true, instructing RocksDB to drop the key; non-empty values return false and are kept unchanged.

## State and Persistence Behavior
The filter is stateless. Its persistent effect occurs during compaction: keys with empty values are omitted from newly written SST files.

## Dependencies and Integration Points
It depends on `rocksdb::Slice` and is registered as a built-in string-loadable compaction filter in `utilities/compaction_filters.cc`.

## Risks and Edge Cases
This filter treats an empty value as deletion-like during compaction, which is safe only for workloads where empty values are not meaningful. It does not set `value_changed` or rewrite values. It does not inspect merge operands before they are resolved.

## Test Signals
Tests should verify that empty values disappear after compaction, non-empty values remain, and the filter can be created by the registered class name.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/compaction_filters/remove_emptyvalue_compactionfilter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/compaction_filters/remove_emptyvalue_compactionfilter.h -->
# sources/storage-engines/rocksdb/utilities/compaction_filters/remove_emptyvalue_compactionfilter.h

## Purpose
This header declares the built-in compaction filter that drops entries with empty values.

## Important APIs, Types, and Functions
`RemoveEmptyValueCompactionFilter` derives from `CompactionFilter`, exposes stable class name `RemoveEmptyValueCompactionFilter`, overrides `Name`, and declares `Filter`.

## Control Flow
The header defines the filter contract; implementation is the empty-value predicate in the `.cc` file.

## State and Persistence Behavior
The class has no data members and therefore no per-instance mutable state.

## Dependencies and Integration Points
It depends on RocksDB compaction filter and slice APIs. The class name is used by built-in object-library registration.

## Risks and Edge Cases
Changing `kClassName` breaks string-based option compatibility. Because the filter has no configuration, deployments needing conditional empty-value handling need a different filter.

## Test Signals
Compile/link coverage plus configuration-loading and compaction behavior tests provide the main confidence signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/compaction_filters/remove_emptyvalue_compactionfilter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/convenience/info_log_finder.cc -->
# sources/storage-engines/rocksdb/utilities/convenience/info_log_finder.cc

## Purpose
This file implements a convenience helper that lists RocksDB info log files for an open DB.

## Important APIs, Types, and Functions
`GetInfoLogList(DB* db, std::vector<std::string>* info_log_list)` validates the DB pointer, reads the DB's options and name, and delegates to `GetInfoLogFiles`.

## Control Flow
If `db` is null, the function returns `InvalidArgument`. Otherwise it obtains `options.env->GetFileSystem()`, `options.db_log_dir`, and `db->GetName()`, then calls the filename utility to populate the output list.

## State and Persistence Behavior
The function is read-only. It may query filesystem metadata but does not mutate DB or log files.

## Dependencies and Integration Points
It depends on the public `rocksdb/utilities/info_log_finder.h`, filename utilities, and DB/Env APIs. It is a thin public utility over lower-level log-file discovery.

## Risks and Edge Cases
Only the DB pointer is validated locally; a null output vector or invalid environment would fail in delegated code. The returned list depends on filename parsing and the DB's configured log directory. Errors from filesystem traversal are returned directly.

## Test Signals
Tests should cover null DB rejection, default and custom `db_log_dir`, rotated logs, and empty/missing log directories.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/convenience/info_log_finder.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/counted_fs.cc -->
# sources/storage-engines/rocksdb/utilities/counted_fs.cc

## Purpose
This file implements `CountedFileSystem`, a `FileSystemWrapper` that counts file opens, closes, deletes, renames, directory operations, flush/sync/fsync calls, read operations/bytes, and write operations/bytes.

## Important APIs, Types, and Functions
Wrapper classes include `CountedSequentialFile`, `CountedRandomAccessFile`, `CountedWritableFile`, `CountedRandomRWFile`, and `CountedDirectory`. Each wraps the corresponding file object and records counters around reads, writes, close, flush, sync, fsync, range sync, and directory fsync. `FileOpCounters::PrintCounters` renders a human-readable report. `CountedFileSystem` overrides file creation/open methods to wrap successful results.

## Control Flow
Each `New*` method opens the target file through the base filesystem. On success it increments open counters and replaces the result with a counted wrapper. File operation wrappers call through to the target first, then record successful or supported operations. `OpCounter::RecordOp` counts operations unless status is `NotSupported` and counts bytes only when the operation succeeds.

## State and Persistence Behavior
All counters live in atomics inside `FileOpCounters`. The wrapper does not change persisted file contents except by forwarding the caller's operation to the target filesystem. Directory wrappers count close in the destructor if an explicit `Close` was not called.

## Dependencies and Integration Points
It depends on RocksDB FileSystem wrapper classes and exposes counters through `GetOptionsPtr(FileOpCounters::kName())`, allowing other components to retrieve the counter object. It is useful for tests, diagnostics, and performance instrumentation.

## Risks and Edge Cases
Close counting differs by file type: some wrappers count in destructors, some count only explicit successful closes. Sequential and random-access file destructors count closes even without a close status. `RangeSync` increments the generic sync counter, not a separate range-sync counter. `MultiRead` records each request's status and result size, while the aggregate status is otherwise ignored for byte accounting.

## Test Signals
Useful tests open/read/write/delete/rename files through `CountedFileSystem`, check byte counts, verify directory open/close/fsync counts, and confirm counters reset and can be retrieved through `GetOptionsPtr`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/counted_fs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/counted_fs.h -->
# sources/storage-engines/rocksdb/utilities/counted_fs.h

## Purpose
This header declares the counting data structures and `CountedFileSystem` wrapper used to instrument RocksDB filesystem activity.

## Important APIs, Types, and Functions
`OpCounter` stores atomic operation and byte counts and exposes `Reset` and `RecordOp`. `FileOpCounters` stores atomics for opens, closes, deletes, renames, flushes, syncs, dsyncs, fsyncs, directory opens/closes, plus read/write `OpCounter`s. It exposes `Reset`, `PrintCounters`, and `kName`.

`CountedFileSystem` derives from `FileSystemWrapper`, overrides file creation/open methods plus delete/rename, exposes const and mutable `counters()`, `PrintCounters`, `ResetCounters`, and `GetOptionsPtr`.

## Control Flow
The header specifies which filesystem events are counted. Most operation counting is implemented in the `.cc` wrappers; inline `DeleteFile` and `RenameFile` count only successful calls.

## State and Persistence Behavior
Counters are process memory only and atomically updated. The wrapper forwards all real file work to the base filesystem.

## Dependencies and Integration Points
It depends on RocksDB `FileSystem`, `IOStatus`, namespace, and logger declarations. Integration occurs by wrapping an existing filesystem and optionally retrieving counters via the options pointer name.

## Risks and Edge Cases
Counters are approximate instrumentation, not a transaction log. Atomic relaxed ordering is appropriate for counts but means callers should not infer ordering. A caller that bypasses the wrapper or obtains the target filesystem directly will not be counted.

## Test Signals
Tests should verify each exposed counter, reset behavior, string rendering, and options-pointer discovery under single-threaded and simple concurrent workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/counted_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/debug.cc -->
# sources/storage-engines/rocksdb/utilities/debug.cc

## Purpose
This file implements debug utilities for inspecting internal key versions in a RocksDB DB or column family.

## Important APIs, Types, and Functions
`value_type_string_map` maps internal `ValueType` enum names to enum values. `KeyVersion::GetTypeName` serializes the numeric type back to a string or returns `Invalid`. `GetAllKeyVersions` has overloads for the default column family and an explicit `ColumnFamilyHandle`.

## Control Flow
The public overload validates the DB pointer and delegates to the CF-aware overload. The CF-aware overload validates DB, CF handle, and output vector; clears the output; obtains the root `DBImpl`; creates an `InternalKeyComparator`; opens a new internal iterator at `kMaxSequenceNumber`; adjusts optional begin/end bounds for timestamped comparators; seeks to the beginning bound or first key; then iterates internal entries until invalid, past end bound, parse failure, or `max_num_ikeys` is reached.

## State and Persistence Behavior
The function is read-only against the DB but exposes internal key/value versions into a caller-owned vector. Returned keys and values are copied to strings. It uses current internal iterator state, not a user snapshot.

## Dependencies and Integration Points
It depends on `DBImpl`, internal key parsing/comparison, timestamp range helpers, `Arena`, `ScopedArenaPtr`, `ReadOptions`, and RocksDB's options enum serialization utilities. It powers public debug APIs in `rocksdb/utilities/debug.h`.

## Risks and Edge Cases
This code reaches into `DBImpl` internals and assumes the DB pointer can be cast to the expected implementation via `GetRootDB`. It returns internal records, including deletions, merges, range deletions, blob indexes, wide-column entities, transaction markers, and timestamp variants, so callers must not treat output as normal user-level state. Range end comparison uses `> 0`, so equality with the end key remains included. Parse errors abort the scan.

## Test Signals
Tests should insert puts/deletes/merges across sequence numbers, call `GetAllKeyVersions` with and without bounds, verify type names, timestamped comparator ranges, column-family handling, null-argument validation, and `max_num_ikeys` limiting.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/debug.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/env_mirror.cc -->
# sources/storage-engines/rocksdb/utilities/env_mirror.cc

## Purpose
This file implements `EnvMirror`, a debugging `Env` that mirrors selected file operations to two backend environments and asserts that their behavior and contents match.

## Important APIs, Types, and Functions
Wrapper classes are `SequentialFileMirror`, `RandomAccessFileMirror`, and `WritableFileMirror`. They hold paired backend files `a_` and `b_` and forward reads/writes/syncs to both, comparing statuses and data where practical. `EnvMirror` overrides legacy Env file creation/open methods `NewSequentialFile`, `NewRandomAccessFile`, `NewWritableFile`, and `ReuseWritableFile`.

## Control Flow
For normal paths, `EnvMirror` opens the file on both backends, asserts equal status, and returns a mirror wrapper on success. Reads generally use backend A's result as the returned data and read the same amount from backend B to assert byte-for-byte equality. Writes append/positioned-append/truncate/close/flush/sync/fsync/allocate/range-sync are sent to both and status equality is asserted. Paths under `/proc/` bypass mirroring and go only to backend A.

## State and Persistence Behavior
The mirror duplicates writes into both environments. Returned read data comes from backend A, with backend B used as a consistency check. The class stores no persistent metadata beyond the two backend `Env*` pointers and wrapper state.

## Dependencies and Integration Points
It implements the API declared in `rocksdb/utilities/env_mirror.h` and is primarily a test/debug utility. `env_mirror_test.cc` exercises it with two `MockEnv` instances.

## Risks and Edge Cases
Consistency failures are `assert`s, so release builds may not detect mismatches. Some methods explicitly do not verify returned priority, preallocation status, or unique IDs. Sequential reads from backend B loop until matching backend A's byte count; unusual short-read behavior could stress this path. The implementation covers legacy `Env` APIs, not the newer `FileSystem` wrapper surface.

## Test Signals
`env_mirror_test.cc` covers directory/file basics, metadata, rename/delete, sequential and random reads, locks, sync/flush/close no-ops, and large sequential data. Additional tests would be useful for positioned append, truncation, allocation, and mismatch assertions in debug builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/env_mirror.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/env_mirror_test.cc -->
# sources/storage-engines/rocksdb/utilities/env_mirror_test.cc

## Purpose
This file tests `EnvMirror` using two `MockEnv` backends. It verifies that mirrored operations affect both backends and that reads through the mirror return expected data.

## Important APIs, Types, and Functions
`EnvMirrorTest` owns `Env::Default()`, two `MockEnv` instances, and an `EnvMirror`. Tests are `Basics`, `ReadWrite`, `Locks`, `Misc`, and `LargeWrite`. The file-level `main` installs the stack trace handler and runs GoogleTest.

## Control Flow
`Basics` creates directories/files, checks existence and children on the mirror and each backend, writes data, renames, attempts missing-file opens/deletes, and deletes the directory. `ReadWrite` writes `hello world`, reads sequentially with skip and EOF behavior, then performs random reads and an out-of-range read. `Locks` verifies lock/unlock success. `Misc` checks test directory discovery and writable-file sync/flush/close. `LargeWrite` writes a 300 KiB deterministic byte string and reads it back sequentially in chunks.

## State and Persistence Behavior
All persistent test state lives inside two `MockEnv` instances. The tests ensure mirrored writes are visible in both, and fixture teardown deletes the mirror and backends.

## Dependencies and Integration Points
The test depends on `rocksdb/utilities/env_mirror.h`, `env/mock_env.h`, and RocksDB's test harness. It indirectly validates the mirror wrappers in `env_mirror.cc`.

## Risks and Edge Cases
The tests do not intentionally create divergent backends, so assert-based mismatch detection is not directly exercised. Positioned append, truncate, allocate, range sync, invalidate cache, and unique ID paths are not covered. Because `MockEnv` behavior is idealized, platform-specific filesystem behavior is not tested.

## Test Signals
Passing tests show basic mirroring semantics, backend parity for metadata operations, correct sequential/random reads, and ability to handle large sequential data without corruption.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/env_mirror_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/env_timed.cc -->
# sources/storage-engines/rocksdb/utilities/env_timed.cc

## Purpose
This file implements a timed filesystem/environment wrapper that records filesystem operation latency into RocksDB `PerfContext` counters.

## Important APIs, Types, and Functions
`TimedFileSystem` derives from `FileSystemWrapper` and overrides creation, metadata, delete/create/rename/link/lock, and logger methods. Each override wraps the forwarded call with the matching `PERF_TIMER_GUARD` counter. `NewTimedFileSystem` returns a shared timed wrapper. `NewTimedEnv` creates a `CompositeEnvWrapper` combining the base Env with a timed filesystem.

## Control Flow
Every overridden method starts the relevant PerfContext timer guard, calls the base `FileSystemWrapper` implementation, and returns its `IOStatus`. `NewTimedEnv` obtains the base env's filesystem, wraps it, and returns a newly allocated composite env.

## State and Persistence Behavior
The wrapper does not alter filesystem semantics or store its own counters. Timing accumulates in thread-local/global PerfContext fields according to RocksDB's perf-level settings.

## Dependencies and Integration Points
It depends on `env/composite_env_wrapper.h`, `monitoring/perf_context_imp.h`, Env/FileSystem APIs, and `rocksdb/status.h`. Consumers call public `NewTimedEnv` or `NewTimedFileSystem` to instrument filesystem calls.

## Risks and Edge Cases
Only methods overridden here get explicit timers; operations performed on returned file objects are not wrapped by this class unless separately instrumented. Timers record only when PerfContext is enabled at a suitable level. `NewTimedEnv` returns a raw pointer, so callers own deletion. The wrapper delegates all status behavior and does not add validation.

## Test Signals
`env_timed_test.cc` enables `PerfLevel::kEnableTime`, opens a writable file through `NewTimedEnv`, and asserts the corresponding counter becomes positive. Broader tests could cover each timer field.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/env_timed.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/env_timed.h -->
# sources/storage-engines/rocksdb/utilities/env_timed.h

## Purpose
This header declares `TimedFileSystem`, the FileSystem wrapper that instruments filesystem operation latency for PerfContext.

## Important APIs, Types, and Functions
The class derives from `FileSystemWrapper`, defines class name `TimedFS`, and overrides file-open, directory, metadata, delete/create, rename/link, lock/unlock, and logger creation methods.

## Control Flow
The header lists all operations that receive timing in the implementation. Construction wraps an existing shared `FileSystem`.

## State and Persistence Behavior
`TimedFileSystem` stores only the base filesystem inherited through `FileSystemWrapper`. It does not persist data or counters itself.

## Dependencies and Integration Points
It depends on RocksDB's `file_system.h`. Public helper declarations are implemented in the `.cc` file and used by `NewTimedEnv`.

## Risks and Edge Cases
The class does not wrap returned file objects, so per-read/write timing must come from other instrumentation. Any new FileSystem APIs added later will not be timed unless explicitly overridden.

## Test Signals
Compile coverage and `env_timed_test.cc` confirm basic construction and at least one timer. A comprehensive test would exercise each overridden method with PerfContext enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/env_timed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/env_timed_test.cc -->
# sources/storage-engines/rocksdb/utilities/env_timed_test.cc

## Purpose
This file is the smoke test for timed environment instrumentation.

## Important APIs, Types, and Functions
`TimedEnvTest.BasicTest` calls `SetPerfLevel(PerfLevel::kEnableTime)`, checks `get_perf_context()->env_new_writable_file_nanos`, constructs a memory env and wraps it with `NewTimedEnv`, then opens a writable file.

## Control Flow
The test begins with the writable-file timer at zero, performs one `NewWritableFile` through the timed environment, and expects the timer counter to be greater than zero.

## State and Persistence Behavior
The test uses an in-memory environment and only creates file `f` inside it. PerfContext timing state is the relevant mutable state.

## Dependencies and Integration Points
It depends on public Env and PerfContext APIs, the timed env factory, memory env implementation, and the test harness.

## Risks and Edge Cases
The test covers only one operation and assumes the timer has nonzero measurable duration. It does not reset PerfContext after the test or verify other timed methods.

## Test Signals
Passing indicates that `NewTimedEnv` routes filesystem creation through `TimedFileSystem` and that PerfContext timing counters are active when enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/env_timed_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/fault_injection_env.cc -->
# sources/storage-engines/rocksdb/utilities/fault_injection_env.cc

## Purpose
This file implements the legacy `Env`-based fault-injection environment used by tests to simulate crashes, inactive filesystems, unsynced data loss, and directory fsync loss.

## Important APIs, Types, and Functions
Utility functions include `GetDirName`, `Truncate`, `TrimDirname`, and `GetDirAndName`. `FileState` can drop all or random unsynced tail data. `TestDirectory` wraps directory fsync/close and records directory syncs. `TestRandomAccessFile`, `TestWritableFile`, and `TestRandomRWFile` wrap file operations and consult `FaultInjectionTestEnv`. `FaultInjectionTestEnv` overrides directory/file creation, reopening, random-access opening, delete, rename, link, and `SyncFile`, and exposes state-management/drop methods.

## Control Flow
Writes through `TestWritableFile` update current position and notify the env. `Flush` records flush position, while `Sync` records sync position without necessarily performing a real sync. `Close` notifies the env and closes the target. If the filesystem is inactive, wrapped operations return the stored error. `DropUnsyncedFileData` iterates tracked file states and truncates files to their last synced position. `DeleteFilesCreatedAfterLastDirSync` deletes files recorded as newly created in directories not fsynced since creation.

## State and Persistence Behavior
The env tracks `db_file_state_`, `open_managed_files_`, `dir_to_new_files_since_last_sync_`, active/inactive state, and an injected error under a mutex. Persistent effects include real file truncation through a temporary rewrite/rename, deletion of files created after the last directory sync, and normal forwarded file operations.

## Dependencies and Integration Points
It wraps the legacy `Env` API and is used by older tests that have not moved fully to `FileSystem`. It depends on filename helpers, RocksDB Env file abstractions, `Random`, and mutex utilities. `checkpoint_test.cc` includes this header alongside the newer FS fault injector.

## Risks and Edge Cases
`Truncate` rewrites files through `truncate.tmp`, which can collide if multiple truncations happen in one directory concurrently. The env does not allow overwriting files through `NewWritableFile`, returning corruption if a file exists. RandomRW writes are not tracked with detailed sync positions. Much validation is assert-based. The model is approximate POSIX crash simulation, not a full filesystem journal model.

## Test Signals
Tests using this env should write, flush, sync, deactivate/reactivate, drop unsynced data, delete unsynced directory entries, and verify DB recovery. It is especially useful for durability tests that predate the FileSystem API.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/fault_injection_env.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/fault_injection_env.h -->
# sources/storage-engines/rocksdb/utilities/fault_injection_env.h

## Purpose
This header declares the legacy `FaultInjectionTestEnv` and its wrapped file/directory types for testing crash and filesystem-failure behavior.

## Important APIs, Types, and Functions
`FileState` records filename, current position, last sync position, and last flush position, and exposes unsynced-data drop helpers. `TestRandomAccessFile`, `TestWritableFile`, `TestRandomRWFile`, and `TestDirectory` wrap legacy Env file objects. `FaultInjectionTestEnv` derives from `EnvWrapper` and overrides key Env operations. It exposes `DropFileData`, `DropUnsyncedFileData`, `DropRandomUnsyncedFileData`, `DeleteFilesCreatedAfterLastDirSync`, `ResetState`, `UntrackFile`, `SyncDir`, filesystem active toggles, `AssertNoOpenFile`, and `GetError`.

## Control Flow
The declared wrappers gate operations on `IsFilesystemActive`, update tracked state on append/sync/close, and let the env simulate crash recovery by truncating unsynced bytes or deleting unsynced directory entries. `SetFilesystemActive` freezes state updates and causes subsequent operations to return a configured error.

## State and Persistence Behavior
The env stores file states, open managed files, unsynced directory entries, active flag, and error status under a mutex. It mutates real files only when drop/delete helpers or forwarded Env calls run.

## Dependencies and Integration Points
It depends on RocksDB Env APIs, filename types, and mutex utilities. It is a test utility for DB recovery, WAL, checkpoint, and durability scenarios using legacy Env interfaces.

## Risks and Edge Cases
The header exposes many mutable controls, so tests must reset state carefully between scenarios. The model tracks files created through this wrapper; externally created files may not be eligible for dropping. `GetFreeSpace` has a Windows macro workaround and reports zero free space when inactive with `NoSpace`.

## Test Signals
Compile and behavior tests should exercise all wrapper types, inactive status propagation, no-space free-space behavior, unsynced truncation, random truncation, directory sync tracking, rename/link state propagation, and open-file assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/fault_injection_env.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/fault_injection_fs.cc -->
# sources/storage-engines/rocksdb/utilities/fault_injection_fs.cc

## Purpose
This file implements the modern `FileSystem`-based fault-injection test wrapper. It simulates unsynced data loss, inactive filesystem errors, metadata/data I/O failures, checksum-handoff corruption checks, file-open contract violations, async read failures, and directory fsync durability.

## Important APIs, Types, and Functions
Top-level helpers parse info-log names, split paths, trim directories, and calculate CRC32c/xxHash checksums. `FSFileState` drops buffered unsynced data. `TestFSDirectory` wraps directory fsync/close. `TestFSWritableFile` buffers non-direct writes until sync/range sync, validates write contracts, injects write/metadata errors, checks handoff checksums, and publishes append/sync/close state. `TestFSRandomRWFile`, `TestFSRandomAccessFile`, and `TestFSSequentialFile` wrap random and sequential access with active-state checks and read error injection.

`FaultInjectionTestFS` overrides FileSystem methods for file/directory creation, open, read metadata, write metadata, rename/link, link-count/same-file checks, absolute path, directory checks, poll/abort I/O, and sync-file handling. It also implements state updates, unsynced data dropping, unsynced-data reads, new-file deletion/restore after missing directory fsync, thread-local error injection, and injected-error backtrace printing.

## Control Flow
Writable files created through the wrapper either forward direct/no-loss writes immediately or buffer append data in `FSFileState::buffer_`. `Sync` appends buffered data to the target, clears the buffer, updates `pos_at_last_sync_`, and records state. `RangeSync` flushes a consecutive prefix of buffered data. `Close` records close once, injects metadata errors if configured, drops unsynced buffered data because close is not sync, and closes the target.

Read wrappers call `MaybeInjectThreadLocalError` before forwarding. Sequential reads have extra logic to merge target data with unsynced buffered tail data when `ReadUnsyncedData()` is enabled, handling races where another thread syncs while a read is in progress. `MultiRead` injects per-request errors and optionally an aggregate multiread error.

Filesystem methods first check active state, then inject metadata/read/write errors based on thread-local contexts, then delegate to the target. Creation/open methods validate file-open contracts, wrap returned file objects, and track newly created directory entries. Rename/link propagate file state and open contracts and remember overwritten small-file contents so `DeleteFilesCreatedAfterLastDirSync` can restore preexisting files instead of simply deleting them.

## State and Persistence Behavior
The wrapper maintains tracked file states, open managed files, file-open contracts, unsynced directory entries with previous contents, active/inactive status, error contexts, read/write/metadata injection counters, and an injected-error log. Buffered unsynced writes may not reach the target filesystem until sync. Drop helpers clear unsynced buffers or delete/restore files whose containing directory was not fsynced. Normal operations still mutate the target filesystem when forwarded.

## Dependencies and Integration Points
It depends on the declarations in `fault_injection_fs.h`, composite env wrappers, thread status utilities, stack traces, `IOStatus`, `SyncPoint`, coding/checksum helpers, CRC32c, xxHash, random utilities, string helpers, and RocksDB FileSystem abstractions. It is used by durability, backup, checkpoint, DB stress, and fault-injection tests.

## Risks and Edge Cases
This is a complex test model, not a production filesystem. Direct I/O writes are not buffered for unsynced data loss. `RangeSync` assumes consecutive ranges. Some read-unsynced paths are intentionally TODO for random reads. Close status injection records the wrapper-level close transition before returning an error to model one-shot close semantics. Error injection can corrupt read buffers or return empty results to exercise checksum validation. Contract tracking can return `NotSupported` for reopen/read violations and must be kept in sync across rename/link/delete. Info-log filename parsing is custom because standard file parsing needs log prefixes.

## Test Signals
Strong signals include DB recovery tests after `DropUnsyncedFileData`, directory fsync loss tests, injected read/write/metadata error tests with retryable/data-loss flags, checksum handoff validation, async read failure callbacks, no-readers/no-reopen file-open contract tests, rename/link state propagation, and checkpoint/backup tests that use `FaultInjectionTestFS` to drop unsynced data.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/fault_injection_fs.cc -->
