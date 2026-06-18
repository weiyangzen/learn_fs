# subset-b-008708 research

Grouped research for RocksDB utility sources. Each source file section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/xxph3.h -->
# sources/storage-engines/rocksdb/util/xxph3.h

## Purpose

This header vendors a preview xxHash v0.7.2 XXH3 implementation into RocksDB as "XXPH3" so RocksDB can keep using the preview algorithm without colliding with standard xxHash symbols. RocksDB customizations force static inline inclusion, set `XXPH_NAMESPACE` to `ROCKSDB_`, enable static-linking-only APIs, include `<cstring>`, remove unused streaming APIs, and alter the zero-length hash behavior.

## Important APIs, types, and functions

The exported surface is the preview 64-bit XXPH3 API: `XXPH3_64bits`, `XXPH3_64bits_withSecret`, `XXPH3_64bits_withSeed`, `XXPH_versionNumber`, `XXPH32_hash_t`, `XXPH64_hash_t`, and `XXPH128_hash_t` for internal 128-bit multiply results. Internal helpers include endian-safe reads (`XXPH_readLE32`, `XXPH_readLE64`), rotations, byte swaps, `XXPH_mult64to128`, `XXPH3_mul128_fold64`, short-key routines for 1-3, 4-8, 9-16, 17-128, and 129-240 byte inputs, and long-key accumulator paths.

## Control flow

Public one-shot hashing dispatches by input length. Inputs up to 16 bytes use specialized scalar mixers, 17-128 bytes mix selected 16-byte chunks, 129-240 bytes run a midsize loop, and larger inputs use a 64-byte stripe accumulator over a 192-byte default secret. Long-key processing accumulates stripes, scrambles accumulator lanes between blocks, mixes accumulator pairs, and finalizes through an avalanche. Vectorized `XXPH3_accumulate_512` and `XXPH3_scrambleAcc` branches support AVX2, SSE2, NEON, VSX, and scalar fallback, selected by preprocessor feature checks.

## State and persistence behavior

The file has no runtime persistence. It defines immutable constants, including prime constants and the 192-byte default secret `kSecret`. Hash results are deterministic for this preview implementation and build target semantics, but comments warn that upstream XXH3 preview versions are not stable for long-term stored values. RocksDB's local fork makes that explicit by renaming the namespace and symbols.

## Dependencies and integration points

The code depends on standard fixed-width integer types when available, compiler intrinsics for vectorization, RocksDB namespace configuration, and `memcpy` for portable unaligned reads. It is consumed by RocksDB hashing code, with `util/hash.cc` calling `XXPH3_64bits` and `XXPH3_64bits_withSeed`. Static inline inclusion avoids exported symbol conflicts, including unity builds.

## Risks

The main correctness risk is hash compatibility: this is not final XXH3, and RocksDB intentionally preserves preview behavior. The RocksDB-specific empty-input change returns a folded hash of the seed/secret instead of zero, so replacing this file with upstream xxHash would silently change results. Other risks are preprocessor portability, vector intrinsic compilation on less common architectures, undefined behavior if callers violate custom-secret size requirements, and poor collision resistance if users supply weak custom secrets.

## Test signals

Relevant signals are hash determinism tests, cross-platform hash-value tests, RocksDB `util/hash.cc` callers, and any persistence or format tests that rely on stable hash values. Build coverage across AVX2/SSE2/NEON/VSX/scalar targets is especially important because much of the implementation is selected at compile time.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/xxph3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/agg_merge/agg_merge.cc -->
# sources/storage-engines/rocksdb/utilities/agg_merge/agg_merge.cc

## Purpose

This file implements RocksDB's experimental aggregation merge operator. It lets values and merge operands carry an aggregation function name plus a payload, then applies registered `Aggregator` plugins during full or partial merge. When aggregation cannot proceed, it preserves the original operands in an encoded error value rather than failing the DB operation.

## Important APIs, types, and functions

Global API implementations are `AddAggregator`, `EncodeAggFuncAndPayload`, `ExtractAggFuncAndValue`, `ExtractList`, and `GetAggMergeOperator`. Internal symbols include the process-global `func_map`, reserved names `kUnnamedFuncName` and `kErrorFuncName`, `EncodeAggFuncAndPayloadNoCheck`, `AggMergeOperator::Accumulator`, `PackAllMergeOperands`, `FullMergeV2`, and `PartialMergeMulti`.

## Control flow

`EncodeAggFuncAndPayload` validates the function name and writes a length-prefixed function slice followed by raw payload. `Accumulator::Add` decodes each operand, selects the first non-empty function, optionally rejects partial aggregation when the registered aggregator opts out, and handles function switches by fully aggregating older values before adding the next function's payload. `FullMergeV2` feeds the existing value and operands through the accumulator, emits the aggregate on success, or packs all inputs under `kErrorFuncName` on failure. `PartialMergeMulti` only returns true if all operands can be safely partially aggregated.

## State and persistence behavior

Registered aggregators live in a static unordered map and are shared by all operator instances. The merge operator singleton is held by `STATIC_AVOID_DESTRUCTION`. Per-merge scratch state is a thread-local accumulator to avoid repeated allocation while remaining safe for concurrent merge invocations. Persisted DB values use length-prefixed function names plus aggregator-defined payload bytes; error values use `kErrorFuncName` plus a length-prefixed list of original encoded operands.

## Dependencies and integration points

The implementation plugs into RocksDB's `MergeOperator` interface and uses `Slice`, `Status`, `PutLengthPrefixedSlice`, `GetLengthPrefixedSlice`, and `port/lang.h`. Public declarations come from `include/rocksdb/utilities/agg_merge.h`, while internal class declarations live in `agg_merge_impl.h`. Applications install it through `Options::merge_operator = GetAggMergeOperator()` and register functions with `AddAggregator`.

## Risks

`func_map` mutation is not synchronized and the public header says aggregators should be registered before use. Duplicate registrations are silently ignored by `emplace` but still return OK, which can surprise users. Stored encodings are explicitly experimental and subject to change. Function switches require payload format compatibility across aggregators. Partial merge is intentionally conservative, but a buggy `DoPartialAggregate` implementation can produce semantically wrong intermediate values.

## Test signals

`agg_merge_test.cc` exercises sum, multiplication, last-three list aggregation, Put-with-unnamed-function behavior, function switching across flush and compaction, unregistered functions, invalid payloads, and error-list extraction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/agg_merge/agg_merge.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/agg_merge/agg_merge_impl.h -->
# sources/storage-engines/rocksdb/utilities/agg_merge/agg_merge_impl.h

## Purpose

This internal header declares the concrete merge-operator class behind the public aggregation-merge API. It separates RocksDB's `MergeOperator` implementation details from the public experimental utility header.

## Important APIs, types, and functions

`AggMergeOperator` derives from `MergeOperator` and overrides `FullMergeV2`, `PartialMergeMulti`, `Name`, `AllowSingleOperand`, and `ShouldMerge`. It exposes `kClassName()` as `"AggMergeOperator.v1"`. Private helpers declare the nested `Accumulator`, `PackAllMergeOperands`, and `GetTLSAccumulator`. `EncodeAggFuncAndPayloadNoCheck` is declared for tests and internal error-path construction.

## Control flow

The header only declares behavior. The control path is implemented in `agg_merge.cc`: full merges aggregate existing value plus operands, partial merges aggregate only when safe, and errors pack original operands. `ShouldMerge` always returns false, leaving merge scheduling to RocksDB's standard merge machinery rather than forcing proactive merge decisions.

## State and persistence behavior

The class itself carries no member fields. State lives in the static aggregator registry, thread-local accumulator, and persisted encoded values. `AllowSingleOperand()` returns true, allowing RocksDB to invoke merge logic even with a single operand.

## Dependencies and integration points

It includes RocksDB merge and slice headers, the public `agg_merge.h`, and an unrelated Cassandra options include that appears unnecessary for this declaration. It is included by the implementation and tests under `utilities/agg_merge`.

## Risks

Because this is an internal header, changing method behavior or `Name()` can affect existing DB option compatibility and tests. The extra include increases compile coupling. The no-state class hides important global state in the implementation, so tests must account for cross-test registrations.

## Test signals

The integration test checks the operator by name only indirectly through `GetAggMergeOperator` and DB merge behavior. Compile coverage also validates that RocksDB's `MergeOperator` override signatures stay current.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/agg_merge/agg_merge_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/agg_merge/agg_merge_test.cc -->
# sources/storage-engines/rocksdb/utilities/agg_merge/agg_merge_test.cc

## Purpose

This GTest file provides DB-level coverage for the experimental aggregation merge operator. It verifies that encoded aggregate operands survive normal RocksDB writes, flushes, compactions, full merges, partial merges, and failure cases.

## Important APIs, types, and functions

`AggMergeTest` derives from `DBTestBase`. The test registers `SumAggregator`, `Last3Aggregator`, and `MultipleAggregator`, installs `GetAggMergeOperator()` into `Options::merge_operator`, and uses `EncodeHelper`, `EncodeAggFuncAndPayloadNoCheck`, `EncodeAggFuncAndPayload`, `ExtractAggFuncAndValue`, and `ExtractList`.

## Control flow

The main test writes several keys. It merges three `sum` operands into `foo`, list operands into `bar` with a flush boundary, uses an unnamed Put followed by sum merges for `foo2`, switches from multiplication to sum on `bar2`, tests function switching across partial-merge opportunities on `foo3`, merges after flush and compaction on `foo4`, then validates unregistered function and invalid payload paths.

## State and persistence behavior

The test opens a real RocksDB test DB with fsync enabled through `DBTestBase`. Flush and compact operations force merge operands into persisted SST state, so the test checks both in-memory and persisted merge paths. The global aggregator registry is populated at test start and then reused by the singleton operator.

## Dependencies and integration points

The file depends on RocksDB test infrastructure, options, public agg-merge APIs, the internal implementation header, and test aggregators from `test_agg_merge.h`. The `main` installs the RocksDB stack trace handler and runs all GTests.

## Risks

Because `AddAggregator` uses a global map and duplicate registration returns OK without replacement, adding more tests in this process can inherit prior registration state. Assertions compare fully encoded strings, which is good for format coverage but means intentional encoding changes require coordinated test updates. The test covers representative aggregators but not concurrency or duplicate registration behavior.

## Test signals

Passing this test signals that full merge, partial merge, function switching, unnamed base values, compaction interaction, error packing, and list decoding still match the implementation contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/agg_merge/agg_merge_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/agg_merge/test_agg_merge.cc -->
# sources/storage-engines/rocksdb/utilities/agg_merge/test_agg_merge.cc

## Purpose

This file implements helper encoders and simple aggregators used by the aggregation-merge tests. It defines concrete integer and list aggregation behavior without making those aggregators part of the production API.

## Important APIs, types, and functions

`EncodeHelper::EncodeFuncAndInt`, `EncodeInt`, `EncodeFuncAndList`, and `EncodeList` build payloads using var-signed integers and length-prefixed slices. `SumAggregator::Aggregate` sums integer payloads. `MultipleAggregator::Aggregate` multiplies integer payloads. `Last3Aggregator::Aggregate` extracts up to three newest list entries from reverse insertion order.

## Control flow

Integer helpers encode values with `PutVarsignedint64` and wrap them with `EncodeAggFuncAndPayload`. List helpers append each slice as a length-prefixed item. Sum and multiplication aggregators decode every payload with `GetVarsignedint64` and reject extra trailing bytes. `Last3Aggregator` walks input lists from newest to oldest, reads length-prefixed entities, and stops once three values are collected.

## State and persistence behavior

The file has no global mutable state. It produces byte encodings that are persisted by test DB writes. Aggregator results are deterministic: integer aggregators return one encoded integer, while `Last3Aggregator` returns a length-prefixed list of retained slices.

## Dependencies and integration points

It depends on `test_agg_merge.h`, RocksDB coding helpers, and the internal agg-merge encoding helper. It is linked only into agg-merge tests.

## Risks

The helpers use `assert(s.ok())`, so invalid test setup aborts rather than reporting a GTest assertion. Integer multiplication can overflow `int64_t` silently in tests. `Last3Aggregator` intentionally ignores malformed list fragments by continuing after a failed parse, which is acceptable for its current tests but not a general validation pattern.

## Test signals

The production test uses these helpers to generate expected byte strings and to validate aggregator behavior through RocksDB's merge operator.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/agg_merge/test_agg_merge.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/agg_merge/test_agg_merge.h -->
# sources/storage-engines/rocksdb/utilities/agg_merge/test_agg_merge.h

## Purpose

This test header declares the concrete aggregators and encoding helper used by `agg_merge_test.cc`. It provides small, focused aggregator implementations for exercising production merge-operator behavior.

## Important APIs, types, and functions

`SumAggregator`, `MultipleAggregator`, and `Last3Aggregator` derive from `Aggregator` and implement `Aggregate`. The first two override `DoPartialAggregate()` to true explicitly, while `Last3Aggregator` inherits the default true behavior. `EncodeHelper` declares methods for integer, list, and function-plus-payload encodings.

## Control flow

The header only declares test components. Implementations in `test_agg_merge.cc` encode payloads and aggregate vectors supplied by `AggMergeOperator`.

## State and persistence behavior

No state is stored in the classes. Instances are registered in the global agg-merge registry during the test and then invoked by RocksDB merge processing. Encoded outputs become normal RocksDB values in the test DB.

## Dependencies and integration points

It includes the public merge and slice headers, public `agg_merge.h`, and the same Cassandra options include as `agg_merge_impl.h`. It is consumed by the agg-merge unit test and helper implementation.

## Risks

The explicit `DoPartialAggregate()` override on integer aggregators documents intent, but `Last3Aggregator` relies on the base default; if that default changes, tests could change behavior. Like the internal header, the Cassandra include appears unnecessary and adds compile coupling.

## Test signals

Compilation and use in `agg_merge_test.cc` signal that custom `Aggregator` subclasses can be registered and invoked through the production operator.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/agg_merge/test_agg_merge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/backup/backup_engine.cc -->
# sources/storage-engines/rocksdb/utilities/backup/backup_engine.cc

## Purpose

This file implements RocksDB's backup and restore engine. It creates point-in-time backups via checkpoint callbacks, stores metadata under a backup directory, shares table/blob files across backups when configured, restores backups into DB/WAL directories, verifies backup contents, deletes old backups, and garbage-collects unreferenced backup files.

## Important APIs, types, and functions

Public entry points are `BackupEngine::Open`, `BackupEngineReadOnly::Open`, `CreateNewBackupWithMetadata`, `PurgeOldBackups`, `DeleteBackup`, `StopBackup`, `GarbageCollect`, `GetBackupInfo`, `GetLatestBackupInfo`, `GetCorruptedBackups`, `RestoreDBFromBackup`, `RestoreDBFromLatestBackup`, and `VerifyBackup`. Internal types include `BackupEngineImpl`, `BackupEngineImplThreadSafe`, `BackupMeta`, `FileInfo`, `WorkItem`, `WorkItemResult`, `BackupAfterCopyOrCreateWorkItem`, `ComputeChecksumWorkItem`, `RestoreAfterCopyOrCreateWorkItem`, and `RemapSharedFileSystem`.

## Control flow

`Initialize` creates or opens the backup directory layout, loads valid metadata files from `meta/`, classifies corrupt backups, computes latest IDs, and starts background worker threads. Backup creation disables DB file deletions, builds a `CheckpointImpl`, schedules copy/create work items for live files and generated files, optionally lets a callback exclude shared checksum files, waits for all work, records metadata, fsyncs directories when requested, and updates latest IDs. Restore resolves excluded files through alternate read-only backup engines, optionally keeps existing DB files by DB session ID or checksum, deletes non-retained files, copies backup files back to DB/WAL directories, and atomically renames `CURRENT.tmp`. Verification checks presence and size and can schedule checksum recomputation. Delete and purge remove metadata first, decrement reference counts, delete unreferenced files, and invoke garbage collection as needed.

## State and persistence behavior

The backup directory uses `private/<backup_id>/`, `meta/<backup_id>`, `shared/`, and `shared_checksum/`. Metadata files are the commit records for backups and are written through temporary meta files followed by rename. `BackupMeta` stores timestamp, approximate sequence number, app metadata, file list, excluded file list, sizes, crc32c hex checksums, and temperatures. In memory, `backuped_file_infos_` reference-counts shared and private files across loaded backups. The engine tracks `latest_backup_id_`, `latest_valid_backup_id_`, corrupt backups, stop state, background threads, and whether another GC might be needed.

## Dependencies and integration points

The implementation integrates with RocksDB `DB`, `CheckpointImpl`, file naming/parsing helpers, `Env` and `FileSystem`, `FSDirectory`, `WritableFileWriter`, `SequentialFileReader`, `LineFileReader`, rate limiters, statistics tickers, table property reading through `SstFileDumper`, DB file checksum metadata, sync points, and public backup options. `RemapSharedFileSystem` lets shared backup files appear inside a private backup directory so backup contents can be opened as a read-only DB for inspection.

## Risks

Backup correctness depends on metadata atomicity, directory fsync behavior, checkpoint file enumeration, and safe sharing names. `share_files_with_checksum=false` is explicitly deprecated because it can lead to data loss. Incremental backups can skip rereading existing shared files, so existing backup corruption is not always detected during new backup creation; `VerifyBackup` is the explicit check path. The background work queue has limited cancellation semantics, and checksum verification waits for scheduled tasks to finish. The code has subtle path handling for shared checksum names, DB session IDs, file sizes, temperatures, excluded files, and restore modes. The read-only facade uses lock ordering across alternate backup engines to avoid TSAN lock inversion reports.

## Test signals

The adjacent `backup_engine_test.cc` covers backup/restore basics, shared checksum naming, restore modes (`kPurgeAllFiles`, `kKeepLatestDbSessionIdFiles`, `kVerifyChecksum`), corruption and schema handling, excluded files, rate limiter clocks, metadata schema options, and option transitions. DB stress code also exercises backup options and schema test hooks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/backup/backup_engine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/backup/backup_engine_impl.h -->
# sources/storage-engines/rocksdb/utilities/backup/backup_engine_impl.h

## Purpose

This internal header exposes test-only hooks for the backup engine implementation. It is not the public backup API; it lets tests force metadata schema variants and control clocks in default rate limiters.

## Important APIs, types, and functions

`TEST_BackupMetaSchemaOptions` carries a schema `version`, booleans controlling crc32c checksum and size field emission, and maps for extra meta, file, and footer fields. `TEST_SetBackupMetaSchemaOptions` installs those options on a `BackupEngine`. `TEST_SetDefaultRateLimitersClock` replaces clocks used by default-created backup and restore rate limiters.

## Control flow

The header declares hooks implemented at the end of `backup_engine.cc`. The schema hook downcasts to `BackupEngineImplThreadSafe` and stores options that `BackupMeta::StoreToFile` reads while writing metadata. The clock hook downcasts and calls through to `GenericRateLimiter::TEST_SetClock` for backup and restore limiters when provided.

## State and persistence behavior

The schema options affect subsequent backup meta-file persistence for the lifetime of the engine object, not for the whole backup directory. They can force unpublished schema version 2 behavior, omit checksums, include sizes, and inject unrecognized or non-ignorable fields. The rate-limiter clock hook changes in-memory limiter timing for tests only.

## Dependencies and integration points

It includes `rocksdb/utilities/backup_engine.h` for `BackupEngine` and uses `SystemClock` through the public backup-engine dependency chain. Tests in `backup_engine_test.cc` and DB stress code include these hooks to cover metadata forward-compatibility, schema rejection, and faster deterministic rate limiter behavior.

## Risks

These hooks rely on downcasting the public engine pointer to the internal implementation wrapper, so they are only valid for engines created by this implementation. Misuse outside tests can write unusual metadata files into real backup directories. The defaults are intentionally test-oriented (`crc32c_checksums=false`, `file_sizes=true`) and differ from normal production metadata writing.

## Test signals

Schema tests use this header to validate metadata parser behavior for missing checksums, size fields, custom fields, footer fields, non-ignorable future fields, and unsupported versions. Rate limiter tests use the clock hook to avoid slow wall-clock waits.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/backup/backup_engine_impl.h -->
